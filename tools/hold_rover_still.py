"""Hold the rover and wheels at the opening pose for the whole timeline."""
import array
import hashlib
from pathlib import Path

import bpy

EXPECTED = "ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd"
scene = bpy.context.scene
site = bpy.data.objects["NASA_HiRISE_DTM_Jezero_FieldSite_4m"]
coords = array.array("f", [0.0]) * (len(site.data.vertices) * 3)
site.data.vertices.foreach_get("co", coords)
if hashlib.sha256(coords.tobytes()).hexdigest() != EXPECTED:
    raise RuntimeError("Site hash changed")

scene.frame_set(76)
hold_frame = scene.frame_end

def fcurves(action):
    found = []
    for layer in action.layers:
        for strip in layer.strips:
            bags = getattr(strip, "channelbags", None) or []
            for bag in bags:
                found.extend(bag.fcurves)
    return found

for name in ("MSL", "Wheels_objs"):
    obj = bpy.data.objects[name]
    location = tuple(float(v) for v in obj.location)
    rotation = tuple(float(v) for v in obj.rotation_euler)
    action = obj.animation_data.action
    for fcurve in fcurves(action):
        if fcurve.data_path == "location":
            value = location[fcurve.array_index]
        elif fcurve.data_path == "rotation_euler":
            value = rotation[fcurve.array_index]
        else:
            continue
        fcurve.keyframe_points.clear()
        for frame in (1.0, float(hold_frame)):
            key = fcurve.keyframe_points.insert(frame, value, options={"FAST"})
            key.interpolation = "CONSTANT"
        fcurve.update()
    obj["motion_note"] = "Held at the frame-76 pose. Wheels are one mesh and are not spun."

scene.frame_set(20000)
rover = bpy.data.objects["MSL"]
wheels = bpy.data.objects["Wheels_objs"]
print("ROVER", [round(float(v), 2) for v in rover.location], "WHEELS", [round(float(v), 2) for v in wheels.location])
if abs(rover.location.x - 1.09) > 0.05 or abs(wheels.location.x - 14.18) > 0.05:
    raise RuntimeError("Hold did not stick")
if hashlib.sha256(coords.tobytes()).hexdigest() != EXPECTED:
    raise RuntimeError("Site hash changed after the hold")
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_mainfile()
print("HELD")
