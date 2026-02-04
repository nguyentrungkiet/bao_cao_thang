# Script tự động cài đặt Telegram Bot trên Windows VPS
# Chạy với quyền Administrator: PowerShell -ExecutionPolicy Bypass -File setup_windows.ps1

Write-Host "=========================================="
Write-Host "Cài đặt Telegram Bot trên Windows VPS"
Write-Host "==========================================" -ForegroundColor Green

# Kiểm tra quyền Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Cần chạy script này với quyền Administrator!" -ForegroundColor Red
    Write-Host "Chuột phải PowerShell -> Run as Administrator" -ForegroundColor Yellow
    exit 1
}

# 1. Kiểm tra Python
Write-Host "`n1. Kiểm tra Python..." -ForegroundColor Cyan
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonInstalled) {
    Write-Host "Python chưa được cài đặt!" -ForegroundColor Red
    Write-Host "Vui lòng tải và cài đặt Python 3.11+ từ: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Nhớ check 'Add Python to PATH' khi cài đặt!" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version
Write-Host "Đã tìm thấy: $pythonVersion" -ForegroundColor Green

# 2. Kiểm tra Git
Write-Host "`n2. Kiểm tra Git..." -ForegroundColor Cyan
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitInstalled) {
    Write-Host "Git chưa được cài đặt!" -ForegroundColor Red
    Write-Host "Vui lòng tải và cài đặt Git từ: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "Git đã được cài đặt" -ForegroundColor Green

# 3. Clone repository
Write-Host "`n3. Clone repository từ GitHub..." -ForegroundColor Cyan
$installPath = "C:\BaoCaoBot"

if (Test-Path $installPath) {
    Write-Host "Thư mục $installPath đã tồn tại" -ForegroundColor Yellow
    $response = Read-Host "Xóa và clone lại? (y/n)"
    if ($response -eq 'y') {
        Remove-Item -Path $installPath -Recurse -Force
    } else {
        Write-Host "Sử dụng thư mục hiện tại" -ForegroundColor Yellow
        Set-Location $installPath
    }
}

if (-not (Test-Path $installPath)) {
    git clone https://github.com/nguyentrungkiet/bao_cao_thang.git $installPath
    Set-Location $installPath
}

# 4. Tạo virtual environment
Write-Host "`n4. Tạo virtual environment..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    Write-Host "Virtual environment đã tồn tại, sử dụng lại" -ForegroundColor Yellow
} else {
    python -m venv .venv
}

# 5. Activate và cài đặt dependencies
Write-Host "`n5. Cài đặt Python packages..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt

# 6. Tạo thư mục
Write-Host "`n6. Tạo thư mục cần thiết..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "reports" | Out-Null

# 7. Tải NSSM (Non-Sucking Service Manager)
Write-Host "`n7. Tải NSSM để tạo Windows Service..." -ForegroundColor Cyan
$nssmPath = "$installPath\nssm"
if (-not (Test-Path "$nssmPath\nssm.exe")) {
    New-Item -ItemType Directory -Force -Path $nssmPath | Out-Null
    
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"
    
    Write-Host "Đang tải NSSM..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
    
    Write-Host "Giải nén NSSM..." -ForegroundColor Yellow
    Expand-Archive -Path $nssmZip -DestinationPath $env:TEMP -Force
    
    # Copy nssm.exe phù hợp với hệ thống
    if ([Environment]::Is64BitOperatingSystem) {
        Copy-Item "$env:TEMP\nssm-2.24\win64\nssm.exe" "$nssmPath\nssm.exe"
    } else {
        Copy-Item "$env:TEMP\nssm-2.24\win32\nssm.exe" "$nssmPath\nssm.exe"
    }
    
    Remove-Item $nssmZip -Force
    Remove-Item "$env:TEMP\nssm-2.24" -Recurse -Force
    
    Write-Host "NSSM đã được cài đặt" -ForegroundColor Green
} else {
    Write-Host "NSSM đã tồn tại" -ForegroundColor Green
}

Write-Host "`n=========================================="
Write-Host "CÀI ĐẶT HOÀN TẤT!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host "`nBƯỚC TIẾP THEO:" -ForegroundColor Yellow
Write-Host "1. Copy file credentials.json vào thư mục: $installPath"
Write-Host "2. Tạo file .env (copy từ .env.example và điền thông tin):"
Write-Host "   notepad .env"
Write-Host "3. Cài đặt Windows Service:"
Write-Host "   PowerShell -ExecutionPolicy Bypass -File deploy\install_service_windows.ps1"
Write-Host "4. Khởi động bot:"
Write-Host "   nssm\nssm.exe start TelegramBot"
Write-Host ""
