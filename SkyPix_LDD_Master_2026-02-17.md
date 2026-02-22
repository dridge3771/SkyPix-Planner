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
11. **"We ingest meaning, not magnitude."** Database growth must correlate with planner intelligence. Tier-3 catalogs are permanently excluded regardless of size or prestige.

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
**Planner:** Full SNR and exposure planning. RAW objects carry L0-inferred spectral profiles (presence_mask, ha_strength, oiii_strength, etc.) from SIMBAD_TAP ingest. Scientifically usable immediately. Remain RAW because geometry is unconfirmed, catalog enrichment is pending, and expert promotion has not occurred — not because spectra are absent.
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

## 4. Database Architecture (LOCKED — 2026-02-19)

**Single homogeneous `objects` table with `layer` ENUM.** Validated by full team (Gemmi + Chatty + David). Executed and confirmed in production. **Canonical state:** 256,577 objects, 280MB, Supabase free tier compliant. Schema frozen for V1 planner development.


**Supabase tier:** Free tier sufficient through beta. Pro tier ($25/mo) when community contribution activity scales beyond 50K users.

## 5. Object Model (LOCKED)

- **SkyPix Object Class** (≤3 chars) is user-facing. Appears in SUD and Rig Planner.
- **SIMBAD otypes** are abbreviations only. Appear only in UI popups, never as planner logic drivers.
- Object Class may consolidate multiple SIMBAD otypes.
- **Terminology:** "Object types" are formally **SkyPix Object Classes**. Label-only change.

## 6. Catalog Coverage Commitment (LOCKED)

All ten catalogs fully represented across four tiers. No catalog object with valid RA/Dec is unhoused.

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
| Arp | VII/192 | RAW/SURFACE |

**Arp handling:** Interacting/peculiar galaxy systems aliased at system level. Individual components linked as associated_objects where scientifically notable. System entry is canonical planning target.

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

## 7.4 Coordinate Normalization Invariant (LOCKED — 2026-02-19)

**Universal ingestion rule — applies to every catalog, no exceptions:**

All catalog coordinates SHALL be normalized to **J2000 (ICRS)** prior to collision matching and object insertion.

If source catalog uses B1950 or other epoch, convert before staging:
```python
from astropy.coordinates import SkyCoord, FK4, FK5
import astropy.units as u

coord_b1950 = SkyCoord(ra, dec, unit=u.deg, frame=FK4(equinox="B1950"))
coord_j2000 = coord_b1950.transform_to(FK5(equinox="J2000"))
```

**Scope:** Arp, HCG, VV, KPG, Abell PN, PK, Green SNR, Dobashi, MWP — every future catalog without exception.

**Reason:** Collision gate matches on ra_deg/dec_deg columns which are J2000 by canon. Epoch mismatch at 60" matching radius produces false misses and silent duplicates.


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
- Live SIMBAD Resolver — failed local search triggers SIMBAD API, inserts new object as layer='RAW' with positional + otype data only (no L0 at insert time; L0 inference runs as background enrichment pass), permanently local thereafter (V1.1)
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

## 23. Current Database State (2026-02-19 — Rebuild Complete)

### 23.1 Rebuild Summary
Full ground-up rebuild executed 2026-02-19. JSONB raw_payload bloat eliminated.
Starting size: ~1,348 MB → Post-rebuild: **~280 MB** ✅ Free tier compliant. Schema frozen for V1.

### 23.2 Canonical Tables (LOCKED)

| Table | Rows | Purpose | Status |
|---|---|---|---|
| `public.objects` | 256,577 | Single authoritative object store | CANONICAL |
| `public.aliases` | TBC | Global identity resolver | CANONICAL |
| `public.associated_objects` | 0 | Relational topology | CANONICAL |
| `public.scd_surface` | VIEW | Legacy compatibility | VIEW over objects |

### 23.3 Layer Distribution (Current)

| Layer | Count | Meaning |
|---|---|---|
| SURFACE | 76,314 | Curated, planner-ready |
| RAW | 93,180 | SIMBAD-resolved, ingested |
| HOLDING | 87,083 | Physically marginal, gated |
| QUARANTINE | 0 | Awaiting user contributions |
| **Total** | **256,577** | |

### 23.4 Performance Confirmed
- Alias lookup: ~0.1ms (GIN trigram index)
- Search: GIN index on search_vector confirmed
- Primary key + id_normalized + layer btree indexes confirmed

### 23.5 ONF Warranty — Three-Layer Protection (LOCKED)

**Layer 1 — Curated Coverage:** Major imaging catalogs ingested (SURFACE + RAW + HOLDING)
**Layer 2 — 256K Local Universe:** Quarter-million objects covering all major emission/reflection/dark populations
**Layer 3 — Live SIMBAD Resolver (V1.1):** Long-tail discovery without storage growth. User searches local DB first; on miss, resolves live via SIMBAD, inserts as RAW, permanently local thereafter.

**Layer 3 scope note:** Live SIMBAD resolver is V1.1. Requires API rate management, error handling, insert-on-resolve workflow. V1 ONF protection is Layers 1 and 2 only — sufficient for beta at 256K objects.

### 23.6 Strategic Architecture Insight (Chatty — 2026-02-19)
SkyPix = Curated Cache + Live Resolver. Local DB serves fast planning universe. SIMBAD serves infinite discovery backend. SkyPix no longer scales by storing more data — it scales by learning from use. This replaces the prior assumption that all 12.5M SIMBAD entries must be stored locally.

### 23.7 Outstanding Items (Post-Rebuild)
- ✅ RESOLVED: RAW rows carry full L0-inferred spectral profiles. RAW is not a stub tier.
- Implement QUARANTINE user workflow
- Live SIMBAD resolver (V1.1)
- Continue VizieR catalog enrichment passes (Phase 2)
- Promote qualified RAW → SURFACE

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

- Live SIMBAD Resolver — failed local search triggers SIMBAD API, inserts new object as layer='RAW' with positional + otype data only (no L0 at insert time; L0 inference runs as background enrichment pass), permanently local thereafter (V1.1)
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


---

# PART XVII — ALIAS & ASSOCIATION SCHEMA

## 40. Alias System Canon (LOCKED — 2026-02-19)

### 40.1 Design Principle
Users think in common names and informal catalog shorthand. The alias system maps every known name variant to a single canonical object record. Users never need to know SkyPix's internal catalog structure.

### 40.2 Canonical Object Rule (LOCKED)
For co-located emission + dark nebula pairs:
- **Emission/reflection object = canonical record.** Full spectral profile. Planner target.
- **Dark/obstructing nebula = associated object.** No independent emission profile. Linked to canonical record.

**Reference case (establishes pattern for all similar pairs):**
- IC 434 (HII emission nebula) → canonical record, SURFACE tier, full spectral profile
- Barnard 33 (dark globule, the "Horsehead") → associated object, linked to IC 434
- Aliases "B33", "Barnard 33", "Horsehead Nebula" → all resolve to IC 434's primary_id

**Rationale:** SkyPix is a spectral planning engine. The emitting source is the planning target. The obstructing dark nebula is compositional context only.

### 40.3 Aliases Table (LOCKED)

```sql
CREATE TABLE aliases (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alias_text       TEXT NOT NULL,         -- original form: "Horsehead Nebula"
  alias_normalized TEXT NOT NULL,         -- lowercase, stripped: "horsehead nebula"
  object_id        UUID NOT NULL REFERENCES objects(primary_id) ON DELETE CASCADE,
  alias_type       TEXT NOT NULL,         -- 'catalog_id' | 'common_name' | 'alternate_id'
  source           TEXT,                  -- "Barnard", "SIMBAD", "user", etc.
  created_at       TIMESTAMP DEFAULT now()
);

CREATE UNIQUE INDEX aliases_normalized_unique
  ON aliases(alias_normalized);           -- collision gate: one object per normalized name

CREATE INDEX aliases_trgm
  ON aliases USING GIN(alias_normalized gin_trgm_ops);  -- fuzzy search (pg_trgm)

CREATE INDEX aliases_object_id
  ON aliases(object_id);                  -- reverse lookup: all names for one object
```

### 40.4 Associated Objects Table (LOCKED)

```sql
CREATE TABLE associated_objects (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_id      UUID NOT NULL REFERENCES objects(primary_id) ON DELETE CASCADE,
  associated_name   TEXT NOT NULL,        -- "Barnard 33"
  association_type  TEXT NOT NULL,        -- 'dark_obstruction' | 'embedded' | 'companion' | 'complex_member'
  notes             TEXT,                 -- "Dark globule silhouetted against IC 434"
  created_at        TIMESTAMP DEFAULT now()
);

CREATE INDEX assoc_canonical_id ON associated_objects(canonical_id);
```

