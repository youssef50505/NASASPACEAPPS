"""Read-only center-ray diagnostic for the original surface camera."""
import bpy
from mathutils import Vector

scene = bpy.context.scene
camera = bpy.data.objects["Mars_Camera"]
depsgraph = bpy.context.evaluated_depsgraph_get()
origin = camera.matrix_world.translation
direction = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
hit, location, normal, face_index, obj, matrix = scene.ray_cast(depsgraph, origin, direction)
print("CAMERA", camera.name, "origin", tuple(round(float(v), 3) for v in origin))
print("RAY", "hit", hit, "object", obj.name if obj else None,
      "location", tuple(round(float(v), 3) for v in location),
      "distance", round(float((location-origin).length), 3))
if obj:
    print("TYPE", obj.type, "dimensions", tuple(round(float(v), 3) for v in obj.dimensions),
          "collections", [c.name for c in obj.users_collection],
          "materials", [m.name for m in getattr(obj.data, "materials", []) if m])
