Write-Host ""
Write-Host "Restoring frontend npm packages"
Write-Host ""
Set-Location ./frontend
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
Write-Host "Restoring backend python packages"
Write-Host ""
Set-Location ../backend
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to restore backend python packages"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Starting backend"
Write-Host ""
Start-Process http://127.0.0.1:8765
python app.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start backend"
    exit $LASTEXITCODE
}
