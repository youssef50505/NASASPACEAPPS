"""Read route bevels, the work-area ring, the globe, and Joe's keys."""
import bpy

scene = bpy.context.scene
print("FRAME", scene.frame_current, scene.frame_start, scene.frame_end)
print("CAM", scene.camera.name if scene.camera else None)
for name in (
    "MS_Route_Shortest_HiRISE",
    "MS_Route_Safest_HiRISE",
    "MS_Route_Science_HiRISE",
    "White_Circle_Marker",
    "White_Ring",
    "MARS_NEW_Globe",
    "MARS_NEW_Globe_Camera",
    "Joe_Astronaut",
    "MS_Surface_Opening_Camera",
):
    obj = bpy.data.objects.get(name)
    if obj is None:
        print("MISSING", name)
        continue
    extra = ""
    if obj.type == "CURVE":
        extra = f" bevel={obj.data.bevel_depth:.3f} points={sum(len(s.points) for s in obj.data.splines)} extrude={obj.data.extrude:.3f}"
    anim = obj.animation_data
    action = None if anim is None or anim.action is None else anim.action.name
    print(
        name,
        obj.type,
        "loc",
        [round(float(v), 2) for v in obj.location],
        "dim",
        [round(float(v), 2) for v in obj.dimensions],
        "parent",
        None if obj.parent is None else obj.parent.name,
        "action",
        action,
        "hide",
        obj.hide_viewport,
        obj.hide_render,
        extra,
    )

joe = bpy.data.objects["Joe_Astronaut"]
ad = joe.animation_data
if ad and ad.action:
    action = ad.action
    print("JOE_ACTION", action.name, "layers", len(getattr(action, "layers", [])))
    fcurves = []
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                bags = getattr(strip, "channelbags", None)
                if bags is None:
                    continue
                for bag in bags:
                    fcurves.extend(bag.fcurves)
    if hasattr(action, "fcurves"):
        try:
            fcurves.extend(action.fcurves)
        except Exception as exc:
            print("FCURVE_ERR", exc)
    for fc in fcurves:
        keys = [(int(kp.co[0]), round(float(kp.co[1]), 3)) for kp in fc.keyframe_points]
        print("FC", fc.data_path, fc.array_index, "n", len(keys), "head", keys[:4], "tail", keys[-3:])
if ad and ad.nla_tracks:
    for track in ad.nla_tracks:
        for strip in track.strips:
            print("NLA", track.name, strip.name, strip.frame_start, strip.frame_end, strip.action.name if strip.action else None)

globe = bpy.data.objects.get("MARS_NEW_Globe")
cam = bpy.data.objects.get("MS_Surface_Opening_Camera")
if globe and cam:
    print("GLOBE_WORLD", [round(float(v), 1) for v in globe.matrix_world.translation], "scale", [round(float(v), 3) for v in globe.scale])
    print("CAM_WORLD", [round(float(v), 2) for v in cam.matrix_world.translation])
    print("CAM_ROT", [round(float(v), 3) for v in cam.rotation_euler])
