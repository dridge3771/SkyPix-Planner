## Part LX — Visibility Engine Multi-Window Revision + UI Architecture Canon (LOCKED 2026-04-08)

---

## Section 288 — Visibility Engine: Multi-Window Schema (LOCKED)

### 288.1 — Motivation

The prior single-window model (ha_rise / ha_set) cannot represent objects whose
visibility is fragmented by horizon polygon obstructions. Validated against rig
"130" (Boulder CO): a 47° horizon spike at az=180° (pine tree) blocks transit
for dec≈−10°, producing two separate windows. The full window model supports
up to four windows per dec band.

### 288.2 — Schema Change

REMOVE from vis_horizon, vis_optimum, vis_hourangle:
  ha_rise    REAL
  ha_set     REAL

ADD:
  ha_windows_json      TEXT    -- JSON array of [ha_rise, ha_set] pairs
                                -- e.g. '[[-3.52,-0.15],[0.90,1.95]]'
                                -- ordered ascending by ha_rise
                                -- NULL if object never clears horizon
  window_count         INTEGER -- surviving windows after min_visible_time filter
                                -- 0 if never clears horizon
  max_window_duration  REAL    -- max(ha_set - ha_rise) across all windows
                                -- required by planner exposure engine

RETAIN unchanged:
  dec_band_begin, dec_band_end
  ha_east_obs, ha_east_obs_end, ha_west_obs, ha_west_obs_end
  visible_east, visible_west, visible_total

### 288.3 — Engine: ha_at_horizon() Revised

PREVIOUS: returns (ha_rise, ha_set) tuple — breaks on first complete pair.

REVISED: returns list of [ha_rise, ha_set] pairs — all crossing pairs across
full ±12h scan. No early break. May return 0, 1, 2, 3, or 4 pairs.

Algorithm:
  1. Scan HA −12h → +12h in N_STEPS=720 steps (2-min resolution)
  2. At each step: compute obj_alt (Bennet refraction) and horizon_alt (SLERP)
  3. Detect ALL sign changes of (obj_alt − horizon_alt):
       negative → positive = rising crossing
       positive → negative = setting crossing
  4. Pair each rising crossing with the next setting crossing
  5. Discard unpaired crossings at ±12h boundary
  6. Return list of complete [ha_rise, ha_set] pairs

### 288.4 — Engine: compute_visibility() Revised

PREVIOUS: takes scalar ha_rise, ha_set.

REVISED: takes list of [ha_rise, ha_set] window pairs.

Per window pair [hr, hs]:
  1. Split at meridian: east=[hr, min(hs,0)], west=[max(hr,0), hs]
  2. Apply zenith obstruction clipping to overlapping component
  3. Discard segments < min_visible_time_hr (default 1.0h)
  4. Accumulate into visible_east, visible_west

Output:
  ha_windows_json     = JSON of surviving [rise, set] pairs
  window_count        = len(surviving pairs)
  max_window_duration = max window duration across all pairs
  visible_east        = sum of east segment durations
  visible_west        = sum of west segment durations
  visible_total       = visible_east + visible_west

### 288.5 — Azimuth Bug Fix (LOCKED)

File: skypix_vis_fixed.py

Previous obj_az_at_ha() used atan2(sin_az × cos_alt, cos_az) which compressed
azimuth at high altitudes, causing false crossings 14–18 minutes early.

Fix: replaced with acos(cos_Az) + east/west flip on sin(HA).

Validation result (rig "130", Vega dec=+38.8°):
  Before fix: 14.8 min error vs Astropy
  After fix:  < 1 min error vs Astropy
  All dec bands: ≤ 1.6 min delta vs Astropy HADec frame

### 288.6 — Planner Implications (Cathy)

When window_count > 1, visible_total must NOT be displayed as a continuous
imaging block. Display must indicate fragmented visibility.

Recommended cell format: "3.2h ×2" (total hours × window count)

Exposure planning must use max_window_duration for:
  - Uninterrupted sequence length
  - Dithering strategy
  - Subframe count
  - Guiding practicality
  - Session feasibility

### 288.7 — Engine Versioning

vis_manifest must include schema_version field. Version mismatch triggers
forced rebuild via delete vis DB + build_all(). skypix_vis.db is derived
data — no migration needed, only rebuild.

---

## Section 289 — Constellation Field: SCD and SUD (LOCKED)

### 289.1 — Field Definition

  constellation    CHAR(3)    -- IAU 3-letter abbreviation (e.g. 'CYG', 'ORI')
                               -- NULL only if coordinates missing
                               -- uppercase, IAU standard 88-constellation set

