## Section 300 — Object Panel: Column Schema, Notes Field, and Community Contribution (LOCKED 2026-04-18)

---

### 300.1 — Left Panel Column Schema (LOCKED)

Canonical columns for Discovery, Objects, and Planners left panel.
Width: 720px total. Two-line minimum row height (44px).

  SC        — selection indicator (28px)
  ID/Name   — primary_id line 1, common_name line 2 (180px)
  RA/Dec    — ra_deg line 1, dec_deg line 2 (110px)
  Size      — major_axis_arcsec (arcmin display) (60px)
  PA        — position_angle_deg (40px)
  Class     — skypix_object_class (52px)
  Notes     — three-zone field (stretch)
  Image URLs — N·AB·U flags (52px)

ES column: Planners only (not present in Discovery or Objects).

Mouse-over behavior on Class field:
  Displays OType ed card for the object's specific OType.
  Content: astrophysics description + imaging notes (Jim's content,
  knowledge vault resident). Read-only. Zero-latency — local cache.

---

### 300.2 — Notes Field: Three-Zone Design (LOCKED)

The Notes field is a single visual field containing three distinct
zones rendered inline:

**Zone 1 — ⓘ icon (left edge of field):**
  Click → opens bi-panel display overlay:
    Left panel: OType imaging strategy
      - Source: knowledge vault (Supabase), OType-specific
      - Read-only
      - Content: recommended imaging approach for this object type
        (written by Jim, community-curated over time)
    Right panel: Community compilation table
      - Aggregated structured submissions from all contributors
        for this specific object
      - AI-summarized, volunteer-curated
      - Columns: Strategy | Common Challenges | Avg Results | Next Time
      - Empty until first submission promoted to SCD

  Zero-latency requirement: OType strategy cached locally.
  Community compilation fetched from Supabase on open.

**Zone 2 — Freeform text area:**
  User's private imaging journal for this object.
  No structure, no format, no submission obligation.
  SUD-resident — never shared, never submitted automatically.
  Editable at any time.
  "My notes for my benefit."

**Zone 3 — ↗ icon (right edge of field):**
  Community contribution mechanism. V2 implementation.
  V1: icon present, grayed, tooltip "Community contribution — V2"

  Post-V2 lifecycle:
    Pre-submission:  ↗ → opens blank contribution form
    Post-submission: ↗ → opens submitted form (read/edit) +
                         curation status badge
    Post-curation:   ↗ → opens submitted form +
                         "Promoted to SCD ✓" confirmation

  The submitted form remains linked to the Notes field permanently.
  User can review what was contributed from the same icon.
  Zones 2 and 3 are completely independent — freeform text is
  never submitted automatically, contribution is always a
  deliberate separate act.

---

### 300.3 — Contribution Form Structure (V2)

Structured form opened via Zone 3 ↗ icon. Five fields:

**Equipment (auto-populated from carriage — no user entry):**
  Rig, camera, filter set, exposure plan from planner commit record.
  User sees it but cannot edit it — it is the factual record.

**Strategy (short text):**
  What approach did I take?
  Examples: narrowband Ha first, LRGB mosaic, lucky imaging on
  poor seeing nights, Ha+OIII only due to LP.
  Character limit: ~280 (one deliberate paragraph).

**Challenges (checklist + short addendum):**
  Checklist items (multi-select):
    □ Sky conditions (clouds, transparency)
    □ Frost / dew
    □ Wind / vibration
    □ Object elevation (low horizon)
    □ Guiding issues
    □ Light pollution event
    □ Equipment failure
    □ Other
  Addendum: short free text for specifics (~140 chars)

**Results (scale + short text):**
  Scale: 1–5 (1=poor, 3=acceptable, 5=excellent)
  Short text: what specifically worked or didn't (~140 chars)
  Examples: "SNR exceeded expectation on OIII",
            "Ha detail lost to LP on west side"

**Next time (short text):**
  What would I change to resolve unmet challenges? (~280 chars)
  This is the highest-value field for the community — concentrated
  learning from failure and near-misses.

---

### 300.4 — Community Compilation Table (SCD side)

Displayed in the right panel of the ⓘ bi-panel overlay.
Aggregated across all promoted submissions for this object.

