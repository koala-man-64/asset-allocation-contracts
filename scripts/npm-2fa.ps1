$otp = "07921789"
$userConfig = npm config get userconfig
$content = Get-Content -Raw $userConfig
if (-not ($content -match '//registry\.npmjs\.org/:_authToken=(.+)')) { throw 'npm auth token not found in ~/.npmrc' }
$token = $matches[1].Trim()
$headers = @{
  Authorization = "Bearer $token"
  Accept        = "application/json"
  "npm-otp"     = $otp
}
Invoke-WebRequest `
  -Uri 'https://registry.npmjs.org/-/package/%40asset-allocation%2Fcontracts/trust' `
  -Headers $headers `
  -Method GET `
  -UseBasicParsing | Select-Object -ExpandProperty Content
