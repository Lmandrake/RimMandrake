
## finding (FOUNDRY, 2026-10-20; source-derived, offline - no live read)

**Owner instruction (verbatim, 2026-08-22, as quoted in commit `1c3a673fe` and in the header of `src/RimStarWars/StarWarsPatches/Patches/BodySizeIsReal.xml`; the original transcript line was not found):**
*"I'd like it to affect carrying capacity, food, melee, etc. just as you say. Let's use this stuff right."*
Earlier same day, same file: *"Err on the side of greater size differentials than reduced size differential. We want great storytelling. Big aliens should feel big, small ones small."* Context: `infrastructure/state/evidence/big_weapon_xenotype_audit_2026-08-22.md` L205-215 (all 70 races mechanically bodySize 1.0).

**What happened.** `1c3a673fe` (2026-08-22) rewrote `RSW_BodySizeGene_big/bigger/biggest/small/smaller` from `SM_Cosmetic_BodySizeOffset` to `SM_BodySizeOffset` (+0.2/+0.5/+0.7/-0.2/-0.5), metabolism `_small` +3, `_smaller` +5. `7707a6aca` (2026-08-23, "Adopt the 59 new race defs") regenerated `SW_Genes.xml` and put all five back to `SM_Cosmetic_BodySizeOffset`, and added `_smallest` (-0.7, cosmetic). The BodySizeIsReal.xml header still says "now mechanical". Nobody noticed: the regen was not a decision.

**Current behaviour.** Patch `BodySizeIsReal.xml` is intact and swaps species to B&S frames (e.g. Lasat `_bigger` -> `HalfJotunFrame` +0.75, REAL: body scale 1.48 and real mass/HP/carry/food/melee/raid wealth). The five own genes remain cosmetic: sprite only, mechanical size 1.0. Uses in `RimMandrakeXenotypes.xml`: big x14 (incl. Nelvaanian), bigger x4, biggest x1, small x7, smaller x5, smallest x0. Not checked live (Player.log / def dump); offline source only.

**Consequence.** Lasat: real giant (HalfJotun; also +1500 raid wealth, metabolism -3, 1.5x mining) - matches intent. Nelvaanian (`_big`): looks 1.14 but is mechanically a 1.0 human; intent was 1.20 real (patch header: "NELVAANIAN IS NOW 1.20"). Same for 13 other `_big` species, all `_small`/`_smaller` species (Bothan etc. look small, fight/eat/carry as 1.0).

**Intent is clear (real).** Proposed patch (not applied): in `src/RimStarWars/StarWarsRaces/Defs/GeneDefs/SW_Genes.xml` change the five `SM_Cosmetic_BodySizeOffset` -> `SM_BodySizeOffset` (same values), restore metabolism `_small` +3 / `_smaller` +5 (check `biostatMet` and the metabolism statOffset against `1c3a673fe`), re-run `validate_patch.py`; decide `_smallest` (unused; -0.7 -> 0.30, below the 0.40 floor of the ladder, leave cosmetic or retire). Max stays 1.70 (<1.99 giant-weapon threshold). Costs: raid wealth/difficulty moves for ~40 species-colonies; head scale in `design/RimStarWars/head_envelope_2026-10-20.md` unaffected (it already reads both stats).
Add a selftest asserting no `RSW_BodySizeGene_*` carries `SM_Cosmetic_BodySizeOffset` so regen cannot revert it again.

NEXT: apply the five-stat change in SW_Genes.xml per the finding, validate, add the selftest, deploy at the next load (owner already ruled; no card needed).
