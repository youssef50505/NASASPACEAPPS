"""Downsample the USGS Mars 2020 TRN CTX DTM to a Blender-friendly grid."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "JEZ_ctx_B_soc_008_DTM_20m.tif"
OUTPUT = ROOT / "data" / "jez_ctx_20m_grid.json"
STRIDE = 4  # 80 m mesh spacing; elevations remain sampled from the 20 m DTM.
PIXEL_SIZE_M = 20
ORIGIN_EASTING_M = 4573663.250853
ORIGIN_NORTHING_M = 1109693.140188


def main() -> None:
    with Image.open(SOURCE) as image:
        image.load()
        width, height = image.size
        sampled = [
            [round(float(image.getpixel((x, y))), 3) for x in range(0, width, STRIDE)]
            for y in range(0, height, STRIDE)
        ]

    flat = [value for row in sampled for value in row]
    payload = {
        "source": "USGS Astrogeology Mars 2020 TRN CTX DTM Mosaic",
        "source_url": "https://planetarymaps.usgs.gov/mosaic/mars2020_trn/CTX/JEZ_ctx_B_soc_008_DTM_MOLAtopography_DeltaGeoid_20m_Eqc_latTs0_lon0.tif",
        "landing_page": "https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic",
        "doi": "10.5066/P906QQT8",
        "license": "CC0 1.0 Universal",
        "native_resolution_m_per_pixel": PIXEL_SIZE_M,
        "mesh_sample_spacing_m": PIXEL_SIZE_M * STRIDE,
        "stride_pixels": STRIDE,
        "crs": "Equirectangular Mars, central longitude 0, latitude of true scale 0; source GeoTIFF georeferencing retained in metadata",
        "geotiff_origin_easting_m": ORIGIN_EASTING_M,
        "geotiff_origin_northing_m": ORIGIN_NORTHING_M,
        "grid_width": len(sampled[0]),
        "grid_height": len(sampled),
        "width_m": (width - 1) * PIXEL_SIZE_M,
        "height_m": (height - 1) * PIXEL_SIZE_M,
        "elevation_min_m": min(flat),
        "elevation_max_m": max(flat),
        "vertical_exaggeration": 1.0,
        "illustrative_geometry_added": False,
        "elevations_m": sampled,
    }
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUTPUT} | {payload['grid_width']}x{payload['grid_height']} | "
          f"{payload['elevation_min_m']:.2f}..{payload['elevation_max_m']:.2f} m")


if __name__ == "__main__":
    main()
