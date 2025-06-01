import math

def get_segments(cam_x, cam_y, margin, params):
    gen = float(params.get("genislik", 0))  # X ekseni çapı
    yuk = float(params.get("yukseklik", 0))  # Y ekseni çapı
    gap = float(params.get("parca_araligi", 0))
    miktar = int(params.get("miktar", 0) or 0)

    if gen <= 0 or yuk <= 0 or gap < 0:
        return []

    step_x = gen + gap
    step_y = yuk + gap
    usable_x = cam_x - 2 * margin
    usable_y = cam_y - 2 * margin

    cols = int(usable_x // step_x)
    rows = int(usable_y // step_y)

    if cols <= 0 or rows <= 0:
        return []

    max_adet = cols * rows

    if 0 < miktar < max_adet:
        cols_used = min(cols, miktar)
        rows_used = math.ceil(miktar / cols_used)
    else:
        cols_used = cols
        rows_used = rows
        miktar = max_adet

    segments = []
    count = 0
    for r in range(rows_used):
        for c in range(cols_used):
            if count >= miktar:
                break
            center_x = margin + c * step_x + gen / 2
            center_y = margin + r * step_y + yuk / 2
            segments.append([("ellipse", center_x, center_y, gen, yuk)])
            count += 1
        if count >= miktar:
            break

    return segments


def get_layout(cam_x, cam_y, margin, params):
    gen = float(params.get("genislik", 0))
    yuk = float(params.get("yukseklik", 0))
    gap = float(params.get("parca_araligi", 0))
    miktar = int(params.get("miktar", 0) or 0)

    if gen <= 0 or yuk <= 0 or gap < 0:
        return {"adet": 0, "parca_adedi": 0}

    step_x = gen + gap
    step_y = yuk + gap
    usable_x = cam_x - 2 * margin
    usable_y = cam_y - 2 * margin

    cols = int(usable_x // step_x)
    rows = int(usable_y // step_y)
    max_adet = cols * rows if cols > 0 and rows > 0 else 0

    if 0 < miktar < max_adet:
        return {"adet": miktar, "parca_adedi": miktar}
    else:
        return {"adet": max_adet, "parca_adedi": max_adet}
