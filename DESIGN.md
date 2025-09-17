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