"""Render focused material previews from restored scene without saving it."""
from pathlib import Path
import bpy

root = Path(__file__).resolve().parents[1] / "previews"
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.eevee.taa_render_samples = 16

for camera_name in ("Mars_Camera", "MARS_NEW_Globe_Camera"):
    camera = bpy.data.objects.get(camera_name)
    if camera is None:
        print(f"SKIP missing camera: {camera_name}")
        continue
    scene.camera = camera
    scene.render.filepath = str(root / f"recovered_eevee_{camera_name}.png")
    print(f"RENDER {camera_name}")
    bpy.ops.render.render(write_still=True, scene=scene.name)
print("Material previews rendered; blend file not saved.")
