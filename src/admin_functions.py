import PySimpleGUI as sg, os
from sqlite3 import connect
from shutil import rmtree
from PIL import Image
from io import BytesIO
from src.get_absolute_path import resource_path

# Define paths for button images
VIEW_IMG_BTN = resource_path(r'src\assets\btn\view_img_btn.png')
DELETE_BTN = resource_path(r'src\assets\btn\delete_post_btn.png')
CANCEL_BTN = resource_path(r'src\assets\btn\cancel_btn.png')
EDIT_BTN = resource_path(r'src\assets\btn\edit_btn.png')
OK_BTN = resource_path(r'src\assets\btn\ok_btn.png')
SAVE_BTN = resource_path(r'src\assets\btn\save_btn.png')
ADD_CANDIDATES_LG_BTN = resource_path(r'src\assets\btn\add_candidates_lg_btn.png')
ADD_POST_BTN = resource_path(r'src\assets\btn\add_post_btn.png')
START_ELECTION_BTN = resource_path(r'src\assets\btn\start_election_btn.png')
AVAILABLE_RESULTS_BTN = resource_path(r'src\assets\btn\available_results_btn.png')
DEL_CANDIDATE_BTN = resource_path(r'src\assets\btn\delete_candidate_btn.png')
ADD_CANDIDATES_BTN = resource_path(r'src\assets\btn\add_candidates_btn.png')

# Define colors
GREY = '#E2E2E2'
DARK_GREY = '#F5F5F5'
RED = '#D33030'

conn = connect(resource_path(r'src\election.db')) # Connect to the SQLite database
cursor = conn.cursor()

SCREEN_WIDTH, SCREEN_HEIGHT = sg.Window.get_screen_size() # Get the screen width and height
CANDIDATE_IMG_SIZE = (400, 400)

added_posts_heading = []

available_results = []
rm_candidates_posts = {} # Posts whose candidates have been removed


def get_available_results():
    """
    Retrieve all available results from the local 'results' directory,
    creating the directory if it does not already exist.
    """
    global available_results
    if os.path.exists(resource_path(r'src\results')) == False:
        os.makedirs(resource_path(r'src\results'))
    
    src_dirs = os.listdir(resource_path(r'src\results'))
    available_results = [i.split('-',1)[1] for i in src_dirs if i.startswith('result-')]  # Add the name of available election result


def display_candidate_info(candidate_details:tuple, post_name:str, key_val:int):
    """
    Args:
        candidate_details (tuple): Stores the information of individual candidate as (name,image)
    """
    col_layout = [sg.Input(candidate_details[0],key=f'{post_name}-name-{key_val}',expand_y=True,disabled=True,size=(30),pad=((12,0),(4, 4)),text_color='#595D62'),
                    sg.Input(resource_path(candidate_details[1]),key=f'{post_name}-image-{key_val}',expand_y=True,disabled=True,size=(30),pad=(8,4),text_color='#595D62'),
                    sg.Image(VIEW_IMG_BTN,enable_events=True,key=f'{post_name}-view-image-{key_val}',pad=((0,8),(4, 4)),background_color='#FFFFFF'),
                    sg.FileBrowse('   Browse Image   ', key=f'{post_name}-image-button-{key_val}',target=f'{post_name}-image-{key_val}',file_types=(("Image Files", "*.png;*.jpg;*.jpeg;*.webp"),),disabled=True,button_color=f'{DARK_GREY} on {GREY}',pad=((0,12),(4, 4)),expand_y=True,font=(None,9,'bold')),
                    sg.Image(DEL_CANDIDATE_BTN,enable_events=True,key=f'del-{post_name}-{key_val}',background_color='#FFFFFF',tooltip='Remove the candidate')
                    ]
    return col_layout


