import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tkinter import filedialog, messagebox
import os
import re
from config.config_loader import compute_cnc_coordinates  # Dinamik koordinat fonksiyonu eklendi

def parse_plt_file(filepath):
    """
    PLT dosyasını satır satır okuyarak PU/PD komutlarını ayrıştırır.
    Koordinatlar ve kalem (pen) bilgisiyle birlikte liste halinde döner.
    """
    commands = []
    current_pen = "SP1"  # Varsayılan kesim kalemi

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("SP"):
                    current_pen = line[:3]  # Örn: SP1, SP6
                elif line.startswith("PU") or line.startswith("PD"):
                    cmd_type = line[:2]
                    coords_str = line[2:].replace(";", "").strip()
                    parts = re.findall(r'-?\d+', coords_str)
                    if len(parts) == 2:
                        try:
                            x, y = int(parts[0]), int(parts[1])
                            commands.append((cmd_type, (x, y), current_pen))
                        except ValueError:
                            continue
    except Exception as e:
        messagebox.showerror("Hata", f"PLT dosyası okunurken hata: {e}")
        return []

    return commands

def run_simulation_from_plt(filepath=None, interval=300, cam_dims=None):
    """
    PLT dosyasından alınan koordinatları matplotlib ile çizerek simülasyon oluşturur.
    Args:
        filepath: PLT dosyasının tam yolu
        interval: animasyon kare aralığı (ms)
        cam_dims: (cam_x, cam_y) tuple - cam plaka ölçüleri (mm)
    """
    if cam_dims is None:
        messagebox.showerror("Hata", "cam_dims (cam_x, cam_y) simülasyon için gereklidir. Lütfen UI'da cam boyutlarını girin.")
        return

    cam_x, cam_y = cam_dims

    # CNC koordinatları hesapla (ileride ihtiyaç olursa kullanılır)
    cnc_coords = compute_cnc_coordinates(cam_x, cam_y)

    if filepath is None:
        filepath = filedialog.askopenfilename(filetypes=[("PLT dosyaları","*.plt")])
        if not filepath:
            return

    filename = os.path.basename(filepath)
    commands_raw = parse_plt_file(filepath)

    if not commands_raw:
        messagebox.showinfo("Simülasyon", "PLT dosyasında çizim komutları bulunamadı veya ayrıştırılamadı. Simülasyon başlatılamıyor.")
        return

    # PLT dosyasındaki mutlak koordinat sınırlarını bul (SP6 çerçeve dahil)
    all_mx = [pt[0] for _, pt in commands_raw]
    all_my = [pt[1] for _, pt in commands_raw]
    min_mx, max_mx = min(all_mx), max(all_mx)
    min_my, max_my = min(all_my), max(all_my)

    # Koordinatları normalize edip cam boyutuna göre dönüştür
    commands_converted = []
    for cmd, (mx, my), pen in commands_raw:
        sx = (mx - min_mx) * cam_x / (max_mx - min_mx)
        sy = cam_y - ((my - min_my) * cam_y / (max_my - min_my))
        commands_converted.append((cmd, (sx, sy), pen))

    print(f"İlk 5 dönüştürülmüş koordinat: {commands_converted[:5]}")

    segments = []
    last_pt = None
    last_pen = "SP1"

    for cmd, pt, pen in commands_converted:
        if cmd == "PU":
            last_pt = pt
            last_pen = pen
        elif cmd == "PD" and last_pt is not None:
            segments.append((last_pt, pt, last_pen))
            last_pt = pt
            last_pen = pen

    if not segments:
        messagebox.showinfo("Simülasyon", "PLT dosyasından çizim segmenti oluşturulamadı. Simülasyon başlatılamıyor. Lütfen PLT dosyasını kontrol edin.")
        return

    print(f"{len(segments)} çizim segmenti oluşturuldu.")

    fig, ax = plt.subplots(figsize=(12, 8))
    from matplotlib.patches import Rectangle

    # Cam kesim alanı (yeşil çerçeve)
    ax.add_patch(Rectangle((0, 0), cam_x, cam_y, fill=False, edgecolor='green', linewidth=2, linestyle='--'))

    # SP6 dış çerçeve alanı (kırmızı çerçeve)
    ax.add_patch(Rectangle((0, 0), cam_x, cam_y, fill=False, edgecolor='red', linewidth=2, linestyle=':'))

    # Kaleme göre renk haritası
    pen_colors = {
        "SP1": "blue",     # Kesim kalemi
        "SP2": "green",
        "SP3": "orange",
        "SP4": "purple",
        "SP5": "cyan",
        "SP6": "red"        # Dış çerçeve
    }

    # Segment çizimleri
    for i, (start, end, pen) in enumerate(segments):
        color = pen_colors.get(pen, "gray")  # Tanımsız kalemler için gri
        ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=1.5, alpha=0.7)
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, str(i), fontsize=6, color='black')

    # Tüm PU/PD noktalarını küçük kırmızı noktalarla göster
    for cmd, (x, y), _ in commands_converted:
        ax.scatter(x, y, color='red', s=10, alpha=0.7)

    try:
        fig.canvas.manager.set_window_title(f"Cam Kesim Simülasyonu: {filename}")
    except Exception:
        pass

    ax.set_xlim(-10, cam_x + 10)
    ax.set_ylim(-10, cam_y + 10)
    ax.set_aspect('equal')

    # Başlık ve etiketler
    frame_text = fig.text(0.01, 0.95, '', fontsize=12, color='red', bbox=dict(facecolor='white', alpha=0.6))
    ax.set_title(f"PLT Simülasyonu: {filename}")
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')

    # Animasyon öğeleri
    line, = ax.plot([], [], lw=1.5, color='blue')
    pen_dot, = ax.plot([], [], 'ro', markersize=6)

    x_data, y_data = [], []

    def init():
        line.set_data([], [])
        pen_dot.set_data([], [])
        return line, pen_dot

    def update(frame):
        print(f"Frame {frame}: Başlangıç noktası: {segments[frame][0]}, Bitiş noktası: {segments[frame][1]}")
        start_pt, end_pt, pen = segments[frame]
        color = pen_colors.get(pen, "blue")
        line.set_color(color)
        pen_dot.set_data([end_pt[0]], [end_pt[1]])
        x_data.append(start_pt[0])
        x_data.append(end_pt[0])
        y_data.append(start_pt[1])
        y_data.append(end_pt[1])
        line.set_data(x_data, y_data)
        frame_text.set_text(f"Adım: {frame + 1}/{len(segments)}")
        return line, pen_dot

    ani = animation.FuncAnimation(fig, update, frames=len(segments),
                                  init_func=init, blit=False, interval=interval, repeat=False)

    def on_close(event):
        plt.close(fig)

    fig.canvas.mpl_connect('close_event', on_close)
    plt.show()
