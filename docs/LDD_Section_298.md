## Section 298 — Rig-Aware Query Context (LOCKED 2026-04-17)

**UX Canon:** Cathy
**Architecture:** Clyde
**Lock Date:** 2026-04-17

---

### 298.1 — Purpose

Section 298 defines the Rig-Aware Query Context for the Discovery Query
Bubble — both the user-facing behavior (UX canon) and the underlying
architectural model (dec-band ownership, computation, count integration).

This section establishes:
  - How query context is presented to the user
  - How Rig Kit visibility mode is reflected in Discovery
  - What controls are and are not exposed
  - How dec-band seasonal fields are computed and owned
  - How context integrates with the Section 297 count engine

---

### 298.2 — Query Contexts (User-Facing Canon)

Three mutually exclusive contexts:

**Home Site Transit** (default)
  Horizon-agnostic. Represents seasonal visibility centered on transit.
  Independent of any rig configuration. Uses object-level transit_month
  field (Section 296.9).

**Rig Transit**
  Activated when a rig is selected and configured for Transit mode.
  Reflects rig-specific geometry. Seasonal interpretation uses
  dec-band transit_halfmonth field.

**Rig Rising**
  Activated when a rig is selected and configured for Rising mode.
  Seasonal interpretation shifts from transit-centered to rising-phase
  centered. Uses dec-band rising_halfmonth field.

**Canonical Query Titles:**
  Home Site Transit
  Rig Transit
  Rig Rising

These titles are the authoritative indicators of query interpretation
and appear as the Query Bubble header.

---

### 298.3 — UI Behavior (UX Canon)

**Context switching:**
  The Query Bubble does not control context directly.
  Context is determined upstream (Rig Kit) and reflected downstream.

  When context changes:
    Query title updates immediately
    Query interpretation changes accordingly
    No layout changes occur
    No additional controls appear or disappear
    Query inputs are NOT reset — filters carry forward
    Filters are re-interpreted under the active context

**Mode indicator (non-interactive):**
  A non-interactive label reinforces the active context.
  Examples: "Context: Rig (Rising)" or "Rig Mode: Rising"

  Rules:
    Visually subordinate to the Query Title
    Not interactive — display only
    Does not duplicate functionality
    Placed in Query Bubble header region
    Must not disrupt established geometry or spacing canon

---

### 298.4 — Source of Truth Principle (UX Canon)

Rig Kit is the sole authority for visibility mode (Transit vs Rising),
geometric constraints, and visibility semantics.

The Query Bubble reflects, does not define.

Canonical rule: visibility mode is defined upstream, consumed downstream.

This eliminates conflicting states and preserves user trust.

---

### 298.5 — Explicit Non-Exposure (UX Canon)

The Discovery Query Bubble must NOT expose:

  No visibility mode toggle in the Query Bubble
  No duplicate control of Rig Kit functionality
  No display of hour angles, arcs, or window structures
  No multi-window indicators
  No duration-based constraints (e.g. "3-hour window")

Discovery is intentionally intuitive and low-friction.
Planner-level detail belongs in downstream modules.

---

### 298.6 — Dec-Band Ownership Model (Architecture)

Seasonal visibility fields are NOT stored on objects.
They are owned by the rig-specific Declination Band structure.

Each dec band row in skypix_vis.db stores two additional fields:

```
transit_halfmonth    INTEGER    -- half-month bin (1–24) of midnight transit
rising_halfmonth     INTEGER    -- half-month bin (1–24) of first east rise
                                -- NULL if no usable east window exists
```

Half-month bins: 1 = first half of January, 2 = second half of January,
... 24 = second half of December.

**Ownership:** skypix_vis.db per-rig, per dec-band row.
**Scope:** rig geometry, not object data. SCD schema unchanged.
**Rebuild triggers:** same as existing visibility rebuild triggers
  (horizon polygon, minimum altitude, dec band width, rig location,
  zenith obstruction changes).

