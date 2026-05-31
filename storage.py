import json
import os
import hashlib

TASK_FILE = "tasks.json"
USER_FILE = "users.json"
REPORTS_DIR = "reports"


def ensure_reports_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)


def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_tasks(tasks):
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)


def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def new_task_id(tasks):
    return max((t.get("id", 0) for t in tasks), default=0) + 1
