import tkinter as tk


def open_temple_window(app, _event=None) -> None:
    top = tk.Toplevel(app.root)
    top.title("Temple of Focus")
    top.geometry("760x520")
    top.configure(bg="#151b22")

    tk.Label(
        top,
        text="Temple of Focus",
        bg="#151b22",
        fg="#e8f2ff",
        font=("Segoe UI", 16, "bold"),
    ).pack(anchor="w", padx=14, pady=(12, 6))

    hierarchy_lbl = tk.Label(
        top,
        text=f"Hierarchy: {app.hierarchy_text.get()}",
        bg="#151b22",
        fg="#b8cae1",
        font=("Segoe UI", 10),
        wraplength=700,
        justify="left",
    )
    hierarchy_lbl.pack(anchor="w", padx=14, pady=(2, 4))

    task_lbl = tk.Label(
        top,
        text=f"Immediate task: {app.task_text.get()}",
        bg="#151b22",
        fg="#f4fbff",
        font=("Segoe UI", 12, "bold"),
        wraplength=700,
        justify="left",
    )
    task_lbl.pack(anchor="w", padx=14, pady=(2, 10))

    task_frame = tk.Frame(top, bg="#10161d", padx=10, pady=10)
    task_frame.pack(fill="both", expand=True, padx=14, pady=8)

    tk.Label(
        task_frame,
        text="Task Queue (auto-load next via command: next-task)",
        bg="#10161d",
        fg="#d2e5fb",
        anchor="w",
    ).pack(fill="x")

    listbox = tk.Listbox(task_frame, bg="#0b1016", fg="#dbe9ff", font=("Consolas", 10))
    listbox.pack(fill="both", expand=True, pady=(6, 8))

    edit_row = tk.Frame(task_frame, bg="#10161d")
    edit_row.pack(fill="x", pady=(0, 8))
    new_task_var = tk.StringVar()
    task_entry = tk.Entry(
        edit_row,
        textvariable=new_task_var,
        bg="#0b1016",
        fg="#e8f2ff",
        insertbackground="#e8f2ff",
        relief="flat",
        font=("Consolas", 10),
    )
    task_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

    def refresh_task_listbox(select_idx: int | None = None) -> None:
        listbox.delete(0, "end")
        for i, task in enumerate(app.task_queue):
            prefix = "> " if i == app.task_index else "  "
            listbox.insert("end", f"{prefix}{i + 1}. {task}")
        if app.task_queue:
            if select_idx is None:
                select_idx = app.task_index
            select_idx = min(max(select_idx, 0), len(app.task_queue) - 1)
            listbox.selection_set(select_idx)
            listbox.activate(select_idx)
            listbox.see(select_idx)
        hierarchy_lbl.configure(text=f"Hierarchy: {app.hierarchy_text.get()}")
        task_lbl.configure(text=f"Immediate task: {app.task_text.get()}")

    def add_task_from_entry() -> None:
        text = new_task_var.get().strip()
        if not text:
            return
        app.task_queue.append(text)
        app.task_index = len(app.task_queue) - 1
        app.sync_task_text()
        new_task_var.set("")
        refresh_task_listbox(app.task_index)

    def selected_index() -> int | None:
        selected = listbox.curselection()
        if not selected:
            return None
        return int(selected[0])

    def activate_selected() -> None:
        idx = selected_index()
        if idx is None or idx >= len(app.task_queue):
            return
        app.task_index = idx
        app.sync_task_text()
        refresh_task_listbox(idx)

    def remove_selected() -> None:
        idx = selected_index()
        if idx is None or idx >= len(app.task_queue):
            return
        app.task_queue.pop(idx)
        if app.task_queue:
            app.task_index = min(app.task_index, len(app.task_queue) - 1)
        else:
            app.task_index = 0
        app.sync_task_text()
        refresh_task_listbox(min(idx, len(app.task_queue) - 1 if app.task_queue else 0))

    def move_selected(delta: int) -> None:
        idx = selected_index()
        if idx is None:
            return
        new_idx = idx + delta
        if new_idx < 0 or new_idx >= len(app.task_queue):
            return
        app.task_queue[idx], app.task_queue[new_idx] = app.task_queue[new_idx], app.task_queue[idx]
        if app.task_index == idx:
            app.task_index = new_idx
        elif app.task_index == new_idx:
            app.task_index = idx
        app.sync_task_text()
        refresh_task_listbox(new_idx)

    def update_selected_from_entry() -> None:
        idx = selected_index()
        if idx is None or idx >= len(app.task_queue):
            return
        text = new_task_var.get().strip()
        if not text:
            return
        app.task_queue[idx] = text
        if app.task_index == idx:
            app.sync_task_text()
        refresh_task_listbox(idx)
        new_task_var.set("")

    task_entry.bind("<Return>", lambda _: add_task_from_entry())
    listbox.bind("<Double-1>", lambda _: activate_selected())

    tk.Button(edit_row, text="Add", command=add_task_from_entry, width=8).pack(side="left")

    control_row = tk.Frame(task_frame, bg="#10161d")
    control_row.pack(fill="x")
    tk.Button(control_row, text="Set Current", command=activate_selected, width=10).pack(side="left", padx=(0, 6))
    tk.Button(control_row, text="Update", command=update_selected_from_entry, width=8).pack(side="left", padx=(0, 6))
    tk.Button(control_row, text="Remove", command=remove_selected, width=8).pack(side="left", padx=(0, 6))
    tk.Button(control_row, text="Move Up", command=lambda: move_selected(-1), width=8).pack(side="left", padx=(0, 6))
    tk.Button(control_row, text="Move Down", command=lambda: move_selected(1), width=9).pack(side="left")

    refresh_task_listbox()

    actions = tk.Frame(top, bg="#151b22")
    actions.pack(fill="x", padx=14, pady=(0, 12))
    tk.Button(actions, text="Next Task", command=app.next_task, width=10).pack(side="left", padx=(0, 6))
    tk.Button(actions, text="Close", command=top.destroy, width=8).pack(side="left")
