import tkinter as tk
from pathlib import Path

from .ui import FocusExplorerApp, import_lionscliapp


def cmd_launch_gui(cli) -> None:
    start_dir = str(cli.ctx.get("path.start_dir", Path.cwd()))
    root = tk.Tk()
    FocusExplorerApp(root, start_dir=start_dir, cli=cli)
    root.mainloop()


def main() -> None:
    cli = import_lionscliapp()
    cli.declare_app("focus-explorer", "0.2")
    cli.describe_app("Focus-aware file explorer with anchors, stack, and task strip.")
    cli.declare_projectdir(".focus-explorer")
    cli.declare_key("path.start_dir", str(Path.cwd()))
    cli.describe_key("path.start_dir", "Default startup directory for the explorer")
    cli.declare_cmd("", lambda: cmd_launch_gui(cli))
    cli.main()


if __name__ == "__main__":
    main()
