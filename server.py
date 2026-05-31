from datetime import datetime

from flask import Flask, jsonify, render_template, request

from storage import ensure_reports_dir, load_tasks, save_tasks, new_task_id

app = Flask(__name__, static_folder="static", template_folder="templates")
ensure_reports_dir()


def validate_task_payload(data):
    if not isinstance(data, dict):
        return None, "Invalid task data."

    title = str(data.get("title", "")).strip()
    deadline = str(data.get("deadline", "")).strip()
    priority = str(data.get("priority", "Medium")).title().strip()

    if not title:
        return None, "Title is required."
    if not deadline:
        return None, "Deadline is required."
    try:
        datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        return None, "Deadline must be in YYYY-MM-DD format."
    if priority not in {"High", "Medium", "Low"}:
        priority = "Medium"

    return {
        "title": title,
        "deadline": deadline,
        "priority": priority,
        "completed": False,
        "progress": 0,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }, None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify(load_tasks())


@app.route("/tasks", methods=["POST"])
def create_task():
    payload = request.get_json(silent=True) or {}
    task_data, error = validate_task_payload(payload)
    if error:
        return jsonify({"error": error}), 400

    tasks = load_tasks()
    task_data["id"] = new_task_id(tasks)
    tasks.append(task_data)
    save_tasks(tasks)
    return jsonify(task_data), 201


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get("id") == task_id:
            task["completed"] = True
            task["progress"] = 100
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({"error": "Task not found."}), 404


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = load_tasks()
    filtered = [task for task in tasks if task.get("id") != task_id]
    if len(filtered) == len(tasks):
        return jsonify({"error": "Task not found."}), 404
    save_tasks(filtered)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
