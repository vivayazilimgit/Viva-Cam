def get_segments(cam_x, cam_y, margin, params):
    def try_float(val):
        try:
            return float(val)
        except:
            return 0.0

    size = try_float(params.get("kenar") or params.get("genislik") or params.get("kenar uzunlugu"))
    miktar = try_float(params.get("miktar") or 0)

    if size <= 0:
        raise ValueError("Kenar uzunluğu pozitif bir değer olmalıdır.")

    usable_x = cam_x - 2 * margin
    usable_y = cam_y - 2 * margin

    cols = int(usable_x // size)
    rows = int(usable_y // size)
    max_parca = cols * rows

    if miktar > 0:
        total = int(min(miktar, max_parca))
    else:
        total = max_parca

    segments = []
    part_count = 0

    for row in range(rows):
        for col in range(cols):
            if part_count >= total:
                break

            x0 = margin + col * size
            y0 = margin + row * size
            x1 = x0 + size
            y1 = y0 + size

            segments.extend([
                ((x0, y0), (x1, y0)),  # Alt
                ((x1, y0), (x1, y1)),  # Sağ
                ((x1, y1), (x0, y1)),  # Üst
                ((x0, y1), (x0, y0))   # Sol
            ])
            part_count += 1

        if part_count >= total:
            break

    return segments
