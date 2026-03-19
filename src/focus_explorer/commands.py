def execute(app, raw: str) -> None:
    parts = raw.split()
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "set-icon":
        app.cmd_set_icon(args)
    elif cmd == "set-focus":
        app.task_text.set(" ".join(args) if args else app.task_text.get())
        app.show_status("Immediate task updated")
    elif cmd == "add-task":
        app.cmd_add_task(args)
    elif cmd == "remove-task":
        app.cmd_remove_task(args)
    elif cmd == "set-task":
        app.cmd_set_task(args)
    elif cmd == "list-tasks":
        app.cmd_list_tasks()
    elif cmd == "set-hierarchy":
        app.hierarchy_text.set(" ".join(args) if args else app.hierarchy_text.get())
        app.show_status("Hierarchy text updated")
    elif cmd == "next-task":
        app.next_task()
    elif cmd == "set-root":
        app.cmd_set_root(args)
    elif cmd == "open":
        app.cmd_open(args)
    elif cmd == "run":
        app.cmd_run(args)
    elif cmd == "save":
        app.save_state()
        app.show_status("Saved state")
    else:
        app.show_status(
            "Commands: set-icon, set-focus, add-task, remove-task, set-task, list-tasks, set-hierarchy, next-task, set-root, open, run, save"
        )