Columns:
  Strategy    — AI summary of submitted strategies, volunteer-curated
  Challenges  — most frequently checked items + notable specifics
  Results     — average score (N submissions) + notable outcomes
  Next Time   — most cited improvements, AI-summarized

Population:
  Empty until first submission is promoted to SCD.
  Updated each time a new submission is curated and promoted.
  AI summarization prompt: "Summarize this user's imaging experience
  with [Object] for other astrophotographers" — volunteer reviews
  before promotion.

---

### 300.5 — Carriage Concept (V2 Stub)

The carriage is the structured container that travels with an
imaging project from plan to result. Four compartments:

  1. Exposure Plan       — from planner commit record
  2. Imaging Scheduler Log — from automation software (NINA log)
  3. Processing Results  — from PixInsight/processing analysis
  4. Observer Notes      — from contribution form (Section 300.3)

The ↗ contribution icon links Zone 3 to the carriage for this
object. The carriage is the submission unit — not the Notes field.

LFU pipeline (V2):
  Carriage submitted → volunteer curator reviews all four compartments
  → extracts signal → promotes to SCD:
    Confirmed band strengths → updates presence_mask + strength values
    Confirmed imaging conditions → updates confidence tier
    Observer notes → promoted to community compilation table
    SEA credits awarded to contributor AND curator

No implementation authorized until SkyPix beta is complete.
This section stubs the concept so V1 UI reserves the right real estate.

---

### 300.6 — SEA Credit Mechanism (V2)

Community participation earns SEA (SkyPix Experience Award) credits:

  Contributor: submits a carriage via ↗ icon → credits awarded
  Curator: promotes a submission to SCD → credits awarded
  Milestone: object reaches N promoted submissions → badge awarded

Curation as a volunteer role:
  Volunteers access a curation queue (web interface, not desktop app)
  Each submission shows all four carriage compartments
  Curator edits AI summary, confirms data quality, promotes or rejects
  Rejected submissions returned to contributor with curator notes

This creates a self-sustaining knowledge loop:
  User learns from vault → images → contributes → volunteer curates
  → community benefits → contributor and curator earn recognition
  → community grows

---

### 300.7 — Implementation Notes

**V1 deliverables (Cathy):**
  - Revised column schema per 300.1 in all three modules
  - Class field mouse-over → OType ed card (local cache)
  - Notes field Zone 1 ⓘ icon → bi-panel overlay
    (OType strategy panel + empty compilation panel placeholder)
  - Notes field Zone 2 freeform text, editable, SUD-persistent
  - Notes field Zone 3 ↗ icon, grayed, V2 tooltip
  - Bi-panel overlay dismisses on click-outside

**V2 deliverables (Jim + Cathy):**
  - Contribution form (300.3) wired to carriage
  - Supabase curation queue table
  - Community compilation table (300.4) populated from promoted data
  - AI summarization prompt integration
  - SEA credit tracking in license base
  - Volunteer curation web interface

**Jim (V1):**
  - OType imaging strategy content for knowledge vault
    (doc_id pattern: otype_strategy_{otype_code})
  - Community compilation table schema in Supabase (empty, ready for V2)

---

### 300.8 — Action Items

**Cathy (V1):**
  - Implement revised column schema (remove Maj/Min, add Size single col)
  - Class field mouse-over OType ed card
  - Notes three-zone field layout
  - ⓘ icon bi-panel overlay (strategy + placeholder compilation)
  - Freeform text area, SUD-persistent
  - ↗ icon grayed with V2 tooltip

**Jim (V1):**
  - Write OType imaging strategy content for knowledge vault
  - Create community_compilation table schema in Supabase
  - Confirm doc_id naming convention for OType strategy docs:
    otype_strategy_{otype_code} (e.g. otype_strategy_SNR)

**Clyde:**
  - Wire Notes Zone 2 text persistence to SUD per object
  - Confirm ⓘ icon fetches correct OType strategy doc from vault
    based on object's simbad_otype field

---

*Section 300 locked 2026-04-18.*
*V1: column schema + Notes zones 1 and 2 + grayed Zone 3.*
*V2: contribution form + carriage + curation queue + SEA credits.*
*The community knowledge loop is the long-term value proposition.*
