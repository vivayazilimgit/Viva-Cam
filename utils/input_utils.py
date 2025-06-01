def get_normalized_inputs(raw_inputs: dict) -> dict:
    """
    Tüm key isimlerini normalize eder: küçük harf ve boşluk/simge temizliği.
    Örn: "Kenar Uzunlugu" → "kenar uzunlugu"
    """
    return {key.strip().lower(): val for key, val in raw_inputs.items()}
