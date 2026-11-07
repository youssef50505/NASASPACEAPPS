# MARS SENTINEL — Blender Recovery & Work Log

> **IMPORTANT — ALL AGENTS: APPEND ONLY.** Do not delete, overwrite, truncate, or rewrite any existing content in this or any Markdown file. Add dated sections at the end. Append corrections and explain them; preserve the original account. Follow [`../AGENTS.md`](../AGENTS.md).

**Last updated:** 6 November 2026 (Africa/Cairo)  
**Workspace:** `C:\Users\yhsn5\Downloads\NASASPACEAPP`  
**Purpose:** durable, factual record of the Blender investigation, recovery, data sources, checks, limitations, and remaining work. This memo records the work actually done in the available project context; it does not pretend to contain chat history that is no longer available in this workspace.

## 1. User’s request and intended result

The user reported that pressing `1` used to frame the astronauts/people and the white-circled work area, and asked to restore the scene so the field site remains part of the Mars planet, with the sky, terrain, astronauts, rover/spacecraft, and related assets visible and connected. They specifically asked for a complete work log: what was searched, changed, not changed, what is missing, and what needs fixing. The first screenshot showed a blank viewport and script warning. A later screenshot of the same path showed the old in-memory `NASA_Jezero_CTX_DTM_20m` scene, synthetic stars, and a tiny orange terrain tile. The disk file was then replaced with the integrated working scene, but Blender had not reloaded the file; the currently displayed application session can continue showing the old scene until it is closed without saving and reopened.

Relevant standing project requirements from earlier messages and `MEMORY.md`:

- Project name: **MARS SENTINEL**, NASA Space Apps Challenge 2026, team challenge focus: **Interplanetary Survival Guide: Martian Map**.
- Build a real, source-backed Jezero exploration/planning experience; clearly label illustrative assets and never present generated numbers as NASA measurements.
- The user has a large existing Blender scene and wants real Mars terrain and a credible sky. They previously allowed downloading the roughly 2 GB HiRISE product.
- The product decision documented in `MEMORY.md` is browser-first Angular + Java/Spring + Three.js for the decision-support demo, with Blender as the authoring source. Unity would be appropriate only if the deliverable becomes a standalone immersive game; do not turn the entire hackathon scope into a game-engine migration.
- The user expects the scene work to be saved as it progresses and the full discussion/work record to be kept in markdown.

See [`MEMORY.md`](MEMORY.md) for the broader product requirements, competition notes, team roles, challenge analysis, and previous conversation digest. See [`PRD.md`](PRD.md) for the current product requirements document. This memo supplements those documents; it does not replace them.

## 2. Files reviewed and their status

| File | Role / finding | State after this work |
|---|---|---|
| `Mars_backup_before_quality_pass.blend` | Pre-existing source/backup. One integrated scene, 4,181 objects, original cameras/world/assets/scripts. | **Untouched.** This remains the recovery source. |
| `MARS_SENTINEL_NASA_Terrain_Study.blend` | Current working file rebuilt from the untouched source. The original integrated `Scene` and world remain, 4,181 objects are preserved, and the globe camera is selected for startup. | **Created and reopened for verification.** This is the file shown in the screenshot and the file to open. |
| `archive/MARS_SENTINEL_NASA_Terrain_Study_PREVIOUS_BROKEN.blend` | Previous study variant that activated the isolated CTX scene. | Copied into the archive before the root working file was replaced. |
| `archive/MARS_SENTINEL_RECOVERED_PREVIOUS.blend` | Earlier recovery checkpoint with the original active camera. | Preserved for rollback. |
| `PRD.md` | Product requirements. | Read as existing project context; not edited in this Blender recovery pass. |
| `MEMORY.md` | Long-form project memory and earlier 3D/data research appendix. | Kept under `docs/` and updated with the current recovery status and file layout. |
| Two pasted-text attachments from the earlier conversation | Team message/context and challenge/project discussion. | Their relevant points are summarized in `MEMORY.md`; this Blender pass did not reconstruct them as a verbatim transcript. |

The source file was not modified. The previous study was copied into `archive/` before the root file with the same name was replaced by the integrated working scene. The change is reversible using the archived copy.

