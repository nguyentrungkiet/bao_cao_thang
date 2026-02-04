@echo off
REM Batch file để dừng bot Windows Service

echo ==========================================
echo Dung Telegram Bot Service
echo ==========================================

cd /d C:\BaoCaoBot

if not exist "nssm\nssm.exe" (
    echo NSSM chua duoc cai dat!
    pause
    exit /b 1
)

echo Dang dung bot...
nssm\nssm.exe stop TelegramBot

timeout /t 2 >nul

nssm\nssm.exe status TelegramBot

echo.
echo Hoan tat!
pause
