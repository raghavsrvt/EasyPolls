import PySimpleGUI as sg, sqlite3, os
from re import match
from shutil import rmtree
from PIL import Image
from src.password_functions import display_password_window
from src.e_voting import display_voting_panel
from src.results import display_results
from src.set_theme import set_theme
from src.get_absolute_path import resource_path
from io import BytesIO

set_theme()

# Define paths for button images
view_img_btn = resource_path('src\\assets\\btn\\view_img_btn.png')
delete_btn = resource_path('src\\assets\\btn\\delete_btn.png')
cancel_btn = resource_path('src\\assets\\btn\\cancel_btn.png')
edit_btn = resource_path('src\\assets\\btn\\edit_btn.png')
save_btn = resource_path('src\\assets\\btn\\save_btn.png')
add_post_btn = resource_path('src\\assets\\btn\\add_post_btn.png')
start_election_btn = resource_path('src\\assets\\btn\\start_election_btn.png')
available_results_btn = resource_path('src\\assets\\btn\\available_results_btn.png')
add_candidates_btn = resource_path('src\\assets\\btn\\add_candidates_btn.png')

# Define colors
grey = '#E2E2E2'
dark_grey = '#F5F5F5'
red = '#D33030'

conn = sqlite3.connect(resource_path('src\\election.db')) # Connect to the SQLite database
cursor = conn.cursor()

screen_width, screen_height = sg.Window.get_screen_size() # Get the screen width and height
candidate_image_size = (400, 400)

added_posts_heading = []

available_results = []

def get_available_results():
    global available_results
    available_results = []
    if os.path.exists(resource_path('src\\results')) == False:
        os.makedirs(resource_path('src\\results'))
    
    src_dirs = os.listdir(resource_path('src\\results'))
    for i in src_dirs:
        if i.startswith('result-'):
            available_results.append(i.split('-',1)[1]) # Add the name of available election result

def styleAddedPosts(post_name,load_posts_layout):
    """
    Create the layout for displaying a post's details.

    Args:
        post_name (str): The name of the post.
        load_posts_layout (list): The layout to which the post's details will be added.

    Returns:
        list: The updated layout including the post's details.
    """
    cursor.execute(f'SELECT name,image FROM "{post_name}"')
    post_data = cursor.fetchall()

    # Layout for each post entry
    post_layout = [[sg.Text(post_name,font=(None,15,'bold'),pad=((12,0),(12, 8)),background_color='#FFFFFF'),sg.Push(background_color='#FFFFFF'),sg.Image(edit_btn,enable_events=True,key=f'edit-{post_name}',pad=((0,8),(12, 5)),metadata='Edit'),sg.Image(cancel_btn,enable_events=True,key=f'cancel-{post_name}',background_color='#FFFFFF',pad=((0,8),(12, 5)),visible=False),sg.Image(delete_btn,enable_events=True,key=f'delete-{post_name}',pad=((0,12),(12, 5)))]] 
    
    key_val = 1
    for i in post_data:
        # Input fields for post name, image and browse button
        post_layout.append([sg.Input(i[0],key=f'{post_name}-name-{key_val}',expand_y=True,disabled=True,size=(30),pad=((12,0),(4, 4))),
                            sg.Input(i[1],key=f'{post_name}-image-{key_val}',expand_y=True,disabled=True,size=(30),pad=(8,4)),
                            sg.Image(view_img_btn,enable_events=True,key=f'{post_name}-view-image-{key_val}',pad=((0,8),(4, 4)),background_color='#FFFFFF'),
                            sg.FileBrowse('   Browse Image   ', key=f'{post_name}-image-button-{key_val}',target=f'{post_name}-image-{key_val}',file_types=(("Image Files", "*.png;*.jpg;*.jpeg;*.webp"),),disabled=True,button_color=f'{dark_grey} on {grey}',pad=((0,12),(4, 4)),expand_y=True,font=(None,11,'bold')),
                            ])
        key_val+=1
    post_layout.extend([[sg.Text('',size=(0,1),font=(None,1))]])
    load_posts_layout.append([sg.pin(sg.Column(post_layout,pad=(5,10),key=f'{post_name}_container',background_color='#FFFFFF'))])
    return load_posts_layout

