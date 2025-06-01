import importlib
import os
import tkinter as tk
import json
from config.config_loader import normalize_label
from simulations.shapes_simulation import run_simulation_from_plt_from_plt
from calculations.universal_calc import calculations as universal_calculations
from config.config_loader import SHAPE_FIELDS

def calculations(self):
    try:
        sekil = self.shape_var.get()
        shape_type = SHAPE_FIELDS.get(sekil, {}).get("type", "rectangle")

        cam_x = float(self.cam_x.get())
        cam_y = float(self.cam_y.get())
        margin = float(self.margin.get())
        speed = float(self.speed.get())

        shape_inputs_dict = {}
        for label_key, entry_widget in self.entries.items():
            val_str = entry_widget.get().strip()
            normalized = normalize_label(label_key)

            if val_str == "":
                continue

            try:
                shape_inputs_dict[normalized] = float(val_str)
            except ValueError:
                raise ValueError(f"'{label_key}' alanı geçerli bir sayı olmalıdır.")

        sonuc = universal_calculations(shape_type, cam_x, cam_y, margin, speed, shape_inputs_dict)

        mesaj = sonuc.get("mesaj", "")
        tavsiye = sonuc.get("tavsiye", "")
        tavsiye_input = sonuc.get("tavsiye_input", None)
        print(f"[DEBUG] tavsiye_input: {tavsiye_input} (type: {type(tavsiye_input)})")

        self.tavsiye_label.config(text=mesaj, fg="#193A7A")
        self.kesim_onay_label.config(text=tavsiye, fg="#E74C3C")

        # events.py içindeki calculations fonksiyonunda
        # ...

        if tavsiye_input:
            print(f"[DEBUG] tavsiye_input: {tavsiye_input} (type: {type(tavsiye_input)})")
            for label, config_data in tavsiye_input.items():
                print(f"[DEBUG] Applying tavsiye_input: {label} -> {config_data}")
                
                if label == "yerlesim_mumkun":
                    continue  # Bu flag, input değil, atla

                normalized_label = normalize_label(label)
                print(f"[DEBUG] Normalized label: {normalized_label}")

                for key_in_entries, entry in self.entries.items():
                    print(f"[DEBUG] Comparing with UI entry: {key_in_entries} normalized: {normalize_label(key_in_entries)}")
                    if normalize_label(key_in_entries) == normalized_label:
                        print(f"[DEBUG] Match found for label: {label}")

                        entry.delete(0, tk.END)
                        if isinstance(config_data, dict) and "value" in config_data:
                            display_value = config_data["value"]
                            if config_data.get("bold"):
                                entry.config(font=("Segoe UI", 13, "bold"))
                            else:
                                entry.config(font=("Segoe UI", 13))
                        else:
                            display_value = config_data
                            entry.config(font=("Segoe UI", 13))
                        entry.insert(0, str(display_value))
                        break


    except Exception as e:
        print(f"[DEBUG] No matching entry found for label: {label}")
        self.tavsiye_label.config(text=f"Hesaplama hatası: {e}", fg="red")

def generate_plt(self):
    if self.missing_input():
        self.tavsiye_label.config(text="⚠️ Gerekli giriş alanları eksik veya geçersiz!", fg="red")
        return

    try:
        sekil = self.shape_var.get()
        cam_x = float(self.cam_x.get())
        cam_y = float(self.cam_y.get())
        margin = float(self.margin.get())

        parametreler = {
            normalize_label(k): float(e.get()) for k, e in self.entries.items() if e.get().strip() != ""
        }

        if "parca_bosluk" in self.special_entries:
            parametreler["parca_bosluk"] = float(self.special_entries["parca_bosluk"].get())

        from generator_plt.plt_generator import generate_plt_file_from_ui
        dosya_yolu = generate_plt_file_from_ui(sekil, cam_x, cam_y, margin, parametreler)

        self.tavsiye_label.config(text=f"✔ PLT dosyası oluşturuldu:\n{dosya_yolu}", fg="green")

    except Exception as e:
        self.tavsiye_label.config(text=f"❌ PLT oluşturulamadı: {e}", fg="red")

def draw(self):
    if self.missing_input():
        self.tavsiye_label.config(text="⚠️ Gerekli giriş alanları eksik veya geçersiz!", fg="red")
        return

    try:
        import importlib
        from drawings.universal_draw import run_cizim
        from calculations.universal_calc import calculations as universal_calculations

        sekil = self.shape_var.get()
        shape_type = SHAPE_FIELDS.get(sekil, {}).get("type", sekil.lower())

        cam_x = float(self.cam_x.get())
        cam_y = float(self.cam_y.get())
        margin = float(self.margin.get())
        speed = float(self.speed.get())

        # Girdileri normalize et
        params = {
            normalize_label(k): float(e.get()) if e.get().strip() else 0.0
            for k, e in self.entries.items()
        }

        # 1️⃣ Hesaplama yap
        hesap_sonucu = universal_calculations(shape_type, cam_x, cam_y, margin, speed, params)

        # 2️⃣ Çizimi başlat
        run_cizim(shape_type, cam_x, cam_y, margin, params)

        # 3️⃣ UI'ya tavsiye ve mesaj göster
        mesaj = hesap_sonucu.get("mesaj", "")
        tavsiye = hesap_sonucu.get("tavsiye", "")
        self.kesim_onay_label.config(text=mesaj, fg="#E74C3C")
        self.tavsiye_label.config(text=tavsiye, fg="#193A7A")

    except Exception as e:
        self.tavsiye_label.config(text=f"Çizim hatası: {e}", fg="red")

def start_simulation(self):
    if self.missing_input():
        self.tavsiye_label.config(text="⚠️ Gerekli giriş alanları eksik veya geçersiz!", fg="red")
        return

    try:
        from simulations.shapes_simulation import run_simulation_from_plt

        drawing_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "drawings", "drawing"))
        sekil = self.shape_var.get().lower()

        dosyalar = [f for f in os.listdir(drawing_path) if f.startswith(sekil) and f.endswith(".json")]
        if not dosyalar:
            self.tavsiye_label.config(text="⚠️ Uygun çizim dosyası bulunamadı.", fg="red")
            return

        dosyalar.sort(key=lambda x: os.path.getmtime(os.path.join(drawing_path, x)), reverse=True)
        dosya_yolu = os.path.join(drawing_path, dosyalar[0])

        with open(dosya_yolu, "r", encoding="utf-8") as f:
            data = json.load(f)

        cam_x = data.get("cam_genislik")
        cam_y = data.get("cam_yukseklik")
        exports_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "exports_plt"))
        dosyalar = [f for f in os.listdir(exports_dir) if f.startswith(sekil) and f.endswith(".plt")]
        dosyalar.sort(key=lambda x: os.path.getmtime(os.path.join(exports_dir, x)), reverse=True)

        if not dosyalar:
            print("❌ Simülasyon için PLT dosyası bulunamadı.")
            return

        plt_yolu = os.path.join(exports_dir, dosyalar[0])

        margin = data.get("margin", float(self.margin.get()))
        cizgi_listesi = data.get("cizgi_listesi", [])

        if not cizgi_listesi:
            self.tavsiye_label.config(text="❌ Çizgi listesi boş. Simülasyon başlatılamıyor.", fg="red")
            return

        run_simulation(cam_x, cam_y, cizgi_listesi, margin=margin, interval=50)

    except Exception as e:
        self.tavsiye_label.config(text=f"Simülasyon hatası: {e}", fg="red")
