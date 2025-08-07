import os
import json
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser

class YOLOAnnotationCore:
    def __init__(self):
        self.image_dir = ""
        self.image_list = []
        self.image_index = 0
        self.annotations = []
        self.classes = []
        self.class_colors = {}
        self.current_class = tk.StringVar()
        self.zoom_level = 1.0
        self.drag_start = None
        self.pan_start = None
        self.show_labels = tk.BooleanVar(value=True)
        self.config_file = "label_config.json"
        
        # Estado da aplicação
        self.img = None
        self.original_img = None
        self.tk_img = None
        self.canvas_img = None
        self.temp_rect = None
        
        self.load_config()
        
        if not self.classes:
            self.classes = ["object"]
            self.class_colors = {"object": "#FF0000"}
            self.current_class.set("object")
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.classes = config.get('classes', [])
                    self.class_colors = config.get('class_colors', {})
                    if self.classes:
                        self.current_class.set(self.classes[0])
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar configuração: {str(e)}")
    
    def save_config(self):
        config = {
            'classes': self.classes,
            'class_colors': self.class_colors
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configuração: {str(e)}")
    
    def open_folder(self, folder=None):
        if not folder:
            folder = filedialog.askdirectory(title="Selecione a pasta com imagens")
            if not folder:
                return False
        
        self.image_dir = folder
        self.image_list = [f for f in os.listdir(self.image_dir) 
                         if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
        self.image_index = 0
        
        if self.image_list:
            return True
        else:
            messagebox.showwarning("Aviso", "Nenhuma imagem encontrada na pasta selecionada")
            return False
    
    def load_image(self):
        if not self.image_list:
            return
            
        img_path = os.path.join(self.image_dir, self.image_list[self.image_index])
        self.img = Image.open(img_path)
        self.original_img = self.img.copy()
        
        # Verificar se existe arquivo de anotações
        txt_path = os.path.splitext(img_path)[0] + ".txt"
        if os.path.exists(txt_path):
            self.load_annotations(txt_path)
        
        self.zoom_level = 1.0
    
    def load_annotations(self, txt_path):
        self.annotations = []
        
        with open(txt_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    class_id, xc, yc, bw, bh = map(float, parts)
                    class_id = int(class_id)
                    
                    if class_id < len(self.classes):
                        class_name = self.classes[class_id]
                    else:
                        class_name = f"classe_{class_id}"
                        if class_name not in self.classes:
                            self.classes.append(class_name)
                            self.class_colors[class_name] = "#FF0000"
                    
                    # Converter de YOLO para coordenadas de imagem
                    img_w, img_h = self.img.size
                    x1 = (xc - bw/2) * img_w
                    y1 = (yc - bh/2) * img_h
                    x2 = (xc + bw/2) * img_w
                    y2 = (yc + bh/2) * img_h
                    
                    self.annotations.append((class_name, x1, y1, x2, y2))
    
    def save_annotations(self):
        if not hasattr(self, 'img') or not self.image_list:
            return False
            
        img_path = os.path.join(self.image_dir, self.image_list[self.image_index])
        txt_path = os.path.splitext(img_path)[0] + ".txt"
        
        try:
            with open(txt_path, 'w') as f:
                img_w, img_h = self.img.size
                
                for class_name, x1, y1, x2, y2 in self.annotations:
                    # Converter para formato YOLO
                    xc = ((x1 + x2) / 2) / img_w
                    yc = ((y1 + y2) / 2) / img_h
                    bw = abs(x2 - x1) / img_w
                    bh = abs(y2 - y1) / img_h
                    
                    class_id = self.classes.index(class_name)
                    f.write(f"{class_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
            
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar anotações: {str(e)}")
            return False
    
    def next_image(self):
        if not self.image_list:
            return False
            
        if self.save_annotations():
            self.image_index = min(self.image_index + 1, len(self.image_list) - 1)
            return True
        return False
    
    def prev_image(self):
        if not self.image_list:
            return False
            
        if self.save_annotations():
            self.image_index = max(self.image_index - 1, 0)
            return True
        return False
    
    def add_class(self, name, color):
        if not name:
            return False, "O nome da classe não pode estar vazio"
            
        if name in self.classes:
            return False, "Esta classe já existe"
            
        self.classes.append(name)
        self.class_colors[name] = color
        self.current_class.set(name)
        self.save_config()
        return True, ""
    
    def edit_class(self, old_name, new_name, new_color):
        if not new_name:
            return False, "O nome da classe não pode estar vazio"
            
        if new_name != old_name and new_name in self.classes:
            return False, "Esta classe já existe"
            
        # Atualizar anotações
        for i, (cls, *coords) in enumerate(self.annotations):
            if cls == old_name:
                self.annotations[i] = (new_name, *coords)
        
        # Atualizar listas
        index = self.classes.index(old_name)
        self.classes[index] = new_name
        self.class_colors[new_name] = new_color
        if old_name in self.class_colors:
            del self.class_colors[old_name]
        
        if self.current_class.get() == old_name:
            self.current_class.set(new_name)
        
        self.save_config()
        return True, ""
    
    def delete_class(self, class_name):
        # Remover anotações
        self.annotations = [(cls, *coords) for cls, *coords in self.annotations if cls != class_name]
        
        # Atualizar listas
        index = self.classes.index(class_name)
        self.classes.pop(index)
        if class_name in self.class_colors:
            del self.class_colors[class_name]
        
        if self.classes:
            self.current_class.set(self.classes[0])
        else:
            self.current_class.set("")
        
        self.save_config()
        return True
    
    def get_image_info(self):
        if not hasattr(self, 'img'):
            return "Nenhuma imagem carregada"
            
        info_text = f"Arquivo: {self.image_list[self.image_index]}\n"
        info_text += f"Tamanho: {self.img.width} x {self.img.height}\n"
        info_text += f"Anotações: {len(self.annotations)}"
        return info_text
    
    def get_progress(self):
        if not self.image_list:
            return 0
        return (self.image_index + 1) / len(self.image_list) * 100
    
    def get_status_text(self):
        if not self.image_list:
            return "Pronto"
        return f"Imagem {self.image_index + 1} de {len(self.image_list)}"