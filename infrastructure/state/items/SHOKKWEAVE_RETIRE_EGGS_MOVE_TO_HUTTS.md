# SHOKKWEAVE_RETIRE_EGGS_MOVE_TO_HUTTS

Owner, Biome card 5 by question card, 2026-10-22 (`design/RimMandrake/biome_owner_cards_2026-10-22.md`): port the Hutt
Cartel egg black market and the Wildsteam weaver caravan into the Webwork's campaign patch layer, then cut
`mandrake.rut.shokkweaveeconomy`.

## spec
- Ported into `src/RimUtinni/UtinniPatches/` (mandrake.rut.patches), defNames and numbers unchanged:
  `Defs/TraderKindDefs/RUT_HuttCartel_EggMarket.xml`, `Defs/TraderKindDefs/RUT_Wildsteam_Caravan.xml`,
  `Patches/RUT_Webwork_EggBlackMarket.xml`, `Patches/RUT_Webwork_RareThrixweaveStock.xml`, and the stock generator
  `Source/RUT_StockGenerator_RareThrixweave.cs` (was `StockGenerator_RareShokkweave`).
- Dropped with the mod: the "shokkweave" relabel of Hyperweave (the Webwork's "thrixweave" is now the only one;
  `lint_webwork_defs.py` errors on a second), and the `RUT_Webwork` silk-knot/nest scatter.
- Cut: the mod folder, the six current mod lists (FULL.LATEST and the five RULED profiles), the `acc_green_min` tier,
  the settings-screen and required-checks rows, the mod archive row (RETIRED-MERGED). `SHOKKWEAVE_ECONOMY_FIRST_SCRIPT_1`
  is dropped with it.
- Saves: no save holds a Thing of any cut def (0 `<def>` hits over 403 saves in the Saves folder plus `world/`). 58
  test/review saves name `RUT_Webwork_SilkKnot`, and one names `RUT_Webwork_Nest`, inside `<li>` filter lists. That is
  one dead-reference log line on load. Saves were not edited.

## verify
Offline: `python3 src/RimUtinni/UtinniPatches/selftest_webwork_egg_market.py` (applies both patches to the real defs;
fails on a changed number), `python3 src/RimMandrake/Utils/lint_webwork_defs.py`. Live: UtinniPatches validation chain
`webwork_egg_market` on a list carrying mandrake.rut.patches and mandrake.rm.biomes.

## criteria
- A1 L0: selftest_webwork_egg_market PASS; lint_webwork_defs 0 ERROR; validate_patch 0 errors on both patch files.
- A2 L1: deploy: `deploy_custom_mods.py --mod UtinniPatches --apply`, the composed biomes mod redeployed with the Webwork DLL,
  and the game copy `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\ShokkweaveEconomy` removed. Otherwise
  the old copy ships duplicate TraderKindDefs if anything re-lists it.
- A3 L2: live: `webwork_egg_market/egg_market_defs_live_as_patched` PASS. The egg's tradeability reads All, both factions
  list their new caravan kinds, and both kinds carry RUT_StockGenerator_RareThrixweave.
- A4 L2: live: a forced Hutt egg-broker caravan arrives and stocks 1-3 RM_OllathrixEgg; Hyperweave reads "thrixweave".
