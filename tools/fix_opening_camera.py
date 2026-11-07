"""Frame the opening camera on the crew while Joe is beside the rover."""
import array
import hashlib

import bpy
from mathutils import Vector

EXPECTED = "ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd"
ROOTS = [
    "Sketchfab_model.007",
    "Sketchfab_model.015",
    "Sketchfab_model",
    "Joe_Astronaut",
    "Sketchfab_model.003",
    "MSL",
    "Wheels_objs",
]
scene = bpy.context.scene
site = bpy.data.objects["NASA_HiRISE_DTM_Jezero_FieldSite_4m"]
coords = array.array("f", [0.0]) * (len(site.data.vertices) * 3)
site.data.vertices.foreach_get("co", coords)
digest = hashlib.sha256(coords.tobytes()).hexdigest()
if digest != EXPECTED:
    raise RuntimeError("Site hash changed before the camera fix")
globe = bpy.data.objects["MARS_NEW_Globe_Camera"]
globe_before = tuple(round(float(v), 6) for v in globe.location)
scene.frame_set(361)
grouped = []
for name in ROOTS:
    root = bpy.data.objects.get(name)
    if root is None:
        continue
    for obj in [root, *root.children_recursive]:
        if obj.type != "MESH":
            continue
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        extent = max(max(point[axis] for point in corners) - min(point[axis] for point in corners) for axis in range(3))
        if extent <= 8.0:
            grouped.append(corners)
centers = [sum(corners, Vector()) / len(corners) for corners in grouped]
order = sorted(range(len(centers)), key=lambda index: (centers[index].x, centers[index].y))
median = centers[order[len(order) // 2]]
chosen = [corners for corners, center in zip(grouped, centers) if (center - median).length <= 50.0]
points = [point for corners in chosen for point in corners]
minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
center = (minimum + maximum) / 2.0
camera = bpy.data.objects["MS_Surface_Opening_Camera"]
span = max(maximum.x - minimum.x, maximum.y - minimum.y, 12.0)
camera.location = center + Vector((-span * 0.55, -span * 0.85, span * 0.42))
camera.rotation_euler = (center + Vector((0.0, 0.0, 0.6)) - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera
for screen in bpy.data.screens:
    if screen.name != "Layout":
        continue
    for area in screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.camera = camera
            area.spaces.active.region_3d.view_perspective = "CAMERA"
if tuple(round(float(v), 6) for v in globe.location) != globe_before:
    raise RuntimeError("Globe camera moved")
site.data.vertices.foreach_get("co", coords)
if hashlib.sha256(coords.tobytes()).hexdigest() != EXPECTED:
    raise RuntimeError("Site hash changed")
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_mainfile()
print("CAMERA", [round(float(v), 2) for v in camera.location], "CENTER", [round(float(v), 2) for v in center], "SPAN", round(span, 2), "FRAME", scene.frame_current)
