<#
.SYNOPSIS
    Shared implementation for the per-server MCP deploy scripts.

.DESCRIPTION
    Dot-sourced by deploy-sales-mcp.ps1 / deploy-inventory-mcp.ps1 /
    deploy-marketing-mcp.ps1. Defines Invoke-McpServerDeploy, which builds one
    MCP server image into ACR and deploys it as a Container App using KEY-BASED
    auth throughout:
      - ACR image pull uses the registry admin username/password.
      - Cosmos DB access uses the account key (injected as a Container App
        secret and read by the app via the COSMOS_KEY env var).
    No managed identity is attached — the MCP servers only need ACR + Cosmos.

    Not meant to be run directly.
#>

function Get-DotEnvValues {
    param([string]$Path)
    $values = @{}
    if (-not (Test-Path $Path)) {
        return $values
    }
    foreach ($line in (Get-Content $Path)) {
        $trimmed = $line.Trim()
        if ($trimmed -eq '' -or $trimmed.StartsWith('#')) {
            continue
        }
        if ($trimmed -match '^([^=]+)=(.*)$') {
            $values[$matches[1].Trim()] = $matches[2].Trim().Trim('"')
        }
    }
    return $values
}

function Get-RequiredValue {
    param([string]$Explicit, [hashtable]$EnvValues, [string]$Key, [string]$Friendly, [string]$EnvFile)
    if (-not [string]::IsNullOrWhiteSpace($Explicit)) {
        return $Explicit
    }
    $fromEnv = $EnvValues[$Key]
    if ([string]::IsNullOrWhiteSpace($fromEnv)) {
        throw "$Friendly not found. Pass it explicitly or set $Key in $EnvFile."
    }
    return $fromEnv
}

function Resolve-CosmosAccountName {
    param([string]$CosmosEndpoint, [hashtable]$EnvValues)
    # Prefer an explicit COSMOS_ACCOUNT in .env; else derive from the endpoint
    # https://<account>.documents.azure.com:443/
    if (-not [string]::IsNullOrWhiteSpace($EnvValues['COSMOS_ACCOUNT'])) {
        return $EnvValues['COSMOS_ACCOUNT']
    }
    if ($CosmosEndpoint -match '^https://([^.]+)\.') {
        return $matches[1]
    }
    return $null
}

