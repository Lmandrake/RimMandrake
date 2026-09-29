## Scope
Follow-on to CONTAGION_RULED_CONTENT_1 Wave A (closed the 15-creature donor
port). This is cast bible §4's **flora ports** (Part 3 of the original
item's scope), quoted verbatim from
`design/Jawa/worldbuilding/biomes/contagion_grotesque_cast_2026-09-27.md`:

> **Flora ports**: Eyebark, Lashgrass, Bleedleaf, Gorestalk, Rattlegrope,
> Sapblister, Bloody Fist, Halfmade Tree + Blighted variant.

Read the cast bible §4 in full — it gives the donor def, ruled commonality
and a one-line sketch (plant class, yield, growDays) for every row.

## Watch out
- All in one new file, `src/RimMandrake/Contagion/Defs/PlantDefs/
  RM_ContagionFlora.xml` (per the bible's §8 wiring summary).
- None edible, none foragable (ban 4) — the biome def's `forageability` stays
  0.0; do not add a foraged-food def to any of these.
- Shorthand element form only in `<wildPlants>` — `<li>` silently discards.
- Halfmade Tree (`RM_HalfmadeTree`) folds in a NAMED ART REDO owed since
  the_contagion.md's own Owed section: "half PLANT, alien on BOTH halves —
  one half an alien plant being overwritten by a different alien wrongness,
  never a half oak, no Earth-tree read anywhere on it." Check
  infrastructure/artpipe/{done,_artsrc,registry.jsonl} under the NEW name
  before assuming this needs queuing — Wave A found 14 of 16 fauna already
  regenerated under new names without being asked; the same daemon may have
  already done Halfmade Tree too.
- This wave's `RM_Contagion.xml` <wildPlants> is UNTOUCHED (still the donor
  AB_* rows) — this item is what replaces it. Donor AB_ rows come OUT in the
  same change these RM_ rows land in, same "no patches" rule as Wave A.
- Sapblister and Bloody Fist yield ITEMS (sap, seed-fist fertilizer), never
  food — same ban-4 shape as Wave A's Scorchpod/Sloshbelly.

## Verify
- validate_patch.py --defs 0 errors.
- Donor AB_ rows absent from RM_Contagion's wildPlants, all 9 RM_ rows
  present at ruled commonality (measured off the deployed file, same method
  Wave A used — read it live, don't assume the repo copy alone proves
  deployment).
