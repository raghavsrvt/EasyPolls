from src.admin_functions import display_admin_panel
from src.password_functions import display_password_window
from src.e_voting import display_voting_panel
from ctypes import windll
from src.get_absolute_path import resource_path
import sqlite3
windll.shcore.SetProcessDpiAwareness(1)
passwd_correct, election_status = None, None

try:
    passwd_correct, election_status = display_password_window()
except UnboundLocalError:
    print('The user closed the window.')

if passwd_correct:
    if election_status:
        conn = sqlite3.connect(resource_path('src\\election.db'))
        cursor = conn.cursor()
        cursor.execute('SELECT election_name FROM user_data')
        display_voting_panel(cursor.fetchone()[0])
    else:
        display_admin_panel()