def get_segments(cam_x, cam_y, margin, params):
    genislik = float(params.get("genislik"))
    yukseklik = float(params.get("yukseklik"))
    miktar = int(params.get("miktar", 0) or 0)

    usable_x = cam_x - 2 * margin
    usable_y = cam_y - 2 * margin

    cols = int(usable_x // genislik)
    rows = int(usable_y // yukseklik)

    if miktar <= 0:
        miktar = cols * rows  # Maksimum sığan adet

    cols_used = min(cols, miktar)
    rows_used = (miktar + cols_used - 1) // cols_used  # Tavan alma

    segments = []

    # Yatay çizgiler
    for row in range(rows_used + 1):
        y = margin + row * yukseklik
        segments.append([(margin, y), (margin + cols_used * genislik, y)])

    # Dikey çizgiler
    for col in range(cols_used + 1):
        x = margin + col * genislik
        segments.append([(x, margin), (x, margin + rows_used * yukseklik)])

    return segments