Added to: SCD public.objects, SUD sud_objects

### 289.2 — Determination Method

Source: IAU Delporte/Roman 1987 boundary file.
Method: precess J2000 RA/Dec → B1875, apply boundary strip lookup.
Runtime: astropy get_constellation() handles precession internally.
Network: none required — boundary data bundled in astropy.

SIMBAD constellation field derives from the same boundary model — no SIMBAD
queries needed or used for constellation assignment.

### 289.3 — Enrichment Pass

Applied to all 257,978 SCD objects via batch REST API + SQL UPDATE.
Objects missing ra_deg/dec_deg assigned NULL (not 'UNK').
Objects with valid coordinates: 100% populated.

Note: 193,459 objects had NULL oid values due to bulk ingest method.
Fixed by: CREATE SEQUENCE objects_oid_seq START WITH 28262297;
          UPDATE public.objects SET oid = nextval('objects_oid_seq') WHERE oid IS NULL;
All objects now have unique oid values.

### 289.4 — Discovery Search Integration

Constellation is a standard Discovery search argument.
UI: dropdown or typeahead of 88 IAU names/abbreviations.
Multi-select supported. Combines with all other criteria via AND.

---

## Section 290 — UI Architecture Canon (LOCKED 2026-04-08)

### 290.1 — Elastic Spring Layout Model

SkyPix UI uses a left-aligned label / right-aligned field pattern with an
elastic spring region between them.

```
[Label text ..... spring ..... [data field]]
```

The spring expands or contracts to accommodate:
  - Screen size variation
  - OS zoom scaling (100% / 125% / 150%)
  - Font scaling

Spring behavior:
  - Proportional governors — spacing expands proportionally, not linearly
  - Prevents label/field collision at any zoom level
  - Maintains visual balance across all supported zoom levels

Implementation: QGridLayout column stretch on the spring column.

### 290.2 — No Fixed Box Widths (CRITICAL RULE)

Fixed widths on UI containers are PROHIBITED.

Permitted constraints:
  - Minimum width (floor only)
  - Elastic expansion
  - Proportional springs

This rule applies to all modules:
  Rig Kit, Camera Kit, Filter Kit, Discovery, Objects, Planners

Rationale: fixed widths cause overflow and collision at 125%/150% zoom.
All prior layout failures traced to hidden fixed width violations.

### 290.3 — Screen Edge Reserve Canon

  Right reserve:   50px  (inelastic)
  Bottom reserve:  50px  (inelastic)

Composition:
  40px tab strip + 10px viewport safety margin

Everything inside the working area must remain responsive.
These reserves do not participate in elastic layout calculations.

### 290.4 — Warning Color Behavior (LOCKED)

Default paint indicates required data entry state.

Rig Physics fields:       #ffff00  (yellow) — gates Save
Display Content,
Imaging Constraints,
Imaging Environment:      #ffaa00  (orange) — optional/environment

Behavior:
  - Field painted at construction
  - Clears to white (or 20% rig tint if rig color selected) on valid entry
  - Single character counts as valid for text fields (Rig Name, Project Name)
  - Numeric fields clear on editingFinished (focus-out), not on keypress
  - Yellow fields gate Save — Save button disabled while any yellow field present
  - Orange fields do not gate Save

Acknowledge Defaults button:
  - Clears all orange fields to 20% rig tint (or white if no rig color)
  - Does not clear yellow fields

### 290.5 — Horizon Table Geometry Constraint

  Bottom of horizon container = 50px from viewport edge (per 290.3)
  Interior margin = 10px on all sides

Horizon table row height calculation:
  available_height = module_height - nav_strip - ribbon - margins - upper_boxes - bottom_reserve
  row_height = available_height / 17  (header row + 16 data rows per group)

Horizon table must never collide with bottom tab strip.

### 290.6 — ScaledView Zoom Architecture (LOCKED)

SkyPix uses a single QGraphicsView (ScaledView) wrapping the entire
application canvas at 1920×1080. All zoom handling is performed by a
single scale transform:

  scale = window.width / 1920
  transform = QTransform().scale(scale, scale)

This renders OS zoom (125%, 150%) transparent to the application.
No individual widget pixel values are multiplied by DPI factors.

Critical: AA_EnableHighDpiScaling = False (deprecated Qt6 attribute, removed)
Critical: AA_UseHighDpiPixmaps = False (deprecated Qt6 attribute, removed)

Validated at 100%, 125%, 150% system zoom — all layouts render identically.

---

*Part LX locked 2026-04-08. Visibility engine schema revised. UI architecture
canon established. Constellation enrichment complete.*
