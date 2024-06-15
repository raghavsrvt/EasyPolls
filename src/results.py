import sqlite3, PySimpleGUI as sg
from src.set_theme import set_theme
from src.get_absolute_path import resource_path
from os import remove
set_theme()
screen_width, screen_height = sg.Window.get_screen_size()
delete_btn = resource_path('src\\assets\\btn\\delete_secondary_btn.png')

# To fix column expand problem
def configure_canvas(event, canvas, frame_id):
    canvas.itemconfig(frame_id, width=canvas.winfo_width())

def configure_frame(event, canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

def display_results(available_results):
    """
    Display the available election results.

    Parameters:
    - available_results (list): List of available results.
    """
    results_layout = [[sg.Text('Results available: ',font=(None,18,'bold'),pad=(10,10))]]
    temp_layout = [] # layout for column
    for i in available_results:
        temp_layout.extend([[sg.pin(sg.Text(i.split('.')[0],pad=(10,5),key=f'link-{i}',font=(None,14,'underline'),enable_events=True,text_color='#4E46B4'),shrink=True),sg.Push(),sg.pin(sg.Image(delete_btn,enable_events=True,key=f'delete-{i}',pad=(10,5)),shrink=True)]]) 
    results_layout.append([sg.Column(temp_layout, scrollable=True, vertical_scroll_only=True,expand_x=True,expand_y=True)]) 
    results_window = sg.Window('Review Election Results', results_layout,size=(500,300),resizable=True)

    while True:
        result_event, result_value = results_window.read() 
        if result_event!=sg.WIN_CLOSED:

            # If opening a result
            if result_event.startswith('link'):
                result_layout = []
                result_name = results_window[result_event].get()
                conn_result = sqlite3.connect(resource_path(f'src\\results\\result-{result_name}.db'))
                cursor_result = conn_result.cursor()
                cursor_result.execute('SELECT name FROM sqlite_master WHERE type="table"')
                posts_for_result = cursor_result.fetchall()
                if ('sqlite_sequence',) in posts_for_result:
                    posts_for_result.remove(('sqlite_sequence',))
                for i in posts_for_result:
                    cursor_result.execute(f'SELECT name,votes FROM {i[0]}')
                    curr_post_data = cursor_result.fetchall()
                    cursor_result.execute(f'SELECT MAX(votes) FROM {i[0]}')
                    max_votes = cursor_result.fetchone()[0]
                    candidate_result_leyout = [[sg.Text(f'Post: {i[0]}',font=(None,18,'bold'),pad=(10,10),background_color='#FFFFFF')]] # Layout that will contain the results of candidates
                    for j in curr_post_data:

                        # Statements to highlight winner and to display vote/votes
                        if j[1]==1 and j[1]==max_votes:
                            vote_text = sg.Text(f'{j[0]} ({j[1]} Vote)',background_color='#FFFFFF', pad=((10,5),(10,0)))
                            bar_color = ('#4E46B4','#4E46B4')
                        elif j[1]==max_votes:
                            vote_text = sg.Text(f'{j[0]} ({j[1]} Votes)',background_color='#FFFFFF', pad=((10,5),(10,0)))
                            bar_color = ('#4E46B4','#4E46B4')
                        elif j[1]==1:
                            vote_text = sg.Text(f'{j[0]} ({j[1]} Vote)',background_color='#FFFFFF', pad=((10,5),(10,0)))
                            bar_color = ('#E2E2E2','#E2E2E2')
                        else:
                            vote_text = sg.Text(f'{j[0]} ({j[1]} Votes)',background_color='#FFFFFF', pad=((10,5),(10,0)))
                            bar_color = ('#E2E2E2','#E2E2E2')
                        
                        candidate_result_leyout.extend([[vote_text],[sg.ProgressBar(j[1],size=(j[1]*0.2,25),bar_color=bar_color,pad=((10,0),(2,0)))]])
                    result_layout.append([sg.Column(candidate_result_leyout,expand_x=True,size=(100,len(curr_post_data)*60+70),background_color='#FFFFFF',pad=(10,10))])

                show_results_window = sg.Window(f'{results_window[result_event].get()} Results',[[sg.Column(result_layout,expand_y=True,expand_x=True,scrollable=True,vertical_scroll_only=True, key='result_container')]],size=(550,500),resizable=True,modal=True,finalize=True)
                
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
                        break
                show_results_window.close()

            # If deleting a result
            elif result_event.startswith('delete'):
                file_name = result_event.split('-',1)[1]
                file_path = resource_path(f'src\\results\\result-{file_name}')
                remove(file_path)
                results_window[result_event].update(visible=False)
                results_window[f'link-{file_name}'].update(visible=False)
                del results_window.key_dict[result_event]
                del results_window.key_dict[f'link-{file_name}']
                other_links_exist = False
                for i in results_window.key_dict:
                    if i.startswith('link'):
                        other_links_exist = True
                        break
                if other_links_exist == False:
                    break
        else:
            break
    results_window.close()