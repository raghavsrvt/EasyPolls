import PySimpleGUI as sg, sqlite3
from src.password_functions import display_password_window
from shutil import rmtree
from src.set_theme import set_theme
from src.get_absolute_path import resource_path

set_theme()
submit_btn = resource_path('src\\assets\\btn\\submit_btn.png')
end_election_btn = resource_path('src\\assets\\btn\\end_election_btn.png')
grey = '#E2E2E2'
dark_grey = '#F5F5F5'

# Connect to the SQLite database
conn = sqlite3.connect(resource_path('src\\election.db'))
cursor = conn.cursor()

screen_width, screen_height = sg.Window.get_screen_size()
candidate_image_size = (400, 400)

post_names = []
posts_layout = []

passwd_correct, election_status = None, None

unchecked_box = resource_path('src\\assets\\btn\\unchecked_box.png')
checked_box = resource_path('src\\assets\\btn\\checked_box.png')

def display_candidates(post_name):
    """
    Display candidates from the specified post table.

    Parameters:
    - post_name (str): Name of the post table from which candidates will be fetched.

    Returns:
    - list: A list containing PySimpleGUI layout elements to display candidates.
    """
    cursor.execute(f'SELECT name,image FROM "{post_name}"')
    post_data = cursor.fetchall()
    max_id = len(post_data)
    if((post_name,max_id) not in post_names):
        post_names.append((post_name,max_id))
    col_val = 1 # A key to know whether both the columns are added or not
    key_val = 1
    temp_layout = []
    col_1 = None # column element at left
    col_2 = None # column element at right

    for i in post_data:

        if (post_data.index(i)==0):
            checkbox_element = sg.Image(checked_box,enable_events=True,key=f'{post_name}-{key_val}-checkbox',metadata=[True,max_id],background_color='#FFFFFF',pad=((0,0),(5,6)))
        else:
            checkbox_element = sg.Image(unchecked_box,enable_events=True,key=f'{post_name}-{key_val}-checkbox',metadata=[False,max_id],background_color='#FFFFFF',pad=((0,0),(5,6)))

        candidate_image = [sg.Image(i[1],size=candidate_image_size,background_color='#FFFFFF')]
        checkbox_text = sg.Text(i[0],key=f'{post_name}-{key_val}-checkboxtext',enable_events=True,font=(None,14),background_color='#FFFFFF',pad=((2,0),(5,7)))

        if(col_val==1):
            col_1 = sg.Column([candidate_image,[sg.Push(background_color='#FFFFFF'),checkbox_element,checkbox_text,sg.Push(background_color='#FFFFFF')]],background_color='#FFFFFF',pad=((20,10),(20,0)))
            col_val = 2
            if post_data.index(i)==len(post_data)-1:
                temp_layout.append([col_1])

        elif (col_val==2):
            col_2 = sg.Column([candidate_image,[sg.Push(background_color='#FFFFFF'),checkbox_element,checkbox_text,sg.Push(background_color='#FFFFFF')]],background_color='#FFFFFF',pad=((10,20),(20,0)))
            temp_layout.append([col_1,col_2])
            col_1,col_2 = None,None
            col_val = 1
        key_val+=1
    temp_layout.insert(0, [sg.Text(post_name,font=(None,18,'bold'),pad=((24,0),(20,0)),background_color='#FFFFFF',text_color='black')])
    temp_layout.append([sg.Text('',size=(0,1),font=(None,7),background_color='#FFFFFF')])
    return [sg.Column(temp_layout,pad=((15,7.5)),background_color='#FFFFFF')]
            
# Load available election data
def load_election_data():
    """
    Load election data from the SQLite database and create a layout to display candidates.

    Returns:
    - list: A list containing PySimpleGUI layout elements to display candidate information.
    """
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    temp_layout = [] # Layout for the column which would be added to posts_layout

    # Remove the tables not related to posts.
    if ('sqlite_sequence',) in tables:
        tables.remove(('sqlite_sequence',))
    if('user_data',) in tables:
        tables.remove(('user_data',))
    post_num=1
    for i in tables:
        post_name = i[0]
        temp_layout.append(display_candidates(post_name))
        post_num+=1
    temp_layout.append([sg.Image(submit_btn,enable_events=True, key='submit-votes',pad=(9,10))])
    posts_layout.append(sg.Column(temp_layout,vertical_scroll_only=True,expand_y=True,scrollable=True,pad=(25,25)))

