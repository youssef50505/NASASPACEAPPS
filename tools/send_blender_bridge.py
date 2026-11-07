import json
import socket

code = r'''
import math
import bpy
from mathutils import Vector

scene = bpy.context.scene
root = bpy.data.objects["Sketchfab_model.002"]
terrain = bpy.data.objects["NASA_HiRISE_DTM_Jezero_FieldSite_4m"]
inverse = terrain.matrix_world.inverted()

def terrain_z(x, y, above):
    start = inverse @ Vector((x, y, above))
    hit, location, normal, index = terrain.ray_cast(start, inverse.to_3x3() @ Vector((0.0, 0.0, -1.0)), distance=200.0)
    if not hit:
        return None
    return (terrain.matrix_world @ location).z

points = []
for obj in root.children_recursive:
    if obj.type != "MESH":
        continue
    points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
lowest = min(points, key=lambda point: point.z)
ground = terrain_z(lowest.x, lowest.y, lowest.z + 40.0)
if ground is None:
    raise RuntimeError("terrain missed under the base")
gap = lowest.z - ground
root.location.z -= gap
bpy.context.view_layer.update()
print("GAP_FIXED", round(gap, 3))

collection = bpy.data.collections.get("MS_Illustrative_Rocks")
if collection is None:
    collection = bpy.data.collections.new("MS_Illustrative_Rocks")
    scene.collection.children.link(collection)
for obj in list(collection.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

center = root.matrix_world.translation
made = 0
for index in range(8):
    angle = index * 0.8 + 0.4
    radius = 7.0 + (index % 4) * 1.7
    x = center.x + math.cos(angle) * radius
    y = center.y + math.sin(angle) * radius
    height = terrain_z(x, y, center.z + 30.0)
    if height is None:
        continue
    name = f"MS_Illustrative_Rock_{index + 1:02d}"
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.55, location=(x, y, height + 2.0))
    rock = bpy.context.active_object
    rock.name = name
    for vertex in rock.data.vertices:
        nudge = 0.16 * math.sin((vertex.co.x + index) * 8.0) + 0.1 * math.cos(vertex.co.y * 11.0 + index)
        vertex.co *= 1.0 + nudge
        vertex.co.z *= 0.62
    rock.scale = (1.1 + (index % 3) * 0.25, 0.9, 0.75)
    rock.rotation_euler = (0.15, 0.1, angle)
    bpy.context.view_layer.update()
    bottom = min((rock.matrix_world @ vertex.co).z for vertex in rock.data.vertices)
    rock.location.z += height - bottom + 0.02
    material = bpy.data.materials.get("MS_Illustrative_Rock")
    if material and material.name not in rock.data.materials:
        rock.data.materials.append(material)
    for poly in rock.data.polygons:
        poly.use_smooth = True
    rock["illustrative"] = "Placed rock prop. Not a NASA measurement."
    for user in list(rock.users_collection):
        user.objects.unlink(rock)
    collection.objects.link(rock)
    made += 1

eevee = scene.eevee
if hasattr(eevee, "taa_samples"):
    eevee.taa_samples = 32
if hasattr(eevee, "taa_render_samples"):
    eevee.taa_render_samples = 64
bpy.context.view_layer.objects.active = root
target = root.matrix_world.translation + Vector((0.0, 0.0, 1.6))
eye = Vector((0.85, -1.15, 0.42)).normalized()
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type != "VIEW_3D":
            continue
        space = area.spaces.active
        space.shading.type = "MATERIAL"
        space.lens = 50.0
        region = space.region_3d
        region.view_perspective = "PERSP"
        region.view_location = target
        region.view_distance = 26.0
        region.view_rotation = eye.to_track_quat("Z", "Y")
        space.clip_start = 0.05
        space.clip_end = 400.0
print("ROCKS", made, "ROOT_Z", round(root.location.z, 3))
'''
message = json.dumps({"type": "execute_code", "params": {"code": code}}) + "\n"
with socket.create_connection(("127.0.0.1", 9875), timeout=90) as sock:
    sock.sendall(message.encode("utf-8"))
    data = b""
    while b"\n" not in data:
        chunk = sock.recv(65536)
        if not chunk:
            break
        data += chunk
print(data.decode("utf-8", errors="replace")[:2500])
