import PySimpleGUI as sg
from PIL import ImageFont
from src.get_absolute_path import resource_path
def set_theme():
    font_inter = ImageFont.truetype(resource_path('src\\assets\\Inter.ttf'),16)
    inter_font_family = font_inter.getname()[0]
    sg.set_options(font=(inter_font_family,11),suppress_raise_key_errors=True, suppress_error_popups=True, suppress_key_guessing=True)
    sg.set_global_icon(resource_path('src\\assets\\logo.ico'))
    sg.theme_add_new(
        'MoonLight', 
        {
            'BACKGROUND': '#F5F5F5', 
            'TEXT': '#000000', 
            'INPUT': '#FFFFFF', 
            'TEXT_INPUT': '#18181b',
            'SCROLL': '#4E46B4', 
            'BUTTON': ('#FFFFFF', '#4E46B4'), 
            'PROGRESS': ('#000000', '#000000'), 
            'BORDER': 0, 
            'SLIDER_DEPTH': 0, 
            'PROGRESS_DEPTH': 0, 
            'ACCENT1': '#FFB319', 
            'ACCENT2': '#FF4E64', 
            'ACCENT3': '#B3804A', 
        }
    )
    sg.theme('MoonLight')