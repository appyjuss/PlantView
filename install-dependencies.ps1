# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Green
Set-Location "backend"
pip install --upgrade pip
pip install -r requirements.txt
Set-Location ".."

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Green
Set-Location "plantViewFrontend"
npm install
Set-Location ".."

Write-Host "Installation complete!" -ForegroundColor Green
