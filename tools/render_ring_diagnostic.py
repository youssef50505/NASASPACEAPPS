"""Diagnostic render: hide the obstructing White_Ring in memory only."""
from pathlib import Path
import bpy

root = Path(__file__).resolve().parents[1] / "previews"
scene = bpy.context.scene
ring = bpy.data.objects.get("White_Ring")
if ring is None:
    raise RuntimeError("White_Ring not found")
ring.hide_render = True
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.camera = bpy.data.objects["Mars_Camera"]
scene.render.filepath = str(root / "diagnostic_without_White_Ring.png")
bpy.ops.render.render(write_still=True, scene=scene.name)
print("Rendered diagnostic only; White_Ring visibility and blend file were not saved.")
