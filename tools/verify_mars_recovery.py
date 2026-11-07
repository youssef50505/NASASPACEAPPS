"""Reopen and verify the recovered scene without executing embedded scripts."""
import json
from pathlib import Path
import bpy

scene = bpy.context.scene
terrain = bpy.data.objects.get("Mars_Terrain")
camera = scene.camera
checks = {
    "file": bpy.data.filepath,
    "active_scene": scene.name if scene else None,
    "scene_count": len(bpy.data.scenes),
    "scene_objects": len(scene.objects) if scene else None,
    "camera": camera.name if camera else None,
    "world": scene.world.name if scene and scene.world else None,
    "frame": scene.frame_current if scene else None,
    "terrain_exists": terrain is not None,
    "terrain_collections": [c.name for c in terrain.users_collection] if terrain else [],
    "site_link_collection_objects": len(bpy.data.collections["FIELD SITE | Jezero (linked original assets)"].objects),
    "original_text_blocks_present": [n for n in ("front_view_models.py", "mars_dashboard.py") if bpy.data.texts.get(n)],
    "terrain_shape_keys": ({
        key.name: {"value": round(float(key.value), 6), "slider_min": float(key.slider_min), "slider_max": float(key.slider_max)}
        for key in terrain.data.shape_keys.key_blocks
    } if terrain and terrain.data.shape_keys else {}),
    "terrain_custom_props": {k: terrain[k] for k in terrain.keys() if k.startswith("mars_site_")} if terrain else {},
}
output = Path(__file__).resolve().parents[1] / "data" / "verify_MARS_SENTINEL_RECOVERED.json"
output.write_text(json.dumps(checks, indent=2, default=str), encoding="utf-8")
print(json.dumps(checks, indent=2, default=str))
