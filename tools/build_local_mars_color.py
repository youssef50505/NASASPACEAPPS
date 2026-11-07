"""Crop HiRISE approximate-true-color ESP_045994_1985 onto the existing site window.

Pixels outside the color product, and null pixels inside it, keep the current
HiRISE-brightness tint. The mesh is not touched.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
JP2 = ROOT / "data" / "ESP_045994_1985_MRGB.JP2"
BASE = ROOT / "data" / "jez_hirise_site_nasa_color_1m.png"
OUT = ROOT / "data" / "jez_hirise_site_local_rgb_1m.png"
PROVENANCE = ROOT / "data" / "jez_site_local_color_provenance.json"
PRIOR = ROOT / "data" / "jez_site_color_provenance.json"
SIZE = 4096
MARS_RADIUS_M = 3_396_190.0
MAP_RES = 118502.26464032
COS_CENTER = math.cos(math.radians(15.0))
WEST = 77.382125238101
MAX_LAT = 18.550007435058


def main() -> None:
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    bounds = prior["bounds_m"]
    left, right = bounds["left"], bounds["right"]
    bottom, top = bounds["bottom"], bounds["top"]

    def pixel(x_m: float, y_m: float) -> tuple[float, float]:
        lon = math.degrees(x_m / MARS_RADIUS_M)
        lat = math.degrees(y_m / MARS_RADIUS_M)
        sample = (lon - WEST) * MAP_RES * COS_CENTER
        line = (MAX_LAT - lat) * MAP_RES
        return sample, line

    corners = [pixel(x, y) for x, y in ((left, top), (right, top), (left, bottom), (right, bottom))]
    samples = [item[0] for item in corners]
    lines = [item[1] for item in corners]
    with rasterio.open(JP2) as src:
        col0 = max(0, int(math.floor(min(samples))))
        row0 = max(0, int(math.floor(min(lines))))
        col1 = min(src.width, int(math.ceil(max(samples))) + 1)
        row1 = min(src.height, int(math.ceil(max(lines))) + 1)
        window = rasterio.windows.Window(col0, row0, col1 - col0, row1 - row0)
        raw = src.read(window=window)
    print("source window", col0, row0, col1 - col0, row1 - row0, "bands", raw.shape[0])
    # Source axes are line, sample. Output row 0 is north.
    out_sample = (np.linspace(left, right, SIZE) / MARS_RADIUS_M) * (180.0 / math.pi)
    out_line_y = np.linspace(top, bottom, SIZE)
    sample_index = (out_sample - WEST) * MAP_RES * COS_CENTER - col0
    line_index = (MAX_LAT - np.degrees(out_line_y / MARS_RADIUS_M)) * MAP_RES - row0
    col_i = np.clip(np.rint(sample_index).astype(np.int32), 0, raw.shape[2] - 1)
    row_i = np.clip(np.rint(line_index).astype(np.int32), 0, raw.shape[1] - 1)
    sampled = raw[:, row_i[:, None], col_i[None, :]]
    rgb = np.moveaxis(sampled[:3], 0, 2).astype(np.uint8)
    means = rgb.reshape(-1, 3).mean(axis=0)
    print("sampled mean rgb", [round(float(v), 2) for v in means])
    if means[2] > means[0] * 1.15 and means[2] > means[1]:
        raise RuntimeError("Sampled image is blue-dominant, so it is not the approximate-true-color RGB product")
    base = np.asarray(Image.open(BASE).convert("RGB"))
    if base.shape != rgb.shape:
        raise RuntimeError(f"Base color shape {base.shape} does not match {rgb.shape}")
    chroma = rgb.max(axis=2).astype(np.int16) - rgb.min(axis=2).astype(np.int16)
    column = chroma.mean(axis=0)
    # The merged product is full-width, but the BG color CCDs cover only the center strip.
    # Gray wings are the red mosaic, so they stay on the existing brightness tint.
    colored = column > 1.5
    if not colored.any():
        raise RuntimeError("No approximate-true-color strip was found in this window")
    span_m = float(bounds["right"] - bounds["left"])
    ramp = max(1, int(round(30.0 / span_m * SIZE)))
    colored_index = np.flatnonzero(colored)
    left_edge = int(colored_index[0])
    right_edge = int(colored_index[-1])
    weight = np.zeros(SIZE, dtype=np.float32)
    weight[left_edge:right_edge + 1] = 1.0
    fade_in = np.linspace(0.0, 1.0, ramp, endpoint=False, dtype=np.float32)
    fade_out = np.linspace(1.0, 0.0, ramp, endpoint=False, dtype=np.float32)
    left_cols = np.arange(left_edge - ramp, left_edge)
    right_cols = np.arange(right_edge + 1, right_edge + 1 + ramp)
    left_ok = (left_cols >= 0) & (left_cols < SIZE)
    right_ok = (right_cols >= 0) & (right_cols < SIZE)
    weight[left_cols[left_ok]] = fade_in[left_ok]
    weight[right_cols[right_ok]] = fade_out[: int(right_ok.sum())]
    blend = weight[None, :, None]
    composite = np.clip(rgb.astype(np.float32) * blend + base.astype(np.float32) * (1.0 - blend), 0, 255).astype(np.uint8)
    valid = weight > 0.5
    Image.fromarray(composite, "RGB").save(OUT, optimize=True)
    covered = float(valid.mean())
    record = {
        "output_png": OUT.name,
        "fallback_png": BASE.name,
        "product": "HiRISE merged RGB, approximate true color, observation ESP_045994_1985",
        "observation_id": "ESP_045994_1985",
        "product_file": "ESP_045994_1985_MRGB.JP2",
        "doi": None,
        "url": "https://hirise-pds.lpl.arizona.edu/PDS/EXTRAS/RDR/ESP/ORB_045900_045999/ESP_045994_1985/ESP_045994_1985_MRGB.JP2",
        "label_url": "https://hirise-pds.lpl.arizona.edu/PDS/EXTRAS/RDR/ESP/ORB_045900_045999/ESP_045994_1985/ESP_045994_1985_MRGB.LBL",
        "observation_page": "https://www.uahirise.org/ESP_045994_1985",
        "credit": "NASA/JPL-Caltech/UArizona",
        "license": "Public domain",
        "false_color": False,
        "irb_used_as_surface_color": False,
        "stretch": "HiRISE NORMAL_STRETCH relative DN, not calibrated reflectance",
        "map_scale_m_per_pixel": 0.5,
        "coverage_fraction_of_4096_window": round(covered, 4),
        "color_strip": "HiRISE BG color CCDs cover the center of the red image. Gray wings keep the earlier HiRISE-brightness tint.",
        "edge_blend_m": 30,
        "bounds_m": bounds,
        "outside_footprint": "Existing HiRISE red brightness with the bright-site Viking hue is retained where this product is null.",
        "mesh_unchanged": True,
    }
    PROVENANCE.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("coverage", record["coverage_fraction_of_4096_window"], "wrote", OUT)


if __name__ == "__main__":
    main()
