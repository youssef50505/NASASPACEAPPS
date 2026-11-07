"""Crop the USGS HiRISE Jezero orthomosaic and tint it with Viking color.

The crop matches the existing 4 m site mesh: UV 0 and 1 sit on the first and
last elevation samples. Vertices, scale, and placement are not touched here.
HiRISE supplies the surface brightness. Viking supplies only the low-frequency
color, because the orthomosaic is a single red-band 8-bit image.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parents[1]
GRID_JSON = ROOT / "data" / "jez_hirise_site_detail_4m.json"
ORTHO_URL = (
    "https://planetarymaps.usgs.gov/mosaic/mars2020_trn/HiRISE/"
    "JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first.tif"
)
VIKING_URL = "https://planetarymaps.usgs.gov/mosaic/Mars_Viking_MDIM21_ClrMosaic_global_232m.tif"
ORTHO_PAGE = "https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_hirise_orthorectified_image_mosaic"
VIKING_PAGE = "https://planetarymaps.usgs.gov/mosaic/Mars_Viking_MDIM21_ClrMosaic_global_232m.tif"
ORTHO_DOI = "10.5066/P9QJDP48"
SIZE = 4096
GDAL_ENV = {
    "GDAL_HTTP_TIMEOUT": 300,
    "GDAL_HTTP_MAX_RETRY": 4,
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
    "VSI_CACHE": "TRUE",
    "VSI_CACHE_SIZE": 200000000,
}


def grid_meta() -> dict:
    raw = GRID_JSON.read_text(encoding="utf-8")
    cut = raw.find(',"valid_mask"')
    return json.loads(raw[:cut] + "}")


def sample_bounds(meta: dict) -> tuple[float, float, float, float]:
    # geotransform is the 4096 m source window, not the full mosaic.
    origin_x = float(meta["geotransform"][2])
    origin_y = float(meta["geotransform"][5])
    samples = int(meta["grid_width"])
    spacing = float(meta["mesh_sample_spacing_m"])
    x_west = origin_x + 0.5 * spacing
    x_east = origin_x + (samples - 0.5) * spacing
    y_north = origin_y - 0.5 * spacing
    y_south = origin_y - (samples - 0.5) * spacing
    return x_west, y_south, x_east, y_north


def pixel_index(values: np.ndarray, origin: float, scale: float) -> np.ndarray:
    return np.rint((values - origin) / scale).astype(np.int64)


def read_indexed(src: rasterio.DatasetReader, rows: np.ndarray, cols: np.ndarray, band: int) -> np.ndarray:
    image = np.zeros((rows.size, cols.size), dtype=np.uint8)
    row_min = int(rows.min())
    row_max = int(rows.max())
    col_min = int(max(0, cols.min()))
    col_max = int(min(src.width - 1, cols.max()))
    width = col_max - col_min + 1
    block = 512
    total = row_max - row_min + 1
    done = 0
    for row0 in range(row_min, row_max + 1, block):
        row1 = min(row0 + block - 1, row_max)
        data = src.read(band, window=Window(col_min, row0, width, row1 - row0 + 1))
        selected = np.flatnonzero((rows >= row0) & (rows <= row1))
        local_rows = rows[selected] - row0
        local_cols = np.clip(cols, col_min, col_max) - col_min
        image[selected] = data[local_rows][:, local_cols]
        done += row1 - row0 + 1
        print(f"band {band}: {done}/{total} source rows", flush=True)
    return image


def main() -> None:
    meta = grid_meta()
    left, bottom, right, top = sample_bounds(meta)
    xs = np.linspace(left, right, SIZE)
    ys = np.linspace(top, bottom, SIZE)
    print(f"crop bounds m: left={left:.3f} bottom={bottom:.3f} right={right:.3f} top={top:.3f}", flush=True)

    with rasterio.Env(**GDAL_ENV):
        with rasterio.open(f"/vsicurl/{ORTHO_URL}") as ortho:
            if ortho.crs is None or ortho.count != 1:
                raise RuntimeError(f"Unexpected orthomosaic: {ortho.crs}, bands={ortho.count}")
            cols = pixel_index(xs, ortho.transform.c, ortho.transform.a)
            rows = pixel_index(ys, ortho.transform.f, ortho.transform.e)
            if cols.min() < 0 or rows.min() < 0 or cols.max() >= ortho.width or rows.max() >= ortho.height:
                raise RuntimeError(
                    f"Ortho crop falls outside the mosaic: rows {rows.min()}..{rows.max()} "
                    f"cols {cols.min()}..{cols.max()} size {ortho.width}x{ortho.height}"
                )
            print(
                f"ortho {ortho.width}x{ortho.height} pixel {ortho.transform.a} m, "
                f"rows {rows.min()}..{rows.max()} cols {cols.min()}..{cols.max()}",
                flush=True,
            )
            gray = read_indexed(ortho, rows, cols, 1)

        with rasterio.open(f"/vsicurl/{VIKING_URL}") as viking:
            if viking.count < 3:
                raise RuntimeError("Viking mosaic does not have three color bands")
            v_cols = pixel_index(xs, viking.transform.c, viking.transform.a)
            v_rows = pixel_index(ys, viking.transform.f, viking.transform.e)
            print(
                f"viking rows {v_rows.min()}..{v_rows.max()} cols {v_cols.min()}..{v_cols.max()}",
                flush=True,
            )
            viking_rgb = np.stack([read_indexed(viking, v_rows, v_cols, band) for band in (1, 2, 3)], axis=-1)

    gray_f = gray.astype(np.float32) / 255.0
    # Jezero's own Viking DNs are near 30 and blue-biased in this mosaic.
    # Bright control sites in the same file are the stable orange balance.
    bright_rgb = np.array([[140, 103, 96], [126, 89, 79]], dtype=np.float32).mean(axis=0)
    bright_luma = float(bright_rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))
    hue = bright_rgb / bright_luma
    colored = np.clip(gray_f[..., None] * hue, 0.0, 1.0)
    color_u8 = np.rint(colored * 255.0).astype(np.uint8)

    color_path = ROOT / "data" / "jez_hirise_site_nasa_color_1m.png"
    red_path = ROOT / "data" / "jez_hirise_site_hirise_red_1m.png"
    Image.fromarray(color_u8, "RGB").save(color_path, optimize=True)
    Image.fromarray(gray, "L").save(red_path, optimize=True)

    raw = GRID_JSON.read_text(encoding="utf-8")
    grid = json.loads(raw)
    elev = np.asarray(grid["elevations_m"], dtype=np.float32)
    reference = float(grid["center_reference_elevation_m"])
    local_z = elev - reference
    lo = float(local_z.min())
    hi = float(local_z.max())
    span = hi - lo if hi > lo else 1.0
    height_u16 = np.rint((local_z - lo) / span * 65535.0).astype(np.uint16)
    height_path = ROOT / "data" / "jez_hirise_site_height_4m.png"
    Image.fromarray(height_u16, "I;16").save(height_path)

    dz_y, dz_x = np.gradient(local_z, float(meta["mesh_sample_spacing_m"]))
    slope = np.degrees(np.arctan(np.hypot(dz_x, dz_y))).astype(np.float32)
    slope_path = ROOT / "data" / "jez_site_slope_4m.npz"
    np.savez_compressed(slope_path, slope_deg=slope, local_z_m=local_z.astype(np.float32))

    provenance = {
        "color_png": color_path.name,
        "red_png": red_path.name,
        "height_png": height_path.name,
        "slope_npz": slope_path.name,
        "output_pixels": SIZE,
        "mesh_sample_spacing_m": meta["mesh_sample_spacing_m"],
        "bounds_m": {"left": left, "bottom": bottom, "right": right, "top": top},
        "bounds_match": "UV 0/1 on NASA_HiRISE_DTM_Jezero_FieldSite_4m map to the first and last 4 m elevation samples",
        "hirise_product": "USGS Mars 2020 TRN HiRISE Orthorectified Image Mosaic",
        "hirise_url": ORTHO_URL,
        "hirise_page": ORTHO_PAGE,
        "hirise_doi": ORTHO_DOI,
        "hirise_native_m_per_pixel": 0.25,
        "hirise_runtime_sampling": "nearest source pixel at about 1 m across the 4092 m vertex span",
        "hirise_bands": "single 8-bit red-filter orthomosaic; brightness only, not calibrated I/F",
        "viking_product": "NASA/JPL/USGS Viking MDIM 2.1 global color mosaic, 232 m",
        "viking_url": VIKING_URL,
        "viking_role": "Hue only, from bright control samples in the same mosaic. Jezero raw DNs are about 30 and blue-biased, so they are not used as the surface hue.",
        "viking_bright_controls": {
            "arabia_terra_30e_20n_dn": [140, 103, 96],
            "olympus_mons_dn": [126, 89, 79],
        },
        "color_equation": "RGB = clip(HiRISE_DN/255 * mean(Viking_bright_RGB) / Viking_bright_luma)",
        "height_source_doi": meta["doi"],
        "height_range_local_m": [lo, hi],
        "slope_min_deg": float(slope.min()),
        "slope_max_deg": float(slope.max()),
        "site_latitude_north_deg": meta["site_center_latitude_north_deg"],
        "site_longitude_east_deg": meta["site_center_longitude_east_deg"],
        "illustrative": False,
    }
    (ROOT / "data" / "jez_site_color_provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )
    print(
        f"wrote {color_path.name} gray {int(gray.min())}..{int(gray.max())} "
        f"slope {slope.min():.2f}..{slope.max():.2f} deg",
        flush=True,
    )


if __name__ == "__main__":
    main()
