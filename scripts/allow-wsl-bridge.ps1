param(
  [int]$Port = 8787
)

$ErrorActionPreference = "Stop"
$ruleName = "MuseIQ WSL Bridge $Port"
$wslCreatorId = "{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}"

function Test-IsAdmin {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($identity)
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-IsAdmin)) {
  throw "Ejecuta este script desde PowerShell como Administrador."
}

Get-NetFirewallHyperVRule -Name $ruleName -ErrorAction SilentlyContinue |
  Remove-NetFirewallHyperVRule

New-NetFirewallHyperVRule `
  -Name $ruleName `
  -DisplayName $ruleName `
  -Direction Inbound `
  -VMCreatorId $wslCreatorId `
  -Protocol TCP `
  -LocalPorts $Port

Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue |
  Remove-NetFirewallRule

New-NetFirewallRule `
  -DisplayName $ruleName `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalPort $Port `
  -Profile Any | Out-Null

Write-Host "Puerto TCP $Port habilitado para MuseIQ en WSL."
