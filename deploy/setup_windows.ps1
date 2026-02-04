# Script tu dong cai dat Telegram Bot tren Windows VPS
# Chay voi quyen Administrator: PowerShell -ExecutionPolicy Bypass -File setup_windows.ps1

Write-Host "=========================================="
Write-Host "Cai dat Telegram Bot tren Windows VPS"
Write-Host "==========================================" -ForegroundColor Green

# Kiem tra quyen Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Can chay script nay voi quyen Administrator!" -ForegroundColor Red
    Write-Host "Chuot phai PowerShell -> Run as Administrator" -ForegroundColor Yellow
    exit 1
}

# 1. Kiem tra Python
Write-Host ""
Write-Host "1. Kiem tra Python..." -ForegroundColor Cyan
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonInstalledua duoc cai dat!" -ForegroundColor Red
    Write-Host "Vui long tai va cai dat Python 3.11+ tu: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Nho check 'Add Python to PATH' khi cai dat!" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version
Write-Host "Da tim thay: $pythonVersion" -ForegroundColor Green

# 2. Kiem tra Git
Write-Host ""
Write-Host "2. Kie
Write-Host "`n2. Kiểm tra Git..." -ForegroundColor Cyan
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitInstalledua duoc cai dat!" -ForegroundColor Red
    Write-Host "Vui long tai va cai dat Git tu: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "Git da duoc cai dat" -ForegroundColor Green

# 3. Clone repository
Write-Host ""
Write-Host "3. Clone repository tu
Write-Host "`n3. Clone repository từ GitHub..." -ForegroundColor Cyan
$installPath = "C:\BaoCaoBot"

if (Test-Path $insu muc $installPath da ton tai" -ForegroundColor Yellow
    $response = Read-Host "Xoa va clone lai? (y/n)"
    if ($response -eq 'y') {
        Remove-Item -Path $installPath -Recurse -Force
    } else {
        Write-Host "Su dung thu muc hien tai" -ForegroundColor Yellow
        Set-Location $installPath
    }
}

if (-not (Test-Path $installPath)) {
    git clone https://github.com/nguyentrungkiet/bao_cao_thang.git $installPath
    Set-Location $installPath
}

# 4. Tao virtual environment
Write-Host ""
Write-Host "4. Tavironment
Write-Host "`n4. Tạo virtual environment..." -ForegroundColor Cyan
if (Test-Path ".venv") {da ton tai, su dung lai" -ForegroundColor Yellow
} else {
    python -m venv .venv
}

# 5. Activate va cai dat dependencies
Write-Host ""
Write-Host "5. Cai dat Python packages..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt

# 6. Tao thu muc
Write-Host ""
Write-Host "6. Tao thu muc can thie
Write-Host "`n6. Tạo thư mục cần thiết..." -ForegroundColor Cyan
New-Itai NSSM (Non-Sucking Service Manager)
Write-Host ""
Write-Host "7. Tai NSSM de taorce -Path "reports" | Out-Null

# 7. Tải NSSM (Non-Sucking Service Manager)
Write-Host "`n7. Tải NSSM để tạo Windows Service..." -ForegroundColor Cyan
$nssmPath = "$installPath\nssm"
if (-not (Test-Path "$nssmPath\nssm.exe")) {
    New-Item -ItemType Directory -Force -Path $nssmPath | Out-Null
    
    $nssmUrl = "Dang tai NSSM..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
    
    Write-Host "Giai nen NSSM..." -ForegroundColor Yellow
    Expand-Archive -Path $nssmZip -DestinationPath $env:TEMP -Force
    
    # Copy nssm.exe phu hop voi he thong
    if ([Environment]::Is64BitOperatingSystem) {
        Copy-Item "$env:TEMP\nssm-2.24\win64\nssm.exe" "$nssmPath\nssm.exe"
    } else {
        Copy-Item "$env:TEMP\nssm-2.24\win32\nssm.exe" "$nssmPath\nssm.exe"
    }
    
    Remove-Item $nssmZip -Force
    Remove-Item "$env:TEMP\nssm-2.24" -Recurse -Force
    
    Write-Host "NSSM da duoc cai dat" -ForegroundColor Green
} else {
    Write-Host "NSSM da ton tai" -ForegroundColor Green
}

Write-Host ""
Write-Host "=========================================="
Write-Host "CAI DAT HOAN TAT!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host ""ao thu muc: $installPath"
Write-Host "2. Tao file .env (copy tu .env.example va dien thong tin):"
Write-Host "   notepad .env"
Write-Host "3. Cai dat Windows Service:"
Write-Host "   PowerShell -ExecutionPolicy Bypass -File deploy\install_service_windows.ps1"
Write-Host "4. Khoi dole credentials.json vào thư mục: $installPath"
Write-Host "2. Tạo file .env (copy từ .env.example và điền thông tin):"
Write-Host "   notepad .env"
Write-Host "3. Cài đặt Windows Service:"
Write-Host "   PowerShell -ExecutionPolicy Bypass -File deploy\install_service_windows.ps1"
Write-Host "4. Khởi động bot:"
Write-Host "   nssm\nssm.exe start TelegramBot"
Write-Host ""
