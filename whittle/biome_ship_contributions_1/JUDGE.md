# Blind judge: BIOME_SHIP_CONTRIBUTIONS_1 (round 3)

Judge: fresh blind judge, 2026-11-11. Read STATEMENT.md, NOTES.md, the item file (`infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md`: owner words, spec, verify, criteria) and `evidence/`. Did not read DONE.md, BROADEN.md or the earlier JUDGE.md.

## What I checked myself

- Reran `python3 src/RimMandrake/Utils/ship_contributions.py` in this clone: exit 0, `24/24 biomes PASS or EXEMPT; 0 problem(s)`, the same rows as `evidence/ship_contributions_run.txt`. Output kept at `D:\ClaudeWork\rimmandrake\scratch\judge_bsc\run.txt`.
- Selftest evidence: the real list passes, 12 mutated lists each fail. The checker can see a failure, so its pass means something.
- Read defs by hand: `RM_SummGreatBone` (PlaceWorker_OnSubstructure; the BroodLair comp names it as `greatBoneDef`), `RM_PatternHull` (Wall parent, Odyssey category, Substructure affordance, vanilla CompSelfhealHitpoints at 500 ticks/HP with tickerType Rare: 120 HP a day as claimed), `RM_FurnaceHideBank` (unpowered CompHeatPusher of 6/s, capped at 21 C; its cost item `RM_FurnaceHide` is the Pyrelands furnace beast's leatherDef). The cost materials exist and can be obtained in game (`RM_LivePatternMetal` is in the deep-drill table and drops from hull bolts).
- `effective_def_lint.txt`: VERDICT PASS. The only warnings are unrelated (orphan .cs files, setting-gate patches with no xpath). `lints.txt`: the four mods with new defs show 0 ERROR.
- Art (I opened the images): pattern hull and spunstone hull ring/L/straight renders link cleanly with no broken corners. Tellurox hexplate 2x2 shows no visible seam. Fossil case and furnace-hide bank read clearly at in-game size. The five new textures are good enough to ship.
- The 14 art-owed gifts' texPaths: `RM_WindVaporator` uses vanilla `MoisturePump`, `RM_WasteCaskBay` uses vanilla `Shelf`, `RM_AerosolScreen` uses `RM_OldLineTurret_Base`, `RM_HullLinerRig` uses `RM_LiquidTap`, `RM_SunSphere` uses `RM_GlowTank`, `RM_TractionLance` uses the Webwork anchor, and so on. The item file admits all 14.

## Statement line

> Every-biome pass ... is done as `infrastructure/state/items/BIOME_SHIP_CONTRIBUTIONS_1.md` says, shown by fresh evidence.

**false.**

What holds: the `## verify` section ("every shipped biome mod has at least one ship-buildable contribution ... the list matches what the mods actually ship") is shown. Every one of the 24 composed biomes has a row, each def named exists and can be placed on a deck, the checker was rerun fresh, and it is not toothless. The matrix is carded to the owner (`evidence/owner_card.md`).

What fails:
1. **The criterion is not met as it stands.** The criterion reads: "the gravship becomes a scrapbook of everywhere it has been." 14 of the gifts (8 borrowed textures, 6 declared placeholders) look like other things on a deck. The Leaning Scrub gift is drawn as a vanilla moisture pump, and the Wastes gift as a vanilla shelf. The item file says so itself: "until it lands the scrapbook shows in what the gifts do, not yet in how they look". The follow-up item `RIMMANDRAKE_PAINT_SHIP_GIFTS_OWN_ART` is the thing that would finish this. Filing that debt does not finish the scrapbook. I would have to caveat this line, so the line is false.
2. **"Balance the set so every biome's gift is distinct" is only partly done.** Four rows give water: Leaning Scrub vaporator, Weeping Stones condenser, the Stillsand solar still, and Blue Desert's ice as water stock. Three rows give light that needs no lamp: lanternstone, Sump gaslight lamps, the sun-sphere. The rows try to tell them apart in words, but in play these overlap. The heater overlap was fixed; these were not.
3. **"Worth landing for" is not shown for most rows.** 20 of 24 rows are *delegated* agent picks. The owner card is unanswered. Several new numbers are marked PROVISIONAL in the defs (for example, the furnace-hide bank gives a third of a heater's output). No evidence weighs a gift's value against its cost or the trip.

## Staged or flattering evidence

- No gift was seen placed, used or carried in a running game (the README says so). All proof of "can stand on a deck" comes from the checker reading the engine rules, not from the engine. The five art renders are wallsims and tiles on a flat field, not on a real deck next to vanilla hull, so they are a best case.
- The checker's PASS proves that a def exists and that its placement rules allow a deck. It does not check that the effect a row describes works (summ imprinting, drive-core range, archive-vat resurrection, aerosol dome). Those effects are claimed in the row text and only partly backed by the C# I saw referenced.

## What would settle it

The `RIMMANDRAKE_PAINT_SHIP_GIFTS_OWN_ART` art landed for all 14, or an owner ruling that the scrapbook may ship with stand-in art. Either the overlapping water and light rows cut down or ruled acceptable. An owner answer on the card. A live look at one deck carrying several gifts.

would show: no
