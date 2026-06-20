<#
.SYNOPSIS
    Seed (ingest) the Zava workshop data foundation into Azure Cosmos DB.

.DESCRIPTION
    Companion to the deploy-*-mcp.ps1 scripts. Where those ship the MCP server
    *code* to Azure Container Apps, this script ingests the MCP server *data*
    into Cosmos DB by running the workshop's deterministic Python seeders:

        src.mcp_servers.sales.seed.seed_cosmos
        src.mcp_servers.inventory.seed.seed_cosmos
        src.mcp_servers.marketing.seed.seed_cosmos

    Each seeder creates its container (partition key /id) if missing and upserts
    a fixed, reproducible set of documents, so re-running is idempotent.

    Resource values are read from the workshop .env (written by the infra repo's
    Part B load-data.ps1) unless passed explicitly. Authentication to Cosmos is
    passwordless via DefaultAzureCredential, so the operator running this needs
    the Cosmos DB Built-in Data Contributor data-plane role on the account. Pass
    -GrantOperatorAccess to grant it to the signed-in user (or -OperatorObjectId)
    before seeding.

.PARAMETER Service
    Which container(s) to seed: all (default), sales, inventory, or marketing.

.PARAMETER GrantOperatorAccess
    Grant the operator the Cosmos DB Built-in Data Contributor role on the
    account before seeding. Use this for a fresh, standalone run; the infra
    repo's load-data.ps1 already grants it during a full deployment.

.EXAMPLE
    ./scripts/seed-cosmos.ps1

.EXAMPLE
    ./scripts/seed-cosmos.ps1 -Service inventory

.EXAMPLE
    ./scripts/seed-cosmos.ps1 -GrantOperatorAccess
#>
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('all', 'sales', 'inventory', 'marketing')]
    [string]$Service = 'all',

    [Parameter(Mandatory = $false)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $false)]
    [string]$CosmosAccount,

    [Parameter(Mandatory = $false)]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $false)]
    [string]$OperatorObjectId,

    [Parameter(Mandatory = $false)]
    [string]$EnvFile = '.env',

    [switch]$GrantOperatorAccess
)

$ErrorActionPreference = 'Stop'

# Reuse the .env helpers the MCP deploy scripts use (Get-DotEnvValues,
# Get-RequiredValue) so resource resolution stays consistent.
. "$PSScriptRoot/_mcp_deploy_common.ps1"

# service -> python seeder module
$Seeders = [ordered]@{
    sales     = 'src.mcp_servers.sales.seed.seed_cosmos'
    inventory = 'src.mcp_servers.inventory.seed.seed_cosmos'
    marketing = 'src.mcp_servers.marketing.seed.seed_cosmos'
}

function Get-CosmosAccountName {
    param([string]$Explicit, [string]$Endpoint)
    if (-not [string]::IsNullOrWhiteSpace($Explicit)) {
        return $Explicit
    }
    # https://<account>.documents.azure.com:443/  ->  <account>
    if ($Endpoint -match '^https?://([^.]+)\.documents\.azure\.com') {
        return $matches[1]
    }
    return $null
}

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not (Test-Path 'src/mcp_servers')) {
        throw "Run this from the ai-agents-workshop repo (src/mcp_servers not found)."
    }

    $envValues = Get-DotEnvValues -Path $EnvFile

    if ($SubscriptionId) {
        az account set --subscription $SubscriptionId | Out-Null
    }
    elseif ($envValues['AZURE_SUBSCRIPTION_ID']) {
        az account set --subscription $envValues['AZURE_SUBSCRIPTION_ID'] | Out-Null
    }

    $cosmosEndpoint = Get-RequiredValue '' $envValues 'COSMOS_ENDPOINT'  'Cosmos endpoint'  $EnvFile
    $cosmosDatabase = Get-RequiredValue '' $envValues 'COSMOS_DATABASE'  'Cosmos database'  $EnvFile

    Write-Host "Cosmos endpoint : $cosmosEndpoint"
    Write-Host "Cosmos database : $cosmosDatabase"

    # --- Optional: grant the operator the Cosmos data-plane role ------------
    if ($GrantOperatorAccess) {
        $ResourceGroup = Get-RequiredValue $ResourceGroup $envValues 'AZURE_RESOURCE_GROUP' 'Resource group' $EnvFile
        $CosmosAccount = Get-CosmosAccountName $CosmosAccount $cosmosEndpoint
        if ([string]::IsNullOrWhiteSpace($CosmosAccount)) {
            throw "Could not resolve the Cosmos account name. Pass -CosmosAccount explicitly."
        }
        if ([string]::IsNullOrWhiteSpace($OperatorObjectId)) {
            $OperatorObjectId = az ad signed-in-user show --query id -o tsv 2>$null
        }
        if ([string]::IsNullOrWhiteSpace($OperatorObjectId)) {
            throw "Could not resolve an operator object id. Pass -OperatorObjectId explicitly."
        }

        Write-Host "== Granting Cosmos DB Built-in Data Contributor to operator =="
        az cosmosdb sql role assignment create `
            --resource-group $ResourceGroup `
            --account-name $CosmosAccount `
            --role-definition-id '00000000-0000-0000-0000-000000000002' `
            --principal-id $OperatorObjectId `
            --scope '/' `
            --only-show-errors | Out-Null
        Write-Host "  Data Contributor -> $CosmosAccount (operator $OperatorObjectId)"
        Write-Host '  Waiting 30s for the role assignment to propagate...'
        # Start-Sleep -Seconds 30
    }

    # --- Seed the requested container(s) ------------------------------------
    $targets = if ($Service -eq 'all') { @($Seeders.Keys) } else { @($Service) }

    foreach ($svc in $targets) {
        $module = $Seeders[$svc]
        Write-Host ""
        Write-Host "== Seeding '$svc' container ($module) =="
        python -m $module
        if ($LASTEXITCODE -ne 0) {
            throw "Seeding '$svc' failed with exit code $LASTEXITCODE."
        }
    }

    Write-Host ""
    Write-Host "Cosmos data ingestion complete for: $($targets -join ', ')."
}
finally {
    Pop-Location
}
