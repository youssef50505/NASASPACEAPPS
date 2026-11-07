---
name: Scene readability pass
overview: First append a complete working record to the project Markdown files, then make the Jezero scene open on the colored surface, frame the real crew with the 1 key, use local color where a real image covers the window, and separate the routes. The HiRISE mesh size, position, and shape stay frozen.
todos:
  - id: document-handoff
    content: Append a dated working guide to the Markdown docs so the current blend, color method, shortcuts, routes, and limits can be resumed without this chat
    status: completed
  - id: opening-camera
    content: Add a surface camera on the crew and rover, set it as the opening view, and stop key 1 from framing the 27 m rig
    status: completed
  - id: local-color
    content: Replace the single Viking hue with a real color image where one covers this Jezero window, without moving the mesh
    status: completed
  - id: distinct-routes
    content: Rebuild shortest, safest, and science routes so the safer line visibly detours around steep measured slope
    status: completed
isProject: false
---

# Readable view, local color, and distinct routes

## 0. Write the working record first

Nothing already in a Markdown file is deleted or rewritten. New text is appended as dated sections. [docs/memo.md](docs/memo.md) section 13 and [docs/MEMORY.md](docs/MEMORY.md) Appendix G already record the color pass. [docs/README.md](docs/README.md), [docs/INDEX.md](docs/INDEX.md), and [docs/3D_ASSETS_README.md](docs/3D_ASSETS_README.md) still tell the next person to open the older integrated file. Those three, plus [docs/PRD.md](docs/PRD.md), get an appended handoff.

The handoff states:

- Open [MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend](MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend). The color-only checkpoint is `MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend`. Do not modify `Mars_backup_before_quality_pass.blend`.
- The site mesh has 1,132,096 vertices, scale `(1, 1, 1)`, location `(0.23, -0.49, 0.015)`, and coordinate hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`. `Mars_Terrain` stays flat at z `-54.84`.
- Color method: HiRISE red orthomosaic DOI `10.5066/P9QJDP48` for brightness, Viking MDIM 2.1 bright-site hue for color. Jezero's own dark Viking samples were blue-biased and were not used. Provenance is [data/jez_site_color_provenance.json](data/jez_site_color_provenance.json). Preview is [previews/nasa_color_site_preview.png](previews/nasa_color_site_preview.png).
- Startup camera is still `MARS_NEW_Globe_Camera` at frame 112. Routes, astronaut, and rover keys play after that frame. Safest route 1143.31 m, shortest 1135.24 m. Layer switch is `tools/toggle_mars_layer.py` with `color`, `elevation`, or `slope`.
- Key `1` is installed from [tools/mars_front_view.py](tools/mars_front_view.py) into the Blender 5.2 and 5.4 startup folders. Blender must be restarted once. It still includes the 27 m rig, which the next scene pass will exclude.
- What is measured, what is illustrative, and what was deliberately not invented: no CRISM, THEMIS, or dust raster; no ancient-water pin inside this 4.1 km mesh; wheels are one mesh and are not spun on a false axle.
- The agreed next pass is sections 1–3 below. It is not done yet.

The mesh `NASA_HiRISE_DTM_Jezero_FieldSite_4m` stays at 1,132,096 vertices, scale `(1, 1, 1)`, and location `(0.23, -0.49, 0.015)`. `Mars_Terrain` stays flat at z `-54.84`. Later scene work is saved from the exploration blend into a new file so the current one remains the rollback.

## 1. Open on the crew, and make 1 frame them

The file still starts on `MARS_NEW_Globe_Camera` at frame 112, so the new surface is not the first view. One imported rig, `ludovisions_FC1_rig`, is about 27 m across and is included in the 1-key target list in [tools/mars_front_view.py](tools/mars_front_view.py), so it swallows the human-scale crew.

- Add a new surface camera aimed at Joe, the human-scale crew, the rover, and `White_Circle_Marker` when that marker sits within the crew area. Set it as the scene camera and the saved Layout view. Leave the existing globe camera and its animation untouched.
- Change the 1-key targets so the 27 m rig is excluded. Keep the six other crew roots only when their bounds are human-scale, plus the white work-area marker. Update the project copy and the Blender 5.2 and 5.4 startup copies of `mars_front_view.py`.
- A new preview from that camera must show the colored ground, the astronauts, and the rover together.

## 2. Local Mars color without moving the mesh

The current color is real HiRISE brightness with one hue taken from bright Viking terrain elsewhere, so the whole window shares one dust tint. Detail is real; local color is not.

- Search the USGS/HiRISE products already tied to this Jezero mosaic for an approximate-true-color RGB image that intersects the existing 4092 m window (18.43 N, 77.44 E). IRB false color is not used as the surface color.
- Where that image covers the window, crop it to the same bounds as [data/jez_hirise_site_nasa_color_1m.png](data/jez_hirise_site_nasa_color_1m.png) and use it as the base color. Outside its footprint, keep the current HiRISE-brightness tint.
- Record the product, DOI or observation ID, and the covered area on the mesh. Replace only the material image. Re-check the vertex hash before saving.

## 3. Routes that actually diverge

The safest route is 1143 m and the shortest is 1135 m because both walk almost straight to the landing site across gentle ground. The science route copies the safest line. The landing site and Wright Brothers Field are only about 20 m apart.

- From the existing slope grid, choose a start at the crew and a destination at Octavia E. Butler Landing only if a steep patch (the mesh reaches about 64 degrees) sits between them. The shortest path may cross moderate slope. The safest path must detour around cells at or above 15 degrees, so the two lines separate by a visible margin rather than a few meters.
- Draw the science route through any second published, in-window site that is not the same cell as the landing pin. If none exists, keep a single labeled landing stop and do not invent a mineral or ancient-water point. The western delta stays unpinned because it is outside this mesh.
- Thicken and color the three curves, and keep distance, elevation change, and max slope on each curve. Leave the old `RoutePlan` curves in place and marked as the earlier illustrative routes.

## Check

Reopen the new blend and confirm the vertex hash, scale, and location match the current exploration file. Render the new opening camera. The number 1 shortcut needs one Blender restart to load the startup script.