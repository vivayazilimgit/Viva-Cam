
import os
import importlib
from datetime import datetime
import json

DRAWING_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "drawings", "drawing"))
PLT_HEADER = "IN;VS40;PU;PA;SP1;"
PLT_FOOTER = "PU;SP0;IN;"

def generate_plt_file(shape_name, cam_x, cam_y, margin, params):
    try:
        shape_module = importlib.import_module(f"drawings.shapes.{shape_name.lower()}_shape")
        segments = shape_module.get_segments(cam_x, cam_y, margin, params)

        if not isinstance(segments, list):
            raise ValueError("get_segments fonksiyonu çizgi listesi döndürmelidir.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{shape_name.lower()}_{timestamp}_plt.plt"
        file_path = os.path.join(DRAWING_PATH, filename)
        os.makedirs(DRAWING_PATH, exist_ok=True)

        scale = 40  # 1 mm = 40 plot unit (HPGL)
        commands = [PLT_HEADER]

        for segment in segments:
            x1, y1, x2, y2 = segment
            x1_scaled, y1_scaled = round(x1 * scale), round(y1 * scale)
            x2_scaled, y2_scaled = round(x2 * scale), round(y2 * scale)
            commands.append(f"PU{x1_scaled},{y1_scaled};PD{x2_scaled},{y2_scaled};")

        commands.append(PLT_FOOTER)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("".join(commands))

        return filename
    except Exception as e:
        raise RuntimeError(f"PLT dosyası oluşturulurken hata oluştu: {e}")
