"""Check whether the USGS ortho and Viking mosaic support a remote window read."""
from __future__ import annotations

import rasterio

ORTHO = (
    "/vsicurl/https://planetarymaps.usgs.gov/mosaic/mars2020_trn/HiRISE/"
    "JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first.tif"
)
VIKING_CANDIDATES = [
    "/vsicurl/https://planetarymaps.usgs.gov/mosaic/Mars_Viking_MDIM21_ClrMosaic_global_232m.tif",
    "/vsicurl/https://planetarymaps.usgs.gov/mosaic/Mars/Mars_Viking_MDIM21_ClrMosaic_global_232m.tif",
]


def describe(url: str) -> None:
    print("OPEN", url)
    with rasterio.open(url) as src:
        print(" size", src.width, src.height, "bands", src.count, "dtype", src.dtypes)
        print(" crs", src.crs)
        print(" transform", src.transform)
        print(" overviews", src.overviews(1) if src.count else None)
        print(" tiled", src.profile.get("tiled"), "block", src.block_shapes[:1])


def main() -> None:
    describe(ORTHO)
    for url in VIKING_CANDIDATES:
        try:
            describe(url)
        except Exception as exc:
            print("FAIL", url, type(exc).__name__, exc)


if __name__ == "__main__":
    main()
