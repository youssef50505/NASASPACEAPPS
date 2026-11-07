"""Apply the NASA surface color and the remaining exploration stages.

Ground meshes keep their vertex coordinates, transforms, and shape keys.
New markers, routes, cameras, and animation are added around them.
"""
from __future__ import annotations

import array
import hashlib
import heapq
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
INPUT_NAME = "MARS_SENTINEL_NASA_Terrain_Study_HIRISE_READY.blend"
COLOR_BLEND = ROOT / "MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend"
FINAL_BLEND = ROOT / "MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend"
COLOR_PNG = ROOT / "data" / "jez_hirise_site_nasa_color_1m.png"
HEIGHT_PNG = ROOT / "data" / "jez_hirise_site_height_4m.png"
PROVENANCE = ROOT / "data" / "jez_site_color_provenance.json"
SITE_NAME = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"
SITE_LAT = 18.42875
SITE_LON = 77.44215
MARS_RADIUS_M = 3_396_190.0
CORE = 1024
SKIRT = 20
SPACING = 4.0
SLOPE_LIMIT_SAFE = 15.0
SLOPE_LIMIT_SHORT = 28.0

ILLUSTRATIVE_COLLECTIONS = (
    "Craters", "Rocks", "Mars_Pebbles", "Pebble_Variants", "Mountains",
    "NEW_Global_Boulders", "NEW_Global_Craters", "NEW_Global_Dunes",
    "NEW_Global_Plains", "NEW_Global_Slopes", "NEW_Global_Trails",
    "NEW_Global_Valleys", "NEW_Terrain_Features", "NEW_Exploration_Paths",
    "Girl_Outfit_Transfer", "Suit_on_Girl", "NewHead_Parts",
)
LAYER_NOTES = {
    "NEW_Layer_Elevation": "Superseded as a data view by the measured elevation material on the HiRISE site mesh.",
    "NEW_Layer_Slope": "Superseded as a data view by the slope derived from the HiRISE site mesh.",
    "NEW_Layer_Geological": "No CRISM or geologic map was clipped to this window. Not a NASA measurement.",
    "NEW_Layer_Temperature": "No THEMIS temperature raster was clipped to this window. Not a NASA measurement.",
    "NEW_Layer_Dust": "No dust optical-depth raster was clipped to this window. Not a NASA measurement.",
    "NEW_Layer_Sunlight_Shadow": "Scene lighting and shadow only. Not a measured illumination product.",
}


