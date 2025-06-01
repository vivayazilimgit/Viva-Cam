import importlib

def get_simulasyon_modulu(sekil):
    mod_ad = f"simulasyonlar.{sekil}_sim"
    try:
        mod = importlib.import_module(mod_ad)
        return mod
    except ModuleNotFoundError:
        raise ImportError(f"'{mod_ad}' modülü bulunamadı.")
