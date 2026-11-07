"""Read-only structural verification of the integrated HiRISE scene."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

scene = bpy.context.scene
terrain = bpy.data.objects.get("Mars_Terrain")
site = bpy.data.objects.get("NASA_HiRISE_DTM_Jezero_FieldSite_4m")
if site is None:
    raise RuntimeError("Expected integrated HiRISE site object is missing")
corners = [site.matrix_world @ Vector(c) for c in site.bound_box]
report = {
    "blend": bpy.data.filepath,
    "scene_count": len(bpy.data.scenes),
    "active_scene": scene.name,
    "object_count": len(scene.objects),
    "camera": scene.camera.name if scene.camera else None,
    "world": scene.world.name if scene.world else None,
    "frame": scene.frame_current,
    "site_object": site.name,
    "site_mesh_vertices": len(site.data.vertices),
    "site_mesh_faces": len(site.data.polygons),
    "site_materials": [m.name for m in site.data.materials if m],
    "site_world_bounds_min": [min(float(v[i]) for v in corners) for i in range(3)],
    "site_world_bounds_max": [max(float(v[i]) for v in corners) for i in range(3)],
    "site_custom_props": {k: site[k] for k in site.keys()},
    "base_terrain_location_z": float(terrain.location.z) if terrain else None,
    "site_collection": [c.name for c in site.users_collection],
    "custom_key_script_present": bool(bpy.data.texts.get("front_view_models.py")),
}
out = Path(__file__).resolve().parents[1] / "data" / "verify_MARS_SENTINEL_NASA_Terrain_Study_HIRISE_SITE.json"
out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
print(json.dumps(report, indent=2, default=str))
