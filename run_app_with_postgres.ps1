# PowerShell script to run app with PostgreSQL
Write-Host "Setting DATABASE_URL..." -ForegroundColor Cyan
$env:DATABASE_URL="postgresql://postgres:avinash@localhost:5432/retail_db"
Write-Host ""
Write-Host "Starting application..." -ForegroundColor Green
Write-Host ""
python app.py

