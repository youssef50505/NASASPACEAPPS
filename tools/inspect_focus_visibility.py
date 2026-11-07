"""Count hidden meshes under the crew and the rover."""
import bpy

scene = bpy.context.scene
scene.frame_set(1)
for name in ("MSL", "Wheels_objs", "Joe_Astronaut", "Sketchfab_model.003", "Sketchfab_model", "Sketchfab_model.007", "Sketchfab_model.015"):
    root = bpy.data.objects.get(name)
    if root is None:
        print("MISSING", name)
        continue
    meshes = [obj for obj in [root, *root.children_recursive] if obj.type == "MESH"]
    shown = [obj for obj in meshes if not obj.hide_render and not obj.hide_viewport]
    print(name, "meshes", len(meshes), "shown", len(shown), "root_hide", root.hide_render, root.hide_viewport)
