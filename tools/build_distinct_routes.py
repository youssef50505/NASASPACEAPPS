"""Rebuild three measured routes that separate around steep HiRISE slope.

The shortest line may cross moderate slope. The safest line stays clear of
cells at or above 15 degrees. The science line is the safe line through the
published Rochette sample site when that site is inside this window.
"""
from __future__ import annotations

import heapq
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SLOPE_PATH = ROOT / "data" / "jez_site_slope_4m.npz"
OUT = ROOT / "data" / "jez_distinct_routes.json"
CORE = 1024
SPACING = 4.0
STRIDE = 2
SIDE = CORE // STRIDE
CELL = SPACING * STRIDE
HALF = (CORE - 1) * SPACING / 2.0
MARS_RADIUS_M = 3_396_190.0
SITE_LAT = 18.42875
SITE_LON = 77.44215
SAFE_DEG = 15.0
SHORT_DEG = 28.0
CLEARANCE_M = 48.0
MIN_SEPARATION_M = 40.0
ROCHETTE = {
    "name": "Rochette",
    "latitude_north_deg": 18.43074404942975,
    "longitude_east_deg": 77.44434866599056,
    "source": "Named Perseverance sample locality (Montdenier and Montagnac). Coordinate from the compiled Perseverance landmark list.",
    "source_url": "https://www.rab-software.de/_assetbundles/mars/perseverance_landmarks.csv",
}


def local_xy(lat: float, lon: float) -> tuple[float, float]:
    east = MARS_RADIUS_M * math.radians(lon - SITE_LON)
    north = MARS_RADIUS_M * math.radians(lat - SITE_LAT)
    return east, north


def cell_of(east: float, north: float) -> tuple[int, int]:
    col = int(np.clip(round((east + HALF) / CELL), 0, SIDE - 1))
    row = int(np.clip(round((HALF - north) / CELL), 0, SIDE - 1))
    return row, col


def cell_center(row: int, col: int) -> tuple[float, float]:
    src_c = min(CORE - 1, col * STRIDE + STRIDE // 2)
    src_r = min(CORE - 1, row * STRIDE + STRIDE // 2)
    return src_c * SPACING - HALF, HALF - src_r * SPACING


def max_pool(slope: np.ndarray) -> np.ndarray:
    out = np.empty((SIDE, SIDE), dtype=np.float32)
    for row in range(SIDE):
        for col in range(SIDE):
            window = slope[row * STRIDE:(row + 1) * STRIDE, col * STRIDE:(col + 1) * STRIDE]
            out[row, col] = float(window.max())
    return out


def dilate(mask: np.ndarray, radius_cells: int) -> np.ndarray:
    out = mask.copy()
    for _ in range(radius_cells):
        padded = np.pad(out, 1, constant_values=False)
        grown = out.copy()
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                grown |= padded[1 + d_row:1 + d_row + SIDE, 1 + d_col:1 + d_col + SIDE]
        out = grown
    return out


def nearest_open(mask: np.ndarray, row: int, col: int) -> tuple[int, int]:
    if not mask[row, col]:
        return row, col
    for radius in range(1, SIDE):
        r0, r1 = max(0, row - radius), min(SIDE, row + radius + 1)
        c0, c1 = max(0, col - radius), min(SIDE, col + radius + 1)
        window = ~mask[r0:r1, c0:c1]
        if window.any():
            hits = np.argwhere(window)
            hits[:, 0] += r0
            hits[:, 1] += c0
            dist = (hits[:, 0] - row) ** 2 + (hits[:, 1] - col) ** 2
            pick = hits[int(dist.argmin())]
            return int(pick[0]), int(pick[1])
    raise RuntimeError("No open cell")


def astar(blocked: np.ndarray, weight: np.ndarray, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
    open_set = [(math.hypot(start[0] - goal[0], start[1] - goal[1]), 0.0, start)]
    came: dict[tuple[int, int], tuple[int, int]] = {}
    best = {start: 0.0}
    seen: set[tuple[int, int]] = set()
    while open_set:
        _, cost, current = heapq.heappop(open_set)
        if current in seen:
            continue
        seen.add(current)
        if current == goal:
            break
        row, col = current
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row == 0 and d_col == 0:
                    continue
                n_row, n_col = row + d_row, col + d_col
                if n_row < 0 or n_col < 0 or n_row >= SIDE or n_col >= SIDE or blocked[n_row, n_col]:
                    continue
                nxt = (n_row, n_col)
                score = cost + math.hypot(d_row, d_col) * float(weight[n_row, n_col])
                if score < best.get(nxt, 1e30):
                    best[nxt] = score
                    came[nxt] = current
                    heapq.heappush(open_set, (score + math.hypot(n_row - goal[0], n_col - goal[1]), score, nxt))
    if goal not in came and goal != start:
        raise RuntimeError("No path")
    path = [goal]
    while path[-1] != start:
        path.append(came[path[-1]])
    path.reverse()
    return path


def to_polyline(cells: list[tuple[int, int]]) -> list[list[float]]:
    points = []
    for index, (row, col) in enumerate(cells):
        if index not in (0, len(cells) - 1) and index % 2:
            continue
        east, north = cell_center(row, col)
        points.append([round(east, 2), round(north, 2)])
    return points


def path_length(points: list[list[float]]) -> float:
    return float(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])))