### 40.5 Ingest Collision Gate (LOCKED)
Before writing any object, all incoming alias tokens checked against existing aliases:
```sql
SELECT alias_normalized, object_id
FROM aliases
WHERE alias_normalized = ANY($incoming_alias_list);
```
Any row returned = collision → ingest halts for that object, logs conflict, flags for admin review. Nothing writes until collision resolved.

### 40.6 Search Query (LOCKED)
```sql
SELECT o.*,
       a.alias_text AS matched_name,
       similarity(a.alias_normalized, $1) AS score
FROM objects o
JOIN aliases a ON a.object_id = o.primary_id
WHERE a.alias_normalized % $1             -- trigram threshold ~0.3
ORDER BY
  (a.alias_normalized = $1) DESC,        -- exact matches first
  score DESC,                            -- then by similarity
  CASE o.layer
    WHEN 'SURFACE'    THEN 1
    WHEN 'RAW'        THEN 2
    WHEN 'HOLDING'    THEN 3
    WHEN 'QUARANTINE' THEN 4
  END;                                   -- then by tier quality
LIMIT 20;
```

### 40.7 IC 434 / Barnard 33 Reference Implementation

| Table | Field | Value |
|---|---|---|
| objects | primary_id | [uuid] |
| objects | layer | SURFACE |
| objects | id_normalized | ic434 |
| aliases | alias_text | IC 434 |
| aliases | alias_text | Horsehead Nebula |
| aliases | alias_text | Barnard 33 |
| aliases | alias_text | B33 |
| associated_objects | associated_name | Barnard 33 |
| associated_objects | association_type | dark_obstruction |
| associated_objects | notes | Dark globule silhouetted against IC 434 emission nebula |


---

# PART XVIII — LAYER CANON CLARIFICATION (LOCKED — 2026-02-19)

## 41. Canonical Layer Semantics (Chatty — LOCKED)
**Source:** Chatty implementation confirmation, 2026-02-19
**Status:** LOCKED — supersedes any prior description of RAW as "positional only" or "stub"

| Layer | Meaning | Spectral Data |
|---|---|---|
| SURFACE | Curated + verified + planner-ready | Full L0 — expert validated |
| RAW | Inferred + scientifically usable | Full L0 — SIMBAD_TAP ingest |
| HOLDING | Real but physically marginal | L0 present where available |
| QUARANTINE | Unresolved or user-supplied | X confidence (user-declared) |

**Critical distinction:** RAW objects are NOT stubs. They carry full L0-inferred spectral profiles and participate in planner inference immediately. They remain RAW because:
- Curated geometry is unconfirmed
- Catalog enrichment is pending
- Expert promotion has not occurred

**Not** because spectra are absent.

**SkyPix core promise preserved:** Any recognized object yields an intelligent imaging recommendation.

## 42. Phase Transition Record (2026-02-19)

Today SkyPix crossed from **Phase: Database Construction** to **Phase: Operational Universe**.

The backend is no longer experimental. It is infrastructure.

| Role | Status |
|---|---|
| Gemmi | Operational Acceptance |
| Claude | Architectural Canon Lock |
| Chatty | Implementation Complete |
| David | Ready for Planner Phase |

**The Rig Planner is now the project.**


---

# PART XIX — CATALOG INGESTION DOCTRINE (LOCKED — 2026-02-19)

**Source:** Chatty (Implementation) + Claude (Architecture)
**Authority:** David (Architect) approved
**Status:** LOCKED — self-protecting constitution for all future catalog decisions

---

## 43. Tier-1 Ingestion Doctrine (LOCKED)

### Phase 0 — Catalog Qualification Gate
Before any ingestion brief is issued, catalog must satisfy all three:
- Curated by recognized astronomical authority
- Improves a planning decision (target selection, filter choice, exposure strategy)
- Objects are imageable by amateur-to-advanced equipment

Fail any criterion → Tier-2 or Tier-3. No exceptions.

### Phase 1 — Catalog Recon (Claude executes, reports before proceeding)
1. VizieR table identification (specific table name, not just catalog ID)
2. Row count verification
3. Coordinate epoch confirmation
4. Identifier normalization rules

**Ingestion halts until all four are verified.**

### Phase 2 — Canon Classification
Catalog assigned one of five behavioral types (see Section 44).
Classification determines ingestion pathway, database mutation authority, planner activation.

### Phase 3 — Hybrid Acquisition (Standard Pattern)
Every Tier-1 catalog follows identical logic:
```
Stage catalog
↓
J2000 normalize (mandatory — Section 7.4)
↓
Coordinate match (60" spherical geometry)
↓
Matched   → Alias enrichment
Unmatched → RAW insertion
```
No exceptions to this pattern.

### Phase 4 — Collision Gate Authority
Collision system decides duplicates, alias merges, promotions automatically.
Human intervention only on anomaly. Collision gate fires → STOP and report.

### Phase 5 — Provenance Lock
Every row records:
```
source_origin = VizieR:<catalog>:<table>
```
SkyPix must always know why an object exists.

### Phase 6 — Verification Canon
Acquisition is complete only when:
```
aliases_added + new_rows_created = catalog_row_count
```
AND: zero orphan aliases, zero duplicate primary_ids, DB growth acceptable.

### Phase 7 — Semantic Activation
After ingest, catalog meaning becomes usable by Planner. This is where SkyPix differentiates from Stellarium/SIMBAD. Examples: Arp → interaction weighting, HII → emission scoring, Dark clouds → broadband optimization.

---

## 44. Catalog Behavioral Taxonomy (LOCKED)

A catalog's type determines ingestion pathway, database mutation authority, planner activation, and future LFU behavior.

### Type 1 — Identity Catalogs
**Purpose:** Object identification normalization. Introduce names, not new entities.
**Examples:** Messier, Caldwell, UGC, PGC, ESO, LEDA cross-IDs

| Action | Allowed |
|---|---|
| Alias insertion | ✅ |
| Metadata overwrite | ❌ |
| RAW object creation | ❌ |
| Layer promotion | ❌ |

**Planner effect:** None directly. Increases recognition, not knowledge.
**Canon purpose:** Prevent duplicate universes caused by naming differences.

### Type 2 — Enrichment Catalogs
**Purpose:** Describe known objects via alternate curated selection. Express astronomer interest in already-known targets.
**Examples:** Arp Atlas, Hickson Compact Groups, VV, KPG, Collinder, Melotte

| Action | Allowed |
|---|---|
| Alias enrichment | ✅ Primary |
| RAW insert if unmatched | ✅ Conditional |
| Metadata overwrite | ❌ |
| Layer change | ❌ |

**Planner effect:** Semantic weighting — interaction likelihood, aesthetic complexity, imaging priority signals.
**Canon purpose:** Capture astronomer judgment.

### Type 3 — Physics Catalogs
**Purpose:** Physical measurements or emission properties. Refine understanding of known objects.
**Examples:** Green SNR, Abell PN, PK PN, HII emission surveys, spectral databases

| Action | Allowed |
|---|---|
| Update emission profile | ✅ |
| Add spectral flags | ✅ |
| RAW insert | ⚠ Rare — only if truly absent |
| Alias insertion | Optional |

**Planner effect:** Directly modifies filter suitability, exposure prediction, narrowband scoring, LFU calibration.
**Canon purpose:** Convert SkyPix from positional database → physical model.

### Type 4 — Morphology Catalogs
**Purpose:** Structure and appearance, not physics. Encode how objects look.
**Examples:** Arp subclasses, galaxy morphology atlases, ring/tail/merger classifications

| Action | Allowed |
|---|---|
| Structural metadata add | ✅ |
| Alias add | Optional |
| RAW insert | ❌ (unless identity absent) |
| Physics modification | ❌ |

**Planner effect:** Future: framing suggestions, composition guidance, complexity scoring, mosaic prediction.
**Canon purpose:** Teach SkyPix visual intelligence.

### Type 5 — Structure Catalogs
**Purpose:** Real astrophysical groupings or environments. Objects often absent from legacy catalogs.
**Examples:** OB Associations, stellar streams, compact groups, molecular cloud complexes, bubble catalogs

| Action | Allowed |
|---|---|
| RAW insert | ✅ Primary |
| Alias creation | ✅ |
| Environment linking | ✅ |
| Metadata enrichment | ✅ |

**Planner effect:** Regional imaging, widefield planning, context-aware targeting, ecosystem modeling.
**Canon purpose:** Expand SkyPix from object list → cosmic environment model.

### Master Behavior Matrix

