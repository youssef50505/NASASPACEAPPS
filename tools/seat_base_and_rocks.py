"""Seat the low-poly base on the terrain and add a few illustrative rocks."""
import math
import bpy
from mathutils import Vector

scene = bpy.context.scene
scene.frame_set(76)
root = bpy.data.objects["Sketchfab_model.002"]
terrain = bpy.data.objects["NASA_HiRISE_DTM_Jezero_FieldSite_4m"]
depsgraph = bpy.context.evaluated_depsgraph_get()


def ground_z(x, y, start_z):
    origin = Vector((x, y, start_z + 40.0))
    hit, location, _normal, _index, obj, _matrix = scene.ray_cast(
        depsgraph, origin, Vector((0.0, 0.0, -1.0)), distance=120.0
    )
    if hit and obj == terrain:
        return location.z
    return None


samples = []
for obj in root.children_recursive:
    if obj.type != "MESH":
        continue
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    samples.append(min(corners, key=lambda point: point.z))
gaps = []
for point in samples:
    height = ground_z(point.x, point.y, point.z)
    if height is not None:
        gaps.append(point.z - height)
if not gaps:
    raise RuntimeError("no ground under the base")
drop = min(gaps)
root.location.z -= drop
bpy.context.view_layer.update()
print("DROPPED", round(drop, 3))

for obj in root.children_recursive:
    if obj.type != "MESH":
        continue
    for poly in obj.data.polygons:
        poly.use_smooth = True

collection = bpy.data.collections.get("MS_Illustrative_Rocks")
if collection is None:
    collection = bpy.data.collections.new("MS_Illustrative_Rocks")
    scene.collection.children.link(collection)
material = bpy.data.materials.get("MS_Illustrative_Rock")
if material is None:
    material = bpy.data.materials.new("MS_Illustrative_Rock")
    material.use_nodes = True
    shader = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = (0.42, 0.22, 0.15, 1.0)
    shader.inputs["Roughness"].default_value = 0.9

center = root.matrix_world.translation
for index in range(8):
    name = f"MS_Illustrative_Rock_{index + 1:02d}"
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    angle = index * 0.78 + 0.3
    radius = 8.0 + (index % 3) * 1.8
    x = center.x + math.cos(angle) * radius
    y = center.y + math.sin(angle) * radius
    height = ground_z(x, y, center.z + 5.0)
    if height is None:
        continue
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=0.4 + (index % 3) * 0.2,
        location=(x, y, height + 1.0),
    )
    rock = bpy.context.active_object
    rock.name = name
    rock.scale = (1.15, 0.8, 0.55)
    bpy.context.view_layer.update()
    bottom = min((rock.matrix_world @ Vector(corner)).z for corner in rock.bound_box)
    rock.location.z += height - bottom
    rock.data.materials.append(material)
    for poly in rock.data.polygons:
        poly.use_smooth = True
    rock["illustrative"] = "Placed rock prop. Not a NASA measurement."
    for user in list(rock.users_collection):
        user.objects.unlink(rock)
    collection.objects.link(rock)

eevee = scene.eevee
if hasattr(eevee, "taa_samples"):
    eevee.taa_samples = 32
if hasattr(eevee, "taa_render_samples"):
    eevee.taa_render_samples = 64
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type != "VIEW_3D":
            continue
        space = area.spaces.active
        space.shading.type = "MATERIAL"
        region = space.region_3d
        region.view_perspective = "PERSP"
        region.view_location = root.matrix_world.translation
        region.view_distance = 16.0
        region.view_rotation = Vector((0.55, -0.95, 0.25)).to_track_quat("-Z", "Y")
        space.clip_start = 0.05
        space.clip_end = 400.0
print("ROCKS", len(collection.objects))
