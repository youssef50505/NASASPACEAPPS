"""Opening surface camera, local color image, and separated measured routes.

The HiRISE site mesh and the flat Mars_Terrain underlay keep their coordinates.
The globe camera animation is left in place. This writes a new blend.
"""
from __future__ import annotations

import array
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE_NAME = "MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend"
OUTPUT = ROOT / "MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend"
COLOR = ROOT / "data" / "jez_hirise_site_local_rgb_1m.png"
COLOR_INFO = ROOT / "data" / "jez_site_local_color_provenance.json"
ROUTES = ROOT / "data" / "jez_distinct_routes.json"
SITE_NAME = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"
EXPECTED_HASH = "ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd"
CORE = 1024
SKIRT = 20
SPACING = 4.0
HALF = (CORE - 1) * SPACING / 2.0
CREW_ROOTS = [
    "Sketchfab_model.007",
    "Sketchfab_model.015",
    "Sketchfab_model",
    "Joe_Astronaut",
    "Sketchfab_model.003",
]
ROVER_ROOTS = ["MSL", "Wheels_objs"]
MARKERS = ["White_Circle_Marker", "White_Ring"]


def fingerprint(obj: bpy.types.Object) -> dict:
    mesh = obj.data
    coords = array.array("f", [0.0]) * (len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", coords)
    return {
        "vertices": len(mesh.vertices),
        "location": [round(float(v), 6) for v in obj.location],
        "rotation": [round(float(v), 6) for v in obj.rotation_euler],
        "scale": [round(float(v), 6) for v in obj.scale],
        "co_sha256": hashlib.sha256(coords.tobytes()).hexdigest(),
    }


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


def height_at(heights: list[float], east: float, north: float) -> float:
    col = min(CORE - 1, max(0, round((east + HALF) / SPACING)))
    row = min(CORE - 1, max(0, round((HALF - north) / SPACING)))
    return heights[row * CORE + col]


def link(obj: bpy.types.Object, col: bpy.types.Collection) -> None:
    if obj.name not in col.objects:
        col.objects.link(obj)
    for other in list(obj.users_collection):
        if other != col:
            other.objects.unlink(obj)


def material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.45
    mat.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def replace_curve(name: str, points: list[tuple[float, float, float]], mat: bpy.types.Material, col: bpy.types.Collection) -> bpy.types.Object:
    old = bpy.data.objects.get(name)
    if old is not None:
        data = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if data is not None and data.users == 0:
            bpy.data.curves.remove(data)
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 2.6
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for index, point in enumerate(points):
        spline.points[index].co = (point[0], point[1], point[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    curve.materials.append(mat)
    link(obj, col)
    return obj


def world_points(site: bpy.types.Object, heights: list[float], polyline: list[list[float]]) -> list[tuple[float, float, float]]:
    points = []
    for east, north in polyline:
        points.append((
            float(site.location.x) + float(east),
            float(site.location.y) + float(north),
            float(site.location.z) + height_at(heights, float(east), float(north)) + 1.6,
        ))
    return points


def bounds_of(names: list[str], limit: float) -> list[Vector]:
    found = []
    for name in names:
        root = bpy.data.objects.get(name)
        if root is None:
            continue
        objects = [root, *root.children_recursive]
        for obj in objects:
            if obj.type != "MESH":
                continue
            corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            extent = max(max(point[axis] for point in corners) - min(point[axis] for point in corners) for axis in range(3))
            if extent <= limit:
                found.extend(corners)
    return found


def main() -> None:
    if Path(bpy.data.filepath).name != SOURCE_NAME:
        raise RuntimeError(f"Open {SOURCE_NAME} first")
    scene = bpy.context.scene
    site = bpy.data.objects[SITE_NAME]
    terrain = bpy.data.objects["Mars_Terrain"]
    globe_camera = bpy.data.objects["MARS_NEW_Globe_Camera"]
    globe_before = tuple(round(float(v), 6) for v in globe_camera.location)
    before = fingerprint(site)
    terrain_before = fingerprint(terrain)
    if before["co_sha256"] != EXPECTED_HASH:
        raise RuntimeError("Site hash does not match the exploration file")

    color_info = json.loads(COLOR_INFO.read_text(encoding="utf-8"))
    image = bpy.data.images.load(str(COLOR), check_existing=False)
    image.name = "jez_hirise_site_local_rgb_1m.png"
    image.pack()
    surface = bpy.data.materials["Mars_NASA_HiRISE_Viking_Color"]
    replaced = False
    for node in surface.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            node.image = image
            replaced = True
    if not replaced:
        raise RuntimeError("Surface material has no image node")
    site["local_color_product"] = color_info["product"]
    site["local_color_observation"] = color_info["observation_id"]
    site["local_color_url"] = color_info["url"]
    site["local_color_coverage"] = color_info["coverage_fraction_of_4096_window"]
    site["local_color_credit"] = color_info["credit"]

    routes = json.loads(ROUTES.read_text(encoding="utf-8"))
    measured = bpy.data.collections["MARS_SENTINEL_Measured"]
    heights = core_heights(site.data)
    specs = (
        ("MS_Route_Shortest_HiRISE", "shortest", routes["shortest"], (0.95, 0.72, 0.08, 1.0), "MS_Route_Short_Yellow"),
        ("MS_Route_Safest_HiRISE", "safest", routes["safest"], (0.15, 0.85, 0.28, 1.0), "MS_Route_Safe_Green"),
        ("MS_Route_Science_HiRISE", "science", routes["science"], (0.15, 0.45, 1.0, 1.0), "MS_Route_Science_Blue"),
    )
    for name, kind, record, color, mat_name in specs:
        points = world_points(site, heights, record["points"])
        obj = replace_curve(name, points, material(mat_name, color), measured)
        obj["route_kind"] = kind
        obj["distance_m"] = record["distance_m"]
        obj["elevation_change_m"] = record["elevation_change_m"]
        obj["max_slope_deg"] = record["max_slope_deg"]
        obj["nasa_measurement"] = True
        obj["illustrative"] = False
        obj["source"] = "USGS HiRISE DTM 10.5066/P9REJ9JN slope grid. Safest stays 48 m clear of cells at or above 15 degrees."
        obj["threshold_note"] = routes["threshold_note"]
    route_plan = bpy.data.collections.get("RoutePlan")
    if route_plan is not None:
        route_plan["illustrative"] = True
        route_plan["data_note"] = "Earlier illustrative routes. Left in place. The measured paths are MS_Route_*_HiRISE."
        for obj in route_plan.all_objects:
            obj["illustrative"] = True
            obj["data_note"] = "Earlier illustrative route, kept for comparison. Not the measured HiRISE path."

    science = routes.get("science_site")
    if science is not None:
        old = bpy.data.objects.get("MS_Science_Rochette")
        if old is not None:
            bpy.data.objects.remove(old, do_unlink=True)
        mesh = bpy.data.meshes.new("MS_Science_RochetteMesh")
        mesh.from_pydata([(0.0, 0.0, 7.0), *[(math.cos(i / 8 * math.tau) * 1.4, math.sin(i / 8 * math.tau) * 1.4, 0.0) for i in range(8)]], [], [(0, i + 1, (i + 1) % 8 + 1) for i in range(8)] + [tuple(range(1, 9))])
        mesh.update()
        marker = bpy.data.objects.new("MS_Science_Rochette", mesh)
        east, north = science["local_east_m"], science["local_north_m"]
        marker.location = (
            float(site.location.x) + east,
            float(site.location.y) + north,
            float(site.location.z) + height_at(heights, east, north),
        )
        mesh.materials.append(material("MS_Science_Rochette_Blue", (0.2, 0.55, 1.0, 1.0)))
        marker["site_name"] = "Rochette"
        marker["latitude_north_deg"] = science["latitude_north_deg"]
        marker["longitude_east_deg"] = science["longitude_east_deg"]
        marker["source"] = science["source"]
        marker["source_url"] = science["source_url"]
        marker["nasa_measurement"] = True
        marker["illustrative"] = False
        marker["data_note"] = "Published Perseverance sample locality. Not an ancient-water or mineral pin."
        link(marker, measured)

    scene.frame_set(361)
    points = bounds_of(CREW_ROOTS + ROVER_ROOTS, 8.0)
    if len(points) < 8:
        raise RuntimeError("Human-scale crew and rover were not found")
    # Keep the cluster around the crew. Joe is a kilometer away on earlier frames.
    median_source = points
    median = sorted(median_source, key=lambda point: (point.x, point.y))[len(median_source) // 2]
    points = [point for point in points if (point - median).length <= 50.0]
    center = sum(points, Vector()) / len(points)
    for name in MARKERS:
        marker = bpy.data.objects.get(name)
        if marker is None:
            continue
        corners = [marker.matrix_world @ Vector(corner) for corner in marker.bound_box]
        extent = max(max(point.x for point in corners) - min(point.x for point in corners), max(point.y for point in corners) - min(point.y for point in corners))
        marker_center = sum(corners, Vector()) / len(corners)
        if extent <= 40.0 and (marker_center - center).length <= 50.0:
            points.extend(corners)
            center = sum(points, Vector()) / len(points)
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    center = (minimum + maximum) / 2.0
    camera_data = bpy.data.cameras.new("MS_Surface_Opening_Camera")
    camera_data.lens = 28
    camera_data.clip_start = 0.1
    camera_data.clip_end = 20000
    camera = bpy.data.objects.new("MS_Surface_Opening_Camera", camera_data)
    span = max(maximum.x - minimum.x, maximum.y - minimum.y, 8.0)
    camera.location = center + Vector((-span * 0.9, -span * 1.35, span * 0.72))
    camera.rotation_euler = (center + Vector((0.0, 0.0, 0.4)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    link(camera, measured)
    scene.camera = camera
    for screen in bpy.data.screens:
        if screen.name != "Layout":
            continue
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            space = area.spaces.active
            space.camera = camera
            space.region_3d.view_perspective = "CAMERA"
    camera["role"] = "Opening surface view of the human-scale crew, rover, and colored HiRISE ground"
    camera["excludes"] = "ludovisions_FC1_rig is about 27 m across and is not a framing target"

    after = fingerprint(site)
    terrain_after = fingerprint(terrain)
    if after != before or terrain_after != terrain_before:
        raise RuntimeError("Ground geometry changed")
    if tuple(round(float(v), 6) for v in globe_camera.location) != globe_before:
        raise RuntimeError("Globe camera moved")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    print("SAVED", OUTPUT)
    print("HASH", after["co_sha256"])
    print("LOCATION", after["location"], "SCALE", after["scale"])
    print("CAMERA", [round(float(v), 3) for v in camera.location])


if __name__ == "__main__":
    main()
