import PySimpleGUI as sg
from sqlite3 import connect

from src.get_absolute_path import resource_path
from os import remove as rm_file
from pandas import ExcelWriter, read_sql_query

DELETE_BTN = resource_path(r'src\assets\btn\delete_secondary_btn.png')
DOWNLOAD_BTN = resource_path(r'src\assets\btn\download_btn.png')
OK_BTN = resource_path(r'src\assets\btn\ok_btn.png')
RED = '#D33030'

def error_popup(error_message:str,color=RED):
    error_popup = sg.Window(error_message,[[sg.Text(error_message,text_color=color,font=(None,11,'bold'))],
                                           [sg.Image(OK_BTN,key='ok-btn',enable_events=True)]],modal=True,finalize=True,resizable=True)
    error_popup.bind('<Return>','_Enter')
    while True:
        event, values = error_popup.read()
        if event =='_Enter' or event =='ok-btn':
            break
    error_popup.close()


# To fix column expand problem
def configure_canvas(event, canvas, frame_id):
    canvas.itemconfig(frame_id, width=canvas.winfo_width())


def configure_frame(event, canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))


def download_result(cursor_result, conn_result, result_name:str):
    output_file_path = sg.PopupGetFolder('Please select the destination folder to save the result as an Excel file.',modal=True)
                
    if output_file_path:
        cursor_result.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor_result.fetchall()
        tables.remove(('sqlite_sequence',))
                            
        try:

            with ExcelWriter(rf'{output_file_path}\result-{result_name}.xlsx') as writer:
                for i in tables:
                    download_query = f'SELECT name, votes FROM "{i[0]}"'
                    df = read_sql_query(download_query,conn_result)  # Get dataframe
                    df.to_excel(writer, sheet_name=i[0], index=False)  # Write new data on the file
            error_popup('Saved the result successfully!','#2E7D32')

        except OSError:  # If the selected path doesn't exsist
            error_popup('Cannot save file into a non-existent directory.')


def get_result_layout(posts_for_result:list, cursor_result):
    result_layout = []
    for i in posts_for_result:

        cursor_result.execute(f'SELECT name,votes FROM "{i[0]}"')
        curr_post_data = cursor_result.fetchall()

        cursor_result.execute(f'SELECT MAX(votes) FROM "{i[0]}"')
        max_votes = cursor_result.fetchone()[0]

        candidate_result_layout = [[sg.Text('',size=(0,1),font=(None,2),background_color='#FFFFFF')],[sg.Text(f'Post: {i[0]}',font=(None,13,'bold'),pad=(20,10),background_color='#FFFFFF')]]  # Layout that will contain the results of candidates
                    
        for j in curr_post_data:

            # Statements to highlight winner and to display vote/votes
            if j[1]==1 and j[1]==max_votes:
                vote_text = sg.Text(f'{j[0]} ({j[1]} Vote)',background_color='#FFFFFF', pad=((20,5),(10,0)))
                bar_color = ('#4E46B4','#4E46B4')
            elif j[1]==max_votes:
                vote_text = sg.Text(f'{j[0]} ({j[1]} Votes)',background_color='#FFFFFF', pad=((20,5),(10,0)))
                bar_color = ('#4E46B4','#4E46B4')
            elif j[1]==1:
                vote_text = sg.Text(f'{j[0]} ({j[1]} Vote)',background_color='#FFFFFF', pad=((20,5),(10,0)))
                bar_color = ('#E2E2E2','#E2E2E2')
            else:
                vote_text = sg.Text(f'{j[0]} ({j[1]} Votes)',background_color='#FFFFFF', pad=((20,5),(10,0)))
                bar_color = ('#E2E2E2','#E2E2E2')
                        
            candidate_result_layout.extend([[vote_text],[sg.ProgressBar(j[1],size=(j[1]*0.2,6),bar_color=bar_color,pad=((20,0),(2,0)))]])

        candidate_result_layout.extend([[sg.Text('',size=(0,1),font=(None,7),background_color='#FFFFFF')]])
        result_layout.append([sg.Column(candidate_result_layout,expand_x=True,background_color='#FFFFFF',pad=(10,10))])
    return result_layout


