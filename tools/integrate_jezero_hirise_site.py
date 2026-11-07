"""Add a real 4 m sampled HiRISE surface patch to the integrated Blender scene.

This is append-only at the scene-object level: it adds a new DTM mesh and does
not delete or replace existing objects. The existing flat Mars_Terrain base is
lowered beneath the measured mesh plus a short edge skirt so it remains as a
background outside HiRISE coverage. The source .blend is never overwritten.
"""
from __future__ import annotations

import array
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
INPUT_BLEND = ROOT / "MARS_SENTINEL_NASA_Terrain_Study.blend"
OUTPUT_BLEND = ROOT / "MARS_SENTINEL_NASA_Terrain_Study_HIRISE_SITE.blend"
GRID_JSON = ROOT / "data" / "jez_hirise_site_detail_4m.json"
OBJECT_NAME = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"
SITE_COLLECTION_NAME = "FIELD SITE | Jezero (linked original assets)"
SKIRT_M = 80.0
BASE_DEPTH_M = 55.0


def build_site_mesh(grid: dict, terrain: bpy.types.Object) -> bpy.types.Mesh:
    h = int(grid["grid_height"])
    w = int(grid["grid_width"])
    spacing = float(grid["mesh_sample_spacing_m"])
    if h != 1024 or w != 1024 or spacing != 4.0:
        raise RuntimeError(f"Unexpected site grid shape/spacing: {w}x{h}, {spacing}m")
    elevations = grid["elevations_m"]
    mask = grid["valid_mask"]
    if any(not bool(valid) for row in mask for valid in row):
        raise RuntimeError("This site mesh builder expects a fully valid core DTM window")

    skirt_steps = round(SKIRT_M / spacing)
    rows = h + 2 * skirt_steps
    cols = w + 2 * skirt_steps
    z_reference = float(grid["center_reference_elevation_m"])
    base_z = -BASE_DEPTH_M
    half_x = (w - 1) * spacing / 2.0
    half_y = (h - 1) * spacing / 2.0

    vertices = []
    for rr in range(rows):
        src_r = rr - skirt_steps
        clamped_r = min(max(src_r, 0), h - 1)
        for cc in range(cols):
            src_c = cc - skirt_steps
            clamped_c = min(max(src_c, 0), w - 1)
            edge_z = float(elevations[clamped_r][clamped_c]) - z_reference
            distance = max(
                0,
                -src_r,
                src_r - (h - 1),
                -src_c,
                src_c - (w - 1),
            )
            if distance:
                t = min(distance / skirt_steps, 1.0)
                t = t * t * (3.0 - 2.0 * t)
                z = edge_z * (1.0 - t) + base_z * t
            else:
                z = edge_z
            x = src_c * spacing - half_x
            y = half_y - src_r * spacing
            vertices.append((x, y, z))

    faces = []
    for rr in range(rows - 1):
        row_start = rr * cols
        next_row = row_start + cols
        for cc in range(cols - 1):
            a = row_start + cc
            b = next_row + cc
            # CCW when viewed from above; this keeps normals facing +Z.
            faces.append((a, b, b + 1, a + 1))

    mesh = bpy.data.meshes.new(OBJECT_NAME + " | 4 m source grid")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)

    uv_layer = mesh.uv_layers.new(name="UVMap")
    uv_values = array.array("f")
    loop_vertex_indices = [0] * len(mesh.loops)
    mesh.loops.foreach_get("vertex_index", loop_vertex_indices)
    for vertex_index in loop_vertex_indices:
        rr, cc = divmod(vertex_index, cols)
        src_r = rr - skirt_steps
        src_c = cc - skirt_steps
        u = min(max(src_c / (w - 1), 0.0), 1.0)
        v = 1.0 - min(max(src_r / (h - 1), 0.0), 1.0)
        uv_values.extend((u, v))
    uv_layer.data.foreach_set("uv", uv_values)

    smooth_flags = array.array("b", [1]) * len(mesh.polygons)
    mesh.polygons.foreach_set("use_smooth", smooth_flags)
    mesh.update()
    return mesh


