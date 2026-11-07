"""See whether Mixamo Walk moves the rig or only the pose."""
import bpy

arm = bpy.data.objects["Object_4"]
action = arm.animation_data.action
paths = set()
for layer in action.layers:
    for strip in layer.strips:
        bags = getattr(strip, "channelbags", None) or []
        for bag in bags:
            for fcurve in bag.fcurves:
                paths.add(fcurve.data_path.split(".")[0] if "pose" not in fcurve.data_path else fcurve.data_path.split('"')[1] if '"' in fcurve.data_path else fcurve.data_path)
print("ACTION", action.name, "RANGE", tuple(action.frame_range))
interesting = [p for p in paths if "location" in p or "hips" in p.lower() or p in {"location", "rotation_euler"}]
print("PATH_COUNT", len(paths))
for path in sorted(paths):
    if any(word in path.lower() for word in ("location", "hip", "root", "mixamorig")):
        print(path)
        break
print("--- sample ---")
shown = 0
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fcurve in bag.fcurves:
                if "location" in fcurve.data_path and ("Hips" in fcurve.data_path or fcurve.data_path == "location"):
                    keys = [(round(kp.co[0], 1), round(kp.co[1], 4)) for kp in fcurve.keyframe_points]
                    print(fcurve.data_path, fcurve.array_index, "n", len(keys), keys[:3], keys[-2:])
                    shown += 1
                    if shown > 8:
                        raise SystemExit
print("DONE", shown)
