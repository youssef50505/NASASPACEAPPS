"""Read-only inventory of the latest HiRISE-ready Blender scene."""
from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "inspect_hirise_ready_scene.json"
SITE = "NASA_HiRISE_DTM_Jezero_FieldSite_4m"


def matrix_list(obj: bpy.types.Object) -> list[float]:
    return [round(value, 6) for row in obj.matrix_world for value in row]


def bounds(obj: bpy.types.Object) -> dict:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [point.x for point in points]
    ys = [point.y for point in points]
    zs = [point.z for point in points]
    return {
        "min": [min(xs), min(ys), min(zs)],
        "max": [max(xs), max(ys), max(zs)],
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "matrix_world": matrix_list(obj),
    }


def main() -> None:
    scene = bpy.context.scene
    site = bpy.data.objects.get(SITE)
    terrain = bpy.data.objects.get("Mars_Terrain")
    report = {
        "filepath": bpy.data.filepath,
        "scene": scene.name,
        "objects": len(scene.objects),
        "camera": scene.camera.name if scene.camera else None,
        "world": scene.world.name if scene.world else None,
        "frame": scene.frame_current,
        "collections": sorted(
            (f"{col.name} ({len(col.objects)})" for col in bpy.data.collections),
        ),
        "cameras": [obj.name for obj in scene.objects if obj.type == "CAMERA"],
        "armatures": [obj.name for obj in scene.objects if obj.type == "ARMATURE"],
        "lights": [obj.name for obj in scene.objects if obj.type == "LIGHT"],
        "curves": [obj.name for obj in scene.objects if obj.type == "CURVE"],
    }
    if site is not None:
        mesh = site.data
        report["site"] = {
            **bounds(site),
            "vertices": len(mesh.vertices),
            "polygons": len(mesh.polygons),
            "materials": [slot.name if slot else None for slot in mesh.materials],
            "uv": [layer.name for layer in mesh.uv_layers],
            "color_attributes": [attr.name for attr in mesh.color_attributes],
            "shape_keys": None if mesh.shape_keys is None else [key.name for key in mesh.shape_keys.key_blocks],
        }
    if terrain is not None:
        mesh = terrain.data
        keys = None
        if mesh.shape_keys is not None:
            keys = {key.name: key.value for key in mesh.shape_keys.key_blocks}
        report["terrain"] = {
            **bounds(terrain),
            "vertices": len(mesh.vertices),
            "materials": [slot.name if slot else None for slot in mesh.materials],
            "shape_keys": keys,
        }
    interesting = []
    needles = (
        "route", "hazard", "layer", "rover", "astronaut", "wheel", "antenna",
        "arm", "camera", "sun", "dust", "crater", "dune", "boulder", "sample",
        "globe", "pin", "marker", "msl", "joe",
    )
    for obj in scene.objects:
        lowered = obj.name.lower()
        if any(needle in lowered for needle in needles):
            interesting.append({"name": obj.name, "type": obj.type, "parent": obj.parent.name if obj.parent else None})
    report["interesting"] = interesting[:400]
    report["interesting_count"] = len(interesting)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"WROTE {OUT}")


if __name__ == "__main__":
    main()
