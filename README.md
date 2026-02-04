# 🤖 Telegram Bot Báo Cáo Tiến Độ Công Việc

Bot Telegram tự động báo cáo tiến độ công việc từ Google Sheets cho **Tổ thư ký Viện Công Nghệ Số**.

## 📋 Tính năng

### Báo cáo tự động
- **Hàng ngày lúc 06:00**: Báo cáo tiến độ công việc
  - Công việc trễ hạn
  - Công việc hôm nay
  - Công việc sắp tới hạn
  - Thống kê tổng quan

- **Thứ Sáu lúc 17:00**: Báo cáo tuần
  - Top 10 công việc trễ nhiều nhất
  - Thống kê theo từng người
  - Tổng quan tình hình tuần

### Menu tra cứu
- 📌 **Công việc hôm nay**: Xem việc cần làm hôm nay + trễ hạn
- ⏰ **Ai đang trễ deadline**: Thống kê theo người
- ⚠️ **Sắp tới hạn**: Công việc trong 1-3 ngày tới
- 📊 **Báo cáo tuần**: Tổng quan tình hình
- 🔎 **Tìm kiếm**: Tìm theo tên hoặc nội dung công việc
- 🔄 **Làm mới**: Cập nhật dữ liệu mới nhất

### Phân loại công việc
- 🚨 **Trễ hạn**: Quá deadline
- ⏰ **Hôm nay**: Phải hoàn thành hôm nay
- 📌 **Ngày mai**: Deadline vào ngày mai
- ⚠️ **Sắp tới**: Deadline trong 2-3 ngày
- ✅ **Đúng tiến độ**: Deadline còn >= 4 ngày
- ❓ **Chưa có deadline**: Cần bổ sung deadline

## 🛠️ Cài đặt

### Yêu cầu
- Python 3.11 trở lên
- Google Cloud Service Account
- Telegram Bot Token

### Bước 1: Clone/Download project

```bash
cd "D:\SourceCode\Bao cao thang"
```

### Bước 2: Tạo môi trường ảo và cài đặt dependencies

```powershell
# Tạo virtual environment
python -m venv .venv

# Kích hoạt virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 3: Cấu hình Google Sheets

#### 3.1. Tạo Service Account
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Bật **Google Sheets API** và **Google Drive API**
4. Tạo Service Account:
   - Vào **IAM & Admin** → **Service Accounts**
   - Click **Create Service Account**
   - Đặt tên và tạo
5. Tạo key:
   - Click vào service account vừa tạo
   - Tab **Keys** → **Add Key** → **Create new key**
   - Chọn **JSON** và tải về
6. Đổi tên file JSON thành `credentials.json` và đặt trong thư mục project

#### 3.2. Share Google Sheet
1. Mở file `credentials.json`
2. Tìm field `client_email` (dạng: `xxx@xxx.iam.gserviceaccount.com`)
3. Mở Google Sheet cần sử dụng
4. Click **Share** và thêm email service account với quyền **Viewer** hoặc **Editor**

### Bước 4: Tạo Telegram Bot

1. Tìm [@BotFather](https://t.me/botfather) trên Telegram
2. Gửi lệnh `/newbot`
3. Đặt tên và username cho bot
4. Lưu lại **Bot Token**

### Bước 5: Lấy Group Chat ID

1. Thêm bot vào group
2. Gửi một tin nhắn bất kỳ trong group
3. Truy cập: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Tìm field `"chat":{"id":-123456789,...}` (ID âm là group/supergroup)
5. Lưu lại Chat ID

### Bước 6: Cấu hình môi trường

Tạo file `.env` từ template:

```powershell
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8427564565:AAH9rywGt6cXor5n29i449u9B9maZl43ZY8

# Google Sheets Configuration
GOOGLE_SHEET_ID=1sGUDj4IF1-7iZF_0ecwLCXp9lNAUTDhIsPF_C5kWXiw
GOOGLE_SHEET_TAB=Báo cáo
GOOGLE_CREDENTIALS_PATH=D:\SourceCode\Bao cao thang\credentials.json

# Timezone
TZ=Asia/Ho_Chi_Minh

# Target group chat ID
REPORT_CHAT_ID=-3894771069

# Optional settings
CACHE_DURATION=300
MAX_DISPLAY_ITEMS=10
```

**Lưu ý**: 
- `GOOGLE_SHEET_ID` lấy từ URL Google Sheets: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`
- `REPORT_CHAT_ID` phải là số âm cho group/supergroup

### Bước 7: Cấu trúc Google Sheet

Sheet phải có tab tên **"Báo cáo"** với các cột:

| STT | Họ tên | Nội dung công việc đã thực hiện | Mức độ | Deadline | Kết quả / Tiến độ | Ghi chú |
|-----|--------|----------------------------------|--------|----------|-------------------|---------|
| 1   | Nguyễn Văn A | Hoàn thành báo cáo | Cao | 25/12/2024 | Đang thực hiện | |
| 2   | Trần Thị B | Họp với khách hàng | Trung bình | 26/12/2024 | Hoàn thành | |