| Type | Alias | RAW Insert | Metadata | Planner Impact |
|---|---|---|---|---|
| Identity | ✅ | ❌ | ❌ | None |
| Enrichment | ✅ | Conditional | ❌ | Semantic weighting |
| Physics | Optional | Rare | ✅ | Core calculations |
| Morphology | Optional | ❌ | ✅ structural | Visual intelligence |
| Structure | ✅ | ✅ | ✅ | Environmental modeling |

---

## 45. Catalog Tier Policy — Anti-Bloat Constitution (LOCKED)

**Governing principle:** We ingest meaning, not magnitude. Database growth must correlate with planner intelligence.

### Tier-1 — Canonical Universe (Bulk Ingest)
Curated, high observational value, planner intelligence gain, bounded population size.
Enters via full hybrid acquisition pipeline (Phase 0-7 above).

### Tier-2 — Conditional Access (Organic Only)
Large surveys or discovery catalogs useful for expansion but not essential to planner intelligence.
**SHALL NOT be bulk-ingested.** Enters universe organically via:
- Live SIMBAD resolver (V1.1)
- User-triggered expansion
- Future adaptive ingestion

### Tier-3 — Permanently Excluded
Catalogs whose inclusion would increase object count without increasing planner intelligence.
Accessed only via external resolver when required. Never enter SCD.

### The Four-Question Decision Gate

```
Q1: Does it add imageable objects not already in the universe?
    YES → Tier-1 candidate
    NO  → Q2

Q2: Does it add physical metadata to existing objects?
    YES → Tier-2 candidate
    NO  → Reject (Tier-3)

Q3 (Tier-1 check): Does any object meet minimum imageability threshold?
    (size > 15" OR surface brightness < 25 mag/arcsec²)
    YES → Proceed to Tier-1 acquisition
    NO  → Demote to Tier-2 or Reject

Q4 (Storage check): Does projected storage impact exceed 50MB net new?
    YES → Requires David explicit approval
    NO  → Proceed under standing authority
```

### Standing Authorization
- Tier-1 catalogs in approved wave plan: standing authority (no per-catalog approval)
- Tier-1 catalogs NOT in wave plan: David explicit approval required
- Tier-2 enrichment passes < 50MB net: standing authority
- Any catalog triggering Q4: David explicit approval regardless of tier

---

## 46. Wave Execution Order (LOCKED)

### Wave 1 — Interaction Universe
1. Arp Atlas (VII/192/arpord) — Type: Enrichment — 338 objects ✅ IN PROGRESS
2. Hickson Compact Groups (VII/213) — Type: Structure
3. Vorontsov-Velyaminov (VII/62) — Type: Enrichment
4. Karachentsev Pairs (VII/117) — Type: Enrichment
5. Arp-Madore (VII/170) — Type: Enrichment

### Wave 2 — Stellar Death Physics
1. Abell PN (VII/4) — Type: Physics
2. PK Planetary Nebulae (V/84) — Type: Physics
3. Green SNR (VII/84) — Type: Physics

### Wave 3 — Galactic Ecology Completion
1. Gum Catalog (pending) — Type: Physics
2. Collinder (VII/101) — Type: Structure
3. Melotte (VII/110) — Type: Structure
4. Harris GC (VII/202) — Type: Structure

### Wave 4 — SkyPix Intelligence Seeds
1. Dobashi Dark Clouds (J/PASJ/63/S1) — Type: Structure
2. MWP Bubbles (J/MNRAS/424/2442) — Type: Structure

---

## 47. Rejected Catalog Log (Permanent)

| Catalog | Tier | Reason | Date |
|---|---|---|---|
| SDSS photometric | Tier-3 | 69M rows, stellar-dominated, no DSO planning value | 2026-02-19 |
| Gaia DR3 | Tier-3 | 1.8B stellar objects, outside DSO scope | 2026-02-19 |
| 2MASS PSC | Tier-3 | 470M point sources, stellar catalog | 2026-02-19 |
| SIMBAD full | Tier-3 | 12.5M rows, storage catastrophe, resolver handles long-tail | 2026-02-19 |


---

# PART XIX — CATALOG INGESTION DOCTRINE (LOCKED — 2026-02-19)

## 43. Tier-1 Ingestion Doctrine (Chatty + Claude — LOCKED)

### Phase 0 — Catalog Qualification
Before ingestion, catalog must pass all three gates:
- Is it curated by a recognized astronomical authority?
- Is it astrophysically meaningful for planning decisions?
- Does it improve target selection, filter choice, or exposure strategy?

Fail any gate → Tier-2 or reject.

### Phase 1 — Catalog Recon (Claude executes, reports before any ingest)
1. VizieR table identification (exact table name, not parent catalog)
2. Row count verification (must match published catalog size)
3. Coordinate epoch confirmation (J2000 required — see Section 7.4)
4. Identifier normalization rules

**Processing halts until all four items verified.**

### Phase 2 — Canon Classification
Catalog assigned one of five behavioral types (Section 44). Classification determines ingestion pathway, database mutation authority, planner activation, and future LFU behavior.

### Phase 3 — Hybrid Acquisition (Standard Pattern)
Every Tier-1 catalog follows the same invariant:
```
Stage catalog
↓
Coordinate Match (60" spherical — Section 7.4)
↓
Matched   → Alias enrichment
Unmatched → RAW insertion
```
No exceptions. No manual branching.

### Phase 4 — Collision Gate Authority
Collision system decides duplicates, alias merges, promotions. Human intervention only on anomaly. Collision gate fires = STOP and report.

### Phase 5 — Provenance Lock
Every row records:
```
source_origin = VizieR:<catalog>:<table>
```
SkyPix must always know why an object exists.

### Phase 6 — Verification Canon
Acquisition complete only when:
```
aliases_added + new_rows = catalog_row_count
```
AND: zero orphan aliases, zero duplicate primary_ids, DB growth acceptable.

### Phase 7 — Semantic Activation
After ingest, catalog meaning becomes usable by Planner. This is where SkyPix differentiates from Stellarium/SIMBAD. Catalog type determines planner activation (Section 44).

---

## 44. Catalog Behavioral Taxonomy (LOCKED — 2026-02-19)

**Source:** Chatty (Implementation), validated Claude (Architecture)
**Purpose:** Determines system behavior — ingestion pathway, DB mutation authority, planner activation.

### Type 1 — IDENTITY
**Definition:** Catalogs whose purpose is object identification normalization. Introduce names, not new astronomical entities.
**Examples:** Messier, Caldwell, UGC, PGC, ESO, LEDA cross-IDs
**Rule:** SHALL NOT create new objects.
**Allowed:** Alias insertion only
**Blocked:** Metadata overwrite, RAW creation, layer promotion
**Planner effect:** None directly. Improves searchability and resolver success.
**Canon purpose:** Prevent duplicate universes caused by naming differences.

### Type 2 — ENRICHMENT
**Definition:** Catalogs that describe known objects using an alternate curated selection. Express astronomer interest in already-known targets.
**Examples:** Arp Atlas, Hickson Compact Groups, Vorontsov-Velyaminov, Karachentsev Pairs, Collinder, Melotte
**Rule:** ALIAS-FIRST HYBRID acquisition.
**Allowed:** Alias enrichment (primary), RAW insert if unmatched
**Blocked:** Metadata overwrite, layer change
**Planner effect:** Semantic weighting — interaction likelihood, aesthetic complexity, imaging priority signals. Planner gains intent awareness.
**Canon purpose:** Capture astronomer judgment.

### Type 3 — PHYSICS
**Definition:** Catalogs providing physical measurements or emission properties. Refine understanding of objects already known.
**Examples:** Green SNR, PK PN, Abell PN, HII emission surveys, future spectral databases
**Rule:** SHALL enrich existing objects primarily.
**Allowed:** Update emission profile, add spectral flags, RAW insert (rare — only if truly absent), alias (optional)
**Planner effect:** Directly modifies filter suitability, exposure prediction, narrowband scoring, LFU calibration. Feeds the Planner Engine itself.
**Canon purpose:** Convert SkyPix from positional database → physical model.

### Type 4 — MORPHOLOGY
**Definition:** Catalogs describing structure or appearance, not physics. Encode how objects look.
**Examples:** Arp subclasses, galaxy morphology atlases, ring/tail/merger classifications
**Rule:** Annotate objects without redefining them.
**Allowed:** Structural metadata, alias (optional)
**Blocked:** RAW insert (unless identity absent), physics modification
**Planner effect:** Future capabilities — framing suggestions, composition guidance, complexity scoring, mosaic prediction.
**Canon purpose:** Teach SkyPix visual intelligence.

