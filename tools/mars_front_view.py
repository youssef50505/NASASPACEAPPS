"""Frame the Mars crew when 1 is pressed, without enabling auto-run for every blend."""
import math

import bpy
from mathutils import Vector

TARGET_ROOTS = [
    "Sketchfab_model.007",
    "Sketchfab_model.015",
    "Sketchfab_model",
    "Joe_Astronaut",
    "Sketchfab_model.003",
]
WORK_MARKERS = ["White_Circle_Marker", "White_Ring"]
MAX_CREW_EXTENT = 8.0
PADDING = 1.1


class VIEW3D_OT_front_on_models(bpy.types.Operator):
    bl_idname = "view3d.front_on_models"
    bl_label = "Front View on Models"
    bl_description = "Face the models straight from the front, centered and fully visible"

    def execute(self, context):
        area = context.area
        if area is None or area.type != "VIEW_3D":
            return {"CANCELLED"}
        space = area.spaces.active
        region_3d = space.region_3d
        region = next((item for item in area.regions if item.type == "WINDOW"), None)
        if region_3d is None or region is None:
            return {"CANCELLED"}
        if bpy.data.objects.get("MS_Surface_Opening_Camera") is not None:
            context.scene.frame_set(76)
        space.clip_start = 0.05
        space.clip_end = 5000.0
        view_layer = context.view_layer
        grouped = []
        for name in TARGET_ROOTS:
            root = bpy.data.objects.get(name)
            if root is None:
                continue
            for obj in [root, *root.children_recursive]:
                if obj.type != "MESH" or obj.name not in view_layer.objects:
                    continue
                if obj.hide_get() or obj.hide_viewport:
                    continue
                corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
                extent = max(max(point.x for point in corners) - min(point.x for point in corners),
                             max(point.y for point in corners) - min(point.y for point in corners),
                             max(point.z for point in corners) - min(point.z for point in corners))
                if extent > MAX_CREW_EXTENT:
                    continue
                grouped.append(corners)
        points = []
        if grouped:
            centers = [sum(corners, Vector()) / len(corners) for corners in grouped]
            order = sorted(range(len(centers)), key=lambda index: (centers[index].x, centers[index].y))
            median = centers[order[len(order) // 2]]
            near = [corners for corners, center in zip(grouped, centers) if (center - median).length <= 50.0]
            chosen = near or grouped
            for corners in chosen:
                points.extend(corners)
        if points:
            center_now = sum(points, Vector()) / len(points)
            for name in WORK_MARKERS:
                marker = bpy.data.objects.get(name)
                if marker is None or marker.name not in view_layer.objects:
                    continue
                corners = [marker.matrix_world @ Vector(corner) for corner in marker.bound_box]
                extent = max(max(point.x for point in corners) - min(point.x for point in corners),
                             max(point.y for point in corners) - min(point.y for point in corners))
                marker_center = sum(corners, Vector()) / len(corners)
                if extent <= 40.0 and (marker_center - center_now).length <= 50.0:
                    points.extend(corners)
        if not points:
            return bpy.ops.view3d.view_axis(type="FRONT")
        minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
        maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
        center = (minimum + maximum) / 2
        width = maximum.x - minimum.x
        height = maximum.z - minimum.z
        region_3d.view_perspective = "PERSP"
        region_3d.view_rotation = (math.sqrt(0.5), math.sqrt(0.5), 0.0, 0.0)
        region_3d.view_location = center
        half = (space.lens and 36.0 / space.lens) or 0.3
        if region.width >= region.height:
            scale_x, scale_y = half, half * region.height / region.width
        else:
            scale_x, scale_y = half * region.width / region.height, half
        distance = max((width / 2) / scale_x, (height / 2) / scale_y) * PADDING
        distance += (maximum.y - minimum.y) / 2
        region_3d.view_distance = max(distance, 0.1)
        return {"FINISHED"}


class VIEW3D_OT_mars_planet_outside(bpy.types.Operator):
    bl_idname = "view3d.mars_planet_outside"
    bl_label = "Mars From Outside"
    bl_description = "Pull the view back to the planet from outside"

    def execute(self, context):
        area = context.area
        if area is None or area.type != "VIEW_3D":
            return {"CANCELLED"}
        space = area.spaces.active
        region_3d = space.region_3d
        globe = bpy.data.objects.get("MARS_NEW_Globe")
        if region_3d is None or globe is None:
            return {"PASS_THROUGH"}
        center = globe.matrix_world.translation.copy()
        radius = max(globe.dimensions) / 2.0
        satellite = bpy.data.objects.get("Sketchfab_model.008")
        points = []
        if satellite is not None:
            for obj in [satellite, *satellite.children_recursive]:
                if obj.type == "MESH":
                    points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
        if points:
            low = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
            high = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
            satellite_mid = (low + high) / 2
            satellite_radius = (high - low).length / 2.0
            look = center.lerp(satellite_mid, 0.22)
            extent = max((center - look).length + radius, (satellite_mid - look).length + satellite_radius)
            outward = (satellite_mid - center)
            if outward.length < 1.0:
                outward = Vector((0.0, 1.0, 0.0))
            outward.normalize()
            side = outward.cross(Vector((0.0, 0.0, 1.0)))
            if side.length < 0.2:
                side = outward.cross(Vector((0.0, 1.0, 0.0)))
            eye_direction = (side.normalized() * 0.75 + Vector((0.0, 0.0, 1.0)) * 0.35).normalized()
            region_3d.view_rotation = (-eye_direction).to_track_quat("-Z", "Y")
        else:
            look = center
            extent = radius * 1.8
            camera = bpy.data.objects.get("MARS_NEW_Globe_Camera")
            eye = camera.matrix_world.translation if camera is not None else center + Vector((0.0, -900000.0, 400000.0))
            region_3d.view_rotation = (center - eye).to_track_quat("-Z", "Y")
        lens = space.lens or 50.0
        fit = math.tan(math.atan((36.0 / 2.0) / lens)) * 0.55
        distance = extent / fit
        region_3d.view_perspective = "PERSP"
        region_3d.view_location = look
        region_3d.view_distance = distance
        space.clip_start = max(10.0, distance / 5000.0)
        space.clip_end = distance * 6.0
        return {"FINISHED"}


_keymaps = []


def register():
    for operator in (VIEW3D_OT_front_on_models, VIEW3D_OT_mars_planet_outside):
        try:
            bpy.utils.register_class(operator)
        except ValueError:
            pass
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if keyconfig is None:
        return
    for keymap_name, space in (("3D View", "VIEW_3D"), ("Object Mode", "EMPTY")):
        keymap = keyconfig.keymaps.new(name=keymap_name, space_type=space)
        for key in ("NUMPAD_1", "ONE"):
            item = keymap.keymap_items.new("view3d.front_on_models", key, "PRESS", head=True)
            _keymaps.append((keymap, item))
        for key in ("NUMPAD_2", "TWO"):
            item = keymap.keymap_items.new("view3d.mars_planet_outside", key, "PRESS", head=True)
            _keymaps.append((keymap, item))


def unregister():
    for keymap, item in _keymaps:
        try:
            keymap.keymap_items.remove(item)
        except Exception:
            pass
    _keymaps.clear()
    for operator in (VIEW3D_OT_mars_planet_outside, VIEW3D_OT_front_on_models):
        try:
            bpy.utils.unregister_class(operator)
        except Exception:
            pass


register()
