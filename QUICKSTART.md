# HƯỚNG DẪN NHANH - CHẠY BOT

## Bước 1: Cài đặt môi trường

```powershell
# Tạo virtual environment
python -m venv .venv

# Kích hoạt (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Cài đặt dependencies
pip install -r requirements.txt
```

## Bước 2: Cấu hình

1. ✅ File `.env` đã được tạo sẵn với thông tin của bạn
2. ✅ Đảm bảo file `credentials.json` tồn tại trong thư mục này
3. ⚠️ **QUAN TRỌNG**: Share Google Sheet cho service account email
   - Mở file `credentials.json`
   - Tìm `client_email` (dạng: xxx@xxx.iam.gserviceaccount.com)
   - Mở Google Sheet: https://docs.google.com/spreadsheets/d/1sGUDj4IF1-7iZF_0ecwLCXp9lNAUTDhIsPF_C5kWXiw/edit
   - Click **Share** → Thêm email service account → Quyền **Viewer**

## Bước 3: Kiểm tra cấu hình

```powershell
# Test import modules
python -c "from app.config import config; print('Config OK:', config.validate())"
```

## Bước 4: Chạy bot

```powershell
python -m app.main
```

## Bước 5: Test trong Telegram

1. Vào group chat ID: -3894771069
2. Gửi lệnh `/start`
3. Bot sẽ hiển thị menu
4. Test các chức năng

## Chạy Tests

```powershell
pytest -v
```

## Troubleshooting

### Lỗi credentials.json not found
- Kiểm tra file tồn tại tại: D:\SourceCode\Bao cao thang\credentials.json

### Lỗi Spreadsheet not found
- Kiểm tra đã share sheet cho service account
- Kiểm tra Sheet ID trong .env

### Bot không phản hồi
- Kiểm tra bot đã được thêm vào group
- Kiểm tra REPORT_CHAT_ID = -3894771069

## Logs

Xem logs realtime:
```powershell
Get-Content logs\bot.log -Wait -Tail 50
```

---
📖 Xem README.md để biết thêm chi tiết
