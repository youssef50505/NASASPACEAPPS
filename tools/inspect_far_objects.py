"""Find objects far from the terrain, likely the orbiting satellite."""
import bpy
from mathutils import Vector

globe = bpy.data.objects["MARS_NEW_Globe"]
center = globe.matrix_world.translation
radius = max(globe.dimensions) / 2.0
print("RADIUS", round(radius, 1), "CENTER", [round(float(v), 1) for v in center])
far = []
for obj in bpy.data.objects:
    if obj.type not in {"MESH", "EMPTY", "CAMERA"}:
        continue
    loc = obj.matrix_world.translation
    dist = (loc - center).length
    if dist < radius * 1.05:
        continue
    if obj.name.startswith("MARS_NEW_Globe"):
        continue
    far.append((dist, obj.name, obj.type, [round(float(v), 1) for v in loc], [round(float(v), 1) for v in obj.dimensions]))
far.sort(reverse=True)
print("FAR", len(far))
for row in far[:40]:
    print(row)
