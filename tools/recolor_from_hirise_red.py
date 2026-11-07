"""Rebuild the color PNG from the saved HiRISE red crop and the Viking bright-site hue."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RED = ROOT / "data" / "jez_hirise_site_hirise_red_1m.png"
COLOR = ROOT / "data" / "jez_hirise_site_nasa_color_1m.png"
PROVENANCE = ROOT / "data" / "jez_site_color_provenance.json"


def main() -> None:
    gray = np.asarray(Image.open(RED), dtype=np.float32) / 255.0
    bright = np.array([140, 103, 96, 126, 89, 79], dtype=np.float32).reshape(2, 3).mean(axis=0)
    luma = float(bright @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))
    hue = bright / luma
    color = np.clip(gray[..., None] * hue, 0.0, 1.0)
    image = np.rint(color * 255.0).astype(np.uint8)
    Image.fromarray(image, "RGB").save(COLOR, optimize=True)
    meta = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    meta["viking_role"] = (
        "Hue only, from bright control samples in the same mosaic. "
        "Jezero raw DNs are about 30 and blue-biased, so they are not used as the surface hue."
    )
    meta["viking_bright_controls"] = {
        "arabia_terra_30e_20n_dn": [140, 103, 96],
        "olympus_mons_dn": [126, 89, 79],
    }
    meta["color_equation"] = "RGB = clip(HiRISE_DN/255 * mean(Viking_bright_RGB) / Viking_bright_luma)"
    meta["output_mean_rgb"] = [round(float(image[:, :, band].mean()), 2) for band in range(3)]
    PROVENANCE.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("mean", meta["output_mean_rgb"], "hue", [round(float(v), 3) for v in hue])


if __name__ == "__main__":
    main()