### Type 5 — STRUCTURE
**Definition:** Catalogs representing real astrophysical groupings or environments. Describe objects that often do not exist individually in legacy catalogs.
**Examples:** OB Associations, stellar streams, compact groups, molecular cloud complexes, bubble catalogs
**Rule:** EXPECT new object creation.
**Allowed:** RAW insert (primary), alias creation, environment linking, metadata enrichment
**Planner effect:** Regional imaging, widefield planning, context-aware targeting, ecosystem modeling.
**Canon purpose:** Expand SkyPix from object list → cosmic environment model.

### Master Behavior Matrix

| Type | Alias | RAW Insert | Metadata | Planner Impact |
|---|---|---|---|---|
| Identity | Yes | No | No | None |
| Enrichment | Yes | Conditional | No | Semantic weighting |
| Physics | Optional | Rare | Yes | Core calculations |
| Morphology | Optional | No | Yes (structural) | Visual intelligence |
| Structure | Yes | Yes | Yes | Environmental modeling |

---

## 45. Tier Policy — Database Chaos Prevention (LOCKED — 2026-02-19)

### The Guardrail Principle (CANON)
> **"We ingest meaning, not magnitude."**
> Database growth must correlate with planner intelligence.

### Tier-1 — Canonical Universe Catalogs
**Criteria (all three required):**
- Curated by recognized astronomical authority
- Improves a planning decision
- Objects imageable by amateur-to-advanced equipment

**Behavior:** Full hybrid acquisition per Section 43. Enters wave execution queue.

### Tier-2 — Conditional Expansion Catalogs
**Definition:** Large surveys or discovery catalogs useful for expansion but not essential to planner intelligence.
**Examples:** Massive infrared surveys, large galaxy surveys, photometric surveys
**Policy:** SHALL NOT be bulk-ingested. Allowed only through resolver discovery, user-triggered expansion, or future adaptive ingestion. Enter the universe organically, not globally.

### Tier-3 — Permanently Excluded
**Definition:** Catalogs whose inclusion would increase object count without increasing planner intelligence.
**Examples:** Full star catalogs, all-sky photometry, billion-object surveys, purely statistical datasets
**Policy:** Permanently excluded from SCD ingestion. Accessible only via external resolver when required.

### The Tier Decision Gate

```
Q1: Does it add imageable objects not already in the universe?
    YES → Tier-1 candidate
    NO  → Q2

Q2: Does it add physical metadata to existing objects?
    YES → Tier-2 candidate
    NO  → Reject (Tier-3)

Q3 (Tier-1): Do objects meet minimum imageability threshold?
    size > 15" OR surface_brightness < 25 mag/arcsec²
    YES → Proceed to Tier-1 acquisition
    NO  → Demote to Tier-2 or Reject

Q4 (Storage): Does projected net new storage exceed 50MB?
    YES → Requires David explicit approval
    NO  → Proceed under standing authority
```

### Standing Authorization
- Tier-1 catalogs in approved wave plan → David's standing authority
- Tier-1 catalogs NOT in wave plan → David explicit approval required
- Tier-2 enrichment passes < 50MB net → standing authority
- Any catalog triggering Q4 → David explicit approval regardless of tier

### Rejected Catalog Log (Permanent — append only)

| Catalog | Tier | Reason | Date |
|---|---|---|---|
| SDSS photometric | Tier-3 | 69M rows, stellar-dominated, no DSO planning value | 2026-02-19 |
| Gaia DR3 | Tier-3 | 1.8B stellar objects, outside DSO scope | 2026-02-19 |
| 2MASS PSC | Tier-3 | 470M point sources, stellar catalog | 2026-02-19 |

---

## 46. Wave Execution Order (LOCKED — 2026-02-19)

**Source:** Chatty recommendation, Claude approved
**Authority:** David standing authorization for all waves below

### Wave 1 — Interaction Universe
1. Arp Atlas (VII/192/arpord) — Enrichment ✅ Brief issued
2. Hickson Compact Groups (VII/213) — Enrichment
3. Vorontsov-Velyaminov (VII/62) — Enrichment
4. Karachentsev Pairs (VII/60) — Enrichment
5. Arp-Madore (VII/170) — Enrichment

### Wave 2 — Stellar Death Physics
1. Abell PN (VII/4) — Physics
2. PK PN (V/84) — Physics
3. Green SNR (VII/316) — Physics

### Wave 3 — Galactic Ecology Completion
1. Gum Catalog (pending VizieR table) — Structure
2. Collinder (VII/92) — Enrichment
3. Melotte (VII/?) — Enrichment
4. Harris GC (VII/202) — Physics/Structure

### Wave 4 — SkyPix Intelligence Seeds
1. Dobashi dark clouds (J/PASJ/63/S1) — Structure
2. MWP Bubbles (J/ApJS/184/18) — Structure

**Each wave meaningfully increases planner intelligence before the next begins.**


---

# PART XX — PROFILE VALENCE CANON (LOCKED — 2026-02-19)

## 47. Profile Valence — Query Construction Canon (Chatty — LOCKED)

**Purpose:** Profile Valence defines how the SkyPix Planner converts user imaging intent into deterministic database search keys. The user never sees the internal encoding — they interact only with the Band Selection Matrix.

### 47.1 Canon Band Set (PERMANENT — SHALL NOT CHANGE)

| Band | Symbol | Presence Value | Prevalence Digit |
|---|---|---|---|
| H-alpha | Ha | 100 | 1 |
| OIII | OIII | 200 | 2 |
| SII | SII | 400 | 3 |
| H-beta | Hb | 800 | 4 |
| NII | NII | 1600 | 5 |
| HeII | HeII | 3200 | 6 |
| Infrared Regime | IR | 6400 | 7 |

### 47.2 Schema Column Mapping (LOCKED)

Chatty's prevalence pair (Dd) maps to existing objects table columns:

| Chatty Term | objects Column | Type |
|---|---|---|
| presence_mask | presence_mask | integer |
| D (dominant digit) | dominant_band | text |
| d (2nd dominant digit) | diminutive_band | text |

No schema change required. Columns already exist.

### 47.3 User Interface Model

The planner presents a Band Selection Matrix:

| Band | Required | Allowed | Dominant | 2nd Dominant |
|---|---|---|---|---|

**Column semantics:**
- **Required:** Band must be present. Multiple allowed. Defines Required Presence Component (R).
- **Allowed:** Band may be present, not mandatory. Multiple allowed. Defines Allowed Set (A).
- **Dominant:** Exactly one. Expected strongest emission regime.
- **2nd Dominant:** Exactly one. Expected secondary regime.

### 47.4 Canon Invariants (LOCKED)

**Dominance Requirement Rule:**
If a band is Dominant or 2nd Dominant, it MUST also be Required.
```
D ∈ Required
d ∈ Required
D ≠ d
```
UI SHALL enforce automatically. Users SHALL NOT declare dominance for a non-required band.

**Required Overrides Allowed:** Band marked Required SHALL NOT participate in Allowed combinations.

**Presence vs Prevalence Separation:** Presence determines which objects qualify. Prevalence refines how they rank. Prevalence SHALL NEVER relax presence requirements.

### 47.5 Presence Key Construction

```
R = sum(presence values of Required bands)
A = set of presence values of Allowed bands

Keys = { R + sum(S) | S ⊆ A }
|Keys| = 2^(|A|)
```

**Example:**
Required: OIII (200) + Hb (800) → R = 1000
Allowed: Ha (100), SII (400), NII (1600)

Keys generated: 1000, 1100, 1400, 1500, 2600, 2700, 3000, 3100

Adding Required bands reduces the solution space (more specific intent = smaller, more precise search).

### 47.6 Internal Representation

```
presence_mask   = integer sum (stored in objects.presence_mask)
dominant_band   = D digit as text (stored in objects.dominant_band)
diminutive_band = d digit as text (stored in objects.diminutive_band)

display form = leading-zero string e.g. "01825" (non-authoritative)
```

### 47.7 Planner Query Token

```
QueryToken = (presence_key, Dd)
```

Planner evaluates all tokens deterministically across all generated keys.

### 47.8 Prohibited Uses

Profile Valence SHALL NOT:
- Be treated as a bitstring
- Encode causal astrophysics
- Replace emission profiles
- Be edited manually outside planner logic

It is a query construction mechanism, not a physics model.

### 47.9 Scaling Note

Framework scales to an 8th band without redesign — add row to band set table, assign next presence value (12800) and prevalence digit (8).


---

# PART XXI — INFRARED BAND DEFINITION & INFERENCE CANON (LOCKED — 2026-02-19)

## 48. Infrared Band — Tangible Definition

