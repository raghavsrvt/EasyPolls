import PySimpleGUI as sg, hashlib, os
from sqlite3 import connect
from src.get_absolute_path import resource_path

CONTINUE_BTN = resource_path(r'src\assets\btn\continue_btn.png')

conn = connect(os.path.join(resource_path('src\\'),'election.db'))
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_data(
    passwd TEXT DEFAULT '',
    election_status INT DEFAULT 0,
    election_name TEXT DEFAULT ''
);
''')
conn.commit()
cursor.execute('SELECT election_status FROM user_data')
election_status = cursor.fetchone()
if election_status:
    election_status = election_status[0]


# Define the password input layout based on whether password exists or not
def passwd_layout(passwd):
    if passwd:
        return [sg.Column([[sg.Text('Enter password: ',pad=(0,11)), sg.Input(key='passwd-1',size=(40),expand_y=True,password_char='•')]],pad=((6,0),(11,11)))]
    else:
        return [sg.Column([
            [sg.Text('Create an admin password',pad=((0,0),(11,0)),font=(None,15,'bold'))],
            [sg.Text('Access exclusive rights like creating election posts and viewing results.', text_color='#737373', pad=((0,0),(11,18)))],
            [sg.Text('Enter password: ',pad=(0,11)), sg.Input(key='passwd-1',size=(40),expand_y=True,expand_x=True,password_char='•')],
            [sg.Text('Confirm password: ',pad=(0,11)), sg.Input(key='passwd-2',size=(40),expand_y=True,password_char='•')]
        ],pad=((6,0),(11,11)))]



# Hash a password using SHA-256
def hash_passwd(passwd):
    passwd_bytes = passwd.encode('utf-8')
    hashed_passwd = hashlib.sha256(passwd_bytes).hexdigest()
    return hashed_passwd


# Check if the entered password is correct
def check_passwd_correct(values,passwd):
    passwd_entered = hash_passwd(values['passwd-1'])
    return passwd_entered == passwd[0]


# Save the hashed password to a file
def passwd_input(passwd):
    hashed_passwd = hash_passwd(passwd)
    cursor.execute('INSERT INTO user_data (passwd) VALUES (?)',(hashed_passwd,))
    conn.commit()


def display_password_window():
    show_admin_panel = False
    cursor.execute('SELECT passwd FROM user_data')
    passwd = cursor.fetchone()
    # Define the layout of the window
    layout = [
        passwd_layout(passwd),
        [sg.pin(sg.Text(key='passwd-error', text_color='#D33030',font=(None,11,'bold'),visible=False),shrink=True)],
        [sg.Image(CONTINUE_BTN, key='passwd-submit',enable_events=True,pad=((6,6)))]
    ]
    window = sg.Window('Admin Password  •  EasyPolls', layout, finalize=True, modal=True)

    window['passwd-1'].bind("<Return>", "_Enter")
    window['passwd-1'].set_focus()
    if window['passwd-2']:
        window['passwd-2'].bind("<Return>", "_Enter")
    while True:
        event, values = window.read() 
        passwd_error = window['passwd-error']
        
        if event != sg.WIN_CLOSED:

            if event == 'passwd-submit' or event=='passwd-1'+'_Enter' or event=='passwd-2'+'_Enter':
                if passwd:
                    # If password file exists, verify the entered password
                    if values['passwd-1'] != '':
                        if check_passwd_correct(values,passwd):
                            show_admin_panel = True
                            break
                        else:
                            passwd_error.update(visible=True) 
                            passwd_error.update('Incorrect Password') 
                    else:
                        passwd_error.update('Please enter a password') 
                else:
                    # If no password file exists, set a new password
                    if values['passwd-1'].isspace() or values['passwd-1'] == '' or not values['passwd-1'].isalnum():
                        passwd_error.update(visible=True) 
                        passwd_error.update('Password can only contain alphanumeric characters.') 
                    elif values['passwd-1'] != values['passwd-2']:
                        passwd_error.update(visible=True) 
                        passwd_error.update("Those passwords don't match. Try again.") 
                    else:
                        passwd_input(values['passwd-1'])
                        show_admin_panel = True
                        break
        else:
            break

    window.close()
    return (show_admin_panel,election_status)