**Định dạng deadline hỗ trợ**:
- `dd/mm/yyyy` (25/12/2024)
- `d/m/yyyy` (5/3/2024)
- `yyyy-mm-dd` (2024-12-25)
- Google Sheets serial number

**Đánh dấu hoàn thành**:
- Cột "Kết quả / Tiến độ" chứa từ "Hoàn thành" (không phân biệt hoa thường)

## 🚀 Chạy Bot

```powershell
# Kích hoạt virtual environment (nếu chưa)
.\.venv\Scripts\Activate.ps1

# Chạy bot
python -m app.main
```

Bot sẽ chạy và hiển thị:
```
===================================================
Starting Telegram Bot - Work Progress Reporter
===================================================
Bot is now running!
Target group chat ID: -3894771069
Press Ctrl+C to stop
===================================================
```

## 🧪 Chạy Tests

```powershell
# Chạy tất cả tests
pytest

# Chạy với chi tiết
pytest -v

# Chạy một file test cụ thể
pytest tests/test_rules.py -v
```

## 📁 Cấu trúc Project

```
Bao cao thang/
├── app/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── config.py         # Configuration & env loading
│   ├── models.py         # Data models (Task, TaskStatus)
│   ├── sheets.py         # Google Sheets client
│   ├── rules.py          # Business rules (parsing, classification)
│   ├── reporting.py      # Message formatting
│   ├── bot.py            # Telegram handlers
│   └── scheduler.py      # Scheduled jobs
├── tests/
│   ├── __init__.py
│   ├── test_rules.py
│   └── test_reporting.py
├── logs/                 # Log files (auto-created)
├── .env                  # Environment variables (NOT in git)
├── .env.example          # Template for .env
├── .gitignore
├── credentials.json      # Google service account (NOT in git)
├── requirements.txt
└── README.md
```

## 🔒 Bảo mật

- ✅ **KHÔNG BAO GIỜ** commit file `.env` hoặc `credentials.json`
- ✅ File `.gitignore` đã được cấu hình để bỏ qua các file nhạy cảm
- ✅ Tất cả secrets được đọc từ biến môi trường
- ✅ Logs không chứa thông tin nhạy cảm

## 📝 Lệnh Telegram Bot

### Commands
- `/start` - Hiển thị menu chính
- `/help` - Hướng dẫn sử dụng
- `/ping` - Kiểm tra bot hoạt động
- `/cancel` - Hủy tìm kiếm (khi đang trong chế độ tìm kiếm)

### Quyền sử dụng
- Bot chỉ hoạt động trong group có ID = `REPORT_CHAT_ID`
- Tất cả thành viên trong group đều có thể sử dụng menu và tra cứu
- Ở private chat: chỉ cho phép `/help`, `/ping` và hướng dẫn

## 🐛 Xử lý lỗi

### Lỗi: "credentials.json not found"
- Kiểm tra đường dẫn trong `.env` file
- Đảm bảo file `credentials.json` tồn tại

### Lỗi: "Spreadsheet not found"
- Kiểm tra `GOOGLE_SHEET_ID` trong `.env`
- Đảm bảo đã share sheet cho service account email

### Lỗi: "Worksheet 'Báo cáo' not found"
- Kiểm tra tên tab trong Google Sheet
- Đảm bảo `GOOGLE_SHEET_TAB` trong `.env` khớp với tên tab

### Lỗi: Bot không phản hồi trong group
- Kiểm tra `REPORT_CHAT_ID` có đúng không
- Đảm bảo bot đã được thêm vào group
- Kiểm tra bot có quyền đọc và gửi tin nhắn

## 📊 Monitoring & Logs

Logs được lưu tại: `logs/bot.log`

```powershell
# Xem logs realtime
Get-Content logs\bot.log -Wait -Tail 50
```

## 🔄 Cập nhật

```powershell
# Kéo code mới nhất
git pull

# Cập nhật dependencies
pip install -r requirements.txt --upgrade

# Khởi động lại bot
python -m app.main
```

## 💡 Tips

1. **Cache**: Dữ liệu được cache 5 phút để giảm API calls. Dùng nút "Làm mới" để cập nhật ngay.

2. **Giới hạn hiển thị**: Mỗi section chỉ hiển thị tối đa 10 items (có thể thay đổi trong `.env`)

3. **Timezone**: Tất cả thời gian theo `Asia/Ho_Chi_Minh`

4. **Performance**: Bot xử lý sheet lớn (>1000 rows) mà không vấn đề

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs: `logs/bot.log`
2. Kiểm tra cấu hình `.env`
3. Đảm bảo credentials.json hợp lệ
4. Liên hệ admin

## 📄 License

Internal use only - Tổ thư ký Viện Công Nghệ Số

---

**Phiên bản**: 1.0.0  
**Ngày tạo**: 2026-02-04  
**Python**: 3.11+
