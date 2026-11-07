"""Create a non-destructive Blender study with real Jezero terrain and a starfield."""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
BLEND_SOURCE = ROOT / "Mars_backup_before_quality_pass.blend"
GRID_JSON = ROOT / "data" / "jez_ctx_20m_grid.json"
BLEND_OUTPUT = ROOT / "archive" / "MARS_SENTINEL_NASA_Terrain_Study_LEGACY.blend"
GLOBE_PREVIEW = ROOT / "previews" / "mars_globe_starfield.png"
TERRAIN_PREVIEW = ROOT / "previews" / "mars_jezero_real_terrain.png"
HIRISE_OVERVIEW = ROOT / "previews" / "mars_jezero_hirise_overview.png"
HIRISE_DETAIL = ROOT / "previews" / "mars_jezero_hirise_detail.png"


def create_star_world(name: str) -> bpy.types.World:
    world = bpy.data.worlds.new(name)
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.8
    environment = nodes.new("ShaderNodeTexEnvironment")
    environment.projection = "EQUIRECTANGULAR"
    star_image = bpy.data.images.load(str(ROOT / "data" / "starfield_equirectangular.png"), check_existing=True)
    if not star_image.packed_file:
        star_image.pack()
    environment.image = star_image
    links = world.node_tree.links
    # Leave Vector unconnected: Blender maps an equirectangular environment on Z-up by default.
    links.new(environment.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], out.inputs["Surface"])
    world["starfield_type"] = "Illustrative equirectangular star map, procedurally generated; not an astrometric catalog"
    return world


def look_at(obj: bpy.types.Object, point: Vector) -> None:
    obj.rotation_euler = (point - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_camera(scene: bpy.types.Scene, name: str, location: tuple[float, float, float],
               target: tuple[float, float, float], lens: float, clip_end: float) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = location
    camera.data.lens = lens
    camera.data.clip_end = clip_end
    look_at(camera, Vector(target))
    scene.camera = camera
    return camera


def add_sun(scene: bpy.types.Scene, name: str, position: tuple[float, float, float],
            target: tuple[float, float, float], energy: float, angle: float) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="SUN")
    data.energy = energy
    data.angle = angle
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    look_at(obj, Vector(target))
    return obj


def make_elevation_material(name: str) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = (0.55, 0.25, 0.12, 1.0)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = 0.92
    vertex_color = nodes.new("ShaderNodeVertexColor")
    vertex_color.layer_name = "ElevationTint"
    material.node_tree.links.new(vertex_color.outputs["Color"], shader.inputs["Base Color"])
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def add_globe_camera_backdrop(scene: bpy.types.Scene, camera: bpy.types.Object) -> bpy.types.Object:
    """Keep the active orbital camera's star texture visible behind the globe."""
    distance = 2100000.0
    half_width = distance * camera.data.sensor_width / (2.0 * camera.data.lens) * 1.18
    half_height = distance * 24.0 / (2.0 * camera.data.lens) * 1.18
    mesh = bpy.data.meshes.new("Starfield_Camera_Backdrop_Mesh")
    mesh.from_pydata(
        [(-half_width, -half_height, 0), (half_width, -half_height, 0),
         (half_width, half_height, 0), (-half_width, half_height, 0)],
        [], [(0, 1, 2, 3)],
    )
    uv_layer = mesh.uv_layers.new(name="UVMap")
    uv_by_vertex = ((0, 0), (1, 0), (1, 1), (0, 1))
    for loop in mesh.loops:
        uv_layer.data[loop.index].uv = uv_by_vertex[loop.vertex_index]
    backdrop = bpy.data.objects.new("Starfield_Backdrop_Illustrative_Camera_Only", mesh)
    scene.collection.objects.link(backdrop)
    cam_forward = camera.rotation_euler.to_matrix() @ Vector((0, 0, -1))
    backdrop.location = camera.location + cam_forward * distance
    backdrop.rotation_euler = camera.rotation_euler

    material = bpy.data.materials.new("Starfield_Emissive_Visual_Backdrop")
    material.use_nodes = True
    material.node_tree.nodes.clear()
    nodes = material.node_tree.nodes
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(ROOT / "data" / "starfield_globe_camera_crop.png"), check_existing=True)
    if not texture.image.packed_file:
        texture.image.pack()
    emission = nodes.new("ShaderNodeEmission")
    output = nodes.new("ShaderNodeOutputMaterial")
    material.node_tree.links.new(texture.outputs["Color"], emission.inputs["Color"])
    material.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    mesh.materials.append(material)
    backdrop["is_illustrative"] = True
    backdrop["purpose"] = "Camera-facing starfield backdrop for the orbital globe render"
    return backdrop


