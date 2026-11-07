# MARS SENTINEL — Project Hub

> **IMPORTANT — ALL AGENTS: APPEND ONLY.** Do not delete, overwrite, truncate, or rewrite existing content in any `.md` file. Preserve all existing lines and add new dated sections at the end. Corrections must be appended as corrections; keep prior notes. Read [`AGENTS.md`](AGENTS.md) before changing this project.

## Open the fixed Blender project

Open **`MARS_SENTINEL_NASA_Terrain_Study.blend`** in this folder. It now loads the original integrated `Scene` in the `Layout` workspace, with the globe camera selected, scene materials/world enabled, and all existing people, rover, terrain, marker, and camera assets retained.

If Blender is still showing the old star-only CTX scene, close that loaded session and choose **Don't Save**. Reopen the file from this folder; the old version is preserved under `archive/`. Clear any `sphere` text from the Outliner search box to show all objects.

The custom top-row `1` action belongs to the embedded Blender script `front_view_models.py`. Blender blocks registered scripts unless trusted. Choose **Allow Execution** only if you have reviewed and trust this project file; choosing **Continue Safely** leaves the custom key unregistered. Do not switch on global auto-run for every `.blend` file.

## Project layout

```text
NASASPACEAPP/
├── MARS_SENTINEL_NASA_Terrain_Study.blend  # current working file
├── Mars_backup_before_quality_pass.blend   # untouched source backup
├── README.md                               # this quick start
├── docs/                                   # project and 3D documentation
├── data/                                   # NASA/USGS rasters, grids, metadata
├── tools/                                  # Blender inventory, repair, and preview scripts
├── previews/                               # diagnostic and earlier study images
└── archive/                                # previous broken study and rollback copies
```

## Documentation index

- [Project memory](docs/MEMORY.md) — competition, team, product, architecture, and prior context.
- [Product requirements](docs/PRD.md) — MARS SENTINEL requirements and delivery plan.
- [Blender recovery work log](docs/memo.md) — what was changed, verified, and remains open.
- [3D assets and data notes](docs/3D_ASSETS_README.md) — terrain provenance and prior study details.
- [Documentation index](docs/INDEX.md) — links to key assets and files.

## Verified limits

- The globe camera and integrated scene are restored; its sky uses procedural stars, not a measured Gaia star catalog.
- The local `Mars_Terrain` object is currently flat at its saved shape-key value. Its non-flat state does not yet match the downloaded DEM’s measured height range.
- The local camera is obstructed by rover mesh `MSL`; the startup view is the globe camera while that surface-camera composition remains to fix.
- The 1 m/pixel USGS HiRISE raster is available under `data/`; the current local Blender terrain has not yet been regenerated from it.

See `docs/memo.md` before changing terrain transforms, shape keys, cameras, or script trust settings.

## Agent work-log instruction — 2026-11-06

All agents must follow [`AGENTS.md`](AGENTS.md): preserve all Markdown content and append dated additions only. This section is an additive instruction and must remain in place.

## Working file — 2026-11-06

Open `MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend`. The color-only checkpoint is `MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend`. Do not modify `Mars_backup_before_quality_pass.blend`.

The HiRISE site mesh `NASA_HiRISE_DTM_Jezero_FieldSite_4m` has 1,132,096 vertices, scale `(1, 1, 1)`, location `(0.23, -0.49, 0.015)`, and coordinate hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`. `Mars_Terrain` stays flat at z `-54.84` with `Flat_Ground = 1`.

Surface brightness is the USGS HiRISE red orthomosaic, DOI `10.5066/P9QJDP48`. The hue is the Viking MDIM 2.1 bright-site balance, because Jezero's own dark Viking samples in that file are blue-biased. Provenance: `data/jez_site_color_provenance.json`. Preview: `previews/nasa_color_site_preview.png`.

The file still opens on `MARS_NEW_Globe_Camera` at frame 112. Play later frames for the tour, astronaut, and rover keys. Safest route: 1143.31 m. Shortest route: 1135.24 m. Switch the site material with `tools/toggle_mars_layer.py` and `color`, `elevation`, or `slope`.

Key `1` comes from `tools/mars_front_view.py`, copied into the Blender 5.2 and 5.4 startup folders. Restart Blender once. It still frames the 27 m `ludovisions_FC1_rig` with the crew.

No CRISM, THEMIS, or dust raster was clipped to this window. No ancient-water pin was placed inside the 4.1 km mesh. `Wheels_objs` is one mesh and is not spun on a false axle. The full log is `docs/memo.md` sections 13 and 14. The next agreed pass, not done yet, opens on the crew, excludes the oversized rig from key `1`, uses a local color image where one covers the window, and separates the routes.

## Readable scene — 2026-11-06

Open `MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend`. The exploration file above stays the rollback. The site hash, vertex count, scale, and location are unchanged, and `Mars_Terrain` is still flat at z `-54.84`.

The opening camera is `MS_Surface_Opening_Camera` at frame 361, when Joe is beside the rover. Key `1` ignores meshes larger than 8 m, including the 27 m rig. Restart Blender once. The center of the ground uses HiRISE merged RGB `ESP_045994_1985` (NASA/JPL-Caltech/UArizona, not IRB). The rest of the window keeps the earlier tint. Shortest route 1113.50 m, safest 1159.95 m, science 1203.21 m through the Rochette sample site. Details are in `docs/memo.md` section 16. Previews: `previews/surface_opening_preview.png` and `previews/route_separation_preview.png`.

## Tightened opening shot — 2026-11-06

Open `MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend`. The readable blend above is the rollback. Frame 76 shows the rover and Joe up close. The routes are thin lines, the big work ring is hidden, and the globe is outside that camera. Joe walks to the landing by frame 458. The color edge fades across 30 m. Record: `docs/memo.md` section 17. Preview: `previews/surface_focus_opening.png`.

## Walk on the same file — 2026-11-06

Keep working in `MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend`. `Sketchfab_model` walks the green route from frame 100 using `Mixamo Walk` at 1.4 m per cycle. Joe stays beside the rover until frame 1514. The rover and wheels stay put, and the wheels are not spun. The timeline ends at frame 38906. Record: `docs/memo.md` section 18. Previews: `previews/surface_walk_open.png` and `previews/surface_walk_step.png`.
