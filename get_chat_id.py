"""
Script đơn giản để lấy chat_id từ Telegram.
Gửi /start trong group rồi chạy script này.
"""
import requests
import json

BOT_TOKEN = "8427564565:AAH9rywGt6cXor5n29i449u9B9maZl43ZY8"

# Get updates
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

print(json.dumps(data, indent=2, ensure_ascii=False))

if data['ok'] and data['result']:
    print("\n" + "="*60)
    print("CHAT IDs tìm thấy:")
    print("="*60)
    for update in data['result']:
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            chat_type = update['message']['chat']['type']
            chat_title = update['message']['chat'].get('title', 'N/A')
            text = update['message'].get('text', '')
            
            print(f"\nChat ID: {chat_id}")
            print(f"Type: {chat_type}")
            print(f"Title: {chat_title}")
            print(f"Message: {text}")
            print("-"*60)
else:
    print("\nKhông có updates nào. Vui lòng:")
    print("1. Gửi /start trong Telegram group")
    print("2. Chạy lại script này ngay sau đó")
