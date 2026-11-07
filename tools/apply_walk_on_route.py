"""Walk the Mixamo astronaut along the green route inside the current blend.

Joe keeps his existing landing keys, shifted so he stays beside the rover
until the walker has left. The rover and its wheels are not moved.
"""
from __future__ import annotations

import array
import hashlib
import math
from pathlib import Path

import bpy
from mathutils import Vector

EXPECTED = "ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd"
SOURCE = "MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend"
CYCLE_FRAMES = 45.6
STRIDE_M = 1.4
WALK_START = 100
AWAY_M = 25.0


def fingerprint(obj: bpy.types.Object) -> str:
    coords = array.array("f", [0.0]) * (len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get("co", coords)
    return hashlib.sha256(coords.tobytes()).hexdigest()


def action_fcurves(action: bpy.types.Action):
    found = []
    for layer in action.layers:
        for strip in layer.strips:
            bags = getattr(strip, "channelbags", None) or []
            for bag in bags:
                found.extend(bag.fcurves)
    return found


def polyline(points: list[Vector]) -> tuple[list[Vector], float]:
    length = 0.0
    for first, second in zip(points, points[1:]):
        length += (second - first).length
    return points, length


def sample_by(points: list[Vector], spacing: float) -> list[Vector]:
    if len(points) < 2:
        return points
    sampled = [points[0]]
    carried = 0.0
    for first, second in zip(points, points[1:]):
        edge = second - first
        edge_length = edge.length
        if edge_length == 0.0:
            continue
        while carried + edge_length >= spacing:
            remain = spacing - carried
            first = first + edge * (remain / edge_length)
            sampled.append(first.copy())
            edge = second - first
            edge_length = edge.length
            carried = 0.0
            if edge_length == 0.0:
                break
        else:
            carried += edge_length
    if (sampled[-1] - points[-1]).length > spacing * 0.25:
        sampled.append(points[-1])
    return sampled


def heading(direction: Vector) -> float:
    # The imported rig faces world -Y when Z rotation is 0.
    return math.atan2(direction.x, -direction.y)


def shift_joe(joe: bpy.types.Object, hold_until: float) -> None:
    delta = hold_until - 210.0
    for fcurve in action_fcurves(joe.animation_data.action):
        hold_value = None
        for key in fcurve.keyframe_points:
            if abs(key.co[0] - 90.0) < 0.1:
                hold_value = float(key.co[1])
            if key.co[0] >= 200.0:
                key.co[0] += delta
        if hold_value is not None:
            key = fcurve.keyframe_points.insert(hold_until, hold_value, options={"FAST"})
            key.interpolation = "CONSTANT"
        fcurve.update()


def main() -> None:
    if Path(bpy.data.filepath).name != SOURCE:
        raise RuntimeError(f"Open {SOURCE} first")
    scene = bpy.context.scene
    site = bpy.data.objects["NASA_HiRISE_DTM_Jezero_FieldSite_4m"]
    before = fingerprint(site)
    if before != EXPECTED:
        raise RuntimeError("Site hash changed before the walk")
    rover = bpy.data.objects["MSL"]
    wheels = bpy.data.objects["Wheels_objs"]
    rover_location = tuple(round(float(v), 5) for v in rover.location)
    wheels_location = tuple(round(float(v), 5) for v in wheels.location)
    rover_action = rover.animation_data.action.name
    wheels_action = wheels.animation_data.action.name

    scene.frame_set(76)
    walker = bpy.data.objects["Sketchfab_model"]
    route = bpy.data.objects["MS_Route_Safest_HiRISE"]
    spline = route.data.splines[0]
    origin = Vector(walker.location)
    lift = origin.z - spline.points[0].co.z
    raw = [origin]
    for point in spline.points:
        raw.append(Vector((point.co.x, point.co.y, point.co.z + lift)))
    _full, length = polyline(raw)
    samples = sample_by(raw, STRIDE_M)
    step_frames = CYCLE_FRAMES
    joe = bpy.data.objects["Joe_Astronaut"]
    joe_now = Vector(joe.matrix_world.translation)
    away_index = 0
    for index in range(1, len(samples)):
        if (samples[index] - joe_now).length >= AWAY_M and (samples[index] - origin).length >= AWAY_M:
            away_index = index
            break
    away_frame = WALK_START + away_index * step_frames
    shift_joe(joe, away_frame)

    base_euler = walker.rotation_euler.copy()
    if walker.animation_data is None:
        walker.animation_data_create()
    for index, point in enumerate(samples):
        frame = WALK_START + index * step_frames
        walker.location = point
        walker.keyframe_insert("location", frame=frame)
        direction = samples[min(index + 1, len(samples) - 1)] - point
        if direction.length == 0.0 and index > 0:
            direction = point - samples[index - 1]
        walker.rotation_euler = (base_euler.x, base_euler.y, heading(direction))
        walker.keyframe_insert("rotation_euler", frame=frame)
    walker["walk_route"] = "MS_Route_Safest_HiRISE"
    walker["walk_action"] = "Mixamo Walk"
    walker["stride_m_per_cycle"] = STRIDE_M
    walker["cycle_frames"] = CYCLE_FRAMES

    arm = bpy.data.objects["Object_4"]
    action = arm.animation_data.action
    for track in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(track)
    track = arm.animation_data.nla_tracks.new()
    track.name = "MixamoWalkLoop"
    strip = track.strips.new("Mixamo Walk", 1, action)
    strip.repeat = max(1, math.ceil((len(samples) * step_frames) / CYCLE_FRAMES))
    strip.extrapolation = "HOLD"
    arm.animation_data.action = None
    arm["walk_note"] = "Existing Mixamo Walk cycles while Sketchfab_model follows the green route."

    scene.frame_end = max(scene.frame_end, int(WALK_START + (len(samples) - 1) * step_frames) + 1, int(away_frame) + 400)
    scene.frame_set(76)
    if fingerprint(site) != before:
        raise RuntimeError("Site hash changed")
    if tuple(round(float(v), 5) for v in rover.location) != rover_location:
        raise RuntimeError("Rover moved")
    if tuple(round(float(v), 5) for v in wheels.location) != wheels_location:
        raise RuntimeError("Wheels moved")
    if rover.animation_data.action.name != rover_action or wheels.animation_data.action.name != wheels_action:
        raise RuntimeError("Rover or wheel action changed")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_mainfile()
    print("SAVED_IN_PLACE", bpy.data.filepath)
    print("SAMPLES", len(samples), "LENGTH", round(length, 1), "AWAY_FRAME", round(away_frame), "END", scene.frame_end)
    print("WALKER76", [round(float(v), 2) for v in walker.matrix_world.translation])


if __name__ == "__main__":
    main()