### 48.1 What IR Means in SkyPix Context

IR in SkyPix does not mean "thermal infrared" or "near-infrared camera sensitivity."

**IR means:** The object's dominant visual character is driven by **dust scattering, thermal re-emission, or continuum processes** rather than line emission. The target rewards broadband or luminance imaging over narrowband, and benefits from IR-pass filters or modified camera response.

**Imaging implication:** IR-flagged objects are broadband-first targets. Narrowband filters may suppress their primary signal rather than enhance it.

### 48.2 IR Presence Criteria (Astrophysical)

IR presence bit (6400) is set when the object exhibits one or more of:
- Dust scattering as primary brightness mechanism (reflection nebulae)
- Thermal dust re-emission (protostellar envelopes, YSOs, dusty HII regions)
- Stellar continuum dominance in a diffuse structure (open cluster nebulosity)
- Known infrared excess in published photometry

IR is explicitly NOT set for:
- Pure line-emission objects (PN, SNR, HII without dust flags) where continuum is negligible
- Galaxies (IR character too complex and target-specific for L0 inference)
- Dark nebulae (IR absorption targets, not IR emission — handled as associated_objects)

### 48.3 L0 Inference Rules by SIMBAD otype

Three-state inference: `confirmed` / `conditional` / `none`

| otype | otype Description | IR Inference | Rationale |
|---|---|---|---|
| RNe | Reflection nebula | confirmed | Dust scattering is defining mechanism |
| YSO | Young stellar object | confirmed | Protostellar dust envelope |
| pA* | Post-AGB star | confirmed | Dusty circumstellar shell |
| HII | HII region | conditional | Dust mixed with ionized gas — common but not universal |
| MoC | Molecular cloud | conditional | Dust-rich but IR emission depends on embedded sources |
| DNe | Dark nebula | none | Absorber, not emitter — handled as associated_object |
| PN | Planetary nebula | none | Pure line emission dominates |
| SNR | Supernova remnant | none | Synchrotron/line emission; negligible dust |
| GlC | Globular cluster | none | Stellar continuum only, no dust structure |
| OpC | Open cluster | conditional | Only if associated nebulosity present |
| EmO | Emission object (generic) | conditional | Requires secondary otype check |
| G | Galaxy | none | Too complex for L0 IR inference |

**Conditional rule:** When IR = `conditional`, set presence bit only if a secondary confirming signal exists (e.g. broadband flag already set, or cross-match with WISE/Spitzer known source). Otherwise leave IR bit unset. L1/L2 enrichment passes will refine.

### 48.4 SNR Handling for IR Band

IR participates in **presence matching only**. SNR calculation for IR regime is deferred:

- Planner treats IR SNR as `null` for all objects
- Exposure recommendation for IR-flagged objects uses broadband (luminance) SNR model
- Dedicated IR sensitivity model (camera QE curve in IR regime) is V2+ scope
- UI displays IR presence as a target characteristic flag, not an exposure calculator input

### 48.5 is_broadband_target Relationship

IR confirmation automatically sets `is_broadband_target = true`.

```
IF presence_mask & 6400 > 0 THEN is_broadband_target = true
```

This is a derived invariant — not stored separately, enforced at ingest and promotion.

### 48.6 Profile Valence Interaction

IR participates in Band Selection Matrix as a full citizen:
- Selectable as Required, Allowed, Dominant, 2nd Dominant
- Follows all Section 47.4 invariants (dominance requires required, etc.)
- Generates presence keys normally via Section 47.5 algorithm

IR as Dominant band is a valid and meaningful selection — it expresses "I am primarily hunting reflection/dust targets." The planner respects this intent fully.


---

# PART XXII — PER-BAND CONFIDENCE MODEL (LOCKED — 2026-02-19)

## 49. Per-Band Confidence — Schema and Inference Canon

### 49.1 Rationale
Object-level confidence (L0/L1/L2/L3) describes how well we know the object overall.
Band strength (ha_strength, oiii_strength, etc.) describes expected emission intensity.
Neither answers: **how certain are we that this specific band's strength value is accurate?**

Per-band confidence provides that answer. It drives individual filter cell paint in the Rig Planner — same object, different certainty per band.

### 49.2 Schema Definition (LOCKED)

Seven additional smallint columns in `public.objects`:

```sql
ALTER TABLE public.objects
  ADD COLUMN ha_confidence   smallint NOT NULL DEFAULT 0,
  ADD COLUMN oiii_confidence smallint NOT NULL DEFAULT 0,
  ADD COLUMN sii_confidence  smallint NOT NULL DEFAULT 0,
  ADD COLUMN hb_confidence   smallint NOT NULL DEFAULT 0,
  ADD COLUMN nii_confidence  smallint NOT NULL DEFAULT 0,
  ADD COLUMN heii_confidence smallint NOT NULL DEFAULT 0,
  ADD COLUMN ir_confidence   smallint NOT NULL DEFAULT 0;
```

**Storage:** 7 × 2 bytes = 14 bytes per object. Negligible at 256K rows (~3.5MB total).
**Default:** 0 (no basis) for all existing rows. Populated via inference pass.
**Pattern:** Matches strength column naming convention exactly — planner logic treats them as parallel arrays.

### 49.3 Confidence Scale (LOCKED — mirrors L-tier)

| Value | Meaning | L-tier equivalent |
|---|---|---|
| 0 | No basis — band likely absent or unknown | X |
| 1 | Low — possible for this otype class | L1 |
| 2 | Medium — typical for this otype | L2 |
| 3 | High — defining characteristic of otype | L3 |

**Ceiling rule:** A band confidence value SHALL NOT exceed the object's overall L-tier numeric value. An L0 object has max band confidence = 0 until enrichment raises the object tier.

**Exception:** L0 inference sets band confidence during the inference pass itself — this is what L0 means. L0 objects may have band confidence 1-2 from otype inference. Band confidence 3 requires L2+ object tier (measured data).

### 49.4 L0 Inference Rules by otype (LOCKED)

Per-band confidence values assigned during L0 inference pass:

| otype | Ha | OIII | SII | Hb | NII | HeII | IR |
|---|---|---|---|---|---|---|---|
| HII | 3 | 2 | 2 | 1 | 2 | 0 | 2 |
| PN | 2 | 3 | 1 | 2 | 1 | 2 | 0 |
| SNR | 2 | 1 | 3 | 0 | 1 | 0 | 0 |
| RNe | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| YSO | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| EmO | 2 | 1 | 1 | 1 | 1 | 0 | 1 |
| MoC | 1 | 0 | 0 | 0 | 0 | 0 | 2 |
| OpC | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| GlC | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| G   | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| AGN | 1 | 2 | 0 | 1 | 2 | 3 | 0 |
| LIN | 1 | 2 | 0 | 1 | 2 | 2 | 0 |

*All other otypes default to 0 across all bands.*

### 49.5 Planner Confidence Paint Model (LOCKED — 2026-02-19)

Filter cell presentation uses **two independent visual axes:**

**Opacity** = L-tier of the object (how well we know it overall)
**Texture** = whether the determining band confidence is inferred or measured

| | Cross-hatch (inferred) | Solid (measured) |
|---|---|---|
| L3 | Cross-hatch 50% | Solid 50% |
| L2 | Cross-hatch 35% | Solid 35% |
| L1 | Cross-hatch 20% | Solid 20% |
| L0 | Cross-hatch 5% | Solid 5% |
| X  | Suppressed | Suppressed |

**Axis behavior:**
- A cell moves **up** (higher opacity) as the object advances through L-tiers — independent of how the value was determined
- A cell moves **right** (cross-hatch → solid) when band confidence transitions from inferred to measured — independent of L-tier

**Multi-band filter rule (LOCKED):**
For filters that pass multiple bands (e.g. L-Xtreme passes Ha + OIII, Quad-band passes Ha + OIII + SII + Hb), the filter cell presentation is determined by the **most confident band** passing through that filter:
- Opacity = L-tier of highest-confidence band present
- Texture = solid if ANY passing band has measured confidence; cross-hatch only if ALL passing bands are inferred

**Example:** L-Xtreme filter for an object with inferred Ha (cross-hatch) and measured OIII (solid) → filter cell renders **solid** at OIII band's L-tier opacity. Measured evidence dominates.

**Object L-tier badge** (SEA system) remains the overall object quality indicator. Per-band confidence governs individual filter cell presentation only.

### 49.6 Null Data Policy for V1

All 256K existing objects have band_confidence = 0 (DEFAULT) at schema creation. This is intentional and valid:
- Planner renders all filter cells as suppressed/hatched for unscored objects
- User sees honest "no inference data" state rather than false confidence
- L0 inference pass populates values; runs as background enrichment job
- V1 ships with inference pass complete for SURFACE tier (76K objects)
- RAW tier inference deferred to V1.1

