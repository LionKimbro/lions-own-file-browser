import os
import subprocess
import sys
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, simpledialog

from . import ui_command_bar
from . import ui_overlay
from . import ui_panes
from . import state
from . import ui_temple_dialog

try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:
    Image = None
    ImageTk = None


def import_lionscliapp():
    try:
        import lionscliapp as cli  # type: ignore
        return cli
    except Exception:
        fallback_src = Path(r"F:\lion\github\lionscliapp\src")
        if fallback_src.exists():
            sys.path.insert(0, str(fallback_src))
            import lionscliapp as cli  # type: ignore
            return cli
        raise


def norm(path: str) -> str:
    return os.path.normpath(path)


ANCHOR_KEYS = "QWERTASDFGZXCVB"
ICON_LABELS = {
    "repo": "🐙",
    "graphics": "🖼️",
    "docs": "📄",
    "scripts": "⚙️",
    "temp": "⏱️",
    "audio": "🎵",
    "video": "🎬",
    "star": "⭐",
    "in": "⮷",
    "out": "⮵",
    "none": "·",
}


@dataclass
class Anchor:
    path: str
    icon: str = "none"


class FocusExplorerApp:
    def __init__(self, root: tk.Tk, start_dir: str | None = None, cli=None):
        self.root = root
        self.cli = cli
        self.root.title("Focus Explorer MVP")
        self.root.geometry("1200x760")
        self.root.protocol("WM_DELETE_WINDOW", self.on_app_close)

        self.current_dir = norm(start_dir or os.getcwd())
        self.back_history: list[str] = []
        self.forward_history: list[str] = []
        self.dir_stack: list[str] = []
        self.anchors: dict[str, Anchor] = {}

        self.hierarchy_text = tk.StringVar(value="Temple -> Session -> Active Task")
        self.task_queue: list[str] = [
            "Run Gemini upscale",
            "Review output images",
            "Rename and tidy files",
        ]
        self.task_index = 0
        self.task_text = tk.StringVar(value=self.task_queue[self.task_index])
        self.preview_image_ref = None

        self.toast_after_id: str | None = None
        self.notes_open = False
        self.named_paths: dict[str, str] = {}

        self.build_ui()
        self.bind_keys()
        self.load_state()
        self.refresh_dir(self.current_dir, record_history=False)
        self.update_stack_text()

    def build_ui(self) -> None:
        ui_panes.build_ui(self)

    def bind_keys(self) -> None:
        self.root.bind_all("<Control-space>", self.open_command_bar)
        self.root.bind_all("<Control-t>", self.open_terminal_hotkey)
        self.root.bind_all("<Control-n>", self.new_task_hotkey)
        self.root.bind_all("<Control-Return>", self.push_current_dir)
        self.root.bind_all("<Control-BackSpace>", self.pop_dir)
        self.root.bind_all("<Control-Left>", self.nav_back)
        self.root.bind_all("<Control-Right>", self.nav_forward)
        self.root.bind_all("<Control-Up>", lambda _: self.go_parent())

        self.root.bind_all("<KeyPress-Control_L>", lambda _: self.show_overlay())
        self.root.bind_all("<KeyPress-Control_R>", lambda _: self.show_overlay())
        self.root.bind_all("<KeyRelease-Control_L>", lambda _: self.hide_overlay())
        self.root.bind_all("<KeyRelease-Control_R>", lambda _: self.hide_overlay())

        self.root.bind_all("<Alt-d>", self.focus_path_entry)
        self.root.bind_all("<Control-semicolon>", lambda _: self.file_list.focus_set())
        self.root.bind_all("<KeyPress>", self.handle_anchor_hotkeys)

    def show_overlay(self) -> None:
        ui_overlay.show_overlay(self)

    def hide_overlay(self) -> None:
        ui_overlay.hide_overlay(self)

    def refresh_overlay_labels(self) -> None:
        ui_overlay.refresh_overlay_labels(self)

    def format_size(self, num_bytes: int) -> str:
        units = ["B", "KB", "MB", "GB"]
        size = float(num_bytes)
        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{num_bytes} B"

    def file_target_from_item(self, item_id: str | None) -> str | None:
        if not item_id:
            return None
        name = self.file_list.item(item_id, "text")
        if not name:
            return None
        return norm(os.path.join(self.current_dir, name))

    def get_image_dimensions(self, path: str) -> tuple[int, int] | None:
        ext = Path(path).suffix.lower()
        if ext not in {".png", ".gif", ".jpg", ".jpeg", ".bmp", ".webp", ".ppm", ".pgm"}:
            return None
        try:
            if Image is not None:
                with Image.open(path) as img:
                    return img.size
            if ext in {".png", ".gif", ".ppm", ".pgm"}:
                tk_img = tk.PhotoImage(file=path)
                return (tk_img.width(), tk_img.height())
        except Exception:
            pass
        return None

    def update_details_for_target(self, target: str | None) -> None:
        if not target:
            self.details_name.set("Name: -")
            self.details_type.set("Type: -")
            self.details_dimensions.set("Dimensions: -")
            self.details_size.set("Size: -")
            self.details_modified.set("Modified: -")
            self.details_path.set("Path: -")
            self.preview_label.configure(image="", text="Image preview")
            self.preview_image_ref = None
            return

        p = Path(target)
        name = p.name
        kind = "Directory" if p.is_dir() else "File"
        size = "-"
        modified = "-"
        try:
            stat = p.stat()
            if p.is_file():
                size = self.format_size(stat.st_size)
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

        dims = self.get_image_dimensions(target) if p.is_file() else None

        self.details_name.set(f"Name: {name}")
        self.details_type.set(f"Type: {kind}")
        self.details_dimensions.set(f"Dimensions: {dims[0]} × {dims[1]}" if dims else "Dimensions: -")
        self.details_size.set(f"Size: {size}")
        self.details_modified.set(f"Modified: {modified}")
        self.details_path.set(f"Path: {target}")
        self.update_preview(target)

    def update_preview(self, target: str) -> None:
        path = Path(target)
        if not path.is_file():
            self.preview_label.configure(image="", text="No preview (not a file)")
            self.preview_image_ref = None
            return

        ext = path.suffix.lower()
        image_exts = {".png", ".gif", ".ppm", ".pgm", ".jpg", ".jpeg", ".bmp", ".webp"}
        if ext not in image_exts:
            self.preview_label.configure(image="", text="No preview (not an image)")
            self.preview_image_ref = None
            return

        try:
            if Image is not None and ImageTk is not None:
                img = Image.open(target)
                img.thumbnail((280, 280))
                tk_img = ImageTk.PhotoImage(img)
                self.preview_label.configure(image=tk_img, text="")
                self.preview_image_ref = tk_img
                return

            tk_img = tk.PhotoImage(file=target)
            self.preview_label.configure(image=tk_img, text="")
            self.preview_image_ref = tk_img
        except Exception:
            self.preview_label.configure(
                image="",
                text="Preview unavailable\n(install Pillow for more formats)",
            )
            self.preview_image_ref = None

    def refresh_dir(self, path: str, record_history: bool = True) -> None:
        path = norm(path)
        if not os.path.isdir(path):
            self.show_status(f"Not a directory: {path}")
            return

        if record_history and self.current_dir != path:
            self.back_history.append(self.current_dir)
            self.forward_history.clear()

        self.current_dir = path
        self.path_var.set(path)

        for item in self.file_list.get_children():
            self.file_list.delete(item)

        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                kind = "dir" if entry.is_dir() else "file"
                size = "" if entry.is_dir() else self.format_size(entry.stat().st_size)
                self.file_list.insert("", "end", text=entry.name, values=(kind, size))
            first = self.file_list.get_children()
            if first:
                self.file_list.focus(first[0])
                self.file_list.selection_set(first[0])
                self.file_list.see(first[0])
                self.update_details_for_target(self.file_target_from_item(first[0]))
            else:
                self.update_details_for_target(None)
            self.show_status(f"Opened: {path}")
        except PermissionError:
            self.show_status(f"Permission denied: {path}")
        except Exception as exc:
            self.show_status(f"Error: {exc}")

        self.refresh_anchor_panel()

    def show_status(self, text: str) -> None:
        self.status_var.set(text)

    def show_toast(self, text: str, ms: int = 900) -> None:
        if self.toast_after_id:
            self.root.after_cancel(self.toast_after_id)
            self.toast_after_id = None
        self.toast.configure(text=text)
        self.toast.place(relx=0.5, rely=0.08, anchor="center")

        def _hide() -> None:
            self.toast.place_forget()

        self.toast_after_id = self.root.after(ms, _hide)

    def refresh_anchor_panel(self) -> None:
        self.anchor_list.delete(0, "end")
        for key in sorted(self.anchors.keys()):
            anchor = self.anchors[key]
            icon = ICON_LABELS.get(anchor.icon, "[ ]")
            marker = "*" if norm(anchor.path) == self.current_dir else " "
            self.anchor_list.insert("end", f"{marker} {key} {icon}  {anchor.path}")
        self.refresh_overlay_labels()

    def anchor_for_current_dir(self) -> str | None:
        current = norm(self.current_dir)
        for key, anchor in self.anchors.items():
            if norm(anchor.path) == current:
                return key
        return None

    def open_selected_anchor(self, _event=None) -> None:
        idx = self.anchor_list.curselection()
        if not idx:
            return
        line = self.anchor_list.get(idx[0])
        parts = line.split()
        if len(parts) >= 2:
            key = parts[1]
            self.jump_anchor(key)

    def go_to_path(self) -> None:
        target = norm(self.path_var.get().strip())
        self.refresh_dir(target)

    def copy_current_path(self) -> None:
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_dir)
            self.root.update_idletasks()
            self.show_status(f"Copied path: {self.current_dir}")
        except Exception as exc:
            self.show_status(f"Copy path failed: {exc}")

    def on_file_activate(self, _event=None) -> None:
        if _event is not None and (int(getattr(_event, "state", 0)) & 0x4):
            return
        selected = self.file_list.selection()
        if not selected:
            return
        item = selected[0]
        name = self.file_list.item(item, "text")
        target = norm(os.path.join(self.current_dir, name))
        if os.path.isdir(target):
            self.refresh_dir(target)
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(target)
            else:
                subprocess.Popen(["xdg-open", target])
            self.show_status(f"Opened file: {name}")
        except Exception as exc:
            self.show_status(f"Open failed: {exc}")

    def on_file_select(self, _event=None) -> None:
        selected = self.file_list.selection()
        if not selected:
            self.update_details_for_target(None)
            return
        self.update_details_for_target(self.file_target_from_item(selected[0]))

    def on_file_list_up(self, _event=None) -> str:
        if _event is not None and (int(getattr(_event, "state", 0)) & 0x4):
            return None
        items = self.file_list.get_children()
        if not items:
            return "break"
        selected = self.file_list.selection()
        current = selected[0] if selected else items[0]
        idx = items.index(current)
        next_idx = max(0, idx - 1)
        next_item = items[next_idx]
        self.file_list.selection_set(next_item)
        self.file_list.focus(next_item)
        self.file_list.see(next_item)
        self.update_details_for_target(self.file_target_from_item(next_item))
        return "break"

    def on_file_list_down(self, _event=None) -> str:
        if _event is not None and (int(getattr(_event, "state", 0)) & 0x4):
            return None
        items = self.file_list.get_children()
        if not items:
            return "break"
        selected = self.file_list.selection()
        current = selected[0] if selected else items[0]
        idx = items.index(current)
        next_idx = min(len(items) - 1, idx + 1)
        next_item = items[next_idx]
        self.file_list.selection_set(next_item)
        self.file_list.focus(next_item)
        self.file_list.see(next_item)
        self.update_details_for_target(self.file_target_from_item(next_item))
        return "break"

    def open_terminal_here(self) -> None:
        path = self.current_dir
        try:
            subprocess.Popen(["wt", "-d", path])
            self.show_status(f"Opened Windows Terminal in {path}")
        except Exception:
            subprocess.Popen(["cmd", "/K", f"cd /d {path}"])
            self.show_status(f"Opened cmd in {path}")

    def open_browse_here(self) -> None:
        path = self.current_dir
        if not os.path.isdir(path):
            self.show_status(f"Directory not found: {path}")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            self.show_status(f"Opened file browser in {path}")
        except Exception as exc:
            self.show_status(f"Browse failed: {exc}")

    def open_terminal_hotkey(self, _event=None) -> str:
        self.open_terminal_here()
        return "break"

    def new_task_hotkey(self, _event=None) -> str:
        text = simpledialog.askstring("New Task", "Task text:", parent=self.root)
        if text and text.strip():
            self.task_queue.append(text.strip())
            self.task_index = len(self.task_queue) - 1
            self.sync_task_text()
            self.show_toast(f"Task added: {self.task_text.get()}")
        return "break"

    def go_parent(self) -> None:
        parent = norm(str(Path(self.current_dir).parent))
        if parent != self.current_dir:
            self.refresh_dir(parent)

    def nav_back(self, _event=None) -> None:
        if not self.back_history:
            self.show_status("Back history empty")
            return
        self.forward_history.append(self.current_dir)
        target = self.back_history.pop()
        self.refresh_dir(target, record_history=False)

    def nav_forward(self, _event=None) -> None:
        if not self.forward_history:
            self.show_status("Forward history empty")
            return
        self.back_history.append(self.current_dir)
        target = self.forward_history.pop()
        self.refresh_dir(target, record_history=False)

    def push_current_dir(self, _event=None) -> None:
        self.dir_stack.append(self.current_dir)
        self.update_stack_text()
        self.show_toast(f"Pushed: {Path(self.current_dir).name or self.current_dir}")

    def pop_dir(self, _event=None) -> None:
        if not self.dir_stack:
            self.show_status("Directory stack empty")
            return
        target = self.dir_stack.pop()
        self.update_stack_text()
        self.refresh_dir(target)
        self.show_toast(f"Popped: {Path(target).name or target}")

    def update_stack_text(self) -> None:
        if not self.dir_stack:
            self.stack_var.set("Stack: []")
            return
        tail = [Path(p).name or p for p in self.dir_stack[-6:]]
        self.stack_var.set(f"Stack top -> {tail[::-1]}")

    def toggle_anchor(self, key: str) -> None:
        key = key.upper()
        current = norm(self.current_dir)
        existing = self.anchors.get(key)
        if existing and norm(existing.path) == current:
            del self.anchors[key]
            self.show_toast(f"Unanchored {key}")
            self.show_status(f"Removed anchor {key} from {current}")
        else:
            self.anchors[key] = Anchor(path=current, icon="none")
            leaf = Path(current).name or current
            self.show_toast(f"Anchored {key} -> {leaf}")
            self.show_status(f"Anchor {key} set to {current}")
        self.refresh_anchor_panel()

    def jump_anchor(self, key: str) -> None:
        key = key.upper()
        anchor = self.anchors.get(key)
        if not anchor:
            self.show_status(f"No anchor on {key}")
            return
        self.refresh_dir(anchor.path)
        self.file_list.focus_set()

    def handle_anchor_hotkeys(self, event: tk.Event) -> str | None:
        widget = event.widget
        if widget is self.command_entry:
            return None

        # Do not steal Ctrl key combos from text-editing widgets.
        widget_class = ""
        try:
            widget_class = widget.winfo_class()
        except Exception:
            pass
        if widget_class in {"Entry", "TEntry", "Text", "Spinbox", "TCombobox"}:
            return None

        state = int(getattr(event, "state", 0))
        ctrl_pressed = bool(state & 0x4)
        if not ctrl_pressed:
            return None

        key = (event.keysym or "").upper()
        if key not in ANCHOR_KEYS:
            return None
        if key == "T" and not bool(state & 0x1):
            return None

        shift_pressed = bool(state & 0x1)
        if shift_pressed:
            self.toggle_anchor(key)
        else:
            self.jump_anchor(key)
        return "break"

    def open_command_bar(self, _event=None) -> str:
        return ui_command_bar.open_command_bar(self, _event)

    def hide_command_bar(self) -> None:
        ui_command_bar.hide_command_bar(self)

    def run_command_bar(self, _event=None) -> str:
        return ui_command_bar.run_command_bar(self, _event)

    def sync_task_text(self) -> None:
        if not self.task_queue:
            self.task_index = 0
            self.task_text.set("(no tasks)")
            return
        self.task_index = min(max(self.task_index, 0), len(self.task_queue) - 1)
        self.task_text.set(self.task_queue[self.task_index])

    def cmd_add_task(self, args: list[str]) -> None:
        text = " ".join(args).strip()
        if not text:
            self.show_status("Usage: add-task <task text>")
            return
        self.task_queue.append(text)
        if len(self.task_queue) == 1:
            self.task_index = 0
        self.sync_task_text()
        self.show_status(f"Added task {len(self.task_queue)}: {text}")

    def cmd_remove_task(self, args: list[str]) -> None:
        if not self.task_queue:
            self.show_status("Task queue is empty")
            return
        if not args:
            remove_idx = self.task_index
        else:
            try:
                remove_idx = int(args[0]) - 1
            except ValueError:
                self.show_status("Usage: remove-task [1-based-index]")
                return
        if remove_idx < 0 or remove_idx >= len(self.task_queue):
            self.show_status("remove-task index out of range")
            return
        removed = self.task_queue.pop(remove_idx)
        if self.task_queue:
            if remove_idx < self.task_index:
                self.task_index -= 1
            elif self.task_index >= len(self.task_queue):
                self.task_index = len(self.task_queue) - 1
        else:
            self.task_index = 0
        self.sync_task_text()
        self.show_status(f"Removed task: {removed}")

    def cmd_set_task(self, args: list[str]) -> None:
        if not args:
            self.show_status("Usage: set-task <1-based-index>")
            return
        try:
            idx = int(args[0]) - 1
        except ValueError:
            self.show_status("Usage: set-task <1-based-index>")
            return
        if idx < 0 or idx >= len(self.task_queue):
            self.show_status("set-task index out of range")
            return
        self.task_index = idx
        self.sync_task_text()
        self.show_toast(f"Current task: {self.task_text.get()}")

    def cmd_list_tasks(self) -> None:
        if not self.task_queue:
            self.show_status("Tasks: (empty)")
            return
        parts = []
        for i, task in enumerate(self.task_queue):
            marker = "*" if i == self.task_index else "-"
            parts.append(f"{marker}{i + 1}:{task}")
        summary = " | ".join(parts)
        self.show_status(summary[:250])

    def cmd_set_icon(self, args: list[str]) -> None:
        key = self.anchor_for_current_dir()
        if not key:
            self.show_status("No anchor points to current directory")
            return

        if not args:
            self.open_icon_picker(key)
            return

        icon = args[0].lower()
        if icon not in ICON_LABELS:
            self.show_status(f"Unknown icon '{icon}'. Options: {', '.join(ICON_LABELS.keys())}")
            return

        self.anchors[key].icon = icon
        self.refresh_anchor_panel()
        self.show_toast(f"{key} icon -> {icon}")

    def open_icon_picker(self, key: str) -> None:
        picker = tk.Toplevel(self.root)
        picker.title(f"Pick Icon for {key}")
        picker.geometry("460x220")
        picker.transient(self.root)
        picker.grab_set()
        frame = tk.Frame(picker, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=f"Anchor {key}: {self.anchors[key].path}", anchor="w").pack(fill="x", pady=(0, 8))

        grid = tk.Frame(frame)
        grid.pack(fill="both", expand=True)

        icons = list(ICON_LABELS.keys())
        for i, icon in enumerate(icons):
            r, c = divmod(i, 4)
            btn = tk.Button(
                grid,
                text=f"{ICON_LABELS[icon]} {icon}",
                width=12,
                command=lambda ic=icon: self.pick_icon_and_close(key, ic, picker),
            )
            btn.grid(row=r, column=c, padx=4, pady=4)

    def pick_icon_and_close(self, key: str, icon: str, picker: tk.Toplevel) -> None:
        self.anchors[key].icon = icon
        self.refresh_anchor_panel()
        picker.destroy()
        self.show_toast(f"{key} icon -> {icon}")

    def cmd_name(self, args: list[str]) -> None:
        if not args:
            matches = [k for k, v in self.named_paths.items() if v == self.current_dir]
            if matches:
                self.show_status(f"Current path named: {', '.join(sorted(matches))}")
            else:
                self.show_status("Current path has no name")
            return
        label = args[0]
        self.named_paths[label] = self.current_dir
        self.show_toast(f"Named: {label}")
        self.show_status(f"Named '{label}' -> {self.current_dir}")

    def cmd_go(self, args: list[str]) -> None:
        if not args:
            names = ", ".join(sorted(self.named_paths)) or "(none)"
            self.show_status(f"Named paths: {names}")
            return
        label = args[0]
        path = self.named_paths.get(label)
        if path is None:
            self.show_status(f"No named path '{label}'")
            return
        self.refresh_dir(path)
        self.file_list.focus_set()

    def cmd_set_root(self, args: list[str]) -> None:
        path = " ".join(args).strip() if args else ""
        if not path:
            selected = filedialog.askdirectory(initialdir=self.current_dir)
            if not selected:
                return
            path = selected
        self.refresh_dir(norm(path))

    def cmd_open(self, args: list[str]) -> None:
        if not args:
            self.show_status("Usage: open <path>")
            return
        target = norm(" ".join(args))
        if os.path.isdir(target):
            self.refresh_dir(target)
            return
        if os.path.isfile(target):
            try:
                os.startfile(target)
                self.show_status(f"Opened file: {target}")
            except Exception as exc:
                self.show_status(f"Open failed: {exc}")
            return
        self.show_status(f"Path not found: {target}")

    def cmd_run(self, args: list[str]) -> None:
        if not args:
            self.show_status("Usage: run <command>")
            return
        command = " ".join(args)
        try:
            completed = subprocess.run(
                command,
                cwd=self.current_dir,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            out = (completed.stdout or "").strip()
            err = (completed.stderr or "").strip()
            if completed.returncode == 0:
                self.show_status(f"run ok: {command}")
            else:
                self.show_status(f"run exit {completed.returncode}: {command}")
            if out:
                self.show_toast(out[:120].replace("\n", " | "), ms=1300)
            if err:
                self.show_toast(err[:120].replace("\n", " | "), ms=1300)
        except subprocess.TimeoutExpired:
            self.show_status("run timed out after 30s")
        except Exception as exc:
            self.show_status(f"run failed: {exc}")

    def get_state_payload(self) -> dict:
        return state.get_state_payload(self)

    def save_state(self) -> None:
        state.save_state(self)

    def load_state(self) -> None:
        state.load_state(self)

    def on_app_close(self) -> None:
        try:
            self.save_state()
        except Exception as exc:
            self.show_status(f"State save error: {exc}")
        self.root.destroy()

    def next_task(self) -> None:
        if not self.task_queue:
            self.show_status("Task queue is empty")
            return
        self.task_index = (self.task_index + 1) % len(self.task_queue)
        self.sync_task_text()
        self.show_toast(f"Next task: {self.task_text.get()}")

    def focus_path_entry(self, _event=None) -> str:
        self.path_entry.focus_set()
        self.path_entry.selection_range(0, "end")
        return "break"

    def toggle_notes_pane(self) -> None:
        if self.notes_open:
            self.notes_frame.pack_forget()
            self.notes_open = False
            self.notes_toggle_btn.configure(text="Notes ▲")
        else:
            self.notes_frame.pack(side="bottom", fill="x")
            self.notes_open = True
            self.notes_toggle_btn.configure(text="Notes ▼")

    def open_temple_window(self, _event=None) -> None:
        ui_temple_dialog.open_temple_window(self, _event)
