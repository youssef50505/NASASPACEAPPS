"""Read the walk rig, the green route, and Joe's hold keys."""
import bpy

scene = bpy.context.scene
scene.frame_set(76)
root = bpy.data.objects["Sketchfab_model"]
arm = bpy.data.objects["Object_4"]
print("ROOT", [round(float(v), 3) for v in root.matrix_world.translation], "rot", [round(float(v), 3) for v in root.matrix_world.to_euler()])
print("ARM", [round(float(v), 3) for v in arm.matrix_world.translation], "parent", arm.parent.name)
action = arm.animation_data.action
print("WALK", action.name, "frame", action.frame_range[:] if hasattr(action, "frame_range") else None)
print("ARM_PARENT_CHAIN")
parent = arm
while parent is not None:
    print(" ", parent.name, parent.type, "loc", [round(float(v), 3) for v in parent.location])
    parent = parent.parent

curve = bpy.data.objects["MS_Route_Safest_HiRISE"]
spline = curve.data.splines[0]
print("ROUTE_POINTS", len(spline.points), "bevel", curve.data.bevel_depth)
for index in (0, 1, len(spline.points) // 2, len(spline.points) - 1):
    co = spline.points[index].co
    print(" P", index, [round(float(v), 2) for v in co])

joe = bpy.data.objects["Joe_Astronaut"]
print("JOE76", [round(float(v), 2) for v in joe.matrix_world.translation])
for fcurve in []:
    pass
action = joe.animation_data.action
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fcurve in bag.fcurves:
                if fcurve.data_path == "location" and fcurve.array_index == 0:
                    print("JOE_X", [(round(kp.co[0]), round(kp.co[1], 2)) for kp in fcurve.keyframe_points])

msl = bpy.data.objects["MSL"]
wheels = bpy.data.objects["Wheels_objs"]
print("MSL", [round(float(v), 2) for v in msl.location], msl.animation_data.action.name if msl.animation_data and msl.animation_data.action else None)
print("WHEELS", [round(float(v), 2) for v in wheels.location], wheels.animation_data.action.name if wheels.animation_data and wheels.animation_data.action else None)
print("FPS", scene.render.fps, "end", scene.frame_end)
