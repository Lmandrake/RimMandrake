# THE_SCALD_LOST_ITS_WATER_1 — a ruled sea stopped counting as water

## spec

🔴 **OWNER, 2026-08-21: "Chase it before anything else builds on this world."** He also
ruled the same session that `WORLDMAP_gen` is **the first-draft v1 keeper**, so this is a
defect in a world that is meant to ship.

**The arithmetic, and it is what makes this worth chasing rather than shrugging at.**
From `w9_run_2026-08-21_0143.md`:

| | |
|---|---|
| water measured after the repaint | **6.71%** of 21,872 tiles = **1,468** tiles |
| the three ruled seas, per canon | The Twilight Sea 851 + The Gray Sea 617 + **The Scald 312** = **1,780** |
| shortfall | **312 tiles — The Scald exactly** |
| lint, same run | **`lakesAboveSeaLevel: 312`** — the same number again |

Two independent numbers landing on 312 is not coincidence. ⇒ **The Scald is very likely
present as a lake sitting above sea level, and is not registering as a body of water.**

⚠️ **Before the repaint, water was 35.86% and lint reported 3,508 `landBiomeSubmerged`.**
After, 6.71% and 86 findings. The repaint fixed far more than it broke — do not treat this
as a reason to undo it. But it is the run that changed The Scald's status, and that is
where to look.

🔑 **Canon is explicit that The Scald being `Lake` is DELIBERATE, so "it is a lake" is not
the defect.** `canon.yml:129` — *"The Scald is painted `Lake`, NOT `Ocean` — all 312 of its
tiles. The other two seas are `Ocean`."* The owner confirmed `Lake` stays on 2026-08-20,
because cutting the def deletes a named sea. **The question is its ELEVATION and whether
the engine counts it as water, not its biome.**

**Two outcomes, and they need different fixes — decide which before touching anything:**
1. **The repaint lifted it above sea level.** Then the map is wrong and the elevation of
   those 312 tiles is the fix.
2. **The lint rule does not know a ruled sea can legitimately sit high.** A scald is a
   salt-crusted flat; a highland salt sea is plausible worldbuilding. Then the map is
   right and the RULE learns about it — and `stats` should still count it as water.

⛔ **Do not "fix" this by repainting The Scald to `Ocean`.** That reverses a standing owner
ruling and deletes the distinction between the three seas.

## verify

- Read the actual elevation of the 312 Scald tiles off the live world and state it as a
  number against sea level. That single measurement decides which outcome above applies.
- Confirm the 312 in `lakesAboveSeaLevel` are the same 312 tiles canon calls The Scald —
  compare tile IDs, do not match on the count alone.
- Recompute water% counting The Scald; it should reach ~8.14% if the three seas are all
  wet.
- 🔭 **Look at it.** Render the region and compare against
  `world/view/ASHKARR_WORLDMAP.biome.equirect.png` and the 01:43 bridge screenshot. Per
  `CLAUDE.md`, every defect that has mattered in this work passed its numeric check while
  the picture was wrong.

## criteria

A number for The Scald's elevation, a stated verdict on which of the two outcomes it is,
and — if it is outcome 1 — 312 tiles that are wet again without any of them becoming
`Ocean`.