def terrain_color(t: float) -> tuple[float, float, float, float]:
    stops = [
        (0.0, (0.16, 0.055, 0.035)),
        (0.26, (0.33, 0.105, 0.055)),
        (0.55, (0.58, 0.22, 0.10)),
        (0.78, (0.77, 0.38, 0.17)),
        (1.0, (0.92, 0.67, 0.37)),
    ]
    for index in range(len(stops) - 1):
        lo, color_lo = stops[index]
        hi, color_hi = stops[index + 1]
        if t <= hi:
            f = max(0.0, min(1.0, (t - lo) / (hi - lo)))
            rgb = tuple(color_lo[c] * (1 - f) + color_hi[c] * f for c in range(3))
            return (*rgb, 1.0)
    return (*stops[-1][1], 1.0)


def build_dem_scene(grid: dict) -> bpy.types.Scene:
    scene = bpy.data.scenes.new("NASA_Jezero_CTX_DTM_20m")
    scene.world = create_star_world("MARS_Deep_Space_Stars")
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.001, 0.003, 0.009)
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    heights = grid["elevations_m"]
    rows, cols = grid["grid_height"], grid["grid_width"]
    step = float(grid["mesh_sample_spacing_m"])
    z_min = float(grid["elevation_min_m"])
    z_max = float(grid["elevation_max_m"])
    z_mid = 0.5 * (z_min + z_max)
    x_mid = 0.5 * (cols - 1) * step
    y_mid = 0.5 * (rows - 1) * step

    vertices = []
    colors = []
    for y, row in enumerate(heights):
        for x, z in enumerate(row):
            # GeoTIFF rows run southward from the north edge; flip Y so north is +Y.
            vertices.append((x * step - x_mid, y_mid - y * step, z - z_mid))
            colors.append(terrain_color((z - z_min) / (z_max - z_min)))

    faces = []
    for y in range(rows - 1):
        row_start = y * cols
        next_row = row_start + cols
        for x in range(cols - 1):
            a = row_start + x
            b = a + 1
            c = next_row + x + 1
            d = next_row + x
            faces.append((a, b, c, d))

    mesh = bpy.data.meshes.new("USGS_CTX_DTM_20m_sampled_at_80m")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    terrain = bpy.data.objects.new("Jezero_Real_Elevation_DTM_No_Exaggeration", mesh)
    scene.collection.objects.link(terrain)
    color_attr = mesh.color_attributes.new(name="ElevationTint", type="FLOAT_COLOR", domain="POINT")
    for item, color in zip(color_attr.data, colors):
        item.color = color
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    mesh.materials.append(make_elevation_material("CTX_DTM_Elevation_Colors"))

    info = bpy.data.texts.new("DATA_PROVENANCE_Jezero_CTX_DTM")
    info.write(json.dumps({k: v for k, v in grid.items() if k != "elevations_m"}, indent=2))
    terrain["source"] = grid["source"]
    terrain["source_doi"] = grid["doi"]
    terrain["native_resolution_m_per_pixel"] = grid["native_resolution_m_per_pixel"]
    terrain["sample_spacing_m"] = grid["mesh_sample_spacing_m"]
    terrain["vertical_exaggeration"] = 1.0
    terrain["is_illustrative"] = False

    add_camera(scene, "Jezero_DTM_Oblique_Camera", (0, -33000, 23000), (0, 0, 0), 38, 100000)
    add_sun(scene, "Mars_Sun_Key", (-15000, -25000, 40000), (0, 0, 0), 2.2, math.radians(8))
    scene.render.filepath = str(TERRAIN_PREVIEW)
    return scene


def build_globe_scene(source_scene: bpy.types.Scene, source_globe: bpy.types.Object) -> bpy.types.Scene:
    scene = bpy.data.scenes.new("MARS_Globe_Realistic_Starfield")
    scene.world = create_star_world("MARS_Deep_Space_Stars_Globe")
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.001, 0.003, 0.009)

    globe = source_globe.copy()
    globe.data = source_globe.data.copy()
    scene.collection.objects.link(globe)
    globe.name = "MARS_Orbital_Globe_Textured_Source_Copy"
    globe["surface_source"] = "Existing embedded Mars globe texture from source blend; visual texture, not the terrain DEM."
    camera = add_camera(scene, "Mars_Orbital_Camera", (0, -1600000, 380000), (0, 0, 0), 48, 3200000)
    add_globe_camera_backdrop(scene, camera)
    add_sun(scene, "Mars_Sun_Orbital", (-500000, -700000, 700000), (0, 0, 0), 2.0, math.radians(3))
    scene.render.filepath = str(GLOBE_PREVIEW)
    return scene