### 49.7 Query Pattern (Planner Use)

```sql
-- Find objects with high Ha confidence and medium+ OIII
SELECT * FROM public.objects
WHERE layer = 'SURFACE'
  AND ha_confidence >= 3
  AND oiii_confidence >= 2
  AND presence_mask & 300 = 300;  -- both Ha and OIII bits set
```

Band confidence and presence_mask work together — presence says the band exists, confidence says how sure we are.


---

# PART XXIII — SMART TELESCOPE & INTEGRATED OPTICAL SYSTEM SUPPORT (LOCKED — 2026-02-19)

## 50. Smart Telescope Equipment Model

### 50.1 Strategic Rationale
Smart telescopes (ZWO Seestar, Unistellar Odyssey, Dwarf III, etc.) represent the fastest-growing segment of amateur astrophotography. Excluding them produces an eroding customer base as the beginner-to-intermediate market expands. Including them makes SkyPix the natural upgrade path as users outgrow integrated systems.

**SkyPix supports all imaging hardware without exception.**

### 50.2 The Integration Problem
Standard SkyPix equipment model assumes three separable kits:
- Rig Kit (optics + mount)
- Camera Kit (sensor)
- Filter Kit (user-selectable filters)

Smart telescopes violate this assumption. Optics, sensor, and filter are a single integrated unit. The filter is not user-selectable — it is fixed at manufacture.

### 50.3 Equipment Table Flag (LOCKED)

Add `is_integrated_system` boolean to equipment table:

```sql
ALTER TABLE public.equipment
  ADD COLUMN is_integrated_system boolean NOT NULL DEFAULT false,
  ADD COLUMN integrated_filter_type text,      -- e.g. 'broadband', 'dual-band', 'LP'
  ADD COLUMN integrated_filter_passband jsonb; -- center wavelengths + bandwidths
```

When `is_integrated_system = true`:
- Three-kit model collapses to single entry
- Filter Kit UI is suppressed — filter shown as read-only system property
- SNR calculation uses fixed filter parameters from `integrated_filter_passband`
- Band Selection Matrix still fully functional — user still expresses intent
- Filter Confidence Matrix shows only the integrated filter row

### 50.4 Required Specs for SNR Calculation

| Spec | Source |
|---|---|
| Aperture (mm) | Published manufacturer spec |
| Focal length (mm) | Published manufacturer spec |
| Sensor dimensions + pixel size | Published manufacturer spec |
| Read noise (e-) | Published spec or community measurement |
| Peak QE or QE curve | Published spec or ASI sensor datasheet |
| Fixed filter type + passband | Published spec |

All specs available from manufacturer documentation. ZWO publishes full sensor specs for Seestar S50 (Sony IMX462), Unistellar publishes Odyssey specs, Dwarf Labs publishes DWARF III specs.

### 50.5 Known Integrated Systems (Seed List)

| System | Aperture | FL | Sensor | Filter |
|---|---|---|---|---|
| ZWO Seestar S50 | 50mm | 250mm | IMX462 | Dual-band Ha+OIII |
| ZWO Seestar S30 | 30mm | 150mm | IMX462 | Broadband |
| Unistellar Odyssey | 85mm | 450mm | IMX585 | Broadband |
| Dwarf III | 24mm | 100mm | IMX678 | Broadband |

*Specs to be verified against manufacturer documentation before equipment DB entry.*

### 50.6 Planner Behavior for Integrated Systems

- Band Selection Matrix: fully functional — user expresses narrowband intent
- Filter Confidence Matrix: single row showing integrated filter performance
- SNR calculation: uses fixed filter passband, cannot be changed
- Exposure recommendation: calibrated for fixed filter — different baseline than modular rigs
- UI note displayed: "Integrated system — filter fixed at [type]. Showing achievable SNR for fixed configuration."

### 50.7 User Experience Implication

Seestar user opens SkyPix, selects NGC 6992 (Eastern Veil):
- System recognizes Seestar S50 as integrated dual-band (Ha+OIII)
- Filter Confidence Matrix shows one row: "Seestar Dual-Band" with Ha+OIII cells populated
- SNR calculated for 50mm aperture at f/5 with IMX462 + dual-band filter
- Exposure recommendation: "4.2h for SNR 40 at your site"
- User understands exactly what their integrated scope can achieve on this target

This is the beginner's entry point. When they outgrow the Seestar and buy a modular rig, SkyPix already knows their imaging history and project library. Retention is structural, not accidental.


---

## 51. Manufacturer Integration Strategy (BUSINESS DEVELOPMENT — 2026-02-19)

### 51.1 Opportunity
Smart telescope manufacturers have large captive user bases with no dedicated planning intelligence layer. SkyPix arrives pre-configured for their exact hardware. The `is_integrated_system` flag (Section 50.3) makes this a configuration, not a rebuild.

**Target manufacturers (priority order):**
1. ZWO (Seestar S50/S30) — largest smart scope installed base globally
2. Unistellar (Odyssey) — premium segment, science-partnership brand
3. Dwarf Labs (DWARF III) — price-sensitive entry segment

### 51.2 Commercial Models

**Option A — OEM White-Label**
"Seestar Planner powered by SkyPix." Manufacturer pays per-unit or per-user licensing. SkyPix branding optional. Highest revenue per user, requires deeper partnership.

**Option B — Co-Branded Bundle**
SkyPix remains SkyPix. Seestar purchase includes 12 months SkyPix Pro. Manufacturer subsidizes subscription as product feature. Lower per-unit revenue, mass distribution.

**Option C — Referral Integration**
SkyPix ships with manufacturer profile pre-loaded. Manufacturer promotes SkyPix to user base. Revenue share on conversions. Lowest friction to execute.

**Recommended entry point:** Option C to establish relationship, negotiate toward Option B at scale.

### 51.3 Integration Cleanness Checklist
- [ ] `is_integrated_system` flag in equipment table ✅ (Section 50.3)
- [ ] Fixed filter passband in equipment record ✅
- [ ] Filter Kit UI suppression for integrated systems ✅
- [ ] Pre-loaded rig profile at first launch (one config file per manufacturer)
- [ ] Manufacturer co-brand slot in header UI (logo + "powered by SkyPix")
- [ ] Onboarding flow skips kit configuration entirely for integrated users

Items 4-6 are UI additions only — no schema changes required.

### 51.4 Timing
**V1 prerequisite:** Equipment DB populated with smart scope specs.
**V1.1 target:** Manufacturer outreach after working product exists.
**Prerequisite for outreach:** Working Rig Planner + 3-5 real Seestar planning examples demonstrating genuine value.

### 51.5 Strategic Note
Users who start on a Seestar and graduate to a modular rig carry their SkyPix project history with them. Manufacturer integration creates the entry point. SkyPix's own value retains them through every equipment upgrade. Retention is structural at both ends.


### 51.6 Reciprocal Marketing Value (LOCKED)
Manufacturer integration creates a two-way marketing amplifier:

- Manufacturer promotes their hardware as "SkyPix-enabled" → SkyPix brand reaches manufacturer's entire customer base and marketing budget
- Every Seestar review, unboxing, YouTube tutorial, and ad that mentions planning intelligence is organic SkyPix exposure
- SkyPix appears in manufacturer retail channels, box copy, and setup guides
- Community word-of-mouth: "get SkyPix" becomes standard advice in smart scope forums

**Net effect:** Manufacturer's marketing spend partially funds SkyPix customer acquisition at zero incremental cost to SkyPix.

This is not a side benefit — it is a primary reason to pursue Option C (referral integration) as the entry point. Low friction to execute, immediate brand exposure, negotiating leverage toward Option B as user base grows.


### 51.7 Upgrade Path as Revenue Stream
The smart telescope → modular rig upgrade path is commercially significant for all parties:

- **For the user:** SkyPix project history, targets, and SNR baselines travel with them. No restart. No lost work. The upgrade feels like a promotion, not a migration.
- **For SkyPix:** User retains subscription and immediately unlocks fuller platform capability (three-kit model, full filter selection, advanced SNR). Upgrade increases user engagement and retention.
- **For the manufacturer:** SkyPix demonstrates to smart scope users what advanced modular imaging can achieve. Users who see what a Takahashi + Player One combination produces in SkyPix's planner are primed to want that hardware. SkyPix becomes a de facto upgrade motivation engine.

**Net effect:** Manufacturer integration seeds the advanced market. Every Seestar user who upgrades to a modular rig is a new unit sale the manufacturer can trace back to SkyPix exposure. That is a quantifiable ROI argument for the partnership conversation.


