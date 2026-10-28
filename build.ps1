param(
    [ValidateSet('mac', 'windows')]
    [string]$Target = 'windows'
)
$ErrorActionPreference = 'Stop'
$context = Join-Path $PSScriptRoot 'maya_studio'
if ($Target -eq 'mac') {
    docker build -f (Join-Path $context 'Dockerfile.mac') -t maya-voice-studio-mac $context
} else {
    docker build --platform linux/amd64 -f (Join-Path $context 'Dockerfile.cuda') -t maya-voice-studio-windows $context
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
