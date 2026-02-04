# Script cài đặt Telegram Bot như Windows Service
# Chạy với quyền Administrator

Write-Host "=========================================="
Write-Host "Cài đặt Telegram Bot Windows Service"
Write-Host "==========================================" -ForegroundColor Green

# Kiểm tra quyền Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Cần chạy script này với quyền Administrator!" -ForegroundColor Red
    exit 1
}

$installPath = "C:\BaoCaoBot"
$serviceName = "TelegramBot"

# Kiểm tra thư mục
if (-not (Test-Path $installPath)) {
    Write-Host "Thư mục $installPath không tồn tại!" -ForegroundColor Red
    Write-Host "Vui lòng chạy setup_windows.ps1 trước" -ForegroundColor Yellow
    exit 1
}

Set-Location $installPath

# Kiểm tra credentials.json và .env
if (-not (Test-Path "credentials.json")) {
    Write-Host "Chưa có file credentials.json!" -ForegroundColor Red
    Write-Host "Vui lòng copy file này vào thư mục $installPath" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Host "Chưa có file .env!" -ForegroundColor Red
    Write-Host "Vui lòng tạo file .env từ .env.example" -ForegroundColor Yellow
    exit 1
}

# Kiểm tra NSSM
$nssmPath = "$installPath\nssm\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "NSSM chưa được cài đặt!" -ForegroundColor Red
    Write-Host "Vui lòng chạy setup_windows.ps1 trước" -ForegroundColor Yellow
    exit 1
}

# Xóa service cũ nếu có
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Service $serviceName đã tồn tại, đang xóa..." -ForegroundColor Yellow
    & $nssmPath stop $serviceName
    Start-Sleep -Seconds 2
    & $nssmPath remove $serviceName confirm
}

# Cài đặt service mới
Write-Host "`nĐang cài đặt Windows Service..." -ForegroundColor Cyan

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

# Cấu hình restart
& $nssmPath set $serviceName AppExit Default Restart
& $nssmPath set $serviceName AppRestartDelay 5000

Write-Host "`n=========================================="
Write-Host "CÀI ĐẶT SERVICE HOÀN TẤT!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host "`nCác lệnh quản lý service:" -ForegroundColor Yellow
Write-Host "  nssm\nssm.exe start $serviceName      # Khởi động bot"
Write-Host "  nssm\nssm.exe stop $serviceName       # Dừng bot"
Write-Host "  nssm\nssm.exe restart $serviceName    # Khởi động lại bot"
Write-Host "  nssm\nssm.exe status $serviceName     # Xem trạng thái"
Write-Host ""
Write-Host "Hoặc dùng Windows Services:" -ForegroundColor Yellow
Write-Host "  services.msc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Xem logs:" -ForegroundColor Yellow
Write-Host "  Get-Content logs\bot.log -Tail 50 -Wait"
Write-Host ""

# Hỏi có muốn khởi động ngay không
$response = Read-Host "Khởi động bot ngay bây giờ? (y/n)"
if ($response -eq 'y') {
    Write-Host "`nĐang khởi động bot..." -ForegroundColor Cyan
    & $nssmPath start $serviceName
    Start-Sleep -Seconds 3
    
    $status = & $nssmPath status $serviceName
    Write-Host "Trạng thái: $status" -ForegroundColor Green
    
    Write-Host "`nXem logs để kiểm tra:" -ForegroundColor Yellow
    Write-Host "  Get-Content logs\bot.log -Tail 20"
}
