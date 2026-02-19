
# SkyPix LDD Addendum — Rig Planner Canon Consolidation
Date: 2026-02-18
Status: Authoritative Addendum for Integration into Master LDD

---

## 1. 4D Location Canon

SkyPix supports dual-input location definition:

- Address → Lat/Lon → Elevation → Timezone/DST
- Explicit Lat/Lon (with optional elevation) → Timezone/DST

Home location propagates to new rigs by default.
Each rig may override its own 4D location.

Rig location governs:
- Transit time calculations
- DST qualifier
- Darkness convention clipping
- Atmospheric modeling
- Weather/AQI integration

---

## 2. Rig Identity Definition

A Rig is uniquely defined by:

1. Optics
   - Aperture diameter
   - Central obstruction
   - Focal length
   - Derived collecting area (mm² canonical)

2. Location (4D)

3. Horizon Polygon
   - Arbitrary az/alt vertex list
   - Accepts dense or sparse sampling
   - Vertical obstructions encoded as additional vertices (“teeth”)
   - Max 1 vertical obstruction per declination band (computational simplification)

4. Zenith Obstruction Polygon
   - Assembly-specific
   - No symmetry assumption
   - ≥3 vertices, flexible count
   - Clips visibility arcs if defined

---

## 3. Declination Band Model

- Band width defined in RK row 31
- Bands partition declination range
- Visibility arcs precomputed per band
- Regenerated when horizon changes
- Duplicated when rig is duplicated

Smaller band width improves fidelity when:
- Horizon segments are nearly parallel to declination circles
- Horizon sampling is coarse

User Guidance:
“For best accuracy: use regular 5° horizon samples, and reduce declination band width when your horizon has long slanted ridges near the east/west horizon.”

---

## 4. Visibility Arc Canon

Raw VA depends on:
- Declination band
- Horizon polygon
- Zenith obstruction

Eastern VA:
- Rising intersection → Meridian or obstruction boundary

Western VA:
- Meridian or obstruction clearing → Setting intersection

If obstruction interrupts band away from meridian:
TotalVA = RisingArc + SettingArc − ObstructionHourAngle

Up to two visible windows per band supported.

---

## 5. Minimum Elevation (RK Row 29)

Defines zenith-centered exclusion circle.

In Optimum mode:
- Clips reported visibility arcs
- May reduce VA to 0:00
- Object remains displayed (orange) if transit within darkness

---

## 6. Darkness Convention (RK Row 19)

Clips visibility arcs to dusk/dawn interval.
Derived from:
- Latitude
- Longitude
- Date (15th reference)
- DST qualifier
- Darkness convention selection

---

## 7. Mid-Month Cell Canon

Top: Lunar occlusion notation (dd or dd-dd)
Middle: Transit or Rising time (RK row 20)
Bottom Left: Eastern VA or total VA
Bottom Right: Western VA

Lunar occlusion defined by avoidance angle (RK row 30).

---

## 8. Exposure & SNR Canon

Inputs include:
- Rig collecting area (mm²)
- Focal length
- Camera QE
- Camera read noise
- Cooling delta + ambient temp
- Filter transmission curves (up to 4 bands)
- Sky brightness
- AQI
- Atmospheric density
- Exposure strategy (default 1 if null)
- Desired Image SNR
- Rig time budget (RK row 27)
- Max subframe exposure (RK row 28)

Time budget is global per rig per object.
If cap binds → New SNR displayed.

Subframe exposure ≤ RK row 28.

---

## 9. Camera Propagation Canon

- Camera name: informational only
- Specs retrieved from SkyPix equipment DB (editable)
- Highlight color used at 50% opacity in planner total time cells
- Confidence paint levels: 50%, 35%, 20%, 5%, Orange for X
- Rig eligibility matrix: 3 rows per rig
  1. Eligibility checkbox
  2. FOV (major/minor)
  3. Image scale

---

## 10. Filter Propagation Canon

- Filter name appears in Rig Planner header
- Displayed set determined solely by Filter Kit eligibility matrix
- Column pair per filter: Total Exposure + Subframe Duration
- Supports 1–4 bands
- Five-point transmission curve model per band
- Band shading tiers: 20%, 15%, 10%, 5%

---

## 11. Color Matrix Canon (Web Migration)

Replace GAS onEdit propagation with centralized Color Matrix:

- One column per device (rig/camera/filter)
- Rows represent opacity tiers:
  100%, 80%, 50%, 35%, 20%, 15%, 10%, 5%
- Applied via CSS/RGBA tokens
- Matrix grows/shrinks as devices added/removed

---

## 12. Design Intent Summary

The Rig Planner is:
- A geometric visibility engine
- A time-budget optimization engine
- A spectral signal optimization engine
- A lunar proximity warning system
- A project allocation tool

End of Addendum.
