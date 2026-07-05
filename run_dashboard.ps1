Set-Location $PSScriptRoot

$env:FLASK_APP = "app.py"
$env:HOST = "0.0.0.0"
$env:PORT = "5000"

$pythonExe = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$pythonProcess = Start-Process -FilePath $pythonExe -ArgumentList "app.py" -WorkingDirectory $PSScriptRoot -PassThru
Start-Sleep -Seconds 2

$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -ne '127.0.0.1' -and $_.IPAddress -notlike '169.254.*' } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if (-not $ipAddress) {
    $ipAddress = "127.0.0.1"
}

Write-Host "Dashboard available at http://$ipAddress:5000"
Start-Process "http://$ipAddress:5000"
Wait-Process -Id $pythonProcess.Id