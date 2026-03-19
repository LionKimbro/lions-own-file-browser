from pathlib import Path


def show_overlay(app) -> None:
    refresh_overlay_labels(app)
    x = app.root.winfo_rootx() + 300
    y = app.root.winfo_rooty() + 80
    app.overlay.geometry(f"640x240+{x}+{y}")
    app.overlay.deiconify()


def hide_overlay(app) -> None:
    app.overlay.withdraw()


def refresh_overlay_labels(app) -> None:
    from .ui_app import ICON_LABELS

    for key, lbl in app.overlay_labels.items():
        anchor = app.anchors.get(key)
        if anchor:
            leaf = Path(anchor.path).name or anchor.path
            icon = ICON_LABELS.get(anchor.icon, "[ ]")
            lbl.configure(text=f"{key} {icon}\n{leaf}", bg="#22405e")
        else:
            lbl.configure(text=f"{key} [ ]", bg="#1b2735")
