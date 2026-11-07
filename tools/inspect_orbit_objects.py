"""Find the globe, its camera, and anything that looks like a satellite."""
import bpy

needles = ("sat", "orbit", "craft", "mro", "probe", "ship", "station", "globe", "planet")
for obj in bpy.data.objects:
    name = obj.name.lower()
    if any(word in name for word in needles):
        loc = obj.matrix_world.translation
        dims = obj.dimensions
        print(
            obj.name, obj.type,
            [round(float(v), 1) for v in loc],
            "dim", [round(float(v), 1) for v in dims],
            "parent", obj.parent.name if obj.parent else None,
        )
