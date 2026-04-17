param(
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [string]$RepoRoot = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
} else {
    $RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
}

$versionPattern = '^\d+\.\d+\.\d+$'
if ($Version -notmatch $versionPattern) {
    throw "Version '$Version' is not valid stable semver. Use values like 1.2.3."
}

$pythonPath = Join-Path $RepoRoot "python\pyproject.toml"
$tsPath = Join-Path $RepoRoot "ts\package.json"

foreach ($path in @($pythonPath, $tsPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required file not found: $path"
    }
}

function Get-VersionMatch {
    param(
        [Parameter(Mandatory = $true)][string]$Content,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Label
    )

    $match = [regex]::Match($Content, $Pattern)
    if (-not $match.Success) {
        throw "Could not locate version field in $Label."
    }
    return $match
}

function Set-VersionValue {
    param(
        [Parameter(Mandatory = $true)][string]$Content,
        [Parameter(Mandatory = $true)][System.Text.RegularExpressions.Match]$Match,
        [Parameter(Mandatory = $true)][string]$NewVersion
    )

    $prefix = $Content.Substring(0, $Match.Index)
    $suffix = $Content.Substring($Match.Index + $Match.Length)
    return $prefix + $Match.Groups[1].Value + $NewVersion + $Match.Groups[3].Value + $suffix
}

$pythonContent = Get-Content -LiteralPath $pythonPath -Raw
$tsContent = Get-Content -LiteralPath $tsPath -Raw

$pythonMatch = Get-VersionMatch -Content $pythonContent -Pattern '(?m)^(version\s*=\s*")([^"]+)(")\s*$' -Label $pythonPath
try {
    $tsPackageJson = $tsContent | ConvertFrom-Json
} catch {
    throw "Could not parse JSON in $tsPath. $($_.Exception.Message)"
}

if ($null -eq $tsPackageJson.PSObject.Properties["version"]) {
    throw "Could not locate version field in $tsPath."
}

$currentPythonVersion = $pythonMatch.Groups[2].Value
$currentTsVersion = [string]$tsPackageJson.version

Write-Host "Python version: $currentPythonVersion"
Write-Host "TypeScript version: $currentTsVersion"
Write-Host "Target version: $Version"

if ($currentPythonVersion -eq $Version -and $currentTsVersion -eq $Version) {
    Write-Host "Both package versions are already set to $Version."
    return
}

$updatedPython = Set-VersionValue -Content $pythonContent -Match $pythonMatch -NewVersion $Version
$tsPackageJson.version = $Version
$updatedTs = $tsPackageJson | ConvertTo-Json -Depth 100
if (-not $updatedTs.EndsWith("`n")) {
    $updatedTs += "`n"
}

if ($DryRun) {
    Write-Host "Dry run: no files were changed."
    return
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($pythonPath, $updatedPython, $utf8NoBom)
[System.IO.File]::WriteAllText($tsPath, $updatedTs, $utf8NoBom)

Write-Host "Updated release version to $Version in:"
Write-Host " - $pythonPath"
Write-Host " - $tsPath"
Write-Host "Next step: review the diff, commit, and publish version $Version."
