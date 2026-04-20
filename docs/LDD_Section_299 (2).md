## Section 299 — Objects/Discovery: Right Panel, Rig Context, and SkyVu Binding (LOCKED 2026-04-18)

---

### 299.1 — Right Panel Architecture

The right panel (1120px) for Objects and Discovery modules presents
object data synchronized with the left panel. It is not a separate
functional panel — it is a data extension of each left panel row,
presenting spectral and seasonal information for every object
simultaneously.

Right panel is divided into two sub-panels displayed together:

  Emission Profile:     400px  (8 bands × 50px each)
  Transit/Visibility:   720px  (12 months × 60px each)

Left and right panels share a single scrollbar and scroll in
perfect vertical lockstep. One scroll position drives both panels.

SkyVu overlays the full right panel (1120px × full height) when
activated. No separate toggle panels — SkyVu is the only overlay.

---

### 299.2 — Context Model (LOCKED)

Three mutually exclusive contexts, identical authority model to
Section 298 (Query Bubble):

**Home Site Context (default)**
  - Transit matrix shows transit time HH:MM per month cell
  - Row 1: visible hours tonight using assigned home site rig horizon
  - Shading: visible days per month using assigned home site rig horizon
  - Transit time uses home site longitude + DST from assigned rig's
    timezone parameter
  - Assigned rig: user-selectable, defaults to seasonality_rig_id
    (Setup parameter, Section 272)
  - Label: "Home Site Transit — [Assigned Rig Name]"
  - SkyVu shows assigned rig's horizon polygon
  - Changed via rig tab selection in the module left strip

**Rig Transit Context**
  - Transit matrix REPLACES Home Site columns entirely
  - Cell row 0: transit time HH:MM (current planning date)
  - Cell row 1: total visible hours for the current session/night
  - Cell shading: intensity reflects visible days per month for this rig
  - Shaded matrix IS the Rig context indicator — shading presence
    tells the user they are in Rig context without requiring a label
  - SkyVu shows that rig's horizon polygon + object visibility arc
  - Dark hours on dome synced to rig site coordinates

**Rig Rising Context**
  - Same as Rig Transit but matrix shows rising phase entry
  - First usable east window only (per Section 298.7)
  - Objects with no usable east window show NULL / greyed cell

**Context selector:**
  Owned by the Objects/Discovery module UI — same authority model
  as the Query Bubble (Section 298.4). Rig Kit defines parameters,
  module reflects and consumes them. No duplicate control in the
  matrix itself.

  Rig selection uses the same rig tab touching behavior as the
  Query Bubble rig context. Rig tabs are presented in the 80px
  left strip of the Objects module, identical to Discovery.

  Home Site Context: rig tab selection assigns the home site rig
    (horizon + DST). Does not change transit longitude — home site
    longitude always drives Home Site Context transit times.
  Rig Context: rig tab selection switches active rig entirely —
    rig site coordinates drive transit time, horizon, and DST.

---

### 299.3 — Transit Matrix Cell Specification

**Cell content (two rows per object row, matching left panel row height):**

  Row 0: Transit time — HH:MM format, current planning date
          In Home Site Context: transit at home site longitude,
            DST from assigned home site rig timezone parameter
          In Rig Context: transit time at rig site coordinates,
            DST from selected rig timezone parameter

  Row 1: Visible hours — total unobstructed session hours tonight
          Home Site Context: hours above assigned home site rig horizon
          Rig Context: hours above selected rig horizon
          Both contexts: ≥ min_visible_time threshold applied
          Row 1 is NEVER blank — rig horizon always assigned

**Cell shading (Rig Context only):**
  Shading intensity = urgency signal for that calendar month
  Formula: opacity = 100% − (3.3% × visible_days_this_month)
  Full opacity (darkest) = very few usable nights this month → urgent
  No shading = month fully visible → no urgency

  Shading color: user-defined in Setup (single color family shared
  with emission confidence shading — no multiple color languages)

  Home Site Context: NO shading on any cell

**Context is indicated by Row 1 data presence:**
  Home Site Context: Row 1 blank — no rig horizon data available
  Rig Context: Row 1 populated — visible hours tonight for this rig

  The presence of Row 1 data IS the context indicator.
  No separate mode label needed in the matrix itself.

**The two signals are orthogonal:**
  Cell content = tonight's actual numbers (transit time, session hours)
  Cell shading = monthly urgency (how many opportunities this month)
  Shading is present only in Rig Context but is NOT the context
  indicator — Row 1 data presence is.

  Example: Row 1 populated, heavily shaded March cell 02:15 / 4.2h:
    "Tonight: transits at 2:15am, 4.2 hours visible.
     March: only 8 usable nights — plan this target soon."

---

### 299.4 — Emission Profile Specification

Eight bands displayed left to right per presence_mask sequence:

  Cont · OII · Hβ · NII · Hα · OIII · SII · IR

Column width: 50px each × 8 = 400px total.

