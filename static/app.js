




    document.addEventListener("DOMContentLoaded", () => {
    const STORAGE_KEY = "tms_tasks";
    const taskForm = document.getElementById("taskForm");
    const tasksDiv = document.getElementById("tasks");

    function loadTasks() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch {
            return [];
        }
    }

    function saveTasks(tasks) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    }

    function renderTasks() {
        const tasks = loadTasks();
        tasksDiv.innerHTML = "";
        if (tasks.length === 0) {
            tasksDiv.innerHTML = "<p>No tasks found!</p>";
            return;
        }
        tasks.forEach((task, idx) => {
            const taskEl = document.createElement("div");
            taskEl.className = "task" + (task.completed ? " completed" : "") + " " + (task.priority.toLowerCase() || "");
            taskEl.innerHTML = `
                <span>
                    <strong>${task.title}</strong> | Deadline: ${task.deadline} | Priority: ${task.priority}
                </span>
                <span class="task-actions">
                    <button onclick="completeTask(${idx})" ${task.completed ? "disabled" : ""}>Complete</button>
                    <button onclick="deleteTask(${idx})">Delete</button>
                </span>
            `;
            tasksDiv.appendChild(taskEl);
        });
    }

    taskForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const title = document.getElementById("title").value.trim();
        const deadline = document.getElementById("deadline").value;
        const priority = document.getElementById("priority").value;

        if (!title || !deadline) {
            alert("Please enter a title and deadline.");
            return;
        }

        const tasks = loadTasks();
        tasks.push({
            title,
            deadline,
            priority,
            completed: false,
            createdAt: new Date().toISOString(),
        });
        saveTasks(tasks);
        taskForm.reset();
        renderTasks();
    });

    window.completeTask = function(idx) {
        const tasks = loadTasks();
        if (!tasks[idx]) return;
        tasks[idx].completed = true;
        saveTasks(tasks);
        renderTasks();
    };

    window.deleteTask = function(idx) {
        const tasks = loadTasks();
        tasks.splice(idx, 1);
        saveTasks(tasks);
        renderTasks();
    };

    renderTasks();
});