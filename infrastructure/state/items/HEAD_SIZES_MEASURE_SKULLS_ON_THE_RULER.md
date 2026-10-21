
## what (FOUNDRY, 2026-10-20)

`47a707a35` made, offline only (nothing deployed):
- `RSW_BodySizeGene_*` real size again (`SM_BodySizeOffset`), owned by `gen_races_mod.SIZE_GENES_REAL` so a regeneration
  cannot revert it (`src/RimMandrake/Utils/selftest_size_genes_real.py`). After `BodySizeIsReal.xml`'s swaps only eight
  xenotypes still carry one: Nelvaanian `_big` (1.0 -> 1.20 real), Bothan, Defel, Gand, GeonosianVariants, Selkath,
  Snivvian, Sullustan `_small` (1.0 -> 0.80 real, metabolism +3). Sprites do not move (B&S renders mech + cosmetic).
- Head size in the def (owner by card 2026-10-20: "How should head sizes be set?" -> "Tune in the def"):
  `SM_HeadSize_Cosmetic` 0.88 on `RSW_LasatHead` (head rule x1.369 -> on screen 1.20 human skulls) and 0.95 on
  `RSW_NelvaanianHead` (x1.107 -> 1.05). Mimbanese, Ortolan 1.00. Records: `src/RimMandrake/Utils/art/head_envelope.json`
  `species_render`; recomputed from the defs by `src/RimMandrake/Utils/art/selftest_head_scale_from_defs.py`.

## to prove in game
1. Deploy `StarWarsRaces` and `StarWarsPatches` (`deploy_custom_mods.py --mod <name>`, read the plan, then `--apply`).
2. Line up a human, Lasat, Nelvaanian, Mimbanese, Ortolan (bare and hatted), screenshot, and re-measure the skull scale
   with `D:\ClaudeWork\rimmandrake\scratch\headscale\match.py`: expect Lasat ~1.20, Nelvaanian ~1.05, others 1.00, and
   hats shrinking with the head. Then write `measured_live` (and `measured_with_head_mult`) into `head_envelope.json`.
3. State read: a Nelvaanian's `BodySize` stat 1.20 and a Bothan's 0.80 (mechanical, not only sprite).

NEXT: deploy StarWarsRaces + StarWarsPatches at the next game-down window, then line up the four species beside a human and measure on-screen skull heights.
