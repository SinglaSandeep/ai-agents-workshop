<#
.SYNOPSIS
    Build and register the Zava Inventory **hosted** agent on Foundry (no azd).

.DESCRIPTION
    The no-azd, az + Python deploy path for the hosted Inventory agent:

      1. Build src/hosted (Agent Framework + ResponsesHostServer) into ACR.
      2. Register a Foundry agent **version** that points at the image, via
         scripts/register_inventory_hosted.py (HostedAgentDefinition).

    Runtime identity: the container authenticates as the user-assigned identity
    'id-zava-workload' (APP_IDENTITY_CLIENT_ID), injected as AZURE_CLIENT_ID by
    the registration script. That identity already holds the model/Foundry roles
    and AcrPull on the ACR, so no role assignment is performed here.

    Values are read from the workshop .env unless passed explicitly. The
    declarative Prompt Agent (zava-inventory-agent) is untouched; Magentic keeps
    calling it. This registers a separate hosted agent for side-by-side demo.

.EXAMPLE
    ./scripts/deploy-inventory-hosted.ps1

.EXAMPLE
    ./scripts/deploy-inventory-hosted.ps1 -ImageTag v2 -SkipBuild
#>
param(
    [Parameter(Mandatory = $false)] [string]$ResourceGroup,
    [Parameter(Mandatory = $false)] [string]$AcrName,
    [Parameter(Mandatory = $false)] [string]$SubscriptionId,
    [Parameter(Mandatory = $false)] [string]$ImageTag = 'latest',
    [Parameter(Mandatory = $false)] [string]$EnvFile = '.env',
    [Parameter(Mandatory = $false)] [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'

function Get-DotEnvValues {
    param([string]$Path)
    $values = @{}
    if (-not (Test-Path $Path)) { return $values }
    foreach ($line in (Get-Content $Path)) {
        $trimmed = $line.Trim()
        if ($trimmed -eq '' -or $trimmed.StartsWith('#')) { continue }
        if ($trimmed -match '^([^=]+)=(.*)$') {
            $values[$matches[1].Trim()] = $matches[2].Trim().Trim('"')
        }
    }
    return $values
}

function Get-RequiredValue {
    param([string]$Explicit, [hashtable]$EnvValues, [string]$Key, [string]$Friendly, [string]$EnvFile)
    if (-not [string]::IsNullOrWhiteSpace($Explicit)) { return $Explicit }
    $fromEnv = $EnvValues[$Key]
    if ([string]::IsNullOrWhiteSpace($fromEnv)) {
        throw "$Friendly not found. Pass it explicitly or set $Key in $EnvFile."
    }
    return $fromEnv
}

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $dockerfile = 'src/hosted/Dockerfile'
    if (-not (Test-Path $dockerfile)) {
        throw "Dockerfile not found at '$dockerfile'. Run this from the ai-agents-workshop repo."
    }

    # Resolve a usable Python: prefer the active venv, then the repo .venv, then
    # whatever 'python'/'py' is on PATH (avoids the Windows Store stub).
    $python = $null
    $candidates = @()
    if ($env:VIRTUAL_ENV) { $candidates += (Join-Path $env:VIRTUAL_ENV 'Scripts/python.exe') }
    $candidates += (Join-Path $projectRoot '.venv/Scripts/python.exe')
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) { $python = $candidate; break }
    }
    if (-not $python) {
        foreach ($name in @('python', 'py')) {
            $cmd = Get-Command $name -ErrorAction SilentlyContinue |
                Where-Object { $_.Source -notlike '*WindowsApps*' } | Select-Object -First 1
            if ($cmd) { $python = $cmd.Source; break }
        }
    }
    if (-not $python) {
        throw "No usable Python found. Activate the venv (.venv\Scripts\Activate.ps1) or install Python."
    }

    $envValues = Get-DotEnvValues -Path $EnvFile

    if ($SubscriptionId) {
        az account set --subscription $SubscriptionId | Out-Null
    }
    elseif ($envValues['AZURE_SUBSCRIPTION_ID']) {
        az account set --subscription $envValues['AZURE_SUBSCRIPTION_ID'] | Out-Null
    }

    $AcrName       = Get-RequiredValue $AcrName       $envValues 'ACR_NAME'             'ACR name'       $EnvFile
    $agentName     = Get-RequiredValue ''             $envValues 'INVENTORY_HOSTED_AGENT_NAME' 'Hosted agent name' $EnvFile

    $image = "$AcrName.azurecr.io/$($agentName):$ImageTag"

    # ---- Step 1: build the image into ACR ----------------------------------
    if ($SkipBuild) {
        Write-Host "== Step 1/2: skipping build (using existing $image) =="
    }
    else {
        Write-Host "== Step 1/2: building $image (ACR Tasks) =="
        $env:PYTHONIOENCODING = 'utf-8'
        az acr build --registry $AcrName --image "$($agentName):$ImageTag" --file $dockerfile --no-logs . | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "az acr build failed with exit code $LASTEXITCODE. (On Windows the log stream can crash even when the server-side build succeeds — verify with: az acr repository show-tags -n $AcrName --repository $agentName)"
        }
    }

    # ---- Step 2: register the hosted agent version -------------------------
    Write-Host '== Step 2/2: registering the Foundry hosted agent version =='
    & $python scripts/register_inventory_hosted.py --image $image
    if ($LASTEXITCODE -ne 0) {
        throw "register_inventory_hosted.py failed with exit code $LASTEXITCODE."
    }

    Write-Host ''
    Write-Host "Hosted agent '$agentName' deployed from $image."
    Write-Host "Invoke via the Responses API: model=$agentName (project.get_openai_client(agent_name='$agentName'))."
}
finally {
    Pop-Location
}
