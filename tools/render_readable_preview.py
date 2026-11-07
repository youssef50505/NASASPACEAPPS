"""Render the opening surface camera and a wider view of the three routes."""
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
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

keep_names = {
    "NASA_HiRISE_DTM_Jezero_FieldSite_4m",
    "MS_Surface_Opening_Camera",
    "MS_Route_Shortest_HiRISE",
    "MS_Route_Safest_HiRISE",
    "MS_Route_Science_HiRISE",
    "MS_Science_Octavia_E_Butler_Landing",
    "MS_Science_Wright_Brothers_Field",
    "MS_Science_Rochette",
    "White_Circle_Marker",
    "White_Ring",
}
keep_roots = {
    "Sketchfab_model.007",
    "Sketchfab_model.015",
    "Sketchfab_model",
    "Joe_Astronaut",
    "Sketchfab_model.003",
    "MSL",
    "Wheels_objs",
}
keep = set(keep_names)
for name in keep_roots:
    root = bpy.data.objects.get(name)
    if root is None:
        continue
    keep.add(root.name)
    keep.update(child.name for child in root.children_recursive)

hidden = []
for obj in scene.objects:
    hidden.append((obj, obj.hide_render))
    obj.hide_render = obj.name not in keep

opening = bpy.data.objects["MS_Surface_Opening_Camera"]
scene.camera = opening
scene.render.filepath = str(ROOT / "previews" / "surface_opening_preview.png")
bpy.ops.render.render(write_still=True, scene=scene.name)
print("RENDERED", scene.render.filepath)

overview = bpy.data.objects.new("TEMP_Route_Overview", bpy.data.cameras.new("TEMP_Route_Overview"))
scene.collection.objects.link(overview)
site = bpy.data.objects["NASA_HiRISE_DTM_Jezero_FieldSite_4m"]
overview.location = site.matrix_world.translation + Vector((180.0, -700.0, 900.0))
overview.rotation_euler = (site.matrix_world.translation + Vector((220.0, 280.0, 0.0)) - overview.location).to_track_quat("-Z", "Y").to_euler()
overview.data.lens = 28
overview.data.clip_end = 20000
scene.camera = overview
scene.render.filepath = str(ROOT / "previews" / "route_separation_preview.png")
bpy.ops.render.render(write_still=True, scene=scene.name)
print("RENDERED", scene.render.filepath)
for obj, was_hidden in hidden:
    obj.hide_render = was_hidden
