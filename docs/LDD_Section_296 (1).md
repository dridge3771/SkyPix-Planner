## Section 296 — Discovery Query Bubble: Advisory System & Spectral Filter Canon (LOCKED 2026-04-08)

**Source:** Cathy (Advisory System Design) + Clyde (Spectral Filter Reconciliation)

---

### 296.1 — Advisory System Core Principles

The advisory system is symmetric, non-owning, union-based, and
persistence-driven across peer domains. No domain owns another.
Relationships are revealed, not enforced.

Advisory is a learning mechanism — users discover spectral behavior
of object types, relationships between observing conditions and targets,
and imaging regimes without reading documentation.

---

### 296.2 — Behavioral Model

Bidirectional advisory:
  Domain A selection → advisory highlighting in Domain B
  Domain B selection → advisory highlighting in Domain A

Examples:
  Month ↔ Constellation
  Spectral Band ↔ OType / Class

Union-based persistence:
  Advisory state = union of all active selections
  Multiple selections → combined advisory mask
  Advisory remains active while any contributing selection exists
  Last selection removed → advisory clears

Non-owning:
  No domain asserts control over another
  Advisory is informational only
  Advisory never modifies query state directly

---

### 296.3 — Advisory vs Constraint Separation

  Advisory        — reveals relationships
  Query Filters   — constrain results
  Warning Colors  — signal contradictions

These three systems are independent and non-overlapping.
Advisory state is never included in query predicates.

---

### 296.4 — Visual Canon (Advisory Rings)

  Ring diameter:  radio button diameter + 4px
  Stroke width:   2px normal, 3px emphasis
  Color:          dark gray — distinguishable without introducing new
                  color vocabulary, works across all UI backgrounds
  Position:       centered on radio button centroid (with visual correction)
  Clipping:       rings drawn inside the radio widget — never clipped
  Ambiguity:      advisory must never be visually ambiguous

  Note: Color blindness accessibility is a known V2 consideration.
  The SkyPix color language (yellow/orange/green/red/opacity scale)
  is too deeply embedded to retrofit at beta. Deferred by design.

---

### 296.5 — Spectral ↔ Object Advisory

Spectral → Object:
  Selecting one or more bands:
    Ring OTypes where band relation = required or sometimes
    Ring class header if any child OType qualifies

Object → Spectral:
  Selecting one or more OTypes/classes:
    Ring spectral bands where relation = required or sometimes

Relation rules:
  required  → ring
  sometimes → ring
  absent    → no ring
  unknown   → no ring

Broadband integration:
  Broadband is a distinct spectral mode — not derived from absence
  Implemented as a dedicated control row
  Broadband selected → ring broadband-first OTypes
  Broadband-first OTypes selected → ring Broadband

Narrowband advisory suppression:
  Any narrowband band selected → advisory suppresses broadband-first
    OTypes (informational hint only, not a filter)
  Broadband selected → advisory suppresses emission OTypes
  Reflects mutual exclusivity of imaging regimes

---

### 296.6 — Spectral Filter Canon (LOCKED)

Broadband and Narrowband are mutually exclusive imaging regimes.
Both may be selected simultaneously (mixed session) but advisory
signals the regime tension when both are active.

Narrowband population:
  22,908 SURFACE tier objects with characterized OIII and/or SII
  strength values derived from OType spectral inference.
  These are the only objects for which SkyPix can make a meaningful
  narrowband recommendation based on actual spectral data.

Broadband population:
  Objects with broadband_first = true (continuum-dominated,
  reflection nebulae, galaxies, clusters, open clusters).

