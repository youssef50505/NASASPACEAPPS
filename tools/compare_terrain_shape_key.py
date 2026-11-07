"""Read-only in-memory check of the flat versus terrain shape key bounds."""
import bpy

obj = bpy.data.objects["Mars_Terrain"]
keys = obj.data.shape_keys.key_blocks
flat = keys.get("Flat_Ground")
if flat is None:
    raise RuntimeError("Mars_Terrain has no Flat_Ground key")

def bounds(label):
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    corners = [evaluated.matrix_world @ __import__("mathutils").Vector(corner) for corner in evaluated.bound_box]
    low = [min(p[i] for p in corners) for i in range(3)]
    high = [max(p[i] for p in corners) for i in range(3)]
    print(f"{label}: z_min={low[2]:.4f} z_max={high[2]:.4f} z_span={high[2]-low[2]:.4f} Flat_Ground={flat.value:.1f}")

bounds("saved_state")
flat.value = 0.0
bounds("Flat_Ground_off_in_memory_only")
