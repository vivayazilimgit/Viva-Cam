import math

def get_segments(cam_x, cam_y, margin, params):
    def try_float(val):
        try:
            return float(val)
        except:
            return 0.0

    width = try_float(params.get("genislik"))
    height = try_float(params.get("yukseklik"))
    miktar = try_float(params.get("miktar"))

    # Radius değerleri (0 olanlar 90° köşe sayılır)
    radius = {
        "tl": try_float(params.get("radius sol ust")),
        "tr": try_float(params.get("radius sag ust")),
        "bl": try_float(params.get("radius sol alt")),
        "br": try_float(params.get("radius sag alt")),
    }

    def draw_arc(cx, cy, r, start_angle, end_angle, steps=10):
        points = []
        for i in range(steps + 1):
            angle = math.radians(start_angle + (end_angle - start_angle) * i / steps)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append((round(x, 3), round(y, 3)))
        return points

    segments = []

    usable_x = cam_x - 2 * margin
    usable_y = cam_y - 2 * margin

    cols = int(usable_x // width)
    rows = int(usable_y // height)
    total_possible = cols * rows

    if miktar > 0:
        needed = int(min(total_possible, miktar))
    else:
        needed = total_possible

    count = 0

    for row in range(rows):
        for col in range(cols):
            if count >= needed:
                break

            x0 = margin + col * width
            y0 = margin + row * height
            x1 = x0 + width
            y1 = y0 + height

            # Sadece ilk parçada radius'lar uygulanır
            apply_radius = count == 0
            r = radius if apply_radius else {k: 0 for k in radius}

            def segment_r(x0, y0, x1, y1, r):
                segs = []
                if r["bl"] > 0:
                    arc = draw_arc(x0 + r["bl"], y0 + r["bl"], r["bl"], 180, 270)
                    segs += [(arc[i], arc[i+1]) for i in range(len(arc)-1)]
                    start = arc[-1]
                else:
                    start = (x0, y0)

                y_target = y1 - r["tl"] if r["tl"] > 0 else y1
                segs.append((start, (x0, y_target)))
                start = (x0, y_target)

                if r["tl"] > 0:
                    arc = draw_arc(x0 + r["tl"], y1 - r["tl"], r["tl"], 90, 180)
                    segs += [(arc[i], arc[i+1]) for i in range(len(arc)-1)]
                    start = arc[-1]

                x_target = x1 - r["tr"] if r["tr"] > 0 else x1
                segs.append((start, (x_target, y1)))
                start = (x_target, y1)

                if r["tr"] > 0:
                    arc = draw_arc(x1 - r["tr"], y1 - r["tr"], r["tr"], 0, 90)
                    segs += [(arc[i], arc[i+1]) for i in range(len(arc)-1)]
                    start = arc[-1]

                y_target = y0 + r["br"] if r["br"] > 0 else y0
                segs.append((start, (x1, y_target)))
                start = (x1, y_target)

                if r["br"] > 0:
                    arc = draw_arc(x1 - r["br"], y0 + r["br"], r["br"], 270, 360)
                    segs += [(arc[i], arc[i+1]) for i in range(len(arc)-1)]
                    start = arc[-1]

                x_target = x0 + r["bl"] if r["bl"] > 0 else x0
                segs.append((start, (x_target, y0)))

                return segs

            segments.extend(segment_r(x0, y0, x1, y1, r))
            count += 1

    return segments
