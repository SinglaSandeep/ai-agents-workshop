<#
.SYNOPSIS
    Build the Zava chat app image into ACR and deploy it to Azure Container Apps.

.DESCRIPTION
    Codifies the manual steps from docs/12_deploy_chat_app/12_deploy_chat_app.md:
      1. az acr build  -> builds the repo-root Dockerfile into your ACR (no local Docker).
      2. az containerapp create/update -> ships src/app/main.py to the ACA environment.
         - ACR image pull uses key-based auth (the registry's admin
           username/password), stored as a Container App registry secret.
         - The app is attached to a pre-created USER-ASSIGNED managed identity
           (default 'id-zava-workload') to call the Foundry Agent Service, which
           requires Microsoft Entra ID (it does not accept API keys). That
           identity already has Foundry access because it is a member of the
           workshop Entra group (granted Azure AI User on the resource group),
           so this script does NOT create any role assignments.

    Resource names are read from the workshop .env (written by the infra repo's
    Part B load-data.ps1) unless passed explicitly. Re-run any time the app code
    changes; the deploy step is idempotent (create on first run, update after).

.PARAMETER BasicAuthUsername
    Username for the app's Basic auth gate. Default 'demo-admin'.

.PARAMETER BasicAuthPassword
    Password for the app's Basic auth gate. If omitted you'll be prompted
    securely (never echoed, never stored in source).

.PARAMETER AppName
    Container App name. Default 'zava-chat-app'.

.PARAMETER ImageTag
    Image tag built/deployed. Default 'latest'.

.PARAMETER EnvFile
    Path to the workshop .env to source resource names from. Default '.env'.

.EXAMPLE
    ./scripts/deploy-chat-app.ps1

.EXAMPLE
    ./scripts/deploy-chat-app.ps1 -BasicAuthUsername admin -AppName zava-chat-prod
#>
param(
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $false)]
    [string]$AcrName,

    [Parameter(Mandatory = $false)]
    [string]$AcaEnvironment,

    [Parameter(Mandatory = $false)]
    [string]$AppIdentityResourceId,

    [Parameter(Mandatory = $false)]
    [string]$AppIdentityName = 'id-zava-workload',

    [Parameter(Mandatory = $false)]
    [string]$FoundryAccountName,

    [Parameter(Mandatory = $false)]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $false)]
    [string]$AppName = 'zava-chat-app',

    [Parameter(Mandatory = $false)]
    [string]$ImageTag = 'latest',

    [Parameter(Mandatory = $false)]
    [string]$BasicAuthUsername = 'demo-admin',

    [Parameter(Mandatory = $false)]
    [securestring]$BasicAuthPassword,

    [Parameter(Mandatory = $false)]
    [string]$ModelChoices = 'gpt-4.1-mini,gpt-5.4-mini,gpt-5.4-nano',

    [Parameter(Mandatory = $false)]
    [string]$EnvFile = '.env'
)

$ErrorActionPreference = 'Stop'

function Get-ProjectRoot {
    Split-Path -Parent $PSScriptRoot
}

# Load KEY=VALUE pairs from the workshop .env so we can default resource names.
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
    param([string]$Explicit, [hashtable]$Env, [string]$Key, [string]$Friendly)
    if (-not [string]::IsNullOrWhiteSpace($Explicit)) {
        return $Explicit
    }
    $fromEnv = $Env[$Key]
    if ([string]::IsNullOrWhiteSpace($fromEnv)) {
        throw "$Friendly not found. Pass it explicitly or set $Key in $EnvFile."
    }
    return $fromEnv
}