def style_added_posts(post_name:str, posts_layout:list):
    """
    Create the layout for displaying a post's details.

    Args:
        post_name (str): The name of the post.
        posts_layout (list): The layout to which the post's details will be added.

    Returns:
        list: The updated layout including the post's details.
    """
    cursor.execute(f'SELECT name,image FROM "{post_name}"')
    post_data = cursor.fetchall()

    # Layout for each post entry
    post_layout = [[sg.Text(post_name,font=(None,12,'bold'),pad=((12,0),(12, 8)),background_color='#FFFFFF'),
                    sg.Push(background_color='#FFFFFF'),sg.Image(ADD_CANDIDATES_BTN,enable_events=True,key=f'add-more-candidates-{post_name}',pad=((0,8),(12, 5))),
                    sg.Image(EDIT_BTN,enable_events=True,key=f'edit-{post_name}',pad=((0,8),(12, 5)),metadata='Edit'),
                    sg.pin(sg.Image(CANCEL_BTN,enable_events=True,key=f'cancel-{post_name}',background_color='#FFFFFF',pad=((0,8),(12, 5)),visible=False)),
                    sg.Image(DELETE_BTN,enable_events=True,key=f'delete-{post_name}',pad=((0,12),(12, 5)),tooltip=f'Delete {post_name} post')]] 

    key_val = 1
    for i in post_data:
        # Input fields for post name, image and browse button
        post_layout.append([sg.pin(sg.Column([display_candidate_info(i,post_name,key_val)],background_color='#FFFFFF',key=f'{post_name}-{key_val}'),shrink=True)])
        key_val+=1
    posts_layout.append([sg.pin(sg.Column(post_layout,pad=(5,10),key=f'{post_name}_container',background_color='#FFFFFF'))])
    posts_layout.append([sg.Text('',size=(0,1),font=(None,7))])
    return posts_layout


# Function to load existing posts from the database
def load_posts(main_layout:list):
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
            load_posts_layout = style_added_posts(post_name,load_posts_layout)

    header_layout = [[sg.Text('Admin │ EasyPolls',text_color='#4E46B4',font=(None,15,'bold'),pad=(12,12)),sg.Push(),
                      sg.Image(AVAILABLE_RESULTS_BTN,key='check-results',visible=bool(available_results),enable_events=True),
                      sg.Image(START_ELECTION_BTN,key='start-elections-btn',visible=bool(tables),enable_events=True)]]

    main_layout.insert(0,[sg.Frame('',header_layout,expand_x=True)])
    # Adding loaded posts to the main layout
    main_layout.append([sg.Column(load_posts_layout,key='posts-container',scrollable=True,vertical_scroll_only=True,expand_y=True,expand_x=True)])
    return main_layout


def error_popup(error_message:str,color=RED):
    """
    Display an error popup

    Args:
        error_message (str): The error message which needs to be displayed
        color (str): The color of the message. This popup can display both error messages, which are red,
                    and success messages, which are green.
    """
    error_popup = sg.Window(error_message,[[sg.Text(error_message,text_color=color,font=(None,11,'bold'))],
                                           [sg.Image(OK_BTN,key='ok-btn',enable_events=True)]],modal=True,finalize=True,resizable=True)
    error_popup.bind('<Return>','_Enter')
    while True:
        event, values = error_popup.read()
        if event =='_Enter' or event =='ok-btn':
            break
    error_popup.close()


def save_img(curr_path:str, img_path:str):
    """
    Save images to the local directory assets

    Args:
        curr_path (str): The path where the image is located currently
        img_path (str): The path where the image will be saved.
    """
    try:
        im = Image.open(curr_path)
        im.thumbnail(CANDIDATE_IMG_SIZE)  # Save the image in the resolution of 400 X 400 pixels
        im.save(img_path, format='png')  # Save as png
    except FileNotFoundError:
        print('Image file not found.')


