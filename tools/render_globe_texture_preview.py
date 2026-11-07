"""Texture-mode Workbench view of the restored globe; no blend save."""
from pathlib import Path
import bpy

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "TEXTURE"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.camera = bpy.data.objects["MARS_NEW_Globe_Camera"]
scene.render.filepath = str(Path(__file__).resolve().parents[1] / "previews" / "recovered_globe_texture_preview.png")
bpy.ops.render.render(write_still=True, scene=scene.name)
print("Texture preview rendered only; blend file not saved.")
