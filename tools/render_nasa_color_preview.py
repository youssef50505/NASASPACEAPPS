"""Render the NASA-colored site without saving the blend."""
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SITE = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"


def aim(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
site = bpy.data.objects[SITE]
camera_data = bpy.data.cameras.new("TEMP_NASA_Color_Camera")
camera_data.lens = 35
camera_data.clip_end = 20000
camera = bpy.data.objects.new("TEMP_NASA_Color_Camera", camera_data)
scene.collection.objects.link(camera)
center = site.matrix_world.translation
camera.location = center + Vector((0.0, -900.0, 520.0))
aim(camera, center + Vector((0.0, 0.0, 20.0)))
scene.camera = camera
for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(ROOT / "previews" / "nasa_color_site_preview.png")
if scene.render.engine.startswith("BLENDER_EEVEE"):
    scene.eevee.taa_render_samples = 16
hidden = []
for obj in scene.objects:
    if obj not in {site, camera}:
        hidden.append((obj, obj.hide_render))
        obj.hide_render = True
bpy.ops.render.render(write_still=True, scene=scene.name)
for obj, was_hidden in hidden:
    obj.hide_render = was_hidden
print("RENDERED", scene.render.filepath, scene.render.engine)
