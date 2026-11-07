"""Find what turns the rover and crew back off."""
import bpy

scene = bpy.context.scene
scene.frame_set(1)
msl = bpy.data.objects["MSL"]
print("MSL anim", None if msl.animation_data is None else msl.animation_data.action)
print("MSL hide now", msl.hide_render, msl.hide_viewport)
child = next(obj for obj in bpy.data.objects["Joe_Astronaut"].children_recursive if obj.type == "MESH")
print("JOE_MESH", child.name, child.hide_render, child.hide_viewport, "anim", None if child.animation_data is None else child.animation_data.action)
count = 0
for obj in bpy.data.objects:
    anim = obj.animation_data
    if anim is None or anim.action is None:
        continue
    action = anim.action
    curves = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            bags = getattr(strip, "channelbags", None) or []
            for bag in bags:
                curves.extend(bag.fcurves)
    try:
        curves.extend(action.fcurves)
    except Exception:
        pass
    for fc in curves:
        if "hide" in fc.data_path:
            count += 1
            if count <= 12:
                print("HIDE_KEY", obj.name, fc.data_path, [(round(kp.co[0]), round(kp.co[1], 2)) for kp in fc.keyframe_points[:4]])
print("HIDE_KEY_COUNT", count)
