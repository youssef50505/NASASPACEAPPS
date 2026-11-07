"""Reopen the exploration blend and confirm the ground mesh did not move."""
from __future__ import annotations

import array
import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT / "data" / "exploration_integration_check.json").read_text(encoding="utf-8"))
SITE = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"


def digest(obj: bpy.types.Object) -> str:
    coords = array.array("f", [0.0]) * (len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get("co", coords)
    return hashlib.sha256(coords.tobytes()).hexdigest()


def main() -> None:
    scene = bpy.context.scene
    site = bpy.data.objects[SITE]
    terrain = bpy.data.objects["Mars_Terrain"]
    checks = {
        "scene_camera": scene.camera.name if scene.camera else None,
        "frame": scene.frame_current,
        "site_vertices": len(site.data.vertices),
        "site_location": [round(float(v), 6) for v in site.location],
        "site_scale": [round(float(v), 6) for v in site.scale],
        "site_hash": digest(site),
        "site_material": site.data.materials[0].name if site.data.materials else None,
        "terrain_location_z": round(float(terrain.location.z), 6),
        "terrain_shape_keys": {key.name: round(float(key.value), 6) for key in terrain.data.shape_keys.key_blocks},
        "image_packed": bpy.data.images.get("jez_hirise_site_nasa_color_1m.png").packed_file is not None,
        "routes": [name for name in ("MS_Route_Safest_HiRISE", "MS_Route_Shortest_HiRISE", "MS_Route_Science_HiRISE") if bpy.data.objects.get(name)],
        "landing": bpy.data.objects.get("MS_Science_Octavia_E_Butler_Landing") is not None,
        "tour_action": bpy.data.objects["MS_Tour_Camera"].animation_data.action.name if bpy.data.objects["MS_Tour_Camera"].animation_data and bpy.data.objects["MS_Tour_Camera"].animation_data.action else None,
        "hazards": sum(1 for obj in scene.objects if obj.name.startswith("MS_Hazard_Slope_")),
        "msl_location": [round(float(v), 3) for v in bpy.data.objects["MSL"].location],
    }
    ok = (
        checks["site_vertices"] == REPORT["site_vertices"]
        and checks["site_hash"] == REPORT["site_co_sha256"]
        and checks["site_location"] == [0.23, -0.49, 0.014996]
        and checks["site_scale"] == [1.0, 1.0, 1.0]
        and checks["terrain_shape_keys"]["Flat_Ground"] == 1.0
        and abs(checks["terrain_location_z"] + 54.84) < 0.001
        and checks["site_material"] == "Mars_NASA_HiRISE_Viking_Color"
        and checks["image_packed"]
        and len(checks["routes"]) == 3
        and checks["landing"]
        and checks["hazards"] == REPORT["hazard_markers"]
        and checks["tour_action"]
        and checks["scene_camera"] == "MARS_NEW_Globe_Camera"
        and checks["frame"] == 112
    )
    out = {"ok": ok, "checks": checks}
    (ROOT / "data" / "verify_exploration_geometry.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("VERIFY", "OK" if ok else "FAILED")
    print(json.dumps(checks))
    if not ok:
        raise RuntimeError("Exploration geometry verification failed")


if __name__ == "__main__":
    main()
