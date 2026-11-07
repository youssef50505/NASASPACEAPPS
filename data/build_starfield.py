"""Generate a subtle, deterministic equirectangular starfield for the Mars globe."""
from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "starfield_equirectangular.png"
WIDTH, HEIGHT = 4096, 2048


def main() -> None:
    rng = np.random.default_rng(40112026)
    y, x = np.mgrid[0:HEIGHT, 0:WIDTH]
    center = HEIGHT * 0.53 + 105 * np.sin(x / WIDTH * math.tau * 1.3 + 0.6)
    distance = (y - center) / 175.0
    band = np.exp(-0.5 * distance * distance)
    noise = rng.normal(0.0, 0.32, (HEIGHT, WIDTH))
    base = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for channel, dark, band_gain in ((0, 2.0, 2.7), (1, 4.0, 3.2), (2, 10.0, 5.0)):
        values = dark + band * band_gain + noise
        base[:, :, channel] = np.clip(values, 0, 255).astype(np.uint8)
    image = Image.fromarray(base, "RGB")
    draw = ImageDraw.Draw(image)
    rand = random.Random(40112026)

    def add_star(px: float, py: float, size: float, color: tuple[int, int, int], glow: bool = False) -> None:
        cx, cy = int(px) % WIDTH, max(0, min(HEIGHT - 1, int(py)))
        if glow:
            halo = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            hdraw = ImageDraw.Draw(halo)
            radius = max(2, int(size * 5))
            hdraw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(*color, 48))
            halo = halo.filter(ImageFilter.GaussianBlur(max(1, radius // 2)))
            image.paste(Image.alpha_composite(image.convert("RGBA"), halo).convert("RGB"))
        radius = max(0.45, size)
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=color)
        if size > 2.0:
            draw.line((cx-int(size*2), cy, cx+int(size*2), cy), fill=tuple(max(0, c-55) for c in color), width=1)
            draw.line((cx, cy-int(size*2), cx, cy+int(size*2)), fill=tuple(max(0, c-55) for c in color), width=1)

    colors = [(182, 205, 255), (216, 226, 255), (255, 248, 232), (255, 219, 173)]
    # Sparse stars across the full sky.
    for _ in range(3000):
        size = rand.choices([0.45, 0.8, 1.15, 1.8, 2.8], weights=[52, 30, 13, 4, 1])[0]
        color = rand.choices(colors, weights=[17, 46, 29, 8])[0]
        add_star(rand.random() * WIDTH, rand.random() * HEIGHT, size, color, glow=size > 1.5)
    # The Milky Way plane is gently denser, without a bright fake nebula.
    for _ in range(3600):
        px = rand.random() * WIDTH
        band_y = HEIGHT * 0.53 + 105 * math.sin(px / WIDTH * math.tau * 1.3 + 0.6)
        py = rand.gauss(band_y, 145)
        size = rand.choices([0.4, 0.65, 0.9, 1.3], weights=[59, 27, 11, 3])[0]
        color = rand.choices(colors, weights=[19, 47, 27, 7])[0]
        add_star(px, py, size, color)
    # A small number of prominent points provide a natural brightness range.
    for _ in range(24):
        px, py = rand.random() * WIDTH, rand.random() * HEIGHT
        size = rand.uniform(2.2, 3.4)
        add_star(px, py, size, rand.choice(colors), glow=True)

    image.save(OUTPUT, optimize=True)
    print(f"Saved {OUTPUT} ({WIDTH}x{HEIGHT})")
    crop = image.crop((1536, 704, 2560, 1344)).resize((1600, 1000), Image.Resampling.LANCZOS)
    crop_path = ROOT / "starfield_globe_camera_crop.png"
    crop.save(crop_path, optimize=True)
    print(f"Saved {crop_path} (1600x1000 camera crop)")


if __name__ == "__main__":
    main()
