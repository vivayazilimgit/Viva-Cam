import importlib

# İstediğin şekil için modülü dinamik import eden fonksiyon
def get_cizim_modulu(sekil):
    mod_ad = f"drawings.{sekil}_draw"
    try:
        mod = importlib.import_module(mod_ad)
        return mod
    except ModuleNotFoundError:
        raise ImportError(f"'{mod_ad}' modülü bulunamadı.")

# İstersen burada diğer yardımcı fonksiyonları da ekleyebilirsin.
