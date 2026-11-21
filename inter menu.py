from get_tabs import process_tables
from functools import lru_cache
from contextlib import redirect_stdout
from pathlib import Path
from lexer import tokenize
from parser import Parser
from interpreter import Interpreter
from errors import AlgoTNError
from get_tabs import process_tables
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, QButtonGroup, QFileDialog,QHeaderView,QAction,QMenu,QToolButton,
    QMessageBox, QTableWidgetItem, QComboBox,QInputDialog,QSizePolicy
)
from PyQt5.QtCore import QObject, QEvent, QEventLoop, Qt
from PyQt5.QtGui import QTextCursor,QKeySequence
from PyQt5.QtCore import Qt
import sys
import io
app=QApplication(sys.argv)
window=uic.loadUi("interface.ui")
window.tdoTab_3.setLayout(window.verticalLayout_10)

window.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
window.verticalLayout_10.setSpacing(7)

window.tdoTable_3.setSizePolicy(
    QSizePolicy.Expanding,
    QSizePolicy.Expanding
)

menu_symboles = QMenu(window)

operateurs = [
    ("∈", "Appartient à", "Ctrl+E"),
    ("≠", "Différent", "Ctrl+="),
    ("≥", "Supérieur ou égal", "Ctrl+Shift+<"),
    ("≤", "Inférieur ou égal", "Ctrl+<"),
    ("←", "Affectation", 'Ctrl+"')
]

def inserer_symbole(symbole):
    cursor = window.CodeEditor.textCursor()
    cursor.insertText(symbole)
    window.CodeEditor.setTextCursor(cursor)
    window.CodeEditor.setFocus()


for symbole, description, raccourci in operateurs:

    action = QAction(symbole,window)

    action.setShortcut(QKeySequence(raccourci))
    action.setShortcutContext(Qt.WindowShortcut)

    action.triggered.connect(
        lambda checked=False, s=symbole: inserer_symbole(s)
    )

    window.addAction(action)
    menu_symboles.addAction(action)



bouton_inserer = QToolButton(window)
bouton_inserer.setText("Insérer")
bouton_inserer.setMenu(menu_symboles)
bouton_inserer.setPopupMode(QToolButton.InstantPopup)

window.MaintoolBar.insertWidget(
    window.actionEx_cuter,
    bouton_inserer
)
header = window.tdoTable_3.horizontalHeader()
header.setSectionResizeMode(QHeaderView.Stretch)
window.setMinimumSize(800, 600)
window.resize(1100, 750)
test=uic.loadUi("dialog.ui")
test.show()
groupe = QButtonGroup(test)
groupe.addButton(test.check2eme)
groupe.addButton(test.check3eme4eme)
groupe.setExclusive(True)



def new_file():
    global current_file

    window.CodeEditor.clear()
    window.ConsoleOutput.clear()

    current_file = None

    window.setWindowTitle("AlgoTN Studio - Sans titre")
    
def open_file():

    global current_file

    path, _ = QFileDialog.getOpenFileName(
        window,
        "Ouvrir un algorithme",
        "",
        "AlgoTN (*.mini *.txt);;Tous les fichiers (*.*)"
    )

    if not path:
        return

    try:
        with open(path, "r", encoding="utf-8") as file:
            code = file.read()

        window.codeEditor.setPlainText(code)

        current_file = Path(path)

        window.setWindowTitle(f"AlgoTN Studio - {current_file.name}")

    except OSError as error:
        QMessageBox.critical(window, "Erreur", str(error))
        
def save_file():

    global current_file

    if current_file is None:

        path, _ = QFileDialog.getSaveFileName(
            window,
            "Enregistrer l'algorithme",
            "",
            "AlgoTN (*.mini);;Fichier texte (*.txt)"
        )

        if not path:
            return

        current_file = Path(path)

    try:
        code = window.codeEditor.toPlainText()

        current_file.write_text(code, encoding="utf-8")

        window.setWindowTitle(f"AlgoTN Studio - {current_file.name}")

    except OSError as error:
        QMessageBox.critical(window, "Erreur", str(error))

def get_tdo_data():
    variables = {}

    for row in range(window.tdoTable_3.rowCount()):
        name_item = window.tdoTable_3.item(row, 0)

        if name_item is None:
            continue

        name = name_item.text().strip()

        type_widget = window.tdoTable_3.cellWidget(row, 1)

        if type_widget is not None:
            var_type = type_widget.currentText()
        else:
            type_item = window.tdoTable_3.item(row, 1)
            var_type = type_item.text() if type_item else ""

        if name and var_type:
            variables[name.upper()] = var_type.upper()

    return [
        {
            "name": "TDOG",
            "data": variables
        }
    ]
