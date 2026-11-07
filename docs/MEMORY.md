# MARS SENTINEL — Project Memory / Source of Truth

> **IMPORTANT — ALL AGENTS: APPEND ONLY.** Do not delete, overwrite, truncate, or rewrite any existing content in `MEMORY.md` or any other Markdown file. Append a dated section at the end for new facts and corrections. Preserve older context and explain corrections rather than silently replacing it. Follow [`../AGENTS.md`](../AGENTS.md).

> **Purpose.** A durable working memory for the NASA Space Apps 2026 effort: what is known, what the team has proposed, what exists in this workspace, decisions, links, scope, and a faithful in-repository record of the PRD and team discussion. It is deliberately more useful than a chat transcript: it separates evidence from assumptions.
>
> **Last consolidated:** 6 November 2026 (Africa/Cairo; Blender file inspected read-only).  
> **Status:** planning; no application source code is present in this workspace yet.  
> **Working product:** `MARS SENTINEL`.

## 0. How to use this document

- **Verified** means checked against a primary/official source on the consolidation date.
- **Team proposal** means it came from the team/PRD or an earlier assistant response; it must not be presented as an official rule until confirmed in the Space Apps portal.
- **Demo / illustrative** data or 3D props must be visibly labeled as such. Never show generated rocks, weather, or values as NASA measurements.
- The official challenge brief and its Resources tab are the final authority. The exact Martian Map URL was inaccessible to automated retrieval (HTTP 502) on 6 Nov; open it manually while signed in before locking data, judging criteria, or submission limits.

## 1. Fast orientation: the decision that prevents scope collapse

**Build a decision-support web experience, not a whole Mars game.** The demo should tell one complete, defensible story:

1. Open a real, bounded area in Jezero Crater.
2. Select a start and a science destination.
3. Show real elevation/imagery and two or three clearly attributed layers.
4. Calculate and compare shortest, safest, and science-value routes.
5. Explain every route’s risks, data age/resolution, and Safety Score.
6. Let the judge see the result in 3D and inspect sources.

The strongest differentiator is **explainable trust**: a reproducible route, its component costs, a data manifest, and clear uncertainty/coverage labels. A rover, astronaut, dust, sky, VR, hologram, and full-planet experience are visual enhancements only; they cannot block the vertical slice above.

## 2. Competition record (officially checked)