# Function to load existing posts from the database
def loadPosts(main_layout):
    """
    Load existing posts from the database and add them to the main layout.

    Args:
        main_layout (list): The main layout of the GUI.

    Returns:
        list: The updated main layout including the loaded posts.
    """

    get_available_results()
    load_posts_layout = []

    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()

    if ('sqlite_sequence',) in tables:
        tables.remove(('sqlite_sequence',))
    if('user_data',) in tables:
        tables.remove(('user_data',))

    if tables:
        load_posts_layout.append(added_posts_heading)

        for i in tables:
            post_name = i[0]
            load_posts_layout = styleAddedPosts(post_name,load_posts_layout)

    header_layout = [[sg.Text('Admin │ EasyPolls',text_color='#4E46B4',font=(None,18,'bold')),sg.Push(),sg.Image(available_results_btn,key='check-results',visible=bool(available_results),enable_events=True),sg.Image(start_election_btn,key='start-elections-btn',visible=bool(tables),enable_events=True)]]
    main_layout.insert(0,[sg.Frame('',header_layout,expand_x=True)])
    # Adding loaded posts to the main layout
    main_layout.append([sg.Column(load_posts_layout,key='posts-container',scrollable=True,vertical_scroll_only=True,expand_y=True,expand_x=True)])
    return main_layout

def error_popup(error_message):
    error_popup = sg.popup_ok(error_message,text_color=red,modal=True,font=(None,12,'bold'))

def table_exists(table_name):
    """
    Check if a table with the given name exists in the database.

    Args:
        table_name (str): The name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    cursor.execute(f'SELECT name FROM sqlite_master WHERE type="tabl" AND name="{table_name}"')
    result = cursor.fetchone()
    return result is not None

def inputValidation(element,no_of_candidates,values,post_name,action,window):
    """
    Validate inputs for creating or saving a post.

    Args:
        element (PySimpleGUI element): The element to update with error message.
        no_of_candidates (int): Number of candidates for the post.
        values (dict): Dictionary containing values from the GUI inputs.
        post_name (str): Name of the post.
        action (str): Action to perform ('create post' or 'save post').
    """
    all_inputs_filled = True
    candidate_info = []
    
    # Collect candidate information and validate inputs
    for i in range(1, no_of_candidates + 1):
        candidate_image = values.get(f'{post_name}-image-{i}', '').strip()
        candidate_name = values.get(f'{post_name}-name-{i}', '').strip()
        
        if not candidate_image or not candidate_name or candidate_image=='Selected image\'s path will appear here.':
            all_inputs_filled = False
            error_popup('Please fill all inputs.')
            break
        
        candidate_info.append((candidate_name, candidate_image))
    
    # Extracting candidate names and images
    candidate_names = [i[0] for i in candidate_info]
    candidate_images = [os.path.basename(i[1]) for i in candidate_info]

     # Checking for duplicate names and images
    dup_names_exist = len(candidate_names) != len(set(candidate_names))
    dup_images_exist = len(candidate_images) != len(set(candidate_images))
    
    # Handling different validation scenarios
    if dup_names_exist:
        error_popup('Every name entered should be unique.')  
    elif dup_images_exist:
        error_popup("Every image's name should be unique.")  
    elif all_inputs_filled and action =='create post':
        create_table(post_name, candidate_info,window)
        element.close()
    elif all_inputs_filled and action =='save post':
        save_edited_post(post_name, no_of_candidates,candidate_info, element)
    elif all_inputs_filled==False:
        print('All inputs were not filled.')
    else:
        print('An error occurred.')

# <======================================= EDIT & DELETE POST =======================================>

def delete_post(post_name,window):
    """
    Delete a post from the database and update the GUI.

    Args:
        post_name (str): The name of the post to delete.
        container (sg.Column): The container to update after deletion.
    """
    if sg.popup_yes_no(f'Are you sure you want to delete the post titled {post_name}?') == 'Yes':

        cursor.execute(f'DROP TABLE "{post_name}";')
        conn.commit()
        rmtree(resource_path(f'src\\assets\\post_img\\{post_name}'))
        window[f'{post_name}_container'].update(visible=False)
        del window.key_dict[f'{post_name}_container']
        
        other_posts_exist = False
        for key in window.key_dict:
            if key.endswith('_container') and key!=f'{post_name}_container':
                other_posts_exist = True
                break
        if not other_posts_exist:
            window['start-elections-btn'].update(visible=False)
            window['added_posts_heading'].update(visible=False)

def save_edited_post(post_name,max_id,candidates_info,window):
    '''
    Update the entries in the specified post table with new candidate information.

    Parameters:
    - post_name (str): Name of the post table to update.
    - max_id (int): Maximum ID of entries in the post table.
    - candidates_info (list): List of tuples containing candidate information (name, image_path).
    - window: PySimpleGUI window object to interact with GUI elements.
    '''
    window[f'edit-{post_name}'].metadata = 'Edit'
    window[f'edit-{post_name}'].update(edit_btn)
    save_post_query = f"""
