import tkinter as tk
from tkinter import ttk
from drawings import get_cizim_modulu
from simulations import get_simulasyon_modulu
import importlib
import json
from PIL import Image, ImageTk
import os
from ui import events
from datetime import datetime
from config.config_loader import get_default_margin, get_default_cut_speed, get_cnc_limits, get_default_glass_size, normalize_label, SHAPE_FIELDS

CONFIG_PATH = "config"

class VivaUI:

    from config.config_loader import get_cnc_limits

    def check_cnc_limits(self, event=None):
        try:
            cam_x = float(self.cam_x.get())
            cam_y = float(self.cam_y.get())

            max_width, max_height = get_cnc_limits()

            if cam_x > max_width or cam_y > max_height:
                self.warning_label.config(
                    text=f"⚠️ CNC alanı aşıldı! Maksimum: {max_width}x{max_height} mm",
                    fg="red"
                )
            else:
                self.warning_label.config(text="")
        except ValueError:
            self.warning_label.config(text="⚠️ Sayısal olmayan cam ölçüsü!", fg="red")

    def __init__(self, root):
        self.root = root
        self.entries = {}
        self.special_entries = {}
        self.setup_layout()

 
    def setup_layout(self):
        self.root.title("Viva Cam Kesim Asistanı v3.0")
        self.root.configure(bg="#F0F2F5")
        self.root.geometry("980x760")
        self.root.minsize(750, 550)

        style = ttk.Style()
        style.theme_use('default')

        style.configure("Hesapla.TButton", font=("Segoe UI", 11), foreground="white", background="#8A76E7", padding=6)
        style.map("Hesapla.TButton", background=[("active", "#6C5BCD")])

        style.configure("Cizim.TButton", font=("Segoe UI", 11), foreground="white", background="#E7577A", padding=6)
        style.map("Cizim.TButton", background=[("active", "#C13C60")])

        style.configure("Simulasyon.TButton", font=("Segoe UI", 11), foreground="white", background="#27AE60", padding=6)
        style.map("Simulasyon.TButton", background=[("active", "#1E874A")])

        style.configure("PLTOlustur.TButton", font=("Segoe UI", 11), foreground="white", background="#3257BC", padding=6)
        style.map("PLTOlustur.TButton", background=[("active", "#2A489F")])

        style.configure("PLTYukle.TButton", font=("Segoe UI", 11), foreground="white", background="#F39C12", padding=6)
        style.map("PLTYukle.TButton", background=[("active", "#D68910")])

        style.configure("Exit.TButton", font=("Segoe UI", 11), foreground="white", background="#DB4D4B", padding=6)
        style.map("Exit.TButton", background=[("active", "#B03A37")])

        main_frame = tk.Frame(self.root, bg="#F0F2F5")
        main_frame.pack(expand=True, fill="both")

        info_bar = tk.Frame(main_frame, bg="#34495E", height=50)
        info_bar.pack(fill="x", pady=(0,10))
        info_bar.pack_propagate(False)
        
        tk.Label(info_bar, text="Viva Cam Kesim Asistanı v3.0", fg="white", bg="#34495E",
                 font=("Segoe UI", 16, "bold"), anchor="w").pack(side="left", padx=(20,40), fill="x", expand=True)
        max_width, max_height = get_cnc_limits()
        info_text = f"CNC Kesme Aralığı X: {max_width} mm - Y: {max_height} mm"
        tk.Label(info_bar, text=info_text, fg="white", bg="#34495E",
                 font=("Segoe UI", 11)).pack(side="right", padx=20)

        self.result_box = tk.LabelFrame(main_frame, text="Yapay Zeka Tavsiyesi", bg="#F0F2F5",
            font=("Segoe UI", 12, "bold"), fg="#193A7A", padx=10, pady=10)
        self.result_box.pack(side="bottom", fill="x", padx=30, pady=(0, 10))

        self.tavsiye_label = tk.Label(self.result_box, text="", font=("Segoe UI", 12),
            bg="#F0F2F5", fg="#193A7A", wraplength=880, justify="left")
        self.tavsiye_label.pack(anchor="w")

        self.kesim_onay_label = tk.Label(self.result_box, text="", 
            font=("Segoe UI", 12, "bold"), bg="#F0F2F5", fg="#E74C3C", 
            wraplength=880, justify="left")
        self.kesim_onay_label.pack(anchor="w", pady=(5,0))

        content = tk.Frame(main_frame, bg="#F0F2F5")
        content.pack(anchor="center")
    
        input_frame = tk.Frame(content, bg="#F0F2F5")
        input_frame.pack(padx=30, pady=(0,0))

        # === Parça Geometrisi Satırı ve Şekil Görseli ===
        shape_row = tk.Frame(content, bg="#F0F2F5")
        shape_row.pack(padx=30, pady=(0, 15), anchor="w")

        glass_size = get_default_glass_size()
        default_width = glass_size.get("width_mm", 2000)
        default_height = glass_size.get("height_mm", 1000)

        # Uyarı etiketi (CNC sınırları için)
        self.warning_label = tk.Label(content, text="", font=("Segoe UI", 11), fg="red", bg="#F0F2F5")
        self.warning_label.pack(pady=(0, 5))

        # Önizleme çerçevesi (sadece bir kez oluşturulacak)
        self.preview_frame = tk.Frame(content, bg="#F0F2F5")
        self.preview_frame.pack(padx=30, pady=(0, 15))
                
        # Giriş alanları çerçevesi
        self.inputs_frame = tk.Frame(content, bg="#F0F2F5")
        self.inputs_frame.pack(padx=30, pady=(0, 5), anchor="w", fill="x")

        # Uyarı etiketi ayarı
        self.warning_label.config(text="", fg="red")
        
        def add_input(row, col, label, default, attr):
            tk.Label(input_frame, text=label, font=("Segoe UI", 13), bg="#F0F2F5").grid(row=row, column=col*2, sticky="e", padx=5, pady=5)
            frame = tk.Frame(input_frame, bg="#F0F2F5")
            frame.grid(row=row, column=col*2+1, sticky="w")
            entry = ttk.Entry(frame, font=("Segoe UI", 13), width=12, justify="right")
            entry.insert(0, default)
            entry.pack(side="left")
            birim = "Adet" if "miktar" in label.lower() else "mm"
            tk.Label(frame, text=birim, font=("Segoe UI", 13), bg="#F0F2F5").pack(side="left", padx=5)
            tk.Label(frame, text="mm", font=("Segoe UI", 13), bg="#F0F2F5").pack(side="left", padx=5)
            entry.bind("<KeyRelease>", self.validate_numeric)
            entry.bind("<KeyRelease>", self.check_cnc_limits)
            setattr(self, attr, entry)
        
        add_input(0, 0, "Cam Genişliği (X):", str(default_width), "cam_x")
        add_input(0, 1, "Cam Yüksekliği (Y):", str(default_height), "cam_y")
        add_input(1, 0, "Kenar Boşluğu:", str(get_default_margin()), "margin")
        add_input(1, 1, "Kesim Hızı [VS]:", str(get_default_cut_speed()), "speed")

        # Sol kısım: Etiket + Combobox
        combo_frame = tk.Frame(shape_row, bg="#F0F2F5")
        combo_frame.pack(side="left")

        tk.Label(combo_frame, text="Parça Geometrisi:", font=("Segoe UI", 13), bg="#F0F2F5").pack(side="left", padx=(0, 5))

        self.shape_var = tk.StringVar()
        self.shape_combo = ttk.Combobox(combo_frame, textvariable=self.shape_var,
            values=sorted(["Altigen", "Baklava", "Daire", "Dikdortgen", "Elips", "Kare", "Ucgen", "Radius"]),
            font=("Segoe UI", 13, "bold"), state="readonly", width=20)
        self.shape_combo.pack(side="left")

        # Sağ kısım: Görsel önizleme
        self.shape_preview = tk.Label(shape_row, bg="#F0F2F5")
        self.shape_preview.pack(side="left", padx=30)
        
        self.shape_var.trace_add("write", lambda *args: self.update_shape_inputs())
        self.shape_var.set("Dikdortgen")

        button_area = tk.Frame(main_frame, bg="#F0F2F5")
        button_area.pack(side="bottom", padx=30, pady=(10, 0), anchor="w")

        # Hesapla butonu
        self.calculate_button = ttk.Button(button_area, text="🤖 Hesapla", style="Hesapla.TButton",
                                           command=lambda: self.on_calculate())
        self.calculate_button.pack(side="left", padx=4, ipady=4)

        # Çizim butonu - Başta hep aktif (kısıtlama kaldırıldı)
        self.draw_button = ttk.Button(button_area, text="📊 Çizim", style="Cizim.TButton",
                                      command=lambda: events.draw(self), state="normal")
        self.draw_button.pack(side="left", padx=4, ipady=4)

        # Diğer butonlar
        ttk.Button(button_area, text="🫭 Simulasyon", style="Simulasyon.TButton", command=lambda: events.start_simulation(self),
                   width=15).pack(side="left", padx=4, ipady=4)
        ttk.Button(button_area, text="📋 PLT Oluştur", style="PLTOlustur.TButton", command=lambda: events.generate_plt(self),
                   width=15).pack(side="left", padx=4, ipady=4)
        ttk.Button(button_area, text="📂 PLT Yükle", style="PLTYukle.TButton", command=lambda: None,
                   width=15).pack(side="left", padx=4, ipady=4)
        ttk.Button(button_area, text="❌ Çıkış", style="Exit.TButton", command=self.root.quit,
                   width=15).pack(side="left", padx=4, ipady=4)

    def on_calculate(self):
        try:
            result = events.calculations(self)  # hesaplama fonksiyonunu çağırır
            
            # Her durumda çizim butonu aktif
            self.draw_button.config(state="normal")
            self.kesim_onay_label.config(text="✔ Hesaplama tamamlandı. Çizim yapabilirsiniz.", fg="green")

        except Exception as e:
            self.draw_button.config(state="disabled")
            self.kesim_onay_label.config(text=f"⚠ Hesaplama hatası: {e}", fg="red")

    def validate_numeric(self, event):
        widget = event.widget
        value = widget.get()
        if not value.replace('.', '', 1).isdigit() and value != "":
            widget.delete(0, tk.END)
            widget.insert(0, "".join(filter(lambda x: x.isdigit() or x == '.', value)))
            if widget.get().count('.') > 1:
                parts = widget.get().split('.')
                widget.delete(0, tk.END)
                widget.insert(0, parts[0] + '.' + ''.join(parts[1:]))

    def update_shape_inputs(self):
        # Tavsiye ve uyarı metinlerini sıfırla
        self.tavsiye_label.config(text="")
        self.kesim_onay_label.config(text="")
    
        # Sadece inputlar içeren frame temizleniyor, preview ayrı tutuluyor
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        self.special_entries.clear()

        shape = self.shape_var.get()
        input_fields = SHAPE_FIELDS.get(shape, {}).get("fields", [])
                
        # Şekil önizlemesini güncelle
        self.update_shape_preview()
    
        for i, field_info in enumerate(input_fields):
            label_text = field_info.get("name", "")
            default_value = field_info.get("default", "")
            help_text = field_info.get("help", "")

            # Label
            tk.Label(self.inputs_frame, text=label_text + ":", font=("Segoe UI", 13), bg="#F0F2F5")\
                .grid(row=i, column=0, sticky="e", padx=10, pady=4)

            # Entry
            entry = ttk.Entry(self.inputs_frame, font=("Segoe UI", 13), width=12, justify="right")
            entry.insert(0, str(default_value))
            entry.grid(row=i, column=1, padx=5, pady=4, sticky="w")

            # Birim Label (mm veya Adet)
            birim = "Adet" if "miktar" in label_text.lower() else "mm"
            tk.Label(self.inputs_frame, text=birim, font=("Segoe UI", 13), bg="#F0F2F5")\
                .grid(row=i, column=2, padx=5, sticky="w")

            # Yardım metni varsa
            if help_text:
                tk.Label(self.inputs_frame,
                         text=f"💡 {help_text}",
                         font=("Segoe UI", 9),
                        fg="#D40D0D",
                        bg="#F0F2F5",
                        wraplength=500,
                        justify="left")\
                    .grid(row=i, column=3, padx=10, pady=4, sticky="w")

            # Event bağlamaları
            entry.bind("<KeyRelease>", self.validate_numeric)
            entry.bind("<KeyRelease>", self.check_cnc_limits)

            self.entries[label_text] = entry
   
    def update_shape_preview(self):
        shape = self.shape_var.get()
        shape_info = SHAPE_FIELDS.get(shape, {})
        image_path = shape_info.get("image", "")

        if not hasattr(self, 'shape_preview'):
            return

        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path).resize((60, 60), Image.Resampling.LANCZOS)
                self.preview_img = ImageTk.PhotoImage(img)
                self.shape_preview.config(image=self.preview_img)
                self.shape_preview.image = self.preview_img  # Referansı koru
                self.shape_preview.config(text="")
            except Exception as e:
                print(f"Görsel yüklenirken hata: {e}")
                self.shape_preview.config(image="", text="(Görsel yüklenemedi)", font=("Segoe UI", 10), fg="gray")
        else:
            self.shape_preview.config(image="", text="(Görsel bulunamadı)", font=("Segoe UI", 10), fg="gray")

    def missing_input(self):
        for label, entry in self.entries.items():
            key = label.lower().strip()
            val = entry.get().strip()

            # 'miktar' etiketi boş olabilir, kontrol dışı bırak
            if "miktar" in key:
                continue

            try:
                if val == "" or float(val) <= 0:
                    return True
            except ValueError:
                return True
        return False