def table_exists(table_name:str):
    """
    Check if a table with the given name exists in the database.

    Args:
        table_name (str): The name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{table_name}"')
    result = cursor.fetchone()
    return result is not None


def del_elements(elements:list, window:sg.Window):
    """
    Delete the elements from a window
    """
    for i in elements:
        del window.AllKeysDict[i]


def check_inputs_filled(element:sg.Window ,no_of_candidates:int, values:dict, post_name:str, 
                        action:str, window=None):
    """
    Validate inputs for creating or saving a post.

    Args:
        element (PySimpleGUI element): The element which displays the input fields.
        no_of_candidates (int): Number of candidates for the post.
        values (dict): Dictionary containing values from the GUI inputs.
        post_name (str): Name of the post.
        action (str): Action to perform ('create post' or 'save post' or 'add more candidates').
        window (PySimpleGUI Window): The main window which displays the main GUI. Required while saving a post.
    """
    all_inputs_filled = True
    candidate_details = []
    keys_dict = element.AllKeysDict

    # Collect candidate information and validate inputs
    for i in range(1, no_of_candidates + 1):
        if f'{post_name}-image-{i}' in keys_dict:
            candidate_image = values.get(f'{post_name}-image-{i}', '').strip()
            candidate_name = values.get(f'{post_name}-name-{i}', '').strip()
            
            # if candidate_name not in rm_candidates_posts[post_name]:
            if not candidate_image or not candidate_name or candidate_image=='Selected image\'s path will appear here.':
                all_inputs_filled = False
                error_popup('Please fill all inputs.')
                break
            # Add details only if the selected image exists.
            if os.path.exists(candidate_image):
                candidate_details.append((candidate_name, candidate_image))
            else:
                all_inputs_filled = False
                error_popup(f'The selected image for Candidate {candidate_name} does not exist.')
                break

    if all_inputs_filled == True:
        validate_modal_inputs(post_name, candidate_details, no_of_candidates, action, element, window)


def validate_modal_inputs(post_name:str, candidate_details:list[tuple], no_of_candidates:int,
                    action:str, element:sg.Window, window):
    """
    Validate the inputs present in the modal created while adding candidates.
    
    Args:
        post_name (str): The name of the post.
        candidate_details (list[tuple]): List of tuples containing candidate details (name, image_path).
        no_of_candidates (int): Total no of candidates.
    """
    new_names = [i[0] for i in candidate_details]
    new_img_names = [os.path.basename(i[1]).split('.',1)[0] for i in candidate_details]

    # Checking for duplicate names and images
    dup_names_exist = len(new_names) != len(set(new_names))
    dup_images_exist = len(new_img_names) != len(set(new_img_names))
        
    # Handling different validation scenarios
    if dup_names_exist:
        error_popup('Every name entered should be unique.')  
    elif dup_images_exist:
        # Show the candidates which have the same image name.
        for i in new_img_names:
            # List which stores the indices of the candidates with same img.
            lst = [f'{index+1}' for index, value in enumerate(new_img_names) if i==value]
            if len(lst)>1:
                error_popup(f'Candidates {', '.join(lst)} have the same image name.\nEvery image\'s name should be unique.')
                break
    elif action =='create post':
        create_table(post_name, candidate_details,window)
        element.close()
    elif action =='save post':
        save_edited_post(post_name, no_of_candidates,candidate_details, element)
    elif action =='add more candidates':
        img_same_name_exists, same_candidate_exists = validate_new_candidates(post_name, new_img_names,new_names)
        if img_same_name_exists==False and same_candidate_exists==False:
            add_more_candidates(post_name, candidate_details, window)
            element.close()
    else:
        print('An error occurred.')


def validate_new_candidates(post_name:str, new_img_names:list[str], new_names:list[str]) -> tuple:
    """
    Validate the candidates that the user is trying to add to an already existing post.
    
    Args:
        post_name (str): The name of the post.
        new_img_names (list[str]): List of the images of all the candidates the user is trying to add.
        new_names (list[str]): List of the names of all the candidates the user is trying to add.
    """
    img_same_name_exists = False
    same_candidate_exists = False
    
    cursor.execute(f'SELECT image FROM "{post_name}"')
    existing_img_name = [os.path.basename(i[0]).split('.',1)[0] for i in cursor.fetchall()]
    
    cursor.execute(f'SELECT name FROM "{post_name}"')
    existing_candidate_name = [i[0] for i in cursor.fetchall()]
    
    for i in range(len(new_img_names)):
        if new_img_names[i] in existing_img_name:
            img_same_name_exists = True
            # Candidate having the same image name.
            candidate_same_img = existing_candidate_name[existing_img_name.index(new_img_names[i])]
            error_popup(f'The image for {new_names[i]} matches an existing candidate {candidate_same_img}. Image names must be unique.')
            break
        if new_names[i] in existing_candidate_name:
            same_candidate_exists = True
            error_popup(f'The candidate with the name {new_names[i]} already exists. Candidate names must be unique.')
            break
    return img_same_name_exists,same_candidate_exists


# <======================================= EDIT & DELETE POST =======================================>


def delete_post(post_name:str, window:sg.Window):
    """
    Delete a post from the database and update the GUI.

    Args:
        post_name (str): The name of the post to delete.
        window (sg.Window): The window needed to update the GUI.
    """

    if sg.popup_yes_no(f'Are you sure you want to delete the post titled {post_name}?') == 'Yes':

        rmtree(resource_path(rf'src\assets\post_img\{post_name}'))
        window[f'{post_name}_container'].update(visible=False)

        del_elements([f'{post_name}_container', f'add-more-candidates-{post_name}', f'edit-{post_name}', f'cancel-{post_name}', f'delete-{post_name}'],
                    window)

        cursor.execute(f'SELECT MAX(id) FROM "{post_name}"')
        max_id = cursor.fetchone()[0]
        keys_dict = window.AllKeysDict
        for i in range(1,max_id+1):
            if f'{post_name}-name-{i}' in keys_dict:
                del_elements([f'{post_name}-{i}', f'{post_name}-name-{i}', f'{post_name}-image-{i}',
                              f'{post_name}-view-image-{i}', f'{post_name}-image-button-{i}', f'del-{post_name}-{i}'], window)

        cursor.execute(f'DROP TABLE "{post_name}";')
        conn.commit()
        
        other_posts_exist = False
        for key in window.AllKeysDict:
            if key.endswith('_container') and key!=f'{post_name}_container':
                other_posts_exist = True
                break
        if not other_posts_exist:
            window['start-elections-btn'].update(visible=False)
            window['added_posts_heading'].update(visible=False)
        if post_name in rm_candidates_posts:
            del rm_candidates_posts[post_name]
        window.refresh()
        window['posts-container'].contents_changed()


def add_more_candidates(post_name : str, candidates_info:list, window:sg.Window):
    """
    Add more candidates to an already existing post.

    Args:
        post_name (str): The name of the post.
        candidates_info (list): List of tuples containing candidate information (name, image_path).
        window (PySimpleGUI window): The main GUI window.
    """
    cursor.execute(f'SELECT MAX(id) FROM "{post_name}"')
    key_val = cursor.fetchone()[0] + 1
    key_val_2 = key_val
    base_img_names = []

    post_img_path = rf'src\assets\post_img\{post_name}'
    
    # Copy candidate images to the directory and insert candidate info into the table
    for candidate in candidates_info:
        base_image_name = os.path.basename(candidate[1])
        base_img_names.append(base_image_name.split('.')[0]+'.png')

        image_name = f'{os.path.splitext(base_image_name)[0]}.png'
        image_path = rf'{post_img_path}\{image_name}'
        save_img(candidate[1],image_path)

        cursor.execute(f'INSERT INTO "{post_name}" (id,name, image) VALUES (?,?,?)', (key_val_2,candidate[0], image_path))
        if post_name in rm_candidates_posts:
            if candidate[0] in rm_candidates_posts[post_name]:
                rm_candidates_posts[post_name].remove(candidate[0])
        key_val_2+=1
    
    # Commit the changes to the database
    conn.commit()

    # Updating GUI
    post_layout = []
    
    for i in candidates_info:
        saved_img_path = post_img_path + rf'\{base_img_names[candidates_info.index(i)]}'
        # Input fields for post name, image and browse button
        post_layout.append([sg.pin(sg.Column([display_candidate_info((i[0],saved_img_path),post_name,key_val)],background_color='#FFFFFF',key=f'{post_name}-{key_val}'))])
        key_val+=1
    window.extend_layout(window[f'{post_name}_container'],post_layout)


def save_edited_post(post_name:str, max_id:int, candidates_info:list, window:sg.Window):
    '''
    Update the entries in the specified post table with new candidate information.

    Args:
        post_name (str): Name of the post table to update.
        max_id (int): Maximum ID of entries in the post table.
        candidates_info (list): List of tuples containing candidate information (name, image_path).
        window: PySimpleGUI window object to interact with GUI elements.
    '''

    window[f'edit-{post_name}'].metadata = 'Edit'
    window[f'edit-{post_name}'].update(EDIT_BTN)
    save_post_query = f"""
        UPDATE "{post_name}"
        SET name = ?,image= ?
        WHERE id = ? AND (name != ? OR image != ?);
    """
    post_img_path = rf'src\assets\post_img\{post_name}'
    cursor.execute(f'SELECT id FROM "{post_name}"')
    all_ids = [i[0] for i in cursor.fetchall()]
    all_ids.sort()
    curr_id = all_ids[0]
    if post_name in rm_candidates_posts:
        for i in candidates_info:
            if i[0] in rm_candidates_posts[post_name]:
                candidates_info.remove(i)

    for candidate in candidates_info:

        cursor.execute(f'SELECT image FROM "{post_name}" WHERE id={curr_id}')
        prev_image_path = cursor.fetchone()[0]
        
        base_image_name = os.path.basename(candidate[1])
        image_name = f'{os.path.splitext(base_image_name)[0]}.png'
        image_path = rf'{post_img_path}\{image_name}' 
        
        window[f'{post_name}-image-{curr_id}'].update(f'{resource_path(image_path)}')
        cursor.execute(save_post_query,(candidate[0],image_path,curr_id,candidate[0],image_path))

        if(candidate[1]!=prev_image_path):
            save_img(candidate[1],image_path)

        curr_id_index = all_ids.index(curr_id)
        if curr_id_index != len(all_ids)-1:
            curr_id = all_ids[curr_id_index+1]
    
    conn.commit()
    window[f'cancel-{post_name}'].update(visible=False)
    cursor.execute(f'SELECT image FROM "{post_name}"')
    all_img_name = [os.path.basename(i[0]) for i in cursor.fetchall()]

    for i in os.listdir(post_img_path):
        if(i not in all_img_name):
            try:
                remove_file = os.path.join(post_img_path,i)  # Remove unused images.
                os.remove(resource_path(remove_file))
            except FileNotFoundError:
                print('save_edited_post() -> Error in removing image.')

    keys_dict = window.AllKeysDict
    for i in range(1,max_id+1):
        if f'{post_name}-name-{i}' in keys_dict:
            cursor.execute(f'SELECT name, image FROM "{post_name}" WHERE id={i}')
            name, image = cursor.fetchone()
            window[f'{post_name}-name-{i}'].update(name,disabled=True) 
            window[f'{post_name}-image-button-{i}'].update(disabled=True,button_color=f'{DARK_GREY} on {GREY}')
            window[f'{post_name}-image-{i}'].update(resource_path(image))


def edit_post(post_name:str, window:sg.Window):
    """
    Enable editing of candidate information for a post.

    Args:
        post_name (str): The name of the post.
        window (PySimpleGUI window): The main GUI window.
    """
    window[f'edit-{post_name}'].metadata = 'Save'
    window[f'edit-{post_name}'].update(SAVE_BTN)
    cursor.execute(f'SELECT MAX(id) FROM "{post_name}";')
    max_id = cursor.fetchone()[0]

    window[f'cancel-{post_name}'].update(visible=True)
    keys_dict = window.AllKeysDict
    setfocus = False
    for i in range(1,max_id+1):
        if f'{post_name}-name-{i}' in keys_dict:
            window[f'{post_name}-name-{i}'].update(disabled=False,background_color='#EBEBEB')  # Enable candidate name input fields
            window[f'{post_name}-image-button-{i}'].update(disabled=False,button_color = '#FFFFFF on #4E46B4')  # Enable browse buttons for candidate images
            if setfocus == False:
                curr_content = window[f'{post_name}-name-{i}'].get()
                window[f'{post_name}-name-{i}'].update('')
                window[f'{post_name}-name-{i}'].set_focus()
                window[f'{post_name}-name-{i}'].update(curr_content)
                setfocus = True


def del_candidate(event:str, window:sg.Window):
    """
    Delete an individual candidate from a post.

    Args:
        event (str): The key of the delete button.
        window (PySimpleGUI window): The main GUI window.
    """
    info_list = event.split('-')
    post_name = info_list[1]
    if window[f'edit-{post_name}'].metadata == 'Edit':
        candidate_id = info_list[2]
        cursor.execute(f'SELECT name FROM "{post_name}" WHERE id={candidate_id}')
        candidate_name = cursor.fetchone()[0]
        avail_candidates = [i for i in window.AllKeysDict if i.startswith(f'del-{post_name}') and i!=f'del-{post_name}-{candidate_id}']
        
        if len(avail_candidates)==1:
            confirm = sg.PopupYesNo(f'With two candidates left, removing {candidate_name} will delete the post {post_name}. Would you like to continue?')
            if confirm=='Yes':
                delete_post(post_name,window)
        
        else:
            confirm = sg.PopupYesNo(f'Are you sure you want to remove {candidate_name} from the post {post_name}?')
            if confirm=='Yes':
                cursor.execute(f'SELECT image FROM "{post_name}" WHERE id={candidate_id}')
                image_path = resource_path(cursor.fetchone()[0])

                try:
                    os.remove(image_path)
                except FileNotFoundError:
                    print('save_edited_post() -> Error in removing image.')

                cursor.execute(f'DELETE FROM "{post_name}" WHERE id={candidate_id}')
                conn.commit()
                window[f'{post_name}-{candidate_id}'].update(visible=False)

                del_elements_list = [f'{post_name}-{candidate_id}', f'{post_name}-name-{candidate_id}', 
                                     f'{post_name}-image-{candidate_id}', f'{post_name}-view-image-{candidate_id}',
                                     f'{post_name}-image-button-{candidate_id}', f'del-{post_name}-{candidate_id}']
                del_elements(del_elements_list, window)

                window.refresh()
                if post_name in rm_candidates_posts:
                    rm_candidates_posts[post_name].append(candidate_name)
                else:
                    rm_candidates_posts[post_name] = [candidate_name,]
    else:
        error_popup('Delete operation is not available while in edit mode.')


def cancel_edit(event:str, window:sg.Window):
    """
    Cancel editing the post and revert any changes.

    Args:
        event (str): The key of the cancel button.
        window (PySimpleGUI window): The main GUI window.
    """
    postname = event.split('-')[1]

    cursor.execute(f'SELECT name,image FROM "{postname}"')
    post_data = cursor.fetchall()
                
    cursor.execute(f'SELECT id FROM "{postname}"')
    all_ids = [i[0] for i in cursor.fetchall()]
    all_ids.sort()
    curr_id = all_ids[0]

    for i in post_data:
        window[f'{postname}-name-{curr_id}'].update(i[0]) 
        window[f'{postname}-image-{curr_id}'].update(resource_path(i[1]))
        curr_id_index = all_ids.index(curr_id)
        if curr_id_index != len(all_ids)-1:
            curr_id = all_ids[curr_id_index+1]

    for i in all_ids:
        window[f'{postname}-name-{i}'].update(disabled=True) 
        window[f'{postname}-image-button-{i}'].update(disabled=True,button_color='#e8e8e8 on #f2f2f2')  
    window[f'edit-{postname}'].metadata = 'Edit' 
    window[f'edit-{postname}'].update(EDIT_BTN) 
    window[event].update(visible=False) 


# <================================= CREATE NEW POST ====================================>


def create_table(post_name:str, candidate_details:list, window:sg.Window):
    """
    Create a table for the given post name and insert candidate information into the table.

    Args:
        post_name (str): The name of the post.
        candidate_details (list): A list of tuples containing candidate names and image paths.
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
    post_img_path = rf'src\assets\post_img\{post_name}'
    os.makedirs(post_img_path)
    
    # Copy candidate images to the directory and insert candidate info into the table
    for candidate in candidate_details:
        base_image_name = os.path.basename(candidate[1])
        image_name = f'{os.path.splitext(base_image_name)[0]}.png'
        image_path = rf'{post_img_path}\{image_name}'
        save_img(candidate[1],image_path)
        cursor.execute(f'INSERT INTO "{post_name}" (name, image) VALUES (?,?)', (candidate[0], image_path))
    
    # Commit the changes to the database
    conn.commit()
    post_layout = style_added_posts(post_name,[])
    posts_heading_exists = window.find_element('added_posts_heading', silent_on_error=True)

    if not posts_heading_exists:
        post_layout.insert(0,added_posts_heading)

    window['added_posts_heading'].update(visible=True)
    window['start-elections-btn'].update(visible=True)
    window.extend_layout(window['posts-container'],post_layout)
    window.refresh()
    window['posts-container'].contents_changed()