$projectRoot = Get-ProjectRoot
Push-Location $projectRoot
try {
    if (-not (Test-Path 'Dockerfile')) {
        throw "Dockerfile not found at repo root '$projectRoot'. Run this script from the ai-agents-workshop repo."
    }

    $envValues = Get-DotEnvValues -Path $EnvFile

    if ($SubscriptionId) {
        az account set --subscription $SubscriptionId | Out-Null
    }
    elseif ($envValues['AZURE_SUBSCRIPTION_ID']) {
        az account set --subscription $envValues['AZURE_SUBSCRIPTION_ID'] | Out-Null
    }

    $ResourceGroup      = Get-RequiredValue $ResourceGroup      $envValues 'AZURE_RESOURCE_GROUP' 'Resource group'
    $AcrName            = Get-RequiredValue $AcrName            $envValues 'ACR_NAME'             'ACR name'
    $AcaEnvironment     = Get-RequiredValue $AcaEnvironment     $envValues 'ACA_ENVIRONMENT'      'Container Apps environment'
    $projectEndpoint    = Get-RequiredValue ''                  $envValues 'AZURE_AI_PROJECT_ENDPOINT' 'Foundry project endpoint'
    $modelDeployment    = Get-RequiredValue ''                  $envValues 'AZURE_AI_MODEL_DEPLOYMENT'  'Foundry model deployment'

    # App Insights connection string is optional (observability is graceful).
    $appInsights = $envValues['APPLICATIONINSIGHTS_CONNECTION_STRING']

    # Prompt for the Basic-auth password if not supplied, without echoing it.
    if (-not $BasicAuthPassword) {
        $BasicAuthPassword = Read-Host -AsSecureString "Basic-auth password for '$BasicAuthUsername'"
    }
    $plainPassword = [System.Net.NetworkCredential]::new('', $BasicAuthPassword).Password
    if ([string]::IsNullOrWhiteSpace($plainPassword)) {
        throw 'Basic-auth password must not be empty.'
    }

    $image = "$AcrName.azurecr.io/$($AppName):$ImageTag"

    # ----------------------------------------------------------------------
    # Resolve the pre-created USER-ASSIGNED managed identity the app runs as.
    # It is a member of the workshop Entra group, so it already inherits the
    # group's Foundry access (Azure AI User on the RG) — no role grants here.
    # Precedence: explicit param > .env APP_IDENTITY_RESOURCE_ID > name lookup.
    # ----------------------------------------------------------------------
    if ([string]::IsNullOrWhiteSpace($AppIdentityResourceId)) {
        $AppIdentityResourceId = $envValues['APP_IDENTITY_RESOURCE_ID']
    }
    if ([string]::IsNullOrWhiteSpace($AppIdentityResourceId)) {
        $AppIdentityResourceId = az identity show --name $AppIdentityName `
            --resource-group $ResourceGroup --query id -o tsv 2>$null
    }
    if ([string]::IsNullOrWhiteSpace($AppIdentityResourceId)) {
        throw "Could not resolve the user-assigned identity. Pass -AppIdentityResourceId, set APP_IDENTITY_RESOURCE_ID in $EnvFile, or create '$AppIdentityName' in $ResourceGroup."
    }
    $identityClientId = $envValues['APP_IDENTITY_CLIENT_ID']
    if ([string]::IsNullOrWhiteSpace($identityClientId)) {
        $identityClientId = az identity show --ids $AppIdentityResourceId --query clientId -o tsv
    }
    if ([string]::IsNullOrWhiteSpace($identityClientId)) {
        throw "Could not resolve the client id for identity '$AppIdentityResourceId'."
    }
    Write-Host "Using user-assigned identity (Foundry via group membership): $AppIdentityResourceId"

    # ----------------------------------------------------------------------
    # ACR image pull uses KEY-BASED auth: enable the registry admin user and
    # read its credentials. The Container App stores the password as a
    # registry secret (no AcrPull role / managed-identity pull needed).
    # ----------------------------------------------------------------------
    Write-Host '== Step 1/4: enabling ACR admin user =='
    az acr update --name $AcrName --resource-group $ResourceGroup --admin-enabled true --only-show-errors | Out-Null
    $acrCredsJson = az acr credential show --name $AcrName --resource-group $ResourceGroup -o json
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($acrCredsJson)) {
        throw "Could not read ACR admin credentials for '$AcrName'. Ensure admin user is enabled."
    }
    $acrCreds = $acrCredsJson | ConvertFrom-Json
    $acrUsername = $acrCreds.username
    $acrPassword = $acrCreds.passwords[0].value

    Write-Host "== Step 2/4: building $image from Dockerfile (ACR Tasks) =="
    $env:PYTHONIOENCODING = 'utf-8'
    az acr build --registry $AcrName --image "$($AppName):$ImageTag" --no-logs . | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "az acr build failed with exit code $LASTEXITCODE."
    }

    # Build the env-var list passed to the Container App. AZURE_CLIENT_ID tells
    # DefaultAzureCredential which user-assigned identity to use at runtime.
    $envVars = @(
        "AZURE_CLIENT_ID=$identityClientId",
        "BASIC_AUTH_USERNAME=$BasicAuthUsername",
        'BASIC_AUTH_PASSWORD=secretref:basic-auth-password',
        "AZURE_AI_PROJECT_ENDPOINT=$projectEndpoint",
        "AZURE_AI_MODEL_DEPLOYMENT=$modelDeployment",
        "ORCHESTRATOR_MODEL_CHOICES=$ModelChoices"
    )
    if (-not [string]::IsNullOrWhiteSpace($appInsights)) {
        $envVars += "APPLICATIONINSIGHTS_CONNECTION_STRING=$appInsights"
    }

    # Remove any app left in a Failed provisioning state by a previous run —
    # such an app cannot be updated out of that state and must be recreated.
    $existingState = az containerapp show --name $AppName --resource-group $ResourceGroup `
        --query properties.provisioningState -o tsv 2>$null
    if (-not [string]::IsNullOrWhiteSpace($existingState) -and $existingState -ne 'Succeeded') {
        Write-Host "== Step 3/4: removing stale app (provisioningState=$existingState) and recreating =="
        az containerapp delete --name $AppName --resource-group $ResourceGroup --yes --only-show-errors | Out-Null
        $existingState = $null
    }

    if ([string]::IsNullOrWhiteSpace($existingState)) {
        Write-Host "== Step 3/4: creating Container App '$AppName' with the user-assigned identity =="
        az containerapp create `
            --name $AppName `
            --resource-group $ResourceGroup `
            --environment $AcaEnvironment `
            --image $image `
            --target-port 8000 `
            --ingress external `
            --user-assigned $AppIdentityResourceId `
            --registry-server "$AcrName.azurecr.io" `
            --registry-username $acrUsername `
            --registry-password $acrPassword `
            --secrets "basic-auth-password=$plainPassword" `
            --env-vars $envVars `
            --only-show-errors | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "az containerapp create failed with exit code $LASTEXITCODE."
        }
    }
    else {
        Write-Host "== Step 3/4: updating existing Container App '$AppName' =="
        az containerapp identity assign --name $AppName --resource-group $ResourceGroup `
            --user-assigned $AppIdentityResourceId --only-show-errors | Out-Null
        az containerapp registry set --name $AppName --resource-group $ResourceGroup `
            --server "$AcrName.azurecr.io" --username $acrUsername --password $acrPassword --only-show-errors | Out-Null
        az containerapp secret set --name $AppName --resource-group $ResourceGroup `
            --secrets "basic-auth-password=$plainPassword" --only-show-errors | Out-Null
        az containerapp update `
            --name $AppName `
            --resource-group $ResourceGroup `
            --image $image `
            --set-env-vars $envVars `
            --only-show-errors | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "az containerapp update failed with exit code $LASTEXITCODE."
        }
    }

    Write-Host '== Step 4/4: resolving the app URL =='
    $fqdn = az containerapp show --name $AppName --resource-group $ResourceGroup `
        --query properties.configuration.ingress.fqdn -o tsv
    Write-Host ''
    Write-Host "Chat app deployed: https://$fqdn"
    Write-Host "Sign in with username '$BasicAuthUsername' and your chosen password."
}
finally {
    Pop-Location
}
