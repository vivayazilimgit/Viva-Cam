import importlib
import os
# import tkinter as tk  # Bu modül genellikle events.py içinde doğrudan kullanılmaz.
import json
from config.config_loader import normalize_label
from simulations.shapes_simulation import run_simulation_from_plt
from calculations.universal_calc import calculations as universal_calculations # Asıl hesaplama motorunuz
from config.config_loader import SHAPE_FIELDS

def calculations(self):
    """
    UI'dan alınan giriş değerlerini toplar ve universal_calculations'ı çağırır.
    Hesaplama sonuçlarını döndürür, UI'yı doğrudan güncellemez.
    Hata durumunda hatayı yukarı fırlatır.
    """
    try:
        sekil = self.shape_var.get()
        shape_type = SHAPE_FIELDS.get(sekil, {}).get("type", "rectangle")

        # Genel giriş alanlarından değerleri oku
        cam_x = float(self.cam_x.get())
        cam_y = float(self.cam_y.get())
        margin = float(self.margin.get())
        speed = float(self.speed.get())

        # Şekle özel giriş alanlarından değerleri oku ve normalize et
        shape_inputs_dict = {}
        for label_key, entry_widget in self.entries.items():
            val_str = entry_widget.get().strip()
            normalized = normalize_label(label_key)

            if val_str == "":
                # Boş bırakılan alanları işlemeyi atlayın veya varsayılan atayın
                # Ancak, universal_calc'ın beklediği tüm zorunlu alanların dolu olduğundan emin olun.
                continue 

            try:
                # Miktar alanı için özel durum, int'e dönüştür
                if "miktar" in normalized: 
                    shape_inputs_dict[normalized] = int(float(val_str)) # Float'a çevirip sonra int yapmak daha güvenli
                else:
                    shape_inputs_dict[normalized] = float(val_str)
            except ValueError:
                # Geçersiz sayısal girdi durumunda hata fırlat
                raise ValueError(f"'{label_key}' alanı geçerli bir sayı olmalıdır.")

        # Asıl hesaplama fonksiyonunu çağırın
        sonuc = universal_calculations(shape_type, cam_x, cam_y, margin, speed, shape_inputs_dict)

        # Hesaplama sonucunu döndür
        return sonuc

    except Exception as e:
        # Herhangi bir hata oluştuğunda, hatayı debug olarak yazdır ve tekrar fırlat.
        # Bu, hatanın VivaUI'daki on_calculate tarafından yakalanmasını sağlar.
        print(f"[DEBUG] events.calculations içinde bir hata oluştu: {e}")
        raise # Hatanın on_calculate'e iletilmesini sağlar

def generate_plt(self):
    """
    PLT dosyası oluşturma işlemini yönetir.
    UI'yı doğrudan güncellemez, hata durumunda hata fırlatır.
    """
    if self.missing_input():
        raise ValueError("Gerekli giriş alanları eksik veya geçersiz!")

    try:
        sekil = self.shape_var.get()
        cam_x = float(self.cam_x.get())
        cam_y = float(self.cam_y.get())
        margin = float(self.margin.get())

        parametreler = {}
        for k, e in self.entries.items():
            val_str = e.get().strip()
            if val_str != "":
                normalized_key = normalize_label(k)
                try:
                    if "miktar" in normalized_key:
                        parametreler[normalized_key] = int(float(val_str))
                    else:
                        parametreler[normalized_key] = float(val_str)
                except ValueError:
                    raise ValueError(f"'{k}' alanı geçerli bir sayı olmalıdır.")

        if "parca_bosluk" in self.special_entries:
            try:
                parametreler["parca_bosluk"] = float(self.special_entries["parca_bosluk"].get())
            except ValueError:
                raise ValueError("'Parça Boşluk' alanı geçerli bir sayı olmalıdır.")


        from generator_plt.plt_generator import generate_plt_file_from_ui
        dosya_yolu = generate_plt_file_from_ui(sekil, cam_x, cam_y, margin, parametreler)

        return f"✔ PLT dosyası oluşturuldu:\n{dosya_yolu}" # Başarı mesajını döndür

    except Exception as e:
        print(f"[DEBUG] generate_plt içinde bir hata oluştu: {e}")
        raise ValueError(f"❌ PLT oluşturulamadı: {e}") # Hata mesajını fırlat

