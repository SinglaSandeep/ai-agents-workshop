<#
.SYNOPSIS
    Build and deploy the Zava INVENTORY MCP server to Azure Container Apps.

.DESCRIPTION
    Ships src/mcp_servers/inventory (FastMCP, streamable HTTP) to the ACA
    environment as the 'zava-inventory-mcp' Container App with external ingress
    so the Foundry agents can reach it by URL.

    Uses key-based auth throughout: the image is pulled with the ACR admin
    username/password, and Cosmos is accessed with the account key (injected as
    the COSMOS_KEY Container App secret). No managed identity is attached.

    Resource names are read from the workshop .env (written by the infra repo's
    Part B load-data.ps1) unless passed explicitly. Idempotent: create on first
    run, update after.

.EXAMPLE
    ./scripts/deploy-inventory-mcp.ps1
#>
param(
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroup,

    [Parameter(Mandatory = $false)]
    [string]$AcrName,

    [Parameter(Mandatory = $false)]
    [string]$AcaEnvironment,

    [Parameter(Mandatory = $false)]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $false)]
    [string]$ImageTag = 'latest',

    [Parameter(Mandatory = $false)]
    [string]$EnvFile = '.env'
)

$ErrorActionPreference = 'Stop'

# ---- This server's deployment shape -----------------------------------------
$Service          = 'inventory'
$AppName          = 'zava-inventory-mcp'
$Port             = 8004
$ContainerEnvKey  = 'COSMOS_INVENTORY_CONTAINER'
$UrlEnvKey        = 'INVENTORY_MCP_URL'
# -----------------------------------------------------------------------------

. "$PSScriptRoot/_mcp_deploy_common.ps1"

Invoke-McpServerDeploy `
    -Service $Service -AppName $AppName -Port $Port `
    -ContainerEnvKey $ContainerEnvKey -UrlEnvKey $UrlEnvKey `
    -ResourceGroup $ResourceGroup -AcrName $AcrName -AcaEnvironment $AcaEnvironment `
    -SubscriptionId $SubscriptionId -ImageTag $ImageTag -EnvFile $EnvFile
