"""Create a recovery copy from the untouched pre-quality-pass Blender project.

No embedded Text datablock is executed. Existing meshes, transforms, animation,
materials, worlds, scripts, and shape-key values are preserved. The new
collection is an organizational view that links existing objects; it does not
duplicate or move them.
"""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCENE = "Scene"
OUTPUT = ROOT / "MARS_SENTINEL_NASA_Terrain_Study.blend"

scene = bpy.data.scenes.get(EXPECTED_SCENE)
if scene is None:
    raise RuntimeError(f"Expected original scene {EXPECTED_SCENE!r} was not found")

# Restore the original integrated scene as the active scene and preserve its
# original camera and frame. The backup had one scene and this exact camera.
if scene.camera is None or scene.camera.name != "Mars_Orbit_View_Camera":
    raise RuntimeError("Original scene camera does not match the audited backup")
if len(bpy.data.scenes) != 1:
    raise RuntimeError(f"Expected one source scene, found {len(bpy.data.scenes)}")
globe_camera = bpy.data.objects.get("MARS_NEW_Globe_Camera")
if globe_camera is None or globe_camera.type != "CAMERA":
    raise RuntimeError("Original MARS_NEW_Globe_Camera is missing")

# Give the connected Jezero work one easy-to-find Outliner entry. These are
# links to the existing objects, not copies; original collections stay intact.
site_collection_name = "FIELD SITE | Jezero (linked original assets)"
site_collection = bpy.data.collections.get(site_collection_name)
if site_collection is None:
    site_collection = bpy.data.collections.new(site_collection_name)
    scene.collection.children.link(site_collection)

linked_names = [
    "Mars_Terrain",
    "White_Circle_Marker",
    "White_Ring",
    "Joe_Astronaut",
    "Joe_JA",
    "ludovisions_FC1_rig",
    "Mars_Camera",
    "MARS_NEW_Globe_Camera",
    "MARS_NEW_Explore_Area_Pin",
    "MARS_NEW_Explore_Area_Ring",
]
missing = []
for object_name in linked_names:
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        missing.append(object_name)
        continue
    if obj.name not in site_collection.objects:
        site_collection.objects.link(obj)
if missing:
    raise RuntimeError("Missing expected original assets: " + ", ".join(missing))

# Cross-reference the local NASA terrain patch to its geographic source and
# the globe's existing exploration marker, without changing either transform.
terrain = bpy.data.objects["Mars_Terrain"]
terrain["mars_site_latitude_deg"] = 18.42875
terrain["mars_site_longitude_east_deg"] = 77.44215
terrain["mars_site_data_relationship"] = (
    "Jezero local HiRISE DTM patch; geographic location corresponds to the "
    "MARS_NEW_Explore_Area_Pin/Ring controls on the global Mars scene. "
    "Original local/world transforms intentionally preserved."
)
scene["mars_sentinel_recovery"] = (
    "Recovered from Mars_backup_before_quality_pass.blend. "
    "Original integrated Scene restored as the active scene; geometry and "
    "animation preserved."
)
scene["mars_sentinel_primary_scene"] = EXPECTED_SCENE
scene["mars_sentinel_site_collection"] = site_collection_name
scene["mars_sentinel_startup_view"] = (
    "Global Mars camera in the Layout workspace; the original local, orbit, "
    "astronaut and dashboard cameras remain available."
)

# Make the file open on the actual planet rather than the user's previous
# arbitrary viewport orbit. Keep all original cameras and animations.
scene.camera = globe_camera
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            if screen.name == "Layout":
                space.region_3d.view_perspective = "CAMERA"
                space.region_3d.view_camera_zoom = 0.0
                space.shading.type = "MATERIAL"
                space.shading.use_scene_world = True
                space.shading.use_scene_lights = True
        elif area.type == "OUTLINER":
            space = area.spaces.active
            if hasattr(space, "filter_text"):
                space.filter_text = ""

# Do not execute, remove, or modify embedded Python Text datablocks. Blender
# security preferences remain the user's choice.
if bpy.context.window is not None:
    bpy.context.window.scene = scene
# The previous version was copied to archive/ before this write. Do not leave
# an ambiguous adjacent .blend1 that could be mistaken for the canonical file.
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
print(f"WORKING_FILE={OUTPUT}")
print(f"ACTIVE_SCENE={scene.name}; SCENES={len(bpy.data.scenes)}; OBJECTS={len(scene.objects)}")
print(f"SITE_COLLECTION_OBJECTS={len(site_collection.objects)}; FRAME={scene.frame_current}; CAMERA={scene.camera.name}")
