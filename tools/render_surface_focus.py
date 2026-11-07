"""Render the tightened opening camera and check Joe's new walk."""
import hashlib
import array
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd"
scene = bpy.context.scene
site = bpy.data.objects["NASA_HiRISE_DTM_Jezero_FieldSite_4m"]
coords = array.array("f", [0.0]) * (len(site.data.vertices) * 3)
site.data.vertices.foreach_get("co", coords)
digest = hashlib.sha256(coords.tobytes()).hexdigest()
joe = bpy.data.objects["Joe_Astronaut"]
scene.frame_set(76)
start = [round(float(v), 2) for v in joe.matrix_world.translation]
scene.frame_set(458)
landing = [round(float(v), 2) for v in joe.matrix_world.translation]
scene.frame_set(76)
print("HASH", digest == EXPECTED, "JOE1", start, "JOE328", landing)
print("RING", bpy.data.objects["White_Circle_Marker"].hide_render, bpy.data.objects["White_Circle_Marker"].hide_viewport)
print("GLOBE_CAM", [round(float(v), 2) for v in bpy.data.objects["MARS_NEW_Globe_Camera"].location])
print("FRAME", scene.frame_current, "CLIP", scene.camera.data.clip_end)

for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
if scene.render.engine.startswith("BLENDER_EEVEE"):
    scene.eevee.taa_render_samples = 8
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(ROOT / "previews" / "surface_focus_opening.png")
bpy.ops.render.render(write_still=True, scene=scene.name)
print("RENDERED", scene.render.filepath)
