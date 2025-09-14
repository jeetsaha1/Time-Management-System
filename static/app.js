




    document.addEventListener("DOMContentLoaded", () => {
    const taskForm = document.getElementById("taskForm");
    const tasksDiv = document.getElementById("tasks");

    function fetchTasks() {
        fetch("/tasks")
            .then(res => res.json())
            .then(tasks => {
                tasksDiv.innerHTML = "";
                if (tasks.length === 0) {
                    tasksDiv.innerHTML = "<p>No tasks found!</p>";
                    return;
                }
                tasks.forEach((task, idx) => {
                    const taskEl = document.createElement("div");
                    taskEl.className = "task" + (task.completed ? " completed" : "");
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
            });
    }

    taskForm.onsubmit = (e) => {
        e.preventDefault();
        const title = document.getElementById("title").value;
        const deadline = document.getElementById("deadline").value;
        const priority = document.getElementById("priority").value;
        fetch("/tasks", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, deadline, priority })
        })
        .then(res => {
            if (!res.ok) return res.json().then(data => { throw data.error });
            return res.json();
        })
        .then(() => {
            taskForm.reset();
            fetchTasks();
        })
        .catch(alert);
    };

    window.completeTask = function(idx) {
        fetch(`/tasks/${idx}/complete`, { method: "POST" })
            .then(() => fetchTasks());
    };

    window.deleteTask = function(idx) {
        fetch(`/tasks/${idx}`, { method: "DELETE" })
            .then(() => fetchTasks());
    };

    fetchTasks();
});