# Telegram Bot - Windows Service Installation Script
# Run as Administrator

Write-Host "=========================================="
Write-Host "Telegram Bot - Windows Service Setup"
Write-Host "=========================================="

# Check Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Administrator privileges required!" -ForegroundColor Red
    exit 1
}

$installPath = "C:\BaoCaoBot"
$serviceName = "TelegramBot"

# Check directory
if (-not (Test-Path $installPath)) {
    Write-Host "ERROR: Directory $installPath does not exist!" -ForegroundColor Red
    Write-Host "Please run setup_windows.ps1 first" -ForegroundColor Yellow
    exit 1
}

Set-Location $installPath

# Check credentials.json and .env
if (-not (Test-Path "credentials.json")) {
    Write-Host "ERROR: credentials.json file not found!" -ForegroundColor Red
    Write-Host "Please copy this file to $installPath" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file from .env.example" -ForegroundColor Yellow
    exit 1
}

# Check NSSM
$nssmPath = "$installPath\nssm\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "ERROR: NSSM not installed!" -ForegroundColor Red
    Write-Host "Please run setup_windows.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Remove existing service if exists
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Service $serviceName already exists, removing..." -ForegroundColor Yellow
    & $nssmPath stop $serviceName
    Start-Sleep -Seconds 2
    & $nssmPath remove $serviceName confirm
}

# Install new service
Write-Host ""
Write-Host "Installing Windows Service..." -ForegroundColor Cyan

$pythonPath = "$installPath\.venv\Scripts\python.exe"
$appPath = "$installPath\app\main.py"

& $nssmPath install $serviceName $pythonPath "-m" "app.main"
& $nssmPath set $serviceName AppDirectory $installPath
& $nssmPath set $serviceName DisplayName "Telegram Work Progress Bot"
& $nssmPath set $serviceName Description "Work progress reporting bot from Google Sheets"
& $nssmPath set $serviceName Start SERVICE_AUTO_START

# Configure logging
& $nssmPath set $serviceName AppStdout "$installPath\logs\service.log"
& $nssmPath set $serviceName AppStderr "$installPath\logs\service-error.log"

# Configure restart
& $nssmPath set $serviceName AppExit Default Restart
& $nssmPath set $serviceName AppRestartDelay 5000

Write-Host ""
Write-Host "=========================================="
Write-Host "SERVICE INSTALLATION COMPLETED!"
Write-Host "=========================================="

Write-Host ""
Write-Host "Service Management Commands:" -ForegroundColor Yellow
Write-Host "  nssm\nssm.exe start $serviceName      # Start bot"
Write-Host "  nssm\nssm.exe stop $serviceName       # Stop bot"
Write-Host "  nssm\nssm.exe restart $serviceName    # Restart bot"
Write-Host "  nssm\nssm.exe status $serviceName     # Check status"
Write-Host ""
Write-Host "Or use Windows Services:" -ForegroundColor Yellow
Write-Host "  services.msc" -ForegroundColor Cyan
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Yellow
Write-Host "  Get-Content logs\bot.log -Tail 50 -Wait"
Write-Host ""

# Ask if user wants to start now
$response = Read-Host "Start bot now? (y/n)"
if ($response -eq 'y') {
    Write-Host ""
    Write-Host "Starting bot..." -ForegroundColor Cyan
    & $nssmPath start $serviceName
    Start-Sleep -Seconds 3
    
    $status = & $nssmPath status $serviceName
    Write-Host "Status: $status" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Check logs:" -ForegroundColor Yellow
    Write-Host "  Get-Content logs\bot.log -Tail 20"
}
