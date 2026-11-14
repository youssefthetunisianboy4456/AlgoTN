import builtins
import re
import traceback
import tkinter as tk

from bisect import bisect_right
from contextlib import redirect_stdout
from functools import lru_cache
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter
from errors import AlgoTNError
from get_tabs import process_tables


BG = "#0c121d"
BAR = "#111a28"
PANEL = "#121d2d"
EDITOR = "#101927"
RAISED = "#172538"
BORDER = "#28384d"
TEXT = "#e8f0f8"
SECONDARY = "#b5c5d7"
MUTED = "#8599b1"
ACCENT = "#68e1c6"
ACCENT_INK = "#0b2d2b"
ACCENT_SURFACE = "#193a3d"
RED = "#ff9da8"
ERROR_LINE = "#492832"
SELECTION = "#2a455e"
UI_FONT = "Segoe UI"
CODE_FONT = ("Consolas", 13)

# Pixel masks keep the toolbar icons crisp without an image dependency.
ICONS = {
    "file": (
        "  ######     ", "  #    ##    ", "  #    # #   ", "  #    ####  ",
        "  #       #  ", "  #       #  ", "  #       #  ", "  #       #  ",
        "  #       #  ", "  #       #  ", "  #       #  ", "  #########  ",
    ),
    "folder": (
        "             ", "             ", " #####       ", " #    #      ",
        " #     ##### ", " #         # ", " #         # ", " #         # ",
        " #         # ", " #         # ", " ########### ", "             ",
    ),
    "save": (
        " #########   ", " # #   #  #  ", " # #   #   # ", " # #####   # ",
        " #         # ", " #         # ", " # ####### # ", " # #     # # ",
        " # #     # # ", " # #     # # ", " ########### ", "             ",
    ),
}

