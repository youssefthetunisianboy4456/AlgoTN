import builtins
import traceback
import tkinter as tk

from contextlib import redirect_stdout
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter
from errors import AlgoTNError


# ---------------- COLORS ----------------

BG = "#0f172a"
PANEL = "#1e293b"
EDITOR = "#111827"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"
ACCENT = "#2563eb"
RED = "#f87171"
GREEN = "#4ade80"


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
        root.title("AlgoTN Studio")
        root.geometry("1050x720")
        root.minsize(650, 450)
        root.configure(bg=BG)

        # Toolbar
        toolbar = tk.Frame(root, bg=BG, padx=16, pady=12)
        toolbar.pack(fill="x")

        tk.Label(
            toolbar,
            text="AlgoTN Studio",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 19, "bold")
        ).pack(side="left", padx=(0, 20))

        self.make_button(toolbar, "Nouveau", self.new_file)
        self.make_button(toolbar, "Ouvrir", self.open_file)
        self.make_button(toolbar, "Enregistrer", self.save_file)
        self.make_button(toolbar, "▶ Exécuter (F5)", self.run_code, True)

        # Resizable panels
        panes = tk.PanedWindow(
            root,
            orient="vertical",
            bg=BG,
            sashwidth=7,
            bd=0
        )
        panes.pack(fill="both", expand=True, padx=16, pady=8)

        # ---------------- EDITOR ----------------

        editor_panel = tk.Frame(panes, bg=PANEL)

        tk.Label(
            editor_panel,
            text="  ÉDITEUR",
            anchor="w",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
            pady=8
        ).pack(fill="x")

        editor_frame = tk.Frame(editor_panel, bg=EDITOR)
        editor_frame.pack(fill="both", expand=True)

        editor_scroll = tk.Scrollbar(editor_frame)
        editor_scroll.pack(side="right", fill="y")

        self.editor = tk.Text(
            editor_frame,
            wrap="none",
            undo=True,
            bg=EDITOR,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground="#334155",
            relief="flat",
            font=("Consolas", 13),
            padx=14,
            pady=12,
            yscrollcommand=editor_scroll.set
        )

        self.editor.pack(fill="both", expand=True)
        editor_scroll.config(command=self.editor.yview)

        self.editor.tag_configure(
            "error_line",
            background="#4c2028"
        )

        self.editor.insert(
            "1.0",
            'ECRIRE("Bonjour depuis AlgoTN !")\n'
        )

        panes.add(editor_panel, minsize=160)

        # ---------------- OUTPUT ----------------

        output_panel = tk.Frame(panes, bg=PANEL)

        tk.Label(
            output_panel,
            text="  SORTIE / ERREURS",
            anchor="w",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
            pady=8
        ).pack(fill="x")

        output_frame = tk.Frame(output_panel, bg=EDITOR)
        output_frame.pack(fill="both", expand=True)

        output_scroll = tk.Scrollbar(output_frame)
        output_scroll.pack(side="right", fill="y")

        self.output = tk.Text(
            output_frame,
            bg=EDITOR,
            fg=TEXT,
            relief="flat",
            font=("Consolas", 11),
            padx=14,
            pady=12,
            yscrollcommand=output_scroll.set
        )

        self.output.pack(fill="both", expand=True)
        output_scroll.config(command=self.output.yview)

        self.output.tag_configure("error", foreground=RED)
        self.output.tag_configure("success", foreground=GREEN)

        panes.add(output_panel, minsize=110)

        # ---------------- STATUS BAR ----------------

        self.status = tk.Label(
            root,
            text="Prêt",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
            anchor="w",
            padx=16,
            pady=7
        )
        self.status.pack(fill="x")

        # ---------------- KEYBOARD SHORTCUTS ----------------

        root.bind("<F5>", lambda e: self.shortcut(self.run_code))
        root.bind("<Control-o>", lambda e: self.shortcut(self.open_file))
        root.bind("<Control-s>", lambda e: self.shortcut(self.save_file))
        root.bind("<Control-n>", lambda e: self.shortcut(self.new_file))

        self.editor.bind("<Tab>", self.insert_spaces)
        self.editor.bind("<KeyRelease>", self.update_cursor)

        self.editor.focus_set()

    # ---------------- BUTTONS ----------------

    def make_button(self, parent, label, action, primary=False):
        button = tk.Button(
            parent,
            text=label,
            command=action,
            bg=ACCENT if primary else PANEL,
            fg=TEXT,
            activebackground="#1d4ed8" if primary else "#334155",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10),
            padx=13,
            pady=9
        )

        button.pack(side="left", padx=(0, 8))

    def shortcut(self, action):
        action()
        return "break"

    def insert_spaces(self, event):
        self.editor.insert("insert", "    ")
        return "break"

    def update_cursor(self, event=None):
        line, column = self.editor.index("insert").split(".")
        self.status.config(
            text=f"Ligne {line}, colonne {int(column) + 1}"
        )

    # ---------------- FILE OPERATIONS ----------------

    def new_file(self):
        self.file_path = None
        self.editor.delete("1.0", "end")
        self.output.delete("1.0", "end")
        self.root.title("AlgoTN Studio — Sans titre")

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
        self.root.title(f"AlgoTN Studio — {self.file_path.name}")

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

        self.root.title(f"AlgoTN Studio — {self.file_path.name}")
        self.status.config(text="Fichier enregistré")

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
                f"{line}.end"
            )

            self.editor.see(start)
            self.editor.mark_set("insert", start)

        self.status.config(text="Erreur dans l'algorithme")

    # ---------------- EXECUTE AlgoTN ----------------

    def run_code(self):
        self.output.delete("1.0", "end")
        self.editor.tag_remove("error_line", "1.0", "end")

        code = self.editor.get("1.0", "end-1c")

        original_input = builtins.input

        self.status.config(text="Exécution en cours...")

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
                interpreter.run(tree)

            self.output.insert(
                "end",
                "\n✓ Exécution terminée.\n",
                "success"
            )

            self.status.config(text="Exécution terminée")

        except AlgoTNError as error:
            self.show_error(error)

        except Exception:
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
            self.output.see("end")


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = AlgoTNApp(root)
    root.mainloop()
