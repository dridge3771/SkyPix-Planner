## Section 301 — Right Panel Toggle Workflow, Selection Model, and Planner Assignment (LOCKED 2026-04-19)

---

### 301.1 — Four Right Panel States

The right panel (1120px) cycles through four distinct views via the
toggle button (upper right, opposite the logo). Each panel occupies
the full 1120px width. No two panels are shown simultaneously in
any module.

**Panel 1 — Transit/Rising Matrix**
  Seasonal observability data for all objects in the left panel.
  Context-dependent per active rig selection (Section 299):
    Home Site Context: transit time HH:MM, visible hours, shading
    Rig Transit: rig-specific transit time, visible hours, shading
    Rig Rising: rising phase entry time, visible hours, shading
  Full SUD shown — all objects present.

**Panel 2 — Emission Profile**
  Spectral characterization data.
  8 bands: Cont · OII · Hβ · NII · Hα · OIII · SII · IR
  Per object row:
    Row 0: relative band strength 0–100 (Hα=100 reference)
    Row 1: estimated flux in Rayleighs
  Confidence shading per band per object (L3→L0→L− opacity scale)
  ⚠ triangle when ha_absent = true
  Shows: only objects that survived the Transit Matrix selection gate
  (see 301.3 — Toggle State Transitions)

**Browser Interrupt (not a panel state) — Image Panel**
  Three image source rows per object:
    N  — NASA gallery image (Hubble, JWST, Chandra, etc.)
    AB — Astrobin URL (community imaging of this object)
    U  — User's selected URL (personal bookmark — any URL)

  V1 behavior:
    URL fields displayed, clickable → opens external browser
    Astrobin inline viewing deferred pending permission from Salvatore
    NASA and U images load inline via QWebEngineView if URL is direct
    image link, otherwise open external browser

  V2 behavior (post-permission):
    AB loads inline in QWebEngineView within the panel
    Full embedded browser experience, user never leaves SkyPix

  N·AB·U flags in left panel column are the at-a-glance indicator
  of which image sources are populated for each object.

**Panel 3 — SkyVu**
  Full 1120px dome renderer.
  Projects SC-selected objects as markers with visibility arcs.
  Retains unselected objects in left panel list for opportunistic
  addition (see 301.4).
  Bidirectional binding: list selection ↔ dome marker (Section 299.5)
  SkyVu is the final action panel — spatial commitment and
  planner assignment occur here.

---

### 301.2 — Toggle Sequence and Behavior (LOCKED)

Toggle button cycles through three data panel states:

  Transit Matrix (1) → Emission Profile (2) → SkyVu (3) → Transit Matrix (1)

No reverse direction. Single toggle button, single direction.

Panel indicator: three dots or numbered indicator (1/2/3) adjacent
to toggle button showing current panel position.

**Browser interrupt behavior:**
  URL icon touch (N, AB, or U) in left panel:
    Saves current panel state (_prior_panel = 1, 2, or 3)
    Replaces right panel with embedded browser at that URL
    Browser is NOT a toggle state — has no position in 1→2→3 cycle

  Toggle while browser is showing:
    Returns to _prior_panel — whichever of 1/2/3 was last displayed
    Browser dismissed, prior panel restored exactly
    Toggle cycle resumes from that panel

  Rule: toggle while browser showing = return to last right panel.
  No exceptions. One rule.

**Toggle behavior table:**

  Current state        Toggle →
  Transit Matrix (1)   Emission Profile (2)
  Emission Profile (2) SkyVu (3)
  SkyVu (3)            Transit Matrix (1)
  Browser (interrupt)  Last panel shown (1, 2, or 3)

---

### 301.3 — Toggle State Transitions (Selection Gates)

The toggle is not just a display switch — it is a progressive
filter. Selection state at each panel determines what travels
forward to the next panel.

**Panel 1 → Panel 2 (Transit Matrix → Emission Profile):**
  Gate: only SC-selected objects from Panel 1 travel to Panel 2
  Unselected objects remain in the SUD — never lost
  Panel 2 shows the season-qualified subset only
  Use case: 500 SUD objects → user selects 20 promising this season
    → Panel 2 shows those 20 with their spectral data

**Panel 2 → Panel 3 (Emission Profile → Image Panel):**
  Gate: SC-selected objects from Panel 2 travel to Panel 3
  Unselected Panel 2 objects retained in list but not projected
  Panel 3 shows image sources for the spectra-qualified subset
  Use case: 20 season-qualified → 12 pass spectral review
    → Panel 3 shows images for those 12

**Panel 3 → Panel 4 (Image Panel → SkyVu):**
  Gate: SC-selected objects from Panel 3 projected on dome
  Unselected Panel 3 objects retained in left panel list
  Both projected and retained objects remain accessible in SkyVu
  Use case: 12 pass image review → projected on dome
    User can select retained objects to add to dome if needed

**Backward toggle — full restoration:**
  Toggle backward from Panel 2 → Panel 1: full SUD restored (500)
  All prior SC marks preserved — selections not cleared on back-toggle
  Toggle backward from Panel 4 → Panel 3: Panel 3 state restored
  The backward direction never loses work

**Panel 1 always shows full SUD:**
  Regardless of what state the user came from, Panel 1 always
  shows all SUD objects with SC marks preserved.

---

### 301.4 — SkyVu Selection Model

**Object markers in SkyVu:**
  All Panel 3 objects appear as markers on the dome:
    Green marker   = SC-selected (will be assigned on planner touch)
    Neutral marker = retained, available but not yet selected

**Selection gesture:**
  Windows: right-click on marker → toggles green/neutral
  Mac:     Cmd-click on marker → toggles green/neutral
  Right-click again on green marker → deselects, returns to neutral