def add_variable():
    table = window.tdoTable_3
    table.setColumnCount(2)

    row = table.rowCount()
    table.insertRow(row)

    name_item = QTableWidgetItem("")
    name_item.setFlags(
    name_item.flags() | Qt.ItemIsEditable
    )
    table.setItem(row, 0, name_item)

    type_combo = QComboBox()
    type_combo.addItems([
        "ENTIER",
        "REEL",
        "BOOLEAN",
        "CARACTERE",
        "CHAINE"
    ])

    table.setCellWidget(row, 1, type_combo)

    table.setCurrentCell(row, 0)


def delete_variable():
    table = window.tdoTable_3

    row = table.currentRow()

    if row >= 0:
        table.removeRow(row)
        
def qt_input(prompt=""):
    value, ok = QInputDialog.getText(
        window,
        "AlgoTN - LIRE",
        str(prompt) if prompt else "Entrez une valeur :"
    )

    if not ok:
        raise AlgoTNError("Saisie annulée")

    return value

class ConsoleInput(QObject):

    def __init__(self, console):
        super().__init__()
        self.console = console
        self.waiting = False
        self.loop = None
        self.value = ""
        self.input_start = 0

        self.console.setReadOnly(True)
        self.console.installEventFilter(self)

    def read_input(self, prompt=""):
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(str(prompt))

        self.input_start = self.console.textCursor().position()

        self.waiting = True
        self.console.setReadOnly(False)
        self.console.setFocus()

        self.loop = QEventLoop()
        self.loop.exec_()

        self.console.setReadOnly(True)
        return self.value

    def eventFilter(self, watched, event):

        if watched == self.console and event.type() == QEvent.KeyPress and self.waiting:

            cursor = self.console.textCursor()
            key = event.key()

            if key in (Qt.Key_Return, Qt.Key_Enter):
                cursor.movePosition(QTextCursor.End)
                cursor.setPosition(self.input_start, QTextCursor.KeepAnchor)

                self.value = cursor.selectedText()

                self.console.moveCursor(QTextCursor.End)
                self.console.insertPlainText("\n")

                self.waiting = False
                self.loop.quit()
                return True

            if key == Qt.Key_Backspace:
                if cursor.position() <= self.input_start and not cursor.hasSelection():
                    return True

            if key == Qt.Key_Left and cursor.position() <= self.input_start:
                return True

            if key == Qt.Key_Home:
                cursor.setPosition(self.input_start)
                self.console.setTextCursor(cursor)
                return True

            if cursor.position() < self.input_start:
                self.console.moveCursor(QTextCursor.End)

        return super().eventFilter(watched, event)

class ConsoleStream:

    def __init__(self, console):
        self.console = console

    def write(self, text):
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(text)
        self.console.ensureCursorVisible()

    def flush(self):
        pass

def execute_code():
    code = window.CodeEditor.toPlainText()
    import builtins


    old_input = builtins.input

    window.ConsoleOutput.clear()

    try:
        tokens = tokenize(code)

        parser = Parser(tokens)
        tree = parser.parse()

        interpreter = Interpreter()
        interpreter.node_lines = parser.node_lines

        builtins.input = console_input.read_input
        
        with redirect_stdout(ConsoleStream(window.ConsoleOutput)):
            process_tables(get_tdo_data())
            interpreter.run(tree)

        



        window.ConsoleOutput.moveCursor(QTextCursor.End)
        window.ConsoleOutput.insertPlainText(
            "\nExécution terminée."
        )

    except AlgoTNError as error:
        window.ConsoleOutput.appendPlainText(
            "\nERREUR : " + str(error)
        )

    except Exception as error:
        window.ConsoleOutput.appendPlainText(
            "\nERREUR INTERNE : " + str(error)
        )

    finally:
        builtins.input = old_input
        window.ConsoleOutput.setReadOnly(True)
    
def run():
    window.actionNouveau.triggered.connect(new_file)
    window.actionouvrir.triggered.connect(open_file)
    window.actionEnregistrer.triggered.connect(save_file)
    window.actionEx_cuter.triggered.connect(execute_code)
    window.btnAddVariable.clicked.connect(add_variable)
    window.btnDeleteVariable.clicked.connect(delete_variable)



def continuer():
    if test.check2eme.isChecked():
        test.close()
        window.show()
        run()
    elif test.check3eme4eme.isChecked():
        test.StartupMessage.setText("Coming Soon ...")
test.btnContinue.clicked.connect(continuer)
console_input = ConsoleInput(window.ConsoleOutput)
sys.exit(app.exec_())