# Ash'karr adversarial audit and six-pass edit — 2026-08-26, seat CHECK

Driven live through the bridge against the running game. **Nothing here is regenerable:**
`BEFORE_*` is the only copy of the planet as it stood before the edit.

## Restore

`BEFORE_mutators.json` / `BEFORE_landmarks.json` / `BEFORE_links.json` / `BEFORE_tiles.csv`
are a complete pre-edit record. `AFTER_*.csv` is the post-edit bundle in `worldview.py`
form (render it with `python3 src/RimMandrake/Utils/worldview.py world/audit_2026-08-26/AFTER`).

## What was written

`ops.json` is the exact edit list; `apply_log.txt` is what the game reported back.

| pass | what |
|---|---|
| A-solar | `VEE_MoreSolarPower` on 4,362 tiles at arc <= 55, `VEE_LessSolarPower` on 3,900 at arc >= 125. The terminator belt is deliberately unmarked. |
| B-water | 22 dead channels traced downhill out of the named ranges: `VEE_DryRiver` -> `VEE_SaltPlains`, plus relict deltas on the Grey Sea shore and alluvial fans on the Twilight Sea. |
| C-roads | 147 dead-straight road segments re-routed A-t-B -> A-x-y-B. `AncientAsphaltHighway` untouched on purpose. |
| D-cluster | 18 landmark families grown around anchors instead of lone pins. |
| E-regions | Sinkground, Fanground, Salt Gate, Lantern Deeps, Sporefields filled. Lantern Deeps' 7 core tiles raised to Mountainous so a `Cavern` can legally exist there. |
| F-tatooine | `WildTattooinePlants` on 1,400 dayside tiles; 5 sarlacc pits and 3 dead ones, all off-road. |

## Three things measured here that the docs did not say

1. **`world_landmarks_set`'s `isValidTile` is evaluated AFTER the add**, so it reports the
   landmark it just placed. It is not a gate and not a usable pre-check — `added >= 1` plus
   a read-back showing the def is the only honest success signal.
2. **The landmark is `Ruins`; the mutator is `AncientRuins`.** Nine placements failed on the
   assumption that one name served both.
3. **Landmark `mutatorChances` rolls bypass any category guard you apply to your own writes.**
   Seven same-category mutators were displaced this way; six were correct specialisations
   (`Cavern`/`SerpentineCanyons`/`Cenotes` replacing a generic `Mountain`), one was a real
   defect — a `VEE_DryRiver` landmark landed on a live river tile (863) and displaced `River`.
   Repaired. Diff whole-planet LOSSES after any landmark pass, not just your intended gains.
