import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ui_app import FocusExplorerApp


def get_state_payload(app: "FocusExplorerApp") -> dict:
    return {
        "current_dir": app.current_dir,
        "anchors": {k: {"path": a.path, "icon": a.icon} for k, a in app.anchors.items()},
        "stack": app.dir_stack,
        "focus": {
            "hierarchy": app.hierarchy_text.get(),
            "task": app.task_text.get(),
            "task_queue": app.task_queue,
            "task_index": app.task_index,
        },
        "notes": {
            "text": app.notes_text.get("1.0", "end-1c"),
            "open": app.notes_open,
        },
    }


def save_state(app: "FocusExplorerApp") -> None:
    payload = get_state_payload(app)
    if app.cli is not None:
        app.cli.write_json("state.json", payload, "p2")
        return
    with open("focus_explorer_state.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_state(app: "FocusExplorerApp") -> None:
    from .ui_app import ANCHOR_KEYS, Anchor, norm

    data = None
    if app.cli is not None:
        try:
            data = app.cli.read_json("state.json", "p")
        except FileNotFoundError:
            return
        except Exception as exc:
            app.show_status(f"State load error: {exc}")
            return
    else:
        if not os.path.isfile("focus_explorer_state.json"):
            return
        with open("focus_explorer_state.json", "r", encoding="utf-8") as f:
            data = json.load(f)

    if not isinstance(data, dict):
        return

    state_dir = norm(data.get("current_dir", app.current_dir))
    if os.path.isdir(state_dir):
        app.current_dir = state_dir

    app.anchors = {
        k: Anchor(path=v.get("path", app.current_dir), icon=v.get("icon", "none"))
        for k, v in data.get("anchors", {}).items()
        if k in ANCHOR_KEYS and isinstance(v, dict)
    }
    app.dir_stack = [norm(p) for p in data.get("stack", []) if isinstance(p, str) and os.path.isdir(p)]

    focus = data.get("focus", {})
    if isinstance(focus, dict):
        app.hierarchy_text.set(focus.get("hierarchy", app.hierarchy_text.get()))
        queue = focus.get("task_queue", app.task_queue)
        if isinstance(queue, list):
            app.task_queue = [str(t) for t in queue]
        try:
            app.task_index = int(focus.get("task_index", app.task_index))
        except Exception:
            app.task_index = 0
    app.sync_task_text()

    notes = data.get("notes", {})
    if isinstance(notes, dict):
        text = notes.get("text", "")
        if isinstance(text, str) and text:
            app.notes_text.delete("1.0", "end")
            app.notes_text.insert("1.0", text)
        if notes.get("open", False):
            app.toggle_notes_pane()