---

## 52. Wave Ingestion Results Log (Permanent — append only)

### Wave 1 — Interaction Universe

| Catalog | Date | Aliases Added | New RAW Objects | Collisions | DB Size |
|---|---|---|---|---|---|
| Arp (VII/192/arpord) | 2026-02-19 | 214 | 124 | 0 | 280MB |

**Arp notes:** 214 matched to existing NGC/IC objects (aliases only). 124 genuinely new RAW objects — peculiar galaxies absent from legacy catalogs. Haversine matching confirmed. J2000 normalization confirmed. Total accounted: 338/338 ✅


| HCG (VII/213) | 2026-02-19 | 100 | 100 | 0 | 281MB |

**HCG notes:** 100 groups created as RAW objects (class GxyG) regardless of centroid proximity to existing galaxies — groups are distinct astrophysical entities, not reducible to members. 463 member galaxies inserted into associated_objects (association_type='compact_group_member'). Total accounted: 100/100 ✅

**Canon addition — Group Object Policy (LOCKED):**
Catalog entries representing astrophysical *systems* (compact groups, galaxy clusters, associations) SHALL always exist as independent objects rows. Centroid proximity to an existing object does not trigger alias-only treatment. The system identity is distinct from any individual member. Applies to: HCG, Arp-Madore, future cluster catalogs.


---

# PART XXIV — RIG PLANNER COMPUTATIONAL FUNCTIONS (LOCKED — 2026-02-19)

## 53. Lunar Occlusion Algorithm

### 53.1 Two-Phase Bounding Box + Spherical Trig Pattern

Full haversine computation against 256K objects at query time is prohibitively expensive. The canonical occlusion check uses a two-phase approach:

**Phase 1 — Bounding box pre-filter (index-backed, microseconds):**

```python
margin_deg = 0.5  # Moon angular radius ~0.26° + safety margin

# Correct for declination compression of RA
ra_min = moon_ra - margin_deg / cos(radians(moon_dec))
ra_max = moon_ra + margin_deg / cos(radians(moon_dec))
dec_min = moon_dec - margin_deg
dec_max = moon_dec + margin_deg
```

SQL using existing `idx_objects_radec` btree index — no new index required:

```sql
SELECT object_id, ra_deg, dec_deg FROM public.objects
WHERE ra_deg BETWEEN %(ra_min)s AND %(ra_max)s
AND dec_deg BETWEEN %(dec_min)s AND %(dec_max)s
AND layer = 'SURFACE';
```

Reduces candidate set from 256K to typically 5-20 objects.

**Phase 2 — Haversine only on survivors:**

```python
from math import radians, degrees, sin, cos, asin, sqrt

def haversine_sep(ra1, dec1, ra2, dec2):
    dra = radians(ra2 - ra1)
    ddec = radians(dec2 - dec1)
    a = (sin(ddec/2)**2 +
         cos(radians(dec1)) * cos(radians(dec2)) * sin(dra/2)**2)
    return degrees(2 * asin(sqrt(a)))

occluded = [obj for obj in candidates
            if haversine_sep(moon_ra, moon_dec,
                             obj['ra_deg'], obj['dec_deg']) < margin_deg]
```

### 53.2 RA Wraparound Edge Case (REQUIRED)

When Moon is near RA 0°/360° boundary, bounding box splits into two queries:

```python
if ra_min < 0:
    # Query 1: ra_deg BETWEEN (ra_min + 360) AND 360
    # Query 2: ra_deg BETWEEN 0 AND ra_max
elif ra_max > 360:
    # Query 1: ra_deg BETWEEN ra_min AND 360
    # Query 2: ra_deg BETWEEN 0 AND (ra_max - 360)
else:
    # Single query as above
```

### 53.3 Performance Envelope
- Bounding box phase: index scan ~microseconds
- Haversine on survivors: ~20 FP ops each, negligible
- Net: effectively free at 256K object scale

### 53.4 Occlusion Margin Policy
- Moon angular radius: ~0.26° (varies ±0.03° with lunar distance)
- Default planning margin: 0.5° (accommodates radius + seeing + user preference)
- User-adjustable: allow 0.3°–5.0° range in Rig Kit settings

---

## 54. Chatty Development Commentary as Inline Documentation

### 54.1 Rationale
Chatty's code development process naturally produces precise technical commentary explaining *why* each implementation decision was made. This commentary is more valuable than post-hoc documentation because it captures the reasoning at the moment of decision.

### 54.2 Canon Practice
When Chatty delivers implementation code, her inline commentary SHALL be preserved as-is in the codebase. Do not strip explanatory comments during code review or integration.

**What to preserve:**
- Decision rationale comments (`# Using haversine here because...`)
- Edge case explanations (`# RA wraparound requires split query when...`)
- Performance notes (`# Bounding box reduces 256K to ~20 candidates before...`)
- Canon references (`# Per LDD Section 7.4 — J2000 normalization required`)

**What to strip:**
- Progress narration (`# Now we load the staging table...`)
- Obvious mechanics (`# Loop through results`)

### 54.3 LDD Capture
When Chatty's commentary reveals a non-obvious algorithm decision, Claude captures it in the relevant LDD section. The lunar occlusion two-phase pattern (Section 53) is an example — Chatty's implementation reasoning became permanent architectural canon.


| VV (VII/62) | 2026-02-19 | 729 | 1281 | 0 | 281MB |

**VV notes:** 2010 systems staged. 729 aliases to existing objects. 1281 genuinely new RAW system objects. 3011 components into associated_objects. Total accounted: 2010/2010 ✅

**System Catalog Rule — EMPIRICALLY VALIDATED (Arp + HCG + VV):**
System catalogs describing interacting systems, compact groups, or physical associations SHALL always create canonical system object rows (ARPxxx, HCGxxx, VVxxxx) even when positional matches exist. System identity is distinct from any member or nearby object. Components attach to the system. Aliases link catalogs across identities. This rule is now proven across three independent catalogs — it is no longer policy, it is validated architectural principle.

**Wave 1 interaction universe running total:**
- Arp: 124 new systems
- HCG: 100 new systems  
- VV: 1281 new systems
- **Total: 1505 new interaction universe objects**


| KPG (VII/60) | 2026-02-19 | 34 same-system aliases | 569 | 0 | 281MB |

