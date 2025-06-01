import math

def get_segments(cam_x, cam_y, margin, params):
    def try_float(val):
        try:
            return float(val)
        except:
            return 0.0

    taban = try_float(params.get("taban"))
    yukseklik = try_float(params.get("yukseklik"))
    miktar_raw = params.get("miktar")

    usable_x = cam_x - 2 * margin
    usable_y = cam_y - 2 * margin

    # Miktar belirlenmişse ona göre satır-sütun hesapla
    cols = int(usable_x // taban)
    if cols <= 0:
        return []

    if miktar_raw not in [None, ""]:
        try:
            miktar = int(miktar_raw)
            if miktar <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError("Miktar pozitif bir tam sayı olmalıdır.")

        rows = math.ceil(miktar / cols)
    else:
        rows = int(usable_y // yukseklik)
        miktar = rows * cols

    segments = []

    for row in range(rows):
        for col in range(cols):
            index = row * cols + col
            if index >= miktar:
                break

            x0 = margin + col * taban
            y0 = margin + row * yukseklik

            # Üçgen: sol alt, sağ alt, orta üst (eşkenar değil ama düz taban)
            p1 = (x0, y0)
            p2 = (x0 + taban, y0)
            p3 = (x0 + taban / 2, y0 + yukseklik)

            segments += [
                (p1, p2),
                (p2, p3),
                (p3, p1)
            ]

    return segments
