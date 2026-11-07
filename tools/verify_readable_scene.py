"""Reopen the readable blend and confirm the frozen ground and the new view."""
import hashlib
import array
from pathlib import Path

import bpy

EXPECTED = "ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd"
site = bpy.data.objects["NASA_HiRISE_DTM_Jezero_FieldSite_4m"]
terrain = bpy.data.objects["Mars_Terrain"]
coords = array.array("f", [0.0]) * (len(site.data.vertices) * 3)
site.data.vertices.foreach_get("co", coords)
digest = hashlib.sha256(coords.tobytes()).hexdigest()
camera = bpy.context.scene.camera
routes = {}
for name in ("MS_Route_Shortest_HiRISE", "MS_Route_Safest_HiRISE", "MS_Route_Science_HiRISE"):
    obj = bpy.data.objects[name]
    routes[name] = {
        "distance_m": obj["distance_m"],
        "elevation_change_m": obj["elevation_change_m"],
        "max_slope_deg": obj["max_slope_deg"],
        "bevel": obj.data.bevel_depth,
    }
layout = bpy.data.screens["Layout"]
views = []
for area in layout.areas:
    if area.type == "VIEW_3D":
        views.append(area.spaces.active.region_3d.view_perspective)
print("FILE", Path(bpy.data.filepath).name)
print("HASH", digest, "MATCH", digest == EXPECTED)
print("VERTS", len(site.data.vertices), "LOC", [round(float(v), 6) for v in site.location], "SCALE", [round(float(v), 6) for v in site.scale])
print("TERRAIN_Z", round(float(terrain.location.z), 2))
print("CAMERA", None if camera is None else camera.name)
print("LAYOUT", views)
print("ROUTES", routes)
print("ROCHETTE", bpy.data.objects.get("MS_Science_Rochette") is not None)
print("GLOBE_CAMERA", [round(float(v), 3) for v in bpy.data.objects["MARS_NEW_Globe_Camera"].location])
if digest != EXPECTED or camera is None or camera.name != "MS_Surface_Opening_Camera":
    raise SystemExit(1)
print("VERIFY_OK")
