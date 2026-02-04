#!/bin/bash
# Script cài đặt systemd service

set -e

# Lấy username hiện tại
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

echo "=========================================="
echo "Cài đặt Systemd Service"
echo "=========================================="
echo "User: $CURRENT_USER"
echo "Directory: $CURRENT_DIR"
echo ""

# Thay thế placeholder trong file service
echo "1. Tạo file service..."
sed "s|your-username|$CURRENT_USER|g; s|/home/your-username/bao_cao_thang|$CURRENT_DIR|g" \
    deploy/telegram-bot.service > /tmp/telegram-bot.service

# Copy file service vào systemd
echo "2. Copy file service vào systemd..."
sudo cp /tmp/telegram-bot.service /etc/systemd/system/telegram-bot.service

# Reload systemd
echo "3. Reload systemd daemon..."
sudo systemctl daemon-reload

# Enable service để tự động khởi động khi reboot
echo "4. Enable service..."
sudo systemctl enable telegram-bot

echo ""
echo "=========================================="
echo "CÀI ĐẶT SERVICE HOÀN TẤT!"
echo "=========================================="
echo ""
echo "Các lệnh quản lý service:"
echo "  sudo systemctl start telegram-bot     # Khởi động bot"
echo "  sudo systemctl stop telegram-bot      # Dừng bot"
echo "  sudo systemctl restart telegram-bot   # Khởi động lại bot"
echo "  sudo systemctl status telegram-bot    # Xem trạng thái bot"
echo "  sudo journalctl -u telegram-bot -f    # Xem logs realtime"
echo ""
