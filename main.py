from src.password_functions import display_password_window
from ctypes import windll
from src.set_theme import set_theme
windll.shcore.SetProcessDpiAwareness(1)
passwd_correct, election_status = None, None
set_theme()
try:
    passwd_correct, election_status = display_password_window()
except UnboundLocalError:
    print('The user closed the window.')

if passwd_correct:
    if election_status:
        from sqlite3 import connect
        from src.get_absolute_path import resource_path
        from src.e_voting import display_voting_panel
        
        conn = connect(resource_path('src\\election.db'))
        cursor = conn.cursor()
        cursor.execute('SELECT election_name FROM user_data')
        display_voting_panel(cursor.fetchone()[0])
    else:
        from src.admin_functions import display_admin_panel
        display_admin_panel()