---

### 298.7 — Rising Half-Month Computation (Architecture)

**Transit half-month** derives from existing transit_month logic
extended to 24-bin resolution:

```
transit_halfmonth = round(transit_month * 2)  -- maps 1.0–12.5 → 2–25
                                               -- clamp to 1–24
```

**Rising half-month** derives from the east visibility arc:

```
rising_halfmonth = transit_halfmonth - round(ha_rise_hours / 15.2 * 2)
```

Where:
  ha_rise_hours = absolute value of ha_rise (hours east of meridian)
                  from vis_horizon table for this dec band
  15.2 = days per half-month (365.25 / 24)
  Divide by 15.2 converts hours-before-transit to half-month offset

Wrap-around: if result < 1, add 24.

**Definition of ha_rise for this calculation:**
  First usable east window only.
  Window must meet min_visible_time threshold.
  If no usable east window exists: rising_halfmonth = NULL.

**West-first visibility edge case:**
  Objects with no east window (rise in west, or polar objects with
  west-only visibility for a given rig) → rising_halfmonth = NULL.
  These objects are excluded from Rig Rising query results.

**Multi-window edge case:**
  Use the first (earliest) east window ha_rise only.
  Subsequent windows (e.g. post-obstruction) are ignored for
  rising_halfmonth. Discovery is not a multi-window planner.

---

### 298.8 — Query Engine Integration (Architecture)

**Home Site Transit:**
```sql
AND transit_month BETWEEN :month_min AND :month_max
```
Uses object-level transit_month (Section 296.9). No rig dependency.

**Rig Transit:**
```sql
-- Join dec-band table for active rig
AND db.transit_halfmonth BETWEEN :halfmonth_min AND :halfmonth_max
```
Where db = dec_band row matching object's dec_deg for the active rig.

**Rig Rising:**
```sql
AND db.rising_halfmonth IS NOT NULL
AND db.rising_halfmonth BETWEEN :halfmonth_min AND :halfmonth_max
```
NULL rising_halfmonth objects are automatically excluded.

**Count engine (Section 297) integration:**
  Same predicate logic used for both Count and Retrieve — no divergence.
  Context switch changes which seasonal field the predicate references.
  All other filter stages (spectral, class, constellation, spatial,
  photometric) are context-independent.

**Performance:**
  Dec-band table has at most 180 rows per rig (1° bands).
  Join is trivial. No performance impact on count target of < 100ms.

---

### 298.9 — Scope Boundaries (Explicit Non-Goals)

Intentionally excluded from this section and from Discovery:

  Uninterrupted imaging window queries ("3-hour continuous")
  Multi-window query constraints
  Per-object rising month fields on SCD
  Planner-grade temporal filtering in Discovery

These belong to Planner-level refinement.

---

### 298.10 — Behavioral Philosophy

This system introduces planning awareness without exposing planning
complexity. The user is enabled to ask:

  "What is visible this season?"   → Home Site Transit
  "What works for my rig?"         → Rig Transit
  "What is entering usability?"    → Rig Rising

without needing to understand visibility arcs, obstruction geometry,
or multi-window behavior.

Context feels like a shift in perspective, not a change in tool behavior.

---

### 298.11 — Action Items

**Jim:**
  Add transit_halfmonth and rising_halfmonth columns to the dec-band
  table in skypix_vis.db schema.
  Add index on (rig_name, rising_halfmonth) for Rig Rising queries.

**Clyde:**
  Implement rising_halfmonth computation in build_vis_horizon()
  after ha_rise is determined per dec band.
  Handle NULL case (no east window) cleanly.

**Cathy:**
  Query title updates per 298.2.
  Non-interactive mode indicator per 298.3.
  No new controls — context labeling only.

---

*Section 298 locked 2026-04-17.*
*UX canon: Cathy. Architecture: Clyde. Schema: Jim.*
