# SkyPix Planner — Living Design Document

> **How to use this file (for non-coders / APs):**
> - Read this file to see all design rules, clarifications, and workflow logic for SkyPix Planner.
> - After each work session, copy/paste new clarifications or decisions here.
> - Use the "Session Summary" section at the end to track what was discussed or decided.
> - Reference this file for all coding, testing, or collaboration—so everyone follows the same logic.

---

## Requirements

- SkyPix Planner is a dynamic tool for astrophotographers to plan imaging sessions and optimize exposures for selected celestial objects.
- Supports multi-rig, multi-camera, multi-filter planning, with eligibility rules per rig.
- Integrates object emission spectra, filter transmission, camera QE, rig specs, and atmospheric constraints into SNR and exposure calculations.
- Output is a Planner sheet per rig, showing objects, observability, exposure time, filter breakdown, and lunar avoidance.

---

## Planner Logic

### Observability Cell Rules

- Each object/rig row in the Planner displays observability:
  - **Top:** Lunar occlusion icon + date range (7pt normal, start–end format).
  - **Center:** Transit time (or rising time if selected in Rig Kit).
  - **Bottom left/right:** Two longest visibility arcs for the object's 2° declination band (hh:mm), regardless of east/west orientation or meridian crossing. If only one arc, show in left, leave right blank.
  - If minimum contiguous imaging time (Rig Kit) not met, cell not painted.

- **Cell coloring:** By number of test days passed (OPC shade 30% to 5%).
- **Eligibility:** Only eligible cameras/filters shown.
- **Arcs:** Calculated from horizon polyline and zenith obstruction; stored in hidden sheet/database.

### Lunar Ephemeris & Month Matrix

- Ephemeris: 365/366 days, starting at first of current month, ending Dec 31, then Jan 1 to end of prior month (wraparound).
- Month columns: Each month is a merged pair of columns, width proportional to number of days (see Pixel-width table below).
- Dusk/dawn convention: Each month’s columns aligned to dusk/dawn of 15th (per Rig Kit dark convention).

| Month      | Days (Left+Right) | Total Pixels |
|------------|-------------------|-------------|
| January    | 31 + 30           | 62          |
| Feb (non-leap) | 28 + 27      | 56          |
| Feb (leap) | 29 + 28           | 58          |
| March      | 31 + 30           | 62          |
| April      | 30 + 29           | 60          |
| ...        | ...               | ...         |

---

## Kit Integration

- Rig Kit, Camera Kit, Filter Kit, Object Kit must have correct spacing, formatting, and eligibility connections to database.
- Data validations in Planner only present eligible items per rig.
- Any changes to horizon, zenith, lunar avoidance, or eligibility require a database refresh (marked by yellow bar).

---

## Lunar Avoidance Logic

- Lunar avoidance angle set per rig.
- For each object, calculate when Moon is within avoidance angle—dates mapped to Planner cells.
- Lunar occlusion shown as flash icon, centered on the affected day(s), with dates to left/right depending on half of month.
- Tooltip/cell note may display avoidance details.

---

## Lunar Occlusion, Zenith Obstruction, and Horizon Limits — Design Conclusions

### 1. Lunar Occlusion Calculations (Practical Approach)
- Lunar occlusion warnings are based on a user-specified lunar avoidance angle, typically 10–20° (with 20° being common).
- The Moon's position (RA/Dec) and the object's RA/Dec are used to compute true angular separation at key times (e.g., object transit, or at nightly intervals).
- Atmospheric conditions (such as high clouds) broaden the effective area influenced by the Moon, so the warning is intentionally approximate.
- The goal is to advise the user: "Avoid this night for this object," rather than provide fine-grained time estimates.

### 2. Rig-Dependence and Constraints
- Occlusion calculations are **rig-dependent**:
  - Each rig has a unique location (latitude/longitude) affecting sky coordinates and Moon/object visibility.
  - Each rig has its own horizon profile (altitude limits by azimuth), determined by its site environment (trees, buildings, terrain, etc.).
  - Each rig has its own zenith obstruction profile, determined solely by hardware (mount, tripod, imaging assembly).
  - The lunar avoidance angle is user-configurable per rig and can vary.

- **Zenith obstruction** is solely hardware-dependent and represents sky regions near the zenith that the rig cannot access due to physical or mechanical limits. It may geometrically intersect the landscape horizon (e.g., overhanging trees above the rig), but remains a distinct mask from the environmental horizon.

- **Landscape horizon** is environmental and site-specific, determined by features such as trees, buildings, and terrain, and describes the lowest altitude above the horizon that is observable.

- The planner must treat these two constraints separately and combine them to determine the actual observable sky for occlusion and eligibility calculations.

### 3. Tabulation and Approximations
- Nightly occlusion warnings are tabulated for each (rig, object, date, avoidance angle). Minute-by-minute or hour-by-hour calculations are not required.
- For each night, if the Moon is within the avoidance angle of the object during any part of the observable window, that night is flagged as “occluded” (avoid for that object).
- RA and Dec are both used to calculate true angular separation; declination-dependent scaling of RA (cos(Dec)) is incorporated for practical tabulation.
- The warning system is designed for efficiency and realistic user expectations, not absolute mathematical precision.

### 4. Implementation Notes
- The Rig Kit must store, for each rig:
  - Horizon profile (altitude by azimuth)
  - Zenith obstruction profile
  - Lunar avoidance angle
  - Geographic location
- The precomputation of lunar occlusion must use all these constraints to generate accurate lookup tables for each rig/object/date combination.

---

*This design enables the SkyPix Planner to deliver accurate, practical lunar occlusion warnings and eligibility calculations, supporting multi-rig, multi-object, multi-filter planning in real-world observing scenarios.*

---

## UI/UX Decisions

- Planner is a visual, interactive sheet with minimal clutter.
- Observability primary color (OPC) user-selected in Setup.
- All calculations are automatic; no manual edits to visibility arcs.
- Only months set in Rig Kit are shown in Planner.
- Vertical merging for cameras; horizontal expansion for filters; eligibility matrices control display.

---

## Outstanding Questions

- [Add new clarifications or unresolved design questions here.]

---

## Session Summaries

### 2025-09-17
- Uploaded full system spec and design clarifications.
- Finalized Planner observability cell logic and lunar ephemeris mapping.
- Decided to use flash icon for lunar occlusion.
- Noted need for kit tightening and fixing database connections before final Planner integration.

---

*Update this file after each session for a living history of your project!*