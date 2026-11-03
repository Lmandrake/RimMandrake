# Extra-art commission per biome (`EXTRA_ART_PER_BIOME_COMMISSION_1`, 2026-11-03)

The owner, 2026-10-08 (typed): gender art, *"I'm happy with every herd animal"*; *"After that we should commission this
answer for each biome once it's done. Same for juveniles."* By question card the same day (18:44): *to break up a herd
of identical-looking animals, a COLOUR VARIANT comes first (not a female look).* Female flight frames: *"Only if the
females and males are very different looking."*

Every biome's group sizes are settled (`BIOME_GROUP_SIZE_WALK_1`, done 2026-11-03) and so is canon herd status
(`design/RimStarWars/canon_herd_lore/canon_herd_rulings.md`), so every biome is commissioned. The guidelines are the
2026-10-08 draft (`Transient/extra_art_guidelines_2026-10-08.md` at git `d92775a94`; the Transient copy expired).

## What each creature gets

| rule | look | when |
|---|---|---|
| HERD | colour variant | a herd in this biome (herdAnimal, or canon `herd`; walked max group above 1; not canon `solitary`) with no female look and no `alternateGraphics` variant yet |
| HERD | female (+ female pack set for a pack beast) | the same, when canon says the sexes look different (read by hand: kybuck, Iridonian reek) |
| YOUNG | young | canon says the young look different (mott, uvak, woolamander, clodhopper, neebray), or a pack / easily-tamed animal of body size 0.4 or more, young for 15 days or more; never when a distinct young texture or a separate young race exists |

A creature on several biomes is commissioned once, in the first biome that owes it. Biomes go smallest first; job
priority is 50 + the biome's order, so the artpipe daemon draws the art one biome at a time.

## Files

- `commission.csv`: one row per look: biome, order, race, kind, rule, look, slot, the new texture path, the reference
  sprite, canvas, facings, job count, the evidence, the artpipe job id.
- `commission_state.json`: the biomes filed, when, and their job ids.

## Tools

    python3 src/RimMandrake/Utils/art/extra_art_commission.py plan | check | submit --next | submit --biome RM_X

`src/RimMandrake/Utils/art/selftest_extra_art_commission.py` proves the table matches the defs and the walk, and that
every filed job is on the artpipe queue. The eligibility gate (`regen_eligibility.py`) reads `commission.csv`: a
commissioned new slot counts as drawn by its def, and must still be confirmed NONE.

## Known limits

- A variant of a flyer flies in the base colours: flight frames are per kind, not per variant.
- The new textures are not drawn by any def until they land. Wiring them (`femaleGraphicData`, `alternateGraphics`,
  the young life stages' `bodyGraphicData`) once all facings exist is the follow-on item.