def create_post_modal(post_name:str, no_of_candidates:int, window:sg.Window, action='create post'):
    """
    Create and display a modal window to collect candidate information.

    Args:
        post_name (str): The name of the post.
        no_of_candidates (int): The number of candidates.
        window (PySimpleGUI element): Used to update the UI with new posts.
        action (str): The action function is called to perform ('create post', 'add more candidates') 
    """

    post_modal_layout = [[sg.Text('Provide Candidate Information:',font=(None,15,'bold'),pad=(10,10))]]
    column_layout = []

    # Create input fields for each candidate's name and image
    for i in range(1, no_of_candidates + 1):
        candidate_layout = [sg.Column([[
            sg.Text(f'Candidate {i}: ',pad=((0,10),(11,11))), 
            sg.Input(key=f'{post_name}-name-{i}',expand_y=True, size=(40)), 
            sg.Input('Selected image\'s path will appear here.',key=f'{post_name}-image-{i}', disabled=True, text_color='#595D62', size=(25),expand_y=True),
            sg.FileBrowse('   Browse Image   ', file_types=(("Image Files", "*.png;*.jpg;*.jpeg;*.webp"),),font=(None,9,'bold'),expand_y=True)
        ]])]
        column_layout.append(candidate_layout) 

    column_layout.extend([[sg.Text('',size=(0,1),font=(None,2))],[sg.Image(ADD_POST_BTN if action=='create post' else ADD_CANDIDATES_LG_BTN, key=f'{post_name}-save-btn',pad=(5,5),enable_events=True)]]) 
    post_modal_layout.append([sg.Column(column_layout,vertical_scroll_only=True,scrollable=True,expand_x=True,expand_y=True)]) # type: ignore
    
    # Create and display the modal window
    post_modal = sg.Window(f'Add candidates for the post {post_name}  •  EasyPolls  •  Made by Raghav Srivastava (GitHub: raghavsrvt)',
                           post_modal_layout, size=(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 120), resizable=True,modal=True,finalize=True)
    post_modal[f'{post_name}-name-1'].set_focus()

    while True:
        event, values = post_modal.read() 
        if event != sg.WIN_CLOSED:
            if event == f'{post_name}-save-btn':
                check_inputs_filled(post_modal, no_of_candidates, values, post_name, action, window)
        else:
            break


