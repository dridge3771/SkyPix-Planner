## Section 297 — presence_mask Canon & Count Engine Specification (LOCKED 2026-04-08)

**Source:** Live SCD audit + team resolution of schema ambiguity
**Resolves:** Section 296.6 provisional hold on count/retrieve logic

---

### 297.1 — presence_mask: Authoritative Canon (LOCKED)

`presence_mask` in `public.objects` is band-resolved, decodable, and
safe for query/count gating. The encoding is intact in the live SCD.
No drift from the original design intent.

**Encoding (additive bitmask):**

| Band  | Bit value |
|-------|-----------|
| Hα    | 100       |
| OIII  | 200       |
| SII   | 400       |
| Hβ    | 800       |
| NII   | 1600      |
| HeII  | 3200      |
| IR    | 6400      |

**Live SCD distribution (SURFACE tier, verified 2026-04-08):**

| presence_mask | Decode                          | Count  |
|---------------|---------------------------------|--------|
| 0             | No bands — broadband/unchar.    | 37,535 |
| 9500          | Hα+OIII+SII+Hβ+NII+IR          | 24,069 |
| 6500          | Hα+IR                           | 18,771 |
| 5900          | Hα+OIII+Hβ+NII+HeII            |  2,769 |
| 6400          | IR only                         |  2,024 |
| 4300          | Hα+OIII+Hβ+HeII                |  1,639 |
| 6300          | Hα+OIII+SII+Hβ+NII+HeII       |  1,020 |
| 2300          | Hα+OIII+SII+NII                |    363 |

Total SURFACE: 88,190

---

### 297.2 — Broadband/Uncharacterized Population

`presence_mask = 0` identifies objects with no characterized emission
bands. This is the broadband/uncharacterized population (37,535 objects).

**Terminology (canonical):** broadband_first / uncharacterized

This term is deliberately hyphenated to preserve future flexibility:
- Some are true broadband objects (reflection nebulae, galaxies,
  open clusters, continuum-dominated)
- Some are objects not yet spectrally characterized — they may have
  emission but it has not been derived or confirmed

The distinction between true broadband and uncharacterized will be
resolved in future enrichment passes. For query purposes at beta,
`presence_mask = 0` is the single gate for both populations.

---

### 297.3 — Count Engine: Band Query Predicates

Band selection maps directly to bitwise AND operations on presence_mask.

**Single band predicates:**

```sql
-- Broadband / uncharacterized
presence_mask = 0

-- Hα
presence_mask & 100 != 0

-- OIII
presence_mask & 200 != 0

-- SII
presence_mask & 400 != 0

-- Hβ
presence_mask & 800 != 0

-- NII
presence_mask & 1600 != 0

-- HeII
presence_mask & 3200 != 0

-- IR
presence_mask & 6400 != 0
```

**Multi-band selection (OR / union mode — default):**

When a user selects multiple bands, an object qualifies if ANY selected
band bit is present. This is the union mode — the advisory system
uses the same logic.

```sql
-- Example: user selects Hα AND OIII (union — either qualifies)
(presence_mask & 100 != 0) OR (presence_mask & 200 != 0)

-- Generalised form for selected band set B:
-- object qualifies if (presence_mask & B) != 0
-- where B = bitwise OR of all selected band values
(presence_mask & :selected_band_union) != 0
```

**AND mode (strict — future option):**

If a future "require all selected bands" mode is added:
```sql
-- Object must have ALL selected bands
(presence_mask & :selected_band_union) = :selected_band_union
```

AND mode is not implemented at beta. Union mode is the default and only
mode at launch.

**Broadband + Narrowband combined (mixed session):**

```sql
-- Union of broadband population and any narrowband band selection
presence_mask = 0
OR (presence_mask & :selected_band_union) != 0
```

---

### 297.4 — Count Engine: Full Predicate Specification

The count predicate is built incrementally. All stages use the same
logic as Retrieve — single predicate source, no divergence permitted.

**Stage 1: Spectral gate**

```sql
-- No spectral filter selected
(no spectral WHERE clause)

-- Broadband only
WHERE presence_mask = 0

-- Narrowband (one or more bands)
WHERE (presence_mask & :band_union) != 0

-- Both broadband and narrowband
WHERE presence_mask = 0
   OR (presence_mask & :band_union) != 0
```

Where `:band_union` = bitwise OR of all selected band bit values.
Example: Hα + OIII selected → band_union = 100 | 200 = 300

