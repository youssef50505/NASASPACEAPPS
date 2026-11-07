"""Thin the routes, tighten the opening shot, and start Joe beside the rover.

The HiRISE mesh and Mars_Terrain stay put. The globe camera is not edited.
This saves a new blend and leaves the readable file as the rollback.
"""
from __future__ import annotations

import array
import hashlib
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend"
OUTPUT = ROOT / "MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend"
COLOR = ROOT / "data" / "jez_hirise_site_local_rgb_1m.png"
EXPECTED = "ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd"
SITE_NAME = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"
ROUTE_NAMES = (
    "MS_Route_Shortest_HiRISE",
    "MS_Route_Safest_HiRISE",
    "MS_Route_Science_HiRISE",
)
CREW_ROOTS = (
    "Sketchfab_model.007",
    "Sketchfab_model.015",
    "Sketchfab_model",
    "Sketchfab_model.003",
    "Joe_Astronaut",
)


def fingerprint(obj: bpy.types.Object) -> str:
    coords = array.array("f", [0.0]) * (len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get("co", coords)
    return hashlib.sha256(coords.tobytes()).hexdigest()


def action_fcurves(action: bpy.types.Action):
    found = []
    for layer in action.layers:
        for strip in layer.strips:
            bags = getattr(strip, "channelbags", None)
            if not bags:
                continue
            for bag in bags:
                found.extend(bag.fcurves)
    return found


def surface_z(site: bpy.types.Object, east: float, north: float) -> float:
    core = 1024
    skirt = 20
    spacing = 4.0
    half = (core - 1) * spacing / 2.0
    side = core + 2 * skirt
    coords = array.array("f", [0.0]) * (len(site.data.vertices) * 3)
    site.data.vertices.foreach_get("co", coords)
    col = min(core - 1, max(0, round((east + half) / spacing)))
    row = min(core - 1, max(0, round((half - north) / spacing)))
    index = ((row + skirt) * side + (col + skirt)) * 3 + 2
    return float(site.location.z) + coords[index]


def reverse_walk(obj: bpy.types.Object, site: bpy.types.Object) -> None:
    path_start = 210.0
    action = obj.animation_data.action
    start_values = {"location": [0.0, 0.0, 0.0], "rotation_euler": [0.0, 0.0, 0.0]}
    for fcurve in action_fcurves(action):
        samples = []
        for key in fcurve.keyframe_points:
            frame = float(key.co[0])
            if 112.0 <= frame <= 360.0:
                samples.append((frame, float(key.co[1]), key.interpolation))
        if not samples:
            continue
        samples.sort(key=lambda item: item[0], reverse=True)
        if fcurve.data_path in start_values and 0 <= fcurve.array_index < 3:
            start_values[fcurve.data_path][fcurve.array_index] = samples[0][1]
        fcurve.keyframe_points.clear()
        for old_frame, value, interpolation in samples:
            new_frame = path_start + (360.0 - old_frame)
            key = fcurve.keyframe_points.insert(new_frame, value, options={"FAST"})
            key.interpolation = interpolation
        fcurve.update()
    rover = bpy.data.objects["MSL"].matrix_world.translation
    beside_x = float(rover.x) + 3.2
    beside_y = float(rover.y) - 1.6
    ground = surface_z(site, beside_x - float(site.location.x), beside_y - float(site.location.y))
    old_ground = surface_z(
        site,
        start_values["location"][0] - float(site.location.x),
        start_values["location"][1] - float(site.location.y),
    )
    foot_offset = start_values["location"][2] - old_ground
    start_values["location"] = [beside_x, beside_y, ground + foot_offset]
    for fcurve in action_fcurves(action):
        if fcurve.data_path not in start_values:
            continue
        value = start_values[fcurve.data_path][fcurve.array_index]
        for frame in (1.0, 90.0):
            key = fcurve.keyframe_points.insert(frame, value, options={"FAST"})
            key.interpolation = "CONSTANT" if frame == 1.0 else "BEZIER"
        fcurve.update()


def mesh_corners(obj: bpy.types.Object, limit: float) -> list[Vector]:
    if obj.type != "MESH":
        return []
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    extent = max(max(point[axis] for point in corners) - min(point[axis] for point in corners) for axis in range(3))
    if extent > limit:
        return []
    return corners


def main() -> None:
    if Path(bpy.data.filepath).name != SOURCE:
        raise RuntimeError(f"Open {SOURCE} first")
    scene = bpy.context.scene
    site = bpy.data.objects[SITE_NAME]
    terrain = bpy.data.objects["Mars_Terrain"]
    globe_camera = bpy.data.objects["MARS_NEW_Globe_Camera"]
    globe = bpy.data.objects["MARS_NEW_Globe"]
    before = fingerprint(site)
    terrain_z = round(float(terrain.location.z), 5)
    globe_camera_location = tuple(round(float(v), 6) for v in globe_camera.location)
    globe_location = tuple(round(float(v), 3) for v in globe.location)
    if before != EXPECTED:
        raise RuntimeError("Site hash does not match the readable file")

    for name in ROUTE_NAMES:
        curve = bpy.data.objects[name]
        curve.data.bevel_depth = 0.18
        curve.data.bevel_resolution = 2
        for spline in curve.data.splines:
            for point in spline.points:
                x, y, z, w = point.co
                point.co = (x, y, z - 1.42, w)
        curve["display"] = "0.36 m wide line sitting on the HiRISE surface"

    ring = bpy.data.objects["White_Circle_Marker"]
    ring.hide_viewport = True
    ring.hide_render = True
    ring["opening_view"] = "Hidden from the opening shot. The curve and its 40 m bevel are still in the file."

    joe = bpy.data.objects["Joe_Astronaut"]
    reverse_walk(joe, site)
    scene.frame_set(76)

    def show_small_meshes(root_name: str) -> None:
        root = bpy.data.objects.get(root_name)
        if root is None:
            return
        root.hide_render = False
        root.hide_viewport = False
        for obj in [root, *root.children_recursive]:
            if obj.type != "MESH":
                continue
            corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            extent = max(max(point[axis] for point in corners) - min(point[axis] for point in corners) for axis in range(3))
            if extent <= 8.0:
                obj.hide_render = False
                obj.hide_viewport = False

    for name in ("MSL", "Wheels_objs", *CREW_ROOTS):
        show_small_meshes(name)
    rover = bpy.data.objects["MSL"].matrix_world.translation
    points = []
    for name in ("MSL", "Wheels_objs"):
        root = bpy.data.objects.get(name)
        if root is None:
            continue
        for obj in [root, *root.children_recursive]:
            points.extend(mesh_corners(obj, 8.0))
    people = []
    for name in CREW_ROOTS:
        root = bpy.data.objects.get(name)
        if root is None:
            continue
        for obj in [root, *root.children_recursive]:
            corners = mesh_corners(obj, 8.0)
            if not corners:
                continue
            center = sum(corners, Vector()) / len(corners)
            if (center - rover).length <= 8.0:
                people.extend(corners)
    if len(people) < 8:
        raise RuntimeError("No astronaut stands within 8 m of the rover at frame 1")
    points.extend(people)
    target = Vector((float(rover.x) + 1.6, float(rover.y) - 0.8, float(rover.z) + 1.2))
    camera = bpy.data.objects["MS_Surface_Opening_Camera"]
    camera.location = target + Vector((-4.2, -5.4, 2.2))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 28
    camera.data.clip_start = 0.05
    camera.data.clip_end = 80.0
    camera.data.dof.use_dof = False
    span = (camera.location - target).length
    scene.camera = camera
    scene.frame_current = 76
    for screen in bpy.data.screens:
        if screen.name != "Layout":
            continue
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            space = area.spaces.active
            space.camera = camera
            space.region_3d.view_perspective = "CAMERA"
            space.clip_end = 80.0

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
        raise RuntimeError("Surface material has no image")
    site["color_edge_blend_m"] = 30

    after = fingerprint(site)
    if after != before or round(float(terrain.location.z), 5) != terrain_z:
        raise RuntimeError("Ground geometry changed")
    if tuple(round(float(v), 6) for v in globe_camera.location) != globe_camera_location:
        raise RuntimeError("Globe camera moved")
    if tuple(round(float(v), 3) for v in globe.location) != globe_location:
        raise RuntimeError("Globe moved")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    print("SAVED", OUTPUT)
    print("JOE", [round(float(v), 2) for v in joe.matrix_world.translation])
    print("CAM", [round(float(v), 2) for v in camera.location], "DIST", round(span, 2))
    print("BEVEL", bpy.data.objects[ROUTE_NAMES[0]].data.bevel_depth)


if __name__ == "__main__":
    main()