# Start Election
def start_election():
    global available_results
    election_name = sg.popup_get_text('Name the Election',modal=True)
    if election_name:
        election_name = election_name.strip()
        if f'{election_name}.db' in available_results:
            error_popup(f"A result with this election name already exists. Please choose a different name or delete the existing '{election_name}' result.")

        elif election_name.replace(' ','').replace('-','').replace('_','').isalnum()==False:
            error_popup('Election name can only contain alphabets, digits and special characters \'-\' & \'_\'.')

        elif f'{election_name}.db' not in available_results:
            from src.password_functions import display_password_window
            passwd_correct = display_password_window()[0]

            if passwd_correct:
                cursor.execute('UPDATE user_data SET election_status = 1;')
                cursor.execute('UPDATE user_data SET election_name =(?)',(election_name,))
                conn.commit()
                return election_name.strip()
            

def view_image(post_name:str, image_path:str, window:sg.Window):
    """
    View image of the added candidate

    Args:
        post_name (str): The name of the post.
        image_path (str): The path of the image.
        window (PySimpleGUI window): The main GUI window.
    """
    img_exists = True
    # If in edit mode then save image in 400X400 resolution to not crop the image.
    if window[f'edit-{post_name}'].metadata == 'Save':
        try:
            im = Image.open(image_path)
            im.thumbnail(CANDIDATE_IMG_SIZE)
            bytesio = BytesIO()
            im.save(bytesio,format='png')
            image_view_layout = [[sg.Push(),sg.Image(data=bytesio.getvalue(),key='view-image'),sg.Push()]]
        except FileNotFoundError:
            img_exists = False
            error_popup('The image you tried to view does not exist.')
    else:
        image_view_layout = [[sg.Push(),sg.Image(image_path,key='view-image'),sg.Push()]]

    if img_exists:
        image_view_window = sg.Window('View image',image_view_layout,size=(400,400),element_justification='center', modal=True)

        while True:
            event,values = image_view_window.read() 
            if event == sg.WIN_CLOSED:
                break

        image_view_window.close()


