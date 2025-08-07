import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
from sklearn.metrics import confusion_matrix, accuracy_score
import seaborn as sns
import threading
from ultralytics import YOLO
import pandas as pd
import json
from tkinter import simpledialog
from typing import List, Dict, Optional, Tuple

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EQTL VISION PRO")
        self.root.geometry("1280x720")
        
        # Configuração do tema moderno
        self.style = ttkb.Style(theme="vapor")
        self.style.configure(".", background="#202020", foreground="#ffffff")
        self.style.configure("TButton", font=('Helvetica', 10), background="#202020")
        self.style.configure("TLabel", font=('Helvetica', 10), background="#202020")
        self.style.configure("TFrame", background="#202020")
        self.style.configure("TLabelframe", background="#202020", foreground="#202020")
        self.style.configure("TLabelframe.Label", background="#202020", foreground="#202020")
        self.style.configure("TNotebook", background="#202020")
        self.style.configure("TNotebook.Tab", background="#202020", foreground="#202020")
        self.style.map("TNotebook.Tab", background=[("selected", "#202020")])
        
        # Configuração de fontes
        self.title_font = ('Helvetica', 16, 'bold')
        self.subtitle_font = ('Helvetica', 12, 'bold')
        self.normal_font = ('Helvetica', 10)
        
        # Variáveis de estado
        self.model = None
        self.image_folder = ""
        self.image_files = []
        self.results = []
        self.current_image_idx = 0
        self.class_names = []
        self.running = False
        self.class_colors = {}
        
        # Layout
        self.create_widgets()
        
        # Configuração de atalhos de teclado
        self.setup_keyboard_shortcuts()
    
    def setup_keyboard_shortcuts(self):
        self.root.bind("<Left>", lambda e: self.show_previous_image())
        self.root.bind("<Right>", lambda e: self.show_next_image())
        self.root.bind("<Control-s>", lambda e: self.save_predictions())
        self.root.bind("<Escape>", lambda e: self.stop_inference() if self.running else None)
    
    def create_widgets(self):
        # Frame principal
        self.main_frame = ttkb.Frame(self.root, bootstyle="dark")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controle (esquerda)
        self.control_frame = ttkb.Frame(self.main_frame, width=300, bootstyle="dark")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Frame de visualização (direita)
        self.view_frame = ttkb.Frame(self.main_frame, bootstyle="dark")
        self.view_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Widgets do frame de controle
        self.create_control_widgets()
        
        # Widgets do frame de visualização
        self.create_view_widgets()
    
    def create_control_widgets(self):
        # Header com logo e título
        header_frame = ttkb.Frame(self.control_frame, bootstyle="black")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo (pode ser substituído por uma imagem real)
        self.logo_label = ttkb.Label(
            header_frame,
            text="⚡",
            font=('Helvetica', 24),
            bootstyle="light"
        )
        self.logo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Título
        self.title_label = ttkb.Label(
            header_frame,
            text="EQTL VISION",
            font=self.title_font,
            bootstyle="light"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Seção de modelo
        model_frame = ttkb.Labelframe(
            self.control_frame, 
            text="MODEL SETTINGS",
            bootstyle="light"
        )
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botão para carregar modelo
        self.load_model_btn = ttkb.Button(
            model_frame,
            text="📁 Load YOLO Model",
            command=self.load_model,
            bootstyle="primary",
            width=20
        )
        self.load_model_btn.pack(fill=tk.X, pady=5)
        
        self.model_status = ttkb.Label(
            model_frame,
            text="No model loaded",
            bootstyle="#000000",
            font=self.normal_font
        )
        self.model_status.pack(fill=tk.X, pady=(0, 5))
        
        # Seção de dados
        data_frame = ttkb.Labelframe(
            self.control_frame, 
            text="DATA INPUT", 
            bootstyle="#000000"
        )
        data_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botão para carregar imagens
        self.load_images_btn = ttkb.Button(
            data_frame,
            text="📂 Load Images",
            command=self.load_image_folder,
            bootstyle="primary"
        )
        self.load_images_btn.pack(fill=tk.X, pady=5)
        
        self.data_status = ttkb.Label(
            data_frame,
            text="No data loaded",
            bootstyle="#000000",
            font=self.normal_font
        )
        self.data_status.pack(fill=tk.X, pady=(0, 5))
        
        # Seção de controle
        control_frame = ttkb.Labelframe(
            self.control_frame, 
            text="INFERENCE CONTROL", 
            bootstyle="#000000"
        )
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botão para iniciar inferência
        self.start_btn = ttkb.Button(
            control_frame,
            text="▶ Start Processing",
            command=self.start_inference,
            bootstyle="success",
            state=tk.DISABLED
        )
        self.start_btn.pack(fill=tk.X, pady=5)
        
        # Botão para parar inferência
        self.stop_btn = ttkb.Button(
            control_frame,
            text="⏹ Stop",
            command=self.stop_inference,
            bootstyle="danger",
            state=tk.DISABLED
        )
        self.stop_btn.pack(fill=tk.X, pady=5)
        
        # Progresso
        self.progress = ttkb.Progressbar(
            control_frame,
            bootstyle="success-striped",
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttkb.Label(
            control_frame,
            text="Ready to process images",
            bootstyle="#000000",
            font=self.normal_font
        )
        self.progress_label.pack(fill=tk.X)
        
        # Seção de navegação
        nav_frame = ttkb.Labelframe(
            self.control_frame, 
            text="IMAGE NAVIGATION", 
            bootstyle="#000000"
        )
        nav_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botões de navegação
        nav_buttons_frame = ttkb.Frame(nav_frame)
        nav_buttons_frame.pack(fill=tk.X, pady=5)
        
        self.prev_btn = ttkb.Button(
            nav_buttons_frame,
            text="◀ Previous",
            command=self.show_previous_image,
            bootstyle="secondary",
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.next_btn = ttkb.Button(
            nav_buttons_frame,
            text="Next ▶",
            command=self.show_next_image,
            bootstyle="secondary",
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Contador de imagens
        self.image_counter = ttkb.Label(
            nav_frame,
            text="Image 0/0",
            bootstyle="#000000",
            font=self.normal_font
        )
        self.image_counter.pack(fill=tk.X, pady=(0, 5))
        
        # Botão para salvar resultados
        self.save_btn = ttkb.Button(
            nav_frame,
            text="💾 Save Results",
            command=self.save_predictions,
            bootstyle="sucess",
            state=tk.DISABLED
        )
        self.save_btn.pack(fill=tk.X, pady=5)
        
        # Seção de métricas
        metrics_frame = ttkb.Labelframe(
            self.control_frame, 
            text="CURRENT IMAGE", 
            bootstyle="light"
        )
        metrics_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.meter_status_label = ttkb.Label(
            metrics_frame,
            text="Meter: Not detected",
            bootstyle="light",
            font=self.normal_font
        )
        self.meter_status_label.pack(fill=tk.X, pady=(0, 5))
        
        self.display_status_label = ttkb.Label(
            metrics_frame,
            text="Display: Not detected",
            bootstyle="light",
            font=self.normal_font
        )
        self.display_status_label.pack(fill=tk.X, pady=(0, 5))
        
        self.digits_label = ttkb.Label(
            metrics_frame,
            text="Digits: None",
            bootstyle="light",
            font=self.normal_font
        )
        self.digits_label.pack(fill=tk.X, pady=(0, 5))
        
        # Rodapé
        footer_frame = ttkb.Frame(self.control_frame)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        footer_label = ttkb.Label(
            footer_frame,
            text="EQUATORIAL ENERGIA",
            bootstyle="light",
            font=('Helvetica', 8)
        )
        footer_label.pack(side=tk.TOP)
    
    def create_view_widgets(self):
        # Notebook para abas de visualização
        self.view_notebook = ttkb.Notebook(self.view_frame, bootstyle="light")
        self.view_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de visualização de imagem
        self.image_tab = ttkb.Frame(self.view_notebook)
        self.view_notebook.add(self.image_tab, text="IMAGE VIEW")
        
        # Canvas para a imagem com scrollbars
        self.image_canvas_frame = ttkb.Frame(self.image_tab)
        self.image_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(
            self.image_canvas_frame, 
            bg='#1e1e1e', 
            highlightthickness=0
        )
        
        self.h_scroll = ttk.Scrollbar(
            self.image_canvas_frame, 
            orient="horizontal", 
            command=self.canvas.xview
        )
        self.v_scroll = ttk.Scrollbar(
            self.image_canvas_frame, 
            orient="vertical", 
            command=self.canvas.yview
        )
        
        self.canvas.configure(
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para informações da imagem
        self.image_info_frame = ttkb.Frame(self.image_tab)
        self.image_info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.image_info_label = ttkb.Label(
            self.image_info_frame,
            text="No image loaded",
            bootstyle="light",
            font=self.normal_font
        )
        self.image_info_label.pack(side=tk.LEFT)
        
        # Aba de resultados
        self.results_tab = ttkb.Frame(self.view_notebook)
        self.view_notebook.add(self.results_tab, text="RESULTS")
        
        # Treeview para mostrar os resultados
        self.results_tree = ttk.Treeview(
            self.results_tab,
            columns=("image", "medidor", "display", "digits", "confidence"),
            show="headings",
            selectmode="browse"
        )
        
        self.results_tree.heading("image", text="Image")
        self.results_tree.heading("medidor", text="medidor")
        self.results_tree.heading("display", text="Display")
        self.results_tree.heading("digits", text="Digits")
        self.results_tree.heading("confidence", text="Confidence")
        
        self.results_tree.column("image", width=200)
        self.results_tree.column("medidor", width=100)
        self.results_tree.column("display", width=100)
        self.results_tree.column("digits", width=150)
        self.results_tree.column("confidence", width=100)
        
        scrollbar = ttk.Scrollbar(
            self.results_tab,
            orient="vertical",
            command=self.results_tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configuração de cores para a treeview
        style = ttk.Style()
        style.configure("Treeview",
            background="#202020",
            foreground="#ffffff",
            fieldbackground="#649dfa",
            font=self.normal_font
        )
        style.configure("Treeview.Heading",
            background="#649dfa",
            foreground="white",
            font=('Helvetica', 10, 'bold')
        )
        style.map("Treeview",
            background=[('selected', "#d3d3d3ff")],
            foreground=[('selected', 'white')]
        )
    
    def load_model(self):
        file_path = filedialog.askopenfilename(
            title="Select YOLO Model",
            filetypes=[("YOLO Model", "*.pt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.model = YOLO(file_path)
                self.class_names = self.model.names if hasattr(self.model, 'names') else []
                
                if not self.class_names:
                    num_classes = self.model.model.nc if hasattr(self.model.model, 'nc') else 0
                    self.class_names = [f"class_{i}" for i in range(num_classes)]
                
                self.model_status.config(text=f"Model: {os.path.basename(file_path)}")
                self.update_buttons_state()
                self.generate_class_colors()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model: {str(e)}")
                self.model = None
                self.model_status.config(text="No model loaded")
    
    def generate_class_colors(self):
        """Gera cores distintas para cada classe"""
        colors = plt.cm.get_cmap('tab20', len(self.class_names))
        self.class_colors = {}
        
        for i, class_name in enumerate(self.class_names):
            r, g, b, _ = colors(i)
            hex_color = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
            self.class_colors[class_name] = hex_color
    
    def load_image_folder(self):
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        
        if folder_path:
            try:
                self.image_folder = folder_path
                self.image_files = []
                
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                            self.image_files.append(os.path.join(root, file))
                
                if not self.image_files:
                    raise ValueError("No images found in the selected folder")
                
                self.data_status.config(text=f"Loaded {len(self.image_files)} images")
                self.results = []
                self.current_image_idx = 0
                self.update_buttons_state()
                self.update_image_counter()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load images: {str(e)}")
                self.image_folder = ""
                self.data_status.config(text="No data loaded")
    
    def update_buttons_state(self):
        if self.model and self.image_files:
            self.start_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(state=tk.DISABLED)
    
    def start_inference(self):
        if not self.model or not self.image_files:
            return
            
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        
        self.progress["maximum"] = len(self.image_files)
        self.progress["value"] = 0
        self.progress_label.config(text="Processing images...")
        
        self.results = []
        self.results_tree.delete(*self.results_tree.get_children())
        
        self.inference_thread = threading.Thread(target=self.run_inference, daemon=True)
        self.inference_thread.start()
        
        self.update_ui_during_inference()
    
    def stop_inference(self):
        self.running = False
        self.progress_label.config(text="Process stopped")
    
    def run_inference(self):
        try:
            for i, img_path in enumerate(self.image_files):
                if not self.running:
                    break
                
                try:
                    results = self.model(img_path)
                    
                    if not results or len(results) == 0:
                        continue
                        
                    first_result = results[0]
                    detections = []
                    
                    if hasattr(first_result, 'boxes') and first_result.boxes is not None:
                        boxes = first_result.boxes
                        for box in boxes:
                            xyxy = box.xyxy[0].tolist()
                            cls_id = int(box.cls[0].item())
                            conf = box.conf[0].item()
                            class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else str(cls_id)
                            
                            detections.append({
                                'class_id': cls_id,
                                'class_name': class_name,
                                'confidence': conf,
                                'box': xyxy
                            })
                    
                    # Processa os resultados para medidor/display/dígitos
                    meter_detected = any(d['class_name'] == 'medidor' for d in detections)
                    display_detected = any(d['class_name'] == 'display' for d in detections)
                    digits = [d for d in detections if d['class_name'].isdigit()]
                    
                    # Ordena dígitos da esquerda para a direita
                    digits_sorted = sorted(digits, key=lambda x: x['box'][0])
                    digit_values = [d['class_name'] for d in digits_sorted]
                    
                    result = {
                        'image_path': img_path,
                        'detections': detections,
                        'meter_detected': meter_detected,
                        'display_detected': display_detected,
                        'digits': "".join(digit_values) if digit_values else None,
                        'digits_confidence': np.mean([d['confidence'] for d in digits_sorted]) if digits_sorted else 0.0
                    }
                    
                    self.results.append(result)
                    self.root.after(0, lambda r=result: self.update_results_tree(r))
                    
                    self.progress["value"] = i + 1
                    self.progress_label.config(text=f"Processing {i+1}/{len(self.image_files)}")
                    
                except Exception as e:
                    print(f"Error processing image {img_path}: {str(e)}")
                    continue
                    
                time.sleep(0.01)
            
            self.root.after(0, self.inference_completed)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Critical inference error: {error_msg}")
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", f"Inference failed: {msg}"))
        finally:
            self.running = False
    
    def update_results_tree(self, result):
        img_name = os.path.basename(result['image_path'])
        
        self.results_tree.insert("", tk.END, values=(
            img_name,
            "Yes" if result['meter_detected'] else "No",
            "Yes" if result['display_detected'] else "No",
            result['digits'] if result['digits'] else "None",
            f"{result['digits_confidence']:.2f}" if result['digits'] else "N/A"
        ))
    
    def update_ui_during_inference(self):
        if self.running:
            if self.results and len(self.results) > self.current_image_idx:
                self.display_current_image()
            
            self.root.after(100, self.update_ui_during_inference)
    
    def inference_completed(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if len(self.results) > 0:
            self.prev_btn.config(state=tk.NORMAL if len(self.results) > 1 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if len(self.results) > 1 else tk.DISABLED)
            self.save_btn.config(state=tk.NORMAL)
            self.progress_label.config(text=f"Completed! Processed {len(self.results)} images")
            self.current_image_idx = 0
            self.display_current_image()
            self.update_image_counter()
        else:
            self.progress_label.config(text="Completed (no valid results)")
    
    def display_current_image(self):
        if not self.results or self.current_image_idx >= len(self.results):
            return
            
        result = self.results[self.current_image_idx]
        img_path = result['image_path']
        
        try:
            img = Image.open(img_path)
            draw = ImageDraw.Draw(img)
            
            for detection in result.get('detections', []):
                class_name = detection['class_name']
                x1, y1, x2, y2 = detection['box']
                color = self.class_colors.get(class_name, "#202020")
                
                draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=3)
                
                label = f"{class_name}: {detection['confidence']:.2f}"
                
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                try:
                    left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
                    text_width = right - left
                    text_height = bottom - top
                except AttributeError:
                    text_width, text_height = draw.textsize(label, font=font)
                
                draw.rectangle(
                    [(x1, y1 - text_height - 5), (x1 + text_width + 5, y1)],
                    fill=color
                )
                
                draw.text(
                    (x1 + 2, y1 - text_height - 3),
                    label,
                    font=font
                )
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 800
                canvas_height = 600
            
            img.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
            
            img_tk = ImageTk.PhotoImage(img)
            
            self.canvas.delete("all")
            self.canvas.config(
                width=img.width,
                height=img.height,
                scrollregion=(0, 0, img.width, img.height)
            )
            
            self.canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
            
            img_name = os.path.basename(img_path)
            self.image_info_label.config(text=img_name)
            
            # Atualiza as métricas da imagem atual
            self.meter_status_label.config(
                text=f"Meter: {'Detected' if result['meter_detected'] else 'Not detected'}"
            )
            self.display_status_label.config(
                text=f"Display: {'Detected' if result['display_detected'] else 'Not detected'}"
            )
            self.digits_label.config(
                text=f"Digits: {result['digits'] if result['digits'] else 'None'}"
            )
            
            self.current_image_tk = img_tk
            
        except Exception as e:
            print(f"Error displaying image {img_path}: {str(e)}")
    
    def show_previous_image(self):
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.display_current_image()
            self.update_image_counter()
    
    def show_next_image(self):
        if self.current_image_idx < len(self.results) - 1:
            self.current_image_idx += 1
            self.display_current_image()
            self.update_image_counter()
    
    def update_image_counter(self):
        total = len(self.results) if self.results else 0
        self.image_counter.config(text=f"Image {self.current_image_idx + 1}/{total}")
    
    def save_predictions(self):
        if not self.results:
            messagebox.showwarning("Warning", "No predictions to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                data = []
                
                for result in self.results:
                    img_name = os.path.basename(result['image_path'])
                    
                    data.append({
                        'Imagem': img_name,
                        'Tem Medidor': "Yes" if result['meter_detected'] else "No",
                        'Tem Display': "Yes" if result['display_detected'] else "No",
                        'Dígitos Encontrados': result['digits'] if result['digits'] else "None",
                        'Confiança': f"{result['digits_confidence']:.2f}" if result['digits'] else "N/A"
                    })
                
                df = pd.DataFrame(data)
                
                if file_path.endswith('.txt'):
                    # Formato de texto personalizado
                    with open(file_path, 'w') as f:
                        f.write("Imagem;Tem Medidor;Tem Display;Dígitos Encontrados;Confiança\n")
                        for _, row in df.iterrows():
                            f.write(f"{row['Imagem']};{row['Tem Medidor']};{row['Tem Display']};{row['Dígitos Encontrados']};{row['Confiança']}\n")
                else:
                    # Formato CSV padrão
                    df.to_csv(file_path, index=False)
                
                messagebox.showinfo("Success", f"Results saved to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {str(e)}")


if __name__ == "__main__":
    root = ttkb.Window()
    app = ModernApp(root)
    root.mainloop()