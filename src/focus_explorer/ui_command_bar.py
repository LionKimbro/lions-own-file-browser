from . import commands


def open_command_bar(app, _event=None) -> str:
    app.command_entry_var.set("")
    app.command_overlay.place(relx=0.5, rely=0.94, anchor="s")
    app.command_entry.focus_set()
    return "break"


def hide_command_bar(app) -> None:
    app.command_overlay.place_forget()
    app.file_list.focus_set()


def run_command_bar(app, _event=None) -> str:
    raw = app.command_entry_var.get().strip()
    hide_command_bar(app)
    if not raw:
        return "break"

    commands.execute(app, raw)
    return "break"