def validate_post_name(post_name:str, window:sg.Window, values:dict):
    """
    Validate post name

    Args:
        post_name (str): The name of the post.
        window (PySimpleGUI window): The main GUI window.
        values (dict): The values retreived from the window.read() function.
    """
    if post_name == '' or post_name.isspace():
        error_popup("Post name can't be empty")  
    elif post_name[0].isalpha()==False:
        error_popup('Post name must start with a letter.')
    elif post_name.replace(' ','').replace('_','').isalnum()==False:
        error_popup('Post name can only contain alphabets, digits and special character \'_\'.')
    elif table_exists(post_name):
        error_popup('Post with this name already exists.')  
    else:
        try:
            no_of_candidates = int(values['no-of-candidates'].strip())
            if no_of_candidates < 2:
                raise ValueError("No. of candidates < 2")
            window['post-name'].update('')
            window['no-of-candidates'].update('')
            window['post-name'].set_focus()
            create_post_modal(post_name, no_of_candidates,window)
        except ValueError:
            error_popup('No. of candidates should at least be 2.')


def change_id():
    """
    Update the post IDs for candidates who have been deleted to ensure that all IDs are sequential.
    """
    if rm_candidates_posts:
        for i in rm_candidates_posts:
            cursor.execute(f'SELECT id FROM "{i}"')
            existing_ids = [j[0] for j in cursor.fetchall()]
            # Assign temporary IDs to avoid conflicts
            for k in range(len(existing_ids)):
                temp_id = -(k + 1)  # Assign a negative temporary ID
                cursor.execute(f'UPDATE "{i}" SET id=? WHERE id=?', (temp_id, existing_ids[k]))

            # Assign new final IDs
            for k in range(len(existing_ids)):
                new_id = k + 1
                temp_id = -(k + 1)  # The same negative temporary ID
                cursor.execute(f'UPDATE "{i}" SET id=? WHERE id=?', (new_id, temp_id))
    conn.commit()