**Stage 2: OType/Class filter**

```sql
AND skypix_object_class IN (:selected_classes)
-- or
AND simbad_otype IN (:selected_otypes)
```

**Stage 3: Constellation**

```sql
AND constellation IN (:selected_constellations)
```

**Stage 4: Spatial (RA/Dec range)**

```sql
AND ra_deg BETWEEN :ra_min AND :ra_max
AND dec_deg BETWEEN :dec_min AND :dec_max
```

**Stage 5: Photometric**

```sql
AND v_mag BETWEEN :mag_min AND :mag_max
AND major_axis_arcsec BETWEEN :size_min AND :size_max
AND position_angle_deg BETWEEN :pa_min AND :pa_max
```

**Stage 6: Observability**

```sql
AND transit_month BETWEEN :month_min AND :month_max
```

**All stages combined:**

```sql
SELECT COUNT(DISTINCT oid)
FROM public.objects
WHERE layer = 'SURFACE'
  -- Stage 1: spectral
  AND (
      :broadband_selected AND presence_mask = 0
      OR :narrowband_selected AND (presence_mask & :band_union) != 0
      OR :no_spectral_filter
  )
  -- Stage 2: class/otype (if selected)
  AND (:no_class_filter OR skypix_object_class IN (:classes))
  -- Stage 3: constellation (if selected)
  AND (:no_constellation_filter OR constellation IN (:constellations))
  -- Stage 4: spatial (if selected)
  AND (:no_spatial_filter OR (
      ra_deg BETWEEN :ra_min AND :ra_max
      AND dec_deg BETWEEN :dec_min AND :dec_max
  ))
  -- Stage 5: photometric (if selected)
  AND (:no_mag_filter OR v_mag BETWEEN :mag_min AND :mag_max)
  AND (:no_size_filter OR major_axis_arcsec BETWEEN :size_min AND :size_max)
  -- Stage 6: observability (if selected)
  AND (:no_month_filter OR transit_month BETWEEN :month_min AND :month_max)
```

---

### 297.5 — Index Requirements

The following indexes are required for < 100ms count performance:

```sql
-- presence_mask — for spectral band queries
CREATE INDEX idx_objects_presence_mask
ON public.objects (presence_mask)
WHERE layer = 'SURFACE';

-- transit_month — for observability queries
CREATE INDEX idx_objects_transit_month
ON public.objects (transit_month)
WHERE layer = 'SURFACE';

-- constellation — for constellation queries
CREATE INDEX idx_objects_constellation
ON public.objects (constellation)
WHERE layer = 'SURFACE';

-- Combined spectral + observability (most common query pattern)
CREATE INDEX idx_objects_spectral_seasonal
ON public.objects (presence_mask, transit_month)
WHERE layer = 'SURFACE';
```

Jim to confirm indexes exist or create them.

---

### 297.6 — Hα Special Pleading: Retired

Prior discussion questioned whether Hα terrain strength should be
used as a query gate. This question is now closed.

`presence_mask & 100 != 0` is the authoritative Hα query gate.
No terrain strength filter. No special pleading. The bitmask is
the single source of truth for all band-based queries.

Hα terrain strength (`ha_strength`) continues to feed:
  - SNR engine signal calculations
  - SkyVu SHFM mist layer

It does not participate in count/retrieve query logic.

---

### 297.7 — Narrowband Population Reconciliation

Section 296.6 stated the narrowband population as 22,908 objects
(those with characterized OIII/SII strength values).

The presence_mask audit reveals the true narrowband-eligible population
is larger — any object with any non-zero presence_mask has at least
one characterized emission band. That totals 88,190 - 37,535 = 50,655
objects across SURFACE tier.

The 22,908 figure referred specifically to objects with OIII/SII
strength values (numeric Rayleigh-scale estimates). The presence_mask
population (50,655) is the correct gate for band-based queries.

**Corrected narrowband population: 50,655 SURFACE objects**
(presence_mask != 0)

Section 296.6 spectral filter summary updated accordingly:

  Narrowband (any band) → objects where (presence_mask & band_union) != 0
  Maximum narrowband pool at SURFACE tier → 50,655 objects

---

*Section 297 locked 2026-04-08.*
*Resolves presence_mask ambiguity. Count engine can now be built.*
*Jim: create indexes per 297.5 before count implementation.*
*Cathy: band_union parameter replaces per-band query logic in predicate builder.*
