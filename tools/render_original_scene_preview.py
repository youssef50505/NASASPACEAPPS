"""Render the original active scene to a preview without saving or editing the blend."""
from pathlib import Path
import bpy

scene = bpy.data.scenes.get("Scene")
if scene is None or scene.camera is None:
    raise RuntimeError("Original Scene or its camera is missing")
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(Path(__file__).resolve().parents[1] / "previews" / "mars_original_scene_before_recovery.png")
bpy.context.window.scene = scene
bpy.ops.render.render(write_still=True, scene=scene.name)
print("Original blend was not saved or modified; preview rendered from the source scene.")
