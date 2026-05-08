param(
    [string]$OrganizationUrl = "https://dev.azure.com/rdprokes",
    [string]$Project = "AdaptiveAssetAllocation",
    [string]$VariableGroup = "vg-aa-packaging",
    [string]$EnvFilePath,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$envPath = if ($EnvFilePath) { $EnvFilePath } else { Join-Path $repoRoot ".env.web" }
$contractPath = Join-Path $repoRoot "docs\ops\env-contract.csv"

function Parse-EnvFile {
    param([string]$Path)
    $map = @{}
    foreach ($rawLine in (Get-Content $Path)) {
        $line = $rawLine.Trim()
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#") -or $line -notmatch "^([^=]+)=(.*)$") { continue }
        $map[$matches[1].Trim()] = $matches[2]
    }
    return $map
}

function Load-EnvContract {
    param([string]$Path)
    if (-not (Test-Path $Path)) { throw "Env contract not found at $Path" }
    $map = @{}
    foreach ($row in (Import-Csv -Path $Path)) {
        $name = (($row.name | Out-String).Trim())
        if ($name) { $map[$name] = $row }
    }
    return $map
}

function Get-VariableGroupId {
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) { throw "Azure CLI (az) is required to sync Azure DevOps variables." }
    $groupId = az pipelines variable-group list `
        --organization $OrganizationUrl `
        --project $Project `
        --group-name $VariableGroup `
        --query "[0].id" `
        --output tsv
    if ([string]::IsNullOrWhiteSpace($groupId)) { throw "Azure DevOps variable group '$VariableGroup' was not found in project '$Project'." }
    return $groupId.Trim()
}

function Set-AdoVariable {
    param([string]$GroupId, [string]$Name, [string]$Value)
    if ($DryRun) {
        Write-Host "[DRY RUN] Would set Azure DevOps variable $Name in $VariableGroup"
        return
    }
    $common = @("--organization", $OrganizationUrl, "--project", $Project, "--group-id", $GroupId, "--name", $Name)
    $updateOutput = az pipelines variable-group variable update @common --value $Value --output none 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Updated Azure DevOps variable: $Name" -ForegroundColor Green
        return
    }
    az pipelines variable-group variable create @common --value $Value --output none
    Write-Host "Created Azure DevOps variable: $Name" -ForegroundColor Green
}

if (-not (Test-Path $envPath)) { throw ".env.web not found at $envPath. Run scripts/setup-env.ps1 first." }

$envMap = Parse-EnvFile -Path $envPath
$contractMap = Load-EnvContract -Path $contractPath
$undocumented = @($envMap.Keys | Where-Object { -not $contractMap.ContainsKey($_) } | Sort-Object -Unique)
if ($undocumented.Count -gt 0) { throw ".env.web contains undocumented keys: $($undocumented -join ', ')" }

$groupId = Get-VariableGroupId
foreach ($key in ($contractMap.Keys | Sort-Object)) {
    $entry = $contractMap[$key]
    $storage = (($entry.ado_storage | Out-String).Trim()).ToLowerInvariant()
    if ($storage -eq "feed") {
        Write-Host "Skipping feed-managed setting: $key"
        continue
    }
    if ($storage -in @("keyvault", "secret")) {
        Write-Host "Skipping Key Vault-backed secret: $key"
        continue
    }
    if ($storage -ne "variable") { continue }
    $value = if ($envMap.ContainsKey($key)) { $envMap[$key] } else { "" }
    if ([string]::IsNullOrWhiteSpace($value)) {
        Write-Host "Skipping empty Azure DevOps variable: $key" -ForegroundColor Yellow
        continue
    }
    Set-AdoVariable -GroupId $groupId -Name $key -Value $value
}
