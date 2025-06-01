import os
import json
import importlib
from datetime import datetime
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, Polygon
import matplotlib.image as mpimg
from config.config_loader import get_raw_cnc_limits, SHAPE_FIELDS, get_cnc_limits
from utils.input_utils import get_normalized_inputs

DRAWING_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "drawing"))

def get_cizgi_listesi(sekil, cam_x, cam_y, margin, params, save_json=True, show_terminal_log=False):
    params = get_normalized_inputs(params)

    try:
        shape_type = SHAPE_FIELDS.get(sekil, {}).get("type", sekil.lower())
        shape_module = importlib.import_module(f"drawings.shapes.{shape_type}_shape")
        segments = shape_module.get_segments(cam_x, cam_y, margin, params)
    except Exception as e:
        raise ValueError(f"Çizgi oluşturulamadı: {e}")

    if not isinstance(segments, list):
        raise ValueError("get_segments() fonksiyonu bir çizgi listesi döndürmelidir.")

    if save_json:
        try:
            os.makedirs(DRAWING_PATH, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(DRAWING_PATH, f"{sekil.lower()}_{timestamp}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "cam_genislik": cam_x,
                    "cam_yukseklik": cam_y,
                    "margin": margin,
                    "cizgi_listesi": segments
                }, f, indent=2, ensure_ascii=False)
            if show_terminal_log:
                print(f"✔ JSON kaydedildi: {file_path}")
        except Exception as e:
            print(f"JSON kaydı sırasında hata: {e}")

    return segments

def run_cizim(sekil, cam_x, cam_y, margin, params, save_json=True, show_terminal_log=False):
    try:
        shape_type = SHAPE_FIELDS.get(sekil, {}).get("type", sekil.lower())
        shape_module = importlib.import_module(f"drawings.shapes.{shape_type}_shape")
        if hasattr(shape_module, "get_layout"):
            layout_result = shape_module.get_layout(cam_x, cam_y, margin, params)
            cam_x = layout_result.get("onerilen_cam_x", cam_x)
            cam_y = layout_result.get("onerilen_cam_y", cam_y)
        else:
            layout_result = {}
    except Exception as e:
        print(f"[WARN] Tavsiye cam ölçüsü alınamadı: {e}")
        layout_result = {}

    # Yerleşim mümkün değilse çizim yapma
    if not layout_result.get("tavsiye_input", {}).get("yerlesim_mumkun", True):
        print("⚠️ Yerleşim mümkün değil, çizim yapılmayacak.")
        return layout_result

    segments = get_cizgi_listesi(sekil, cam_x, cam_y, margin, params, save_json=save_json, show_terminal_log=show_terminal_log)

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.canvas.manager.set_window_title(f"CNC Cam Kesim - {sekil}")
    fig.suptitle(f"CNC Cam Kesim | Şekil: {sekil} | Cam: {cam_x}x{cam_y} mm | Margin: {margin} mm", fontsize=14, fontweight='bold')
    ax.set_title(f"{sekil} Yerleşim Çizimi")
    ax.set_xlabel("X Ekseni (mm)", fontsize=12)
    ax.set_ylabel("Y Ekseni (mm)", fontsize=12)
    ax.set_aspect("equal")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    cnc_width, cnc_height = get_cnc_limits()
    ax.set_xlim(0, cnc_width)
    ax.set_ylim(0, cnc_height)

    ax.add_patch(Rectangle((0, 0), cnc_width, cnc_height, facecolor='none', edgecolor='none', zorder=0))
    ax.add_patch(Rectangle((0, 0), cam_x, cam_y, facecolor='#CFE8FF', edgecolor='navy', linewidth=3, linestyle='-', alpha=0.3))

    if cam_x < cnc_width:
        ax.add_patch(Rectangle((cam_x, 0), cnc_width - cam_x, cam_y, facecolor='#FFB6C1', edgecolor='none', alpha=0.3))
    if cam_y < cnc_height:
        ax.add_patch(Rectangle((0, cam_y), cam_x, cnc_height - cam_y, facecolor='#FFB6C1', edgecolor='none', alpha=0.3))
    if cam_x < cnc_width and cam_y < cnc_height:
        ax.add_patch(Rectangle((cam_x, cam_y), cnc_width - cam_x, cnc_height - cam_y, facecolor='#FFB6C1', edgecolor='none', alpha=0.3))

    for segment in segments:
        if isinstance(segment, list) and len(segment) == 2 and all(isinstance(p, tuple) for p in segment):
            (x1, y1), (x2, y2) = segment
            ax.plot([x1, x2], [y1, y2], color="blue", linewidth=1.2)
            ax.arrow(x1, y1, (x2 - x1) * 0.5, (y2 - y1) * 0.5,
                     head_width=10, head_length=20, fc='red', ec='red', length_includes_head=True)
        elif isinstance(segment, tuple):
            shape = segment[0]
            if shape == "circle":
                _, cx, cy, cap = segment
                radius = cap / 2
                ax.add_patch(plt.Circle((cx, cy), radius, fill=False, color="blue", linewidth=1.5))
            elif shape == "ellipse":
                _, cx, cy, a, b = segment
                ax.add_patch(Ellipse((cx, cy), width=a, height=b, angle=0, fill=False, color="blue", linewidth=1.5))
            elif shape == "radius":
                _, x, y, r1, r2, _, _ = segment
                ax.add_patch(Rectangle((x, y), r1, r2, edgecolor="blue", facecolor="none", linewidth=1.5))
            elif shape == "baklava":
                _, cx, cy, w, h = segment
                half_w, half_h = w / 2, h / 2
                diamond = Polygon([
                    (cx, cy + half_h),
                    (cx + half_w, cy),
                    (cx, cy - half_h),
                    (cx - half_w, cy)
                ], closed=True, fill=False, edgecolor="blue", linewidth=1.5)
                ax.add_patch(diamond)

    # Sağ panelde gösterilecek bilgiler
    etiketler = layout_result.get("etiketler", {})
    actual_miktar = etiketler.get("adet") or layout_result.get("adet") or layout_result.get("parca_adedi") or 0

    info_text = (
        f"Şekil: {SHAPE_FIELDS.get(sekil, {}).get('name', sekil)}\n"
        f"Cam Ölçüsü (UI): {cam_x} x {cam_y} mm\n"
        f"Margin: {margin} mm\n"
        f"Kesilecek Parça Ölçüleri:\n"
    )

    if etiketler:
        for k, v in etiketler.items():
            if k != "adet":
                info_text += f"  {k}: {v}\n"
    else:
        for k, v in params.items():
            info_text += f"  {k}: {v}\n"

    info_text += f"Hesaplanan Miktar: {actual_miktar}\n"

    fire_m2 = layout_result.get("fire_m2")
    if fire_m2 is not None:
        info_text += f"\n🔥 Fire Alanı: {fire_m2:.4f} m²"

    # Şekil simgesi gösterimi (images klasöründen .png)
    image_path = os.path.join(os.path.dirname(__file__), "images", f"{sekil.lower()}.png")
    try:
        img = mpimg.imread(image_path)
        ax_img = plt.axes([0.85, 0.4, 0.1, 0.15], frameon=False)
        ax_img.imshow(img)
        ax_img.axis("off")
    except FileNotFoundError:
        # Görsel yoksa hata verme, sessizce geç
        pass

    ax.text(cnc_width + 20, cnc_height / 2, info_text, fontsize=10, color="white", va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="#333333", ec="white", lw=0.5))

    plt.tight_layout()
    plt.show()
    return layout_result
