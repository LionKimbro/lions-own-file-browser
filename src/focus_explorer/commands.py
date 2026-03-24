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
    elif cmd == "name":
        app.cmd_name(args)
    elif cmd == "go":
        app.cmd_go(args)
    elif cmd == "set-root":
        app.cmd_set_root(args)
    elif cmd == "open":
        app.cmd_open(args)
    elif cmd == "run":
        app.cmd_run(args)
    elif cmd == "mkdir":
        app.cmd_mkdir(args)
    elif cmd == "rmdir":
        app.cmd_rmdir(args)
    elif cmd == "save":
        app.save_state()
        app.show_status("Saved state")
    elif cmd in ("quit", "exit"):
        app.on_app_close()
    else:
        app.show_status(
            "Commands: name, go, set-icon, set-focus, add-task, remove-task, set-task, list-tasks, set-hierarchy, next-task, set-root, open, run, mkdir, rmdir, save, quit, exit"
        )
