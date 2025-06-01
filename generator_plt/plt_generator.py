import os
import json
import importlib
from typing import List, Tuple
from config.config_loader import (
    get_cnc_limits,
    get_default_margin,
    get_default_cut_speed
)

HPGL_UNITS_PER_MM = 40

def convert_coords(x_mm: float, y_mm: float) -> Tuple[int, int]:
    x_hpgl = int(round(x_mm * HPGL_UNITS_PER_MM))
    y_hpgl = int(round(y_mm * HPGL_UNITS_PER_MM))
    return x_hpgl, y_hpgl

def generate_hpgl_header(speed: int = 80) -> List[str]:
    return [
        "IN;",
        *[f"VS{speed},{i};" for i in range(1, 9)],
        "WU0;",
        *[f"PW0.350,{i};" for i in range(1, 9)],
        "LT;",
        "SP1;"
    ]
def generate_cutting_lines(segments: List[List[Tuple[float, float]]]) -> List[str]:
    lines = []
    for segment in segments:
        if len(segment) < 2:
            continue
        x0, y0 = convert_coords(*segment[0])
        lines.append(f"PU{x0} {y0};")
        for pt in segment[1:]:
            x, y = convert_coords(*pt)
            lines.append(f"PD{x} {y};")
    return lines
def generate_frame(cam_x: float, cam_y: float) -> List[str]:
    points = [
        (0, 0),
        (cam_x, 0),
        (cam_x, cam_y),
        (0, cam_y),
        (0, 0)
    ]
    commands = [
        "VS1;",
        "PW0.0;",
        "SP6;"  # Görsel çerçeve kalemi
    ]
    for i, pt in enumerate(points):
        x, y = convert_coords(*pt)
        cmd = "PD" if i > 0 else "PU"
        commands.append(f"{cmd}{x} {y};")
    commands.append("PU0 0;")
    commands.append("SP0;")
    commands.append("IN;")
    return commands

def save_hpgl_file(cam_x: float, cam_y: float,
                   part_x: float, part_y: float,
                   segments: List[List[Tuple[float, float]]],
                   margin: float = None,
                   speed: int = None,
                   shape_name: str = "Shape") -> str:
    max_width, max_height = get_cnc_limits()
    margin = margin if margin is not None else get_default_margin()
    speed = speed if speed is not None else get_default_cut_speed()

    cam_x = min(cam_x, max_width - margin)
    cam_y = min(cam_y, max_height - margin)

    lines = []
    lines.extend(generate_hpgl_header(speed))
    lines.extend(generate_cutting_lines(segments))
    lines.extend(generate_frame(cam_x, cam_y))

    os.makedirs("exports_plt", exist_ok=True)
    filename = f"{shape_name}_{part_x}x{part_y}_cam_{int(cam_x)}x{int(cam_y)}.plt"
    filepath = os.path.join("exports_plt", filename)

    with open(filepath, "w", newline="\n") as f:
        f.write("\n".join(lines))

    return filepath

def generate_plt_file_from_ui(sekil: str, cam_x: float, cam_y: float, margin: float, parametreler: dict) -> str:
    sekil_lower = sekil.lower()

    try:
        module = importlib.import_module(f"drawings.{sekil_lower}_draw")
        segments = module.get_cizgi_listesi(
            cam_x, cam_y, margin, parametreler,
            save_json=False, show_terminal_log=False
        )

        part_x = parametreler.get("Genislik", parametreler.get("genislik", 0))
        part_y = parametreler.get("Yukseklik", parametreler.get("yukseklik", 0))
        speed = parametreler.get("speed", get_default_cut_speed())

        return save_hpgl_file(
            cam_x=cam_x,
            cam_y=cam_y,
            part_x=part_x,
            part_y=part_y,
            segments=segments,
            margin=margin,
            speed=speed,
            shape_name=sekil
        )

    except Exception as e:
        raise RuntimeError(f"PLT dosyası oluşturulurken hata oluştu: {e}")
