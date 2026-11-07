# Mars 3D Study — Data and Build Notes

> **IMPORTANT — ALL AGENTS: APPEND ONLY.** Never delete, overwrite, truncate, or rewrite any existing Markdown content. Add dated notes at the end and append corrections while retaining earlier history. Follow [`../AGENTS.md`](../AGENTS.md).

> **Recovery status (6 Nov 2026):** Open [`../MARS_SENTINEL_NASA_Terrain_Study.blend`](../MARS_SENTINEL_NASA_Terrain_Study.blend). It has one integrated scene and opens through the globe camera. The old isolated-scene version is kept under `../archive/`. Read [`memo.md`](memo.md) for verified status and remaining work. The built-in `Mars_Sky_NASA` stars and the separate generated starfield are procedural visuals, not measured catalogue stars.

The project root contains the untouched source backup and the current integrated working file. The previous broken study and its `.blend1` backup are preserved under `../archive/`.

## Earlier experimental scenes (not the recovered workflow)

- `MARS_Globe_Realistic_Starfield`: a copy of the supplied Mars globe, with a packed equirectangular World starfield and a camera-facing starfield crop behind the orbital composition. The star distribution is procedural and illustrative; it is not a measured stellar catalog.
- `NASA_Jezero_CTX_DTM_20m`: a Jezero surface derived from the USGS Mars 2020 CTX DTM. The source is 20 m/pixel. The Blender mesh is sampled at 80 m to keep the scene responsive.
- `NASA_Jezero_HiRISE_1m_Regional_Overview`: an overview from the USGS Mars 2020 TRN HiRISE DTM, sampled at 40 m for display.
- `NASA_Jezero_HiRISE_1m_Detail`: a 4 km square crop from the same HiRISE source, sampled at 4 m for a detailed Blender mesh.

All terrain meshes use the source elevation values with vertical exaggeration 1:1. Mesh positions are local, centered around zero for Blender navigation; source bounds, raster transform, crop offsets, DOI and URL are recorded in object properties and an embedded provenance text block. Elevation tinting is a visualization ramp, not a measured color image.

## Data sources

- USGS Mars 2020 TRN CTX DTM, 20 m/pixel, DOI `10.5066/P906QQT8`: [USGS product page](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic)
- USGS Mars 2020 TRN HiRISE DTM Mosaic, 1 m/pixel, DOI `10.5066/P9REJ9JN`: [USGS product page](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_hirise_dtm_mosaic)
- Direct HiRISE GeoTIFF: `https://asc-pds-services.s3.us-west-2.amazonaws.com/mosaic/mars2020_trn/HiRISE/JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40.tif`
- HiRISE metadata XML: same S3 folder and filename ending in `.xml`.

The 1 m HiRISE raster is a stereo-derived USGS elevation product supporting Mars 2020 Terrain Relative Navigation. Do not describe its downsampled Blender mesh as 1 m geometry: the full-resolution TIFF is retained separately, while overview and detail meshes use 40 m and 4 m vertex spacing.

## Regeneration

1. Run `py -3.14 data/build_terrain_grid.py` to create the compact CTX grid JSON.
2. After `data/JEZ_hirise_soc_006_DTM_1m.tif` has downloaded and its size is verified, run `py -3.14 data/build_hirise_grids.py`.
3. The old builder is archived at `../tools/legacy/build_mars_study_legacy.py`. It creates the previous isolated-scene experiment and should not be run as the current workflow. For the integrated project, use `../tools/restore_mars_scene.py` only when deliberately rebuilding from the untouched source.

The 1.84 GB HiRISE source is large but Blender only imports sampled grids; it does not turn the entire TIFF into a dense Blender mesh.

## Agent work-log instruction — 2026-11-06

All future changes to this Markdown file must be added as dated sections at the end. Preserve every existing line, link, and note.

## Integrated site color — 2026-11-06

Open `../MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend`. The color checkpoint is `../MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend`. `../Mars_backup_before_quality_pass.blend` stays untouched.

`NASA_HiRISE_DTM_Jezero_FieldSite_4m` is the 4 m mesh, 4092 m across, 1,132,096 vertices, scale `(1, 1, 1)`, location `(0.23, -0.49, 0.015)`, hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`. `Mars_Terrain` remains the flat underlay at z `-54.84`.

The base color uses HiRISE red-filter brightness from `JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first.tif`, DOI `10.5066/P9QJDP48`, sampled near 1 m across the vertex span. The hue is the mean of Viking MDIM 2.1 bright controls at Arabia Terra (DN 140, 103, 96) and Olympus Mons (DN 126, 89, 79). Jezero's own Viking DNs are about 30 and blue-biased, so they were not used as the hue. Crops and the written equation are in `../data/jez_site_color_provenance.json`. The elevation bump does not move vertices.

Routes on the mesh: safest 1143.31 m at a 15 degree block, shortest 1135.24 m at a 28 degree block. The science curve currently repeats the safest geometry. These lengths are too close to read as a real choice. The file still opens on the globe camera at frame 112. Key `1` still includes the 27 m `ludovisions_FC1_rig`. No local RGB replacement, no opening surface camera, and no separated routes have been saved yet.

## Readable scene — 2026-11-06

Open `../MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend`. Geometry of `NASA_HiRISE_DTM_Jezero_FieldSite_4m` and `Mars_Terrain` matches the exploration file, including hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`.

The replacement image is `../data/jez_hirise_site_local_rgb_1m.png`, cropped from HiRISE merged RGB `ESP_045994_1985_MRGB.JP2` onto the same bounds as the earlier 4096-pixel tint. Only the center color strip replaces that tint. Record: `../data/jez_site_local_color_provenance.json`.

The three measured curves are thicker and no longer share one shape. Shortest 1113.50 m, safest 1159.95 m with a 48 m clearance from slope at or above 15 degrees, science 1203.21 m through Rochette. `RoutePlan` is still present and marked as the earlier illustrative pair. The opening camera frames the crew at frame 361. Key `1` no longer targets the 27 m rig. See `memo.md` section 16.

## Walk on the same file — 2026-11-06

`../MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend` is now the file that gets edited. The mesh hash is unchanged. `Sketchfab_model` / armature `Object_4` plays the existing `Mixamo Walk` action in a loop and the empty advances 1.4 m per 45.6-frame cycle along `MS_Route_Safest_HiRISE`, starting at frame 100. Joe has no rig, so he still slides on his empty after frame 1514. `MSL` and `Wheels_objs` stay at the frame-76 pose. The wheel mesh is not spun. See `memo.md` section 18.