## 3. Investigation and root cause

### 3.1 Why pressing `1` stopped framing the astronauts

The original file has one active integrated scene named `Scene`. The experimental study introduced separate scenes and activated the CTX-only scene. The `front_view_models.py` operator searches the **active View Layer** for the target astronaut model roots. When the isolated CTX scene was active, those targets were outside that View Layer, so the operator could not frame them. The actors had not been deleted; they were in the other/original scene.

The screenshot’s Outliner search field also contains `sphere`. That is only a display filter: it hides object names that do not match the text from the Outliner list; it does not delete those objects. Clear the Outliner search field when checking the recovered asset list.

The original embedded `front_view_models.py` registers a custom operator, `view3d.front_on_models`, with both `NUMPAD_1` and the top-row `ONE` key. It computes a visible mesh bounding box from the current View Layer and points the viewport at the named astronaut roots. Restoring the original integrated scene is the essential scene-graph repair.

### 3.2 Why Blender showed the script warning

The screenshot is Blender’s normal security warning for registered Python Text blocks. Blender disables automatic execution by default; a `.blend` may request it through registered Text datablocks or drivers. The dialog offers “Allow Execution” or “Continue Safely.” The warning itself does not mean the file is corrupt, nor does it mean that the scripts already ran. Blender documents this behavior in its [Scripting & Security manual](https://docs.blender.org/manual/en/latest/advanced/scripting/security.html).

The existing `front_view_models.py` and `mars_dashboard.py` were statically reviewed in the prior investigation. The reviewed code uses Blender API operations for viewport framing, camera switching, controls, and interface behavior; static searches found no shell/process, network, file-write, `exec`, or `eval` behavior in those two scripts. **No embedded script was executed during this recovery.** Static inspection is not a full proof of safety for every Text block, driver, or external asset. Therefore no global Blender auto-run preference was changed and no “Allow Execution” click was made by the automation. Because the keymap is registered by a script, the custom `1` action may remain unavailable until the user trusts/runs the reviewed project scripts or otherwise loads that add-on. Do not enable automatic execution for arbitrary downloaded `.blend` files.

### 3.3 The camera view is also poorly framed

The scene inventory confirms the people, rover-like objects, and globe exist. A read-only ray cast from the center of `Mars_Camera` hits the mesh object **`MSL`** at about 20.0 scene units. That rover body is the central object obstructing the local camera view. A diagnostic render with `White_Ring` hidden in memory looked unchanged, so the ring was not the occluder. The previous interim guess that the ring caused the obstruction was wrong; the ray-cast result supersedes it.

The cameras have different purposes and current framing quality varies:

- `MARS_NEW_Globe_Camera`: shows the full globe in the restored scene’s Workbench preview, though its background is the Workbench display and not a verified final sky render.
- `Mars_Camera`: points through/at the `MSL` mesh; its composition hides part of what the user expects to see.
- `Mars_Orbit_View_Camera`: is the original scene camera, but its low-cost structural preview is not a polished “planet from orbit” composition.

No camera transform or animation was changed in the recovery copy. Only the active camera pointer and saved Layout viewport were set to the existing globe camera. A separate surface overview camera is still needed to frame the rover and people together without changing existing shots.

## 4. What the recovery copy changes

The current working copy was generated by `tools/restore_mars_scene.py` from `Mars_backup_before_quality_pass.blend` using Blender 5.2.3 LTS in background mode.

It:

1. Requires exactly one source scene named `Scene` and the expected original camera `Mars_Orbit_View_Camera`; it aborts rather than silently reconstructing from the wrong file.
2. Keeps the original Scene, frame 112, world `Mars_Sky_NASA`, all 4,181 scene objects, geometry, materials, animation, original cameras, and embedded Text blocks. It selects the existing `MARS_NEW_Globe_Camera` for opening so the planet is framed immediately.
3. Adds a single organizational collection named `FIELD SITE | Jezero (linked original assets)` with links to ten already-existing objects: `Mars_Terrain`, `White_Circle_Marker`, `White_Ring`, `Joe_Astronaut`, `Joe_JA`, `ludovisions_FC1_rig`, `Mars_Camera`, `MARS_NEW_Globe_Camera`, `MARS_NEW_Explore_Area_Pin`, and `MARS_NEW_Explore_Area_Ring`.
4. Adds geographic cross-reference custom properties to `Mars_Terrain`: latitude `18.42875° N`, longitude `77.44215° E`, and a note relating the local Jezero terrain patch to the existing globe exploration pin/ring. This is metadata, not a newly georeferenced 3D transform.
5. Saves to the screenshot’s expected filename, `MARS_SENTINEL_NASA_Terrain_Study.blend`, after preserving the previous variant in `archive/`.

It does **not** move the field site onto the globe, alter the globe’s scale, parent terrain to the pin, resize the ring, change the world/sky, run embedded scripts, or change the terrain shape-key value. It changes the active scene camera to the existing globe camera and saves the `Layout` viewport in camera view. The original camera objects and animation remain intact. A mathematically correct globe-to-local mapping still needs to be established before moving the local terrain.

## 5. Reopen verification results

`verify_mars_recovery.py` reopened the newly saved `.blend` in Blender 5.2.3 with automatic script execution still disabled and confirmed:

| Check | Observed result |
|---|---|
| Active scene | `Scene` |
| Scene count | 1 |
| Scene objects | 4,181 |
| Scene camera | `MARS_NEW_Globe_Camera` |
| World | `Mars_Sky_NASA` |
| Current frame | 112 |
| `Mars_Terrain` | present; retains original `Ground` membership and is additionally discoverable in the field-site collection |
| Linked field-site collection | 10 object links |
| Main operator/dashboard Text datablocks | `front_view_models.py` and `mars_dashboard.py` both present |
| Embedded scripts executed during verification | No; Blender printed “scripts disabled … skipping” |

Verification report: `../data/verify_MARS_SENTINEL_NASA_Terrain_Study.json`.

## 6. Terrain data investigation

### 6.1 Official products already present

- **HiRISE:** `../data/JEZ_hirise_soc_006_DTM_1m.tif`, a USGS Mars 2020 Terrain Relative Navigation HiRISE DTM mosaic. Local file size: **1,839,545,409 bytes**. Rasterio inspection earlier in this task found 21,400 × 21,488 float32 cells, 1 m native spacing, and Mars equirectangular georeferencing. Official product page: [USGS Mars 2020 TRN HiRISE DTM Mosaic](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_hirise_dtm_mosaic). Data release DOI: `10.5066/P9REJ9JN`.
- **CTX context:** `../data/JEZ_ctx_B_soc_008_DTM_20m.tif`, about 9.7 MB, 20 m/pixel product. Official page: [USGS Mars 2020 TRN CTX DTM Mosaic](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic). DOI: `10.5066/P906QQT8`.
- The USGS catalogue explains the Jezero products and their intended context/scale: [Mars 2020 Jezero Crater Landing Site Products](https://astrogeology.usgs.gov/search/map/mars-2020-jezero-crater-landing-site-products).

The high-resolution source is real data and was already downloaded. The fact that its TIFF is 1 m/pixel does **not** mean the current Blender scene is visibly displaying that raster as 1 m mesh geometry.

### 6.2 Derived analysis grids already present

`../data/build_hirise_grids.py` samples the official HiRISE raster into Blender-sized JSON grids while retaining source URL, DOI, CRS, window/crop offsets, geotransform, sample spacing, elevation min/max, nodata mask, and `vertical_exaggeration: 1.0`:

- `../data/jez_hirise_1m_overview_grid.json`: whole mosaic sampled every 40 m, 535 × 537 samples.
- `../data/jez_hirise_1m_detail_grid.json`: centered 4,096 × 4,096 m crop sampled every 4 m, 1,024 × 1,024 samples. The file records elevation range approximately **−2563.806 m to −2394.238 m** (span ≈ **169.567 m**) and valid data across this central crop.
- `../data/jez_ctx_20m_grid.json`: context grid sampled every 80 m.

The grid builder fills nodata sample positions with a median value for vertex placeholders but retains a validity mask and skips faces that cross invalid data. It does not claim these filled placeholders are measured terrain.

### 6.3 Existing terrain in the Blender source is flattened

The original `Mars_Terrain` has shape keys named `Basis` and `Flat_Ground`. Both were saved at value `1.0`. Read-only evaluated-bound checks on the recovery file found:

- Saved state: `Flat_Ground = 1.0`, evaluated Z span **0.0000** (flat surface).
- In-memory diagnostic only: `Flat_Ground = 0.0`, evaluated Z span about **1,341.0888 scene units**.
- The source object’s custom properties describe the local HiRISE patch elevation span as **163.386 m** and claim vertical scale 1:1, which is much closer to the raster-derived central crop (~169.567 m) than to the 1,341-unit shape-key result.

For that reason the recovery copy preserves the saved flattened state; blindly toggling the shape key would expose a surface with an unresolved discrepancy against the source DEM and could cause people/vehicles to float or sink. The native DTM is retained in `data/`; a safe next build is to regenerate one accurately georeferenced/local-coordinate 4 m or 8 m grid mesh from that GeoTIFF, check vertical datum and scale, then compare it side-by-side with the existing object. Do not call the existing shape key “verified 1:1 HiRISE relief” until reconciled.

### 6.4 User’s 2 GB question and downloaded data

The official USGS HiRISE TIFF has been downloaded at about 1.84 GB and is available locally. No second 2.048 GB 50 cm model-refined product was downloaded; the earlier attempt at the Refubium source was blocked by its bot check. The 50 cm alternative is not the same product as native stereo DTM; if evaluated later, keep it clearly distinguished from the official USGS HiRISE source and record its license/provenance. The current project therefore has the real, official 1 m DTM available without needing another 2 GB download.

## 7. Sky and starfield status

- The original world `Mars_Sky_NASA` already includes procedural stars, a Milky Way-like band, atmospheric haze, and a camera-ray mix that keeps sky appearance separate from world lighting. This was verified in the saved node graph: `Stars_Background` is mixed through `Camera_Stars_vs_Lighting`, driven by `Light Path Is Camera Ray`.
- The working file preserves this world. Its saved `Layout` opens at `MARS_NEW_Globe_Camera` in Material shading with scene world enabled, so the planet and sky are in the same integrated view.
- The stars are procedural, not actual catalogue positions. The separate image generated by `data/build_starfield.py` is also synthetic and remains associated with the archived study.
- The Workbench globe preview does not render the world shader, so its tan background is not a preview of the saved Material viewport. A full original render was too expensive; an EEVEE material render consumed high memory and was stopped before saving. The node graph is verified, but final rendered lighting is not.
- If a sky tied to real stellar positions is required, use ESA Gaia DR3 positions and photometry and validate orientation against known sky references. ESA documents `gaiadr3.gaia_source` in its [official data model](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dmdiff_dm_diffs/) and supports programmatic TAP access.

## 8. Previews produced and their limitations

These outputs are diagnostic Workbench renders. They prove scene contents/camera framing, **not** final material, Cycles, sky, or lighting quality:

- `../previews/recovered_preview_Mars_Camera.png`: surface camera view; central `MSL` mesh obstructs the subjects.
- `../previews/recovered_preview_MARS_NEW_Globe_Camera.png`: globe is visible in the camera frame; Workbench uses a plain display background.
- `../previews/recovered_preview_Mars_Orbit_View_Camera.png`: previous orbit-camera composition.
- `../previews/diagnostic_without_White_Ring.png`: in-memory test confirmed hiding `White_Ring` did not fix the surface-camera obstruction.
- `../previews/recovered_globe_texture_preview.png`: Workbench texture-mode preview from the current canonical file shows the globe’s Mars texture and existing small Jezero pin. Workbench does not render the world shader.
- `../previews/mars_globe_before.png` / `../previews/mars_globe_after.png`: previous isolated previews; the “after” includes synthetic stars.

An initial high-cost render of the original scene was stopped because it consumed substantial CPU/memory and did not produce an image in a reasonable window. A later EEVEE material-preview process reached roughly 13 GB working set without finishing; it was stopped before any blend save. The lower-cost Workbench previews completed in roughly 18–26 seconds per image. No render process is intended to be left running.

## 9. Tools, scripts, and MCP disclosure

Blender-specific MCP was not available in the connected tool inventory. Blender 5.2.3’s supported background Python interface was used instead. This gives direct read/write to the `.blend` data, but it is not UI automation and did not click or approve the user’s security dialog.

New scripts created for reproducible work:

- `../tools/restore_mars_scene.py` — rebuild canonical file from the untouched source, set globe-camera startup, and link existing site assets.
- `../tools/verify_mars_recovery.py` — reopen/report scene state, key values, and collection membership.
- `../tools/compare_terrain_shape_key.py` — in-memory-only flat versus relief bounds.
- `../tools/render_recovery_previews.py` — low-cost Workbench views; does not save the blend.
- `../tools/render_ring_diagnostic.py` — in-memory White_Ring visibility check.
- `../tools/diagnose_camera_occlusion.py` — center ray confirms `MSL` occludes `Mars_Camera`.
- `../tools/render_recovery_material_previews.py` — EEVEE attempt stopped for high resource use, with no blend save.
- `../tools/render_globe_texture_preview.py` — Workbench globe texture preview.
- `../tools/inspect_mars_blend.py` and `../tools/legacy/build_mars_study_legacy.py` — structural inventory and archived legacy builder.

No application messages were sent, no team data was published, and no test suite was run. This is a Blender scene recovery, source-data audit, static script review, and background structural check.

## 10. What is fixed, what is known, and what remains

### Fixed in the working file

- The original one-scene integrated project is restored as the default active scene in the exact filename shown in the user’s screenshot.
- The saved Layout workspace opens in camera view through `MARS_NEW_Globe_Camera`, with Material shading and the existing world enabled. This puts the globe, its point, and its procedural sky into one scene view.
- Astronaut, rover, camera, globe, white-circle, and terrain assets remain present and are discoverable in one collection without duplicating or relocating originals.
- The local terrain carries explicit geographic cross-reference metadata to the globe’s existing Jezero marker.
- The user’s original source file is preserved untouched.

### Confirmed, but not yet fixed

- Blender auto-run protection still blocks the registered scripts until the user chooses to trust/run them. Therefore custom key `1` may require user-side trust or manual script registration on opening the recovered copy.
- `Mars_Camera` is obstructed by `MSL`; it needs a new/adjusted overview composition.
- `Mars_Orbit_View_Camera` is not a polished globe/space composition in the structural preview.
- The world’s stars are procedural, not measured Gaia/catalogue positions; a Gaia-based starfield has not been built.
- `Mars_Terrain` is flattened at the saved shape-key state. Turning off `Flat_Ground` gives an unresolved 1,341-unit span, inconsistent with the central HiRISE crop’s ~169.6 m range.
- The 3D geographic relationship is only recorded as metadata; terrain and globe transforms have not been numerically reconciled and the local terrain was not physically reprojected onto the globe surface.
- The current full Blender source is hundreds of MB, and physically based full-scene rendering is resource-heavy. A lighter presentation/export scene still needs deliberate curation.

### Not done in this pass

- No astronaut/rover was deleted, re-modelled, reparented, or moved.
- No ring or white-circle object was hidden in the saved working file.
- No camera transform or animation was changed; only the active camera pointer and saved viewport were switched to the existing globe camera.
- No terrain geometry was replaced with the downloaded DTM, and no unsupported terrain relief was switched on.
- No real Gaia star catalogue was downloaded or integrated.
- No true physically based render was completed; the previews are not final presentation art.
- No coding/Unity/Three.js web export was created.
- No embedded Python code was executed, and Blender’s global security preference was not changed.

## 11. Recommended next steps, in safe order

1. Close the old loaded study without saving, then reopen the root `MARS_SENTINEL_NASA_Terrain_Study.blend`. The old content is in `archive/`; saving it from the old Blender window could recreate the broken version. The canonical file should open on the globe.
2. Clear any Outliner filter text. If Blender shows the script warning and you choose **Continue Safely**, the custom top-row `1` operator is not registered. The key binding is in the original Text script; after reviewing/trusting the project, choose **Allow Execution** for this file or run the script manually. Do not enable global auto-run for all blend files.
3. Reconcile `Mars_Terrain` shape-key geometry against `../data/JEZ_hirise_soc_006_DTM_1m.tif` and validate vertical range before integration.
4. Create a new surface overview camera framing MSL + astronauts + local terrain without changing existing camera animation.
5. Reconcile local Jezero coordinates and scale with the existing globe pin/ring before physically joining transforms.
6. If actual catalogue stars are required, integrate Gaia DR3 positions/photometry and verify their projection; keep current procedural stars as the visual fallback.
7. Test the custom `1` key and dashboard in the Blender GUI, then make an optimized GLB/Three.js scene for the web demo.

## 12. Reproducibility and source links

- Blender 5.2.3 LTS executable used: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
- Recovery source: `Mars_backup_before_quality_pass.blend`.
- Working file: `MARS_SENTINEL_NASA_Terrain_Study.blend`.
- HiRISE product: [USGS product landing page](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_hirise_dtm_mosaic), DOI `10.5066/P9REJ9JN`.
- CTX product: [USGS product landing page](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic), DOI `10.5066/P906QQT8`.
- Security behavior: [Blender Scripting & Security manual](https://docs.blender.org/manual/en/latest/advanced/scripting/security.html).
- Star catalogue follow-up: [ESA Gaia DR3 data model](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dmdiff_dm_diffs/) and [ESA Gaia Archive programmatic access](https://www.cosmos.esa.int/web/gaia-users/archive/programmatic-access).

## Append-only instruction for future agents — 2026-11-06

Preserve all existing text in `memo.md` and all other Markdown files. Add future investigation, decisions, file changes, and corrections as new dated sections at the end. Never replace this memo with a summary.

## 13. NASA surface color and exploration scene — 2026-11-06

The latest file before this pass was `MARS_SENTINEL_NASA_Terrain_Study_HIRISE_READY.blend` (6 Nov 2026, 20:05). Its site mesh used an elevation tint, not an orbital image. This pass did not edit vertex coordinates, object scale, or the saved transforms of `NASA_HiRISE_DTM_Jezero_FieldSite_4m` or `Mars_Terrain`.

### Color

- Brightness: USGS HiRISE orthomosaic `JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first.tif`, DOI `10.5066/P9QJDP48`, cropped to the same 4092 m vertex span as the 4 m mesh and sampled near 1 m/pixel. It is an 8-bit red-filter mosaic, not calibrated reflectance and not a three-band color image.
- Hue: NASA/JPL/USGS Viking MDIM 2.1 global color mosaic, 232 m. Jezero's own raw samples in that file are about DN 30 and blue-biased (blue DN above red). Bright control samples in the same file are consistently red > green > blue: Arabia Terra at 30 E, 20 N is DN (140, 103, 96), and Olympus Mons is DN (126, 89, 79). The surface hue uses the mean of those two bright samples. Direct Jezero DN chroma was not used.
- Equation: `RGB = clip(HiRISE_DN/255 * mean(Viking_bright_RGB) / Viking_bright_luma)`.
- A weak bump uses the existing DTM heights. It does not move vertices.
- Saved crops: `data/jez_hirise_site_hirise_red_1m.png`, `data/jez_hirise_site_nasa_color_1m.png`, `data/jez_hirise_site_height_4m.png`, `data/jez_site_color_provenance.json`.

### Files

- Color checkpoint: `MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend`.
- Scene with routes, markers, and animation: `MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend`.
- Open the exploration file. The startup camera is still `MARS_NEW_Globe_Camera` at frame 112.
- Preview: `previews/nasa_color_site_preview.png`.
- Reopen check: `data/verify_exploration_geometry.json`. Site vertex hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`, 1,132,096 vertices, location `(0.23, -0.49, 0.014996)`, scale `(1, 1, 1)`. `Mars_Terrain` remains at z `-54.84` with `Flat_Ground = 1`. `MSL` at frame 112 remains `(1.094, 14.027, 0.364)`.

### What the exploration file adds

- Measured materials on the site mesh: NASA color, elevation vertex colors, and slope vertex colors. Switch them with `tools/toggle_mars_layer.py` using `color`, `elevation`, or `slope`.
- Existing geology, temperature, dust, sunlight, elevation, and slope layer objects were hidden and marked illustrative or superseded. No CRISM, THEMIS, or dust raster was clipped, so those are not shown as NASA data. `Mars_Sun` and `Mars_Sky_NASA` stay. The sky is still procedural.
- Globe scale and location were not changed. Orbit and zoom remain viewport navigation. `MS_Tour_Camera` has a keyed orbit and a move to the site after frame 112.
- Routes `MS_Route_Safest_HiRISE` (15 degree block, 1143.31 m) and `MS_Route_Shortest_HiRISE` (28 degree block, 1135.24 m) are derived from the mesh slope. The science route uses the safest geometry because its destination is the landing site. These thresholds are project display rules, not a flight certification.
- Science pins: Octavia E. Butler Landing at 18.4447 N, 77.4508 E, and Wright Brothers Field at 18.44486 N, 77.45102 E. No ancient-water pin was added. The Jezero western delta is outside this 4092 m mesh.
- Twenty-seven slope markers mark local maxima at or above 15 degrees. `MS_Hazard_Warning` scales up during the later tour frames.
- `Joe_Astronaut` and the nearby rover roots are keyed along the routes after frame 112. Their frame-112 poses stay. `Wheels_objs` is one combined mesh, so it translates with the rover and is not spun on a false axle. `MS_Astronaut_Eye_Camera` is parented to Joe.
- Dust particles and the thermometer, wind sensor, sample tube, and environment-station markers are labeled illustrative.

### Tools

`tools/build_jezero_surface_color.py`, `tools/recolor_from_hirise_red.py`, `tools/apply_nasa_color_and_exploration.py`, `tools/verify_exploration_scene.py`, `tools/render_nasa_color_preview.py`, `tools/toggle_mars_layer.py`.

The untouched source `Mars_backup_before_quality_pass.blend` was not modified. Embedded blend scripts were not executed.

## 14. Number 1 view shortcut — 2026-11-06

Pressing `1` did not frame the crew because Blender skips the embedded `front_view_models.py` unless script execution is allowed. The crew objects are present and visible. The same framing operator is now installed as a Blender startup script for 5.2 and 5.4: `scripts/startup/mars_front_view.py`, with a project copy at `tools/mars_front_view.py`. It binds the top-row `1` and the numpad `1` in the 3D View. In this scene it frames the six crew roots. In other files it falls back to the normal front view. Blender must be restarted once so the startup script loads. Global auto-run of blend scripts was not enabled.

## 15. Handoff for the next session — 2026-11-06

Sections 13 and 14 are the detailed record. The same facts were appended, without replacing older text, to `README.md`, `INDEX.md`, `3D_ASSETS_README.md`, `PRD.md`, and `MEMORY.md`.

Resume from `MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend`. Do not modify `Mars_backup_before_quality_pass.blend`. Keep the site mesh at 1,132,096 vertices, scale `(1, 1, 1)`, location `(0.23, -0.49, 0.015)`, hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`, and keep `Mars_Terrain` flat at z `-54.84`.

Still true at this handoff: the file opens on `MARS_NEW_Globe_Camera` at frame 112; key `1` includes the 27 m `ludovisions_FC1_rig`; the color hue is one Viking bright-site tint rather than local RGB; the safest and shortest routes differ by about 8 m. Those four items are the agreed next pass and are not done in this section.

## 16. Readable opening view, local color, and separated routes — 2026-11-06

Section 15 is the state before this pass. This section is the pass itself. `MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend` was not overwritten. The new file is `MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend`. `Mars_backup_before_quality_pass.blend` was not modified.

Reopened check: site mesh still 1,132,096 vertices, scale `(1, 1, 1)`, location `(0.23, -0.49, 0.014996)`, hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`. `Mars_Terrain` remains flat at z `-54.84`. `MARS_NEW_Globe_Camera` was not moved. The Layout view and the scene camera are now `MS_Surface_Opening_Camera`. The saved frame is 361, the frame where Joe stands about 32 m from the rover. On frame 112 Joe is already about 1 km away at the landing pin, so a camera there cannot show Joe, the crew, and the rover together.

Key `1` in `tools/mars_front_view.py`, and in the Blender 5.2 and 5.4 startup copies, skips any mesh larger than 8 m. That excludes `ludovisions_FC1_rig`. It then keeps the human-scale crew cluster within 50 m of the median center, and adds `White_Circle_Marker` or `White_Ring` only when that marker is within 50 m and no wider than 40 m. Restart Blender once so the startup script replaces the previous one.

Local color is HiRISE merged RGB observation `ESP_045994_1985` (`ESP_045994_1985_MRGB.JP2`), approximate true color, not IRB. Credit NASA/JPL-Caltech/UArizona. Public domain. There is no DOI on the observation label. The BG color CCDs cover about 40.8 percent of this 4096-pixel window, through the middle of the mesh. Outside that strip, and on null pixels, the earlier HiRISE-brightness plus Viking bright-site hue remains. The product is a NORMAL_STRETCH relative DN, so the strip looks gray-green rather than the orange Viking tint. Provenance: `data/jez_site_local_color_provenance.json`. Image: `data/jez_hirise_site_local_rgb_1m.png`.

Routes were rebuilt on the 4 m slope grid, sampled at 8 m cells. Shortest may cross moderate slope and blocks only cells at or above 28 degrees: 1113.50 m, elevation change 5.55 m, sampled max slope 7.08 degrees. Safest blocks cells at or above 15 degrees and stays 48 m clear of them: 1159.95 m, elevation change 5.55 m, sampled max slope 6.49 degrees. The widest gap between those two lines is 67.88 m. The 15-degree patch on the straight line is only about 16 m across, so the clearance is what makes the detour readable. Science goes through Rochette, the published Perseverance sample locality for Montdenier and Montagnac, at 18.43074 N, 77.44435 E, then on to Octavia E. Butler Landing: 1203.21 m, elevation change 5.55 m, sampled max slope 6.80 degrees. The coordinate is from a compiled landmark list, not a NASA DOI. It is not an ancient-water or mineral pin. The western delta stays unpinned. The 15-degree rule is a display rule, not a flight certification. Old `RoutePlan` curves stay in the file and are marked as the earlier illustrative routes. Preview of the opening camera: `previews/surface_opening_preview.png`. Wider view of the split: `previews/route_separation_preview.png`.

## 17. Opening shot tightened — 2026-11-06

Section 16 left the routes as 2.6 m tubes, the work-area ring at a 40 m bevel, the camera far from the crew, and Joe already at the landing on frame 1. That file stays as `MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend`. The corrected file is `MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend`.

The site hash is still `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`. `MARS_NEW_Globe` and `MARS_NEW_Globe_Camera` were not moved. The three route curves are 0.36 m across and sit on the surface. `White_Circle_Marker` is hidden from the view and the render; the curve is still in the file. The opening frame is 76, which is when the existing reveal keys turn the rover and crew on. Joe is beside the rover there, at about `(4.3, 12.4, 0.2)`, and he reaches Octavia E. Butler Landing on frame 458. The surface camera is about 7 m from the rover, with depth of field off and a clip of 80 m so the globe stays outside that shot. The color-strip edge is a 30 m blend into the earlier tint. Preview: `previews/surface_focus_opening.png`.

## 18. Walk on the same file — 2026-11-06

Section 17 is the tightened opening shot. This pass edited `MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend` in place. No new blend was written. `READABLE` stays the rollback, and the backup blend was not touched. The site hash was checked before the save and is still `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`.

`Sketchfab_model` is the only human-scale rig with a walk cycle: armature `Object_4`, action `Mixamo Walk`, 72 bones, cycle 45.6 frames. That action is now an NLA loop. The empty follows the green route `MS_Route_Safest_HiRISE` from its own start at frame 100, at 1.4 m per cycle so the steps match the distance. The path is about 1190.7 m including the short join from where he stood, 852 samples, and the scene ends at frame 38906. Joe has no armature, so his body is still a sliding empty; those bones were not copied onto him.

Joe stays beside the rover through frame 1514, after the walker is 25 m away, then his existing landing keys continue. The old frame-458 landing key moves with that hold. `MSL` and `Wheels_objs` are held at their frame-76 pose for the whole timeline. The wheels are still one mesh and are not spun. Previews: `previews/surface_walk_open.png` at frame 76 and `previews/surface_walk_step.png` at frame 500.

