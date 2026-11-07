"""Name the collection that holds the objects orbiting the globe."""
import bpy

targets = ["Object_9.002", "Object_167", "Object_40.001"]
for name in targets:
    obj = bpy.data.objects.get(name)
    if obj is None:
        print("MISSING", name)
        continue
    parent = obj
    chain = []
    while parent is not None:
        chain.append(parent.name)
        parent = parent.parent
    users = [col.name for col in obj.users_collection]
    print(name, "CHAIN", " > ".join(chain), "COLS", users)

for col in bpy.data.collections:
    low = col.name.lower()
    if any(word in low for word in ("sat", "orbit", "station", "space", "craft", "globe")):
        print("COL", col.name, "objects", len(col.objects))
