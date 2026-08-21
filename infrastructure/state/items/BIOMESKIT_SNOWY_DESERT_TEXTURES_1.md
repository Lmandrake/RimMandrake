# BIOMESKIT_SNOWY_DESERT_TEXTURES_1 — new texture failures in the session that went unstable

## spec

The game became unstable and was brought down at 03:14. `Player.log` is harvested to
`infrastructure/state/observed/logs/Player.2026-08-21_0315_unstable.log` (9,557 lines)
before the next launch destroys it, along with `Player-prev`.

🔑 **The finding is a DIFFERENCE, which is what makes it worth chasing:**

| log | `Could not load Texture2D` |
|---|---|
| `Player.2026-08-20_1754_session.log` (18,563 lines, yesterday) | **0** |
| `Player.2026-08-21_0315_unstable.log` (9,557 lines, tonight) | **148** |

All 148 name BiomesKit world materials for **ExtremeDesert Hills in SNOWY variants**:
`WorldMaterials/BiomesKit/ExtremeDesert/Hills/Mountains_FullySnowy`,
`.../Impassable_FullySnowy`, `.../Impassable_VerySnowy`. They are the last errors in the
log before the Unity memory dump that ends it.

**Tonight is the session in which the planet was repainted** — w9 stages 1–6 applied at
01:43, 21,872 tiles rewritten. ⇒ The correlation is strong and the direction is obvious.

⚠️ **BUT THIS IS A HYPOTHESIS, NOT A CAUSE, AND MUST NOT BE REPORTED AS ONE.** 148 log
lines is not by itself an instability. The allocator statistics in the tail are Unity's
ordinary bucket accounting, not evidence of a leak — REP nearly read them as one. What
would make this the cause is a texture lookup failing **inside the world-render loop, every
frame** — the same shape as the missing `settlementTexturePath` that took TPS to 3.7 on
2026-08-20. Establish that it repeats per frame before believing it.

**What the offline data says, and it does not fit yet:**
`world/ASHKARR_WORLDMAP_tiles.csv` has 3,581 `ExtremeDesert` tiles, of which **345 are
hilliness 4 (Mountains) and ZERO are hilliness 5 (Impassable)**. All 345 measure
**22.9 °C to 63.8 °C — none below freezing.** So by the CSV, nothing should ever ask for a
snowy desert mountain. Either the LIVE world diverges from the CSV, or BiomesKit requests
every (hilliness × snow) permutation for a biome it sees at all. **Which of those it is
decides whether this is cosmetic spam or a real paint defect.**

🔑 **Check it against the other elevation-smelling symptom before treating them separately.**
`THE_SCALD_LOST_ITS_WATER_1` reports `lakesAboveSeaLevel: 312`. Snow and lakes-above-sea-level
are both things that follow from ELEVATION, and the same run produced both. The planet does
carry genuinely cold ground — 8,911 tiles below 0 °C, min −80.8 °C, which is the night side
of a tidally locked world and is correct — so cold is not itself the anomaly. Cold *desert
mountains on the day side* would be.

## verify

- Establish whether the 148 are per-frame or one-shot at world load. This is the question.
- Read the LIVE world's biome × hilliness for the tiles BiomesKit is complaining about and
  compare against the CSV's 345/0 split. Name any divergence.
- Confirm whether the same errors appear on a load of the world WITHOUT the repaint
  (`world/WORLDMAP_source.rws`), which separates "our paint did this" from "BiomesKit
  always does this".
- Say plainly whether this explains the instability or does not. ⛔ "Probably related" is
  not an answer; the log is on disk and the question is settleable.

## criteria

Either a named mechanism for tonight's instability, or a clear statement that these 148
lines are noise and the cause is still unknown.
