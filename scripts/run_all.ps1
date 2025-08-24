# PowerShell runner
$ErrorActionPreference = "Stop"

Start-Process -FilePath "python" -ArgumentList "hub\py\hub.py"
Start-Sleep -Seconds 1

Start-Process -FilePath "python" -ArgumentList "tools\recorder.py"
Start-Process -FilePath "python" -ArgumentList "devices\python\sensor.py"

Start-Process -FilePath "go" -ArgumentList "run devices\go\thermostat\main.go"
Start-Process -FilePath "node" -ArgumentList "devices\js\lightbulb.js"

# Java
Set-Location devices\java
javac LockDevice.java
Start-Process -FilePath "java" -ArgumentList "LockDevice"
Set-Location ..\..\

Write-Host "All processes started. Switch to the hub console window to type commands."
