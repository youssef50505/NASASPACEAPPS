"""Report mesh-bottom elevation for known field-site model roots."""
import bpy
from mathutils import Vector

names = ["Sketchfab_model.007", "ludovisions_FC1_rig", "Sketchfab_model.015",
         "Sketchfab_model", "Joe_Astronaut", "Sketchfab_model.003"]
scene = bpy.context.scene
for name in names:
    root = bpy.data.objects.get(name)
    if root is None:
        continue
    points = []
    for obj in scene.objects:
        parent = obj
        while parent is not None and parent != root:
            parent = parent.parent
        if parent == root and obj.type == "MESH" and not obj.hide_render:
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if points:
        print(name, "loc", tuple(round(float(v), 3) for v in root.location),
              "mesh_count", len(points) // 8,
              "z_min", round(min(float(p.z) for p in points), 3),
              "z_max", round(max(float(p.z) for p in points), 3))
