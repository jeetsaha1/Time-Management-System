import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import json
from datetime import datetime
import os

TASK_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Management System")
        self.tasks = load_tasks()

        # Frame for form
        form_frame = tk.Frame(root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Title:").grid(row=0, column=0)
        self.title_entry = tk.Entry(form_frame)
        self.title_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Deadline (YYYY-MM-DD):").grid(row=0, column=2)
        self.deadline_entry = tk.Entry(form_frame)
        self.deadline_entry.grid(row=0, column=3)

        tk.Label(form_frame, text="Priority:").grid(row=0, column=4)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_menu = ttk.Combobox(form_frame, textvariable=self.priority_var, values=["High", "Medium", "Low"], state="readonly", width=7)
        self.priority_menu.grid(row=0, column=5)

        self.add_btn = tk.Button(form_frame, text="Add Task", command=self.add_task)
        self.add_btn.grid(row=0, column=6, padx=5)

        # Task list
        self.tree = ttk.Treeview(root, columns=("Deadline", "Priority", "Status"), show="headings", selectmode="browse")
        self.tree.heading("Deadline", text="Deadline")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.toggle_complete)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Mark as Completed", command=self.mark_completed).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_tasks).pack(side=tk.LEFT, padx=5)

        self.refresh_tasks()

    def add_task(self):
        title = self.title_entry.get().strip()
        deadline = self.deadline_entry.get().strip()
        priority = self.priority_var.get()
        if not title or not deadline:
            messagebox.showerror("Error", "Please enter both title and deadline.")
            return
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.")
            return
        task = {
            "title": title,
            "deadline": deadline,
            "priority": priority,
            "completed": False
        }
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.refresh_tasks()
        self.title_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)

    def refresh_tasks(self):
        self.tasks = load_tasks()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, task in enumerate(self.tasks):
            status = "✔ Completed" if task["completed"] else "❌ Pending"
            self.tree.insert("", "end", iid=idx, values=(task["deadline"], task["priority"], status), text=task["title"])

    def mark_completed(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task to mark as completed.")
            return
        idx = int(selected[0])
        self.tasks[idx]["completed"] = True
        save_tasks(self.tasks)
        self.refresh_tasks()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task to delete.")
            return
        idx = int(selected[0])
        title = self.tasks[idx]["title"]
        if messagebox.askyesno("Confirm", f"Delete task '{title}'?"):
            self.tasks.pop(idx)
            save_tasks(self.tasks)
            self.refresh_tasks()

    def toggle_complete(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        self.tasks[idx]["completed"] = not self.tasks[idx]["completed"]
        save_tasks(self.tasks)
        self.refresh_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()