def build_hirise_scene(grid: dict, detail: bool) -> bpy.types.Scene:
    label = "Detail" if detail else "Regional_Overview"
    scene = bpy.data.scenes.new(f"NASA_Jezero_HiRISE_1m_{label}")
    scene.world = create_star_world(f"MARS_Stars_HiRISE_{label}")
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1100 if detail else 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    heights = grid["elevations_m"]
    rows, cols = grid["grid_height"], grid["grid_width"]
    valid_mask = grid.get("valid_mask", [[True] * cols for _ in range(rows)])
    step = float(grid["mesh_sample_spacing_m"])
    z_min, z_max = float(grid["elevation_min_m"]), float(grid["elevation_max_m"])
    z_mid = 0.5 * (z_min + z_max)
    x_mid, y_mid = 0.5 * (cols - 1) * step, 0.5 * (rows - 1) * step

    vertices = []
    colors = []
    for y, row in enumerate(heights):
        for x, z in enumerate(row):
            # GeoTIFF rows run southward from the north edge; flip Y so north is +Y.
            vertices.append((x * step - x_mid, y_mid - y * step, z - z_mid))
            colors.append(terrain_color((z - z_min) / max(0.001, z_max - z_min)))
    faces = []
    for y in range(rows - 1):
        row_start, next_row = y * cols, (y + 1) * cols
        for x in range(cols - 1):
            if not (valid_mask[y][x] and valid_mask[y][x + 1] and valid_mask[y + 1][x] and valid_mask[y + 1][x + 1]):
                continue
            a = row_start + x
            faces.append((a, a + 1, next_row + x + 1, next_row + x))

    mesh = bpy.data.meshes.new(f"USGS_HiRISE_1m_sampled_at_{int(step)}m")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    terrain = bpy.data.objects.new(f"Jezero_HiRISE_Real_Elevation_{label}_No_Exaggeration", mesh)
    scene.collection.objects.link(terrain)
    attribute = mesh.color_attributes.new(name="ElevationTint", type="FLOAT_COLOR", domain="POINT")
    for item, color in zip(attribute.data, colors):
        item.color = color
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    mesh.materials.append(make_elevation_material("HiRISE_DTM_Elevation_Colors"))
    info = bpy.data.texts.new(f"DATA_PROVENANCE_HiRISE_{label}")
    info.write(json.dumps({k: v for k, v in grid.items() if k != "elevations_m"}, indent=2))
    for key in ("source", "source_url", "doi", "native_resolution_m_per_pixel", "mesh_sample_spacing_m", "window_col_offset", "window_row_offset"):
        terrain[key] = grid[key]
    terrain["vertical_exaggeration"] = 1.0
    terrain["is_illustrative"] = False
    terrain["nodata_cells"] = sum(1 for row in valid_mask for valid in row if not valid)

    if detail:
        distance = max(float(grid["width_m"]), float(grid["height_m"])) * 1.35
        camera = (0, -distance, distance * 0.72)
        filepath = HIRISE_DETAIL
    else:
        distance = max(float(grid["width_m"]), float(grid["height_m"])) * 1.35
        camera = (0, -distance, distance * 0.72)
        filepath = HIRISE_OVERVIEW
    add_camera(scene, f"HiRISE_{label}_Camera", camera, (0, 0, 0), 42, distance * 4)
    add_sun(scene, f"HiRISE_{label}_Sun", (-distance, -distance, distance * 2), (0, 0, 0), 2.2, math.radians(4))
    scene.render.filepath = str(filepath)
    return scene


def main() -> None:
    grid = json.loads(GRID_JSON.read_text(encoding="utf-8"))
    overview_path = ROOT / "data" / "jez_hirise_1m_overview_grid.json"
    detail_path = ROOT / "data" / "jez_hirise_1m_detail_grid.json"
    source_scene = bpy.context.scene
    source_globe = bpy.data.objects.get("MARS_NEW_Globe")
    if source_globe is None:
        raise RuntimeError("Source MARS_NEW_Globe object not found")

    dem_scene = build_dem_scene(grid)
    hirise_scenes = []
    if overview_path.exists() and detail_path.exists():
        hirise_overview_grid = json.loads(overview_path.read_text(encoding="utf-8"))
        hirise_detail_grid = json.loads(detail_path.read_text(encoding="utf-8"))
        hirise_scenes = [
            build_hirise_scene(hirise_overview_grid, detail=False),
            build_hirise_scene(hirise_detail_grid, detail=True),
        ]
    else:
        print("HiRISE elevation grids not built yet; saving CTX + globe study as an intermediate version.")
    globe_scene = build_globe_scene(source_scene, source_globe)

    if bpy.context.window is not None:
        bpy.context.window.scene = dem_scene
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUTPUT))
    bpy.ops.render.render(write_still=True, scene=globe_scene.name)
    for hirise_scene in hirise_scenes:
        bpy.ops.render.render(write_still=True, scene=hirise_scene.name)
    bpy.ops.render.render(write_still=True, scene=dem_scene.name)
    print(f"Saved study blend: {BLEND_OUTPUT}")


if __name__ == "__main__":
    main()
