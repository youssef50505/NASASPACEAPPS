"""Read-only structural inventory of a Mars .blend. Embedded scripts are not run."""
from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
stem = Path(bpy.data.filepath).stem


def vec(value):
    return [round(float(x), 6) for x in value]


def action_curves(action):
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag is not None:
                    curves.extend(bag.fcurves)
    return curves


def object_record(obj):
    bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    record = {
        "name": obj.name,
        "type": obj.type,
        "location": vec(obj.matrix_world.translation),
        "dimensions": vec(obj.dimensions),
        "bounds_min": [round(min(v[i] for v in bounds), 4) for i in range(3)],
        "bounds_max": [round(max(v[i] for v in bounds), 4) for i in range(3)],
        "parent": obj.parent.name if obj.parent else None,
        "collections": sorted(c.name for c in obj.users_collection),
        "hide_viewport": bool(obj.hide_viewport),
        "hide_render": bool(obj.hide_render),
        "animation_action": obj.animation_data.action.name if obj.animation_data and obj.animation_data.action else None,
        "custom_properties": {k: str(obj[k])[:500] for k in obj.keys() if k != "_RNA_UI"},
    }
    if obj.type == "MESH" and obj.data:
        record["mesh_vertices"] = len(obj.data.vertices)
        record["mesh_edges"] = len(obj.data.edges)
        record["mesh_faces"] = len(obj.data.polygons)
    if obj.type == "CAMERA":
        record["lens_mm"] = float(obj.data.lens)
    if obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        curves = action_curves(action)
        record["animated_paths"] = sorted(set(fc.data_path for fc in curves))
        record["keyframe_count"] = sum(len(fc.keyframe_points) for fc in curves)
    return record


records = [object_record(o) for o in bpy.data.objects]
keywords = ("astronaut", "person", "human", "rover", "spacecraft", "ship", "rocket", "circle", "site", "white", "zone", "area", "mars", "sphere", "camera", "station", "habitat", "mission")
matching = [r for r in records if any(k in r["name"].casefold() for k in keywords)]
scene_records = []
for scene in bpy.data.scenes:
    scene_records.append({
        "name": scene.name,
        "camera": scene.camera.name if scene.camera else None,
        "world": scene.world.name if scene.world else None,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "frame_current": scene.frame_current,
        "marker_frames": [{"name": m.name, "frame": m.frame, "camera": m.camera.name if m.camera else None} for m in scene.timeline_markers],
        "object_count": len(scene.objects),
        "objects": sorted(o.name for o in scene.objects),
    })
texts = []
for block in bpy.data.texts:
    content = block.as_string()
    texts.append({"name": block.name, "characters": len(content), "lines": content.count("\n") + (1 if content else 0), "preview": content[:1200]})
    if block.name.casefold().endswith(".py") or "dashboard" in block.name.casefold() or "view" in block.name.casefold():
        target = DATA / f"{stem}__{Path(block.name).name}.untrusted.txt"
        target.write_text(f"Source text datablock: {block.name}\nNot executed by this inspection.\n\n{content}", encoding="utf-8")

collection_records = []
for collection in bpy.data.collections:
    collection_records.append({"name": collection.name, "object_count": len(collection.objects), "objects": sorted(o.name for o in collection.objects)})

report = {
    "blend_file": bpy.data.filepath,
    "active_scene": bpy.context.scene.name if bpy.context.scene else None,
    "scene_count": len(bpy.data.scenes),
    "object_count": len(records),
    "object_type_counts": {kind: sum(1 for r in records if r["type"] == kind) for kind in sorted(set(r["type"] for r in records))},
    "scene_records": scene_records,
    "camera_records": [r for r in records if r["type"] == "CAMERA"],
    "keyword_matches": matching,
    "animated_objects": [r for r in records if r["animation_action"]],
    "collection_records": collection_records,
    "text_blocks": texts,
    "all_object_names": sorted(r["name"] for r in records),
}
out = DATA / f"inspect_{stem}.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"Wrote read-only report: {out}")
print(f"scenes={len(bpy.data.scenes)} objects={len(records)} cameras={sum(1 for o in bpy.data.objects if o.type == 'CAMERA')} text_blocks={len(texts)}")
print("active scene:", report["active_scene"])
print("matching names:", [r["name"] for r in matching[:250]])
print("text blocks:", [(t["name"], t["lines"]) for t in texts])
