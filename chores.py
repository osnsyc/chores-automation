import requests
import argparse
import json
from datetime import datetime

BASEROW_API_TOKEN = ''
HISTORY_TABLE = ''
BASE_URL = ''
MAIN_TABLE = ''
TODO_VIEW = ''

def get_baserow_rows(table_id=None, params=None, next_page=None):
    if next_page:
        url = next_page
    else:
        url = f"{BASE_URL}/api/database/rows/table/{table_id}/{params or ''}"
    headers = {
        "Authorization": f"Token {BASEROW_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("next", []), response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"获取 Baserow 行数据失败: {e}")
        return [], []

def update_baserow_row(row_id, table_id: int, data: dict):
    url = f"{BASE_URL}/api/database/rows/table/{table_id}/{row_id}/?user_field_names=true"

    headers = {
        "Authorization": f"Token {BASEROW_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"更新 Baserow 行数据失败: {e}")
        return None
    
def create_baserow_row(table_id: int, data: dict):
    url = f"{BASE_URL}/api/database/rows/table/{table_id}/?user_field_names=true"

    headers = {
        "Authorization": f"Token {BASEROW_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"创建 Baserow 行数据失败: {e}")
        return None
    
if __name__ == "__main__":
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        BASE_URL = config.get("BASE_URL", BASE_URL)
        BASEROW_API_TOKEN = config.get("BASEROW_API_TOKEN")
        HISTORY_TABLE = config.get("HISTORY_TABLE")  
        MAIN_TABLE = config.get("MAIN_TABLE")  
        TODO_VIEW = config.get("TODO_VIEW")
        
    parser = argparse.ArgumentParser(description="Execute different modules")
    parser.add_argument("id", help="Select function to run")
    args = parser.parse_args()

    if not args.id.isdigit():
        print("ID 必须是数字")
        exit(1)

    new_item = int(args.id)
    if new_item == 0:
        _, rows = get_baserow_rows(table_id=MAIN_TABLE,params=f"?view_id={TODO_VIEW}&user_field_names=true")
        rows = {row["Name"]: row["下次执行"] for row in rows}
        print(f"{rows}")
        exit(0)

    _, rows = get_baserow_rows(table_id=HISTORY_TABLE,params="?order_by=-执行日&user_field_names=true")
    if rows:
        today_row = rows[0]
        print(f"找到历史记录: {today_row}")

        if rows[0]["执行日"] != datetime.now().strftime("%Y-%m-%d"):
            new_row = {
                "执行日": datetime.now().strftime("%Y-%m-%d"),
            }
            today_row = create_baserow_row(HISTORY_TABLE, new_row)

        new_table_content = []
        table_content = today_row.get("Table", [])
        if table_content:
            for item in table_content:
                new_table_content.append(item["id"])

        new_table_content.append(new_item)
        print(f"{new_table_content}")

        update_baserow_row(today_row["id"], HISTORY_TABLE, {"Table": new_table_content})
        exit(0)
    else:
        print("没有找到历史记录。")
        exit(1)