# <======================================== DISPLAY THE ADMIN PANEL ===================================>

def display_admin_panel():
    """
    Display the main admin panel window to add new posts and candidates.
    """
    global added_posts_heading, available_results

    added_posts_heading = [sg.Text('Added Posts:',font=(None,15,'bold'),pad=((10,0),(10,15)),key='added_posts_heading')]
    layout = [[sg.Text('',size=(0,1),font=(None,6))],
              [sg.Text('Create Post:',font=(None,15,'bold'),pad=((9,0),(16,10)))],
            [sg.Column([[sg.Text('Post name: ',pad=(0,11)), sg.Input(key='post-name',size=(40,50),expand_y=True,expand_x=True)],
                        [sg.Text('No of candidates: ',pad=(0,11)), sg.Input(key='no-of-candidates',size=(40,50),expand_y=True)]],pad=(9,0))],
            [sg.Image(ADD_CANDIDATES_LG_BTN, key='add-candidates-btn',pad=(9,10),enable_events=True)],
            [sg.Text('',size=(0,1),font=(None,6))]]

    layout = load_posts(layout)
    window = sg.Window('Admin  •  EasyPolls  •  Made by Raghav Srivastava (GitHub: raghavsrvt)', layout, size=(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 120), resizable=True,finalize=True)
    
    window['post-name'].bind("<Return>", "_Enter")
    window['no-of-candidates'].bind("<Return>", "_Enter")
    window['post-name'].set_focus()

    while True:

        event, values = window.read()
        if event != sg.WIN_CLOSED:
            if event == 'add-candidates-btn' or event=='post-name_Enter' or event=='no-of-candidates_Enter':
                post_name = values['post-name'].strip()
                validate_post_name(post_name, window, values)

            # Edit post
            elif event.startswith('edit-') and window[event].metadata == 'Edit':
                edit_post(event.partition('-')[2],window)

            # Save edited post
            elif event.startswith('edit-') and window[event].metadata == 'Save': 
                post_being_edited = event.partition('-')[2]
                cursor.execute(f'SELECT MAX(id) FROM "{post_being_edited}";')
                max_id = cursor.fetchone()[0]
                check_inputs_filled(window,max_id,values,post_being_edited,'save post')
                
            # Cancel changes
            elif event.startswith('cancel-'):
                cancel_edit(event, window)

            # Delete a post
            elif event.startswith('delete-'):
                delete_post(event.partition('-')[2],window)

            # View image:
            elif 'view-image' in event:
                l = event.split('-')
                postname,key_val = l[0],l[3]
                image_path = values[f'{postname}-image-{key_val}']
                view_image(postname,image_path,window)
            
            #Remove candidate's info
            elif event.startswith('del-'):
                del_candidate(event,window)

            # Add more candidates to existing post
            elif event.startswith('add-more-candidates'):
                post_name = event.split('-')[3]
                if window[f'edit-{post_name}'].metadata == 'Edit':
                    try:
                        num_candidates = sg.PopupGetText('Enter the no. of candidates you would like to add')
                        if num_candidates:
                            num_candidates=int(num_candidates)
                            if num_candidates<1:
                                raise ValueError('No. of candidates should at least be 1.')
                            else:
                                create_post_modal(post_name, num_candidates, window, action='add more candidates')
                    except ValueError:
                        error_popup('No. of candidates should be at least 1.')
                else:
                    error_popup('Can\'t add more candidates while in edit mode.')

            # Start Elections:
            elif event=='start-elections-btn':
                election_name = start_election()
                if election_name:
                    change_id()
                    window.close()

                    from src.e_voting import display_voting_panel
                    display_voting_panel(election_name)
            
            # Check results
            elif event=='check-results':
                from src.results import display_results
                display_results(available_results)
                get_available_results()
                if not available_results:
                    window[event].update(visible=False)
        else:
            break
    change_id()
    window.close()