Hα terrain — NOT a Discovery query filter (LOCKED):
  Hα strength values are derived from the 1.7-arcmin Hα terrain
  survey (VTSS/WHAM/SHFM). Every SURFACE object has an Hα value
  because every sky position has a terrain value. This represents
  regional sky background emission, not object-specific Hα emission.

  Hα terrain is NOT exposed as a user-facing spectral filter in
  the Discovery bubble.

  Hα terrain feeds:
    SNR engine (signal calculation)
    SkyVu SHFM mist layer (dome renderer)

  Rationale: any user filtering by Hα emission is looking for
  narrowband targets — those are the 22,908 characterized objects.
  Filtering by terrain background would include non-emission objects
  in emission-rich sky regions. Misleading and unhelpful.

Spectral filter summary:

  Broadband selected     → broadband_first = true objects
  Narrowband (any band)  → 22,908 objects with OIII/SII characterized
  Both selected          → union of both sets
  Neither selected       → no spectral constraint, all eligible objects

---

### 296.7 — Query Object Count Specification

Canonical definition:
  Total Objects = unique SCD objects returned by Retrieve under
  the current active query state.

Key rules:

  1. Retrieval consistency
     Count uses identical predicate logic as Retrieve.
     Count and Retrieve must never diverge.

  2. Active filters only
     Object Class / OType
     Constellation
     Spectral Bands (including Broadband)
     Region (RA/Dec)
     Declination range
     Magnitude / Size / Position Angle
     Observability (transit_month)

  3. Exclusions
     Advisory states — never included in count predicate
     Hover/education layers
     UI-only states

  4. Uniqueness
     Count reflects unique objects only.
     No duplicate counting across associations or aliases.

  5. Layer scope
     Count includes all Discovery-eligible SCD objects.
     Exact layer inclusion matches Retrieval behavior.

Performance:
  Count updates live on every UI interaction
  Target: < 100ms
  Indexed on transit_month, constellation, presence_mask
  Cached partial predicates as future optimization

Fallback:
  Database unavailable → return 0 or last cached count
  UI must not crash on count failure

---

### 296.8 — Single Predicate Source (Implementation Canon)

Query predicate builder is shared between Count and Retrieve.
No duplicate logic paths permitted.

Incremental build order:
  1. OType/Class filtering
  2. Spectral filtering (Broadband | Narrowband | none)
  3. Constellation
  4. Spatial (RA/Dec range)
  5. Photometric (magnitude / size / PA)
  6. Observability (transit_month range)

Each stage validated before proceeding to next.

---

### 296.9 — transit_month Field (SCD)

Pre-computed field enabling fast observability queries without
runtime RA-to-month calculation across 257,978 objects.

  Field:          transit_month    NUMERIC(5,2)
  Range:          1.00 to 12.50
  Formula:        ((RA_degrees - base_meridian) / 360 * 12) + 1
                  adjusted for 0/360 wrap-around
  Base meridian:  7.5 + (n * 15) where n = UTC offset integer
  Purpose:        mid-month anchoring — result lands on ~15th of month
                  matching transit matrix cell semantics

The 7.5 degree offset shifts the result by half a month so that
transit_month = 6.50 means mid-June, not June 1st.

Example values:
  Orion Nebula  (RA ~83 deg)   → transit_month ~1.50  (mid-January)
  Cygnus region (RA ~310 deg)  → transit_month ~10.50 (mid-October)

Validation: spot-check against Stellarium midnight transit dates
for 5+ objects spanning the full RA range before committing the
enrichment pass.

Enrichment: Cathy (in progress at section lock date).

---

### 296.10 — SkyVu Forward Projection (Strategic Note)

The advisory model generalizes to SkyVu as relational highlighting
across spatial and spectral layers:

  Band selected         → highlights sky regions of strong emission
  Object class selected → highlights spatial distribution in dome
  Terrain intensity     → highlights candidate objects

Enables interactive discovery through relationship visualization
rather than list-based querying.

Implementation deferred to SkyVu rendering phase.
Noted here for architectural continuity with advisory engine design.

---

*Section 296 locked 2026-04-08.*
*Advisory system: Cathy (current implementation, no action required).*
*Spectral filter canon: locked, no team action required.*
*transit_month enrichment: Cathy (in progress).*
