# v1 gravship: adding the three missing parts will NOT make it fly

**OPS, 2026-08-13. Quicktest map, paused. Campaign untouched.**
Observed live on the ship BRIDGE built and exported at x 82..167, z 58..190.

## The finding

**The hull is 6.4× over the engine's substructure capacity.**

| | |
|---|---|
| in-game engine panel | `Connected substructure: **4057 / 633**` (rendered red) |
| `jawa/get_def GravEngine` | `SubstructureSupport: **632.7954**`, `GravshipRange: **0.0**` |
| hull as built | **4,057** substructure cells — matches the plan exactly |
| shortfall | 4057 / 632.8 = **6.41 engines' worth of capacity, against one engine** |

Screenshot: `observed/evidence/2026-08-13_gravship_over_capacity.png` — the red
`4057/633` overlay sits on the hull, with the engine's inspect panel open.

## Why this is worth raising separately from BRIDGE's note

`ecffe1b` records *"it cannot fly"* and attributes it to the deck plan shipping
**no thruster, fuel tank or controls** — the engine panel does say
`Requires: Thruster, fuel tank, controls`. That is true and it is not the whole
story.

🔴 **A reader of that note would reasonably conclude "add three parts and it
flies." It will not.** Those three parts satisfy a *completeness* check.
`4057 / 633` is a *capacity* check, and it fails independently. Both must pass.

## The distinction that caused this — reach is not capacity

`NEXT_RELOAD.md` builds the design on the owner's four Bigger Gravships settings
(`gravEngineMaxDistance` 34, `gravExtenderMaxDistance` 30, `gravExtenderMax` 12,
`gravExtenderMaxDistanceFromEngine` 85) and reasons entirely about **reach** —
"the hull needs a reach of 74.46; defaults give 51.80".

**Those settings govern how FAR the grav field extends. They do not govern how
MUCH substructure one engine can support.** Capacity is a flat per-engine stat,
`SubstructureSupport 632.7954`, and no distance setting moves it.

⚠️ `NEXT_RELOAD.md` already contains the number that proves this and reads it as a
puzzle rather than an answer: *"`get_def GravEngine` exposes no radius — only
`SubstructureSupport 632.7954`, which matches neither π·34² nor π·25.9²."*
**It matches neither because it is not an area at all.** It is a budget.

## What follows — costed, not decided

1. **~7 engines** (4057 / 632.8 = 6.41, so 7) if capacity is additive across
   engines. ⚠️ **I have NOT verified that it is additive**, and it is the load-
   bearing assumption of this option. Verify before designing on it.
2. **Shrink the hull to ≤ 633 cells** — an 86×133 footprint becomes roughly
   25×25. That is a different ship, not a tuned one.
3. **Ship it stationary**, which is what `ecffe1b` already proposes and what v1
   scope permits — flight is explicitly not in the v1 bar.

**Option 3 costs nothing and is already the plan.** Raising this only so that
nobody spends a load adding a thruster and expecting lift-off.

⚠️ **`GravshipRange: 0.0` on the engine def is unexplained** and I did not chase
it. It may be a base value that comps fill at runtime. Do not read it as "range
is broken" without checking.

## Not verified

Whether `GravFieldExtender` adds substructure capacity. `jawa/get_def` returned
**no** substructure-, support- or distance-named statBases for it, which is
suggestive but not proof — extenders may carry their effect in a comp rather than
a statBase, and `get_def` showed no comps for it either.
