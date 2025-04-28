from pywinauto import Application, Desktop
"""
# Connect to Notepad++
app = Application(backend="uia").connect(title_re=".*Notepad.*")
window = app.window(title_re=".*Notepad.*")

# Find Scintilla editor window
editor = window.child_window(class_name="Scintilla")

# Now you can interact with it!
editor.print_control_identifiers()
"""

# This connects to the full desktop environment
desktop = Desktop(backend="uia")

# List all windows matching "Notepad"
elements = desktop.windows(title_re=".*Notepad.*")
for elem in elements:
    print(elem.window_text())
