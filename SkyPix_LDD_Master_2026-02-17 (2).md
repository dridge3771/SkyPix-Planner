# SkyPix Living Design Document (LDD)
## Master Composite — 2026-02-17
**Status:** Single Authoritative Master — Fully Replaces All Prior LDDs and Addenda
**Owned by:** Claude (Architecture) on behalf of David (SkyPix Architect)
**Method:** Additive, not digestive. Nuance preserved. All prior canon absorbed.
**Canon Labels:** LOCKED | INTERIM CANON | DEFERRED | PENDING TEAM REVIEW

---

## PRIME DIRECTIVES (Operational Canon — Permanent)

1. **The LDD is the sole continuity mechanism.** Conversation history is non-authoritative. If it isn't in the LDD, it isn't canon.
2. **Append-only canon.** New sections added or prior text explicitly superseded. No silent rewrites.
3. **No silent regressions.** If code changes affect established behavior, it must be called out and justified in the LDD.
4. **Full-file handoffs by default.** Unless a change is trivially obvious, provide complete overwrite-ready files.
5. **Website is descriptive only.** All functional planning tools live behind registration-locked portal.
6. **Domain semantics are canonical.** Explore/Engage/Experiment/Enhance/Exhibit mapping is locked.
7. **LFU is baseline-relative and multiplicative.** Any baseline change requires rebase logic.
8. **Institutionalize decisions.** Any design choice that prevents future confusion belongs in the LDD.
9. **Integrate new sections into this single master LDD as a matter of course.** No separate addenda files.
10. **Claude owns LDD maintenance** as Project Architect effective 2026-02-17.

---

# PART I — SYSTEM ARCHITECTURE

## 1. Authority Boundaries (LOCKED)

| System | Authority |
|---|---|
| **Rig Kit** | Sole authority for celestial geometry, horizons, declination bands, visibility arcs |
| **Planner** | Decision engine only. No live geometry calculations. |
| **SCD (SkyPix Curated Database)** | Authoritative object physics, metadata, baseline emission profiles |
| **SUD (SkyPix User Database)** | User-owned objects, emission profiles, LFU coefficients. Resident on user PC. |
| **Admin Functions** | Curated data maintenance only. Never user-facing. |

## 2. Compute Architecture (LOCKED — 2026-02-17)

All compute-intensive operations are client-side. Supabase serves data only.

**Computed once at object entry, stored per object:**
- Transit times (RA-derived, universal — longitude-adjusted at display time)
- 12-month observability windows

**Computed once at rig creation, stored per rig:**
- Horizon polygon
- Declination band visibility arcs (horizon polygon × dec bands)
- Dark time windows (latitude + longitude)
- Longitude offset from home site

**Computed per object per rig (stored in RIG_OBJECT junction):**
- Observability windows (dec band arc + transit time + dark time windows + longitude offset)

**Computed live in Rig Planner (the only real-time heavy lifting):**
- SNR calculations
- Total exposure per filter (hours)
- Subframe duration per filter

**Key principle:** Visibility arcs are declination-band dependent, not per-object. All objects within a dec band share the same arc for a given rig. Transit time is a property of the object (RA only), not the rig.

---

# PART II — OBJECT UNIVERSE ARCHITECTURE

## 3. Four-Tier Object Universe (LOCKED — 2026-02-17)

SkyPix adopts a four-tier object universe. Every object from every catalog has a defined home, promotion pathway, and user-facing behavior. The ONF (Object Not Found) problem is permanently resolved.

```
QUARANTINE → CATALOG HOLDING → RAW → SURFACE
             (promotion flows upward)
```

### 3.1 SURFACE (SCD)
**Purpose:** Planner-grade objects. Full SNR guarantee.
**Admission:** Meets physical threshold + community consensus from RAW.
**Planner:** Full SNR, exposure recommendations, subframe durations, Color Matrix shading, positional planning.
**Visual (Confidence Paint):** Camera total time cell at 50% camera color. Filter total exposure & subframe duration cells painted by confidence tier: L3 @50%, L2 @35%, L1 @20%, L0 @5%. X (Quarantine) @50% orange (100% orange suppressed — obscures text).
**Promotes from:** RAW via community consensus.

### 3.2 RAW
**Purpose:** Catalog-sourced, SIMBAD-validated, meets physical threshold. Promotable.
**Admission:** Authoritative catalog source + RA/Dec + otype resolved + meets 16"@3000mm physical threshold.
**Planner:** Positional planning. SNR available if spectral profile present.
**Promotes from:** CATALOG HOLDING if community contribution resolves physical threshold.
**Promotes to:** SURFACE via community consensus.

### 3.3 CATALOG HOLDING
**Purpose:** ONF firewall. Known catalog objects blocked from RAW promotion.
**Admission:** Authoritative catalog name + RA/Dec. No physical threshold gate on entry.
**Planner gives:** Full positional planning — visibility arc, rise/set, meridian, horizon clearance, moon separation, mid-month observability matrix. No SNR. No exposure. No Color Matrix.
**Visual:** Total exposure + subframe durations painted ORANGE. Badge: "Positional data only — exposure planning unavailable."
**Promotes to:** RAW if community contribution satisfies physical threshold.
**Physical block sub-types:**
- *Confirmed physical:* Permanently below threshold. Contributions improve metadata but cannot overcome physics.
- *Data quality physical:* Appears below threshold due to incomplete catalog data. Corrected contribution may reveal threshold compliance → promotes to RAW.

