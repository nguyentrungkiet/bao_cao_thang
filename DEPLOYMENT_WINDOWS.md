# 🚀 Hướng dẫn Deploy Bot lên Windows VPS

Tài liệu này hướng dẫn chi tiết cách deploy Telegram Bot lên Windows Server/VPS.

## 📋 Yêu cầu

- Windows Server 2016/2019/2022 hoặc Windows 10/11
- Python 3.11 trở lên
- Git for Windows
- Quyền Administrator
- File `credentials.json` (Google Service Account)
- File `.env` với thông tin cấu hình

## 🛠️ Cách 1: Tự động (Khuyến nghị)

### Bước 1: Cài đặt Python

1. Tải Python từ: https://www.python.org/downloads/
2. Chạy installer
3. **QUAN TRỌNG:** ✅ Check "Add Python to PATH"
4. Click "Install Now"

Kiểm tra:
```powershell
python --version
```

### Bước 2: Cài đặt Git

1. Tải Git từ: https://git-scm.com/download/win
2. Chạy installer với cài đặt mặc định

Kiểm tra:
```powershell
git --version
```

### Bước 3: Chạy script setup tự động

Mở **PowerShell với quyền Administrator** (chuột phải PowerShell → Run as Administrator):

```powershell
# Clone repository
git clone https://github.com/nguyentrungkiet/bao_cao_thang.git C:\BaoCaoBot
cd C:\BaoCaoBot

# Chạy script setup
PowerShell -ExecutionPolicy Bypass -File deploy\setup_windows.ps1
```

Script sẽ tự động:
- ✅ Kiểm tra Python và Git
- ✅ Tạo virtual environment
- ✅ Cài đặt tất cả packages
- ✅ Tạo thư mục logs và reports
- ✅ Tải NSSM (Windows Service Manager)

### Bước 4: Copy credentials.json

Copy file `credentials.json` vào thư mục `C:\BaoCaoBot`:

**Cách 1:** Dùng Remote Desktop - Copy/Paste trực tiếp

**Cách 2:** Dùng PowerShell từ máy local:
```powershell
# Từ máy local có file credentials.json
$username = "Administrator"
$vpsIp = "your-vps-ip"
$password = Read-Host "Nhập password VPS" -AsSecureString
$cred = New-Object System.Management.Automation.PSCredential($username, $password)

Copy-Item "credentials.json" -Destination "\\$vpsIp\C$\BaoCaoBot\" -Credential $cred
```

**Cách 3:** Upload qua FTP/SFTP (FileZilla, WinSCP)

### Bước 5: Tạo file .env

Mở PowerShell trong `C:\BaoCaoBot`:

```powershell
cd C:\BaoCaoBot
notepad .env
```

Copy nội dung từ `.env.example` và điền thông tin:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8427564565:AAH9rywGt6cXor5n29i449u9B9maZl43ZY8
REPORT_CHAT_ID=-1003894771069

# Google Sheets Configuration
GOOGLE_SHEET_ID=1YwkJKHQRCFvmuZ5XowTPLMA4zeoth7SzYnmRAe1-we4
GOOGLE_SHEET_TAB=Báo cáo
GOOGLE_CREDENTIALS_PATH=credentials.json

# Timezone
TZ=Asia/Ho_Chi_Minh

# Cache settings (seconds)
CACHE_DURATION=300

# Display settings
MAX_DISPLAY_ITEMS=10
```

Lưu file: `Ctrl+S` → Đóng Notepad

### Bước 6: Test bot thủ công (tuỳ chọn)

```powershell
cd C:\BaoCaoBot
.\.venv\Scripts\Activate.ps1
python -m app.main
```

Nếu bot chạy OK, nhấn `Ctrl+C` để dừng.

### Bước 7: Cài đặt Windows Service

Mở **PowerShell với quyền Administrator**:

```powershell
cd C:\BaoCaoBot
PowerShell -ExecutionPolicy Bypass -File deploy\install_service_windows.ps1
```

Chọn `y` khi được hỏi có muốn khởi động bot ngay.

### Bước 8: Kiểm tra bot hoạt động

```powershell
# Xem trạng thái service
C:\BaoCaoBot\nssm\nssm.exe status TelegramBot

