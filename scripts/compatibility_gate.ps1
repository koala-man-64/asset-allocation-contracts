param()

$ErrorActionPreference = "Stop"

$contractsRepo = Split-Path -Parent $PSScriptRoot
$projectsRoot = Split-Path -Parent $contractsRepo
$controlPlaneRepo = Join-Path $projectsRoot "asset-allocation-control-plane"
$jobsRepo = Join-Path $projectsRoot "asset-allocation-jobs"
$uiRepo = Join-Path $projectsRoot "asset-allocation-ui"
$contractsPythonRepo = Join-Path $contractsRepo "python"
$contractsTsRepo = Join-Path $contractsRepo "ts"

Write-Host "Installing shared Python contracts package..."
Push-Location $contractsPythonRepo
python -m pip install -e .
python scripts\export_schemas.py
Pop-Location

Write-Host "Typechecking shared TypeScript contracts package..."
Push-Location $contractsTsRepo
corepack pnpm install --no-frozen-lockfile
corepack pnpm typecheck
Pop-Location

Write-Host "Running contracts tests..."
Push-Location $contractsRepo
python -m pytest tests\python\test_contract_models.py -q
Pop-Location

Write-Host "Running control-plane compatibility checks..."
Push-Location $controlPlaneRepo
python scripts\export_contract_artifacts.py
python -m pytest tests\api\test_config_js_contract.py tests\api\test_internal_endpoints.py -q
Pop-Location

Write-Host "Running jobs compatibility checks..."
Push-Location $jobsRepo
python -m pytest `
  tests\core\test_control_plane_transport.py `
  tests\core\test_strategy_repository.py `
  tests\core\test_ranking_repository.py `
  tests\core\test_universe_repository.py `
  tests\core\test_regime_repository.py `
  tests\core\test_backtest_repository.py `
  -q
Pop-Location

Write-Host "Running UI compatibility checks..."
Push-Location $uiRepo
corepack pnpm install --no-frozen-lockfile
corepack pnpm build
corepack pnpm vitest run `
  src\app\__tests__\App.auth.test.tsx `
  src\contexts\__tests__\AuthContext.test.tsx `
  src\services\__tests__\apiService.test.ts `
  src\hooks\useRealtime.test.tsx
Pop-Location

Write-Host "Cross-repo compatibility gate passed."
