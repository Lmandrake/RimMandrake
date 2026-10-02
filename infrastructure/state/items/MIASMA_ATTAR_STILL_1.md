# MIASMA_ATTAR_STILL_1 — the attar: the beauty oil refined from delta silt, its glaze and its balm

**Free tier**, `mandrake.rm.miasma`. Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 ruled-unbuilt 1, §4 row 0c. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 1, *Build first*): land everything the card's first option listed, plus the giant's choice in the same batch.

## The ruling being executed
Sheet §7, *"owner's pick, replacing the cut medicine"*: *"an expensive oil that restores beauty… Artists use it as a glaze… the vain
use it as a balm"*. Delta silt and delta salt are harvested (`src/RimMandrake/Miasma/Defs/ThingDefs_Items/RM_Miasma_Goods.xml`, no
recipe, no use); the silt's description already promises the attar. No attar def, recipe or still exists (searched).

## spec
1. `RM_Attar` (a luxury item, high market value) and a still that refines delta silt with delta salt as the second input (the sheet:
   delta salt is *"the one the stills need most"*).
2. **Glaze:** applied to a finished artwork, raises its beauty. **Balm:** fades a scar (a cosmetic; it heals nothing: ban 3, no
   medicine economy).
3. Art from the turn-1 CSV.

## criteria
- Recipe resolves; a glazed sculpture's Beauty rises; a balmed pawn's scar fades and no injury heals.
