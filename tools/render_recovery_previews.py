"""Render low-cost Workbench proof images; never save the .blend file."""
from pathlib import Path
import bpy

root = Path(__file__).resolve().parents[1] / "previews"
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "WORLD"

for camera_name in ("Mars_Camera", "MARS_NEW_Globe_Camera", "Mars_Orbit_View_Camera"):
    camera = bpy.data.objects.get(camera_name)
    if not camera or camera.type != "CAMERA":
        print(f"SKIP missing camera: {camera_name}")
        continue
    scene.camera = camera
    scene.render.filepath = str(root / f"recovered_preview_{camera_name}.png")
    print(f"RENDER {camera_name} -> {scene.render.filepath}")
    bpy.ops.render.render(write_still=True, scene=scene.name)
print("Previews rendered in memory; blend file not saved.")
