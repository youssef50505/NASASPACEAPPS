"""Print the Viking colors sampled over the Jezero site."""
from __future__ import annotations

import math

import rasterio

URL = "/vsicurl/https://planetarymaps.usgs.gov/mosaic/Mars_Viking_MDIM21_ClrMosaic_global_232m.tif"
R = 3_396_190.0


def main() -> None:
    x = R * math.radians(77.44215)
    y = R * math.radians(18.42875)
    with rasterio.Env(GDAL_HTTP_TIMEOUT=120, GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(URL) as src:
            print("crs", src.crs)
            print("count", src.count, "dtype", src.dtypes, "colorinterp", src.colorinterp)
            places = {
                "jezero": (77.44215, 18.42875),
                "arabia": (30.0, 20.0),
                "olympus": -133.8,
            }
            for name, lon, lat in (
                ("jezero", 77.44215, 18.42875),
                ("arabia", 30.0, 20.0),
                ("olympus", -133.8, 18.6),
                ("south_pole", 0.0, -85.0),
            ):
                row, col = src.index(R * math.radians(lon), R * math.radians(lat))
                data = src.read(window=rasterio.windows.Window(col, row, 1, 1))
                print(name, int(data[0, 0, 0]), int(data[1, 0, 0]), int(data[2, 0, 0]))


if __name__ == "__main__":
    main()
