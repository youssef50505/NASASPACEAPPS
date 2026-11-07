"""Create a source-backed HiRISE crop centered on the actual Jezero field site."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "JEZ_hirise_soc_006_DTM_1m.tif"
OUTPUT = ROOT / "data" / "jez_hirise_site_detail_4m.json"
LANDING_PAGE = "https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_hirise_dtm_mosaic"
SOURCE_URL = "https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/HiRISE/JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40.tif"
DOI = "10.5066/P9REJ9JN"
SITE_LAT_DEG = 18.42875
SITE_LON_EAST_DEG = 77.44215
MARS_RADIUS_M = 3_396_190.0
WINDOW_SIZE_M = 4096
SAMPLE_SPACING_M = 4


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    with rasterio.open(SOURCE) as src:
        if src.crs is None or src.width != 21_400 or src.height != 21_488:
            raise RuntimeError(f"Unexpected source raster: {src.crs}, {src.width} x {src.height}")

        # The product uses Mars equirectangular coordinates (R=3,396,190 m).
        # Convert the source terrain's recorded lat/lon to meters, then use the
        # GeoTIFF affine transform to select a crop centered on the actors.
        x_m = MARS_RADIUS_M * math.radians(SITE_LON_EAST_DEG)
        y_m = MARS_RADIUS_M * math.radians(SITE_LAT_DEG)
        center_row, center_col = src.index(x_m, y_m)
        start_col = center_col - WINDOW_SIZE_M // 2
        start_row = center_row - WINDOW_SIZE_M // 2
        window = Window(start_col, start_row, WINDOW_SIZE_M, WINDOW_SIZE_M)
        if start_col < 0 or start_row < 0 or start_col + WINDOW_SIZE_M > src.width or start_row + WINDOW_SIZE_M > src.height:
            raise RuntimeError("The requested Jezero site crop falls outside the HiRISE mosaic")

        out_size = WINDOW_SIZE_M // SAMPLE_SPACING_M
        elev = src.read(
            1,
            window=window,
            out_shape=(out_size, out_size),
            resampling=Resampling.average,
        ).astype("float32", copy=False)
        valid = np.isfinite(elev) & (elev > -10_000)
        if not valid.any():
            raise RuntimeError("No valid HiRISE elevation samples in the site crop")
        fill = float(np.median(elev[valid]))
        elev[~valid] = fill
        transform = src.window_transform(window)
        center_sample = float(elev[out_size // 2, out_size // 2])

        payload = {
            "product": "USGS Mars 2020 TRN HiRISE DTM Mosaic",
            "source_path": str(SOURCE),
            "source_url": SOURCE_URL,
            "landing_page": LANDING_PAGE,
            "doi": DOI,
            "source_crs": str(src.crs),
            "working_crs": "Mars 2000 equirectangular, central longitude 0, latitude of true scale 0; meters",
            "native_resolution_m_per_pixel": 1.0,
            "mesh_sample_spacing_m": float(SAMPLE_SPACING_M),
            "resampling": "average over source pixels per output sample",
            "vertical_exaggeration": 1.0,
            "illustrative_geometry_added_inside_data_core": False,
            "site_center_latitude_north_deg": SITE_LAT_DEG,
            "site_center_longitude_east_deg": SITE_LON_EAST_DEG,
            "mars_radius_used_for_projection_m": MARS_RADIUS_M,
            "center_source_row": int(center_row),
            "center_source_col": int(center_col),
            "window_row_offset": int(start_row),
            "window_col_offset": int(start_col),
            "window_width_pixels": WINDOW_SIZE_M,
            "window_height_pixels": WINDOW_SIZE_M,
            "geotransform": list(transform)[:6],
            "grid_width": out_size,
            "grid_height": out_size,
            "width_m": (out_size - 1) * SAMPLE_SPACING_M,
            "height_m": (out_size - 1) * SAMPLE_SPACING_M,
            "valid_samples": int(valid.sum()),
            "nodata_samples": int(valid.size - valid.sum()),
            "elevation_min_m": float(elev[valid].min()),
            "elevation_max_m": float(elev[valid].max()),
            "elevation_mean_m": float(elev[valid].mean(dtype=np.float64)),
            "center_reference_elevation_m": center_sample,
            "valid_mask": valid.tolist(),
            "elevations_m": elev.tolist(),
        }
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(
        f"Wrote {OUTPUT.name}: {out_size}x{out_size}, spacing={SAMPLE_SPACING_M} m, "
        f"valid={payload['valid_samples']}, elevation={payload['elevation_min_m']:.3f}.."
        f"{payload['elevation_max_m']:.3f} m, center={center_sample:.3f} m"
    )


if __name__ == "__main__":
    main()