def passwd_check_end_elections():
    '''
    Check the password for ending elections and update global variables accordingly.
    '''
    try:
        global passwd_correct, election_status
        passwd_correct, election_status = display_password_window()
    except:
        print('User closed the password popup.')

def display_voting_panel(election_name):
    global post_names,posts_layout, passwd_correct,election_status
    passwd_correct, election_status = None, None
    user_quit = False
    end_elections = False
    post_names,posts_layout = [],[]
    user_election_name = election_name
    shown_admin_panel = False
    header_layout = [sg.Frame('',[[sg.Text(f'{election_name} Election │ EasyPolls',text_color='#4E46B4',font=(None,18,'bold')),sg.Push(),sg.Image(end_election_btn,key='end-elections-btn',enable_events=True)]],expand_x=True)] 
    layout = [header_layout]
    load_election_data()

    layout.append(posts_layout)

    window = sg.Window(f'{election_name} Election  •  EasyPolls  •  Made by Raghav Srivastava (GitHub: raghavsrvt)', layout, size=(screen_width - 80, screen_height - 120), resizable=True,element_justification='c')
    
    # Function to make custom radio button work
    def check_radio(key,post_name,max_id):
        for i in range(1,max_id+1):
            window[f'{post_name}-{i}-checkbox'].update(unchecked_box) 
            window[f'{post_name}-{i}-checkbox'].metadata[0] = False 
        window[key].update(checked_box) 
        window[key].metadata[0] = True
    
    while True:
        event, values = window.read() 
        
        if event!=sg.WIN_CLOSED:
            # Get checkbox key and call the check_radio function
            if event.endswith('checkbox') or event.endswith('checkboxtext'):
                if 'checkboxtext' in event:
                    key = event.replace('checkboxtext','checkbox')
                else:
                    key = event
                post_name = key.split('-')[0]
                check_radio(key,post_name,window[key].metadata[1]) 
            
            # Submit the votes on click of submit button and then ask for password after breaking while loop
            elif event == 'submit-votes':
                for i in post_names:
                    post_name = i[0]
                    max_id = i[1]
                    for j in range(1,max_id+1):
                        if(window[f'{post_name}-{j}-checkbox'].metadata[0] == True): 
                            cursor.execute(f'UPDATE "{post_name}" SET votes = votes + 1 WHERE id={j}')
                            conn.commit()
                            break
                break
            elif event == 'end-elections-btn':
                passwd_check_end_elections() # Ask password before edning the election
                if passwd_correct:
                    end_elections = True
                    passwd_correct,election_status = None,None
                    cursor.execute('SELECT election_name FROM user_data')
                    election_name = cursor.fetchone()[0] # Get election name
                    result_path = resource_path(f'src\\results\\result-{election_name}.db')
                    conn_result = sqlite3.connect(result_path)
                    cursor_result = conn_result.cursor()
                    for i in post_names:
                        post_name = i[0]
                        cursor.execute(f'SELECT name,votes FROM "{post_name}"')
                        post_data = cursor.fetchall()

                        cursor_result.execute(f'''CREATE TABLE IF NOT EXISTS "{post_name}" (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                            name TEXT,
                                            votes INT
                                            );''')
                        
                        for j in post_data:
                            cursor_result.execute(f'INSERT INTO "{post_name}" (name,votes) VALUES (?,?)',(j[0],j[1])) # Inserting value in the result database
                            conn_result.commit()
                    conn_result.close()
                    for i in post_names:
                        post_name = i[0]
                        cursor.execute(f'DROP TABLE "{post_name}"')
                        rmtree(resource_path(f'src\\assets\\post_img\\{post_name}'))
                        conn.commit()
                    
                    cursor.execute('UPDATE user_data SET election_status = 0')  
                    cursor.execute('UPDATE user_data SET election_name =""')  
                    conn.commit()
                    break
        else:
            user_quit = True
            break
    window.close()
    
    # Ask for password after submission to continue voting
    if not end_elections and not user_quit:   
        passwd_correct, election_status = display_password_window()
        if passwd_correct:
            display_voting_panel(user_election_name)
    # Show admin panel after ending the elections
    if end_elections and not shown_admin_panel:
        from src.admin_functions import display_admin_panel
        if(not shown_admin_panel):
            shown_admin_panel = True
            display_admin_panel()