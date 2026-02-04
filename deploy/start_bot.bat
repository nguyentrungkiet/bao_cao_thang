@echo off
REM Batch file để khởi động bot thủ công (không dùng service)

echo ==========================================
echo Khoi dong Telegram Bot
echo ==========================================

cd /d C:\BaoCaoBot

REM Kiểm tra virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment chua duoc tao!
    echo Vui long chay setup_windows.ps1 truoc
    pause
    exit /b 1
)

REM Kiểm tra file cấu hình
if not exist "credentials.json" (
    echo Chua co file credentials.json!
    pause
    exit /b 1
)

if not exist ".env" (
    echo Chua co file .env!
    pause
    exit /b 1
)

REM Activate virtual environment và chạy bot
echo Dang khoi dong bot...
call .venv\Scripts\activate.bat
python -m app.main

REM Nếu bot dừng
echo.
echo Bot da dung!
pause