def max_separation(left: list[list[float]], right: list[list[float]]) -> float:
    def point_line(point: list[float], other: list[list[float]]) -> float:
        best = 1e30
        px, py = point
        for a, b in zip(other, other[1:]):
            abx, aby = b[0] - a[0], b[1] - a[1]
            denom = abx * abx + aby * aby
            if denom == 0:
                dist = math.hypot(px - a[0], py - a[1])
            else:
                t = min(1.0, max(0.0, ((px - a[0]) * abx + (py - a[1]) * aby) / denom))
                dist = math.hypot(px - (a[0] + t * abx), py - (a[1] + t * aby))
            best = min(best, dist)
        return best

    return max(max(point_line(point, right) for point in left), max(point_line(point, left) for point in right))


def main() -> None:
    slope = np.load(SLOPE_PATH)["slope_deg"]
    local_z = np.load(SLOPE_PATH)["local_z_m"]
    pooled = max_pool(slope)
    steep = pooled >= SAFE_DEG
    short_blocked = pooled >= SHORT_DEG
    start = cell_of(14.0, 12.0)
    landing_xy = local_xy(18.4447, 77.4508)
    goal = cell_of(*landing_xy)
    rochette_xy = local_xy(ROCHETTE["latitude_north_deg"], ROCHETTE["longitude_east_deg"])
    rochette_inside = abs(rochette_xy[0]) < HALF and abs(rochette_xy[1]) < HALF
    clearance_cells = max(1, round(CLEARANCE_M / CELL))
    safe_mask = dilate(steep, clearance_cells)
    short_cells = astar(short_blocked, np.ones_like(pooled), nearest_open(short_blocked, *start), nearest_open(short_blocked, *goal))
    safe_cells = astar(
        safe_mask,
        1.0 + 4.0 * (pooled / SAFE_DEG),
        nearest_open(safe_mask, *start),
        nearest_open(safe_mask, *goal),
    )
    short_points = to_polyline(short_cells)
    safe_points = to_polyline(safe_cells)
    separation = max_separation(short_points, safe_points)
    science_site = None
    if rochette_inside:
        via = cell_of(*rochette_xy)
        first = astar(safe_mask, np.ones_like(pooled), nearest_open(safe_mask, *start), nearest_open(safe_mask, *via))
        second = astar(safe_mask, np.ones_like(pooled), nearest_open(safe_mask, *via), nearest_open(safe_mask, *goal))
        science_points = to_polyline(first + second[1:])
        science_site = {**ROCHETTE, "local_east_m": round(rochette_xy[0], 2), "local_north_m": round(rochette_xy[1], 2)}
    else:
        science_points = safe_points
    def stats(points: list[list[float]]) -> dict:
        rows = []
        cols = []
        for east, north in points:
            col = int(np.clip(round((east + HALF) / SPACING), 0, CORE - 1))
            row = int(np.clip(round((HALF - north) / SPACING), 0, CORE - 1))
            rows.append(row)
            cols.append(col)
        sampled = slope[rows, cols]
        heights = local_z[rows, cols]
        return {
            "distance_m": round(path_length(points), 2),
            "elevation_change_m": round(float(heights[-1] - heights[0]), 2),
            "max_slope_deg": round(float(sampled.max()), 2),
            "points": points,
        }
    payload = {
        "slope_source": "data/jez_site_slope_4m.npz",
        "cell_m": CELL,
        "safe_block_deg": SAFE_DEG,
        "safe_clearance_m": clearance_cells * CELL,
        "short_block_deg": SHORT_DEG,
        "lateral_separation_m": round(separation, 2),
        "separation_meets_margin": separation >= MIN_SEPARATION_M,
        "landing": {"name": "Octavia E. Butler Landing", "latitude_north_deg": 18.4447, "longitude_east_deg": 77.4508, "local_east_m": round(landing_xy[0], 2), "local_north_m": round(landing_xy[1], 2)},
        "science_site": science_site,
        "shortest": stats(short_points),
        "safest": stats(safe_points),
        "science": stats(science_points),
        "threshold_note": "15 degrees and the clearance around those cells are project display rules, not a flight or EVA certification.",
    }
    OUT.write_text(json.dumps(payload), encoding="utf-8")
    print("separation", payload["lateral_separation_m"], "safe", payload["safest"]["distance_m"], "short", payload["shortest"]["distance_m"], "science", payload["science"]["distance_m"])
    print("rochette", science_site)


if __name__ == "__main__":
    main()
