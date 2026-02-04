"""
Test Google Sheets connection
"""
from app.sheets import GoogleSheetsClient
from app.rules import parse_all_tasks

try:
    print("Initializing Google Sheets client...")
    client = GoogleSheetsClient()
    
    print("Fetching data from sheet...")
    data = client.fetch_data(force_refresh=True)
    
    print(f"\n✅ Success! Fetched {len(data)} rows")
    print("\nFirst few rows:")
    for i, row in enumerate(data[:5], 1):
        print(f"{i}. {row}")
    
    print("\nParsing tasks...")
    tasks = parse_all_tasks(data)
    print(f"✅ Parsed {len(tasks)} tasks")
    
    for task in tasks[:3]:
        print(f"\n- {task.ho_ten}: {task.noi_dung[:50]}...")
        print(f"  Deadline: {task.deadline}, Status: {task.status.value}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
