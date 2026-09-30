# FORGE_RULED_CONTENT_1 report

Mod: `src/RimMandrake/TheForge/`. No C#, no deploy, no game or bridge, no ledger writes.

## Rulings, and what landed

1. **"Wire in all waiting."** (turn 2)
   - `AA_ColossalAerofleet` 0.5 inline on `RM_TheForge` (MayRequire `sarg.alphaanimals`).
   - `Tibidee` 0.5 in `UtinniPatches/Patches/WildAnimals_TheForge.xml`. It is canon, so it goes through the patch layer. No `RSW_` port exists, so the donor defName is used with MayRequire `mlie.starwarsanimalcollection`.
   - Fleet flier art: 3 facings copied from the artpipe renders `rutfleetflier_v1_*` into `Textures/Things/Pawn/Animal/RM_FleetFlier/`. The def header no longer claims it has no art.
   - `RUT_Plant_FlashFlora` is now the thingClass on `RM_FireLavender`, `RM_HeatsinkFungus` and `RM_CinderCrust`.
   - The three DEPLOY_HOLD art debts have no art anywhere, so they are BLOCKED (see below).
2. **Four natives admitted** (turn 4): `RM_Dhokkur`, `RM_Julmox`, `RM_Jossur`, `RM_Dhuvvox` are in `Defs/ThingDefs_Races/RM_TheForgeNatives.xml`. Each has a ThingDef and a PawnKindDef, cast-bible descriptions, and art. All four are wired inline at 0.02 / 0.4 / 0.06 / 0.3.
   - The dhokkur butchers to `RM_DhokkurHide`, a new leather with high heat armour. It uses foodType None because it drinks rain.
   - The jossur has real 1.6 flight (`MaxFlightTime` 20, `FlightCooldown` 6, Locust race flags) plus the shipped `CompProperties_VaporDrifter`. It has no flip-book frames.
3. **Floatstone** (turn 7): `RM_Floatstone` is a StoneBlocksBase stuff. Mass is 0.1, the MaxHitPoints factor is 2.2, flammability is 0, MarketValue is 8, and Beauty is high. Its colour is pearl-cream on the vanilla wall tint. `RM_FloatstoneGarden` is a harvestable plant yielding 35 floatstone, and nothing else produces the stone. The garden is deliberately left out of wildPlants, because the freeze-phase spawn cycle belongs to the mechanics ticket.
4. **Struck items were not built.** `RM_ArmorRating_Scald` is still granted by nothing, on purpose.

## Already built (found in src)
- `RUT_Plant_FlashFlora`, `RM_MapComponent_FlashCycle`, `CompProperties_VaporDrifter` (EnvironmentalHazards), all reused unchanged.

## Deferred C# follow-ons
All of these are owed to FORGE_CYCLE_MECHANICS_1, and stub comments sit in the defs.
- Dhokkur dormancy keyed to boiling rain. The dormant sprite ships unreferenced at `Textures/Things/Pawn/Animal/RM_DhokkurDormant/`.
- Dhuvvox burst-window eruption and reseal. The nodule sprite ships unreferenced. Its baseline wildAnimals row stands in until then.
- Julmox sealed state and flash-window grazing.
- Floatstone garden freeze-phase spawn, ripening, and drift-off.
- Mod Settings toggles for the new features.
- Proposed separate items: `JOSSUR_FLIGHT_FRAMES_1` (flip-book art), `FLOATSTONE_WALL_ATLAS_1` (only if the owner asks for swirl grain).

## BLOCKED art (drop-in paths)
- `RM_CinderCrust`: `D:\Luke\dev\Rimworld\src\RimMandrake\TheForge\Textures\Things\Plant\RM_CinderCrust\RM_CinderCrust_a.png`. Its Q13 identity has to be written first.
- `RUT_TibannaGas`, `RUT_FoundryTowerEntrance`, `RUT_FoundrySalvageCache`: still DEPLOY_HOLD, with no render in artpipe `done/`, `_artsrc/`, `registry.jsonl` or `Transient/*.decisions.json` (sanity probe: `suush` and `korrum` were both found). They go under `D:\Luke\dev\Rimworld\src\RimUtinni\UtinniPatches\Textures\` at each def's own texPath.

## Side finding (not changed)
- The `LavaSnail` row on `RM_TheForge` is guarded by `MayRequire="sarg.alphabiomes"`, but the def dump attributes LavaSnail to `ludeon.rimworld.odyssey`.

## Verification
- XML parse passed on all 11 touched def/patch/About files.
- DefName sweep over every XML file under `src/` (probe `RM_Suush` found): the only name clashes are the ThingDef/PawnKindDef pairs.
- Every texPath resolves except the pre-existing `RM_CinderCrust`. Every wildAnimals/wildPlants/leather/harvest/body/sound reference resolves to our own defs or to the def dump. Core parents exist.
- `validate_patch.py`: the only error is the pre-existing CinderCrust texPath.
- `run_selftests.py`: 76/78. The failure is `selftest_deployed_biome_refs`, which was already known. 1 test was UNMEASURED (bridge metadata).
