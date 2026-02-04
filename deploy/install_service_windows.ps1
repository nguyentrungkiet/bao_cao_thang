# Script cai dat Telegram Bot nhu Windows Service
# Chay voi quyen Administrator

Write-Host "=========================================="
Write-Host "Cai dat Telegram Bot Windows Service"
Write-Host "==========================================" -ForegroundColor Green

# Kiem tra quyen Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Can chay script nay voi quyen Administrator!" -ForegroundColor Red
    exit 1
}

$installPath = "C:\BaoCaoBot"
$serviceName = "TelegramBot"

# Kiem tra thu muc
if (-not (Test-Path $installPath)) {
    Write-Host "Thu muc $installPath khong ton tai!" -ForegroundColor Red
    Write-Host "Vui long chay setup_windows.ps1 truoc" -ForegroundColor Yellow
    exit 1
}

Set-Location $installPath

# Kiem tra credentials.json va .env
if (-not (Test-Path "credentials.json")) {
    Write-Host "Chua co file credentials.json!" -ForegroundColor Red
    Write-Host "Vui long copy file nay vao thu muc $installPath" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Host "Chua co file .env!" -ForegroundColor Red
    Write-Host "Vui long tao file .env tu .env.example" -ForegroundColor Yellow
    exit 1
}

# Kiem tra NSSM
$nssmPath = "$installPath\nssm\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "NSSM chua duoc cai dat!" -ForegroundColor Red
    Write-Host "Vui long chay setup_windows.ps1 truoc" -ForegroundColor Yellow
    exit 1
}

# Xoa service cu neu co
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Service $serviceName da ton tai, dang xoa..." -ForegroundColor Yellow
    & $nssmPath stop $serviceName
    Start-Sleep -Seconds 2
    & $nssmPath remove $serviceName confirm
}

# Cai dat service moi
Write-Host ""
Write-Host "Dang cai dat Windows Service..." -ForegroundColor Cyan

$pythonPath = "$installPath\.venv\Scripts\python.exe"
$appPath = "$installPath\app\main.py"

& $nssmPath install $serviceName $pythonPath "-m" "app.main"
& $nssmPath set $serviceName AppDirectory $installPath
& $nssmPath set $serviceName DisplayName "Telegram Work Progress Bot"
& $nssmPath set $serviceName Description "Bot báo cáo tiến độ công việc từ Google Sheets"
& $nssmPath set $serviceName Start SERVICE_AUTO_START

# Cấu hình stdout/stderr
& $nssmPath set $serviceName AppStdout "$installPath\logs\service.log"
& $nssmPath set $serviceName AppStderr "$installPath\logs\service-error.log"

# Cau hinh restart
& $nssmPath set $serviceName AppExit Default Restart
& $nssmPath set $serviceName AppRestartDelay 5000

Write-Host ""
Write-Host "=========================================="
Write-Host "CAI DAT SERVICE HOAN TAT!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host ""
Write-Host "Cac lenh quan ly service:" -ForegroundColor Yellow
Write-Host "  nssm\nssm.exe start $serviceName      # Khoi dong bot"
Write-Host "  nssm\nssm.exe stop $serviceName       # Dung bot"
Write-Host "  nssm\nssm.exe restart $serviceName    # Khoi dong lai bot"
Write-Host "  nssm\nssm.exe status $serviceName     # Xem trang thai"
Write-Host ""
Write-Host "Hoac dung Windows Services:" -ForegroundColor Yellow
Write-Host "  services.msc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Xem logs:" -ForegroundColor Yellow
Write-Host "  Get-Content logs\bot.log -Tail 50 -Wait"
Write-Host ""

# Hoi co muon khoi dong ngay khong
$response = Read-Host "Khoi dong bot ngay bay gio? (y/n)"
if ($response -eq 'y') {
    Write-Host ""
    Write-Host "Dang khoi dong bot..." -ForegroundColor Cyan
    & $nssmPath start $serviceName
    Start-Sleep -Seconds 3
    
    $status = & $nssmPath status $serviceName
    Write-Host "Trang thai: $status" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Xem logs de kiem tra:" -ForegroundColor Yellow
    Write-Host "  Get-Content logs\bot.log -Tail 20"
}
