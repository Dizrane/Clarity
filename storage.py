import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "tasks.json")
BALANCE_FILE = os.path.join(os.path.dirname(__file__), "data", "balance.json")


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def load_balance():
    if not os.path.exists(BALANCE_FILE):
        return 0, 0
    with open(BALANCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("balance", 0), data.get("items_owned", 0)


def save_balance(balance, items_owned):
    with open(BALANCE_FILE, "w", encoding="utf-8") as f:
        json.dump({"balance": balance, "items_owned": items_owned}, f)
