import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
from tkinter import messagebox
from PIL import Image, ImageTk
from .core import YOLOAnnotationCore
from .styles import StyleManager

class WelcomeScreen:
    def __init__(self, master, on_start_callback):
        self.master = master
        self.on_start_callback = on_start_callback
        self.style = StyleManager()
        
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal com gradiente
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Título
        title = ttk.Label(main_frame, text="YOLO Label Tool", style="Title.TLabel")
        title.pack(pady=(20, 10))
        
        # Subtítulo
        subtitle = ttk.Label(main_frame, text="Ferramenta avançada para rotulagem de imagens", style="Subtitle.TLabel")
        subtitle.pack(pady=(0, 40))
        
        # Botão de início
        start_btn = ttk.Button(main_frame, text="Iniciar", command=self.on_start_callback, style="Accent.TButton")
        start_btn.pack(pady=20, ipadx=20, ipady=10)
        
        # Rodapé
        footer = ttk.Label(main_frame, text="Desenvolvido para projetos de visão computacional", style="Subtitle.TLabel")
        footer.pack(side=tk.BOTTOM, pady=20)

class MainUI:
    def __init__(self, master, core):
        self.master = master
        self.core = core
        self.style = StyleManager()
        
        self.setup_main_window()
        self.create_menu()
        self.create_toolbar()
        self.create_main_panels()
        self.create_status_bar()
        self.bind_events()
        
        self.update_class_dropdown()
    
    def setup_main_window(self):
        self.master.title("Advanced YOLO Label Tool")
        self.master.geometry("1200x800")
        self.master.minsize(800, 600)
        
        # Configurar grid para expansão
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
    
    def create_menu(self):
        menubar = tk.Menu(self.master)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Abrir Pasta", command=self.open_folder, accelerator="Ctrl+O")
        file_menu.add_command(label="Salvar", command=self.save_annotations, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.master.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Classes
        class_menu = tk.Menu(menubar, tearoff=0)
        class_menu.add_command(label="Adicionar Classe", command=self.show_add_class_dialog, accelerator="Ctrl+N")
        class_menu.add_command(label="Gerenciar Classes", command=self.show_manage_classes_dialog)
        menubar.add_cascade(label="Classes", menu=class_menu)
        
        # Menu Visualização
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label="Mostrar Labels", variable=self.core.show_labels, command=self.toggle_labels)
        view_menu.add_command(label="Zoom In", command=lambda: self.adjust_zoom(1.2), accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=lambda: self.adjust_zoom(0.8), accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=lambda: self.adjust_zoom(1.0, reset=True), accelerator="Ctrl+0")
        menubar.add_cascade(label="Visualização", menu=view_menu)
        
        self.master.config(menu=menubar)
    
    def create_toolbar(self):
        self.toolbar = ttk.Frame(self.master, padding=(5, 2, 5, 2))
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Botões
        btn_open = ttk.Button(self.toolbar, text="Abrir Pasta", command=self.open_folder)
        btn_open.pack(side=tk.LEFT, padx=2)
        
        btn_prev = ttk.Button(self.toolbar, text="Anterior", command=self.prev_image)
        btn_prev.pack(side=tk.LEFT, padx=2)
        
        btn_next = ttk.Button(self.toolbar, text="Próxima", command=self.next_image)
        btn_next.pack(side=tk.LEFT, padx=2)
        
        btn_save = ttk.Button(self.toolbar, text="Salvar", command=self.save_annotations)
        btn_save.pack(side=tk.LEFT, padx=2)
        
        # Dropdown de classes
        self.class_dropdown = ttk.Combobox(self.toolbar, textvariable=self.core.current_class, state="readonly")
        self.class_dropdown.pack(side=tk.LEFT, padx=10)
        
        # Botão para adicionar classe
        btn_add_class = ttk.Button(self.toolbar, text="+ Classe", command=self.show_add_class_dialog)
        btn_add_class.pack(side=tk.LEFT, padx=2)
        
        # Checkbutton para mostrar labels
        chk_show_labels = ttk.Checkbutton(self.toolbar, text="Mostrar Labels", variable=self.core.show_labels, 
                                         command=self.toggle_labels)
        chk_show_labels.pack(side=tk.LEFT, padx=10)
    
    def create_main_panels(self):
        main_panel = ttk.Frame(self.master)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas para imagem
        self.canvas_frame = ttk.Frame(main_panel)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#222222", cursor="tcross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        
        # Painel lateral para informações
        side_panel = ttk.Frame(main_panel, width=250)
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Lista de anotações
        ttk.Label(side_panel, text="Anotações", style="Title.TLabel").pack(pady=(5, 0))
        
        listbox_style = self.style.get_listbox_style()
        self.annotation_list = tk.Listbox(side_panel, **listbox_style)
        self.annotation_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botões para gerenciar anotações
        btn_frame = ttk.Frame(side_panel)
        btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        btn_delete = ttk.Button(btn_frame, text="Remover", command=self.delete_selected_annotation)
        btn_delete.pack(side=tk.LEFT, expand=True)
        
        btn_clear = ttk.Button(btn_frame, text="Limpar Tudo", command=self.clear_annotations)
        btn_clear.pack(side=tk.LEFT, expand=True)
        
        # Informações da imagem
        info_frame = ttk.LabelFrame(side_panel, text="Informações da Imagem")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.image_info = ttk.Label(info_frame, text="Nenhuma imagem carregada")
        self.image_info.pack(pady=5)
    
    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.master)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Pronto")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(self.status_bar, variable=tk.DoubleVar(), maximum=100, 
                                       style="Horizontal.TProgressbar")
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5, pady=2)
    
    def bind_events(self):
        # Eventos do canvas
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.on_mouse_wheel_scroll(e, 1.2))
        self.canvas.bind("<Button-5>", lambda e: self.on_mouse_wheel_scroll(e, 0.8))
        self.canvas.bind("<Button-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.on_pan)
        self.canvas.bind("<ButtonRelease-3>", self.end_pan)
        
        # Atalhos de teclado
        self.master.bind("<Control-o>", lambda e: self.open_folder())
        self.master.bind("<Control-s>", lambda e: self.save_annotations())
        self.master.bind("<Control-q>", lambda e: self.master.quit())
        self.master.bind("<Control-n>", lambda e: self.show_add_class_dialog())
        self.master.bind("<Right>", lambda e: self.next_image())
        self.master.bind("<Left>", lambda e: self.prev_image())
        self.master.bind("<Control-plus>", lambda e: self.adjust_zoom(1.2))
        self.master.bind("<Control-minus>", lambda e: self.adjust_zoom(0.8))
        self.master.bind("<Control-0>", lambda e: self.adjust_zoom(1.0, reset=True))
        self.master.bind("<Delete>", lambda e: self.delete_selected_annotation())
    
    def update_display(self):
        if hasattr(self.core, 'img'):
            self.update_image_display()
            self.update_annotation_list()
            self.update_image_info()
            self.update_progress()
            self.update_status()
    
    def update_image_display(self):
        self.canvas.delete("all")
        
        if not hasattr(self.core, 'img'):
            return
            
        # Aplicar zoom
        w, h = self.core.img.size
        new_w, new_h = int(w * self.core.zoom_level), int(h * self.core.zoom_level)
        zoomed_img = self.core.original_img.resize((new_w, new_h), Image.LANCZOS)
        
        # Atualizar canvas
        self.core.tk_img = ImageTk.PhotoImage(zoomed_img)
        self.canvas.config(scrollregion=(0, 0, new_w, new_h))
        self.core.canvas_img = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.core.tk_img)
        
        # Redesenhar anotações
        if self.core.show_labels.get():
            self.draw_annotations()
    
    def draw_annotations(self):
        self.canvas.delete("bbox")
        self.canvas.delete("label")
        
        for i, (class_name, x1, y1, x2, y2) in enumerate(self.core.annotations):
            # Aplicar zoom às coordenadas
            x1, x2 = x1 * self.core.zoom_level, x2 * self.core.zoom_level
            y1, y2 = y1 * self.core.zoom_level, y2 * self.core.zoom_level
            
            color = self.core.class_colors.get(class_name, "#FF0000")
            
            # Desenhar retângulo
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, tags=("bbox", f"bbox_{i}"), width=2)
            
            # Desenhar rótulo
            label_text = f"{class_name}"
            label_bg = self.canvas.create_rectangle(x1, y1-20, x1+len(label_text)*7, y1, 
                                                  fill=color, tags=("label", f"label_{i}"))
            label = self.canvas.create_text(x1+5, y1-10, anchor=tk.W, text=label_text, 
                                          fill="white", tags=("label", f"label_{i}"))
    
    def update_annotation_list(self):
        self.annotation_list.delete(0, tk.END)
        for class_name, x1, y1, x2, y2 in self.core.annotations:
            self.annotation_list.insert(tk.END, f"{class_name}: [{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}]")
    
    def update_image_info(self):
        self.image_info.config(text=self.core.get_image_info())
    
    def update_progress(self):
        self.progress['value'] = self.core.get_progress()
    
    def update_status(self):
        self.status_label.config(text=self.core.get_status_text())
    
    def update_class_dropdown(self):
        self.class_dropdown['values'] = self.core.classes
        if self.core.classes and not self.core.current_class.get():
            self.core.current_class.set(self.core.classes[0])
    
    def open_folder(self):
        if self.core.open_folder():
            self.core.load_image()
            self.update_display()
    
    def save_annotations(self):
        if self.core.save_annotations():
            self.update_status()
    
    def next_image(self):
        if self.core.next_image():
            self.core.load_image()
            self.update_display()
    
    def prev_image(self):
        if self.core.prev_image():
            self.core.load_image()
            self.update_display()
    
    def toggle_labels(self):
        if self.core.show_labels.get():
            self.draw_annotations()
        else:
            self.canvas.delete("bbox")
            self.canvas.delete("label")
    
    def delete_selected_annotation(self):
        selection = self.annotation_list.curselection()
        if selection:
            index = selection[0]
            self.annotation_list.delete(index)
            self.core.annotations.pop(index)
            if self.core.show_labels.get():
                self.draw_annotations()
    
    def clear_annotations(self):
        self.core.annotations = []
        self.annotation_list.delete(0, tk.END)
        if self.core.show_labels.get():
            self.draw_annotations()
    
    def show_add_class_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Adicionar Classe")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Nome da Classe:").grid(row=0, column=0, padx=5, pady=5)
        class_name_entry = ttk.Entry(dialog)
        class_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Cor:").grid(row=1, column=0, padx=5, pady=5)
        color_var = tk.StringVar(value="#FF0000")
        color_entry = ttk.Entry(dialog, textvariable=color_var)
        color_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def choose_color():
            color = colorchooser.askcolor(title="Escolha uma cor")[1]
            if color:
                color_var.set(color)
        
        color_btn = ttk.Button(dialog, text="Selecionar", command=choose_color)
        color_btn.grid(row=1, column=2, padx=5, pady=5)
        
        def add_class():
            name = class_name_entry.get().strip()
            color = color_var.get()
            
            success, message = self.core.add_class(name, color)
            if success:
                self.update_class_dropdown()
                dialog.destroy()
            else:
                messagebox.showerror("Erro", message)
        
        add_btn = ttk.Button(dialog, text="Adicionar", command=add_class)
        add_btn.grid(row=2, column=1, pady=10)
        
        class_name_entry.focus_set()
    
    def show_manage_classes_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Gerenciar Classes")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Lista de classes
        class_frame = ttk.Frame(dialog)
        class_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(class_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox_style = self.style.get_listbox_style()
        class_list = tk.Listbox(class_frame, yscrollcommand=scrollbar.set, **listbox_style)
        class_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=class_list.yview)
        
        for i, class_name in enumerate(self.core.classes):
            class_list.insert(tk.END, class_name)
            class_list.itemconfig(i, {'fg': self.core.class_colors.get(class_name, "#FFFFFF")})
        
        # Botões de controle
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=(0, 10))
        
        def edit_class():
            selection = class_list.curselection()
            if not selection:
                return
                
            index = selection[0]
            old_name = self.core.classes[index]
            
            edit_dialog = tk.Toplevel(dialog)
            edit_dialog.title("Editar Classe")
            edit_dialog.transient(dialog)
            edit_dialog.grab_set()
            
            ttk.Label(edit_dialog, text="Nome da Classe:").grid(row=0, column=0, padx=5, pady=5)
            name_entry = ttk.Entry(edit_dialog)
            name_entry.insert(0, old_name)
            name_entry.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(edit_dialog, text="Cor:").grid(row=1, column=0, padx=5, pady=5)
            color_var = tk.StringVar(value=self.core.class_colors.get(old_name, "#FF0000"))
            color_entry = ttk.Entry(edit_dialog, textvariable=color_var)
            color_entry.grid(row=1, column=1, padx=5, pady=5)
            
            def choose_color():
                color = colorchooser.askcolor(title="Escolha uma cor")[1]
                if color:
                    color_var.set(color)
            
            color_btn = ttk.Button(edit_dialog, text="Selecionar", command=choose_color)
            color_btn.grid(row=1, column=2, padx=5, pady=5)
            
            def save_changes():
                new_name = name_entry.get().strip()
                new_color = color_var.get()
                
                success, message = self.core.edit_class(old_name, new_name, new_color)
                if success:
                    self.update_class_dropdown()
                    refresh_class_list()
                    if hasattr(self.core, 'img') and self.core.show_labels.get():
                        self.draw_annotations()
                    edit_dialog.destroy()
                else:
                    messagebox.showerror("Erro", message)
            
            save_btn = ttk.Button(edit_dialog, text="Salvar", command=save_changes)
            save_btn.grid(row=2, column=1, pady=10)
            
            name_entry.focus_set()
        
        def delete_class():
            selection = class_list.curselection()
            if not selection:
                return
                
            index = selection[0]
            class_name = self.core.classes[index]
            
            if messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover a classe '{class_name}'?"):
                if self.core.delete_class(class_name):
                    self.update_class_dropdown()
                    refresh_class_list()
                    if hasattr(self.core, 'img'):
                        self.annotation_list.delete(0, tk.END)
                        for ann in self.core.annotations:
                            self.annotation_list.insert(tk.END, f"{ann[0]}: [{ann[1]:.1f}, {ann[2]:.1f}, {ann[3]:.1f}, {ann[4]:.1f}]")
                        if self.core.show_labels.get():
                            self.draw_annotations()
        
        def refresh_class_list():
            class_list.delete(0, tk.END)
            for i, class_name in enumerate(self.core.classes):
                class_list.insert(tk.END, class_name)
                class_list.itemconfig(i, {'fg': self.core.class_colors.get(class_name, "#FFFFFF")})
        
        edit_btn = ttk.Button(btn_frame, text="Editar", command=edit_class)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Remover", command=delete_class)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(btn_frame, text="Fechar", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    # Event handlers
    def on_click(self, event):
        if not hasattr(self.core, 'img'):
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        self.core.start_x = x / self.core.zoom_level
        self.core.start_y = y / self.core.zoom_level
        
        self.core.temp_rect = self.canvas.create_rectangle(
            x, y, x, y, 
            outline=self.core.class_colors.get(self.core.current_class.get(), "#FF0000"), 
            dash=(4, 2), width=2, tags="temp_rect"
        )
    
    def on_drag(self, event):
        if not hasattr(self.core, 'temp_rect'):
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        self.canvas.coords(self.core.temp_rect, 
                          self.core.start_x * self.core.zoom_level, 
                          self.core.start_y * self.core.zoom_level, 
                          x, y)
    
    def on_release(self, event):
        if not hasattr(self.core, 'temp_rect'):
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        end_x = x / self.core.zoom_level
        end_y = y / self.core.zoom_level
        
        if abs(end_x - self.core.start_x) > 5 and abs(end_y - self.core.start_y) > 5:
            class_name = self.core.current_class.get()
            x1, y1 = min(self.core.start_x, end_x), min(self.core.start_y, end_y)
            x2, y2 = max(self.core.start_x, end_x), max(self.core.start_y, end_y)
            
            self.core.annotations.append((class_name, x1, y1, x2, y2))
            self.annotation_list.insert(tk.END, f"{class_name}: [{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}]")
            
            if self.core.show_labels.get():
                self.draw_annotations()
        
        self.canvas.delete("temp_rect")
        del self.core.temp_rect
    
    def on_mouse_move(self, event):
        if not hasattr(self.core, 'img'):
            return
            
        x = self.canvas.canvasx(event.x) / self.core.zoom_level
        y = self.canvas.canvasy(event.y) / self.core.zoom_level
        
        self.status_label.config(text=f"X: {x:.1f}, Y: {y:.1f} | {len(self.core.annotations)} anotações")
    
    def on_mouse_wheel(self, event):
        zoom_factor = 1.2 if event.delta > 0 else 0.8
        self.adjust_zoom(zoom_factor)
    
    def on_mouse_wheel_scroll(self, event, factor):
        self.adjust_zoom(factor)
    
    def adjust_zoom(self, factor, reset=False):
        if not hasattr(self.core, 'img'):
            return
            
        if reset:
            self.core.zoom_level = 1.0
        else:
            self.core.zoom_level *= factor
            self.core.zoom_level = max(0.1, min(self.core.zoom_level, 10.0))
        
        self.update_image_display()
    
    def start_pan(self, event):
        self.core.pan_start = (event.x, event.y)
        self.canvas.config(cursor="fleur")
    
    def on_pan(self, event):
        if self.core.pan_start:
            dx = event.x - self.core.pan_start[0]
            dy = event.y - self.core.pan_start[1]
            self.canvas.xview("scroll", -dx, "units")
            self.canvas.yview("scroll", -dy, "units")
            self.core.pan_start = (event.x, event.y)
    
    def end_pan(self, event):
        self.core.pan_start = None
        self.canvas.config(cursor="tcross")