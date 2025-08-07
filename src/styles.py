from tkinter import ttk
import tkinter as tk

class StyleManager:
    def __init__(self):
        self.setup_theme()
        
    def setup_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores principais
        self.primary_color = "#4A6FA5"
        self.secondary_color = "#3D5A80"
        self.background_dark = "#2D2D2D"
        self.background_light = "#3C3C3C"
        self.text_color = "#FFFFFF"
        self.accent_color = "#FF6B6B"
        
        # Configurações gerais
        style.configure('.', 
                       background=self.background_dark, 
                       foreground=self.text_color,
                       font=('Segoe UI', 10))
        
        # Frames
        style.configure('TFrame', background=self.background_dark)
        style.configure('Dark.TFrame', background=self.background_light)
        
        # Labels
        style.configure('TLabel', background=self.background_dark, foreground=self.text_color)
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10, 'italic'))
        
        # Buttons
        style.configure('TButton', 
                        background=self.primary_color, 
                        foreground=self.text_color,
                        borderwidth=1,
                        focusthickness=3, 
                        focuscolor='none')
        style.map('TButton',
                 background=[('active', self.secondary_color)],
                 foreground=[('active', self.text_color)])
        
        style.configure('Accent.TButton', background=self.accent_color)
        style.map('Accent.TButton',
                 background=[('active', '#E05A5A')])
        
        # Entradas
        style.configure('TEntry', 
                       fieldbackground="#555555", 
                       foreground=self.text_color,
                       insertcolor=self.text_color)
        
        # Combobox
        style.configure('TCombobox', 
                       fieldbackground=self.background_light,
                       background=self.background_light,
                       foreground=self.text_color,
                       selectbackground=self.primary_color)
        
        # Scrollbars
        style.configure('TScrollbar', 
                       background=self.background_light,
                       troughcolor=self.background_dark,
                       arrowcolor=self.text_color)
        
        # Notebook (tabs)
        style.configure('TNotebook', background=self.background_dark)
        style.configure('TNotebook.Tab', 
                       background=self.background_light,
                       foreground=self.text_color,
                       padding=[10, 5])
        style.map('TNotebook.Tab',
                 background=[('selected', self.primary_color)],
                 foreground=[('selected', self.text_color)])
        
        # Progressbar
        style.configure('Horizontal.TProgressbar',
                       background=self.primary_color,
                       troughcolor=self.background_light,
                       bordercolor=self.background_dark,
                       lightcolor=self.primary_color,
                       darkcolor=self.primary_color)
        
        # Listbox
        self.listbox_bg = "#444444"
        self.listbox_fg = self.text_color
        self.listbox_select_bg = self.primary_color
        self.listbox_select_fg = self.text_color

    def get_listbox_style(self):
        return {
            'bg': self.listbox_bg,
            'fg': self.listbox_fg,
            'selectbackground': self.listbox_select_bg,
            'selectforeground': self.listbox_select_fg,
            'highlightthickness': 0,
            'activestyle': 'none'
        }