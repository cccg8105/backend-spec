# Wrapper PowerShell para backend-spec
$cliPath = Join-Path $PSScriptRoot "cli\main.py"
python $cliPath $args