def main() -> None:
    if bpy.data.filepath != str(INPUT_BLEND):
        raise RuntimeError(f"Open the canonical integrated file first: {INPUT_BLEND}")
    if bpy.data.objects.get(OBJECT_NAME):
        raise RuntimeError(f"{OBJECT_NAME} already exists; no objects will be deleted or replaced")
    scene = bpy.data.scenes.get("Scene")
    terrain = bpy.data.objects.get("Mars_Terrain")
    if scene is None or terrain is None:
        raise RuntimeError("Integrated Scene/Mars_Terrain not found")
    collection = bpy.data.collections.get(SITE_COLLECTION_NAME)
    if collection is None:
        raise RuntimeError(f"Field-site collection not found: {SITE_COLLECTION_NAME}")

    grid = json.loads(GRID_JSON.read_text(encoding="utf-8"))
    mesh = build_site_mesh(grid, terrain)
    site_obj = bpy.data.objects.new(OBJECT_NAME, mesh)
    collection.objects.link(site_obj)

    # Place the measured core on the old flat surface at the exact recorded site
    # center. The flat source surface remains intact, 55 m beneath it.
    bbox_world = [terrain.matrix_world @ __import__("mathutils").Vector(v) for v in terrain.bound_box]
    surface_z = sum(float(v.z) for v in bbox_world) / len(bbox_world)
    site_obj.location = (float(terrain.location.x), float(terrain.location.y), surface_z)
    site_obj.rotation_euler = (0.0, 0.0, 0.0)
    site_obj.scale = (1.0, 1.0, 1.0)

    existing_materials = [m for m in terrain.data.materials if m]
    preferred_material = next((m for m in existing_materials if m.name == "Mars_Terrain_Rust"), None)
    if preferred_material is None and existing_materials:
        preferred_material = existing_materials[0]
    if preferred_material is not None:
        mesh.materials.append(preferred_material)
        print("REUSED_MATERIAL", preferred_material.name)
    else:
        raise RuntimeError("No existing Mars surface material found; refusing to invent a color source")

    # Lower, but retain, the old flat terrain as a surrounding substrate.
    original_base_z = float(terrain.location.z)
    terrain.location.z -= BASE_DEPTH_M
    terrain["underlay_offset_for_hirise_site_m"] = -BASE_DEPTH_M
    terrain["underlay_role"] = "Existing flat visual base retained below the new measured HiRISE site mesh"

    site_obj["data_product"] = grid["product"]
    site_obj["data_source_url"] = grid["source_url"]
    site_obj["data_landing_page"] = grid["landing_page"]
    site_obj["data_doi"] = grid["doi"]
    site_obj["site_latitude_north_deg"] = float(grid["site_center_latitude_north_deg"])
    site_obj["site_longitude_east_deg"] = float(grid["site_center_longitude_east_deg"])
    site_obj["native_source_resolution_m_per_pixel"] = float(grid["native_resolution_m_per_pixel"])
    site_obj["mesh_sample_spacing_m"] = spacing = float(grid["mesh_sample_spacing_m"])
    site_obj["vertical_exaggeration"] = float(grid["vertical_exaggeration"])
    site_obj["reference_elevation_m"] = float(grid["center_reference_elevation_m"])
    site_obj["elevation_min_m"] = float(grid["elevation_min_m"])
    site_obj["elevation_max_m"] = float(grid["elevation_max_m"])
    site_obj["core_width_m"] = float(grid["width_m"])
    site_obj["core_height_m"] = float(grid["height_m"])
    site_obj["edge_skirt_width_m"] = SKIRT_M
    site_obj["edge_skirt_is_visual_transition"] = True
    site_obj["nodata_samples"] = int(grid["nodata_samples"])
    scene["hirise_site_mesh_added"] = OBJECT_NAME
    scene["hirise_site_mesh_source_doi"] = grid["doi"]
    scene["hirise_site_flat_base_offset_m"] = -BASE_DEPTH_M

    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    print(f"OUTPUT={OUTPUT_BLEND}")
    print(f"SCENES={len(bpy.data.scenes)} OBJECTS={len(scene.objects)} CAMERA={scene.camera.name if scene.camera else None}")
    print(f"NEW_MESH_VERTICES={len(mesh.vertices)} NEW_MESH_FACES={len(mesh.polygons)}")
    print(f"CORE={grid['width_m']}x{grid['height_m']}m SPACING={spacing}m REFERENCE={grid['center_reference_elevation_m']:.3f}m")
    print(f"BASE_Z_OLD_LOCAL={original_base_z:.3f} NEW_LOCAL={terrain.location.z:.3f} SITE_SURFACE_Z={surface_z:.3f}")


if __name__ == "__main__":
    main()
