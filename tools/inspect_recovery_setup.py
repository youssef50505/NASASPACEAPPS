"""Read-only scene/world/startup viewport diagnostics."""
import bpy

scene = bpy.context.scene
world = scene.world
print("ACTIVE_SCENE", scene.name, "CAMERA", scene.camera.name if scene.camera else None)
print("WORLD", world.name if world else None, "USE_NODES", world.use_nodes if world else None)
if world and world.node_tree:
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    for n in nodes:
        print("WORLD_NODE", n.name, n.bl_idname, "inputs", [(s.name, tuple(s.default_value) if hasattr(s.default_value, "__len__") else s.default_value) for s in n.inputs if hasattr(s, "default_value")])
    for l in links:
        print("WORLD_LINK", l.from_node.name, l.from_socket.name, "->", l.to_node.name, l.to_socket.name)
for s in bpy.data.screens:
    for a in s.areas:
        if a.type == "VIEW_3D":
            sp = a.spaces.active
            rv = sp.region_3d
            print("VIEW", s.name, "perspective", rv.view_perspective, "view_distance", round(rv.view_distance, 2), "shading", sp.shading.type, sp.shading.color_type, "world", sp.shading.use_scene_world)
        elif a.type == "OUTLINER":
            sp = a.spaces.active
            print("OUTLINER", s.name, "filter_text", getattr(sp, "filter_text", "<unavailable>"))
