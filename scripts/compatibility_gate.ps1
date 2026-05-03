param(
  [string]$ControlPlaneRepo,
  [string]$JobsRepo,
  [string]$UiRepo
)

$ErrorActionPreference = "Stop"

$contractsRepo = Split-Path -Parent $PSScriptRoot
$projectsRoot = Split-Path -Parent $contractsRepo
if (-not $ControlPlaneRepo) {
  $ControlPlaneRepo = Join-Path $projectsRoot "asset-allocation-control-plane"
}
if (-not $JobsRepo) {
  $JobsRepo = Join-Path $projectsRoot "asset-allocation-jobs"
}
if (-not $UiRepo) {
  $UiRepo = Join-Path $projectsRoot "asset-allocation-ui"
}
$contractsPythonRepo = Join-Path $contractsRepo "python"
$contractsTsRepo = Join-Path $contractsRepo "ts"

function Invoke-Checked {
  param(
    [Parameter(Mandatory = $true)]
    [string]$FilePath,
    [string[]]$ArgumentList = @()
  )

  & $FilePath @ArgumentList
  if ($LASTEXITCODE -ne 0) {
    throw "$FilePath $($ArgumentList -join ' ') failed with exit code $LASTEXITCODE"
  }
}

Write-Host "Installing shared Python contracts package..."
Push-Location $contractsPythonRepo
Invoke-Checked "python" @("-m", "pip", "install", "-e", ".")
Invoke-Checked "python" @("scripts\export_schemas.py")
Pop-Location

Write-Host "Typechecking shared TypeScript contracts package..."
Push-Location $contractsTsRepo
Invoke-Checked "corepack" @("pnpm", "install", "--no-frozen-lockfile")
Invoke-Checked "corepack" @("pnpm", "typecheck")
Pop-Location

Write-Host "Running contracts tests..."
Push-Location $contractsRepo
Invoke-Checked "python" @("-m", "pytest", "tests\python\test_contract_models.py", "-q")
Pop-Location

Write-Host "Running control-plane compatibility checks..."
Push-Location $ControlPlaneRepo
Invoke-Checked "python" @("scripts\automation\export_contract_artifacts.py")
Invoke-Checked "python" @("-m", "pytest", "tests\api\test_config_js_contract.py", "tests\api\test_internal_endpoints.py", "-q")
Pop-Location

Write-Host "Running jobs compatibility checks..."
Push-Location $JobsRepo
Invoke-Checked "python" @(
  "-m",
  "pytest",
  "tests\core\test_control_plane_transport.py",
  "tests\core\test_strategy_repository.py",
  "tests\core\test_ranking_repository.py",
  "tests\core\test_universe_repository.py",
  "tests\core\test_regime_repository.py",
  "tests\core\test_backtest_repository.py",
  "-q"
)
Pop-Location

Write-Host "Running UI compatibility checks..."
Push-Location $UiRepo
Invoke-Checked "corepack" @("pnpm", "install", "--no-frozen-lockfile")
Invoke-Checked "corepack" @("pnpm", "build")
Invoke-Checked "corepack" @(
  "pnpm",
  "vitest",
  "run",
  "src\app\__tests__\App.auth.test.tsx",
  "src\contexts\__tests__\AuthContext.test.tsx",
  "src\services\__tests__\apiService.test.ts",
  "src\hooks\useRealtime.test.tsx"
)
Pop-Location

Write-Host "Cross-repo compatibility gate passed."
