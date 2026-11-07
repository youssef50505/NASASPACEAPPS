"""Read-only inventory of key scene objects and world bounds."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
records = []
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    name = obj.name
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = [min(float(v[i]) for v in corners) for i in range(3)]
    hi = [max(float(v[i]) for v in corners) for i in range(3)]
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    if (cx * cx + cy * cy) ** 0.5 > 80 and not any(token in name.lower() for token in ("mars_terrain", "hirise")):
        continue
    records.append({"name": name, "parent": obj.parent.name if obj.parent else None,
                    "hide_viewport": obj.hide_viewport, "hide_render": obj.hide_render,
                    "vertices": len(obj.data.vertices), "bounds_min": lo, "bounds_max": hi})
out = {"blend": bpy.data.filepath, "scene": bpy.context.scene.name,
       "camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None,
       "objects": records}
path = ROOT / "data" / "field_asset_bounds.json"
path.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