### 3.4 QUARANTINE (UDQL — User Declared)
**Purpose:** User-declared objects with no catalog provenance. ONF escape valve.
**Admission:** User provides RA/Dec + SkyPix class. No catalog verification.
**Planner:** Positional planning + estimated spectral profile from declared class. Orange badge.
**Visual:** "User-contributed • Unverified spectral data."
**Promotes to:** Never auto-promotes. Admin may manually promote to Catalog Holding if catalog provenance subsequently established.
**LFU:** Excluded from Pass-2 and Pass-3. Never feeds statistical refinement.
**Limit:** 1,000 objects per user.

### 3.5 Physical Threshold Definition
**Reference instrument:** 16" aperture @ 3000mm focal length (f/7.4)
**Surface brightness floor:** ~25 mag/arcsec²
**Minimum angular size:** ~15-20" (below = stellar appearance, no imageable structure)

**Important:** Thresholds govern promotability only. Any object from any tier may be added to SUD and appear in Rig Planner. The tier governs SNR confidence, not access.

### 3.6 ONF Behavior (Complete Resolution)

| Scenario | Result |
|---|---|
| Object in SURFACE | Found. Full planner capability. |
| Object in RAW | Found. Positional + available spectral data. |
| Object in CATALOG HOLDING | Found. Positional only. Orange badge. |
| Object in QUARANTINE (shared) | Found. Orange badge. User-declared warning. |
| Object in none | UDO pathway offered. User declares → QUARANTINE. |

## 4. Database Architecture (PENDING TEAM REVIEW — 2026-02-17)

**Proposal under team review:** Single homogeneous `objects` table with `layer` classification field, replacing four separate tables. Key argument: one indexed lookup at object entry time (defining UX metric) vs. four-table UNION query. Promotion becomes an UPDATE, not a migration. Orphan problem cannot recur.

**Team brief issued:** Gemmi (canon integrity review) + Chatty (schema pathology review).
**Decision gate:** Blocking concern → revert to multi-table. No blocking concern → homogeneous table is canonical schema.

**Estimated total queryable universe:** ~270-280K objects across all four tiers.
**Supabase tier:** Free tier sufficient through beta and early paid user territory (~50K users). Pro tier ($25/mo) when community contribution activity scales.

## 5. Object Model (LOCKED)

- **SkyPix Object Class** (≤3 chars) is user-facing. Appears in SUD and Rig Planner.
- **SIMBAD otypes** are abbreviations only. Appear only in UI popups, never as planner logic drivers.
- Object Class may consolidate multiple SIMBAD otypes.
- **Terminology:** "Object types" are formally **SkyPix Object Classes**. Label-only change.

## 6. Catalog Coverage Commitment (LOCKED)

All nine catalogs fully represented across four tiers. No catalog object with valid RA/Dec is unhoused.

| Catalog | VizieR Table | Primary Layer |
|---|---|---|
| NGC/IC | VII/118/ngc2000 | RAW/SURFACE |
| Sharpless (Sh2) | VII/20/catalog | RAW/SURFACE |
| RCW | VIII/2A/rcw | RAW/SURFACE |
| Abell PN | V/84/catalog | RAW/CATALOG HOLDING |
| Cederblad | VII/231/catalog | RAW/SURFACE |
| vdB | VII/21/catalog | RAW/SURFACE |
| Dias OC | B/ocl/clusters | RAW/CATALOG HOLDING |
| LBN/LDN | VII/9A / VII/7A | RAW/SURFACE |
| WR/Barnard | III/215 / VII/220A | RAW/SURFACE |

**Doctrine:** "Inclusive acquisition, conservative promotion." RAW may grow to 250K+ objects. SURFACE must remain imaging-relevant.

---

# PART III — OBJECT INGESTION

## 7. Object Ingestion Use Cases (LOCKED)

### 7.1 Use Case 1 — Single Object Entry
1. User enters Object ID or Common Name.
2. SCD lookup (across all four tiers) returns location, size, object class, images, SIMBAD otypes.
3. User confirms.
4. Transfer to SUD not complete until:
   - Decimal → sexagesimal conversion
   - 12-month transit times (home location, RA-derived)
   - Image URLs transferred
   - SIMBAD otypes stored for popup disclosure
   - Notes transferred
5. All post-transfer operations locked to ingestion transaction.

### 7.2 Use Case 2 — Batch Ingestion
- User constrains by Object Class and dark-hours transit window (N months).
- UI presents selectable list: Name, ID, Sexagesimal RA/Dec, Size.
- User selects subset before commit to avoid SUD bloat.

### 7.3 Use Case 3 — Object List / CSV Ingestion
- User supplies CSV or sheet. Selection pre-accomplished. Confirmation remains.
- Duplicate handling identical to other paths.

## 8. Duplicate Handling & LFU Scaling (LOCKED)

If duplicate found in SUD:
- Prompt: "Duplicate found — replace?"
- Replacement overwrites base emission profile.
- LFU coefficients scaled per-band to preserve learned signal:
  `C_new = C_old × (B_old / B_new)`
- User DB owns its emission profile. No links to SCD profiles persist.

---

# PART IV — RIG GEOMETRY & TEMPORAL MODEL

## 9. Rig Geometry Definitions (LOCKED)

