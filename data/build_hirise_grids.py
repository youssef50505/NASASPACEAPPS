"""Sample the official USGS HiRISE DTM into Blender-sized elevation grids."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "JEZ_hirise_soc_006_DTM_1m.tif"
OUT = ROOT / "data"
URL = "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/HiRISE/JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40.tif"
LANDING = "https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_hirise_dtm_mosaic"
DOI = "10.5066/P9REJ9JN"


def write_grid(path: Path, src: rasterio.io.DatasetReader, window: Window, stride: int, label: str) -> None:
    sampled = src.read(1, window=window, out_shape=(int(window.height / stride), int(window.width / stride)))
    sampled = sampled.astype("float32", copy=False)
    valid_mask = np.isfinite(sampled) & (sampled > -10000)
    valid = sampled[valid_mask]
    if valid.size == 0:
        raise RuntimeError(f"No valid elevation pixels in {label}")
    sampled[~valid_mask] = float(np.median(valid))
    h, w = sampled.shape
    transform = src.window_transform(window)
    payload = {
        "source": "USGS Astrogeology Mars 2020 TRN HiRISE DTM Mosaic",
        "source_url": URL,
        "landing_page": LANDING,
        "doi": DOI,
        "license": "USGS public planetary data; cite source dataset (metadata states no use restrictions)",
        "native_resolution_m_per_pixel": 1.0,
        "mesh_sample_spacing_m": float(stride),
        "stride_pixels": stride,
        "crs": "Mars 2000 equirectangular, central longitude 0, latitude of true scale 0; meters",
        "source_crs": str(src.crs),
        "window_col_offset": int(window.col_off),
        "window_row_offset": int(window.row_off),
        "window_width_pixels": int(window.width),
        "window_height_pixels": int(window.height),
        "geotransform": list(transform)[:6],
        "grid_width": w,
        "grid_height": h,
        "width_m": (w - 1) * stride,
        "height_m": (h - 1) * stride,
        "elevation_min_m": float(valid.min()),
        "elevation_max_m": float(valid.max()),
        "vertical_exaggeration": 1.0,
        "illustrative_geometry_added": False,
        "grid_role": label,
        "valid_mask": valid_mask.tolist(),
        "elevations_m": sampled.tolist(),
    }
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {path.name}: {w}x{h}, {payload['elevation_min_m']:.2f}..{payload['elevation_max_m']:.2f} m")


def main() -> None:
    with rasterio.open(SOURCE) as src:
        if src.width < 8192 or src.height < 8192:
            raise RuntimeError(f"Unexpected DTM dimensions: {src.width}x{src.height}")
        whole = Window(0, 0, src.width, src.height)
        write_grid(OUT / "jez_hirise_1m_overview_grid.json", src, whole, 40, "Regional overview sampled every 40 m from 1 m DTM")
        size = 4096
        core = Window((src.width - size) // 2, (src.height - size) // 2, size, size)
        write_grid(OUT / "jez_hirise_1m_detail_grid.json", src, core, 4, "Central detail patch sampled every 4 m from 1 m DTM")


if __name__ == "__main__":
    main()
