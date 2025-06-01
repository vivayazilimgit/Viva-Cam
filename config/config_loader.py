import json
import os

# Konfigürasyon dosyasının yolunu tanımlar
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def get_config():
    """
    config.json dosyasını okuyup içeriğini sözlük (dict) olarak döner.
    Tüm sistem ayarlarının temel kaynağıdır.
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_cnc_limits():
    """
    CNC makinesi için maksimum cam plaka sınırlarını (mm) döner.
    config.json içindeki 'cnc_limits' alanını okur.
    
    Returns:
        tuple: (max_width_mm, max_height_mm)
    """
    config = get_config()
    limits = config.get("cnc_limits", {})
    return limits.get("max_width_mm", 2560), limits.get("max_height_mm", 1690)


def get_default_glass_size():
    """
    Kullanıcı varsayılan cam boyutlarını getirir.
    
    Returns:
        dict: {"width_mm": ..., "height_mm": ...}
    """
    config = get_config()
    return config.get("default_glass_size", {"width_mm": 2250, "height_mm": 800})


def get_default_margin():
    """
    Varsayılan kenar boşluğunu (mm) getirir.
    
    Returns:
        int: margin değeri
    """
    config = get_config()
    return config.get("default_margin_mm", 5)


def get_default_cut_speed():
    """
    Varsayılan kesim hızını döner (örnek: VS komutu için).
    
    Returns:
        int: hız değeri
    """
    config = get_config()
    return config.get("default_cut_speed", 80)


def normalize_label(text):
    """
    Etiket metinlerini normalize eder: küçük harfe çevirir, boşlukları ve ':' karakterini temizler.
    
    Args:
        text (str): Etiket metni
    Returns:
        str: normalize edilmiş string
    """
    return text.strip().lower().replace(":", "").replace(" ", "_")


def get_ui_settings():
    """
    UI için varsayılan renk ve pencere boyutu gibi ayarları getirir.
    
    Returns:
        dict: arka plan rengi, pencere boyutu gibi UI konfigürasyonları
    """
    config = get_config()
    return config.get("ui_settings", {
        "background_color": "#FFFFFF",
        "window_size": "900x700",
        "min_window_size": [600, 400]
    })


def compute_cnc_coordinates(glass_w, glass_h):
    """
    Cam boyutlarına göre CNC makinesi için koordinat limitlerini dinamik olarak hesaplar.
    Bu değerler makinenin fiziksel sınırlamalarına göre normalize edilmiş sabitlerle hesaplanır.
    
    Args:
        glass_w (int or float): Camın genişliği (mm)
        glass_h (int or float): Camın yüksekliği (mm)

    Returns:
        dict: {"x_min": ..., "x_max": ..., "y_min": ..., "y_max": ...}
    """
    base_width, base_height = get_cnc_limits()
    return {
        "x_min": int(-190064 * (glass_w / base_width)),
        "x_max": int(-102061 * (glass_w / base_width)),
        "y_min": int(153948 * (glass_h / base_height)),
        "y_max": int(185543 * (glass_h / base_height))
    }


def get_raw_cnc_limits():
    """
    Varsayılan cam boyutlarına göre CNC koordinat sınırlarını hesaplar.
    Sistem sabitlerini kullanarak çizim alanının mutlak sınırlarını verir.
    
    Returns:
        dict: {"x_min": ..., "x_max": ..., "y_min": ..., "y_max": ...}
    """
    default_glass = get_default_glass_size()
    return compute_cnc_coordinates(
        glass_w=default_glass["width_mm"],
        glass_h=default_glass["height_mm"]
    )

# config_loader.py içinde
SHAPE_FIELDS = None
try:
    # Lütfen bu yolu projenizin gerçek dizin yapısına göre tekrar kontrol edin.
    # Eğer config_loader.py ve shapes_settings.json aynı 'config' klasöründeyse:
    _path = os.path.join(os.path.dirname(__file__), "shapes_settings.json")
    # Eğer config klasörü ana projenin kökünde ve config_loader.py onun içindeyse, ve shapes_settings.json da config klasörünün içindeyse:
    # _path = os.path.join(os.path.dirname(__file__), "shapes_settings.json")
    # Daha önceki yorumumdaki varsayım buydu ve path bu olmalıydı.
    # İlk denemenizdeki "..", "config" kısmı, config_loader.py'nin bir üst klasöre çıkıp tekrar "config" klasörüne girmeye çalıştığı anlamına gelir.
    # Bu, config_loader.py'nin config klasörü içinde olmadığı senaryo için uygun olurdu.
    # Örn: main.py, config/config_loader.py, config/shapes_settings.json
    # Yukarıdaki yapı için ilk verdiğim çözüm doğru:
    with open(_path, "r", encoding="utf-8") as f:
        SHAPE_FIELDS = json.load(f)
except Exception as e:
    print(f"Error loading SHAPE_FIELDS: {e}") # Konsola bu hatayı basacak
    SHAPE_FIELDS = {}