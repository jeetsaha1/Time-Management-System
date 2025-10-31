import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
from datetime import datetime, timedelta
import os
import hashlib
import csv

TASK_FILE = "tasks.json"
USER_FILE = "users.json"
REPORTS_DIR = "reports"

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

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Management System - Login")
        self.root.geometry("420x220")
        self.current_user = None
        self.ensure_reports_dir()
        self.build_login_ui()

    def ensure_reports_dir(self):
        if not os.path.exists(REPORTS_DIR):
            os.makedirs(REPORTS_DIR)

    # ---------------- Login / Registration ----------------
    def build_login_ui(self):
        for w in self.root.winfo_children():
            w.destroy()
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(frame, text="Username:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", pady=5)
        self.login_user = tk.Entry(frame, font=("Arial", 11))
        self.login_user.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Password:", font=("Arial", 11)).grid(row=1, column=0, sticky="e", pady=5)
        self.login_pw = tk.Entry(frame, font=("Arial", 11), show="*")
        self.login_pw.grid(row=1, column=1, pady=5)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Login", width=12, command=self.login).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Register", width=12, command=self.register).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Guest", width=12, command=self.login_as_guest).pack(side=tk.LEFT, padx=5)

    def register(self):
        users = load_users()
        username = simpledialog.askstring("Register", "Enter new username:", parent=self.root)
        if not username:
            return
        if username in users:
            messagebox.showerror("Error", "Username already exists.")
            return
        pw = simpledialog.askstring("Register", "Enter password:", show="*", parent=self.root)
        if not pw:
            return
        pw2 = simpledialog.askstring("Register", "Confirm password:", show="*", parent=self.root)
        if pw != pw2:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        users[username] = {"password": hash_pw(pw)}
        save_users(users)
        messagebox.showinfo("Success", "User registered. You can now login.")

    def login(self):
        users = load_users()
        username = self.login_user.get().strip()
        pw = self.login_pw.get()
        if not username or not pw:
            messagebox.showerror("Error", "Enter username and password.")
            return
        user = users.get(username)
        if not user or user.get("password") != hash_pw(pw):
            messagebox.showerror("Error", "Invalid credentials.")
            return
        self.current_user = username
        self.build_main_ui()

    def login_as_guest(self):
        self.current_user = "guest"
        self.build_main_ui()

    # ---------------- Main UI ----------------
    def build_main_ui(self):
        self.root.title(f"Time Management System - {self.current_user}")
        self.root.geometry("1000x540")
        for w in self.root.winfo_children():
            w.destroy()

        self.tasks = load_tasks()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#00796b", foreground="white")
        style.configure("Treeview", font=("Arial", 11), rowheight=28)
        style.map("Treeview", background=[("selected", "#80deea")])

        form_frame = tk.Frame(self.root, bg="#b2dfdb", padx=10, pady=10, bd=2, relief="groove")
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(form_frame, text="Title:", font=("Arial", 12, "bold"), bg="#b2dfdb").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = tk.Entry(form_frame, font=("Arial", 12), bg="#e0f2f1", width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Deadline (YYYY-MM-DD):", font=("Arial", 12, "bold"), bg="#b2dfdb").grid(row=0, column=2, padx=5, pady=5)
        self.deadline_entry = tk.Entry(form_frame, font=("Arial", 12), bg="#e0f2f1", width=14)
        self.deadline_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Priority:", font=("Arial", 12, "bold"), bg="#b2dfdb").grid(row=0, column=4, padx=5, pady=5)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_menu = ttk.Combobox(form_frame, textvariable=self.priority_var,
                                          values=["High", "Medium", "Low"], state="readonly", width=10, font=("Arial", 12))
        self.priority_menu.grid(row=0, column=5, padx=5, pady=5)

        self.add_btn = tk.Button(form_frame, text="Add Task", font=("Arial", 12, "bold"), bg="#00796b", fg="white", command=self.add_task)
        self.add_btn.grid(row=0, column=6, padx=5, pady=5)

        tree_frame = tk.Frame(self.root, bg="#80cbc4", bd=2, relief="groove")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("Title","Deadline", "Priority", "Status", "Progress", "End Time", "Reminder"), show="headings", selectmode="browse")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Deadline", text="Deadline")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Progress", text="Progress %")
        self.tree.heading("End Time", text="End Time")
        self.tree.heading("Reminder", text="Reminder Time")
        self.tree.column("Title", width=260)
        self.tree.column("Deadline", width=110)
        self.tree.column("Priority", width=90)
        self.tree.column("Status", width=100)
        self.tree.column("Progress", width=90)
        self.tree.column("End Time", width=150)
        self.tree.column("Reminder", width=160)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.toggle_complete)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar.set)

        # --- Context menu for task actions (right-click) ---
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Mark Completed", command=self.mark_completed)
        self.context_menu.add_command(label="Set Description", command=self.set_description)
        self.context_menu.add_command(label="Set Reminder", command=self.set_reminder_manual)
        self.context_menu.add_command(label="Set Progress", command=self.set_progress)
        self.context_menu.add_command(label="Set End Time", command=self.set_end_time)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Task", command=self.delete_task)

        # show context menu on right-click; also select the item under mouse
        self.tree.bind("<Button-3>", self._on_right_click)

        btn_frame = tk.Frame(self.root, bg="#e0f7fa", padx=5, pady=5)
        btn_frame.pack(pady=5, fill=tk.X)
        tk.Button(btn_frame, text="Mark Completed", command=self.mark_completed, width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Set End Time", command=self.set_end_time, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Set Description", command=self.set_description, width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Set Reminder", command=self.set_reminder_manual, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Set Progress", command=self.set_progress, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Generate Monthly Report", command=self.generate_monthly_report, width=20).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Logout", command=self.logout, width=10).pack(side=tk.RIGHT, padx=5)

        # reminders
        self.reminder_interval_ms = 60 * 1000  # 1 minute checks
        self.schedule_next_reminder()
        self.refresh_tasks()

    # ---------------- Task operations ----------------
    def add_task(self):
        title = self.title_entry.get().strip()
        deadline = self.deadline_entry.get().strip()
        priority = self.priority_var.get()
        if not title or not deadline:
            messagebox.showerror("Error", "Please enter title and deadline.")
            return
        try:
            dl_date = datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return
        desc = simpledialog.askstring("Description", "Enter task description (optional):", parent=self.root) or ""
        # compute automatic reminder: last day before deadline at 09:00 if possible, else 1 minute from now
        reminder_time = (dl_date - timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        if reminder_time < datetime.now():
            reminder_time = datetime.now() + timedelta(minutes=1)
        reminder_iso = reminder_time.strftime("%Y-%m-%d %H:%M:%S")
        task = {
            "title": title,
            "description": desc,
            "deadline": deadline,
            "priority": priority,
            "completed": False,
            "progress": 0,
            "end_time": "",
            "reminder_time": reminder_iso,
            "notified": False,
            "created_by": self.current_user,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tasks = load_tasks()
        tasks.append(task)
        save_tasks(tasks)
        self.title_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.refresh_tasks()



    def refresh_tasks(self):
        self.tasks = load_tasks()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, t in enumerate(self.tasks):
            # show only tasks for current user and guest can see all
            if self.current_user != "guest" and t.get("created_by") != self.current_user:
                continue
            status = "✔" if t.get("completed") else "❌"
            prog = t.get("progress", 0)
            end_time = t.get("end_time", "")
            reminder = t.get("reminder_time", "")
            self.tree.insert("", "end", iid=idx, values=(t.get("title",""), t.get("deadline",""), t.get("priority",""), status, prog, end_time, reminder))
            # tags
            if t.get("completed"):
                self.tree.item(idx, tags=("completed",))
            elif t.get("priority") == "High":
                self.tree.item(idx, tags=("high",))
            try:
                dl = datetime.strptime(t.get("deadline",""), "%Y-%m-%d")
                if not t.get("completed") and dl < datetime.now():
                    self.tree.item(idx, tags=("overdue",))
            except:
                pass
        self.tree.tag_configure("completed", foreground="gray")
        self.tree.tag_configure("high", background="#ffebee")
        self.tree.tag_configure("overdue", background="#ffccbc")

    def mark_completed(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task.")
            return
        idx = int(selected[0])
        tasks = load_tasks()
        if idx < 0 or idx >= len(tasks):
            return
        task = tasks[idx]
        if task.get("created_by") != self.current_user and self.current_user != "guest":
            messagebox.showerror("Error", "You can only modify your tasks.")
            return
        task["completed"] = True
        task["progress"] = 100
        task["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_tasks(tasks)
        self.refresh_tasks()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task.")
            return
        idx = int(selected[0])
        tasks = load_tasks()
        task = tasks[idx]
        if task.get("created_by") != self.current_user and self.current_user != "guest":
            messagebox.showerror("Error", "You can only delete your tasks.")
            return
        if messagebox.askyesno("Confirm", f"Delete '{task.get('title')}'?"):
            tasks.pop(idx)
            save_tasks(tasks)
            self.refresh_tasks()

    def set_end_time(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task.")
            return
        idx = int(selected[0])
        tasks = load_tasks()
        task = tasks[idx]
        if task.get("created_by") != self.current_user and self.current_user != "guest":
            messagebox.showerror("Error", "You can only modify your tasks.")
            return
        ans = simpledialog.askstring("End Time", "Enter end time (YYYY-MM-DD HH:MM) or blank to clear:", initialvalue=task.get("end_time",""), parent=self.root)
        if ans is None:
            return
        ans = ans.strip()
        if ans == "":
            task["end_time"] = ""
        else:
            try:
                dt = datetime.strptime(ans, "%Y-%m-%d %H:%M")
                task["end_time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                task["completed"] = True
                task["progress"] = 100
            except ValueError:
                messagebox.showerror("Error", "Invalid format.")
                return
        save_tasks(tasks)
        self.refresh_tasks()

    def set_description(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task.")
            return
        idx = int(selected[0])
        tasks = load_tasks()
        task = tasks[idx]
        if task.get("created_by") != self.current_user and self.current_user != "guest":
            messagebox.showerror("Error", "You can only modify your tasks.")
            return
        ans = simpledialog.askstring("Description", "Enter description:", initialvalue=task.get("description",""), parent=self.root)
        if ans is None:
            return
        task["description"] = ans
        save_tasks(tasks)
        self.refresh_tasks()

    def set_reminder_manual(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task.")
            return
        idx = int(selected[0])
        tasks = load_tasks()
        task = tasks[idx]
        if task.get("created_by") != self.current_user and self.current_user != "guest":
            messagebox.showerror("Error", "You can only modify your tasks.")
            return
        ans = simpledialog.askstring("Set Reminder", "Enter reminder datetime (YYYY-MM-DD HH:MM) or blank to clear:", initialvalue=task.get("reminder_time",""), parent=self.root)
        if ans is None:
            return
        ans = ans.strip()
        if ans == "":
            task["reminder_time"] = ""
            task["notified"] = False
        else:
            try:
                dt = datetime.strptime(ans, "%Y-%m-%d %H:%M")
                task["reminder_time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                task["notified"] = False
            except ValueError:
                messagebox.showerror("Error", "Invalid format.")
                return
        save_tasks(tasks)
        self.refresh_tasks()

    def set_progress(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task.")
            return
        idx = int(selected[0])
        tasks = load_tasks()
        task = tasks[idx]
        if task.get("created_by") != self.current_user and self.current_user != "guest":
            messagebox.showerror("Error", "You can only modify your tasks.")
            return
        try:
            ans = simpledialog.askinteger("Progress", "Enter progress percent (0-100):", minvalue=0, maxvalue=100, initialvalue=task.get("progress",0), parent=self.root)
        except:
            return
        if ans is None:
            return
        task["progress"] = int(ans)
        if task["progress"] >= 100:
            task["progress"] = 100
            task["completed"] = True
            task["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            task["completed"] = False
            task["end_time"] = ""
        save_tasks(tasks)
        self.refresh_tasks()

    # ---------------- Reminder system ----------------
    def check_reminders(self):
        tasks = load_tasks()
        now = datetime.now()
        for idx, t in enumerate(tasks):
            # skip if not this user's task unless guest
            if self.current_user != "guest" and t.get("created_by") != self.current_user:
                continue
            if t.get("completed"):
                continue
            rt = t.get("reminder_time", "")
            if not rt:
                continue
            try:
                rt_dt = datetime.strptime(rt, "%Y-%m-%d %H:%M:%S")
            except:
                try:
                    rt_dt = datetime.strptime(rt, "%Y-%m-%d %H:%M")
                except:
                    continue
            if not t.get("notified", False) and rt_dt <= now:
                # show notification
                msg = f"Reminder: {t.get('title')}\nDue: {t.get('deadline')}\nPriority: {t.get('priority')}\n\n{t.get('description','')}"
                try:
                    messagebox.showinfo("Task Reminder", msg)
                except:
                    pass
                # mark notified to avoid repeat
                t["notified"] = True
                tasks[idx] = t
        save_tasks(tasks)

    def schedule_next_reminder(self):
        self.root.after(self.reminder_interval_ms, self._reminder_callback)

    def _reminder_callback(self):
        self.check_reminders()
        self.schedule_next_reminder()

    # ---------------- Reports ----------------
    def generate_monthly_report(self):
        # ask month and year
        year = simpledialog.askinteger("Report Year", "Enter year (YYYY):", parent=self.root, minvalue=2000, maxvalue=2100)
        if year is None:
            return
        month = simpledialog.askinteger("Report Month", "Enter month (1-12):", parent=self.root, minvalue=1, maxvalue=12)
        if month is None:
            return
        tasks = load_tasks()
        # filter tasks created_by current user unless guest
        user_tasks = [t for t in tasks if (self.current_user == "guest" or t.get("created_by") == self.current_user)]
        # tasks completed in that month
        completed = []
        for t in user_tasks:
            et = t.get("end_time","")
            if not et:
                continue
            try:
                etd = datetime.strptime(et, "%Y-%m-%d %H:%M:%S")
            except:
                continue
            if etd.year == year and etd.month == month:
                completed.append(t)
        total = len(user_tasks)
        completed_count = len(completed)
        pending = total - completed_count
        avg_completion = ""
        if completed_count:
            total_seconds = 0
            count = 0
            for t in completed:
                try:
                    created = datetime.strptime(t.get("created_at"), "%Y-%m-%d %H:%M:%S")
                    ended = datetime.strptime(t.get("end_time"), "%Y-%m-%d %H:%M:%S")
                    total_seconds += (ended - created).total_seconds()
                    count += 1
                except:
                    pass
            if count:
                avg = total_seconds / count
                avg_completion = str(timedelta(seconds=int(avg)))
        filename = os.path.join(REPORTS_DIR, f"report_{self.current_user}_{year}_{month:02d}.csv")
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["User", self.current_user])
            writer.writerow(["Year", year])
            writer.writerow(["Month", month])
            writer.writerow(["Total Tasks", total])
            writer.writerow(["Completed", completed_count])
            writer.writerow(["Pending", pending])
            writer.writerow(["Average Completion Time", avg_completion])
            writer.writerow([])
            writer.writerow(["Title","Description","Deadline","Priority","Progress","Created At","End Time"])
            for t in user_tasks:
                writer.writerow([t.get("title",""), t.get("description",""), t.get("deadline",""), t.get("priority",""), t.get("progress",""), t.get("created_at",""), t.get("end_time","")])
        messagebox.showinfo("Report Generated", f"Saved to {filename}")

    def logout(self):
        self.current_user = None
        self.root.title("Time Management System - Login")
        self.build_login_ui()
    
    # def refresh_tasks(self):
    #     self.tasks = load_tasks()
    #     for row in self.tree.get_children():
    #         self.tree.delete(row)

    #     for t in self.tasks:
    #         if self.current_user != "guest" and t.get("created_by") != self.current_user:
    #             continue

    #         task_id = t.get("id")
    #         status = "✔" if t.get("completed") else "❌"
    #         prog = t.get("progress", 0)
    #         end_time = t.get("end_time", "")
    #         reminder = t.get("reminder_time", "")

    #         # Insert first, then safely tag
    #         self.tree.insert("", "end", iid=task_id, values=(
    #             t.get("title", ""), t.get("deadline", ""), t.get("priority", ""), status, prog, end_time, reminder))

    #         tags = []
    #         if t.get("completed"):
    #             tags.append("completed")
    #         elif t.get("priority") == "High":
    #             tags.append("high")

    #         try:
    #             dl = datetime.strptime(t.get("deadline", ""), "%Y-%m-%d")
    #             if not t.get("completed") and dl < datetime.now():
    #                 tags.append("overdue")
    #         except:
    #             pass

    #         if tags:
    #             self.tree.item(task_id, tags=tuple(tags))

    #     # Configure tag colors after all insertions
    #     self.tree.tag_configure("completed", foreground="gray")
    #     self.tree.tag_configure("high", background="#ffebee")
    #     self.tree.tag_configure("overdue", background="#ffccbc")

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a task to delete.")
            return

        task_id = selected[0]
        tasks = load_tasks()
        task = next((t for t in tasks if t.get("id") == task_id), None)

        if not task:
            messagebox.showerror("Error", "Task not found.")
            return

        if task.get("created_by") != self.current_user and self.current_user != "guest":
            messagebox.showerror("Error", "You can only delete your own tasks.")
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{task.get('title')}'?"):
            tasks = [t for t in tasks if t.get("id") != task_id]
            save_tasks(tasks)
            self.refresh_tasks()
            messagebox.showinfo("Deleted", f"Task '{task.get('title')}' deleted successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
