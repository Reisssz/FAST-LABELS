import tkinter as tk
from tkinter import ttk
from src.ui import WelcomeScreen, MainUI
from src.core import YOLOAnnotationCore
from src.styles import StyleManager

class YOLOLabelApp:
    def __init__(self, root):
        self.root = root
        self.style = StyleManager()
        self.core = YOLOAnnotationCore()
        
        self.show_welcome_screen()
    
    def show_welcome_screen(self):
        # Limpar a janela principal
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Mostrar tela de boas-vindas
        self.welcome = WelcomeScreen(self.root, self.start_main_app)
    
    def start_main_app(self):
        # Limpar a janela principal
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Iniciar aplicação principal
        self.main_ui = MainUI(self.root, self.core)

def main():
    root = tk.Tk()
    app = YOLOLabelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()