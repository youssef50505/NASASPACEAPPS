"""Ground the visible crew on measured HiRISE elevations and style the DTM.

Creates a new native file from the already-integrated site file. The source
blend, integrated checkpoint, existing materials and all scene objects remain.
Only the six named crew roots receive a measured vertical placement update.
"""
from __future__ import annotations

import array
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
INPUT_BLEND = ROOT / "MARS_SENTINEL_NASA_Terrain_Study_HIRISE_SITE.blend"
OUTPUT_BLEND = ROOT / "MARS_SENTINEL_NASA_Terrain_Study_HIRISE_READY.blend"
GRID_JSON = ROOT / "data" / "jez_hirise_site_detail_4m.json"
SITE_NAME = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"
CREW_ROOTS = ["Sketchfab_model.007", "ludovisions_FC1_rig", "Sketchfab_model.015",
              "Sketchfab_model", "Joe_Astronaut", "Sketchfab_model.003"]
COLOR_ATTRIBUTE = "HiRISE_Elevation_Tint"
MATERIAL_NAME = "Mars_HiRISE_Elevation_Visual"


def palette(t: float) -> tuple[float, float, float, float]:
    """Muted Mars palette, driven only by source DTM elevation."""
    stops = [
        (0.00, (0.30, 0.075, 0.032)),
        (0.34, (0.45, 0.13, 0.052)),
        (0.67, (0.64, 0.25, 0.10)),
        (1.00, (0.78, 0.41, 0.19)),
    ]
    for i in range(len(stops) - 1):
        a, ca = stops[i]
        b, cb = stops[i + 1]
        if t <= b:
            f = max(0.0, min(1.0, (t - a) / (b - a)))
            return tuple(ca[j] * (1 - f) + cb[j] * f for j in range(3)) + (1.0,)
    return (*stops[-1][1], 1.0)