SYNTAX_COLORS = {"keyword": "#c0b3ff", "string": "#a7db9d", "number": "#f5c78d"}
SYNTAX_SPANS = re.compile(
    r'(?P<string>"[^"]*(?:"|\Z))'
    r"|(?P<word>\b(?:tant que|jusqu'[aà])\b|[^\W\d]\w*|@)"
    r"|(?P<number>\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


@lru_cache(maxsize=512)
def is_keyword(word):
    name = word.upper()
    if name in {"ECRIRE", "LIRE"} or name.startswith("LIRE_"):
        return True
    try:
        token_type = tokenize(word)[0][0]
    except (AlgoTNError, ValueError):
        return False
    return token_type in {"KEYWORD", "TYPE", "LOGIC", "BOOLEAN", "MOD", "DIV"}


# ----------------------------------------------------------------------
# TYPE OPTIONS START: each key is shown in the dropdown.
# Each value is passed to process_tables when the row is saved.
TABLE_TYPE_VALUES = {
    "CHAINE": "CHAINE",
    "ENTIER": "ENTIER",
    "BOOLEAN": "BOOLEAN",
    "REEL": "REEL",
    "CARACTERE": "CARACTERE",
}
# ----------------------------------------------------------------------
# TYPE OPTIONS END: edit the keys to change the labels users see.
# Edit the values to change the declarations sent to AlgoTN.


def configure_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    for name, fill, foreground, border, hover, pressed in (
        ("Toolbar", BAR, SECONDARY, BAR, RAISED, BORDER),
        ("Run", ACCENT, ACCENT_INK, ACCENT, "#8defda", "#4dc9af"),
        ("Outline", PANEL, TEXT, BORDER, RAISED, BORDER),
        ("Save", ACCENT_SURFACE, ACCENT, "#285654", "#214b4c", "#285654"),
    ):
        button = f"{name}.TButton"
        style.configure(
            button, background=fill, foreground=foreground, bordercolor=border,
            lightcolor=fill, darkcolor=fill, focuscolor=foreground,
            font=(UI_FONT, 10, "bold"), padding=(11, 7), relief="solid", anchor="center", width=0,
        )
        style.map(button, **{
            option: [("pressed", pressed), ("active", hover)]
            for option in ("background", "lightcolor", "darkcolor")
        })
    style.configure("Delete.Outline.TButton", padding=(6, 4))

    style.configure(
        "Studio.TNotebook", background=PANEL, bordercolor=PANEL, lightcolor=PANEL,
        darkcolor=PANEL, tabmargins=(0, 0, 0, 8),
    )
    style.configure(
        "Studio.TNotebook.Tab", background=EDITOR, foreground=SECONDARY,
        padding=(11, 5), font=(UI_FONT, 10), focuscolor=ACCENT,
    )
    tab_surfaces = [("selected", ACCENT_SURFACE), ("active", RAISED), ("!selected", EDITOR)]
    style.map(
        "Studio.TNotebook.Tab",
        **{option: tab_surfaces for option in ("background", "bordercolor", "lightcolor", "darkcolor")},
        foreground=[("selected", ACCENT)], expand=[("selected", (0, 0, 0, 0))],
        padding=[("selected", (11, 5))],
    )
    style.configure(
        "Studio.TEntry", fieldbackground=EDITOR, foreground=TEXT, insertcolor=ACCENT,
        bordercolor=BORDER, lightcolor=EDITOR, darkcolor=EDITOR, padding=(7, 5),
        selectbackground=SELECTION, selectforeground=TEXT,
    )
    style.map("Studio.TEntry", **{option: [("focus", ACCENT)] for option in ("bordercolor", "lightcolor", "darkcolor")})
    style.configure(
        "Studio.TCombobox", fieldbackground=EDITOR, foreground=TEXT, background=RAISED,
        bordercolor=BORDER, lightcolor=EDITOR, darkcolor=EDITOR, arrowcolor=SECONDARY,
        padding=(7, 5), selectbackground=SELECTION, selectforeground=TEXT,
    )
    style.map("Studio.TCombobox", fieldbackground=[("readonly", EDITOR)])
    root.option_add("*TCombobox*Listbox.background", EDITOR)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", SELECTION)
    root.option_add("*TCombobox*Listbox.selectForeground", TEXT)

    for orientation, sticky in (("Vertical", "ns"), ("Horizontal", "ew")):
        scrollbar = f"Studio.{orientation}.TScrollbar"
        prefix = f"{orientation}.Scrollbar"
        style.layout(scrollbar, [(f"{prefix}.trough", {
            "sticky": "nswe", "children": [(f"{prefix}.thumb", {"expand": True, "sticky": sticky})],
        })])
        style.configure(
            scrollbar, background=BORDER, troughcolor=EDITOR, bordercolor=EDITOR,
            lightcolor=BORDER, darkcolor=BORDER, gripcount=0, arrowsize=8,
        )
        thumb = [("disabled", EDITOR), ("pressed", "#425875"), ("active", "#425875")]
        style.map(scrollbar, **{option: thumb for option in ("background", "lightcolor", "darkcolor")})


def set_scrollbar(scrollbar, first, last):
    scrollbar.set(first, last)
    scrollbar.state(("disabled" if float(first) == 0 and float(last) == 1 else "!disabled",))


# ---------------- OUTPUT REDIRECTION ----------------

class OutputWriter:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        if text:
            self.widget.insert("end", text)
            self.widget.see("end")

    def flush(self):
        pass


# ---------------- MAIN APPLICATION ----------------

class AlgoTNApp:
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.tables = {}
        self.contained_by_name = {}
        self.icons = {}
        self.highlight_job = None
        self.gutter_job = None
        self.cursor_line = None
        root.title("AlgoTN Studio")
        width = min(1180, root.winfo_screenwidth() - 48)
        height = min(690, root.winfo_screenheight() - 96)
        root.geometry(f"{width}x{height}")
        root.minsize(720, 465)
        root.configure(bg=BG)
        configure_styles(root)

        self.build_toolbar()
        self.build_status_bar()
        workspace = tk.PanedWindow(root, orient="horizontal", bg=BG, sashwidth=12, bd=0)
        workspace.pack(fill="both", expand=True, padx=16, pady=14)
        panes = tk.PanedWindow(workspace, orient="vertical", bg=BG, sashwidth=12, bd=0)
        workspace.add(panes, minsize=320, stretch="always")

        editor_panel = self.build_editor(panes)
        output_panel = self.build_console(panes)
        panes.add(editor_panel, height=390, minsize=155, stretch="always")
        panes.add(output_panel, height=176, minsize=100, stretch="never")

        table_panel = self.panel(workspace)
        workspace.add(table_panel, width=362, minsize=308, stretch="never")
        self.build_table(table_panel)

        root.bind("<F5>", lambda e: self.shortcut(self.run_code))
        root.bind("<Control-o>", lambda e: self.shortcut(self.open_file))
        root.bind("<Control-s>", lambda e: self.shortcut(self.save_file))
        root.bind("<Control-n>", lambda e: self.shortcut(self.new_file))

        self.editor.insert("1.0", 'ECRIRE("Bonjour depuis AlgoTN !")\n')
        self.editor.mark_set("insert", "1.0")
        self.editor.focus_set()

    def build_toolbar(self):
        toolbar = tk.Frame(self.root, bg=BAR, padx=16, pady=11)
        toolbar.pack(fill="x")
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        logo = tk.Label(toolbar, text="‹/›", bg=ACCENT_SURFACE, fg=ACCENT, font=("Consolas", 13, "bold"))
        logo.pack(side="left", ipadx=5, ipady=3, padx=(0, 10))
        tk.Label(toolbar, text="AlgoTN Studio", bg=BAR, fg=TEXT, font=(UI_FONT, 16, "bold")).pack(side="left")
        tk.Frame(toolbar, bg=BORDER, width=1, height=25).pack(side="left", padx=13)

        for label, action, icon in (
            ("Nouveau", self.new_file, "file"), ("Ouvrir", self.open_file, "folder"),
            ("Enregistrer", self.save_file, "save"),
        ):
            self.make_button(toolbar, label, action, "Toolbar", icon).pack(side="left", padx=(0, 3))
        self.make_button(toolbar, "▶   Exécuter    F5", self.run_code, "Run").pack(side="right", ipadx=6)

    def build_status_bar(self):
        bar = tk.Frame(self.root, bg=BG, padx=16, pady=5)
        bar.pack(side="bottom", fill="x")
        tk.Frame(self.root, bg=BORDER, height=1).pack(side="bottom", fill="x")
        self.status_dot = tk.Label(bar, text="●", bg=BG, fg=ACCENT, font=(UI_FONT, 8))
        self.status_dot.pack(side="left", padx=(0, 5))
        self.status = tk.Label(bar, bg=BG, fg=SECONDARY, font=(UI_FONT, 9))
        self.status.pack(side="left")
        self.set_status("Prêt")
        for text in ("AlgoTN", "UTF-8"):
            tk.Label(bar, text=text, bg=BG, fg=MUTED, font=(UI_FONT, 9)).pack(side="right", padx=(15, 0))
        self.cursor = tk.Label(bar, text="Ligne 1, col. 1", bg=BG, fg=SECONDARY, font=(UI_FONT, 9))
        self.cursor.pack(side="right")

    def set_status(self, text, color=ACCENT):
        self.status.config(text=text)
        self.status_dot.config(fg=color)

    def panel(self, parent):
        return tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground=BORDER, highlightcolor=BORDER)

    def panel_header(self, panel):
        header = tk.Frame(panel, bg=PANEL, padx=13)
        header.pack(fill="x")
        tk.Frame(panel, bg=BORDER, height=1).pack(fill="x")
        return header

    def build_editor(self, parent):
        panel = self.panel(parent)
        header = self.panel_header(panel)
        tk.Label(header, text="Éditeur", bg=PANEL, fg=MUTED, font=(UI_FONT, 10)).pack(side="right")
        file_tab = tk.Frame(header, bg=RAISED)
        file_tab.pack(side="left", pady=(6, 0))
        self.file_label = tk.Label(
            file_tab, text=" Sans titre", bg=RAISED, fg=TEXT, font=(UI_FONT, 10, "bold"),
            image=self.icon("file", ACCENT), compound="left",
        )
        self.file_label.pack(padx=12, pady=6)
        tk.Frame(file_tab, bg=ACCENT, height=2).pack(fill="x")

        body = tk.Frame(panel, bg=EDITOR)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        self.gutter = tk.Canvas(body, width=46, bg=EDITOR, highlightthickness=0)
        self.gutter.grid(row=0, column=0, sticky="ns")

        self.editor = tk.Text(
            body, wrap="none", undo=True, width=1, height=1, bg=EDITOR, fg=TEXT,
            insertbackground=ACCENT, selectbackground=SELECTION, selectforeground=TEXT,
            relief="flat", borderwidth=0, highlightthickness=0, font=CODE_FONT,
            padx=0, pady=10, spacing1=2, spacing3=2,
        )
        self.editor.grid(row=0, column=1, sticky="nsew")
        vertical = ttk.Scrollbar(body, style="Studio.Vertical.TScrollbar", command=self.editor.yview)
        vertical.grid(row=0, column=2, sticky="ns")
        horizontal = ttk.Scrollbar(
            body, orient="horizontal", style="Studio.Horizontal.TScrollbar", command=self.editor.xview,
        )
        horizontal.grid(row=1, column=1, sticky="ew")

        def scroll_changed(first, last):
            set_scrollbar(vertical, first, last)
            self.queue_gutter()

        self.editor.config(
            yscrollcommand=scroll_changed, xscrollcommand=lambda *bounds: set_scrollbar(horizontal, *bounds),
        )
        self.editor.tag_configure("current_line", background=RAISED)
        self.editor.tag_configure("error_line", background=ERROR_LINE)
        for tag, color in SYNTAX_COLORS.items():
            self.editor.tag_configure(tag, foreground=color)
        self.editor.tag_raise("sel")

        self.editor.bind("<<Modified>>", self.editor_modified)
        self.editor.bind("<Tab>", self.insert_spaces)
        for event in ("<KeyRelease>", "<ButtonRelease-1>", "<Configure>"):
            self.editor.bind(event, self.queue_gutter, add=True)
        self.gutter.bind("<MouseWheel>", lambda event: self.scroll_wheel(self.editor, event))
        return panel

    def build_console(self, parent):
        panel = self.panel(parent)
        header = self.panel_header(panel)
        tk.Label(header, text="›_", bg=PANEL, fg=MUTED, font=("Consolas", 13, "bold")).pack(side="left")
        tk.Label(header, text="Console", bg=PANEL, fg=TEXT, font=(UI_FONT, 10, "bold")).pack(
            side="left", padx=(8, 0), pady=8,
        )
        body = tk.Frame(panel, bg=EDITOR)
        body.pack(fill="both", expand=True)
        self.output = tk.Text(
            body, width=1, height=1, bg=EDITOR, fg=SECONDARY, relief="flat", borderwidth=0,
            highlightthickness=0, font=("Consolas", 11), padx=14, pady=9,
            selectbackground=SELECTION, selectforeground=TEXT, insertbackground=ACCENT,
        )
        scrollbar = ttk.Scrollbar(body, style="Studio.Vertical.TScrollbar", command=self.output.yview)
        scrollbar.pack(side="right", fill="y")
        self.output.pack(fill="both", expand=True)
        self.output.config(yscrollcommand=lambda *bounds: set_scrollbar(scrollbar, *bounds))
        self.output.tag_configure("error", foreground=RED)
        self.output.tag_configure("success", foreground=ACCENT)
        return panel

    def editor_modified(self, event):
        if not self.editor.edit_modified():
            return
        self.editor.edit_modified(False)
        self.cursor_line = None
        if self.highlight_job is not None:
            self.root.after_cancel(self.highlight_job)
        self.highlight_job = self.root.after(75, self.highlight_syntax)
        self.queue_gutter()

    def highlight_syntax(self):
        self.highlight_job = None
        source = self.editor.get("1.0", "end-1c")
        line_starts = [0, *(newline.end() for newline in re.finditer("\n", source))]

        def text_index(offset):
            line = bisect_right(line_starts, offset) - 1
            return f"{line + 1}.0 + {offset - line_starts[line]} chars"

        spans = {tag: [] for tag in SYNTAX_COLORS}
        for match in SYNTAX_SPANS.finditer(source):
            tag = match.lastgroup
            if tag == "word":
                if not is_keyword(match.group()):
                    continue
                tag = "keyword"
            start, end = match.span()
            spans[tag].extend((text_index(start), text_index(end)))

        for tag, indices in spans.items():
            self.editor.tag_remove(tag, "1.0", "end")
            if indices:
                self.editor.tag_add(tag, *indices)

    def queue_gutter(self, event=None):
        if self.gutter_job is None:
            self.gutter_job = self.root.after_idle(self.redraw_gutter)

    def redraw_gutter(self):
        self.gutter_job = None
        line = self.editor.index("insert").split(".")[0]
        column = len(self.editor.get(f"{line}.0", "insert")) + 1
        self.cursor.config(text=f"Ligne {line}, col. {column}")
        if self.cursor_line != line:
            self.editor.tag_remove("current_line", "1.0", "end")
            self.editor.tag_add("current_line", f"{line}.0", f"{line}.0 lineend + 1c")
            self.cursor_line = line

        gutter = self.gutter
        gutter.delete("all")
        digits = len(self.editor.index("end-1c").split(".")[0])
        width = max(56, 28 + digits * 10)
        if int(gutter.cget("width")) != width:
            gutter.config(width=width)
        index = self.editor.index("@0,0 linestart")
        while (layout := self.editor.dlineinfo(index)) is not None:
            _, y, _, height, baseline = layout
            number = index.split(".")[0]
            if number == line:
                gutter.create_rectangle(0, y, width, y + height, fill=RAISED, outline="")
            gutter.create_text(
                width - 20, y + baseline - 1, text=number, anchor="se",
                font=("Consolas", 10), fill=TEXT if number == line else MUTED,
            )
            index = self.editor.index(f"{index} + 1 line")
            if self.editor.compare(index, ">=", "end"):
                break
        gutter.create_line(width - 11, 0, width - 11, gutter.winfo_height(), fill=BORDER)

    def build_table(self, panel):
        header = self.panel_header(panel)
        tk.Label(header, text="▦", bg=PANEL, fg=ACCENT, font=(UI_FONT, 13)).pack(side="left")
        tk.Label(header, text="Tableaux", bg=PANEL, fg=TEXT, font=(UI_FONT, 12, "bold")).pack(
            side="left", padx=(7, 0), pady=10,
        )
        self.table_tabs = ttk.Notebook(panel, style="Studio.TNotebook")
        self.table_tabs.pack(fill="both", expand=True, padx=12, pady=10)
        self.table_tabs.enable_traversal()
        self.create_table_tab("TDOG", self.contained_by_name)
        self.named_types_tab = self.create_table_tab("TDNT", allow_tdol=False)

    def create_table_tab(self, title, values=None, *, allow_tdol=True):
        tab = tk.Frame(self.table_tabs, bg=PANEL)
        self.table_tabs.add(tab, text=title)
        table_data = {
            "rows": [],
            "values": values if values is not None else {},
            "allow_tdol": allow_tdol,
        }
        self.tables[tab] = table_data

        buttons = tk.Frame(tab, bg=PANEL)
        buttons.pack(side="bottom", fill="x", pady=(10, 0))
        self.make_button(buttons, "+  Ajouter une ligne", lambda: self.add_table_row(tab), "Outline").pack(side="left")
        self.make_button(buttons, "Enregistrer", lambda: self.save_table(tab), "Save", "save").pack(side="right")
        tk.Frame(tab, bg=BORDER, height=1).pack(side="bottom", fill="x", pady=(6, 0))

        body = tk.Frame(tab, bg=PANEL, highlightthickness=1, highlightbackground=BORDER, highlightcolor=BORDER)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)
        canvas = tk.Canvas(body, bg=PANEL, highlightthickness=0, width=1, height=1, yscrollincrement=32)
        scrollbar = ttk.Scrollbar(body, style="Studio.Vertical.TScrollbar", command=canvas.yview)
        scrollbar.grid(row=0, column=1, rowspan=2, sticky="ns")
        canvas.grid(row=1, column=0, sticky="nsew")
        canvas.config(yscrollcommand=lambda *bounds: set_scrollbar(scrollbar, *bounds))

        table = tk.Frame(canvas, bg=PANEL)
        table_data["canvas"] = canvas
        table_data["frame"] = table
        window = canvas.create_window((0, 0), window=table, anchor="nw")
        table.bind(
            "<Configure>",
            lambda event: canvas.config(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(window, width=event.width)
        )

        headings = tk.Frame(body, bg=RAISED)
        headings.grid(row=0, column=0, sticky="ew")
        table.columnconfigure(2, minsize=36)
        headings.columnconfigure(2, minsize=36)
        for column, heading in enumerate(("Object", "T/N")):
            table.columnconfigure(column, weight=1, uniform="table")
            headings.columnconfigure(column, weight=1, uniform="table")
            tk.Label(headings, text=heading, bg=RAISED, fg=SECONDARY, font=(UI_FONT, 9, "bold")).grid(
                row=0, column=column, sticky="w", padx=12, pady=6,
            )
        for widget in (canvas, table, headings):
            widget.bind("<MouseWheel>", lambda event: self.scroll_wheel(canvas, event))

        self.add_table_row(tab, focus=False)
        return tab

    def add_table_row(self, tab, focus=True):
        table_data = self.tables[tab]
        # A deleted row can leave an unused grid index before the last row.
        row_number = table_data["frame"].grid_size()[1]
        frame = table_data["frame"]
        name = ttk.Entry(frame, width=1, style="Studio.TEntry", font=("Consolas", 10))
        if table_data["allow_tdol"]:
            contained = ttk.Combobox(
                frame, width=1, style="Studio.TCombobox", font=(UI_FONT, 10),
                state="readonly", values=("", *TABLE_TYPE_VALUES, "PROCEDURE", "FONCTION"),
            )
            contained.configure(postcommand=lambda: self.refresh_type_choices(contained))
            contained.bind("<<ComboboxSelected>>", lambda event: self.save_table(tab, automatic=True))
        else:
            contained = ttk.Entry(frame, width=1, style="Studio.TEntry", font=(UI_FONT, 10))

        entries = (name, contained)
        for column, entry in enumerate(entries):
            entry.grid(row=row_number, column=column, sticky="ew", padx=5, pady=4)

        row = {"name": name, "contained": contained, "child": None}
        row["delete"] = self.make_button(
            table_data["frame"], "×", lambda: self.delete_table_row(tab, row), "Delete.Outline"
        )
        row["delete"].grid(row=row_number, column=2, padx=4, pady=4)
        table_data["rows"].append(row)
        for entry in entries:
            entry.bind("<FocusOut>", lambda event: self.save_table(tab, automatic=True))
            entry.bind("<Return>", lambda event: self.save_table(tab, automatic=True))
            entry.bind("<MouseWheel>", lambda event: self.scroll_wheel(table_data["canvas"], event))

        if focus:
            entries[0].focus_set()
            table_data["frame"].update_idletasks()
            table_data["canvas"].yview_moveto(1)

    def refresh_type_choices(self, dropdown):
        named_types = (
            row["name"].get().strip()
            for row in self.tables[self.named_types_tab]["rows"]
        )
        choices = dict.fromkeys(("", *TABLE_TYPE_VALUES, "PROCEDURE", "FONCTION", *named_types))
        dropdown.configure(values=tuple(choices))

    def delete_table_row(self, tab, row):
        self.tables[tab]["rows"].remove(row)
        for widget in (row["name"], row["contained"], row["delete"]):
            widget.destroy()
        if row["child"] is not None:
            self.delete_local_table(row["child"])
        self.save_table(tab, automatic=True)

    def delete_local_table(self, tab):
        for row in self.tables.pop(tab)["rows"]:
            if row["child"] is not None:
                self.delete_local_table(row["child"])
        tab.destroy()

    def check_table_row(self, tab, row):
        if not self.tables[tab]["allow_tdol"]:
            return
        name = row["name"].get().strip()
        contained = row["contained"].get().strip().lower()
        if name and contained in ("procédure", "procedure", "fonction"):
            if row["child"] is None:
                row["child"] = self.create_table_tab(f"TDOL de {name}")
            else:
                self.table_tabs.tab(row["child"], text=f"TDOL de {name}")

    def save_table(self, tab, *, automatic=False):
        table_data = self.tables[tab]
        updated = {}

        for row_number, row in enumerate(table_data["rows"], start=1):
            name = row["name"].get().strip()
            contained = row["contained"].get().strip()

            if not name and not contained:
                continue
            if not name:
                if not automatic:
                    messagebox.showerror(
                        "Objet manquant", f"Entrez un objet à la ligne {row_number}.",
                        parent=self.root
                    )
                return False
            if name in updated:
                if not automatic:
                    messagebox.showerror(
                        "Objet en double", f'L’objet "{name}" apparaît plusieurs fois.',
                        parent=self.root
                    )
                return False
            if table_data["allow_tdol"]:
                contained = TABLE_TYPE_VALUES.get(contained, contained)
            updated[name] = contained

        table_data["values"].clear()
        table_data["values"].update(updated)
        for row in table_data["rows"]:
            self.check_table_row(tab, row)
        if not automatic:
            self.set_status(f"Tableau enregistré ({len(updated)})")
        return True

    def get_tables(self):
        # Saving can create a new, empty TDOL tab. Include it in the result below.
        for tab in list(self.tables):
            if not self.save_table(tab):
                self.table_tabs.select(tab)
                return None
        return [
            {
                "name": self.table_tabs.tab(tab, "text"),
                "data": table_data["values"].copy(),
            }
            for tab, table_data in self.tables.items()
        ]

    # ---------------- BUTTONS ----------------

    def icon(self, name, color):
        key = (name, color)
        if key not in self.icons:
            pixels = ICONS[name]
            image = tk.PhotoImage(master=self.root, width=len(pixels[0]), height=len(pixels))
            for y, row in enumerate(pixels):
                for x, pixel in enumerate(row):
                    if pixel == "#":
                        image.put(color, to=(x, y))
            self.icons[key] = image
        return self.icons[key]

    def make_button(self, parent, label, action, style, icon=None):
        button = ttk.Button(parent, text=label, command=action, style=f"{style}.TButton", cursor="hand2")
        if icon:
            color = ACCENT if style == "Save" else SECONDARY
            button.config(text=f" {label}", image=self.icon(icon, color), compound="left")
        return button

    def scroll_wheel(self, widget, event):
        widget.yview_scroll(-int(event.delta / 120), "units")
        return "break"

    def shortcut(self, action):
        action()
        return "break"

    def insert_spaces(self, event):
        self.editor.insert("insert", "    ")
        return "break"

    # ---------------- FILE OPERATIONS ----------------

    def update_file_label(self):
        name = self.file_path.name if self.file_path else "Sans titre"
        self.root.title(f"AlgoTN Studio — {name}")
        display_name = f"{name[:19]}…{name[-8:]}" if len(name) > 28 else name
        self.file_label.config(text=f" {display_name}")

    def new_file(self):
        self.file_path = None
        self.editor.delete("1.0", "end")
        self.output.delete("1.0", "end")
        self.update_file_label()
        self.set_status("Nouveau fichier")
        self.queue_gutter()

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Ouvrir un algorithme",
            filetypes=[
                ("Algorithmes", "*.mini *.txt"),
                ("Tous les fichiers", "*.*")
            ]
        )

        if not path:
            return

        try:
            code = Path(path).read_text(encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Erreur", str(error))
            return

        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", code)

        self.file_path = Path(path)
        self.update_file_label()
        self.set_status("Fichier ouvert")

    def save_file(self):
        if self.file_path is None:
            path = filedialog.asksaveasfilename(
                title="Enregistrer l'algorithme",
                defaultextension=".mini",
                filetypes=[
                    ("AlgoTN", "*.mini"),
                    ("Fichier texte", "*.txt")
                ]
            )

            if not path:
                return

            self.file_path = Path(path)

        try:
            self.file_path.write_text(
                self.editor.get("1.0", "end-1c"),
                encoding="utf-8"
            )
        except OSError as error:
            messagebox.showerror("Erreur", str(error))
            return

        self.update_file_label()
        self.set_status("Fichier enregistré")

    # ---------------- USER INPUT ----------------

    def ask_input(self, prompt=""):
        value = simpledialog.askstring(
            "AlgoTN — LIRE",
            prompt or "Entrez une valeur :",
            parent=self.root
        )

        if value is None:
            raise AlgoTNError("Saisie annulée")

        return value

    # ---------------- ERROR DISPLAY ----------------

    def show_error(self, error):
        self.output.insert(
            "end",
            f"ERREUR : {error}\n",
            "error"
        )

        if error.line is not None:
            line = int(error.line)
            start = f"{line}.0"

            self.editor.tag_add(
                "error_line",
                start,
                f"{line}.end + 1c"
            )

            self.editor.see(start)
            self.editor.mark_set("insert", start)
            self.queue_gutter()

        self.set_status("Erreur dans l'algorithme", RED)

    # ---------------- EXECUTE AlgoTN ----------------

    def run_code(self):
        tables = self.get_tables()
        if tables is None:
            return

        self.output.delete("1.0", "end")
        self.editor.tag_remove("error_line", "1.0", "end")

        code = self.editor.get("1.0", "end-1c")

        original_input = builtins.input

        self.set_status("Exécution en cours…")
        self.root.update_idletasks()

        try:
            # Lexer
            tokens = tokenize(code)

            # Parser
            parser = Parser(tokens)
            tree = parser.parse()

            # Interpreter
            interpreter = Interpreter()
            interpreter.node_lines = parser.node_lines

            # Redirect input to popup dialogs
            builtins.input = self.ask_input

            # Redirect print() to the output panel
            with redirect_stdout(OutputWriter(self.output)):
                process_tables(tables)
                interpreter.run(tree)

            self.output.insert(
                "end",
                "\n✓ Exécution terminée.\n",
                "success"
            )

            self.set_status("Exécution terminée")

        except AlgoTNError as error:
            self.show_error(error)

        except Exception:
            self.set_status("Erreur interne", RED)
            self.output.insert(
                "end",
                "ERREUR INTERNE :\n",
                "error"
            )

            self.output.insert(
                "end",
                traceback.format_exc(),
                "error"
            )

        finally:
            builtins.input = original_input
            self.output.see("end-2c")


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = AlgoTNApp(root)
    root.mainloop()