# Xem logs
Get-Content C:\BaoCaoBot\logs\bot.log -Tail 20
```

Hoặc mở Services Manager:
```powershell
services.msc
```
Tìm service "Telegram Work Progress Bot"

## 🔧 Cách 2: Chạy thủ công (không dùng service)

Nếu không muốn dùng Windows Service, dùng file batch:

### Khởi động bot:
```cmd
C:\BaoCaoBot\deploy\start_bot.bat
```

### Dừng bot:
Nhấn `Ctrl+C` trong cửa sổ đang chạy bot

## 📊 Quản lý Bot

### Quản lý qua NSSM

```powershell
cd C:\BaoCaoBot

# Khởi động
nssm\nssm.exe start TelegramBot

# Dừng
nssm\nssm.exe stop TelegramBot

# Khởi động lại
nssm\nssm.exe restart TelegramBot

# Xem trạng thái
nssm\nssm.exe status TelegramBot
```

### Quản lý qua Windows Services

1. Mở Services: `Win+R` → `services.msc`
2. Tìm "Telegram Work Progress Bot"
3. Chuột phải → Start/Stop/Restart

### Quản lý qua PowerShell

```powershell
# Khởi động
Start-Service TelegramBot

# Dừng
Stop-Service TelegramBot

# Khởi động lại
Restart-Service TelegramBot

# Xem trạng thái
Get-Service TelegramBot
```

### Xem logs

```powershell
# Xem logs realtime
Get-Content C:\BaoCaoBot\logs\bot.log -Tail 50 -Wait

# Xem 100 dòng cuối
Get-Content C:\BaoCaoBot\logs\bot.log -Tail 100

# Xem service logs
Get-Content C:\BaoCaoBot\logs\service.log -Tail 50
```

## 🔄 Cập nhật Code

Khi có code mới trên GitHub:

```powershell
cd C:\BaoCaoBot

# Dừng bot
nssm\nssm.exe stop TelegramBot

# Lấy code mới
git pull origin main

# Cập nhật packages
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Khởi động lại
nssm\nssm.exe start TelegramBot

# Xem logs
Get-Content logs\bot.log -Tail 20 -Wait
```

## 🔒 Bảo mật

### 1. Bảo vệ file nhạy cảm

```powershell
# Chỉ cho phép Administrator đọc
$acl = Get-Acl "C:\BaoCaoBot\.env"
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Administrators","FullControl","Allow")
$acl.AddAccessRule($rule)
Set-Acl "C:\BaoCaoBot\.env" $acl

# Tương tự cho credentials.json
$acl = Get-Acl "C:\BaoCaoBot\credentials.json"
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Administrators","FullControl","Allow")
$acl.AddAccessRule($rule)
Set-Acl "C:\BaoCaoBot\credentials.json" $acl
```

### 2. Windows Firewall

```powershell
# Chặn tất cả inbound connections (chỉ cho RDP)
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

### 3. Tự động cập nhật Windows

Bật Windows Update tự động trong Settings

## 🔥 Firewall - Cho phép RDP từ IP cụ thể

```powershell
# Xóa rule RDP mặc định
Remove-NetFirewallRule -DisplayName "Remote Desktop*"

# Tạo rule mới chỉ cho IP cụ thể
New-NetFirewallRule -DisplayName "RDP from My IP" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 3389 `
    -RemoteAddress "YOUR_IP_ADDRESS" `
    -Action Allow
```

## 🐛 Troubleshooting

### Bot không khởi động

```powershell
# Xem logs chi tiết
Get-Content C:\BaoCaoBot\logs\service-error.log

# Xem logs bot
Get-Content C:\BaoCaoBot\logs\bot.log -Tail 50

# Test trực tiếp
cd C:\BaoCaoBot
.\.venv\Scripts\Activate.ps1
python -m app.main
```

### Lỗi ExecutionPolicy

```powershell
# Chạy PowerShell với bypass
PowerShell -ExecutionPolicy Bypass -File deploy\setup_windows.ps1

# Hoặc set vĩnh viễn (không khuyến nghị)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Service không tự động start sau reboot

```powershell
# Set lại startup type
C:\BaoCaoBot\nssm\nssm.exe set TelegramBot Start SERVICE_AUTO_START

