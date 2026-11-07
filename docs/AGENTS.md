# Mandatory project instructions for all agents

> **IMPORTANT — APPEND ONLY:** Never delete, overwrite, truncate, or rewrite existing content in any `.md` file in this project. Preserve all existing lines. Add new information as a dated section at the end of the relevant file. If correcting an earlier statement, append a dated correction that explains what changed and why; keep the earlier record intact. Apply this rule to `MEMORY.md`, `memo.md`, `PRD.md`, README files, and every other Markdown document.

Before editing project documentation, read `docs/INDEX.md` and the relevant file in full. Do not replace a document with a summary. If more context is needed, create a new dated appendix and link it from the index without removing existing text.

## Blender and scientific-data guardrails

- Preserve `Mars_backup_before_quality_pass.blend` as the untouched source. Work on `MARS_SENTINEL_NASA_Terrain_Study.blend` or make a separate named copy.
- Never report a generated/procedural visual as a measured NASA/ESA product. Cite source product, DOI, resolution, CRS, vertical reference, resampling, no-data treatment, and mesh exaggeration.
- Do not run embedded Blender Python automatically. Review the specific code and keep Blender’s global auto-run security setting off.
- Keep existing objects and document additions/replacements; do not delete project assets or historical documentation.
- Record every material edit, render, data transform, and limitation in a dated section appended to `docs/memo.md` and `docs/MEMORY.md`.
