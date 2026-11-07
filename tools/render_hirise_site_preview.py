"""Render a lightweight, non-saving preview of the crew standing on real DTM."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
site = bpy.data.objects.get("NASA_HiRISE_DTM_Jezero_FieldSite_4m")
if site is None:
    raise RuntimeError("HiRISE site mesh not found")

def aim(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()

camera_data = bpy.data.cameras.new("TEMP_HiRISE_Field_Preview_Camera")
camera = bpy.data.objects.new("TEMP_HiRISE_Field_Preview_Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (0.0, -28.0, 13.0)
camera.data.lens = 38.0
camera.data.clip_end = 10000.0
aim(camera, (0.0, 9.0, 0.4))

scene.camera = camera
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.display.shading.light = "STUDIO"
scene.display.shading.studio_light = "paint.sl"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.background_type = "WORLD"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "WORLD"
scene.render.filepath = str(ROOT / "previews" / "hirise_field_site_preview.png")
keep = {site, camera}
crew_roots = [bpy.data.objects.get(name) for name in (
    "Sketchfab_model.007", "ludovisions_FC1_rig", "Sketchfab_model.015",
    "Sketchfab_model", "Joe_Astronaut", "Sketchfab_model.003")]
for obj in scene.objects:
    parent = obj
    while parent is not None:
        if parent in crew_roots:
            keep.add(obj)
            break
        parent = parent.parent
# Include the compact rover and lander assets at the site; the full 3D scene
# retains every object, while this preview concentrates on the terrain work.
for obj in scene.objects:
    if obj.type == "MESH" and obj != site:
        center = obj.matrix_world.translation
        modest_size = max(float(v) for v in obj.dimensions) < 100.0
        if modest_size and ((10.0 <= center.x <= 18.0 and 8.0 <= center.y <= 16.0) or obj.name == "MSL"):
            keep.add(obj)
hidden = []
for obj in scene.objects:
    if obj not in keep:
        hidden.append((obj, obj.hide_render))
        obj.hide_render = True
print(f"Preview-only focus: {len(keep)} of {len(scene.objects)} objects remain visible")
bpy.ops.render.render(write_still=True, scene=scene.name)
for obj, was_hidden in hidden:
    obj.hide_render = was_hidden
print("Rendered preview only; temporary camera and render settings were not saved.")
