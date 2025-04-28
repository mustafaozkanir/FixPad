from pywinauto import Application

# Connect to Notepad++
app = Application(backend="uia").connect(title_re=".*Notepad.*")

# Access the main Notepad++ window
window = app.window(title_re=".*Notepad.*")

# Access the Preferences child window
prefs_window = window.child_window(title_re="Find", control_type="Window")

# Print all controls inside Preferences
prefs_window.print_control_identifiers()
