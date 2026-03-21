import tkinter as tk
from tkinter import ttk


def build_ui(app) -> None:
    app.root.configure(bg="#1c1f24")

    app.focus_strip = tk.Frame(app.root, bg="#2a313b", height=34)
    app.focus_strip.pack(side="top", fill="x")
    app.focus_strip.pack_propagate(False)

    app.hierarchy_label = tk.Label(
        app.focus_strip,
        textvariable=app.hierarchy_text,
        bg="#2a313b",
        fg="#a8bacf",
        font=("Segoe UI", 9),
        anchor="w",
    )
    app.hierarchy_label.pack(side="left", padx=8)

    app.task_label = tk.Label(
        app.focus_strip,
        textvariable=app.task_text,
        bg="#2a313b",
        fg="#f4f7fb",
        font=("Segoe UI", 11, "bold"),
    )
    app.task_label.place(relx=0.5, rely=0.5, anchor="center")

    app.focus_strip.bind("<Button-1>", app.open_temple_window)
    app.hierarchy_label.bind("<Button-1>", app.open_temple_window)
    app.task_label.bind("<Button-1>", app.open_temple_window)

    body = tk.Frame(app.root, bg="#171a1f")
    body.pack(side="top", fill="both", expand=True)

    app.anchor_panel = tk.Frame(body, bg="#1e242d", width=260)
    app.anchor_panel.pack(side="left", fill="y")
    app.anchor_panel.pack_propagate(False)

    anchor_title = tk.Label(
        app.anchor_panel,
        text="Anchors (Ctrl+Key / Ctrl+Shift+Key)",
        bg="#1e242d",
        fg="#d8e3f2",
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    )
    anchor_title.pack(fill="x", padx=8, pady=(8, 4))

    app.anchor_list = tk.Listbox(
        app.anchor_panel,
        bg="#10141b",
        fg="#deebff",
        selectbackground="#355782",
        relief="flat",
        highlightthickness=0,
        activestyle="none",
        font=("Consolas", 10),
    )
    app.anchor_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
    app.anchor_list.bind("<Double-1>", app.open_selected_anchor)

    center = tk.Frame(body, bg="#171a1f")
    center.pack(side="left", fill="both", expand=True)

    toolbar = tk.Frame(center, bg="#151a21", height=36)
    toolbar.pack(fill="x")
    toolbar.pack_propagate(False)

    app.path_var = tk.StringVar(value=app.current_dir)
    path_entry = tk.Entry(
        toolbar,
        textvariable=app.path_var,
        bg="#0f1319",
        fg="#e5edf9",
        insertbackground="#e5edf9",
        relief="flat",
        font=("Consolas", 10),
    )
    path_entry.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=6)
    path_entry.bind("<Return>", lambda _: app.go_to_path())

    tk.Button(toolbar, text="Path", command=app.copy_current_path, width=6).pack(side="left", padx=(0, 4), pady=5)
    tk.Button(toolbar, text="Parent", command=app.go_parent, width=8).pack(side="left", padx=(0, 4), pady=5)
    tk.Button(toolbar, text="Browse", command=app.open_browse_here, width=8).pack(side="left", padx=(0, 4), pady=5)
    tk.Button(toolbar, text="Terminal", command=app.open_terminal_here, width=9).pack(side="left", padx=(0, 8), pady=5)

    content = tk.Frame(center, bg="#171a1f")
    content.pack(fill="both", expand=True)

    file_area = tk.Frame(content, bg="#171a1f")
    file_area.pack(side="left", fill="both", expand=True)

    app.file_list = ttk.Treeview(file_area, columns=("type", "size"), show="tree headings")
    app.file_list.heading("#0", text="Name")
    app.file_list.heading("type", text="Type")
    app.file_list.heading("size", text="Size")
    app.file_list.column("#0", width=500, anchor="w")
    app.file_list.column("type", width=100, anchor="center")
    app.file_list.column("size", width=100, anchor="e")
    app.file_list.pack(fill="both", expand=True)
    app.file_list.bind("<Double-1>", app.on_file_activate)
    app.file_list.bind("<<TreeviewSelect>>", app.on_file_select)
    app.file_list.bind("<Up>", app.on_file_list_up)
    app.file_list.bind("<Down>", app.on_file_list_down)
    app.file_list.bind("<Return>", app.on_file_activate)

    details = tk.Frame(content, bg="#121821", width=320)
    details.pack(side="right", fill="y")
    details.pack_propagate(False)

    tk.Label(
        details,
        text="Details",
        bg="#121821",
        fg="#dce9ff",
        font=("Segoe UI", 11, "bold"),
        anchor="w",
    ).pack(fill="x", padx=10, pady=(10, 8))

    app.details_name = tk.StringVar(value="Name: -")
    app.details_type = tk.StringVar(value="Type: -")
    app.details_size = tk.StringVar(value="Size: -")
    app.details_modified = tk.StringVar(value="Modified: -")
    app.details_path = tk.StringVar(value="Path: -")

    for variable in (
        app.details_name,
        app.details_type,
        app.details_size,
        app.details_modified,
        app.details_path,
    ):
        tk.Label(
            details,
            textvariable=variable,
            bg="#121821",
            fg="#b6cae8",
            font=("Consolas", 9),
            justify="left",
            anchor="w",
            wraplength=300,
        ).pack(fill="x", padx=10, pady=2)

    app.preview_label = tk.Label(
        details,
        text="Image preview",
        bg="#0b1118",
        fg="#8ba2c2",
        anchor="center",
        justify="center",
        width=38,
        height=16,
    )
    app.preview_label.pack(fill="both", expand=True, padx=10, pady=10)

    app.bottom_frame = tk.Frame(app.root, bg="#0f1319", height=130)
    app.bottom_frame.pack(side="bottom", fill="x")
    app.bottom_frame.pack_propagate(False)

    bottom_header = tk.Frame(app.bottom_frame, bg="#0f1319")
    bottom_header.pack(fill="x", pady=(4, 0))

    app.notes_toggle_btn = tk.Button(
        bottom_header,
        text="Notes ▲",
        command=app.toggle_notes_pane,
        width=9,
    )
    app.notes_toggle_btn.pack(side="right", padx=(0, 8))

    app.stack_var = tk.StringVar(value="Stack: []")
    stack_label = tk.Label(
        app.bottom_frame,
        textvariable=app.stack_var,
        bg="#0f1319",
        fg="#9fb3cc",
        font=("Consolas", 10),
        anchor="w",
    )
    stack_label.pack(fill="x", padx=10, pady=(0, 2))

    app.status_var = tk.StringVar(value="Ready")
    status_label = tk.Label(
        app.bottom_frame,
        textvariable=app.status_var,
        bg="#0f1319",
        fg="#c7d6eb",
        font=("Segoe UI", 10),
        anchor="w",
    )
    status_label.pack(fill="x", padx=10, pady=(0, 8))

    # Notes pane — initially hidden; toggle_notes_pane packs/forgets it
    app.notes_frame = tk.Frame(app.root, bg="#0d1520", height=140)
    app.notes_frame.pack_propagate(False)

    tk.Label(
        app.notes_frame,
        text="Notes",
        bg="#131c2b",
        fg="#7a9abc",
        font=("Segoe UI", 9, "bold"),
        anchor="w",
    ).pack(side="top", fill="x", ipady=3, padx=8)

    app.notes_text = tk.Text(
        app.notes_frame,
        bg="#0d1520",
        fg="#c8daf0",
        insertbackground="#c8daf0",
        relief="flat",
        font=("Consolas", 10),
        wrap="word",
        undo=True,
    )
    app.notes_text.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    app.toast = tk.Label(
        app.root,
        text="",
        bg="#26384b",
        fg="#f4f8ff",
        font=("Segoe UI", 10, "bold"),
        padx=12,
        pady=6,
    )

    app.command_overlay = tk.Frame(app.root, bg="#11161d", bd=1, relief="solid")
    app.command_entry_var = tk.StringVar()
    tk.Label(
        app.command_overlay,
        text=">",
        bg="#11161d",
        fg="#d3e5ff",
        font=("Consolas", 12, "bold"),
    ).pack(side="left", padx=(8, 3), pady=8)
    app.command_entry = tk.Entry(
        app.command_overlay,
        textvariable=app.command_entry_var,
        bg="#0b1118",
        fg="#f0f5ff",
        insertbackground="#f0f5ff",
        relief="flat",
        width=72,
        font=("Consolas", 11),
    )
    app.command_entry.pack(side="left", padx=(0, 8), pady=8)
    app.command_entry.bind("<Return>", app.run_command_bar)
    app.command_entry.bind("<Escape>", lambda _: app.hide_command_bar())

    app.overlay = tk.Toplevel(app.root)
    app.overlay.withdraw()
    app.overlay.overrideredirect(True)
    app.overlay.attributes("-topmost", True)
    app.overlay.configure(bg="#0d1218")
    app.overlay.attributes("-alpha", 0.93)

    tk.Label(
        app.overlay,
        text="Anchor Key Map (hold Ctrl)",
        bg="#0d1218",
        fg="#b5c9e5",
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).pack(fill="x", padx=10, pady=(8, 4))

    app.overlay_grid = tk.Frame(app.overlay, bg="#0d1218")
    app.overlay_grid.pack(padx=10, pady=(0, 10))
    app.overlay_labels: dict[str, tk.Label] = {}

    rows = ["QWERT", "ASDFG", "ZXCVB"]
    for r, row in enumerate(rows):
        for c, key in enumerate(row):
            lbl = tk.Label(
                app.overlay_grid,
                text=f"{key} [ ]",
                width=18,
                height=2,
                bg="#1b2735",
                fg="#dbe8f7",
                relief="flat",
                justify="left",
                anchor="w",
                font=("Consolas", 9),
                padx=7,
            )
            lbl.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            app.overlay_labels[key] = lbl
