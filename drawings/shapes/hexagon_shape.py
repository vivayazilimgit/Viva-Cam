import math

def get_segments(cam_x, cam_y, margin, params):
    side = float(params.get("kenar") or params.get("kenar_uzunlugu") or 0)
    gap = float(params.get("parca_araligi") or 0)
    miktar = int(params.get("miktar") or 0)

    if side <= 0 or gap < 0:
        return []

    width = 2 * side * math.cos(math.pi / 6)
    height = 2 * side
    step_x = width + gap
    step_y = 0.75 * height + gap

    usable_x = cam_x - 2 * margin
    usable_y = cam_y - 2 * margin

    cols = int(usable_x // step_x)
    rows = int(usable_y // step_y)
    max_adet = cols * rows

    if 0 < miktar < max_adet:
        cols_used = min(cols, miktar)
        rows_used = math.ceil(miktar / cols_used)
        miktar = cols_used * rows_used
    else:
        cols_used = cols
        rows_used = rows
        miktar = max_adet

    segments = []
    count = 0
    for r in range(rows_used):
        offset_x = (step_x / 2) if r % 2 else 0
        for c in range(cols_used):
            if count >= miktar:
                break
            cx = margin + offset_x + c * step_x + width / 2
            cy = margin + r * step_y + height / 2

            angle_offset = math.pi / 6
            points = []
            for i in range(6):
                angle = angle_offset + i * math.pi / 3
                x = cx + side * math.cos(angle)
                y = cy + side * math.sin(angle)
                points.append((x, y))

            for i in range(6):
                p1 = points[i]
                p2 = points[(i + 1) % 6]
                segments.append([p1, p2])

            count += 1
        if count >= miktar:
            break

    print(f"[DEBUG] hexagon segment count: {len(segments)}")
    if segments:
        print(f"[DEBUG] First segment: {segments[0]}")
    return segments

def get_layout(cam_x, cam_y, margin, params):
    side = float(params.get("kenar") or params.get("kenar_uzunlugu") or 0)
    gap = float(params.get("parca_araligi") or 0)
    miktar = int(params.get("miktar") or 0)

    if side <= 0 or gap < 0:
        return {"adet": 0, "parca_adedi": 0, "mesaj": "❌ Geçersiz kenar veya aralık."}

    width = 2 * side * math.cos(math.pi / 6)
    height = 2 * side
    step_x = width + gap
    step_y = 0.75 * height + gap
    usable_x = cam_x - 2 * margin
    usable_y = cam_y - 2 * margin

    cols = int(usable_x // step_x)
    rows = int(usable_y // step_y)
    max_adet = cols * rows if cols > 0 and rows > 0 else 0

    if 0 < miktar < max_adet:
        cols_used = min(cols, miktar)
        rows_used = math.ceil(miktar / cols_used)
        miktar = cols_used * rows_used
    else:
        cols_used = cols
        rows_used = rows
        miktar = max_adet

    used_area = miktar * (3 * math.sqrt(3) * side ** 2 / 2)
    total_area = cam_x * cam_y
    fire_area = max(total_area - used_area, 0)

    required_width = cols_used * step_x
    required_height = rows_used * step_y

    if required_width > usable_x or required_height > usable_y:
        return {
            "adet": 0,
            "parca_adedi": 0,
            "mesaj": "❌ Yerleşim mümkün değil. Parçalar cam alanına sığmıyor.",
            "tavsiye": "📏 Cam ölçüsünü artırın ya da parça boyutunu küçültün.",
            "tavsiye_input": {
                "kenar": {"value": f"{side}", "bold": True},
                "parca_araligi": {"value": f"{gap}", "bold": True},
                "miktar": {"value": f"{miktar}", "bold": True}
            }
        }

    return {
        "adet": miktar,
        "parca_adedi": miktar,
        "fire_mm2": round(fire_area, 2),
        "fire_m2": round(fire_area / 1_000_000, 4),
        "kullanim_kolon": cols_used,
        "kullanim_satir": rows_used,
        "mesaj": f"✔ {miktar} adet yerleştirildi.\n📐 Gereken cam boyutu: {round(required_width,1)} x {round(required_height,1)} mm",
        "tavsiye": f"🔥 Fire: {round(fire_area / 1_000_000, 4)} m²",
        "tavsiye_input": {
            "kenar": {"value": f"{side}", "bold": True},
            "parca_araligi": {"value": f"{gap}", "bold": True},
            "miktar": {"value": f"{miktar}", "bold": True}
        }
    }