**Bidirectional sync:**
  Right-click in SkyVu = SC column click in the left panel list
  Both toggle the same selection state
  Green marker ↔ SC column filled — same state, two representations

**SC column header:**
  Touch SC column header → selects ALL currently projected markers
  Second touch → deselects all
  Standard select-all / deselect-all behavior

**Retained objects:**
  Unselected (neutral) objects remain in left panel list
  User can right-click any retained object → turns green → available
  for planner assignment
  Use case: selected objects too spatially bunched →
    deselect one, select a retained object from a different sky region
    to improve session distribution across the meridian

---

### 301.5 — Planner Assignment Mechanism

**Touch-to-assign:**
  Planner tabs appear in the 80px left strip below the SUD tab
  Any planner tab is always a live assignment target
  With SC-selected (green) objects active:
    Touch a planner tab → those objects assigned to that planner
    Full object data copied to planner (not just primary_ids)
    Planner has instant access to spectra, transit data, geometry

**Why full data copy (not reference):**
  User needs instant access to spectra, transit times, band
  strengths, confidence values without re-querying the SCD
  Planner is a self-contained snapshot at assignment time
  If SCD updates after assignment, planner retains its snapshot
  LFU contributions can update planner data — V2

**Multi-planner assignment in one SkyVu session:**
  Multiple planner tabs visible simultaneously in left strip
  User right-clicks object A → green → touches 60° PA planner → assigned
  User right-clicks object B → green → touches 120° PA planner → assigned
  Each touch assigns only the currently green objects to that tab
  Other projected objects unaffected
  One SkyVu session can populate multiple planners simultaneously

**Subsequent assignment to existing planner:**
  A planner tab is always available as an assignment target
  Later SkyVu sessions can assign additional objects to any
  existing planner by selecting and touching the tab
  The planner accumulates objects across multiple sessions

---

### 301.6 — Planner Creation Paths

Two distinct paths to create a planner. Both produce identical
planner structure.

**Path A — From SkyVu (populated planner):**
  1. User has SC-selected objects in SkyVu
  2. Touch the Planner tab (below SUD tab in left strip)
  3. Prompt: planner name (text field) + color picker
  4. Confirm → planner created AND populated with selected objects
  5. New planner tab appears in left strip, color-coded

**Path B — From Rig Kit (empty planner):**
  1. User clicks Create Planner in Rig Kit module
  2. Prompt: planner name + color picker + rig assignment
  3. Confirm → empty planner created
  4. Planner tab appears in left strip across all object modules
  5. User assigns objects later via touch-to-assign from any module

**The Planner tab in the left strip is the same target regardless
of creation path.** Once created, it receives objects from any
module — Discovery, Objects, or SkyVu.

---

### 301.7 — Workflow Summary (End to End)

**The five-gesture planning session:**

  1. Panel 1 (Transit Matrix)
     Browse full SUD, SC-select season candidates
     "What's up this season / this week?"

  2. Panel 2 (Emission Profile)
     Season-selected objects only, SC-refine by spectral fit
     "Which of these match my equipment and targets?"

  3. Panel 3 (Image Panel)
     Spectra-qualified objects, confirm with reference images
     "What does this actually look like? Is it worth my time?"

  4. Panel 4 (SkyVu)
     Image-confirmed objects projected on dome, right-click to select
     Check spatial distribution, swap if bunched
     "How does this fit my session tonight?"

  5. Touch planner tab
     Green-selected objects assigned to planner with full data
     "Done — let's image."

**Total gestures from cold start to populated planner:**
  SC selections + one toggle button + one planner tab touch.
  The workflow is the interface.

---

### 301.8 — Module Applicability

| Feature | Discovery | Objects | Planners |
|---|---|---|---|
| Panel 1 Transit Matrix | ✓ | ✓ | — |
| Panel 2 Emission Profile | ✓ | ✓ | — |
| Panel 3 SkyVu | ✓ | ✓ | ✓ |
| Browser interrupt (URL icon) | ✓ | ✓ | ✓ |
| Toggle sequence | 1→2→3→1 | 1→2→3→1 | 3 only* |
| Selection gates | ✓ | ✓ | — |
| Planner assignment | ✓ | ✓ | n/a |

*Planners module: SkyVu is the primary right panel view.
Exposure Grid (Section 271) is the second toggle state for Planners.
Planners does not have Transit Matrix or Emission Profile panels —
those belong to the evaluation modules (Discovery and Objects).

Browser interrupt available in all modules — URL icon touch always
saves current panel and loads embedded browser. Toggle always returns
to last panel shown.

---

### 301.9 — Action Items

**Cathy:**
  - Four-state toggle button with panel indicator
  - Panel 1: Transit Matrix (full SUD, per 299.3)
  - Panel 2: Emission Profile (filtered by Panel 1 selection)
  - Panel 3: Image Panel (N/AB/U per object, URL fields + QWebEngineView)
  - Panel 4: SkyVu with right-click/Cmd-click selection
  - SC column header select-all / deselect-all
  - Planner tab touch → assignment with full data copy
  - Backward toggle restores full prior panel state
  - Green marker ↔ SC column bidirectional sync

**Jim:**
  - Planner schema to hold full object data snapshot (not just foreign key)
  - Astrobin URL field, NASA URL field, User URL field in SUD schema
  - Confirm object data copy at assignment time includes all fields
    (spectra, transit, geometry, band strengths, confidence)

**Clyde:**
  - Wire toggle state machine into DiscoveryManager and ObjectsManager
  - Wire planner tab touch to assignment handler
  - Confirm full data copy logic at assignment time
  - Wire SC header select-all to SkyVu marker state

---

*Section 301 locked 2026-04-19.*
*The workflow is the interface.*
*Five gestures from cold start to populated planner.*
