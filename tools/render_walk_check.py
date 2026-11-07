"""Render the opening and one step of the green-route walk."""
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
print("HASH", hashlib.sha256(coords.tobytes()).hexdigest() == EXPECTED)
walker = bpy.data.objects["Sketchfab_model"]
joe = bpy.data.objects["Joe_Astronaut"]
rover = bpy.data.objects["MSL"]
for frame in (76, 500, 1514):
    scene.frame_set(frame)
    print(
        "F", frame,
        "WALK", [round(float(v), 1) for v in walker.matrix_world.translation],
        "JOE", [round(float(v), 1) for v in joe.matrix_world.translation],
        "ROVER", [round(float(v), 2) for v in rover.location],
    )

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
for frame, name in ((76, "surface_walk_open.png"), (500, "surface_walk_step.png")):
    scene.frame_set(frame)
    scene.render.filepath = str(ROOT / "previews" / name)
    bpy.ops.render.render(write_still=True, scene=scene.name)
    print("RENDERED", scene.render.filepath)
