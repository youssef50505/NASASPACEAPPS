"""Name the parent chain of the rigs that already have actions."""
import bpy

for obj in bpy.data.objects:
    if obj.type != "ARMATURE":
        continue
    chain = [obj.name]
    parent = obj.parent
    while parent is not None and len(chain) < 6:
        chain.append(parent.name)
        parent = parent.parent
    action = None if obj.animation_data is None or obj.animation_data.action is None else obj.animation_data.action.name
    print(" -> ".join(chain), "|", action)
