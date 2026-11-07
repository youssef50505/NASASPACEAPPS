"""Print world bounds of the human-scale crew and rover meshes."""
import bpy
from mathutils import Vector

roots = [
    "Sketchfab_model.007",
    "Sketchfab_model.015",
    "Sketchfab_model",
    "Joe_Astronaut",
    "Sketchfab_model.003",
    "MSL",
    "Wheels_objs",
    "Joe_JA",
]
for name in roots:
    root = bpy.data.objects.get(name)
    if root is None:
        print("MISSING", name)
        continue
    print("ROOT", name, root.type, [round(float(v), 2) for v in root.matrix_world.translation], "dim", [round(float(v), 2) for v in root.dimensions])
    for obj in [root, *root.children_recursive]:
        if obj.type != "MESH":
            continue
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        extent = max(max(p[i] for p in corners) - min(p[i] for p in corners) for i in range(3))
        center = sum(corners, Vector()) / len(corners)
        if extent <= 12:
            print("  ", obj.name, "ext", round(extent, 2), "at", [round(float(v), 1) for v in center])
