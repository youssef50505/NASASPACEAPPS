"""Name the curves sitting next to the crew."""
import bpy
from mathutils import Vector

scene = bpy.context.scene
scene.frame_set(361)
origin = Vector((7.0, 8.0, 1.0))
for obj in scene.objects:
    if obj.type != "CURVE":
        continue
    point = obj.matrix_world.translation
    if (point - origin).length > 80.0 and obj.name.startswith("MS_Route"):
        print("ROUTE", obj.name, "bevel", round(obj.data.bevel_depth, 2), "hide", obj.hide_render)
        continue
    if (point - origin).length > 80.0:
        continue
    color = None
    if obj.data.materials:
        color = [round(float(v), 2) for v in obj.data.materials[0].diffuse_color]
    print("NEAR", obj.name, "at", [round(float(v), 1) for v in point], "bevel", round(obj.data.bevel_depth, 2), "color", color, "hide", obj.hide_render)
