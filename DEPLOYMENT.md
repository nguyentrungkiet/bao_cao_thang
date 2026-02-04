# 🚀 Hướng dẫn Deploy Bot lên VPS

Tài liệu này hướng dẫn chi tiết cách deploy Telegram Bot lên VPS Ubuntu/Debian.

## 📋 Yêu cầu

- VPS chạy Ubuntu 20.04+ hoặc Debian 11+
- Python 3.11 trở lên
- Git
- SSH access vào VPS
- File `credentials.json` (Google Service Account)
- File `.env` với thông tin cấu hình

## 🛠️ Cách 1: Tự động (Khuyến nghị)

### Bước 1: Kết nối SSH vào VPS

```bash
ssh user@your-vps-ip
```

### Bước 2: Chạy script setup tự động

```bash
# Download và chạy script
curl -o setup.sh https://raw.githubusercontent.com/nguyentrungkiet/bao_cao_thang/main/deploy/setup_vps.sh
chmod +x setup.sh
./setup.sh
```

### Bước 3: Copy credentials.json

Từ máy local:

```bash
scp credentials.json user@your-vps-ip:~/bao_cao_thang/
```

### Bước 4: Tạo file .env

```bash
cd ~/bao_cao_thang
nano .env
```

Copy nội dung từ `.env.example` và điền các giá trị:

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

Lưu file: `Ctrl+X` → `Y` → `Enter`

### Bước 5: Cài đặt systemd service

```bash
cd ~/bao_cao_thang
chmod +x deploy/install_service.sh
./deploy/install_service.sh
```

### Bước 6: Khởi động bot

```bash
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## 🔧 Cách 2: Thủ công

### 1. Cài đặt dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git
```

### 2. Clone repository

```bash
cd ~
git clone https://github.com/nguyentrungkiet/bao_cao_thang.git
cd bao_cao_thang
```

### 3. Tạo virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Cài đặt packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Tạo cấu trúc thư mục

```bash
mkdir -p logs reports
```

### 6. Copy credentials và tạo .env

```bash
# Copy credentials.json từ máy local
# scp credentials.json user@vps:~/bao_cao_thang/

# Tạo .env
cp .env.example .env
nano .env  # Điền thông tin
```

### 7. Test bot

```bash
source .venv/bin/activate
python -m app.main
```

Nhấn `Ctrl+C` để dừng nếu bot chạy OK.

### 8. Cài đặt service

```bash
chmod +x deploy/install_service.sh
./deploy/install_service.sh
```

### 9. Khởi động service

```bash
sudo systemctl start telegram-bot
sudo systemctl enable telegram-bot  # Tự động khởi động khi reboot
```

## 📊 Quản lý Bot

### Xem trạng thái

```bash
sudo systemctl status telegram-bot
```

### Xem logs realtime

```bash
sudo journalctl -u telegram-bot -f
```

Hoặc xem file log trực tiếp:

```bash
tail -f ~/bao_cao_thang/logs/bot.log
```

### Khởi động lại bot

```bash
sudo systemctl restart telegram-bot
```

### Dừng bot

```bash
sudo systemctl stop telegram-bot
```

### Tắt tự động khởi động

```bash
sudo systemctl disable telegram-bot
```

## 🔄 Cập nhật Code

### Khi có code mới trên GitHub

```bash
cd ~/bao_cao_thang
sudo systemctl stop telegram-bot  # Dừng bot
git pull origin main              # Lấy code mới
source .venv/bin/activate
pip install -r requirements.txt   # Cập nhật dependencies
sudo systemctl start telegram-bot # Khởi động lại
```

### Kiểm tra logs sau khi cập nhật

```bash
sudo journalctl -u telegram-bot -n 50 --no-pager
```

## 🔒 Bảo mật

### 1. Bảo vệ file nhạy cảm

```bash
chmod 600 ~/bao_cao_thang/.env
chmod 600 ~/bao_cao_thang/credentials.json
```

### 2. Tạo user riêng cho bot (khuyến nghị)

```bash
sudo adduser --system --group telegram-bot
sudo chown -R telegram-bot:telegram-bot ~/bao_cao_thang
```

Sau đó sửa file service:

```bash
sudo nano /etc/systemd/system/telegram-bot.service
# Đổi User=your-username thành User=telegram-bot
sudo systemctl daemon-reload
sudo systemctl restart telegram-bot
```

### 3. Firewall

```bash
# Chỉ mở SSH
sudo ufw allow ssh
sudo ufw enable
```

## 🐛 Troubleshooting

### Bot không khởi động

```bash
# Xem logs chi tiết
sudo journalctl -u telegram-bot -n 100 --no-pager

# Kiểm tra file .env
cat ~/bao_cao_thang/.env

# Test trực tiếp
cd ~/bao_cao_thang
source .venv/bin/activate
python -m app.main
```

### Lỗi Google Sheets connection

```bash
# Kiểm tra credentials.json
ls -l ~/bao_cao_thang/credentials.json

# Test kết nối
cd ~/bao_cao_thang
source .venv/bin/activate
python test_sheet.py
```

### Bot bị conflict

```bash
# Kiểm tra có process nào khác đang chạy không
ps aux | grep python | grep app.main

# Kill process cũ
sudo systemctl stop telegram-bot
pkill -f "python.*app.main"
sudo systemctl start telegram-bot
```

### Hết dung lượng disk

```bash
# Kiểm tra dung lượng
df -h

# Xóa logs cũ
cd ~/bao_cao_thang/logs
rm *.log
sudo journalctl --vacuum-time=7d  # Xóa logs systemd > 7 ngày
```

## 📈 Monitoring

### Setup cron job để kiểm tra bot

Tạo script kiểm tra:

```bash
nano ~/check_bot.sh
```

Nội dung:

```bash
#!/bin/bash
if ! systemctl is-active --quiet telegram-bot; then
    echo "Bot died at $(date)" >> ~/bot_status.log
    systemctl start telegram-bot
fi
```

Thêm vào crontab:

```bash
chmod +x ~/check_bot.sh
crontab -e
# Thêm dòng: */5 * * * * /home/your-username/check_bot.sh
```

### Log rotation

Tạo file logrotate:

```bash
sudo nano /etc/logrotate.d/telegram-bot
```

Nội dung:

```
/home/your-username/bao_cao_thang/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## 🎯 Kiểm tra hoạt động

Sau khi deploy, kiểm tra:

1. ✅ Bot online trong Telegram: Gửi `/ping`
2. ✅ Menu hiển thị: Gửi `/start`
3. ✅ Đọc Google Sheets: Bấm "📌 Hôm nay"
4. ✅ Xuất Word: Bấm "📄 Menu Word"
5. ✅ Scheduled jobs: Xem logs lúc 06:00 và thứ 6 17:00

## 📞 Support

Nếu gặp vấn đề:
1. Xem logs: `sudo journalctl -u telegram-bot -f`
2. Kiểm tra GitHub Issues
3. Liên hệ admin

---

**Lưu ý:** Nhớ backup file `.env` và `credentials.json` ở nơi an toàn!
