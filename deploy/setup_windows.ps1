# Telegram Bot - Windows VPS Setup Script
# Run as Administrator: PowerShell -ExecutionPolicy Bypass -File setup_windows.ps1

Write-Host "=========================================="
Write-Host "Telegram Bot - Windows VPS Setup"
Write-Host "=========================================="

# Check Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Administrator privileges required!" -ForegroundColor Red
    Write-Host "Right-click PowerShell -> Run as Administrator" -ForegroundColor Yellow
    exit 1
}

# Step 1: Check Python
Write-Host ""
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Cyan
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonInstalled) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please download Python 3.11+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Step 2: Check Git
Write-Host ""
Write-Host "Step 2: Checking Git installation..." -ForegroundColor Cyan
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitInstalled) {
    Write-Host "ERROR: Git not found!" -ForegroundColor Red
    Write-Host "Please download Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "Git is installed" -ForegroundColor Green

# Step 3: Clone repository
Write-Host ""
Write-Host "Step 3: Cloning repository from GitHub..." -ForegroundColor Cyan
$installPath = "C:\BaoCaoBot"

if (Test-Path $installPath) {
    Write-Host "Directory $installPath already exists" -ForegroundColor Yellow
    $response = Read-Host "Delete and clone again? (y/n)"
    if ($response -eq 'y') {
        Remove-Item -Path $installPath -Recurse -Force
    } else {
        Write-Host "Using existing directory" -ForegroundColor Yellow
        Set-Location $installPath
    }
}

if (-not (Test-Path $installPath)) {
    git clone https://github.com/nguyentrungkiet/bao_cao_thang.git $installPath
    Set-Location $installPath
}

# Step 4: Create virtual environment
Write-Host ""
Write-Host "Step 4: Creating virtual environment..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists, reusing it" -ForegroundColor Yellow
} else {
    python -m venv .venv
}

# Step 5: Install Python packages
Write-Host ""
Write-Host "Step 5: Installing Python packages..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Create directories
Write-Host ""
Write-Host "Step 6: Creating required directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "reports" | Out-Null

# Step 7: Download NSSM (Windows Service Manager)
Write-Host ""
Write-Host "Step 7: Downloading NSSM for Windows Service..." -ForegroundColor Cyan
$nssmPath = "$installPath\nssm"
if (-not (Test-Path "$nssmPath\nssm.exe")) {
    New-Item -ItemType Directory -Force -Path $nssmPath | Out-Null
    
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"
    
    Write-Host "Downloading NSSM..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
    
    Write-Host "Extracting NSSM..." -ForegroundColor Yellow
    Expand-Archive -Path $nssmZip -DestinationPath $env:TEMP -Force
    
    # Copy appropriate nssm.exe
    if ([Environment]::Is64BitOperatingSystem) {
        Copy-Item "$env:TEMP\nssm-2.24\win64\nssm.exe" "$nssmPath\nssm.exe"
    } else {
        Copy-Item "$env:TEMP\nssm-2.24\win32\nssm.exe" "$nssmPath\nssm.exe"
    }
    
    Remove-Item $nssmZip -Force
    Remove-Item "$env:TEMP\nssm-2.24" -Recurse -Force
    
    Write-Host "NSSM installed successfully" -ForegroundColor Green
} else {
    Write-Host "NSSM already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "=========================================="
Write-Host "SETUP COMPLETED!"
Write-Host "=========================================="

Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Copy credentials.json file to: $installPath"
Write-Host "2. Create .env file (copy from .env.example and fill in values):"
Write-Host "   notepad .env"
Write-Host "3. Install Windows Service:"
Write-Host "   PowerShell -ExecutionPolicy Bypass -File deploy\install_service_windows.ps1"
Write-Host "4. Start the bot:"
Write-Host "   nssm\nssm.exe start TelegramBot"
Write-Host ""