# Hoặc qua services.msc:
# Chuột phải service → Properties → Startup type → Automatic
```

### Lỗi Google Sheets connection

```powershell
# Kiểm tra credentials.json
Test-Path C:\BaoCaoBot\credentials.json

# Test kết nối
cd C:\BaoCaoBot
.\.venv\Scripts\Activate.ps1
python test_sheet.py
```

### Bot bị conflict (multiple instances)

```powershell
# Tìm tất cả process Python đang chạy
Get-Process python

# Kill tất cả
Get-Process python | Stop-Process -Force

# Khởi động lại service
nssm\nssm.exe restart TelegramBot
```

### Hết dung lượng disk

```powershell
# Kiểm tra dung lượng
Get-PSDrive C

# Xóa logs cũ
Remove-Item C:\BaoCaoBot\logs\*.log

# Dọn dẹp Windows
cleanmgr /d C:
```

## 📈 Monitoring

### Task Scheduler - Tự động kiểm tra bot

1. Tạo script kiểm tra `C:\BaoCaoBot\check_bot.ps1`:

```powershell
$status = & C:\BaoCaoBot\nssm\nssm.exe status TelegramBot

if ($status -ne "SERVICE_RUNNING") {
    $message = "Bot died at $(Get-Date)"
    Add-Content -Path "C:\BaoCaoBot\bot_status.log" -Value $message
    
    # Khởi động lại
    & C:\BaoCaoBot\nssm\nssm.exe start TelegramBot
}
```

2. Tạo Task Scheduler:
   - Mở Task Scheduler: `taskschd.msc`
   - Create Task → Triggers → New → Repeat every 5 minutes
   - Actions → New → Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File C:\BaoCaoBot\check_bot.ps1`
   - Settings → ✅ Run task as soon as possible after scheduled start is missed

### Windows Performance Monitor

Monitor CPU, RAM usage:
```powershell
perfmon
```

### Event Viewer

Xem system logs:
```powershell
eventvwr
```

## 🎯 Kiểm tra hoạt động

Sau khi deploy, kiểm tra:

1. ✅ Bot online trong Telegram: Gửi `/ping`
2. ✅ Menu hiển thị: Gửi `/start`
3. ✅ Đọc Google Sheets: Bấm "📌 Hôm nay"
4. ✅ Xuất Word: Bấm "📄 Menu Word"
5. ✅ Service tự động start: Restart VPS và kiểm tra

## 📁 Cấu trúc thư mục trên VPS

```
C:\BaoCaoBot\
├── .venv\                  # Virtual environment
├── app\                    # Source code
├── deploy\                 # Scripts deployment
├── logs\                   # Log files
│   ├── bot.log            # Bot logs
│   ├── service.log        # NSSM stdout
│   └── service-error.log  # NSSM stderr
├── reports\               # Generated Word files
├── nssm\                  # NSSM service manager
│   └── nssm.exe
├── credentials.json       # Google credentials (bảo mật!)
├── .env                   # Config (bảo mật!)
└── requirements.txt       # Python dependencies
```

## 🔐 Backup

### Backup files quan trọng

```powershell
# Tạo thư mục backup
New-Item -ItemType Directory -Force -Path "D:\Backups\BaoCaoBot"

# Backup .env và credentials.json
Copy-Item C:\BaoCaoBot\.env D:\Backups\BaoCaoBot\
Copy-Item C:\BaoCaoBot\credentials.json D:\Backups\BaoCaoBot\

# Nén backup theo ngày
$date = Get-Date -Format "yyyyMMdd"
Compress-Archive -Path "D:\Backups\BaoCaoBot\*" -DestinationPath "D:\Backups\backup_$date.zip"
```

### Auto backup với Task Scheduler

Tạo task chạy script backup mỗi ngày lúc 2 giờ sáng.

## 📞 Support

Nếu gặp vấn đề:
1. Xem logs: `Get-Content C:\BaoCaoBot\logs\bot.log -Tail 50`
2. Kiểm tra GitHub Issues
3. Liên hệ admin

---

**Lưu ý:** 
- Nhớ backup file `.env` và `credentials.json` ở nơi an toàn!
- Không share credentials lên GitHub!
- Đổi mật khẩu RDP định kỳ
- Bật Windows Update
