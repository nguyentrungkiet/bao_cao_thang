#!/bin/bash
# Script cài đặt bot trên VPS Ubuntu/Debian

set -e

echo "=========================================="
echo "Cài đặt Telegram Bot lên VPS"
echo "=========================================="

# Cập nhật hệ thống
echo "1. Cập nhật hệ thống..."
sudo apt-get update
sudo apt-get upgrade -y

# Cài đặt Python 3.11+ và các dependencies
echo "2. Cài đặt Python và dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv git

# Kiểm tra phiên bản Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Phiên bản Python: $PYTHON_VERSION"

# Clone repository
echo "3. Clone repository từ GitHub..."
cd ~
if [ -d "bao_cao_thang" ]; then
    echo "Thư mục bao_cao_thang đã tồn tại. Xóa và clone lại..."
    rm -rf bao_cao_thang
fi
git clone https://github.com/nguyentrungkiet/bao_cao_thang.git
cd bao_cao_thang

# Tạo virtual environment
echo "4. Tạo virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt dependencies
echo "5. Cài đặt Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Tạo thư mục logs
echo "6. Tạo thư mục logs..."
mkdir -p logs

# Tạo thư mục reports
echo "7. Tạo thư mục reports..."
mkdir -p reports

echo ""
echo "=========================================="
echo "CÀI ĐẶT HOÀN TẤT!"
echo "=========================================="
echo ""
echo "BƯỚC TIẾP THEO:"
echo "1. Copy file credentials.json vào thư mục này:"
echo "   scp credentials.json user@vps-ip:~/bao_cao_thang/"
echo ""
echo "2. Tạo file .env:"
echo "   nano .env"
echo "   (Copy nội dung từ .env.example và điền thông tin)"
echo ""
echo "3. Cài đặt systemd service:"
echo "   ./deploy/install_service.sh"
echo ""
echo "4. Khởi động bot:"
echo "   sudo systemctl start telegram-bot"
echo ""