| Fact | Record |
| --- | --- |
| Event | [NASA Space Apps Challenge](https://www.spaceappschallenge.org/) |
| 2026 dates | **14–15 November 2026** — stated on the official [2026 announcement](https://www.spaceappschallenge.org/blog/explore-the-next-frontier-at-the-2026-nasa-space-apps-challenge/) and [About page](https://www.spaceappschallenge.org/about/). |
| Registration | Official announcement says registration remains open through the end of the hackathon; choose/change a local event in the account. |
| Team size | A 2026 local-event FAQ says **2–6 members**. Confirm the rule for the team’s selected event/account before submission. |
| Selected challenge (team working selection) | **Interplanetary Survival Guide: Martian Map** — [team-supplied URL](https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/). Its availability/content was not independently fetchable on 6 Nov, so the title, brief interpretation, final rubric, deadline, video/slides limit, and prizes remain **to verify in portal**. |
| 2026 theme | “The Next Frontier” according to the official announcement. |

### Critical verification checklist (do this before implementation and again before submit)

- [ ] Each of the six people is registered for the **same** Local/Universal Event.
- [ ] The portal accepts six members for that specific event and records the final team name.
- [ ] Read the challenge brief and Resources tab directly; save a PDF/screenshot/version date.
- [ ] Confirm deliverable fields, allowed links, video duration, submission cutoff/time zone, English requirements, and AI disclosure requirements.
- [ ] Confirm every external asset’s license and NASA attribution wording.
- [ ] Open the deployed app, video, repository, and presentation from a logged-out/private browser.

## 3. The product

### Problem and outcome

Mars terrain, imagery, environmental records, and science targets live across missions and data formats. A planner needs an auditable way to choose a walk that is safer **and** scientifically useful, especially when data coverage and freshness differ. MARS SENTINEL turns a small, real Jezero area into a 3D planning view with comparative routes, hazards, scientific waypoints, and evidence.

### Target users

| User | Need | Product response |
| --- | --- | --- |
| Mission planner | Compare feasible routes quickly | Three routes, distance/time/max-slope and cost explanation |
| Astronaut / field operator | Understand exposure and uncertainty | Hazard callouts, terrain preview, conditions metadata, offline-ready demo data |
| Planetary scientist | Reach relevant targets with provenance | Science waypoints with rationale, source, date, coverage, confidence |
| Judge | Understand value in minutes | One-click scenario, clean presentation, About Data page |

### In scope for the R0 demo

- One AOI in **Jezero Crater**, bounded small enough for fast downloads and 30 FPS.
- Real terrain or imagery provenance; elevation-derived slope; two further usable layers at minimum.
- Start/destination picking, valid-area validation, shortest/safest/science route variants, waypoints.
- Hazard map based on documented, tunable rules; route cards and Safety Score decomposition.
- Conditions panel that always names source, observation date/sol, distance/context, and whether it is historical—not “live”.
- Three scientific waypoints with source-backed rationale.
- 3D terrain, camera controls, layer toggles, source/metadata page, working deployed demo.

### Explicitly out of scope unless R0 is complete

- Whole-Mars coverage; live weather claims; real astronaut life-support physics; accounts/database.
- Hand-built rover/astronaut/equipment models; custom shaders/particles; VR/holographic hardware.
- An unvalidated “optimal” mission recommendation. This is a **prototype decision-support tool**, not flight software.

## 4. Team, ownership, and unresolved names

The conversation contains six names: **مؤمن (Momen), يوسف حسن (Youssef Hassan), يوسف محمد (Youssef Mohamed), مريم (Mariam), أسماء (Asmaa), إسراء (Esraa)**. Earlier prose says “five,” but six is within the cited 2–6 cap. Do not remove someone merely because of that older sentence.

| Workstream | Named owner(s) | Definition of done |
| --- | --- | --- |
| Frontend + Backend | **Youssef Hassan + Youssef Mohamed**, pair on Angular/Spring | Dashboard talks to stable API; invalid input is gracefully handled; demo mode survives API failure |
| 3D | Momen | Terrain view, controls, route/hazard rendering, performant fallback |
| Navigation & hazards | Esraa | Grid/cost model, A*, test cases, safety-score explanation |
| Data & research (proposed; needs sign-off) | Asmaa | AOI, licensed data pack, metadata/manifest, scientific waypoint evidence |
| Integration, QA, security, presentation | Mariam | scenario, test checklist, input/API validation, demo/pitch, final submission |

**Original role descriptions retained:** Esraa was assigned start/destination, A*, shortest-vs-safest comparison, slope/rock risk, waypoints, distance/ETA, and route data for 3D. Mariam was assigned integration, data/source review, error/missing-data testing, API security/input validation, demo/presentation, and progress coordination. Momen’s requested 3D work includes globe, terrain, camera/lighting, rover/astronaut/equipment, movement, and interactive routing; it is now prioritised below the route vertical slice.

## 5. Architecture decision record

### Recommended build (professional but hackathon-sized)

```text
Angular 22 SPA ── REST/JSON ── Spring Boot 4.1 API (Java 25)
       │                           │
       ├─ Three.js renderer         ├─ route/hazard service (A*)
       ├─ service worker/cache      └─ static terrain-pack manifest
       │
       └─ preprocessed static assets: DEM / images / GeoJSON / JSON
                   ↑
          Python offline pipeline (GDAL/rasterio/NumPy)
                   ↑
     NASA/PDS/Mars Trek/HiRISE sources, all captured in a manifest
```

| Layer | Decision | Why / guardrail |
| --- | --- | --- |
| Web UI | Angular 22, TypeScript, standalone components, Signals, Angular CDK; CSS/Tailwind only if the team already knows it | Fits the team’s Java/Angular direction and makes a strong dashboard. [Angular v22 is supported](https://angular.dev/reference/releases); its current install guide requires Node 22.22.3+. |
| 3D | Three.js directly behind a small `SceneAdapter` interface | A custom adapter avoids coupling domain state to rendering. Load a terrain mesh/height map, not millions of independent objects. |
| API | Spring Boot **4.1.x**, Java **25**, Maven, Spring Web + Validation + Actuator | Official docs list Boot 4.1.2 and compatibility with Java through 27. Keep it a modular monolith; no microservices. |
| Routing | Start A* in Java. Use an 8-neighbour grid with deterministic tie-breakers and a cost breakdown per edge. | Keeps core logic testable and appropriate for Esraa/Backend ownership. TypeScript offline routing is P1 only. |
| Data pipeline | Python 3.12+, GDAL/rasterio, NumPy, GeoPandas only when needed | Preprocess once; browser/API consumes a small fixed pack. Never raster-process huge remote NASA files during the demo. |
| Format | GeoTIFF/COG during processing; exported PNG/WebP texture + quantised grid/JSON/GeoJSON at runtime | Fast, portable, easy to cache. Include CRS/axis/units in manifest. |
| Deployment | Static Angular hosting + a small HTTPS Spring service; bundled **Demo Mode** route responses | Host choices are intentionally not locked. Do not add a database unless a requirement appears. |
| Testing | JUnit for A*/score, Angular unit tests, Playwright one happy-path E2E, data-pipeline validation | A demo is only believable if the known route fixtures always work. |

### Contracts to lock before parallel coding

`POST /api/routes` input: `{ start, destination, profile }` where points use one explicit Mars coordinate convention and pack ID. Output: three route objects with `coordinates`, `distanceM`, `etaMinutes`, `maxSlopeDeg`, `riskBreakdown`, `scienceScore`, `safetyScore`, `warnings`, `dataPackVersion`.

`GET /api/aoi`, `/layers`, `/science-sites`, `/manifest` return immutable, versioned data. Invalid coordinates/profile return HTTP 400 with RFC 9457 Problem Details. Never leak Java stack traces. The client should render pre-bundled scenario JSON when API health fails, with a visible **Demo Mode** badge.

### Route and score model (must be visible, not magic)

For grid edge `u → v`, use a documented cost such as:

`baseDistance × (1 + wSlope·penaltySlope + wRough·roughness + wHazard·hazard + wThermal·thermal)`.

- **Shortest:** minimise geometric distance, while still forbidding truly impassable cells.
- **Safest:** maximise avoidance / minimise full hazard cost.
- **Scientific:** safe-cost route with a bounded reward for passing documented science sites; never allow science reward to overcome forbidden cells.
- A normalised score can be `100 − weighted penalties`; expose all weights, thresholds, coverage, and “estimated” label. Calibrate only within this AOI; do not imply a real human safety certification.

## 6. NASA / scientific data plan

| Need | Preferred source | Practical use and caution |
| --- | --- | --- |
| Base terrain / visual map | [Mars Trek](https://trek.nasa.gov/mars/) + [WMTS API](https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars) | NASA’s tile service exposes MOLA, THEMIS, roughness and other layers. Cache/download an AOI, do not depend on a network tile request during judging. |
| Elevation + slope | MGS/MOLA; local [HiRISE DTM](https://hirise.lpl.arizona.edu/dtm/about.php) only if coverage exists | Derive slope yourself, record resolution/resampling and no-data policy. HiRISE DTMs are PDS-released but are not universal coverage. |
| Imagery / rocks context | HiRISE, CTX via [PDS ODE](https://ode.rsl.wustl.edu/mars2/) | ODE searches downloads across MRO/Mars Odyssey/MGS/Mars Express etc. “Rock hazard” needs validation—do not infer it from pretty imagery alone without labeling it. |
| Thermal / surface context | THEMIS IR via Mars Trek/PDS ODE | Use it as a historical orbital layer, not real-time human temperature. |
| Weather context | Perseverance MEDA/PDS | MEDA measures wind, pressure, humidity, ambient temperature and solar radiation; show measurement time/sol and rover locality. |
| Minerals / science targets | CRISM via PDS ODE | State whether waypoint interpretation is an estimate and cite the product/observation. |
| Rover traverse comparison (P1) | [NASA AMMOS MMGIS](https://github.com/NASA-AMMOS/MMGIS) / Mars 2020 data | A back-test is compelling only after coordinate systems and time/version are reconciled. |

### Data-manifest minimum schema

Every shipped asset needs: `id`, `layer`, `mission/instrument`, `sourceUrl`, `productId`, `acquiredAt`, `downloadedAt`, `license/attribution`, `CRS`, `horizontal/vertical units`, `nativeResolution`, `runtimeResolution`, `AOI bbox`, `processingSteps`, `sha256`, `coverage`, `limitations`, and `illustrative: true|false`.

### Data pipeline acceptance gates

1. AOI boundary, longitude convention, datum and meters-per-pixel are chosen once and written down.
2. Clip every source to AOI; reproject/resample consistently; preserve no-data masks.
3. Derive slope/roughness; generate a small blocked-cell/hazard raster with documented thresholds.
4. Produce texture/mesh/grid/waypoint exports and manifest checksums.
5. Verify no NaN/out-of-range cells, grid alignment, coordinate round-trip, checksum, licensing, and displayed source text.
6. Bundle one known scenario and expected outputs so it works offline.

## 7. 48-hour execution plan and critical path

| Time | Non-negotiable outcome | Parallel owners |
| --- | --- | --- |
| 0–2 h | Confirm portal brief, AOI, data availability, schema, Git workflow, one route fixture | Mariam/Asmaa + all |
| 2–6 h | Thin vertical slice: terrain view + mocked fixed route + API contract | Momen; Youssef H/M; Esraa |
| 6–14 h | Real pack/slope/hazard grid; real A*; dashboard consumes contract | Asmaa, Esraa, Youssefs |
| 14–24 h | Three comparative routes + score breakdown + sources + one-click scenario | all integration |
| 24–32 h | Science sites/conditions, errors, performance and deployed preview | Asmaa/Mariam/3D/Frontend |
| 32–40 h | Polish demo story; only then P1 animation/offline verification | all |
| 40–48 h | Feature freeze, private-window test, video/slides, submission buffer | Mariam + everyone |

**Kill order if behind:** whole-globe transition → astronaut/rover animation → dust/sky/equipment → VR/hologram → offline A* → real traverse back-test. Do not cut source attribution, data validity, routing, or demo fallback.

## 8. Quality, security, and delivery bars

- Load target <5 s on a normal laptop; 3D >=30 FPS; route response <2 s for fixed AOI.
- Browser target: current Chrome/Edge/Firefox desktop; test keyboard access, contrast, labels, and non-colour warnings.
- CSP/HTTPS in deploy; no keys in frontend; validate all request payloads; dependency audit; health endpoint; structured request IDs.
- A manifest mismatch must show data as invalid and prevent dependent calculations (P1 if time is tight).
- All P0 requirements have a manually repeatable acceptance test; route algorithm has unit tests; deployment has a static fallback route.
- English is the submission language unless portal says otherwise. Arabic/RTL is an optional enhancement, not a core risk.

## 9. Workspace inventory (observed 6 Nov 2026)

| Path | State | Meaning |
| --- | --- | --- |
| `PRD.md` | Existing, 247 lines | Original product requirements, consolidated below in Appendix A. |
| `Mars_backup_before_quality_pass.blend` | Existing, 719,807,125 bytes (~686 MiB), modified 6 Nov 2026 14:07 | Read-only inspected with Blender 5.2.3; detailed findings in Appendix C. It is a real, extensive scene source, but not a deployable web asset. |
| Application code/config/README | **Not observed** | Scaffold after the team approves the architecture and AOI. |
| `MEMORY.md` | This file | Project memory, not a replacement for tested code or official portal rules. |

## 10. Conversation archive and ideas retained

### The team vision (from Mariam’s pasted message)

The desired experience is an interactive Google-Earth-like 3D visualization, potentially “holographic” in feel: pick any planetary point and see terrain/elevation, temperature, geology/elements, dryness and other contextual information. It should be responsive rather than merely scaling to mobile, laptop, and possible future VR. Future extensibility toward VR, rover/robotic integration and holographic displays was proposed—**architecture direction, not a required hackathon deliverable**. The message asks for a Zoom meeting to prioritise the design and feature set, with an ambition to compete seriously rather than only experiment.

### Original 12-stage 3D wishlist (preserved, reprioritised)

1. Mars globe and exploration marker. 2. Terrain: mountains, craters, valleys, dunes, boulders, slopes, plains and paths. 3. Switchable elevation/slope/geology/temperature/dust/sun layers. 4. Astronaut model and first-person mode. 5. Rover, wheels/camera/arm/antenna. 6. Scientific equipment. 7. Scientific points/markers. 8. Hazard detection/callouts. 9. 3D routes, waypoints and movement. 10. Mars sky/sun/shadows/dust. 11. Camera/astronaut/rover/environment interactions. 12. Final integration/performance testing.

**Correction:** this is a feature catalogue, not a safe serial execution order. Build routing/hazards/data/UI concurrently and demonstrate a working vertical slice early. The 3D team can use existing licensed GLB assets after the core terrain route works; do not model items from scratch.

### Earlier assistant-generated challenge catalogue

The first pasted chat contains Arabic summaries/URLs for 14 alleged 2026 challenges (e.g., Abandoned but not Forgotten, Junior Astronaut Trainer, Earth Information Jukebox, CLPS Browser, Health Monitoring, Martian Map, Flame in Freefall, Field Shift, Earth analog locations, Trend Detective, Dancing with SARs, MODIS/VIIRS, Planet X/SPHEREx). Treat it as **unverified research notes**, not an official challenge list: its stated release date/details were not independently confirmed here. The team has chosen Martian Map as the working focus, so it is intentionally not reproduced as a competing implementation plan.

### AI subscription discussion retained as a decision note

An earlier answer claimed Claude Free did not include Claude Code and recommended starting with a Pro plan for a 48-hour hackathon, upgrading one heavy user only if limits are hit. That pricing/availability is temporal and was not verified in this consolidation; do not purchase based solely on that historic note. AI assistance is optional and must be disclosed/used in line with the final competition rules.

### Original source locations (read-only record)

- First pasted conversation: current attachment `C:\Users\yhsn5\.codex\attachments\80a7df87-96e7-4ab0-81b8-c0c718c42a18\Pasted text.txt`; earlier copy `C:\Users\yhsn5\.codex\attachments\3d03ab09-571c-437c-88c5-36b27f4106dd\Pasted text.txt`.
- Role/3D-plan conversation: current attachment `C:\Users\yhsn5\.codex\attachments\86a00dcc-6c5d-49f5-91a2-55ae37bb1bcd\Pasted text.txt`; earlier copy `C:\Users\yhsn5\.codex\attachments\a4833cd5-c43d-4e80-b892-a7694c247e8a\Pasted text.txt`.

## 11. Open decisions—assign in the next meeting

| ID | Decision | Owner | Exit criterion |
| --- | --- | --- | --- |
| OD-01 | Final AOI and coordinate convention | Asmaa + Esraa | Small AOI with all P0 data and a route fixture |
| OD-02 | Final team name, event and registration | Mariam | Portal screenshot / team record |
| OD-03 | Verify selected brief, rubric and submission constraints | Mariam + all | Link/snapshot and checklist stored |
| OD-04 | Approve RACI and Frontend/Backend pair workflow | Youssef H + Youssef M + team | Owners agree to API contract and review rhythm |
| OD-05 | Hosting plan and static Demo Mode | Youssefs | Public preview exercises happy path |
| OD-06 | Asset licensing/export strategy for `.blend` | Momen + Mariam | License record; optimised web asset under budget |
| OD-07 | Scoring thresholds/weights and science points | Esraa + Asmaa | Tested/configured JSON with citations and limitations |

---

# Appendix A — Consolidated PRD record (v2.0, 1 Nov 2026)

This appendix preserves the operative content of `PRD.md` inside the project memory. `PRD.md` remains the original canonical source file; update both only through a reviewed decision.

## A1. Document metadata and change log

| Field | Value |
| --- | --- |
| Product | MARS SENTINEL |
| Challenge | Interplanetary Survival Guide: Martian Map |
| Version/status | 2.0 / draft for team review |
| Last update / proposed owner | 1 Nov 2026 / Mariam, integration & product |
| Reviewers | Youssef Hassan, Youssef Mohamed, Esraa, Momen, Asmaa |
| Proposed deadline | Sunday 15 Nov 2026 23:59 local event time — **verify in portal** |

Changes: v1.0 (31 Oct) was the first idea/requirements draft. v2.0 (1 Nov) reorganised it toward an enterprise PRD: acceptance criteria, NFRs, traceability, and Angular/Spring/Java. Priority convention: P0 required; P1 important if time permits; P2 polish only.

## A2. Goals, non-goals, success metrics

Goals: one AOI/route using layers from >=3 missions; explain three comparable routes; show conditions/hazards/science stops; deterministic explainable score; data trust/offline aspiration; public end-to-end delivery. Non-goals: whole Mars, precise suit/mission simulation, accounts/database, live data claims, and hand-building rover/equipment.

| KPI | Target | Responsible |
| --- | --- | --- |
| Initial load | <5s on normal laptop | Youssef Hassan |
| 3D frame rate | >=30 FPS on integrated GPU | Momen |
| Route calculation | <2s | Esraa |
| Real layers | >=4 from >=3 missions | Asmaa |
| Science waypoints | >=3, source/rationale each | Asmaa |
| P0 acceptance coverage | 100% | Mariam |
| Stable rehearsal | three clean consecutive demos | Mariam |
| Public links | all open in private window | Mariam |

## A3. PRD functional requirements

| ID | Requirement and acceptance outcome | Priority / owner |
| --- | --- | --- |
| FR-01 | Jezero 3D terrain comes from a real elevation file, supports orbit/zoom/pan, console clean | P0; Momen + Youssef Mohamed |
| FR-02 | Globe entry lets a user choose Jezero and flies camera there smoothly | P0; Momen |
| FR-03 | At least elevation/slope/temperature layers toggle with opacity, legend and source | P0; Youssef Hassan + Asmaa |
| FR-04 | Pick valid start/destination; show coordinates/elevation; reject out-of-AOI/forbidden point clearly | P0; Youssef Hassan + Momen |
| FR-05 | Within 2s return shortest/safest/science routes with waypoints, distance, ETA, max slope; explain no-safe-route | P0; Esraa + Youssef Mohamed |
| FR-06 | 0–100 Safety Score explains five factors/deductions and is deterministic | P0; Esraa |
| FR-07 | Slope-threshold, crater-edge and rough hazards render as layer/3D alerts; thresholds configurable/cited | P0; Esraa + Asmaa |
| FR-08 | Conditions panel shows season, local time, sunrise/sunset, last dated weather observation and station distance; stale marked stale | P0; Asmaa + Youssef Mohamed |
| FR-09 | >=3 science stops show name, coordinate, scientific rationale, source and estimate/confirmed confidence | P0; Asmaa |
| FR-10 | Clear Dashboard: layers, Mission Info, selected location, controls; Chrome/Edge/Firefox clean | P0; Youssef Hassan |
| FR-11 | About Data lists mission, instrument, date, resolution, license and URL per layer | P0; Asmaa + Youssef Hassan |
| FR-12 | Invalid API request is HTTP 400 Problem Details; UI comprehensible; no stack traces | P0; Mariam + Youssef Mohamed |
| FR-13 | Astronaut follows selected route/stops, first-person view | P1; Momen |
| FR-14 | Estimated time/oxygen/safe-return budget, defaults editable and labeled estimate | P1; Esraa |
| FR-15 | SHA-256 manifest check; mismatch red and dependent route blocked | P1; Mariam + Youssef Hassan |
| FR-16 | Post-first-load offline cached AOI/routes with Offline indicator | P1; Youssef Hassan + Mariam |
| FR-17 | Back-test against Perseverance traverse with similarity/difference | P1; Asmaa + Esraa |
| FR-18 | ECDSA-signed plan export/verifier | P2; Mariam |
| FR-19 | Licensed ready-made rover moving on route with simple dust/sky | P2; Momen |
| FR-20 | Arabic/English, RTL; English default | P2; Youssef Hassan |

## A4. Non-functional requirements

Performance: <5s first load, >=30 FPS, cached API p95 <500ms and routing <2s. Reliability: backend outage must show clearly labeled pre-saved demo routes. Security/privacy: no frontend secrets; validate input; CSP+HTTPS; no high/critical dependency issues; no accounts/tracking cookies/third-party analytics. Accessibility: WCAG 2.2 AA basics. Compatibility: current desktop Chrome/Edge/Firefox (1280px+), Safari best effort. Maintainability: lint/format, PR review, target 70% core-logic coverage, CI. Observability: health endpoint and request IDs. Reproducibility: one-command build and rerunnable pipeline. Compliance/scientific honesty: record licenses/AI disclosure, never call synthetic/illustrative content factual NASA data.

## A5. Data requirements, assumptions, risks, and traceability

PRD source mapping: MOLA/global or local HiRISE DTM for elevation; HiRISE/CTX imagery; THEMIS thermal; Perseverance MEDA weather; CRISM minerals; MMGIS/Perseverance traverse P1; Curiosity RAD P1. Every file must have source/date/license/SHA-256; one documented CRS; pinned source version; no invalid values; disclosed resolution differences; illustrative scene assets labeled.

Assumptions/constraints: Jezero coverage is sufficient; all participants are registered at same event; judges have modern laptop; free hosting will suffice; 48-hour build; maximum six people; NASA/open-agency resources required for global-award eligibility (verify). Dependencies: data availability, model licensing, final 2026 delivery/judging guidance.

Main risks and mitigations: oversized 3D scope → early slice/priorities; heavy/missing data → early tests/small AOI/backups; weak graphics performance → LOD/simplified fallback; integration risk → stable contracts from hour one; team fatigue/coordinator overload → split demo/QA and rotate rest.

Traceability: **Influence** is FR-05/06/14 through an end-to-end Marswalk; **Creativity** is FR-13/15/16/18 through trust/offline/3D; **Validity** is FR-06/09/11/17 and source/back-test; **Relevance** is FR-03/04/05/08/09 on one decision screen; **Presentation** is FR-02/10/13 through deck/demo. Award names in the original PRD are goals, not confirmed 2026 categories.

## A6. Original PRD open questions/sign-off

Open: final team name; Local Event; approval of roles; Jezero after data test; backend host; proposed stack; later offline TypeScript A*. Sign-off remains pending for Mariam, both Youssefs, Momen, Esraa, and Asmaa.

---

## Appendix C — Blender asset inspection and production plan

### Inspection facts

Opened `Mars_backup_before_quality_pass.blend` in background/read-only mode with **Blender 5.2.3 LTS**. The file loaded successfully. No save/export/render operation was performed. Blender reported that embedded scripts `front_view_models.py` and `mars_dashboard.py` were skipped because scripts are disabled; this is Blender's safe default and means their code/behavior was not executed or reviewed.

| Observed item | Finding |
| --- | --- |
| File size / format clue | 719,807,125 bytes (~686 MiB); file starts with Zstandard compression signature. |
| Scene inventory | 1 scene (`Scene`), 4,181 objects: 3,208 meshes, 950 empties, 5 armatures, 6 cameras, 3 curves, 8 text objects, 1 light. 1,452 mesh datablocks, 283 materials, 229 images, 26 collections. |
| Image packing | 227/229 images are packed. A packed HiRISE Jezero orthorectified image is 6,673 × 14,266 and remembers a source path under a different Windows user's `Documents\Codex\...`; because it is packed, the image data itself is embedded, but source provenance/path should be corrected and documented. Two images were not packed; their paths were not inspected in this pass, so portability of those two remains unknown. |
| Named content | `Mars_Terrain`, `MARS_NEW_Globe`, `Mars_Sun`, global globe/area marker, terrain feature and layer collections, craters, rocks/pebbles, boulders, dunes, slopes, plains, trails, exploration floor/paths, `RoutePlan`, rover-like hardware, and astronaut/suit parts appear in object/collection names. |
| Collections | Includes `Craters` (564 objects), `Mars_Pebbles` (450), `Rocks` (757), `NEW_Global_Boulders` (117), `NEW_Global_Craters` (186), `NEW_Global_Trails` (99), `NEW_Terrain_Layers` (6), `NEW_Exploration_Paths` (23), `RoutePlan` (22), `NEW_Mars_Globe` (9), plus camera/ground/mountain/astronaut-related collections. These are counts of direct collection objects and do not prove every collection is enabled/visible in the intended scene. |
| Cameras | 6 cameras; active camera was `Mars_Orbit_View_Camera`. Other named views include `MARS_NEW_Globe_Camera`, `Mars_OneShot_Camera`, `Mars_Camera`, `Astronauts_Camera`, and `Girls_Camera`. |
| Animation | At least many actions exist (first 30 include `0Action`, `antenna_*Action`, limb/part actions), which is evidence of animation data but not proof that a complete rover/astronaut route animation is wired correctly. |
| External libraries | Blender reported no linked libraries. |

### Assessment

This is more than a single terrain model: it is a large assembled scene with planetary globe/markers, Mars surface and terrain-feature groupings, routes, many imported detailed meshes, cameras, image/material data, and animation actions. That is a meaningful visual-production foundation. The direct collection names and mesh names also suggest a scene combining authored Mars elements and imported assets; the exact authorship/license of those imported models cannot be established from this file inventory alone and must be checked before public submission.

The file size and 4,181-object scene are a **production source**, not a good browser payload. The scene likely needs substantial curation before web export: choose only the scene/collection and camera that support the demo; hide/delete nothing in the source file; export a separate selected asset; reduce mesh complexity; bake or simplify materials; resize/compress textures; remove unused objects/actions; and test route overlay alignment. Prefer glTF/GLB for the web scene and retain the original `.blend` as the editable master. Do not send the whole `.blend` to each judge or load it directly in Angular/Three.js.

### Specific next review steps for the 3D owner

1. Open the blend interactively and inspect the active `Mars_Orbit_View_Camera` and the globe-to-Jezero shot; verify what is visible, composition, and intended story.
2. Confirm whether `Mars_Terrain` is a data-derived surface or a visual model. If data-derived, record source product, AOI, CRS, vertical datum/units, scale exaggeration, and resolution. If art-directed, label it illustrative.
3. Identify the two unpacked images and all external textures; repair missing paths in a **copy** of the blend if necessary, then keep the original backup intact.
4. Check collection visibility and duplication across old/new global collections. Count alone is not evidence of duplicate geometry, but 564+ crater/rock/scatter objects can inflate draw calls.
5. Audit asset licenses/attributions from the original Sketchfab/vendor/model sources before shipping. Embedded model names are not licensing evidence.
6. Produce two exports: a tiny hero globe/transition asset (optional) and a bounded Jezero scene with terrain + only a few hero props. Keep scientific layers and routes as data-driven overlays, not baked geometry.
7. Benchmark the exported GLB in the target browser; state compressed download size, triangles, texture memory, first-load time, and frame rate. Set a team budget rather than guessing.

### Production architecture decision: game engine vs web 3D

The team asked whether Unity (or another game engine) would outperform Angular + Java + Three.js. The best fit depends on the deliverable:

| Target | Good fit | Reason |
| --- | --- | --- |
| Public browser tool with dashboard, route planning, layers, sources, and responsive layout | Angular + Spring Boot + Three.js | Native web UI/data integration and direct control of a custom Mars scene; keeps the entry path simple for judges. |
| Geospatial tile streaming, large terrains and map-like globe | CesiumJS | Built for geospatial terrain/imagery/3D tiles; Mars projection/ellipsoid and NASA services still require careful configuration and validation. |
| Downloadable immersive simulation/game with interaction as the main product | Unity | Strong editor, animation, lighting and game workflow. Adds a separate UI/API integration and a Web build/deployment target if judges must click a URL. |

**Current recommendation:** keep the product browser-first. Use Three.js for the custom Mars visualization, Angular for controls and dashboard, and Spring/Java for routing/API. Use Blender for modeling and export selected optimized GLB assets. A small engine prototype may be evaluated as a separate spike only if the team already has Unity experience and can still serve the judge-facing route planner. Do not migrate the entire project to Unity just to make it look more “professional”; a tested, fast, evidence-backed web product will read as more complete.

**Rendering note:** Three.js `WebGPURenderer` offers WebGPU and WebGL2 fallback, but the official Three.js manual describes it as experimental and notes feature/performance gaps. For the deadline-critical renderer, use stable WebGL2 `WebGLRenderer` unless the team prototypes WebGPU on the target judges' browsers and verifies fallback. Source: [Three.js WebGPU renderer guide](https://threejs.org/manual/pages/webgpurenderer) and [WebGLRenderer API](https://threejs.org/docs/pages/WebGLRenderer).

**Unity web note:** Unity's current docs support desktop browsers with WebGL2/HTML5/64-bit WebAssembly and explain Web build restrictions and compression/server-header considerations. This is usable, but makes deployment and initial payload an explicit engineering concern; the tradeoff is based on official docs and the project's browser-first constraints. Sources: [Unity web browser compatibility](https://docs.unity3d.com/Manual/webgl-browsercompatibility.html), [Unity WebGL deployment](https://docs.unity3d.com/Manual/webgl-deploying.html).

### Visual/production goal from team chat

Mariam's team message asks for an experience reminiscent of Google Earth with a science-rich point inspection and a cinematic “holographic” feel. The software should be adaptable to future VR, rover/robotic integrations and holographic displays; those are future extension ideas, not hackathon acceptance criteria. The desired responsive design is about adapting the interaction to phone/laptop/headset, not shrinking the same dashboard. The team's ambition shifted from learning/trying the challenge toward competing seriously and aiming for the top; keep that ambition attached to scope control, scientific credibility, finish quality and a rehearsal-ready story.

### Full production wishlist from the 12-stage note, mapped into delivery tiers

| Feature family from team note | Tier | Completion interpretation |
| --- | --- | --- |
| Mars globe, surface color, orbit/zoom, Jezero marker | Demo polish | One short transition, optional if terrain route screen is already fast. |
| Terrain (hills/craters/valleys/dunes/boulders/slopes/plains/rims) | Core only when based on the AOI data | Elevation surface is scientific; extra procedural props are clearly labeled illustrative. |
| Elevation/slope/geology/temperature/dust/sun-shadows layers | P0 subset, later expansion | Start with layers that are truly available for the selected AOI and can be attributed; never invent a data layer for visual richness. |
| Astronaut/first-person/walk/inspect | P2 | Use licensed ready-made rig; scripted stop at waypoint is sufficient; do not model/rig from scratch in core schedule. |
| Rover, wheel/arm/camera/antenna, route traversal | P1/P2 | A simple low-poly rover following route is a good visual proof after route output works. It does not have to be a physically accurate simulator. |
| Science equipment and environmental stations | P2 | Only where an actual source-backed science waypoint merits a prop. |
| Science markers and ancient-water/mineral targets | P0 | Evidence-backed markers with source and uncertainty; no unsupported claims. |
| Slope/rim/roughness/sand/thermal/dust hazards | P0 subset | Derive only measurable hazards; put thresholds and coverage/uncertainty in the UI. |
| 3D route, start/end, waypoints, distance/elevation, safer/shorter variants | P0 | Core product story. Motion along the route is optional polish. |
| Mars sky, lighting/shadows/dust effects | P2 | Keep effects subtle and ensure they do not obscure data or reduce frame rate. |
| Camera transition, layer toggles, selection fly-to, warning interaction | P0/P1 | Camera orbit/pan/zoom and selecting a route/point are core; full orbit-to-surface cinematic transition is optional. |
| Final integration and performance | P0 | Test the actual web export, API/fallback, route overlays, layers, and demo path. |

## Appendix D — Newly supplied conversation digest and provenance

The two newly attached text files reproduce the prior conversation and team messages. The key retained facts are:

- A shared-document workflow was discussed: the PRD's first draft would be removed/restructured and sections prepared in the same document. A prior assistant claimed an artifact had 19 sections and an “10-B” review of the 3D plan; that artifact is not present in this workspace, so its full contents cannot be recovered from the files here.
- The team requested a deep Arabic analysis of every 2026 challenge, with links, technology and resources. An earlier pasted answer listed 14 challenge summaries and recommended Martian Map. Those summaries are unverified snapshots; the links and exact 2026 brief text must be checked against the official challenge portal.
- The Martian Map analysis recommended one Jezero route, terrain/imagery, elevation/slope, thermal/environment context, scientific targets, an explainable safety score, NASA Mars Trek/HiRISE/CTX/MOLA/THEMIS/CRISM/PDS and a 48-hour slice. It also warned that the official challenge page was not readable by automated access at that time.
- Role messages say everyone should own their task and help others. Esraa owns route planning/hazard detection (A*, start/destination, shortest vs safest, slope/rocks, waypoints, distance/time, route-to-3D output). Mariam owns integration, cybersecurity, presentation, validation, API input safety, demo, and coordination. Momen owns 3D development. The original assignments for the two Youssefs were NASA data/research and Python/backend; the later decision says Youssef Hassan and Youssef Mohamed will pair across frontend/backend. Asmaa was proposed for Data & Research, pending team agreement.
- The project’s original problem/solution is retained in sections 3/A2: make Mars surface exploration and route selection easier by showing NASA-based terrain, hazards, science points, and a safer/shorter path comparison.
- The team asked whether a coding subscription “Plus” would suffice. The historic assistant answer discussed Claude Pro/Max and usage limits; subscription naming, prices and limits change and were not reverified here. Treat that text as a past discussion, not purchase advice.
- The user later asked whether Unity/game engines might be better. The conclusion recorded in Appendix C is browser-first Angular + Java/Spring + Three.js for this decision-support product, Unity for a true downloadable/immersive game, CesiumJS for geospatial tiled terrain. Blender remains the asset authoring tool; optimize/export selected GLB assets.

Conversation files currently attached:

- `C:\Users\yhsn5\.codex\attachments\80a7df87-96e7-4ab0-81b8-c0c718c42a18\Pasted text.txt`
- `C:\Users\yhsn5\.codex\attachments\86a00dcc-6c5d-49f5-91a2-55ae37bb1bcd\Pasted text.txt`

---

## Appendix E — Link library

- [NASA Space Apps home](https://www.spaceappschallenge.org/)
- [2026 official announcement](https://www.spaceappschallenge.org/blog/explore-the-next-frontier-at-the-2026-nasa-space-apps-challenge/)
- [Team-supplied Martian Map challenge URL](https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/)
- [Mars Trek](https://trek.nasa.gov/mars/) and [Mars Trek WMTS API](https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars)
- [PDS Mars Orbital Data Explorer](https://ode.rsl.wustl.edu/mars2/)
- [HiRISE DTM guide](https://hirise.lpl.arizona.edu/dtm/howto.php)
- [NASA AMMOS MMGIS](https://github.com/NASA-AMMOS/MMGIS)
- [Angular release/support policy](https://angular.dev/reference/releases), [install guide](https://angular.dev/installation)
- [Spring Boot project](https://spring.io/projects/spring-boot), [system requirements](https://docs.spring.io/spring-boot/system-requirements.html)

---

## Appendix F — 3D data and saved Blender study (2026-11-06)

> **Recovery update (6 Nov 2026):** The first multi-scene `MARS_SENTINEL_NASA_Terrain_Study.blend` made an isolated CTX scene active and broke the original custom `1` framing workflow. That version is preserved under `../archive/`. The source `../Mars_backup_before_quality_pass.blend` remains untouched. The current canonical file is `../MARS_SENTINEL_NASA_Terrain_Study.blend`, rebuilt from the source with the original single integrated `Scene`, plus a linked field-site collection. It opens in the saved Layout camera view using `MARS_NEW_Globe_Camera`, with the original `Mars_Sky_NASA` world enabled. Structural verification confirmed 4,181 objects, one scene, and frame 112. See [`memo.md`](memo.md) for the full work log, camera diagnosis, shape-key discrepancy, script-warning context, and remaining work.

The user asked to continue the Mars 3D work, save as it progresses, make the starfield visually realistic, and use real Mars topography. The source project was kept unchanged. The earlier isolated-scene Blender study and previews remain archived; the canonical file has been rebuilt as described above.

### Terrain sources and treatment

- Downloaded the official USGS Mars 2020 TRN HiRISE DTM GeoTIFF to `data/JEZ_hirise_soc_006_DTM_1m.tif` (1,839,545,409 bytes). It is 21,400 × 21,488 float32 cells at 1 m/pixel; the file’s Mars equirectangular georeferencing is retained in the generated grid metadata. Source DOI: `10.5066/P9REJ9JN`; [USGS product page](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_hirise_dtm_mosaic). The USGS HiRISE product documentation identifies the data release as CC0 and asks users to cite it.
- Existing CTX source: `data/JEZ_ctx_B_soc_008_DTM_20m.tif`, the USGS Mars 2020 TRN CTX DTM at 20 m/pixel, DOI `10.5066/P906QQT8`; [USGS CTX product page](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic).
- HiRISE mesh grids: a full-region overview sampled every 40 m (535 × 537 vertices) and a central 4 km square detail patch sampled every 4 m (1,024 × 1,024 vertices), both derived from the native 1 m DTM. Keep the original GeoTIFF as the scientific source; do not describe a downsampled Blender mesh as native 1 m geometry.
- CTX mesh grid is sampled every 80 m for responsive Blender navigation.
- All terrain geometry uses source elevation values at vertical exaggeration 1:1. Mesh coordinates are centered locally for convenient Blender viewing; raster bounds, transform, source URL/DOI, crop offsets, mesh spacing, and nodata counts are stored in the scene’s provenance text and object properties. The elevation gradient is a false-color height visualization, not an orbital image.
- HiRISE nodata is encoded as finite sentinel values near `-3.4e38`; sampled nodata cells are masked and faces crossing them are omitted. The central detail crop is fully valid. This avoids bogus spikes around the regional DTM’s data boundary.
- A 50 cm/pixel MADNet-refined HiRISE Jezero mosaic (2.048 GB, CC-BY) is cataloged at [Freie Universität Berlin Refubium](https://refubium.fu-berlin.de/handle/fub188/38643). It is a model-refined product based on USGS imagery/DTM. The Blender study uses the official USGS 1 m stereo-derived product for the real-elevation foundation; the 50 cm product can be evaluated later as a separate comparison layer.

### Starfield, saved scenes, and reproducibility

- The original `Mars_Sky_NASA` world uses procedural Voronoi stars and a Milky Way-like band in the original integrated scene. It is a visual asset, not a NASA/ESA star catalog or measured sky solution. The separate `data/starfield_equirectangular.png` generated for the archived study is also synthetic.
- Planned scene names: `MARS_Globe_Realistic_Starfield`, `NASA_Jezero_CTX_DTM_20m`, `NASA_Jezero_HiRISE_1m_Regional_Overview`, and `NASA_Jezero_HiRISE_1m_Detail`.
- Preview files: `mars_globe_starfield.png`, `mars_jezero_real_terrain.png`, `mars_jezero_hirise_overview.png`, and `mars_jezero_hirise_detail.png`. The last two are produced by the final HiRISE build.
- Rebuild tools: `data/build_starfield.py`, `data/build_terrain_grid.py`, `data/build_hirise_grids.py`, and `tools/legacy/build_mars_study_legacy.py`. The legacy builder creates the old isolated-scene study and should not be used as the current workflow. Blender recovery/verification helpers are under `tools/`.
- Design boundary: the globe’s embedded surface texture is inherited from the supplied Blender file and has not been certified as a calibrated science raster; use the georeferenced CTX/HiRISE scenes whenever making scientific elevation or safety claims.

## Append-only instruction for future agents — 2026-11-06

All additions to this memory must be appended in dated sections. Do not remove or replace any earlier context, source link, team message summary, or decision record. Append corrections with the supporting evidence and date.

## Appendix G — NASA-colored Jezero site and exploration scene (2026-11-06)

The working 3D file to open is `MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend`. It was built from `MARS_SENTINEL_NASA_Terrain_Study_HIRISE_READY.blend`. A color-only checkpoint is `MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend`. `Mars_backup_before_quality_pass.blend` was not modified.

The HiRISE site mesh kept 1,132,096 vertices, scale `(1, 1, 1)`, and location `(0.23, -0.49, 0.014996)`. Its coordinate hash after save is `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`. `Mars_Terrain` stayed flat at z `-54.84`. The visible ground color is the USGS HiRISE red orthomosaic (DOI `10.5066/P9QJDP48`) tinted with the stable bright-terrain hue of the Viking MDIM 2.1 color mosaic. Jezero's own Viking samples are dark and blue-biased in that file, so they were not used as the hue. Details and the full route, hazard, and animation record are in `docs/memo.md` section 13 and `data/jez_site_color_provenance.json`.

Measured additions are the elevation and slope materials, two slope-derived routes, 27 slope markers, and pins for Octavia E. Butler Landing and Wright Brothers Field. Geology, temperature, and dust were not given fake NASA rasters. The western delta was not pinned inside the mesh because it lies outside the 4092 m window. Dust particles, equipment empties, and the existing sky remain labeled illustrative. The startup view is still the globe camera at frame 112. Tour, astronaut, and rover keys play after that frame.

## Appendix H — Resume notes (2026-11-06)

`README.md`, `INDEX.md`, `3D_ASSETS_README.md`, and `PRD.md` now carry the same resume facts in dated appendices. Open `MARS_SENTINEL_NASA_Terrain_Study_EXPLORATION.blend`. The color checkpoint is `MARS_SENTINEL_NASA_Terrain_Study_HIRISE_NASA_COLOR.blend`. The backup blend stays untouched. Site hash `ed5e2c9e0d23cb45dfbaf7c11deee3e168ea59d9681d8a094e3b514b32b354dd`. Safest route 1143.31 m, shortest 1135.24 m. Key `1` is `tools/mars_front_view.py` and still includes the 27 m rig until the next pass. That next pass, not done at this note, is a surface opening camera, local color where a real RGB image covers the window, and routes that visibly diverge.

## Appendix I — Readable scene (2026-11-06)

Open `MARS_SENTINEL_NASA_Terrain_Study_READABLE.blend`. `EXPLORATION` remains the rollback. The site hash, scale, location, and flat `Mars_Terrain` are unchanged. The scene camera is `MS_Surface_Opening_Camera` at frame 361. Local color is HiRISE `ESP_045994_1985` merged RGB on the center strip (about 41 percent of the window); the wings keep the earlier tint. Shortest 1113.50 m, safest 1159.95 m with a 67.88 m lateral gap, science 1203.21 m through Rochette. Full record: `docs/memo.md` section 16. Restart Blender once before using key `1`.

## Appendix J — One working file and the walk (2026-11-06)

Open `MARS_SENTINEL_NASA_Terrain_Study_SURFACE_FOCUS.blend`. Later scene work stays in this file. `READABLE` is the rollback. The site hash is unchanged. `Sketchfab_model` walks the green route with the existing `Mixamo Walk` cycle at 1.4 m per cycle, starting at frame 100. Joe stays beside the rover until frame 1514, then continues to the landing. The rover and the single wheel mesh stay at the frame-76 pose and the wheels are not spun. Scene end is frame 38906. Record: `docs/memo.md` section 18.

## Appendix K — Keys 1 and 2 (2026-11-06)

`tools/mars_front_view.py` is copied into the Blender 5.2 and 5.4 startup folders. Restart Blender once. In the surface file, the top-row `1` and numpad `1` leave the camera view, jump to frame 76 if the playhead is earlier, and frame the crew. The top-row `2` and numpad `2` pull back to `MARS_NEW_Globe` through `MARS_NEW_Globe_Camera`. In a file without that globe, `2` does not take over the key. The scene camera and the globe camera transforms are not changed.

