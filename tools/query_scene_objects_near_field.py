"""Report geometry whose world bounds overlap the team site."""
import bpy
from mathutils import Vector

for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = [min(float(v[i]) for v in corners) for i in range(3)]
    hi = [max(float(v[i]) for v in corners) for i in range(3)]
    if lo[0] < 22 and hi[0] > -22 and lo[1] < 25 and hi[1] > -10 and lo[2] < 25 and hi[2] > -8:
        sx, sy, sz = hi[0]-lo[0], hi[1]-lo[1], hi[2]-lo[2]
        if sx > 7 or sy > 7 or sz > 7:
            print(obj.name, "parent", obj.parent.name if obj.parent else None,
                  "bounds", tuple(round(v, 2) for v in lo), tuple(round(v, 2) for v in hi),
                  "hidden", obj.hide_render)
