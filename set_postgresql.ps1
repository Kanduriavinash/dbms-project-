# PowerShell script to set PostgreSQL connection
# Run this BEFORE running python app.py

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Setup for RIMS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get PostgreSQL details
$username = Read-Host "PostgreSQL Username [postgres]"
if ([string]::IsNullOrWhiteSpace($username)) { $username = "postgres" }

$password = Read-Host "PostgreSQL Password" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

$host = Read-Host "Host [localhost]"
if ([string]::IsNullOrWhiteSpace($host)) { $host = "localhost" }

$port = Read-Host "Port [5432]"
if ([string]::IsNullOrWhiteSpace($port)) { $port = "5432" }

$database = Read-Host "Database Name [rims_db]"
if ([string]::IsNullOrWhiteSpace($database)) { $database = "rims_db" }

# Build connection string
$databaseUrl = "postgresql://${username}:${passwordPlain}@${host}:${port}/${database}"

# Set environment variable
$env:DATABASE_URL = $databaseUrl

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "DATABASE_URL SET!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Connection string: $databaseUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "Now run:" -ForegroundColor Cyan
Write-Host "  python check_database.py" -ForegroundColor White
Write-Host "  python app.py" -ForegroundColor White
Write-Host ""