**KPG notes:** 603 systems staged. 34 same-system aliases (≤10" separation — same physical system, different catalog identity). 569 new independent RAW system objects. Total accounted: 603/603 ✅

**System Identity Rule — REFINED AND LOCKED (four-catalog validation):**

1. A physical system has exactly one canonical object row.
2. Multiple catalogs describing the same system → aliases, not duplicate objects.
3. Independent system catalogs produce independent objects when identity is not proven.
4. **Identity proof threshold = ≤10" spherical separation.**

This threshold is now the canonical gate for all future extragalactic system ingests. Applies to: Arp-Madore, AM pairs, southern interacting catalogs, all future system catalogs.

**Wave 1 interaction universe running total (four catalogs complete):**

| Catalog | New Systems | Aliases | Status |
|---|---|---|---|
| Arp | 124 | 214 | ✅ |
| HCG | 100 | 100 | ✅ |
| VV | 1281 | 729 | ✅ |
| KPG | 569 | 34 | ✅ |
| **Total** | **2074** | **1077** | |


| AM (VII/170) | 2026-02-21 | 5973 | 5973 | 0 | TBC |

**AM notes:** ~6,000 southern peculiar galaxies. Large-scale validation of System Catalog Rule and System Identity Rule. Total accounted: confirmed ✅

---

## 55. Wave 1 Completion Record (LOCKED — 2026-02-21)

### 55.1 Final Quantitative Outcome

| Catalog | New Objects | Aliases | Status |
|---|---|---|---|
| Arp (VII/192) | 124 | 338 | ✅ |
| HCG (VII/213) | 100 | 100 | ✅ |
| VV (VII/62) | 2010 | 2010 | ✅ |
| KPG (VII/60) | 569 | 603 | ✅ |
| AM (VII/170) | 5973 | 5973 | ✅ |
| **Wave 1 Total** | **8,776** | **9,024** | ✅ |

### 55.2 Canon Principles Validated by Wave 1

All five principles proven empirically across five independent catalogs:

- ✅ Single objects table — all catalogs merged into one canonical object space
- ✅ Alias-first enrichment — catalog identity preserved without fragmenting object ownership
- ✅ Deterministic rebuilds — every ingestion run reproducible from source catalogs
- ✅ System Catalog Rule — system catalogs represent astronomical identities, not duplicates
- ✅ System Identity Rule — ≤10" = same physical system (alias); >10" = independent object

### 55.3 Architectural Significance (LOCKED)

**Before Wave 1:** SkyPix described objects.
**After Wave 1:** SkyPix describes astrophysical relationships.

SkyPix now models interacting galaxies, mergers, tidal systems, compact groups, and gravitationally bound pairs. Planner capability expands to: multi-target framing, interaction morphology planning, tidal feature optimization, advanced targeting.

This marks the transition from catalog aggregation to curated astrophysical modeling platform.

### 55.4 Wave 1 Promotion Decision (AUTHORIZED — David 2026-02-21)

All Wave 1 interaction systems promoted RAW → SURFACE:
- Scientifically valid curated sources
- Observationally meaningful
- Stable identifiers
- First intentional expansion of the curated SkyPix universe

**Post-promotion:** RAW layer returns to discovery staging only. SURFACE becomes the true observable universe.

### 55.5 Post-Promotion Actions (Deferred)
1. Interaction morphology enrichment
2. SIMBAD classification reconciliation
3. Planner scoring integration
4. Surface balance audit


---

# PART XXV — PROMOTION DOCTRINE & STRUCTURAL CLASS CANON (LOCKED — 2026-02-21)

## 56. RAW → SURFACE Promotion Doctrine

### 56.1 Governing Principle
Promotion is class-dependent. There is no universal gate. SURFACE must remain intentional, not exhaustive. Each class requires its own qualification logic balancing astrophysical meaning, imaging usability, identity stability, and SUD workflow clarity.

**SUD Constraint:** SURFACE classes must support meaningful user project selection. If users cannot sensibly build projects from a class, it does not promote.

### 56.2 Promotion Evaluation Axes
- **Physical Independence:** Is the object an identifiable astrophysical entity, not substructure?
- **Imaging Meaningfulness:** Can users frame and pursue it as a target?
- **Identity Stability:** Does promotion avoid duplication with parent structures?
- **SUD Utility:** Can this class support project lists, planning queries, LFU learning?

### 56.3 Class-Based Promotion Rules (LOCKED)

| Class | Promotion Rule | Size Gate | Notes |
|---|---|---|---|
| EN (Emission Nebula) | Promote if physically independent + has spectral profile | > 15" | Sub-15" → HOLDING |
| DN (Dark Nebula) | Promote if angular size meaningful for framing | > 30' | Absorption target; is_broadband_target=true as baseline. If associated emission object exists → planner inherits emission spectral profile from association. Emission association overrides broadband default. |
| OC (Open Cluster) | Bulk promotion — all | None | Unambiguous independent targets |
| GC (Globular Cluster) | Promote if resolvable | > 2' | Sub-2' GC → HOLDING with rig_suitability flag; effectively stellar below this threshold |
| PN (Planetary Nebula) | Promote if measurable angular extent, non-stellar | > 5" AND non-stellar | Stellar PN (otype=PN* or size=0) → HOLDING; 5"-30" range gets rig_suitability advisory |
| SNR (Supernova Remnant) | Promote all | None | Always structurally independent |
| WR Region | Promote emission region if > 15" | > 15" | Region is target, not the star; classify as EN |
| G (Galaxy) | Thematic waves only | TBD per wave | Quality range too wide for bulk promotion |
| LES (Large Emission Structure) | Promote — wide-field targets | > 1° typical | New class — see Section 57 |
| GxyG (Galaxy Group) | Wave-by-wave — Wave 1 promoted | Per wave auth | System Catalog Rule applies |
| GxyP (Galaxy Pair) | Wave-by-wave — Wave 1 promoted | Per wave auth | System Identity Rule applies |

### 56.4 PN and GC Rig Suitability Rules (LOCKED)

**PN promotion criteria:**
- Angular size > 5" AND non-stellar classification → SURFACE
- Stellar PN (simbad_otype = 'PN*' or size = 0) → HOLDING — unresolved point source, no planning value
- PN 5"–30": rig_suitability advisory — planner flags minimum useful aperture (150mm+, f/7+)
- PN > 30": promote without advisory

**GC promotion criteria:**
- Angular size > 2' → SURFACE
- GC < 2' → HOLDING with rig_suitability flag — effectively stellar, unresolvable at typical focal lengths

Rig suitability is a planner advisory only — never a demotion trigger. Objects remain at their assigned tier; the planner informs the user when their active rig is unsuitable for the target.

### 56.5 SIMBAD otype Preservation
SkyPix classes may consolidate multiple otypes but must remain scientifically interpretable and preserve lineage. SkyPix is a curation layer, not a taxonomy replacement. `simbad_otype` column is never overwritten by SkyPix class assignment.

---

## 57. Large Emission Structure (LES) — New Structural Class (LOCKED — 2026-02-21)

### 57.1 Definition
LES objects are large-scale astrophysical emission structures — HII complexes, superbubbles, and extended emission regions — whose angular extent typically exceeds 1° and which represent valid wide-field and mosaic planning targets.

**LES is distinct from EN (discrete emission nebula):**
- EN: discrete, self-contained emission object, typically < 2°
- LES: large-scale complex, typically > 1°, often containing embedded EN/OC/PN objects

### 57.2 Planner Behavior
- Valid SUD project entity — users can build wide-field and mosaic projects around LES objects
- Framing recommendations calibrated for wide-field rigs (short focal length, large sensor)
- Embedded objects associated via `associated_objects` table — NOT contained, associated
- Multiple objects may associate with the same LES without ownership conflict
- LES objects do not own their associated objects — any object may associate with multiple LES entries

### 57.3 Gum Catalog — Architectural Resolution (LOCKED)
Previous ingestion difficulty arose from treating Gum entries as normal EN objects. Gum regions are LES class. This resolves the architectural ambiguity permanently.

**Gum ingestion parameters:**
- Class: `LES`
- Layer: SURFACE (valid wide-field planning targets)
- Associations: embedded clusters, compact HII regions linked via associated_objects
- Source: VizieR table TBC (confirm at recon phase)
- Coordinate epoch: verify at recon
- Size gate: none — all Gum entries are LES by definition

**Gum is not a container.** Objects associate with Gum regions; Gum regions do not own objects. An object embedded in Gum 15 may also associate with a molecular cloud complex and a stellar OB association simultaneously. The association model handles this naturally.

### 57.4 Future LES Candidates
- Gum catalog
- Large Magellanic Cloud HII complexes
- Galactic superbubbles
- MWP Bubbles (Wave 4) — evaluate for LES classification at recon


### 56.6 Dark Nebula Spectral Profile Canon (LOCKED — 2026-02-21)

Dark nebulae do not emit — they absorb. However DN objects silhouetted against emission backgrounds are narrowband targets where the background emission is the signal and the DN provides the absorption contrast structure.

**DN spectral profile rules:**

- DN in isolation (no background emission association): `is_broadband_target = true`, spectral columns null
- DN with associated emission object: planner inherits emission spectral profile from the canonical emission object via `associated_objects` relationship. Emission association overrides broadband default.

**Planner logic:**
```
IF DN.associated_objects contains emission canonical
  → use emission object spectral profile for filter recommendations
  → is_broadband_target remains true (broadband still valid)
ELSE
  → broadband only
```

**Reference case:** Barnard 33 (Horsehead Nebula) — DN silhouetted against IC 434 (HII). B33 is associated with IC 434 as canonical. Planner recommends Ha/OIII filters based on IC 434's spectral profile, not B33's (which has none). The DN provides the visual target; the emission object provides the spectral planning basis.

This was established in LDD Part XVII (IC 434/B33 canonical pattern) and is confirmed here as the universal DN spectral rule.


### 56.7 Layer Access Model (LOCKED — 2026-02-21)

**All objects in all layers are searchable and identifiable by ID.**
Layer determines SUD pipeline eligibility, not discoverability.

| Layer | Searchable | ID Lookup | SUD Scrape | Planner Target |
|---|---|---|---|---|
| SURFACE | ✅ | ✅ | ✅ | ✅ |
| RAW | ✅ | ✅ | ❌ | ❌ |
| HOLDING | ✅ | ✅ | ❌ | ❌ |
| QUARANTINE | ✅ | ✅ | ❌ | ❌ |

**User experience for non-SURFACE objects:**
- Object is found and displayed with full available data
- Layer status shown honestly ("RAW — not yet curated for planning")
- Rig suitability advisory shown where applicable
- No SUD project creation available until object promotes to SURFACE

**Strategic implication:** As a user's rig improves, previously inaccessible objects become SUD-eligible automatically — not because the database changed, but because the rig_suitability advisory resolves. The database never hides objects; the planner advises appropriately.

