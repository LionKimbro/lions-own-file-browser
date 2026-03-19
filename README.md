# Focus Explorer

A keyboard-first file explorer with:

- Top focus strip (hierarchy + immediate task)
- Click focus strip to open "Temple of Focus"
- Anchor map with visual overlay while Ctrl is held
- Explicit directory stack (`push`/`pop` only)
- Command bar for icon/task/state commands
- Right-side detail pane with file metadata and image preview
- `lionscliapp` project-dir persistence in `.focus-explorer/state.json`

## Project Layout

- `src/focus_explorer/`: package code (main app now lives in `focus_explorer.py`)
- `docs/conversations/`: conversation tracking notes
- `docs/spec/`: project specs
- `pyproject.toml`: package metadata + CLI entry point

## Run (Recommended)

```powershell
pip install -e .
focus-explorer
```

Run without installing an entry point:

```powershell
python -m focus_explorer
```

Show `lionscliapp` help and built-ins:

```powershell
focus-explorer help
focus-explorer keys
focus-explorer set path.start_dir F:\projects\snap-and-paste
```

## Keybindings

- `Ctrl+Shift+<Q/W/E/R/T/A/S/D/F/G/Z/X/C/V/B>`: toggle anchor for current directory on that key
- `Ctrl+<Q/W/E/R/T/A/S/D/F/G/Z/X/C/V/B>`: jump to anchor
- `Ctrl` (hold): show anchor key map overlay
- `Ctrl+Enter`: push current directory to stack
- `Ctrl+Backspace`: pop directory from stack and jump
- `Ctrl+Left`: history back
- `Ctrl+Right`: history forward
- `Ctrl+Up`: parent directory
- `Up` / `Down` (in file list): move selection in middle pane
- `Enter` (in file list): open selected file / enter selected directory
- `Ctrl+N`: create new task
- `Ctrl+Space`: command bar

## Command Bar

- `set-icon <icon>`: set icon on anchor that points to current directory
- `set-icon`: open icon picker for current anchor
- `set-focus <text...>`: set immediate task
- `add-task <text...>`: append a task to queue
- `remove-task [index]`: remove task by 1-based index (or current task)
- `set-task <index>`: set active task by 1-based index
- `list-tasks`: show compact task summary in status bar
- `set-hierarchy <text...>`: set hierarchy text
- `next-task`: load next task (auto-advance behavior)
- `set-root [path]`: jump to path (or pick via dialog)
- `open <path>`: open file or directory
- `run <command...>`: run shell command in current directory
- `save`: save state to `state.json` in project dir

## Notes

The app prioritizes deterministic navigation behavior:

- Anchor jumps do **not** modify the directory stack.
- Only explicit push/pop changes stack state.
- State auto-loads at startup and auto-saves on exit.
- Tasks can be edited in the Temple window with `Add`, `Set Current`, `Update`, `Remove`, `Move Up`, and `Move Down`.
