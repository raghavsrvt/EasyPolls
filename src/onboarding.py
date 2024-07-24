from src.get_absolute_path import resource_path
import PySimpleGUI as sg
from shutil import rmtree
BLACK = '#292929'
DISABLED = '#8F8F8F'
TEXT_PAD = ((10,10),(15,10))
display_passwd = False
ONBOARDING_IMGS = [resource_path(r'src\assets\onboarding\0.png'),resource_path(r'src\assets\onboarding\1.png'),
                   resource_path(r'src\assets\onboarding\2.png'),resource_path(r'src\assets\onboarding\3.png'),
                   resource_path(r'src\assets\onboarding\4.png'),]

def onboarding_layout():
    header_layout = [sg.Column([[sg.Text('EasyPolls',text_color='#4E46B4',font=(None,15,'bold')),sg.Push(),sg.Text('SKIP',key='skip',enable_events=True,font=(None, 10, 'bold'))]],expand_x=True)]
    layout = [header_layout]
    img_status = ['○' for i in range(len(ONBOARDING_IMGS))]
    for i in range(len(ONBOARDING_IMGS)):
        img_status[i] = '●'
        if i==0:
            image = [sg.Image(ONBOARDING_IMGS[0])]
            btn_el = [sg.Push(), sg.Text('PREVIOUS',text_color=DISABLED,pad=TEXT_PAD,font=(None, 10, 'bold')),sg.Text(' '.join(img_status), key='img-status',pad=TEXT_PAD,text_color='#4E46B4'),sg.Text('NEXT', enable_events=True, key='next-1',text_color=BLACK,pad=TEXT_PAD,font=(None, 10, 'bold')),sg.Push()]
            col_el= [sg.pin(sg.Column([image, btn_el], key='img-0',expand_x=True),shrink=True)]
            layout.append(col_el)
        elif i==len(ONBOARDING_IMGS)-1:
            image = [sg.Image(ONBOARDING_IMGS[i])]
            btn_el = [sg.Push(), sg.Text('PREVIOUS', enable_events=True, key=f'prev-{i-1}',text_color=BLACK,pad=TEXT_PAD,font=(None, 10, 'bold')), sg.Text(' '.join(img_status), key='img-status',pad=TEXT_PAD,text_color='#4E46B4'),sg.Text('START', enable_events=True, key='start',text_color=BLACK,pad=TEXT_PAD,font=(None, 10, 'bold')),sg.Push()]
            col_el= [sg.pin(sg.Column([image, btn_el], key=f'img-{i}', visible=False,expand_x=True),shrink=True)]
            layout.append(col_el)
        else:
            image = [sg.Image(ONBOARDING_IMGS[i])]
            btn_el = [sg.Push(), sg.Text('PREVIOUS', enable_events=True, key=f'prev-{i-1}',text_color=BLACK,pad=TEXT_PAD,font=(None, 10, 'bold')),sg.Text(' '.join(img_status), key='img-status',pad=TEXT_PAD,text_color='#4E46B4'),sg.Text('NEXT', enable_events=True, key=f'next-{i+1}',pad=TEXT_PAD,text_color=BLACK,font=(None, 10, 'bold')),sg.Push()]
            col_el= [sg.pin(sg.Column([image, btn_el], key=f'img-{i}', visible=False,expand_x=True),shrink=True)]
            layout.append(col_el)
        img_status[i] = '○'

    return layout

def display_onboarding():
    global display_passwd
    window = sg.Window('EasyPolls  •  Made by Raghav Srivastava (GitHub: raghavsrvt)', onboarding_layout())
    while True:
        event, values = window.read()
        if event!=sg.WIN_CLOSED:
            if event.startswith('next'):
                next_img = int(event.split('-',1)[1])
                curr_img = next_img - 1
                window[f'img-{curr_img}'].update(visible=False)
                window[f'img-{next_img}'].update(visible=True)
            elif event.startswith('prev'):
                prev_img = int(event.split('-',1)[1])
                curr_img = prev_img + 1
                window[f'img-{curr_img}'].update(visible=False)
                window[f'img-{prev_img}'].update(visible=True)
            elif event == 'skip' or event == 'start':
                display_passwd = True
                break
        else:
            break
    window.close()

    if display_passwd == True:
        rmtree(resource_path(r'src\assets\onboarding'))
        from src.password_functions import display_password_window
        show_admin_panel,election_status = display_password_window()
        if show_admin_panel:
            from src.admin_functions import display_admin_panel
            display_admin_panel()