def create_elevation_material(mesh: bpy.types.Mesh, elevations: list[float]) -> None:
    lo, hi = min(elevations), max(elevations)
    attr = mesh.color_attributes.get(COLOR_ATTRIBUTE)
    if attr is None:
        attr = mesh.color_attributes.new(name=COLOR_ATTRIBUTE, type="FLOAT_COLOR", domain="POINT")
    colors = array.array("f")
    span = hi - lo
    for z in elevations:
        colors.extend(palette((z - lo) / span if span else 0.5))
    attr.data.foreach_set("color", colors)

    mat = bpy.data.materials.new(MATERIAL_NAME)
    mat.diffuse_color = (0.55, 0.18, 0.07, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (500, 0)
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.location = (220, 0)
    shader.inputs["Roughness"].default_value = 0.92
    color = nodes.new("ShaderNodeVertexColor")
    color.layer_name = COLOR_ATTRIBUTE
    color.location = (-80, 20)
    mat.node_tree.links.new(color.outputs["Color"], shader.inputs["Base Color"])
    mat.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    mesh.materials.clear()
    mesh.materials.append(mat)


def sample_surface_z(grid: dict, x: float, y: float, site: bpy.types.Object) -> float:
    # Site mesh XY is centered on the AOI and oriented north-up in local XY.
    spacing = float(grid["mesh_sample_spacing_m"])
    h, w = int(grid["grid_height"]), int(grid["grid_width"])
    x0 = -((w - 1) * spacing) / 2
    y0 = ((h - 1) * spacing) / 2
    col = max(0, min(w - 1, round((x - site.location.x - x0) / spacing)))
    row = max(0, min(h - 1, round((y0 - (y - site.location.y)) / spacing)))
    local_z = float(grid["elevations_m"][row][col]) - float(grid["center_reference_elevation_m"])
    return float(site.location.z) + local_z


def descendants(root_obj: bpy.types.Object):
    for obj in bpy.context.scene.objects:
        parent = obj
        while parent is not None and parent != root_obj:
            parent = parent.parent
        if parent == root_obj and obj.type == "MESH" and not obj.hide_render:
            yield obj


def top_root(obj: bpy.types.Object) -> bpy.types.Object:
    while obj.parent is not None:
        obj = obj.parent
    return obj


def main() -> None:
    if bpy.data.filepath != str(INPUT_BLEND):
        raise RuntimeError(f"Open the HiRISE checkpoint first: {INPUT_BLEND}")
    scene = bpy.data.scenes.get("Scene")
    site = bpy.data.objects.get(SITE_NAME)
    if scene is None or site is None:
        raise RuntimeError("Integrated scene or HiRISE DTM mesh is missing")
    grid = json.loads(GRID_JSON.read_text(encoding="utf-8"))
    mesh = site.data
    # The mesh's local Z values are the exact measured elevations minus one
    # constant reference; the generated 80 m skirt blends to the underlay.
    elevations = [float(vertex.co.z) for vertex in mesh.vertices]
    create_elevation_material(mesh, elevations)

    placements = []
    for name in CREW_ROOTS:
        root_obj = bpy.data.objects.get(name)
        if root_obj is None:
            raise RuntimeError(f"Expected crew root not found: {name}")
        points = []
        for child_mesh in descendants(root_obj):
            points.extend(child_mesh.matrix_world @ Vector(c) for c in child_mesh.bound_box)
        if not points:
            raise RuntimeError(f"No visible crew meshes found under: {name}")
        sample_z = sample_surface_z(grid, float(root_obj.matrix_world.translation.x),
                                    float(root_obj.matrix_world.translation.y), site)
        old_min = min(float(p.z) for p in points)
        delta = sample_z - old_min
        root_obj.location.z += delta
        placements.append({"root": name, "surface_z_m": round(sample_z, 4),
                           "old_foot_z_m": round(old_min, 4), "applied_root_delta_m": round(delta, 4)})

    # The imported rover is composed of several top-level mesh assemblies.
    # Move each assembly by one shared terrain offset so internal joints stay
    # together, using the complete rover footprint and its lowest wheel point.
    rover_meshes = []
    for obj in scene.objects:
        if obj.type != "MESH" or obj.hide_render or obj == site:
            continue
        center = obj.matrix_world.translation
        if 10.0 <= center.x <= 18.0 and 8.0 <= center.y <= 16.0:
            rover_meshes.append(obj)
    rover_roots = sorted({top_root(obj) for obj in rover_meshes}, key=lambda o: o.name)
    rover_points = []
    for root_obj in rover_roots:
        for child_mesh in descendants(root_obj):
            center = child_mesh.matrix_world.translation
            if 10.0 <= center.x <= 18.0 and 8.0 <= center.y <= 16.0:
                rover_points.extend(child_mesh.matrix_world @ Vector(c) for c in child_mesh.bound_box)
    if rover_roots and rover_points:
        min_x = sum(float(p.x) for p in rover_points) / len(rover_points)
        min_y = sum(float(p.y) for p in rover_points) / len(rover_points)
        sample_z = sample_surface_z(grid, min_x, min_y, site)
        old_min = min(float(p.z) for p in rover_points)
        delta = sample_z - old_min
        for root_obj in rover_roots:
            root_obj.location.z += delta
        placements.append({"root_group": "Jezero rover assembly", "surface_z_m": round(sample_z, 4),
                           "old_wheel_z_m": round(old_min, 4), "applied_shared_delta_m": round(delta, 4),
                           "root_count": len(rover_roots)})

    # A separately imported lander/rover mesh sits beside the crew at x≈1 m.
    msl = bpy.data.objects.get("MSL")
    if msl is not None and msl.type == "MESH":
        points = [msl.matrix_world @ Vector(c) for c in msl.bound_box]
        sample_z = sample_surface_z(grid, float(msl.matrix_world.translation.x),
                                    float(msl.matrix_world.translation.y), site)
        old_min = min(float(p.z) for p in points)
        delta = sample_z - old_min
        msl.location.z += delta
        placements.append({"root": "MSL", "surface_z_m": round(sample_z, 4),
                           "old_foot_z_m": round(old_min, 4), "applied_root_delta_m": round(delta, 4)})

    site["elevation_color_attribute"] = COLOR_ATTRIBUTE
    site["elevation_colorization_note"] = "Visual rust/ochre tint mapped to measured HiRISE DTM height; elevation geometry and vertical scale unchanged"
    scene["crew_grounding_method"] = "Six named astronaut roots vertically positioned to nearest 4 m HiRISE DTM sample"
    scene["crew_grounding_records"] = json.dumps(placements)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    print("OUTPUT", OUTPUT_BLEND)
    print("SITE_MESH", len(mesh.vertices), "vertices", len(mesh.polygons), "faces", "MATERIAL", MATERIAL_NAME)
    print("CREW_PLACEMENTS", json.dumps(placements))


if __name__ == "__main__":
    main()