def draw(self):
    """
    Çizim işlemini başlatır.
    UI'yı doğrudan güncellemez, hata durumunda hata fırlatır.
    """
    if self.missing_input():
        raise ValueError("Gerekli giriş alanları eksik veya geçersiz!")

    try:
        # import importlib # Zaten en başta import edildi
        from drawings.universal_draw import run_cizim
        # from calculations.universal_calc import calculations as universal_calculations # Zaten en başta import edildi

        sekil = self.shape_var.get()
        shape_type = SHAPE_FIELDS.get(sekil, {}).get("type", sekil.lower())

        cam_x = float(self.cam_x.get())
        cam_y = float(self.cam_y.get())
        margin = float(self.margin.get())
        speed = float(self.speed.get())

        # Girdileri normalize et
        params = {}
        for k, e in self.entries.items():
            val_str = e.get().strip()
            normalized_key = normalize_label(k)
            if val_str: # Boş stringleri atlamayın, gerekirse 0.0 olarak işleyin
                try:
                    if "miktar" in normalized_key:
                        params[normalized_key] = int(float(val_str))
                    else:
                        params[normalized_key] = float(val_str)
                except ValueError:
                    raise ValueError(f"'{k}' alanı geçerli bir sayı olmalıdır.")
            else:
                params[normalized_key] = 0.0 # Boşsa varsayılan 0.0

        # 1️⃣ Hesaplama yap (Sonucunu UI'da göstermek için tutulur)
        hesap_sonucu = universal_calculations(shape_type, cam_x, cam_y, margin, speed, params)

        # 2️⃣ Çizimi başlat
        run_cizim(shape_type, cam_x, cam_y, margin, params)

        # UI'ya dönecek mesaj ve tavsiyeyi döndür
        return {
            "mesaj": hesap_sonucu.get("mesaj", ""),
            "tavsiye": hesap_sonucu.get("tavsiye", "")
        }

    except Exception as e:
        print(f"[DEBUG] draw içinde bir hata oluştu: {e}")
        raise ValueError(f"Çizim hatası: {e}") # Hata mesajını fırlat

def start_simulation(self):
    """
    Simülasyonu başlatır.
    UI'yı doğrudan güncellemez, hata durumunda hata fırlatır.
    """
    if self.missing_input():
        raise ValueError("Gerekli giriş alanları eksik veya geçersiz!")

    try:
        from simulations.shapes_simulation import run_simulation_from_plt

        drawing_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "drawings", "drawing"))
        sekil = self.shape_var.get().lower()

        dosyalar = [f for f in os.listdir(drawing_path) if f.startswith(sekil) and f.endswith(".json")]
        if not dosyalar:
            raise FileNotFoundError("Uygun çizim dosyası bulunamadı.")

        dosyalar.sort(key=lambda x: os.path.getmtime(os.path.join(drawing_path, x)), reverse=True)
        dosya_yolu = os.path.join(drawing_path, dosyalar[0])

        with open(dosya_yolu, "r", encoding="utf-8") as f:
            data = json.load(f)

        cam_x = data.get("cam_genislik")
        cam_y = data.get("cam_yukseklik")
        
        # PLT dosyası kontrolü
        exports_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "exports_plt"))
        plt_dosyalar = [f for f in os.listdir(exports_dir) if f.startswith(sekil) and f.endswith(".plt")]
        plt_dosyalar.sort(key=lambda x: os.path.getmtime(os.path.join(exports_dir, x)), reverse=True)

        if not plt_dosyalar:
            raise FileNotFoundError("Simülasyon için PLT dosyası bulunamadı.")

        plt_yolu = os.path.join(exports_dir, plt_dosyalar[0])

        margin = data.get("margin", float(self.margin.get()))
        cizgi_listesi = data.get("cizgi_listesi", [])

        if not cizgi_listesi:
            raise ValueError("Çizgi listesi boş. Simülasyon başlatılamıyor.")

        run_simulation(cam_x, cam_y, cizgi_listesi, margin=margin, interval=50)
        return "✔ Simülasyon başarıyla başlatıldı." # Başarı mesajı döndür

    except Exception as e:
        print(f"[DEBUG] start_simulation içinde bir hata oluştu: {e}")
        raise ValueError(f"Simülasyon hatası: {e}") # Hata mesajını fırlat