function Invoke-McpServerDeploy {
    param(
        [Parameter(Mandatory)] [string]$Service,
        [Parameter(Mandatory)] [string]$AppName,
        [Parameter(Mandatory)] [int]$Port,
        [Parameter(Mandatory)] [string]$ContainerEnvKey,
        [Parameter(Mandatory)] [string]$UrlEnvKey,
        [string]$ResourceGroup,
        [string]$AcrName,
        [string]$AcaEnvironment,
        [string]$SubscriptionId,
        [string]$ImageTag = 'latest',
        [string]$EnvFile = '.env'
    )

    $ErrorActionPreference = 'Stop'
    $projectRoot = Split-Path -Parent $PSScriptRoot
    Push-Location $projectRoot
    try {
        $dockerfile = "src/mcp_servers/$Service/Dockerfile"
        if (-not (Test-Path $dockerfile)) {
            throw "Dockerfile not found at '$dockerfile'. Run this from the ai-agents-workshop repo."
        }

        $envValues = Get-DotEnvValues -Path $EnvFile

        if ($SubscriptionId) {
            az account set --subscription $SubscriptionId | Out-Null
        }
        elseif ($envValues['AZURE_SUBSCRIPTION_ID']) {
            az account set --subscription $envValues['AZURE_SUBSCRIPTION_ID'] | Out-Null
        }

        $ResourceGroup  = Get-RequiredValue $ResourceGroup  $envValues 'AZURE_RESOURCE_GROUP' 'Resource group'       $EnvFile
        $AcrName        = Get-RequiredValue $AcrName         $envValues 'ACR_NAME'             'ACR name'             $EnvFile
        $AcaEnvironment = Get-RequiredValue $AcaEnvironment  $envValues 'ACA_ENVIRONMENT'      'Container Apps env'   $EnvFile
        $cosmosEndpoint = Get-RequiredValue ''               $envValues 'COSMOS_ENDPOINT'      'Cosmos endpoint'      $EnvFile
        $cosmosDatabase = Get-RequiredValue ''               $envValues 'COSMOS_DATABASE'      'Cosmos database'      $EnvFile
        $containerName  = Get-RequiredValue ''               $envValues $ContainerEnvKey       "Cosmos container for $Service" $EnvFile
        $appInsights    = $envValues['APPLICATIONINSIGHTS_CONNECTION_STRING']

        # ---- Key-based auth: ACR admin credentials -------------------------
        # Enable the registry admin user and read its username/password so the
        # Container App can pull the image without a managed identity.
        az acr update --name $AcrName --resource-group $ResourceGroup --admin-enabled true --only-show-errors | Out-Null
        $acrCredsJson = az acr credential show --name $AcrName --resource-group $ResourceGroup -o json
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($acrCredsJson)) {
            throw "Could not read ACR admin credentials for '$AcrName'. Ensure admin user is enabled."
        }
        $acrCreds = $acrCredsJson | ConvertFrom-Json
        $acrUsername = $acrCreds.username
        $acrPassword = $acrCreds.passwords[0].value

        # ---- Key-based auth: Cosmos DB account key -------------------------
        # The app reads COSMOS_KEY (injected as a secret) instead of using a
        # managed identity for Cosmos data-plane access.
        $cosmosKey = $envValues['COSMOS_KEY']
        if ([string]::IsNullOrWhiteSpace($cosmosKey)) {
            $cosmosAccount = Resolve-CosmosAccountName $cosmosEndpoint $envValues
            if ([string]::IsNullOrWhiteSpace($cosmosAccount)) {
                throw "Could not determine the Cosmos account name. Set COSMOS_KEY or COSMOS_ACCOUNT in $EnvFile."
            }
            $cosmosKey = az cosmosdb keys list --name $cosmosAccount --resource-group $ResourceGroup `
                --query primaryMasterKey -o tsv 2>$null
            if ([string]::IsNullOrWhiteSpace($cosmosKey)) {
                throw "Could not read the Cosmos account key for '$cosmosAccount'. Set COSMOS_KEY in $EnvFile or pass it explicitly."
            }
        }

        $image = "$AcrName.azurecr.io/$($AppName):$ImageTag"

        Write-Host "== Step 1/3: building $image (ACR Tasks) =="
        $env:PYTHONIOENCODING = 'utf-8'
        az acr build --registry $AcrName --image "$($AppName):$ImageTag" --file $dockerfile --no-logs . | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "az acr build failed for '$Service' with exit code $LASTEXITCODE."
        }

        # The app reads COSMOS_KEY (a Container App secret) for key-based
        # Cosmos data-plane access — no managed identity required.
        $envVars = @(
            "PORT=$Port",
            "COSMOS_ENDPOINT=$cosmosEndpoint",
            'COSMOS_KEY=secretref:cosmos-key',
            "COSMOS_DATABASE=$cosmosDatabase",
            "$ContainerEnvKey=$containerName"
        )
        if (-not [string]::IsNullOrWhiteSpace($appInsights)) {
            $envVars += "APPLICATIONINSIGHTS_CONNECTION_STRING=$appInsights"
        }

        # Recreate any app stuck in a non-Succeeded provisioning state.
        $existingState = az containerapp show --name $AppName --resource-group $ResourceGroup `
            --query properties.provisioningState -o tsv 2>$null
        if (-not [string]::IsNullOrWhiteSpace($existingState) -and $existingState -ne 'Succeeded') {
            Write-Host "== Step 2/3: removing stale app (provisioningState=$existingState) and recreating =="
            az containerapp delete --name $AppName --resource-group $ResourceGroup --yes --only-show-errors | Out-Null
            $existingState = $null
        }

        if ([string]::IsNullOrWhiteSpace($existingState)) {
            Write-Host "== Step 2/3: creating Container App '$AppName' (key-based ACR + Cosmos auth) =="
            az containerapp create `
                --name $AppName `
                --resource-group $ResourceGroup `
                --environment $AcaEnvironment `
                --image $image `
                --target-port $Port `
                --ingress external `
                --registry-server "$AcrName.azurecr.io" `
                --registry-username $acrUsername `
                --registry-password $acrPassword `
                --secrets "cosmos-key=$cosmosKey" `
                --env-vars $envVars `
                --only-show-errors | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "az containerapp create failed for '$Service' with exit code $LASTEXITCODE."
            }
        }
        else {
            Write-Host "== Step 2/3: updating existing Container App '$AppName' =="
            az containerapp registry set --name $AppName --resource-group $ResourceGroup `
                --server "$AcrName.azurecr.io" --username $acrUsername --password $acrPassword --only-show-errors | Out-Null
            az containerapp secret set --name $AppName --resource-group $ResourceGroup `
                --secrets "cosmos-key=$cosmosKey" --only-show-errors | Out-Null
            az containerapp ingress update --name $AppName --resource-group $ResourceGroup `
                --target-port $Port --only-show-errors | Out-Null
            az containerapp update `
                --name $AppName `
                --resource-group $ResourceGroup `
                --image $image `
                --set-env-vars $envVars `
                --only-show-errors | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "az containerapp update failed for '$Service' with exit code $LASTEXITCODE."
            }
        }

        Write-Host '== Step 3/3: resolving the server URL =='
        $fqdn = az containerapp show --name $AppName --resource-group $ResourceGroup `
            --query properties.configuration.ingress.fqdn -o tsv
        $url = "https://$fqdn/mcp"
        Write-Host ''
        Write-Host "$Service MCP server deployed: $url"
        Write-Host "Set $UrlEnvKey=$url in your .env, then re-run create_$($Service)_agent so the Foundry connection points here."
    }
    finally {
        Pop-Location
    }
}