def show_result_window(result_name:str):
    
    conn_result = connect(resource_path(rf'src\results\result-{result_name}.db'))
    cursor_result = conn_result.cursor()

    cursor_result.execute('SELECT name FROM sqlite_master WHERE type="table"')
    posts_for_result = cursor_result.fetchall()
    posts_for_result.remove(('sqlite_sequence',))
    cursor_result.execute(f'SELECT SUM(votes) FROM "{posts_for_result[0][0]}"')
    tot_votes = cursor_result.fetchone()[0]
    result_layout = get_result_layout(posts_for_result, cursor_result)
    result_header = [sg.Frame('',[[sg.Text(f'{result_name} Results',text_color='#4E46B4',font=(None,15,'bold'),pad=(15,10)),
                                           sg.Push(),sg.Text(f'Total Votes: {tot_votes}',pad=(15,10)),sg.Image(DOWNLOAD_BTN,enable_events=True,key=f'download-result',pad=((10,10),(5,5)))]],expand_x=True)]

    show_results_window = sg.Window(f'{result_name} Election Results  •  EasyPolls  •  Made by Raghav Srivastava (GitHub: raghavsrvt)',
                                    [result_header,[sg.Text('',size=(0,1),font=(None,5))],
                                    [sg.Column(result_layout,expand_y=True,expand_x=True,scrollable=True,vertical_scroll_only=True, key='result_container')]],
                                    size=(550,500),resizable=True,modal=True,finalize=True)
    show_results_window.Finalize()
    show_results_window.Maximize()
                
    # Code to fix columns in result_layout not expanding
    column = show_results_window['result_container'].widget
    frame_id, frame, canvas = column.frame_id, column.TKFrame, column.canvas
    canvas.bind("<Configure>", lambda event, canvas=canvas, frame_id=frame_id:configure_canvas(event, canvas, frame_id))
    frame.bind("<Configure>", lambda event, canvas=canvas:configure_frame(event, canvas))
    show_results_window.set_size((550, 200))
    show_results_window.refresh()
    show_results_window.move_to_center()

    while True:
        event, values = show_results_window.read() 

        if event==sg.WIN_CLOSED:
            conn_result.close()
            conn_result = None
            break

        # Downloading a result
        elif event=='download-result':    
            # Get the folder where the result excel file will be saved.
            download_result(cursor_result,conn_result,result_name)
    show_results_window.close()


def delete_result(result_event:str, results_window:sg.Window):
    file_name = result_event.split('-',1)[1]
    result_name = file_name.split('.',1)[0]
    file_path = resource_path(rf'src\results\result-{file_name}')
    rm_file(file_path)
    results_window[f'{result_name}-container'].update(visible=False)
    results_window[result_event].update(visible=False)
    results_window[f'link-{file_name}'].update(visible=False)
    del results_window.AllKeysDict[result_event]
    del results_window.AllKeysDict[f'link-{file_name}']
    del results_window.AllKeysDict[f'{result_name}-container']


def display_results(available_results):
    """
    Display the available election results.

    Parameters:
    - available_results (list): List of available results.
    """
    results_layout = [[sg.Text('Results available: ',font=(None,15,'bold'),pad=(10,10))]]
    temp_layout = []  # layout for column

    for i in available_results:
        result_name = i.split('.')[0]
        temp_layout.extend([[sg.pin(sg.Column([[sg.pin(sg.Text(result_name,pad=(10,5),key=f'link-{i}',font=(None,12,'underline'),enable_events=True,text_color='#4E46B4'),shrink=True),sg.Push(),sg.pin(sg.Image(DELETE_BTN,enable_events=True,key=f'delete-{i}',pad=(10,5)),shrink=True)]], key=f'{result_name}-container',expand_x=True),shrink=True)]])

    results_layout.append([sg.Column(temp_layout, scrollable=True, vertical_scroll_only=True,expand_x=True,expand_y=True)]) 
    results_window = sg.Window('Review Election Results', results_layout,size=(500,300),resizable=True,modal=True)

    while True:
        result_event, result_value = results_window.read() 
        if result_event!=sg.WIN_CLOSED:

            # If opening a result
            if result_event.startswith('link'):
                result_name = results_window[result_event].get()
                show_result_window(result_name)

            # If deleting a result
            elif result_event.startswith('delete'):
                delete_result(result_event,results_window)
                other_links_exist = False
                for i in results_window.key_dict:
                    if i.startswith('link'):
                        other_links_exist = True
                        break
                if other_links_exist == False:
                    results_layout = []
                    break
        else:
            results_layout = []
            break
    results_window.close()