def fingerprint(obj: bpy.types.Object) -> dict:
    mesh = obj.data
    coords = array.array("f", [0.0]) * (len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", coords)
    digest = hashlib.sha256(coords.tobytes()).hexdigest()
    keys = None
    if mesh.shape_keys is not None:
        keys = {key.name: round(float(key.value), 6) for key in mesh.shape_keys.key_blocks}
    return {
        "vertices": len(mesh.vertices),
        "polygons": len(mesh.polygons),
        "location": [round(float(v), 6) for v in obj.location],
        "rotation": [round(float(v), 6) for v in obj.rotation_euler],
        "scale": [round(float(v), 6) for v in obj.scale],
        "matrix": [round(float(v), 6) for row in obj.matrix_world for v in row],
        "shape_keys": keys,
        "co_sha256": digest,
    }


def require_same(before: dict, after: dict, label: str) -> None:
    if before != after:
        raise RuntimeError(f"{label} geometry changed: {json.dumps({'before': before, 'after': after})[:2000]}")


def local_xy(lat: float, lon: float) -> tuple[float, float]:
    east = MARS_RADIUS_M * math.radians(lon - SITE_LON)
    north = MARS_RADIUS_M * math.radians(lat - SITE_LAT)
    return east, north


def new_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.9
    mat.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def link(obj: bpy.types.Object, col: bpy.types.Collection) -> None:
    if obj.name not in col.objects:
        col.objects.link(obj)
    for other in list(obj.users_collection):
        if other != col:
            other.objects.unlink(obj)


def cone(name: str, height: float, radius: float) -> bpy.types.Mesh:
    mesh = bpy.data.meshes.new(name)
    verts = [(0.0, 0.0, height)]
    for i in range(8):
        angle = i / 8 * math.tau
        verts.append((math.cos(angle) * radius, math.sin(angle) * radius, 0.0))
    faces = [(0, i + 1, (i + 1) % 8 + 1) for i in range(8)]
    faces.append(tuple(range(1, 9)))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def core_heights(mesh: bpy.types.Mesh) -> list[float]:
    side = CORE + 2 * SKIRT
    coords = array.array("f", [0.0]) * (len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", coords)
    heights = [0.0] * (CORE * CORE)
    for row in range(CORE):
        start = ((row + SKIRT) * side + SKIRT) * 3 + 2
        for col in range(CORE):
            heights[row * CORE + col] = coords[start + col * 3]
    return heights


def slope_grid(heights: list[float]) -> list[float]:
    slopes = [0.0] * (CORE * CORE)
    for row in range(CORE):
        for col in range(CORE):
            c0 = max(0, col - 1)
            c1 = min(CORE - 1, col + 1)
            r0 = max(0, row - 1)
            r1 = min(CORE - 1, row + 1)
            dzdx = (heights[row * CORE + c1] - heights[row * CORE + c0]) / ((c1 - c0) * SPACING)
            dzdy = (heights[r0 * CORE + col] - heights[r1 * CORE + col]) / ((r1 - r0) * SPACING)
            slopes[row * CORE + col] = math.degrees(math.atan(math.hypot(dzdx, dzdy)))
    return slopes


def paint_slope(mesh: bpy.types.Mesh, slopes: list[float]) -> None:
    side = CORE + 2 * SKIRT
    attr = mesh.color_attributes.get("HiRISE_Slope_Tint")
    if attr is None:
        attr = mesh.color_attributes.new(name="HiRISE_Slope_Tint", type="FLOAT_COLOR", domain="POINT")
    colors = array.array("f", [0.0]) * (len(mesh.vertices) * 4)
    for row in range(side):
        src_r = min(max(row - SKIRT, 0), CORE - 1)
        for col in range(side):
            src_c = min(max(col - SKIRT, 0), CORE - 1)
            slope = slopes[src_r * CORE + src_c]
            t = min(max(slope / 30.0, 0.0), 1.0)
            red = 0.15 + 0.8 * t
            green = 0.35 + 0.4 * (1.0 - abs(t - 0.45) * 2.0)
            blue = 0.75 - 0.7 * t
            index = (row * side + col) * 4
            colors[index:index + 4] = array.array("f", [red, max(0.0, green), max(0.0, blue), 1.0])
    attr.data.foreach_set("color", colors)


def attribute_material(name: str, attribute: str) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = 0.9
    color = nodes.new("ShaderNodeVertexColor")
    color.layer_name = attribute
    mat.node_tree.links.new(color.outputs["Color"], shader.inputs["Base Color"])
    mat.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def apply_surface_material(mesh: bpy.types.Mesh) -> bpy.types.Material:
    image = bpy.data.images.load(str(COLOR_PNG), check_existing=True)
    image.colorspace_settings.name = "sRGB"
    image.pack()
    mat = bpy.data.materials.new("Mars_NASA_HiRISE_Viking_Color")
    mat.diffuse_color = (0.45, 0.24, 0.14, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (520, 0)
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.location = (240, 0)
    shader.inputs["Roughness"].default_value = 0.92
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    tex.location = (-80, 40)
    uv = nodes.new("ShaderNodeUVMap")
    uv.uv_map = "UVMap"
    uv.location = (-300, 40)
    links = mat.node_tree.links
    links.new(uv.outputs["UV"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], shader.inputs["Base Color"])
    if HEIGHT_PNG.is_file():
        height = bpy.data.images.load(str(HEIGHT_PNG), check_existing=True)
        height.colorspace_settings.name = "Non-Color"
        height.pack()
        height_tex = nodes.new("ShaderNodeTexImage")
        height_tex.image = height
        height_tex.interpolation = "Linear"
        height_tex.location = (-80, -220)
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.08
        bump.inputs["Distance"].default_value = 0.35
        bump.location = (40, -200)
        links.new(uv.outputs["UV"], height_tex.inputs["Vector"])
        links.new(height_tex.outputs["Color"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    mesh.materials.clear()
    mesh.materials.append(mat)
    return mat


def mean_downsample(values: list[float], stride: int) -> list[float]:
    side = CORE // stride
    out = [0.0] * (side * side)
    cells = stride * stride
    for row in range(side):
        for col in range(side):
            total = 0.0
            for rr in range(row * stride, (row + 1) * stride):
                for cc in range(col * stride, (col + 1) * stride):
                    total += values[rr * CORE + cc]
            out[row * side + col] = total / cells
    return out


def max_downsample(values: list[float], stride: int) -> list[float]:
    side = CORE // stride
    out = [0.0] * (side * side)
    for row in range(side):
        for col in range(side):
            best = 0.0
            for rr in range(row * stride, (row + 1) * stride):
                best = max(best, max(values[rr * CORE + cc] for cc in range(col * stride, (col + 1) * stride)))
            out[row * side + col] = best
    return out


def astar(blocked: list[bool], weight: list[float], start: tuple[int, int], goal: tuple[int, int], side: int) -> list[tuple[int, int]] | None:
    def cell(row: int, col: int) -> int:
        return row * side + col

    def heuristic(row: int, col: int) -> float:
        return math.hypot(row - goal[0], col - goal[1])

    open_set = [(heuristic(*start), 0.0, start)]
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
                n_row = row + d_row
                n_col = col + d_col
                if n_row < 0 or n_col < 0 or n_row >= side or n_col >= side:
                    continue
                if blocked[cell(n_row, n_col)]:
                    continue
                step = math.hypot(d_row, d_col) * weight[cell(n_row, n_col)]
                nxt = (n_row, n_col)
                score = cost + step
                if score < best.get(nxt, 1e30):
                    best[nxt] = score
                    came[nxt] = current
                    heapq.heappush(open_set, (score + heuristic(n_row, n_col), score, nxt))
    if goal not in came and goal != start:
        return None
    path = [goal]
    while path[-1] != start:
        path.append(came[path[-1]])
    path.reverse()
    return path


def nearest_open(blocked: list[bool], row: int, col: int, side: int) -> tuple[int, int]:
    if not blocked[row * side + col]:
        return row, col
    for radius in range(1, 12):
        for rr in range(row - radius, row + radius + 1):
            for cc in range(col - radius, col + radius + 1):
                if 0 <= rr < side and 0 <= cc < side and not blocked[rr * side + cc]:
                    return rr, cc
    return row, col


def grid_index(east: float, north: float, stride: int) -> tuple[int, int]:
    half = (CORE - 1) * SPACING / 2.0
    col = round((east + half) / (SPACING * stride))
    row = round((half - north) / (SPACING * stride))
    side = CORE // stride
    return min(max(row, 0), side - 1), min(max(col, 0), side - 1)


def height_at(heights: list[float], east: float, north: float) -> float:
    half = (CORE - 1) * SPACING / 2.0
    col = min(CORE - 1, max(0, round((east + half) / SPACING)))
    row = min(CORE - 1, max(0, round((half - north) / SPACING)))
    return heights[row * CORE + col]


def world_point(site: bpy.types.Object, row: int, col: int, heights: list[float], stride: int, lift: float) -> tuple[float, float, float]:
    half = (CORE - 1) * SPACING / 2.0
    src_c = min(CORE - 1, col * stride + stride // 2)
    src_r = min(CORE - 1, row * stride + stride // 2)
    east = src_c * SPACING - half
    north = half - src_r * SPACING
    return (
        float(site.location.x) + east,
        float(site.location.y) + north,
        float(site.location.z) + heights[src_r * CORE + src_c] + lift,
    )


def add_curve(name: str, points: list[tuple[float, float, float]], material: bpy.types.Material, col: bpy.types.Collection) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.7
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for index, point in enumerate(points):
        spline.points[index].co = (point[0], point[1], point[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    curve.materials.append(material)
    link(obj, col)
    return obj


def path_stats(points: list[tuple[float, float, float]], slopes: list[float], stride: int) -> dict:
    distance = 0.0
    max_slope = 0.0
    half = (CORE - 1) * SPACING / 2.0
    for first, second in zip(points, points[1:]):
        distance += math.dist(first, second)
    for _x, y, _z in points:
        # slope lookup is filled by the caller via parallel arrays when needed
        pass
    return {"distance_m": round(distance, 2), "points": len(points)}


def hold_transform(obj: bpy.types.Object, frame: int) -> None:
    obj.keyframe_insert("location", frame=frame)
    obj.keyframe_insert("rotation_euler", frame=frame)


def main() -> None:
    if Path(bpy.data.filepath).name != INPUT_NAME:
        raise RuntimeError(f"Open {INPUT_NAME} first")
    if not COLOR_PNG.is_file() or not PROVENANCE.is_file():
        raise RuntimeError("NASA color crop is missing")
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    scene = bpy.context.scene
    site = bpy.data.objects[SITE_NAME]
    terrain = bpy.data.objects["Mars_Terrain"]
    before_site = fingerprint(site)
    before_terrain = fingerprint(terrain)
    saved_frame = scene.frame_current

    surface = apply_surface_material(site.data)
    heights = core_heights(site.data)
    slopes = slope_grid(heights)
    paint_slope(site.data, slopes)
    elevation = attribute_material("Mars_Layer_Elevation_Measured", "HiRISE_Elevation_Tint")
    slope_mat = attribute_material("Mars_Layer_Slope_Measured", "HiRISE_Slope_Tint")
    site["surface_color_product"] = provenance["hirise_product"]
    site["surface_color_doi"] = provenance["hirise_doi"]
    site["surface_color_url"] = provenance["hirise_url"]
    site["surface_color_equation"] = provenance["color_equation"]
    site["surface_color_viking"] = provenance["viking_product"]
    site["surface_brightness"] = provenance["hirise_bands"]
    site["geometry_frozen"] = "Vertex coordinates, transform, and scale were not edited when the NASA color was applied"
    terrain["underlay_note"] = "Flat visual base retained. Shape keys and transform were not edited in the NASA color pass."

    for name in ILLUSTRATIVE_COLLECTIONS:
        col = bpy.data.collections.get(name)
        if col is not None:
            col["illustrative"] = True
            col["nasa_measurement"] = False
            col["data_note"] = "Existing authored asset. Not a measured NASA terrain product."
    for name, note in LAYER_NOTES.items():
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        obj["illustrative"] = True
        obj["nasa_measurement"] = False
        obj["data_note"] = note
        obj["previous_hide_render"] = bool(obj.hide_render)
        obj.hide_render = True
        obj.hide_viewport = True

    globe = bpy.data.objects.get("MARS_NEW_Globe")
    if globe is not None:
        globe["navigation"] = "Viewport orbit and zoom. Globe scale and location were not changed."
        globe["geometry_frozen"] = True
    scene["mars_layers"] = json.dumps({
        "color": surface.name,
        "elevation": elevation.name,
        "slope": slope_mat.name,
        "geology": "unavailable - no CRISM clip",
        "temperature": "unavailable - no THEMIS clip",
        "dust": "unavailable - no dust raster; particle dust is illustrative",
        "sunlight": "Mars_Sun scene light, not a measurement",
    })
    require_same(before_site, fingerprint(site), "site")
    require_same(before_terrain, fingerprint(terrain), "terrain")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(COLOR_BLEND), check_existing=False)
    print("SAVED_COLOR", COLOR_BLEND)

    measured = collection("MARS_SENTINEL_Measured")
    illustrative = collection("MARS_SENTINEL_Illustrative")
    stride = 4
    side = CORE // stride
    slope_max = max_downsample(slopes, stride)
    height_mean = mean_downsample(heights, stride)
    start_east, start_north = 14.0, 12.0
    land_east, land_north = local_xy(18.4447, 77.4508)
    heli_east, heli_north = local_xy(18.44486, 77.45102)
    start = nearest_open([value > SLOPE_LIMIT_SHORT for value in slope_max], *grid_index(start_east, start_north, stride), side)
    goal = nearest_open([value > SLOPE_LIMIT_SHORT for value in slope_max], *grid_index(land_east, land_north, stride), side)
    safe_blocked = [value > SLOPE_LIMIT_SAFE for value in slope_max]
    short_blocked = [value > SLOPE_LIMIT_SHORT for value in slope_max]
    safe_weight = [1.0 + 4.0 * (value / SLOPE_LIMIT_SAFE) for value in slope_max]
    short_weight = [1.0] * len(slope_max)
    safe_start = nearest_open(safe_blocked, *start, side)
    safe_goal = nearest_open(safe_blocked, *goal, side)
    safe_cells = astar(safe_blocked, safe_weight, safe_start, safe_goal, side)
    short_cells = astar(short_blocked, short_weight, start, goal, side)
    if safe_cells is None or short_cells is None:
        raise RuntimeError("No route across the measured slope grid")

    def cells_to_points(cells: list[tuple[int, int]]) -> list[tuple[float, float, float]]:
        return [world_point(site, row, col, heights, stride, 1.4) for row, col in cells]

    safe_points = cells_to_points(safe_cells)
    short_points = cells_to_points(short_cells)
    safe_curve = add_curve("MS_Route_Safest_HiRISE", safe_points, new_material("MS_Route_Safe_Green", (0.1, 0.75, 0.25, 1)), measured)
    short_curve = add_curve("MS_Route_Shortest_HiRISE", short_points, new_material("MS_Route_Short_Yellow", (0.9, 0.75, 0.15, 1)), measured)
    science_curve = add_curve("MS_Route_Science_HiRISE", safe_points, new_material("MS_Route_Science_Blue", (0.2, 0.45, 0.95, 1)), measured)
    for obj, kind, limit, points in (
        (safe_curve, "safest", SLOPE_LIMIT_SAFE, safe_points),
        (short_curve, "shortest", SLOPE_LIMIT_SHORT, short_points),
        (science_curve, "science", SLOPE_LIMIT_SAFE, safe_points),
    ):
        distance = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
        obj["route_kind"] = kind
        obj["distance_m"] = round(distance, 2)
        obj["elevation_start_m"] = round(points[0][2] - 1.4, 2)
        obj["elevation_end_m"] = round(points[-1][2] - 1.4, 2)
        obj["slope_block_deg"] = limit
        obj["nasa_measurement"] = True
        obj["source"] = "Slope and elevation from USGS HiRISE DTM 10.5066/P9REJ9JN, 4 m mesh, 16 m route cells"
        obj["science_destination"] = "Octavia E. Butler Landing, 18.4447 N, 77.4508 E"
        obj["illustrative"] = False

    for index in range(0, len(safe_cells), 8):
        row, col = safe_cells[index]
        point = safe_points[index]
        empty = bpy.data.objects.new(f"MS_Waypoint_{index:03d}", None)
        empty.empty_display_type = "PLAIN_AXES"
        empty.empty_display_size = 4.0
        empty.location = point
        empty["nasa_measurement"] = True
        empty["route"] = "safest"
        link(empty, measured)

    marker_mesh = cone("MS_Science_MarkerMesh", 8.0, 1.6)
    landing = bpy.data.objects.new("MS_Science_Octavia_E_Butler_Landing", marker_mesh)
    landing.location = world_point(site, *grid_index(land_east, land_north, stride), heights, stride, 0.2)
    landing.data.materials.append(new_material("MS_Science_White", (0.9, 0.9, 0.85, 1)))
    landing["site_name"] = "Octavia E. Butler Landing"
    landing["latitude_north_deg"] = 18.4447
    landing["longitude_east_deg"] = 77.4508
    landing["confidence"] = "confirmed landing site"
    landing["source"] = "NASA Mars 2020 Perseverance landing site, published as 18.4447 N, 77.4508 E"
    landing["nasa_measurement"] = True
    landing["illustrative"] = False
    link(landing, measured)
    heli = bpy.data.objects.new("MS_Science_Wright_Brothers_Field", marker_mesh)
    heli.location = world_point(site, *grid_index(heli_east, heli_north, stride), heights, stride, 0.2)
    heli["site_name"] = "Wright Brothers Field"
    heli["latitude_north_deg"] = 18.44486
    heli["longitude_east_deg"] = 77.45102
    heli["confidence"] = "confirmed Ingenuity airfield"
    heli["source"] = "NASA Ingenuity Wright Brothers Field, published near 18.44486 N, 77.45102 E"
    heli["nasa_measurement"] = True
    heli["note"] = "About 20 m from the landing marker at this mesh resolution"
    link(heli, measured)
    scene["ancient_water_marker"] = (
        "No ancient-water pin was added. The Jezero western delta fan is outside this 4092 m HiRISE mesh, "
        "so a pin inside the mesh would not be the published delta."
    )

    hazard_mesh = cone("MS_Hazard_MarkerMesh", 6.0, 1.3)
    hazard_mat = new_material("MS_Hazard_Red", (0.85, 0.08, 0.05, 1))
    hazard_mesh.materials.append(hazard_mat)
    placed = 0
    for row in range(2, side - 2, 3):
        for col in range(2, side - 2, 3):
            value = slope_max[row * side + col]
            if value < SLOPE_LIMIT_SAFE or placed >= 36:
                continue
            neighbors = [
                slope_max[(row + rr) * side + (col + cc)]
                for rr in (-1, 0, 1) for cc in (-1, 0, 1)
            ]
            if value < max(neighbors):
                continue
            marker = bpy.data.objects.new(f"MS_Hazard_Slope_{placed:02d}", hazard_mesh)
            marker.location = world_point(site, row, col, heights, stride, 0.3)
            marker["hazard"] = "slope"
            marker["slope_deg"] = round(value, 2)
            marker["threshold_deg"] = SLOPE_LIMIT_SAFE
            marker["threshold_note"] = "Project display threshold of 15 degrees. Not a flight or EVA safety certification."
            marker["nasa_measurement"] = True
            marker["source"] = "Derived from USGS HiRISE DTM elevations on the existing mesh"
            link(marker, measured)
            placed += 1

    joe = bpy.data.objects.get("Joe_Astronaut")
    msl = bpy.data.objects.get("MSL")
    for label, obj, offset in (
        ("Thermometer", joe, (3.0, 1.0, 0.0)),
        ("Wind_Dust_Sensor", joe, (3.0, -1.2, 0.0)),
        ("Sample_Tube", joe, (1.5, 2.0, 0.4)),
        ("Environment_Station", msl, (4.0, 3.0, 0.0)),
    ):
        if obj is None:
            continue
        empty = bpy.data.objects.new(f"MS_ILLUSTRATIVE_{label}", None)
        empty.empty_display_type = "ARROWS"
        empty.empty_display_size = 1.2
        empty.location = obj.matrix_world.translation + Vector(offset)
        empty["illustrative"] = True
        empty["nasa_measurement"] = False
        empty["data_note"] = "Placeholder prop. It does not display a measured NASA value."
        link(empty, illustrative)

    dust_mesh = bpy.data.meshes.new("MS_Dust_Emitter")
    dust_mesh.from_pydata([(-8, -8, 0), (8, -8, 0), (8, 8, 0), (-8, 8, 0)], [], [(0, 1, 2, 3)])
    dust = bpy.data.objects.new("MS_ILLUSTRATIVE_Dust", dust_mesh)
    dust.location = (float(site.location.x), float(site.location.y) - 40.0, float(site.location.z) + 25.0)
    dust["illustrative"] = True
    dust["nasa_measurement"] = False
    dust["data_note"] = "Visual dust particles only. Not a measured dust optical-depth layer."
    link(dust, illustrative)
    dust_mod = dust.modifiers.new("Dust", "PARTICLE_SYSTEM")
    settings = dust_mod.particle_system.settings
    settings.count = 40
    settings.frame_start = saved_frame
    settings.frame_end = saved_frame + 40
    settings.lifetime = 90
    settings.emit_from = "FACE"
    settings.normal_factor = 0.15
    settings.factor_random = 0.8
    settings.particle_size = 0.08

    tour_data = bpy.data.cameras.new("MS_Tour_Camera")
    tour_data.lens = 45
    tour_data.clip_end = 100000
    tour = bpy.data.objects.new("MS_Tour_Camera", tour_data)
    link(tour, measured)
    globe_cam = bpy.data.objects["MARS_NEW_Globe_Camera"]
    tour.matrix_world = globe_cam.matrix_world.copy()
    tour.data.lens = globe_cam.data.lens
    hold_transform(tour, saved_frame)
    tour.data.keyframe_insert("lens", frame=saved_frame)
    if globe is not None:
        center = globe.matrix_world.translation.copy()
        distance = (globe_cam.matrix_world.translation - center).length
        for step, frame in enumerate((160, 200, 240, 280)):
            angle = step / 4 * math.tau
            tour.location = center + Vector((math.sin(angle) * distance, math.cos(angle) * distance, distance * 0.18))
            tour.rotation_euler = (center - tour.location).to_track_quat("-Z", "Y").to_euler()
            tour.keyframe_insert("location", frame=frame)
            tour.keyframe_insert("rotation_euler", frame=frame)
            tour.data.lens = 50 - step * 4
            tour.data.keyframe_insert("lens", frame=frame)
    look_at = Vector(safe_points[len(safe_points) // 2])
    tour.location = look_at + Vector((0.0, -180.0, 90.0))
    tour.rotation_euler = (look_at - tour.location).to_track_quat("-Z", "Y").to_euler()
    tour.data.lens = 32
    tour.keyframe_insert("location", frame=340)
    tour.keyframe_insert("rotation_euler", frame=340)
    tour.data.keyframe_insert("lens", frame=340)

    if joe is not None:
        hold_transform(joe, saved_frame)
        joe_local_x = float(joe.matrix_world.translation.x - site.location.x)
        joe_local_y = float(joe.matrix_world.translation.y - site.location.y)
        clearance = float(joe.matrix_world.translation.z - site.location.z - height_at(heights, joe_local_x, joe_local_y))
        samples = safe_points[:: max(1, len(safe_points) // 12)][:12]
        for index, point in enumerate(samples):
            joe.location = Vector((point[0] + 6.0, point[1], point[2] - 1.4 + clearance))
            if index:
                direction = Vector(samples[index]) - Vector(samples[index - 1])
                joe.rotation_euler.z = math.atan2(direction.y, direction.x)
            joe.keyframe_insert("location", frame=360 + index * 8)
            joe.keyframe_insert("rotation_euler", frame=360 + index * 8)
        joe.rotation_euler.x = 0.5
        joe.keyframe_insert("rotation_euler", frame=460)
        joe.rotation_euler.x = 0.0
        joe.keyframe_insert("rotation_euler", frame=480)
        eye = bpy.data.cameras.new("MS_Astronaut_Eye_Camera")
        eye.lens = 28
        eye.clip_start = 0.05
        eye.clip_end = 20000
        eye_obj = bpy.data.objects.new("MS_Astronaut_Eye_Camera", eye)
        eye_obj.parent = joe
        eye_obj.location = (0.0, -0.25, max(1.5, joe.dimensions.z * 0.82))
        eye_obj.rotation_euler = (math.radians(80), 0.0, math.radians(180))
        link(eye_obj, measured)
        eye_obj["data_note"] = "Eye-height camera parented to Joe_Astronaut. Local axes follow the imported model."

    rover_roots = []
    if msl is not None:
        excluded = {SITE_NAME, "Mars_Terrain", "MARS_NEW_Globe", "MARS_NEW_Globe_Rotator"}
        skip_prefixes = ("MS_", "NEW_", "MARS_NEW_")

        def top_root(obj: bpy.types.Object) -> bpy.types.Object:
            while obj.parent is not None:
                obj = obj.parent
            return obj

        for obj in scene.objects:
            if obj.type != "MESH" or obj.hide_render or obj.name in excluded or obj.name.startswith(skip_prefixes):
                continue
            if any(token in obj.name for token in ("Crater", "Boulder", "Pebble", "Rock", "Dune", "Globe")):
                continue
            center = obj.matrix_world.translation
            in_rover_box = 10.0 <= center.x <= 18.0 and 8.0 <= center.y <= 16.0
            near_msl = abs(center.x - msl.matrix_world.translation.x) < 8.0 and abs(center.y - msl.matrix_world.translation.y) < 8.0
            if in_rover_box or near_msl or obj == msl:
                rover_roots.append(top_root(obj))
        rover_roots = sorted(set(rover_roots), key=lambda obj: obj.name)
        origins = {obj: obj.location.copy() for obj in rover_roots}
        for obj in rover_roots:
            hold_transform(obj, saved_frame)
        samples = short_points[:: max(1, len(short_points) // 10)][:10]
        base = Vector(samples[0])
        for index, point in enumerate(samples):
            delta = Vector(point) - base
            for obj, origin in origins.items():
                obj.location = origin + delta
                obj.keyframe_insert("location", frame=500 + index * 8)
        wheels = bpy.data.objects.get("Wheels_objs")
        if wheels is not None:
            wheels["wheel_spin_note"] = (
                "Wheels_objs is one combined mesh without separate axle origins, "
                "so the assembly translates with the rover and is not spun around a false axle."
            )

    sun = bpy.data.objects.get("Mars_Sun")
    if sun is not None:
        hold_transform(sun, saved_frame)
        sun.rotation_euler.x += math.radians(8)
        sun.keyframe_insert("rotation_euler", frame=340)
        sun.rotation_euler.x -= math.radians(8)
        sun.keyframe_insert("rotation_euler", frame=saved_frame)

    warning = bpy.data.objects.new("MS_Hazard_Warning", hazard_mesh)
    warning.location = safe_points[len(safe_points) // 2]
    warning.scale = (0.01, 0.01, 0.01)
    warning["illustrative"] = False
    warning["data_note"] = "Appears when the tour reaches the middle of the measured route. Slope markers elsewhere are the hazard layer."
    link(warning, measured)
    warning.keyframe_insert("scale", frame=saved_frame)
    warning.scale = (4.0, 4.0, 4.0)
    warning.keyframe_insert("scale", frame=420)
    warning.scale = (0.01, 0.01, 0.01)
    warning.keyframe_insert("scale", frame=480)

    scene.frame_end = max(int(scene.frame_end), 580)
    scene.frame_set(saved_frame)
    scene.camera = globe_cam
    require_same(before_site, fingerprint(site), "site final")
    require_same(before_terrain, fingerprint(terrain), "terrain final")
    report = {
        "color_blend": str(COLOR_BLEND),
        "final_blend": str(FINAL_BLEND),
        "site_vertices": before_site["vertices"],
        "site_co_sha256": before_site["co_sha256"],
        "terrain_shape_keys": before_terrain["shape_keys"],
        "safe_distance_m": safe_curve["distance_m"],
        "short_distance_m": short_curve["distance_m"],
        "hazard_markers": placed,
        "slope_max_deg": round(max(slopes), 3),
        "landing_local_m": [round(land_east, 2), round(land_north, 2)],
        "layers_hidden_as_unmeasured": list(LAYER_NOTES),
        "ancient_water_marker": scene["ancient_water_marker"],
        "scene_camera_remains": scene.camera.name,
        "frame_preserved": saved_frame,
    }
    (ROOT / "data" / "exploration_integration_check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND), check_existing=False)
    print("SAVED_FINAL", FINAL_BLEND)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