UPDATE {post_name}
SET name = ?,image= ?
WHERE id = ? AND (name != ? OR image != ?);
"""
    curr_id = 1
    post_img_path = resource_path(f'src\\assets\\post_img\\{post_name}')

    for candidate in candidates_info:

        cursor.execute(f'SELECT image FROM "{post_name}" WHERE id={curr_id}')
        prev_image_path = cursor.fetchone()
        
        base_image_name = os.path.basename(candidate[1])
        image_name = f'{os.path.splitext(base_image_name)[0]}.png'
        image_path = f'{post_img_path}\\{image_name}' 
        
        window[f'{post_name}-image-{curr_id}'].update(f'{image_path}')
        cursor.execute(save_post_query,(candidate[0],image_path,curr_id,candidate[0],image_path))
        if(candidate[1]!=prev_image_path[0]):
            im = Image.open(candidate[1])
            im.thumbnail(candidate_image_size) # Save the image in the resolution of 400 X 400 pixels
            im.save(image_path, format = "png") # Save as png
        curr_id+=1
    
    conn.commit()
    window[f'cancel-{post_name}'].update(visible=False)
    cursor.execute(f'SELECT image FROM "{post_name}"')
    all_img_name = [os.path.basename(i[0]) for i in cursor.fetchall()]

    for i in os.listdir(post_img_path):
        if(i not in all_img_name):
            remove_file = os.path.join(post_img_path,i) # Remove unused images.
            os.remove(remove_file)
    
    for i in range(1,max_id+1):
        window[f'{post_name}-name-{i}'].update(disabled=True) 
        window[f'{post_name}-image-button-{i}'].update(disabled=True,button_color=f'{dark_grey} on {grey}')  

def edit_post(post_name,window):
    """
    Enable editing of candidate information for a post.

    Args:
        post_name (str): The name of the post.
        window (PySimpleGUI window): The main GUI window.
    """
    window[f'edit-{post_name}'].metadata = 'Save'
    window[f'edit-{post_name}'].update(save_btn)
    cursor.execute(f'SELECT MAX(id) FROM "{post_name}";')
    max_id = cursor.fetchone()[0]

    window[f'cancel-{post_name}'].update(visible=True)
    for i in range(1,max_id+1):
        window[f'{post_name}-name-{i}'].update(disabled=False,background_color='#EBEBEB') # Enable candidate name input fields
        window[f'{post_name}-image-button-{i}'].update(disabled=False,button_color = '#FFFFFF on #4E46B4') # Enable browse buttons for candidate images


# <================================= CREATE NEW POST ====================================>

def create_table(post_name, candidate_info,window):
    """
    Create a table for the given post name and insert candidate information into the table.

    Args:
        post_name (str): The name of the post.
        candidate_info (list): A list of tuples containing candidate names and image paths.
    """
    # Create the table if it does not exist
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS "{post_name}"(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name TEXT UNIQUE,
        votes INT DEFAULT 0,
        image TEXT UNIQUE
    );
    ''')
    
    # Create a directory to store candidate images
    post_img_path = resource_path(f'src\\assets\\post_img\\{post_name}')
    os.makedirs(post_img_path)
    
    # Copy candidate images to the directory and insert candidate info into the table
    for candidate in candidate_info:
        base_image_name = os.path.basename(candidate[1])
        image_name = f'{os.path.splitext(base_image_name)[0]}.png'
        image_path = f'{post_img_path}\\{image_name}' 
        im = Image.open(candidate[1])
        im.thumbnail(candidate_image_size)
        im.save(image_path, format = "png")
        cursor.execute(f'INSERT INTO "{post_name}" (name, image) VALUES (?,?)', (candidate[0], image_path))
    
    # Commit the changes to the database
    conn.commit()
    post_layout = styleAddedPosts(post_name,[])
    posts_heading_exists = window.find_element('added_posts_heading', silent_on_error=True)

    if not posts_heading_exists:
        post_layout.insert(0,added_posts_heading)

    window['added_posts_heading'].update(visible=True)
    window['start-elections-btn'].update(visible=True)
    window.extend_layout(window['posts-container'],post_layout)

def create_post_modal(post_name, no_of_candidates,window):
    """
    Create and display a modal window to collect candidate information.

    Args:
        post_name (str): The name of the post.
        no_of_candidates (int): The number of candidates.
    """
    post_modal_layout = [[sg.Text('Provide Candidate Information:',font=(None,18,'bold'),pad=(10,10))]]
    column_layout = []
    # Create input fields for each candidate's name and image
    for i in range(1, no_of_candidates + 1):
        candidate_layout = [sg.Column([[
            sg.Text(f'Candidate {i}: ',pad=((0,10),(11,11))), 
            sg.Input(key=f'{post_name}-name-{i}',expand_y=True, size=(40)), 
            sg.Input('Selected image\'s path will appear here.',key=f'{post_name}-image-{i}', disabled=True, text_color='black', size=(25),expand_y=True),
            sg.FileBrowse('   Browse Image   ', file_types=(("Image Files", "*.png;*.jpg;*.jpeg;*.webp"),),font=(None,11,'bold'),expand_y=True)
        ]])]
        column_layout.append(candidate_layout) 
    column_layout.append([sg.Image(add_candidates_btn, key=f'{post_name}-save-btn',pad=(5,5),enable_events=True)]) 
    post_modal_layout.append([sg.Column(column_layout,vertical_scroll_only=True,scrollable=True,expand_x=True,expand_y=True)]) 
    
    
    # Create and display the modal window
    post_modal = sg.Window(f'Add post information for {post_name}  •  EasyPolls  •  Made by Raghav Srivastava (GitHub: raghavsrvt)', post_modal_layout, size=(screen_width - 80, screen_height - 120), resizable=True,modal=True)
    
    while True:
        event, values = post_modal.read() 
        if event != sg.WIN_CLOSED:
            if event == f'{post_name}-save-btn':
                inputValidation(post_modal,no_of_candidates,values,post_name,'create post',window)
        else:
            break

# <======================================== DISPLAY THE ADMIN PANEL ===================================>

def display_admin_panel():
    global added_posts_heading, available_results
    """
    Display the main admin panel window to add new posts and candidates.
    """
    added_posts_heading = [sg.Text('Added Posts:',font=(None,18,'bold'),pad=(10,10),key='added_posts_heading')]
    layout = [[sg.Text('Create Post:',font=(None,18,'bold'),pad=((9,0),(16,10)))],
            [sg.Column([[sg.Text('Post name: ',pad=(0,11)), sg.Input(key='post-name',size=(40,50),expand_y=True,expand_x=True)],[sg.Text('No of candidates: ',pad=(0,11)), sg.Input(key='no-of-candidates',size=(40,50),expand_y=True)]],pad=(9,0))],
            [sg.Image(add_post_btn, key='add-post-btn',pad=(9,10),enable_events=True)],
            ]
    layout = loadPosts(layout)
    window = sg.Window('Admin  •  EasyPolls  •  Made by Raghav Srivastava (GitHub: raghavsrvt)', layout, size=(screen_width - 80, screen_height - 120), resizable=True)
    
    while True:
        event, values = window.read() 

        if event != sg.WIN_CLOSED:
            if event == 'add-post-btn':
                post_name = values['post-name']
                
                # Validate the post name
                if post_name == '' or post_name.isspace():
                    error_popup("Post name can't be empty")  
                elif match(r'^[^a-zA-Z]', post_name):
                    error_popup('Post name must start with a letter.')  
                elif '-' in post_name:
                    error_popup("Post name must not contain '-'.")  
                # elif includes_reserved_words:
                #     error_popup(f"Sorry, you can't use {post_name} as it contains reserved words.") 
                elif table_exists(post_name):
                    error_popup('Post with this name already exists.')  
                else:
                    try:
                        no_of_candidates = int(values['no-of-candidates'])
                        if no_of_candidates < 2:
                            raise ValueError("No. of candidates < 2")
                        create_post_modal(post_name, no_of_candidates,window)
                    except ValueError:
                        error_popup('No. of candidates should be at least 2.')  

            # Edit post
            elif event.startswith('edit-') and window[event].metadata == 'Edit': 
                edit_post(event.partition('-')[2],window)

            # Save edited post
            elif event.startswith('edit-') and window[event].metadata == 'Save': 
                post_being_edited = event.partition('-')[2]
                cursor.execute(f'SELECT MAX(id) FROM "{post_being_edited}";')
                max_id = cursor.fetchone()[0]
                inputValidation(window,max_id,values,post_being_edited,'save post',window)
                
            #cancel changes
            elif event.startswith('cancel-'):
                postname = event.split('-')[1]
                cursor.execute(f'SELECT name,image FROM "{postname}"')
                post_data = cursor.fetchall()
                key_val = 1
                for i in post_data:
                    window[f'{postname}-name-{key_val}'].update(i[0]) 
                    window[f'{postname}-image-{key_val}'].update(i[1]) 
                    key_val+=1
                
                cursor.execute(f'SELECT MAX(id) FROM "{postname}"')
                max_id = cursor.fetchone()[0]
                for i in range(1,max_id+1):
                    window[f'{postname}-name-{i}'].update(disabled=True) 
                    window[f'{postname}-image-button-{i}'].update(disabled=True,button_color='#e8e8e8 on #f2f2f2') 
                window[f'edit-{postname}'].metadata = 'Edit' 
                window[f'edit-{postname}'].update(edit_btn) 
                window[event].update(visible=False) 

            # Delete a post
            elif event.startswith('delete-'):
                delete_post(event.partition('-')[2],window)

            #View image:
            elif 'view-image' in event:
                # edit-postname
                l = event.split('-')
                postname,key_val = l[0],l[3]
                image_path = values[f'{postname}-image-{key_val}']

                # If in edit mode then save image in 400X400 resolution to not crop the image.
                if window[f'edit-{postname}'].metadata == 'Save':
                    im = Image.open(image_path)
                    im.thumbnail(candidate_image_size)
                    bytesio = BytesIO()
                    im.save(bytesio,format='png')
                    image_view_layout = [[sg.Push(),sg.Image(data=bytesio.getvalue(),key='view-image'),sg.Push()]]
                else:
                    image_view_layout = [[sg.Push(),sg.Image(image_path,key='view-image'),sg.Push()]]

                image_view_window = sg.Window('View image',image_view_layout,size=(400,400))
                while True:
                    event,values = image_view_window.read() 
                    if event == sg.WIN_CLOSED:
                        break
                image_view_window.close()
            
            # Start Elections:
            elif event=='start-elections-btn':
                election_name = sg.popup_get_text('Name the Election',modal=True)
                if election_name:
                    if f'{election_name.strip()}.db' in available_results:
                        error_popup('A result with this election name already exists. Please try again with a different name.')

                    if f'{election_name.strip()}.db' not in available_results:
                        passwd_correct = display_password_window()[0]
                        if passwd_correct:
                            available_results = []
                            cursor.execute('UPDATE user_data SET election_status = 1;')
                            cursor.execute('UPDATE user_data SET election_name =(?)',(election_name,))
                            conn.commit()

                            window.close()
                            display_voting_panel(election_name.strip())
            
            # Check results
            elif event=='check-results':
                display_results(available_results)
                get_available_results()
                if not available_results:
                    window[event].update(visible=False)
        else:
            break
    window.close()