**Cell content (two rows per object row):**

  Row 0: Relative band strength 0–100
          Normalized to Hα = 100 as reference anchor
          If Hα = 0: strongest present band promoted to 100
          Font: 13px, matching left panel primary text

  Row 1: Estimated flux in Rayleighs
          Format: NNNN R or N×10⁶ R (magnitude-appropriate)
          Source: literature, measured, or LFU
          Null-tolerant: shows — if unavailable
          Font: smaller, matching secondary data size

**Confidence shading:**
  Same opacity scale as transit matrix shading:
    L3: 40% · L2: 30% · L1: 20% · L0: 10% · L−/SAWAG: 0%
  Applied independently to row 0 and row 1 per band per object
  Same user-defined color as transit matrix shading

**Hα-absent indicator:**
  Condition: object has Hα = 0 (e.g. PN, WR dominated by OIII/Hβ)
  Display: ⚠ hazard triangle shown in ALL band cells for that object
  Semantic: reference band absent — cross-object comparison invalid
  ⚠ and confidence shading are orthogonal — may appear together

  ha_absent flag supplied by Cathy's SNR engine. Display layer
  consumes it and does not derive this condition independently.

**Emission profile is context-independent:**
  Spectral data does not change with rig context selection.
  Only the transit/visibility sub-panel responds to rig context.

---

### 299.5 — Bidirectional Object Binding: List ↔ SkyVu (LOCKED)

The left panel object list and the SkyVu dome renderer maintain
bidirectional binding. One active object at a time.

**List → Dome:**
  Selecting an object in the left panel (SC column click):
    - Object marker highlighted on dome
    - Visibility arc rendered for that object
    - Arc reflects active rig context (horizon polygon applied)
    - Dome does not scroll or reposition — object marker appears
      wherever it sits in the current dome orientation

**Dome → List:**
  Clicking an object marker on the dome:
    - List scrolls to reveal that object's row
    - Row highlighted as active object
    - Emission profile and transit data update to reflect that object
    - Previous active object deselected
    - Sequential: click A → list shows A. Click B → list shows B.
      A is no longer highlighted. One active object at any moment.

**No multi-select on dome:**
  Dome click always selects one object — the clicked marker.
  Multi-object display on dome (all SUD objects visible as markers)
  is the passive state. Active selection is always single-object.

**SkyVu as spatial index:**
  The dome functions as a spatial navigation device into the list.
  Novice users who understand RA/Dec intellectually but not visually
  can use the dome to locate objects in their actual sky and then
  read the list data for those objects.

  "Point at the sky, read the data" — the dome is the index,
  the list is the reference.

---

### 299.6 — SkyVu Context Synchronization

SkyVu rendering state is driven by the active context:

**Home Site Context:**
  - Generic dome rendering — no horizon polygon
  - No visibility arc (no rig context)
  - Object markers shown at correct RA/Dec positions
  - Dark hours based on home site coordinates

**Rig Context (Transit or Rising):**
  - Selected rig's horizon polygon rendered
  - Active object's visibility arc rendered
  - Arc clipped by rig horizon polygon
  - Dark hours synced to rig site coordinates
  - Pine tree / obstruction spikes visible in horizon polygon

**Multi-window visibility:**
  SkyVu shows ALL visibility windows for the active object.
  Where the transit matrix shows total hours (aggregate),
  SkyVu shows the actual arc geometry including gaps from
  horizon obstructions. This is how the user manages obstructed
  windows — by selecting alternative targets for the gap period.
  The matrix motivates, SkyVu enables.

---

### 299.7 — Module vs Discovery Differences

Both Objects and Discovery use this right panel architecture.
Key differences:

  Objects:    SUD-resident objects — rig shading fully available
  Discovery:  Provisional SCD candidates — Home Site Context only
              No rig shading in Discovery (objects not yet in SUD,
              no committed rig context)
              SkyVu available in Discovery for spatial prospecting

---

### 299.8 — Action Items

**Cathy (SkyVu):**
  - Bidirectional binding: list selection → dome marker + arc
  - Dome click → list scroll + row highlight
  - Rig horizon polygon rendering in Rig Context
  - Multi-window arc geometry (all windows, not just first)
  - Dark hours sync to active context (Home Site or Rig site)

**Cathy (Right Panel):**
  - Emission profile: 8 bands × 50px, two-row cells
  - Confidence shading per band per object
  - ⚠ triangle on ha_absent objects
  - Transit matrix: 12 months × 60px, two-row cells
  - Cell shading in Rig Context only (urgency signal)
  - Synchronized scrolling with left panel

**Jim:**
  - Ensure visible_days_per_month is available per object per rig
    from skypix_vis.db dec-band tables
  - Confirm transit time for current planning date is queryable
    per object per rig context

**Clyde:**
  - Wire rig tabs into Objects module left strip (80px, same pattern
    as Discovery)
  - Wire rig tab selection to update transit time, Row 1, shading,
    and SkyVu horizon simultaneously
  - Wire active object state as shared signal between list and SkyVu
  - Ensure home site transit data stored in SUD at ingestion time
  - Confirm DST parameter available from rig record for transit
    time calculation in both Home Site and Rig contexts

---

*Section 299 locked 2026-04-18.*
*Right panel architecture, rig context model, and bidirectional*
*SkyVu binding all canonical from this section forward.*
