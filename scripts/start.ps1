./scripts/load_python_env.ps1

Write-Host ""
Write-Host "Restoring frontend npm packages"
Write-Host ""
Set-Location ./app/frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to restore frontend npm packages"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Building frontend"
Write-Host ""
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build frontend"
    exit $LASTEXITCODE
}


Write-Host ""
Write-Host "Starting backend"
Write-Host ""
Set-Location ../backend
$venvPythonPath = "./.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./.venv/bin/python"
}
Start-Process -FilePath $venvPythonPath -ArgumentList "-m app" -Wait -NoNewWindow
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start backend"
    exit $LASTEXITCODE
}
