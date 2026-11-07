"""See whether steep slope lies between the crew and the landing site."""
from __future__ import annotations

import math

import numpy as np

SLOPE = r"C:\Users\yhsn5\Downloads\NASASPACEAPP\data\jez_site_slope_4m.npz"
CORE = 1024
SPACING = 4.0
HALF = (CORE - 1) * SPACING / 2.0


def cell(east: float, north: float) -> tuple[int, int]:
    col = int(np.clip(round((east + HALF) / SPACING), 0, CORE - 1))
    row = int(np.clip(round((HALF - north) / SPACING), 0, CORE - 1))
    return row, col


def main() -> None:
    slope = np.load(SLOPE)["slope_deg"]
    start = (14.0, 12.0)
    landing = (512.73, 945.43)
    samples = []
    for t in np.linspace(0, 1, 80):
        east = start[0] + (landing[0] - start[0]) * t
        north = start[1] + (landing[1] - start[1]) * t
        row, col = cell(east, north)
        samples.append(float(slope[row, col]))
    print("line min/mean/max", min(samples), sum(samples) / len(samples), max(samples))
    print("cells >= 15 on line", sum(value >= 15 for value in samples))
    print("cells >= 10 on line", sum(value >= 10 for value in samples))
    steep = np.argwhere(slope >= 15)
    print("steep cells", len(steep), "of", slope.size)
    if len(steep):
        rows, cols = steep[:, 0], steep[:, 1]
        east = cols * SPACING - HALF
        north = HALF - rows * SPACING
        print("steep east", float(east.min()), float(east.max()), "north", float(north.min()), float(north.max()))
        # nearest steep cell to the straight segment midpoint
        mid = np.array([(start[0] + landing[0]) / 2, (start[1] + landing[1]) / 2])
        dist = np.hypot(east - mid[0], north - mid[1])
        index = int(dist.argmin())
        print("nearest steep to mid", float(east[index]), float(north[index]), "dist", float(dist[index]), "slope", float(slope[steep[index][0], steep[index][1]]))


if __name__ == "__main__":
    main()
