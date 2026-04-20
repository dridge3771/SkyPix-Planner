## Section 302 — SkyPix Global Color Vocabulary (LOCKED 2026-04-19)

---

### 302.1 — Complete Color Canon

All SkyPix UI colors across all modules. Canonical reference —
use these constants, never hardcode hex values in module code.

```python
# skypix_colors.py — import from here in all modules
YELLOW        = "#ffff00"   # save-gated required fields
ORANGE        = "#ffaa00"   # optional / stale / environment
RED_EXCL      = "#cc0000"   # filter exclusion
GREEN         = "#22c55e"   # Selector green — SC column, active selection
GREEN_DK      = "#16a34a"   # Command green — nav tabs complete, commit actions
```

---

### 302.2 — Color Semantics

| Constant | Hex | Used for |
|---|---|---|
| YELLOW | `#ffff00` | Save-gated required fields — must be filled before Save |
| ORANGE | `#ffaa00` | Optional fields, stale data, environment parameters |
| RED_EXCL | `#cc0000` | Filter exclusion indicators |
| GREEN | `#22c55e` | **Selector green** — SC column, active selection states, toggle active arrow shaft |
| GREEN_DK | `#16a34a` | **Command green** — nav tabs completed, toggle arrowhead, commit/go actions |

---

### 302.3 — Green Vocabulary Derivation

  GREEN    (#22c55e) = Selector green
    The active arrow shaft. Bright, attention-catching.
    Meaning: "I am looking at / have selected this."
    Lightweight and reversible — a pointing gesture.

  GREEN_DK (#16a34a) = Command green
    The active arrowhead. Darker, directional, authoritative.
    Meaning: "I am doing this / this module is armed and ready."
    Used for completed nav tabs (the module is ready to use),
    commit/assign actions, and the toggle arrowhead (direction of travel).

The toggle icon teaches both colors simultaneously on first use.
The shaft (Selector) points to the current panel.
The arrowhead (Command) indicates the direction of travel.

---

### 302.4 — Usage Rules

**GREEN (#22c55e) — Selector green:**
  - SC column cell when object is selected
  - Active/selected state in any list or table (row highlight)
  - Toggle active arrow shaft
  - Any "I am looking at this" signal — lightweight, reversible

**GREEN_DK (#16a34a) — Command green:**
  - Nav tabs when module step is completed (armed and ready)
  - Toggle active arrowhead (direction of travel)
  - Commit / assign action buttons
  - Any "I am doing this" signal — authoritative, directional

**Forbidden combinations:**
  - Never use GREEN or GREEN_DK for required field gating (YELLOW only)
  - Never use GREEN for filter exclusion (RED_EXCL only)
  - Never use ORANGE for selection states (GREEN/GREEN_DK only)

---

### 302.5 — Onboarding Tab Progression Colors

| State | Color | Hex |
|---|---|---|
| Current step (flashing) | YELLOW | `#ffff00` |
| Locked / not yet available | Grey | `#e0e0e0` |
| Completed step | GREEN_DK (Command) | `#16a34a` |

The Config tab flashes YELLOW on first run. Each completed step
turns GREEN and the next step turns YELLOW. See Section 303
(Onboarding Progression) for full tab state machine.

---

*Section 302 locked 2026-04-19.*
*All modules must import color constants — no hardcoded hex.*