- **Landscape Horizon:** Polygon (Az/Alt) defining object visibility.
- **Minimum Altitude:** User-defined constraint to reduce extinction/seeing.
- **Usable Horizon:** Higher of landscape horizon or minimum altitude, applied to declination band centerpoints.
- **Zenith Obstruction:** Contra-tripod projected onto zenith. Must be ≤ 89°.

## 10. Declination Bands (LOCKED)

- Bands start at celestial equator.
- Increment by band width (Rig Kit row 31) toward pole.
- Final band may be fractional.
- All objects within a band share identical visibility arcs for a given rig.
- Visibility arcs are horizon-declination band dependent — computed once per rig. Not per-object.

## 11. Visibility Arcs (INTERIM CANON)

- Values are hour angles, measured east-to-west with meridian as terminus.
- Stored as: East visibility arc + West visibility arc.
- Computed once per rig per declination band.
- Planner usage: Data lookup only. No rendering logic implied.

## 12. Temporal Model (INTERIM CANON)

### 12.1 Rolling 12-Month Computation
- Computed as rolling 12-month window.
- Recomputed when horizon, minimum altitude, or declination band width changes.
- Monthly recompute is user-confirmed.

### 12.2 Create Planner
- User selects start month via popup.
- Planner consumes rolling table starting at that month.

### 12.3 Rig Duplication for Projects
- "Add Duplicate" allows rigs to represent seasonal or project-specific planners.
- Duplicate must allow source rig selection.

## 13. Lunar Occlusion (LOCKED)

### 13.1 Model
- Continuous angular model using Euler-derived chord width. No lookup tables.

### 13.2 Core Test
- Does Moon's RA during dark hours intersect the object's ±LAA window?
- Daylight-only encounters auto-eliminate.

### 13.3 Required Parameters
- From Rig Kit: LAA, min observable time, darkness convention, horizon, lat/long.
- From Object DB: RA, ecliptic latitude.

**Note:** Lunar path calculations (RA+Dec across multiple nights) are compute-non-trivial. Meteoblue astronomy API to be investigated for seeing forecasts. Lunar occlusion for multi-night projection is V1.1 scope.

---

# PART V — PLANNER

## 14. Planner Responsibilities (LOCKED)

Planner determines:
- Observability
- Rising or transit timing
- Desired vs achievable SNR
- Exposure strategies per filter/camera
- Alternative SNR under constraints

Planner never performs celestial geometry. Planner reads pre-computed values from SUD.

## 15. V1 Rig Planner Scope (LOCKED — 2026-02-17)

V1 Rig Planner is a liberation of the existing GAS design from the spreadsheet paradigm. It does not reimagine the design — it presents the same design without spreadsheet constraints.

**V1 delivers:**
- The designed Rig Planner as a web component
- Color Matrix rendered with real color (not cell fills)
  - **Device Color Matrix (LOCKED — 2026-02-18):** CSS-based replacement for the GAS distributed onEdit color scheme. Color logic migrated from spreadsheet event handlers into a single CSS architecture. Relationship mapping (Chatty, Feb 18) defined forward propagation from Rig/Camera/Filter Kits and back-propagation to Rig Planner.
