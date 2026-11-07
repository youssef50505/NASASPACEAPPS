# MARS SENTINEL Documentation

> **IMPORTANT — ALL AGENTS: APPEND ONLY.** Preserve every existing Markdown line. Do not delete, overwrite, truncate, or rewrite content; append dated additions and correction notes at the end. See [`../AGENTS.md`](../AGENTS.md).

Start with the project [README](../README.md) for opening the canonical Blender file and understanding the folder layout.

## Core documents

- [PRD](PRD.md) — detailed product requirements, scope, team roles, risks, and acceptance criteria.
- [MEMORY](MEMORY.md) — durable project context, challenge research, architecture, prior discussions, and data notes.
- [Blender work log](memo.md) — recovery, verification, known limitations, and next steps.
- [3D asset/data notes](3D_ASSETS_README.md) — Blender study history, source rasters, sampling, and regeneration.

## Main project files

- Working Blender scene: [`../MARS_SENTINEL_NASA_Terrain_Study.blend`](../MARS_SENTINEL_NASA_Terrain_Study.blend)
- Untouched source backup: [`../Mars_backup_before_quality_pass.blend`](../Mars_backup_before_quality_pass.blend)
- HiRISE 1 m raster: [`../data/JEZ_hirise_soc_006_DTM_1m.tif`](../data/JEZ_hirise_soc_006_DTM_1m.tif)
- CTX 20 m raster: [`../data/JEZ_ctx_B_soc_008_DTM_20m.tif`](../data/JEZ_ctx_B_soc_008_DTM_20m.tif)
- Current globe preview: [`../previews/recovered_globe_texture_preview.png`](../previews/recovered_globe_texture_preview.png)
- Previous broken file and rollback copies: [`../archive/`](../archive/)

## Agent work-log instruction — 2026-11-06

Any later index updates must be additive dated entries. Existing links and history stay in place.

## Current working scene — 2026-11-06

The links above remain the recovery record. The file to open now is [`../MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend`](../MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend). Color checkpoint: [`../MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend`](../MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend). Do not modify [`../Mars_backup_before_quality_pass.blend`](../Mars_backup_before_quality_pass.blend).

- Color provenance: [`../data/jez_site_color_provenance.json`](../data/jez_site_color_provenance.json)
- Geometry check: [`../data/verify_exploration_geometry.json`](../data/verify_exploration_geometry.json)
- Surface preview: [`../previews/nasa_color_site_preview.png`](../previews/nasa_color_site_preview.png)
- Site mesh hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`, 1,132,096 vertices, scale `(1, 1, 1)`, location `(0.23, -0.49, 0.015)`. `Mars_Terrain` remains flat at z `-54.84`.
- Startup view is still `MARS_NEW_Globe_Camera` at frame 112. Safest route 1143.31 m, shortest 1135.24 m. Layer tool: `tools/toggle_mars_layer.py`.
- Key `1` is `tools/mars_front_view.py` in the Blender 5.2 and 5.4 startup folders. Restart Blender once. The 27 m rig is still included.
- Measured: HiRISE brightness DOI `10.5066/P9QJDP48`, elevation, slope, landing pin 18.4447 N, 77.4508 E, Wright Brothers Field 18.44486 N, 77.45102 E. Not measured and not invented: CRISM, THEMIS, dust optical depth, and an ancient-water pin inside this mesh. Wheel spin is not faked. Details: `memo.md` sections 13–14.

## Readable scene — 2026-11-06

The file to open after the readability pass is [`../MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend`](../MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend). The exploration blend remains the rollback.

- Opening preview: [`../previews/surface_opening_preview.png`](../previews/surface_opening_preview.png)
- Route preview: [`../previews/route_separation_preview.png`](../previews/route_separation_preview.png)
- Local color provenance: [`../data/jez_site_local_color_provenance.json`](../data/jez_site_local_color_provenance.json)
- Same site hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`. Camera `MS_Surface_Opening_Camera`, frame 361. Routes 1113.50 m, 1159.95 m, and 1203.21 m. Log: `memo.md` section 16.

## Walk on the same file — 2026-11-06

The file to keep editing is [`../MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend`](../MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend).

- Opening still: [`../previews/surface_walk_open.png`](../previews/surface_walk_open.png)
- Walker entering the shot: [`../previews/surface_walk_step.png`](../previews/surface_walk_step.png)
- `Sketchfab_model` follows the green route with `Mixamo Walk` from frame 100. Joe holds until frame 1514. The rover and wheels do not move. Timeline ends at frame 38906. Log: `memo.md` section 18.

