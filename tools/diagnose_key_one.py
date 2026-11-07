"""See why the 1 key cannot frame the crew."""
import bpy

ROOTS = [
    "Sketchfab_model.007", "ludovisions_FC1_rig", "Sketchfab_model.015",
    "Sketchfab_model", "Joe_Astronaut", "Sketchfab_model.003",
]
scene = bpy.context.scene
print("FILE", bpy.data.filepath)
print("VIEW_LAYERS", [vl.name for vl in scene.view_layers])
vl = scene.view_layers[0]
names = {obj.name for obj in vl.objects}
for name in ROOTS:
    root = bpy.data.objects.get(name)
    if root is None:
        print("MISSING", name)
        continue
    meshes = []
    for obj in [root] + list(root.children_recursive):
        if obj.type != "MESH":
            continue
        meshes.append(
            f"{obj.name}|in_vl={obj.name in names}|hide_v={obj.hide_viewport}|hide_r={obj.hide_render}|excluded_cols={sum(1 for c in obj.users_collection if c.name not in {x.name for x in vl.layer_collection.children})}"
        )
    print(f"ROOT {name} type={root.type} children={len(root.children_recursive)} meshes={len([o for o in [root]+list(root.children_recursive) if o.type=='MESH'])} in_vl={name in names}")
    for line in meshes[:8]:
        print(" ", line)

def walk(layer_col, prefix=""):
    print(f"{prefix}{layer_col.name} exclude={layer_col.exclude} hide={layer_col.hide_viewport}")
    for child in layer_col.children:
        walk(child, prefix + "  ")

walk(vl.layer_collection)
text = bpy.data.texts.get("front_view_models.py")
print("TEXT_PRESENT", text is not None, "use_module", getattr(text, "use_module", None))
