"""Time consecutive and strided remote ortho reads."""
from __future__ import annotations

import time

import rasterio
from rasterio.windows import Window

ORTHO = (
    "/vsicurl/https://planetarymaps.usgs.gov/mosaic/mars2020_trn/HiRISE/"
    "JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first.tif"
)


def main() -> None:
    with rasterio.Env(
        GDAL_HTTP_TIMEOUT=180,
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
        VSI_CACHE="TRUE",
        VSI_CACHE_SIZE=50000000,
    ):
        with rasterio.open(ORTHO) as src:
            start = time.perf_counter()
            data = src.read(1, window=Window(43000, 50000, 16000, 64))
            print("consecutive64", data.shape, f"{time.perf_counter() - start:.2f}s")
            start = time.perf_counter()
            total = 0
            for index in range(8):
                row = src.read(1, window=Window(43000, 50000 + index * 16, 256, 1))
                total += int(row.mean())
            print("strided8", total, f"{time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
