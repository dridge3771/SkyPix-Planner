## Section 291 — Discovery Query Bubble (LOCKED 2026-04-08)
**Source:** Jim (UI Architecture)
**Implementation:** Cathy

---

### 291.1 — Overview

The Discovery Query Bubble is a floating, draggable overlay container
rendered in Light Mode (#F8FAFC background). It behaves as a modal overlay
that can be repositioned over SkyVu or the Left Panel without blocking
either entirely. It is not a fixed-position dialog.

---

### 291.2 — Header: Identity Gatekeeper

A full-width Query Name input field at the top of the bubble.

Color states:
  Empty (< 3 characters): Yellow — bg #FEF9C3, text #A16207
  Valid (≥ 3 characters): Green  — bg #DCFCE7, text #166534

Gate behavior:
  All Transfer and Save to Tab functions in the main UI are globally
  disabled until the Query Name field is Green (≥ 3 characters entered).
  This is a hard UI gate — no exceptions.

---

### 291.3 — Mid-Section: The Sieve

**Observability Header**
Horizontal matrix of 12 months (JAN–DEC) with radio selectors.
Spans full width of the bubble above the two segment boxes.

**Left Segment — Spatial/Safety**
Border: Red (#EF4444)
Contents:
  RA range:  From / To fields
  Dec range: From / To fields
  Dec Limit fields: Rig Guardrails — the absolute horizon/obstruction
    floor for the currently active rig. These fields listen to the
    active Rig Kit and update automatically when the user switches rigs
    (see 291.6 — Rig Sync).

**Right Segment — Geometry/Physics**
Border: Green (#22C55E)
Contents:
  Size limits:      < and > fields (arcmin)
  Magnitude limits: < and > fields
  Position Angle:   range fields (0° to 180°)

---

### 291.4 — Wings: Hierarchical Interaction

The bubble has two dynamic wings that deploy on user selection.
Wings do not replace the bubble — they extend it.

**Right Wing — Physics Tree**
Trigger: User selects the Object Class radio button on the right
edge of the bubble.
Motion: Bracket-style tree slides out horizontally to the right.
Structure:
  Column 1: Major object classes (Nebula, Galaxy, Cluster, etc.)
  Column 2: Sub-OTypes (HII, PN, SNR, WR, etc.)
Hover/right-click on any OType:
  Displays Source Physics educational text from the Local Lookup Table
  Example: "SNR: The wreckage of a titanic stellar explosion..."
  Zero-latency requirement — must read from local storage (291.7)

**Bottom Wing — Mythology Matrix**
Trigger: User selects the Constellation radio button at the bottom
of the bubble.
Motion: Grid matrix slides down vertically from the base of the bubble.
Structure: 6-column grid of all 88 IAU constellation abbreviations
  (CYG, ORI, CAS, etc.)
Hover/right-click on any constellation:
  Primary reveal: Full name (e.g. "Cassiopeia") + calculated centroid RA/Dec
  Educational reveal: Narrative lore (Greek/Roman/Arabic history)
    + Best Viewing Season
  Zero-latency requirement — must read from local storage (291.7)

---

### 291.5 — Discovery Behavioral Workflow

**A. Ingestion and Triage**

All query results and pasted legacy data land in the Left Panel as
transient rows. Default state: Yellow (L0/Holding tier).

Winnowing logic:
  User clicks rows to select them — Selection column turns Green
  Delete behavior:
    If any rows are Green → Delete prunes only Green rows
    If NO rows are Green → Delete acts as Clear All (safety
    confirmation required before executing)

**B. Healing and Marriage (Transfer)**

Selecting a row in the Left Panel opens the Spectra Panel (Right Side).
User resolves duration caps and spectral dominance (Hα, OIII, SII)
using SCD-enriched data.

Once healed, user activates Transfer (Activity Button):
  Object is formally adopted from the transient list into the SUD
  Direct assignment: touching a Planner Tab moves the object directly
    to that planner
  Safety net: single-object assignments trigger a 4-second Reverse
    Toast notification to undo accidental clicks

---

### 291.6 — Rig Sync

The Dec Limit fields in the Left Segment (291.3) listen to the active
Rig Kit. When the user switches rigs, the Dec Limit fields update
automatically to reflect the new rig's safety floor (minimum elevation,
horizon obstruction floor).

This is a live binding — not a one-time population at bubble open.
If the rig changes while the bubble is open, the Dec Limits update
in place without closing or resetting the bubble.

Implementation: connect to the rig_saved Signal(dict) from RigKitManager.
The Dec Limit fields subscribe to rig switches via the shell's active
rig state.

---

### 291.7 — Local Lookup Table

The Educational Library (Source Physics descriptions and Constellation
lore) must be stored locally — not fetched from Supabase at hover time.

Requirement: zero-latency hover response even when Supabase is offline.
Storage: bundled JSON or SQLite in src/data/
Contents:
  Per OType: Source Physics narrative text
  Per constellation: Full name, centroid RA/Dec, mythology narrative,
    best viewing season

This library is read-only at runtime. Updates ship with application
versions, not at runtime.

---

### 291.8 — Session Persistence (Orange Tabs)

Discovery sessions are shelved using Orange Tabs (per existing planner
architecture — Section 265). This allows the user to run a new search
without losing the winnowed progress of the previous session.

Orange tab stores:
  Query name (the gated field from 291.2)
  All filter criteria from the bubble (291.3)
  Current Left Panel transient row list and selection state
  Query snapshot JSON (per Section 278.9)

Restoring an orange tab restores the full session state including
the bubble's filter criteria, not just the object list.

---

### 291.9 — Implementation Notes for Cathy

- Bubble is draggable, not fixed-position
- Wings extend the bubble — they do not replace it or open separate windows
- The 4-second Reverse Toast is a non-blocking overlay, not a dialog
- Query Name gate (291.2) is global — affects buttons outside the bubble
- Dec Limit rig sync (291.6) is a live binding, not a snapshot
- All hover educational content reads from local storage (291.7) —
  never from network at hover time
- Light Mode (#F8FAFC) throughout — no dark backgrounds in the bubble
- Color language: Red border = spatial/safety constraints,
  Green border = geometry/physics constraints

---

*Section 291 locked 2026-04-08. Source: Jim. Implementation: Cathy.*