- Tap object → detail view without leaving planner
- Dynamic filtering (show tonight's best window)
- Mid-month observability matrix as visual timeline

**V1 does NOT include (deferred to V1.1/V2):**
- Real-time weather overlay
- Hourly seeing forecast
- Lunar avoidance angle per object for tonight
- Multi-night projection view
- Tonight's real times (V1.1 — architecturally free, date parameter only)

## 16. UI Philosophy (LOCKED — 2026-02-17)

**North star:** SkyPix is the bridge between the Sky (curiosity) and the Equipment Cabinet (capability).

Every screen answers one of two questions:
- *What can I image?* (Sky filtered through Cabinet capability)
- *How should I image it?* (Cabinet applied to Sky target)

**Visual language:** Dark backgrounds, sky-appropriate color palette. Users from Stellarium, SGP, NINA should feel immediately oriented.

**Two UI personalities that coexist:**
- **Cabinet** (Rig Kit, Camera Kit, Filter Kit) — precise, technical, form-driven, familiar
- **Sky** (Object entry, Rig Planner) — exploratory, visual, filter-driven, evocative

**SkyPix is not:** a star atlas, equipment store, social network, or image gallery.

**Team roles for UI:**
- Claude — information architecture, user flow, screen hierarchy
- Chatty — component design and implementation
- Gemmi — domain accuracy review of data presentation

---

# PART VI — SPECTRAL ENRICHMENT & EMISSION PROFILES

## 17. Emission Profile Confidence Levels (LOCKED)

| Level | Source | Timeline |
|---|---|---|
| L0_mapped | Expert judgment + astrophysical principles | Launch (Feb 2026) |
| L0_inferred | Manual override for known objects | Launch |
| L1 | Peer-reviewed spectroscopic measurements | 3-6 months post-launch |
| L2 | Community imaging data + statistical analysis | 12+ months post-launch |
| X | User-declared (Quarantine only) | On UDO creation |

## 18. Emission Profile Data Acquisition (LOCKED)

### 18.1 Astrobin Integration (Primary Bootstrap Method)
- Integration times as crowdsourced proxy for emission strength
- Astrophotographers allocate more time to weaker lines → ratios converge across images
- Chrome Extension (Manifest V3) for manual, single-page extraction
- No bulk crawling. Attribution always. TOS-compliant.

### 18.2 Filter Normalization Canon
| Variants | Canon |
|---|---|
| Ha, H-alpha, Hα | Ha |
| OIII, O3, [OIII] | OIII |
| SII, S2, [SII] | SII |
| L-Extreme, Dual-Band | Ha+OIII (simultaneous — flagged `balanced`) |

### 18.3 Confidence Classification
| Level | Criteria |
|---|---|
| High | n ≥ 5 AND σ < 0.2 |
| Medium | n = 3-4 OR σ = 0.2-0.4 |
| Low | n < 3 OR σ > 0.4 |

### 18.4 Emission Profile Output (Per Object)
- samples_analyzed, emission_ratios (ha/oiii/sii median + std_dev)
- planning_ratios, confidence, min/max integration hours, notes

## 19. Pass Architecture (LOCKED)

| Pass | Confidence | Source | Timeline |
|---|---|---|---|
| Pass-1 | L0 | Expert judgment, astrophysical principles | Now → Feb 20 |
| Pass-2 | L1 | Scientific literature (Gemmi review) | May-Sept 2026 |
| Pass-3 | L2 | Community imaging data / LFU statistical | Feb 2027+ |

**95% emission profile coverage achieved across 77K+ objects (current state).**

## 20. LFU Canon (LOCKED)

### 20.1 Core Principle
LFU = Learning From Using. User imaging session results feed back to refine SNR models and emission profiles.

- Multiplicative system: `Baseline × Coefficient → Effective emission`
- Coefficient k = 1.20 means "this line is ~20% stronger than baseline predicts"
- Rolling average (20 samples). Not driven by single samples.

### 20.2 Rebasing Formula (Universal, Unconditional)
On any baseline change:
```
k_new[line] = k_old[line] × (B_old[line] / B_new[line])
```
Example: baseline +25%, coefficient +20% → k_new = 1.20 / 1.25 = 0.96 (−4%)

### 20.3 Edge Cases (Deterministic — No Manual Review)
- Line missing in new baseline OR new baseline = 0 → remove coefficient
- Old baseline = 0 → remove coefficient
- No clamping at data layer (trust gating belongs in planning layer)

### 20.4 Terminology
- **REBASE:** Coefficient transform preserving effective predictions when baselines change.
- **RESEED/RETRAIN/BLEND/FORGET:** Intentional change to effective predictions. Out of scope until LFU active.

---

# PART VII — PRODUCTION MINER & DATABASE MAINTENANCE

## 21. Canonical Ingestion Workflow (LOCKED — Phase 2A Canon)

### Phase 1 — Coverage Audit (Read-Only)
- Force full fetch (ROW_LIMIT = -1)
- Use ICRS coordinates only
- Match radius = 60 arcseconds
- No writes during audit
- Outputs: `<catalog>_missing.json`, `<catalog>_coverage_report.json`

### Phase 2 — Alias-or-Add
- If separation ≤ 60": add alias token, append imaging_notes (additive only)
- If no match: create new object at appropriate tier, apply type_default emission profile
- Guardrails: skip non-finite coordinates, record collisions

### Phase 3 — Reconcile (Optional)
- Coordinate refinement, token-based recovery
- Guard max separation = 30 arcminutes
- In-place Surface correction

### Structural Guardrails (Non-Negotiable)
1. No destructive emission changes during Phase-2A
2. imaging_notes are additive only
3. Alias additions are additive only
4. Always re-run coverage audit after apply
5. Confirm Surface object growth explicitly

## 22. Collision-Proof Miner Canon (LOCKED)

- Collision-proof IDs via `source_uid` (catalog + table + row_key)
- Profile IDs = source_uid + `:L0`
- INGEST_RUN_ID stamped on every written doc
- JSON exports filtered to current run only (run-scoped exports)
- Resolution: last-write-wins by process order (deterministic, no Admin adjudication)
- Collision reporting required: timestamp, catalog, rows_fetched, collision_count, resolution_method

## 23. Current Database State (2026-02-17)

- **SURFACE:** ~77K objects with L0 spectral profiles, 95% emission coverage
- **RAW:** ~181K objects (SIMBAD-validated)
- **Orphan recovery pending:** ~10,630 recoverable objects (Master Sidebar script — Chatty)
- **Sharpless:** 313 catalog → 135 in RAW → 9 in SURFACE; 126 blocked; 178 missing from RAW (seed backfill pending)
- **Phase 2A catalogs integrated:** Sharpless, RCW, Gum, WISE HII, Barnard, LDN, LBN
- **Pending:** Abell PN, Harris GC, Abell Galaxy Clusters

---

# PART VIII — SEA BADGE SYSTEM

## 24. SkyPix Emission Ambassador (SEA) — 10-Tier Pleiades Badge (LOCKED — 2026-02-17)

### 24.1 Badge Design
Badge is an SVG canvas showing the Pleiades asterism outline. Each tier achievement illuminates ONE star in its actual astronomical position within the cluster map. Not a row of stars — a spatial constellation that reveals itself progressively.

### 24.2 Award Sequence and Positions

| Tier | Star | Designation | Position | SEA Points |
|---|---|---|---|---|
| 1 | Merope | 23 Tau | Outer SW | 10 |
| 2 | Maia | 20 Tau | Outer NW | 25 |
| 3 | Electra | 17 Tau | Outer NE | 50 |
| 4 | Taygeta | 19 Tau | Mid SE | 100 |
| 5 | Celaeno | 16 Tau | Mid E | 200 |
| 6 | Asterope | 21 Tau | Mid S | 350 |
| 7 | Atlas | 27 Tau | Inner NE | 500 |
| 8 | Pleione | 28 Tau | Inner E | 700 |
| 9 | Alcyone | Eta Tau | CENTER (brightest) | 1000 |
| 10 | M45 Complete | Full cluster | Nebulosity overlay | 1500 |

### 24.3 Pattern Recognition Journey
- **Tiers 1-6:** Pattern non-obvious (outer sisters, mid positions)
- **Tier 7 (Atlas):** "Moving inward toward parents..."
- **Tier 8 (Pleione):** "Parents before center!"
- **Tier 9 (Alcyone):** "The brightest at the heart!"
- **Tier 10:** Full cluster with nebulosity. Pattern revealed: outer sisters → parents → center.

### 24.4 SEA Point Awards
- **1 point:** Contribution (object entry with data)
- **3 points:** Refinement (improving existing record)
- **10 points:** LFU contribution (imaging session data submitted)

### 24.5 Workshop Scholarships
- Tier 3 (Electra): 1/year
- Tier 4 (Taygeta): 2/year
- Tier 5 (Celaeno): 3/year + 10% discount
- Tier 6 (Asterope): 5/year + 20% discount
- Tier 7 (Atlas): 8/year + 30% + Curator authority
- Tier 8 (Pleione): 12/year + 40% + Can host workshops
- Tier 9 (Alcyone): 20/year + 50% + Featured profile + Direct promote (limited)
- Tier 10 (Complete): Unlimited + 50% + 70% workshop revenue share + Admin review authority

---

# PART IX — WEBSITE (STARSHIP)

## 25. Starship Structural Invariants (LOCKED)

The public website uses a "Starship Lobby" metaphor with five domain doors. This is the marketing/public site. The Planner application lives behind ENGAGE (registration).

**Frozen geometry:**
- Starship Lobby: door ratios, spacing, aperture behavior, zoom mechanics — frozen
- Background sky: single, crisp, never scales or blurs independently
- Zoom anchor: 30% down from door center, outward bias, timing, easing — never change
- Domain Wall: original non-viewport-extended geometry + same translucency
- Domain aperture: single unioned geometry (circle dia=0.432×wallW + vertical strip width=0.28×wallW)
- No multiple masks, intersections, or negation stacking
- Aperture center: fully clear, no tint

**Domain structure:**
- Two columns as two cards per domain
- Exactly one card per column
- Cards never overlap central aperture
- One master scroll mechanism — cards never retain independent scroll state
- Navigation uses back-stack; cleared on Return to Starship

**Domain semantic mapping (LOCKED):**
- **EXPLORE** — Product description (high/mid/technical levels)
- **ENGAGE** — Registration, EULA, keys, getting started
- **EXPERIMENT** — Simulate imaging results before committing to approach
- **ENHANCE** — Automated imaging and processing feedback to refine simulations (LFU/SEA)
- **EXHIBIT** — User image showcase, community-sourced tips and techniques

**Bottom panes (four, canonical):**
- Attribution (Explore door): 3 lines, reduced font
- Return to Starship (Experiment door): bold uppercase
- Viewing Guidance (Enhance door): "For best viewing, set browser zoom to 100%"
- Sound Toggle (Exhibit door): action-oriented labels

**Inter-domain linking:**
- Permitted only inside Domain experience (post-zoom)
- Back-stack preserves scroll position on return
- Back-stack cleared on Return to Starship

**Desktop-first. Mobile responsiveness must not alter geometry or behavior.**

---

# PART X — PRODUCT & STRATEGY

## 26. Pricing (LOCKED — 2026-02-17)

- **90-day full-feature trial** (no credit card)
- **V1:** $49 one-time purchase
- **V2 upgrade:** $29 (LFU + learning loop + community-validated spectral data)
- **Freemium tier:** Discontinued

**Rationale:** Astrophotographers prefer ownership over subscription. Seasonal usage makes monthly fees inappropriate. $29 upgrade justified by LFU — V2 is a tool that gets smarter with use. V1 without upgrade remains static but functional.

## 27. AstroBin Collaboration Strategy (LOCKED)

Sequence:
1. **REWARD** — Outbound object gallery URLs driving traffic to AstroBin
2. **OPPORTUNITY** — SEA pilot (3-month membership for early contributors)
3. **ASK** — Future metadata access proposal to Salvatore Iovene

**Non-negotiable commitments:**
- No scraping without permission
- Attribution always (source URLs, photographer credit)
- Transformative use only (aggregated statistics, not data mirrors)
- No gallery hosting or image mirroring
- Cease immediately if requested
- Emission profiles open to all community

**Partnership email:** Approved draft. Send when SkyPix has working Capture Card examples, functional NINA/PixInsight parsers, and 3-5 real emission profile refinements from alpha users.

## 28. ROO White-Label (DEFERRED — V3)
- Requires LFU certification
- Deferred pending V1 proven and V2 data collection established

## 29. Version Roadmap

| Version | Scope |
|---|---|
| **V1** | Core planning architecture, multi-rig/project, SCD, exposure calculations, web app migration of GAS design |
| **V1.1** | Tonight's real times, weather overlay, seeing forecast, lunar avoidance per object, multi-night projection |
| **V2** | LFU (Learning From Using) — actual session data ingestion, SNR refinement, community-validated spectral data |
| **V3** | Remote observatory integration, automated session planning, ROO white-label |

---

# PART XI — GOVERNANCE & TEAM

## 30. Three-Tier Governance Model (LOCKED)

| Tier | Type | Authority |
|---|---|---|
| 1 | Strategic Product Decisions | David (Architect) — final authority |
| 2 | Technical Architecture Decisions | Claude (Architect) — proposes, David approves |
| 3 | Canon Integrity Decisions | Gemmi (Critic) — flags, Claude adjudicates, David ratifies |

## 31. Team Roles (LOCKED)

| Team Member | Primary Role | Secondary |
|---|---|---|
| David | Architect, product owner, final authority | Domain expert (40yr astrophotography) |
| Claude | Technical architect, LDD owner, team briefs | Information architecture, UI flow |
| Chatty (ChatGPT) | Developer, schema design, script execution | UI component implementation |
| Gemmi (Gemini) | Astrophysical validation, canon integrity | Data accuracy review, design critique |

**Team workflow discipline:** Each team member works one brief at a time. Do not context-switch between open briefs. Queue new requests as formal briefs for the right moment.

## 32. Equipment Databases (LOCKED)

- Camera and Filter catalogs are SkyPix-curated
- Users consume local cached snapshots only
- Admin-only monthly validation/sync: DEFERRED

---

# PART XII — OPEN ITEMS & DEFERRED

## 33. Active Briefs (In Progress — 2026-02-17)

| Brief | Assigned | Status |
|---|---|---|
| GAS Relationship Mapping | Chatty | **COMPLETE — 2026-02-18** |
| Device Color Matrix | Chatty + David | **COMPLETE — 2026-02-18** |
| Database Schema Design | Chatty | **NEXT — 2026-02-19** |
| Homogeneous Table Architecture | Gemmi + Chatty | **LOCKED — 2026-02-19** |
| Sharpless VizieR size injection (~40 objects) | Parallel track | Pending |
| Master Sidebar orphan recovery (10,630 objects) | Chatty | Pending |

## 34. V1 Feature Queue (Not V1 — Formally Deferred)

- Tonight's real times (V1.1 — architecturally free, date parameter only)
- Hourly weather forecast (V1.1 — Open-Meteo API)
- Hourly seeing forecast (V1.1 — Meteoblue or 7Timer API)
- Lunar avoidance angle per object for tonight (V1.1 — requires lunar path calc or API)
- Multi-night object projection (V1.1)
- Batch object import from CSV (V1 if time, V1.1 if not)
- Admin script with alarms/to-dos (DEFERRED)
- Scheduler integrations (NINA, APT) (V2)
- LFU statistical analysis engine (V2)
- PA (position angle) enrichment (V2)
- PN morphology classes (V2)
- SNR shell sizes from radio catalogs (V2)
- Remote observatory integration (V3)
- ROO white-label (V3)
- AstroBin post-to integration (V3)
- LDN/LBN parent-child complex grouping (V2)
- Distributed/offline-capable dark-site software (V3)

## 35. Beta & Launch Targets

| Milestone | Target |
|---|---|
| Week 1 complete (DB live, 77K profiles) | Feb 20, 2026 |
| Week 2 (SCD queryable by spectral filters) | Feb 27, 2026 |
| Week 3 (Project create, targets to SUD) | Mar 6, 2026 |
| Week 4 (Observability filtering, Planner display) | Mar 13, 2026 |
| Weeks 5-6 (SNR/exposure calcs, Color Matrix) | Mar 27, 2026 |
| Week 7 (Bug fix, beta-quality polish) | Apr 3, 2026 |
| **Public Beta** | **Apr 10, 2026** |

---

# PART XIII — MARKETING CLAIMS

## 36. Validated Marketing Claims

- "Comprehensive spectral intent filtering — nobody else has this"
- "Project-centric planning" — unclaimed territory
- "77K+ object SCD with better emission coverage than SIMBAD"
- "Designed for the Beginner, Engineered for the Expert"
- "Step into the cosmos with Predictive Astrophotography, geared to your equipment and tuned to your imaging environment"
- "SkyPix includes integrated coverage of all major classical nebular and dark cloud catalogs"
- "~95% emission profile coverage across 77K+ objects" (maintain `skypix_metrics.py` to keep current)
- "First-mover advantage: spectral intent filtering for astrophotography planning"

---

# PART XIV — DYNAMIC WEATHER & ATMOSPHERIC INTEGRATION

## 37. Team Brief: Dynamic Weather & Atmospheric Integration
**Source:** Gemmi (Canon Integrity / Design Critic)
**Date:** 2026-02-17
**Status:** INTERIM CANON — Pending Claude architecture response and David ratification
**Cross-reference:** Supplements Section 15 (V1 Rig Planner Scope). Weather/seeing features are V1.1 scope per David's V1 discipline decision. This brief defines the architecture for that V1.1 delivery and constrains how V1 must be structured to receive it cleanly.

---

### 37.1 Purpose (Gemmi's Framing — Preserved)

To transform the SkyPix Rig Planner into a dynamic "cockpit" that adjusts planning parameters (exposure targets, subframe durations, and object selection) based on live and forecasted atmospheric conditions.

---

### 37.2 Primary API Candidates (Gemmi's Research — Preserved)

**Meteoblue (Astronomy API)**
- Value: The "Gold Standard" for high-resolution seeing data.
- Data Points: Seeing Index (1 & 2), Jet Stream speed (turbulence indicator), celestial transparency, and multi-layer cloud cover.
- Implementation: REST/JSON. High priority for "Surface" tier planning where sub-arcsecond detail is the goal.

**7Timer! (ASTRO Product)**
- Value: Open-source and specifically modeled for astronomers.
- Data Points: Cloud cover, transparency, seeing (scaled 1-8), and humidity.
- Implementation: Lightweight and free. Recommended as the "V1.1 Baseline" for providing immediate atmospheric context without overhead.

**Astrospheric**
- Value: Industry favorite for North American transparency and smoke/aerosol data.
- Constraint: Requires a specific API partnership/key.
- Implementation: Secondary target for "Stud Imager" feature sets.

**OpenWeatherMap**
- Value: Ground-level safety data.
- Data Points: Wind gusts (rig stability), dew point (heater management), and temperature.
- Implementation: Essential for "Safety Alerts" within the Planner environment.

---

### 37.3 Planned Functional Mechanics (Gemmi's Design — Preserved)

- **Seeing-Adjusted Planning:** If the API reports seeing > 3.0", the Planner triggers a "Resolution Warning" for small targets (Planetary Nebulae / Galaxies) and suggests shifting to wide-field emission targets.
- **Dew Point Tracking:** Real-time delta between ambient temperature and dew point to automate "Heater Required" notifications in the UI.
- **Wind Loading:** High-altitude jet stream and surface gust data to calculate "Tracking Risk" based on the user's specific focal length and mount profile.

---

### 37.4 Database Requirements (Gemmi's Specification — Preserved)

- **User Site Profile:** Database must support persistent storage of user coordinates (Lat/Long) as global variable for all API pings.
- **Forecast Cache:** Temporary table structure to store last 6 hours of weather data to prevent redundant API calls and stay within free-tier limits.

---

### 37.5 Action Items from Gemmi's Brief

**For Claude (Architecture):**
Integrate API endpoints into Dynamic Rig Planner section. Define UI hooks where data is displayed — e.g., Sidebar Weather Widget vs. Row-Level Planning Alerts.

**For Chatty (Database Lead):**
Schema for User Site Profile (Lat/Long persistent) and Forecast Cache (6-hour rolling temporary table).

---

### 37.6 Architect's Response (Claude — Additive to Brief)
**Status:** PENDING — To be completed as next formal response

Scope note: Per Section 15, weather/seeing integration is V1.1 scope. However, two V1 obligations follow from this brief:
1. User Site Profile (Lat/Long) must be in the V1 schema — it is also needed for longitude-adjusted transit times (Section 12.1). This is not weather-specific. No schema risk.
2. The Rig Planner component must be architected with a designated weather data hook — a sidebar slot or header zone — so V1.1 can inject weather without redesigning the component. Chatty must receive this constraint in the web component brief.

UI hook definition and API priority sequencing (7Timer → Meteoblue upgrade path) will be issued as a formal supplement to this section upon David's direction to proceed.

---

*SkyPix LDD Master — Version 2026-02-17*
*Owned by: Claude (Architecture)*
*Approved by: David (SkyPix Architect)*
*Next scheduled review: Database session Feb 19, 2026*
*All prior LDD files and addenda superseded by this document.*

---

# PART XV — RIG PLANNER CANON CONSOLIDATION

## 38. Rig Planner Canon — Chatty Addendum
**Source:** Chatty (Developer) via Relationship Mapping session with David
**Date:** 2026-02-18
**Status:** LOCKED — Absorbed into master per LDD Prime Directive 9
**Cross-references:** Supplements and resolves INTERIM CANON in Sections 9, 10, 11, 12, 14, 15. Color Matrix (Section 38.11) locks Section 15 V1 delivery item.

---

### 38.1 4D Location Canon (LOCKED)

SkyPix supports dual-input location definition:
- Address → Lat/Lon → Elevation → Timezone/DST
- Explicit Lat/Lon (with optional elevation) → Timezone/DST

Home location propagates to new rigs by default. Each rig may override its own 4D location.

Rig location governs: transit time calculations, DST qualifier, darkness convention clipping, atmospheric modeling, weather/AQI integration.

---

### 38.2 Rig Identity Definition (LOCKED)

A Rig is uniquely defined by:

**1. Optics** — Aperture diameter, central obstruction, focal length, derived collecting area (mm² canonical)

**2. Location (4D)**

**3. Horizon Polygon** — Arbitrary az/alt vertex list, accepts dense or sparse sampling, vertical obstructions encoded as additional vertices ("teeth"), max 1 vertical obstruction per declination band (computational simplification)

**4. Zenith Obstruction Polygon** — Assembly-specific, no symmetry assumption, ≥3 vertices, flexible count, clips visibility arcs if defined

---

### 38.3 Declination Band Model (LOCKED — resolves Section 10 INTERIM CANON)

- Band width defined in RK row 31
- Bands partition declination range
- Visibility arcs precomputed per band
- Regenerated when horizon changes
- Duplicated when rig is duplicated

Smaller band width improves fidelity when horizon segments are nearly parallel to declination circles or horizon sampling is coarse.

**User Guidance:** "For best accuracy: use regular 5° horizon samples, and reduce declination band width when your horizon has long slanted ridges near the east/west horizon."

---

### 38.4 Visibility Arc Canon (LOCKED — resolves Section 11 INTERIM CANON)

Raw VA depends on: declination band, horizon polygon, zenith obstruction.

- **Eastern VA:** Rising intersection → Meridian or obstruction boundary
- **Western VA:** Meridian or obstruction clearing → Setting intersection

If obstruction interrupts band away from meridian:
`TotalVA = RisingArc + SettingArc − ObstructionHourAngle`

Up to two visible windows per band supported.

---

### 38.5 Minimum Elevation — RK Row 29 (LOCKED)

Defines zenith-centered exclusion circle. In Optimum mode: clips reported visibility arcs, may reduce VA to 0:00, object remains displayed (orange) if transit within darkness.

---

### 38.6 Darkness Convention — RK Row 19 (LOCKED — resolves Section 12 INTERIM CANON)

Clips visibility arcs to dusk/dawn interval. Derived from: latitude, longitude, date (15th reference), DST qualifier, darkness convention selection.

---

### 38.7 Mid-Month Cell Canon (LOCKED)

| Cell Position | Content |
|---|---|
| Top | Lunar occlusion notation (dd or dd-dd) |
| Middle | Transit or Rising time (RK row 20) |
| Bottom Left | Eastern VA or total VA |
| Bottom Right | Western VA |

Lunar occlusion defined by avoidance angle (RK row 30).

---

### 38.8 Exposure & SNR Canon (LOCKED)

Inputs: rig collecting area (mm²), focal length, camera QE, camera read noise, cooling delta + ambient temp, filter transmission curves (up to 4 bands), sky brightness, AQI, atmospheric density, exposure strategy (default 1 if null), desired image SNR, rig time budget (RK row 27), max subframe exposure (RK row 28).

Time budget is global per rig per object. If cap binds → New SNR displayed. Subframe exposure ≤ RK row 28.

---

### 38.9 Camera Propagation Canon (LOCKED)

- Camera name: informational only
- Specs retrieved from SkyPix equipment DB (editable)
- Highlight color used at 50% opacity in planner total time cells
- Confidence paint levels: L3 @50%, L2 @35%, L1 @20%, L0 @5%, X @50% orange
- Rig eligibility matrix: 3 rows per rig — (1) eligibility checkbox, (2) FOV major/minor, (3) image scale

---

### 38.10 Filter Propagation Canon (LOCKED)

- Filter name appears in Rig Planner header
- Displayed set determined solely by Filter Kit eligibility matrix
- Column pair per filter: Total Exposure + Subframe Duration
- Supports 1–4 bands
- Five-point transmission curve model per band
- Band shading tiers: 20%, 15%, 10%, 5%

---

### 38.11 Color Matrix Canon — Web Migration (LOCKED — locks Section 15 V1 item)

Replaces GAS onEdit propagation with centralized Color Matrix:
- One column per device (rig/camera/filter)
- Rows represent opacity tiers: 100%, 80%, 50%, 35%, 20%, 15%, 10%, 5%
- Applied via CSS/RGBA tokens
- Matrix grows/shrinks as devices added/removed

---

### 38.12 Rig Planner Design Intent (LOCKED)

The Rig Planner is: a geometric visibility engine, a time-budget optimization engine, a spectral signal optimization engine, a lunar proximity warning system, and a project allocation tool.


---

# PART XVI — DATABASE SCHEMA (LOCKED)

## 39. Homogeneous Objects Table (LOCKED — 2026-02-19)
**Decision:** Single `objects` table. Replaces four-table proposal. Unanimous — Gemmi + Chatty concur.

### 39.1 Tier Column
```sql
layer ENUM('SURFACE','RAW','HOLDING','QUARANTINE')
```
Promotion/demotion = UPDATE only. No cross-table copy/delete. No orphan risk.

### 39.2 Schema Additions (Chatty spec — LOCKED)
Add to existing `objects` table:

| Column | Type | Purpose |
|---|---|---|
| `layer` | ENUM | Tier classification |
| `source_origin` | text | "SIMBAD", "VizieR:VII/118", "OpenNGC", etc. |
| `v_mag` | numeric | Physical threshold gatekeeping (V<16 reference) |
| `redshift_z` | numeric | Future expansion (z constraints) |
| `layer_reason` | text (optional) | Why HOLDING: too faint, too small, missing size, etc. |
| `layer_updated_at` | timestamp | Audit trail |

Existing identity keys (`primary_id`, `id_normalized`, catalog provenance) unchanged.

### 39.3 Indexing (LOCKED)
```sql
INDEX objects(layer)
INDEX objects(id_normalized)
INDEX objects(ra_deg, dec_deg)
INDEX objects(layer, simbad_otype)   -- if filtering by type within tier
```

### 39.4 Views (Optional Ergonomic Layer)
Four views preserve "four-table feel" for query clarity without physical separation:
```sql
CREATE VIEW surface_objects AS SELECT * FROM objects WHERE layer='SURFACE';
CREATE VIEW raw_objects AS SELECT * FROM objects WHERE layer='RAW';
CREATE VIEW holding_objects AS SELECT * FROM objects WHERE layer='HOLDING';
CREATE VIEW quarantine_objects AS SELECT * FROM objects WHERE layer='QUARANTINE';
```

### 39.5 Immediate Action
Map ~10,630 surface-orphans into HOLDING (valid RA/Dec confirmed) via ALTER TABLE + UPDATE. Chatty to provide exact DDL statements against current Supabase schema on David's request.

