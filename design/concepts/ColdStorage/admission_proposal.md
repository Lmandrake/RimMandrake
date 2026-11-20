# ColdStorage: admission at intake, and a PROPOSED split of Design Version 0.1.0

Written 2026-11-20 by BENCH, item RIMMANDRAKE_ADMIT_COLD_STORAGE_AS_PIPELINE_MOD_RIMFRIDGE_GONE. **Everything below
"What exists" is a PROPOSAL for the Designer stage and the owner.** The Designer's Lock step sets the bars; nothing
here is a lock. Design input: `design/RimStarWars/cold_storage_line_2026-10-26.md` (the "line doc").

## His words

- 2026-10-26 ~07:00 PDT (line doc §0): "...let's just make our own Starwars-type freezer unit with our own properties.
  Commission it, and drop RimFridge... Let's make them in a few sizes and tech levels. Rakatan would be full Stasis
  Chambers (what you unlock through the ship or loot from their ancient tech dungeons/experiences) and the local Star
  Wars one would be cruder devices that work based on cold temperature as expected (fridge-like) and of course then
  there are the stranger versions like the one that seals things in tar, canning-type options from/through VFE. this
  is a critical interaction with Star Wars Cuisine of course. Sealing in sap as well. some of them would not only be
  food preservation but required to impart particularly wonderful tastes."
- 2026-11-20 (ledger 19:49Z, 11:49 AM PST), after RimFridge left the live list: "Also we need to reproduce rimfridge.
  In the new system it needs to be ticketed into part of a mod."

## What exists (measured 2026-11-20, this clone at 6db798e5a4)

- **Code.** `src/RimMandrake/ColdStorage`: 12 C# files, 3,775 lines, namespace `RimMandrake.ColdStorage`; DLL with its
  `.srchash`; last change 6a5ce0ad37 (2026-11-12). Engine: `CompStorageClimate` (Chill, Stasis), `CompSealed`,
  aging, encasing, 9 `ColdStorageMethodDef`s, gated Harmony patches, LWM Deep Storage and Replace Stuff hooks.
- **Devices a player can build or find.**
  - ColdStorage (RM): `RM_EvaporativeCrock` (no power, dry air only), 4 seal stations (`RM_ResinTap`,
    `RM_ResinSealingJarShelf`, `RM_SandDryingBox`, `RM_BrineCrock`), `RM_AncientStasisLocker` in 4 grades (loot).
  - Cuisine (RSW, `src/RimStarWars/Cuisine/Defs/RSW_CoolingUnits.xml`): `RSW_CoolingSupplyUnit` (1x1),
    `RSW_CoolingUnit_Wall`, `RSW_CoolingChamber` (2x2), `RSW_DrinksChiller`, `RSW_CryoUnit` (1x2, -25 C), research
    `RSW_CoolingUnits` and `RSW_CryoStorage`; also the carbon-freezing press, Rakatan stasis casket and vault (4 grades
    each), preserved dishes.
  - TheSump (RM): `RM_TarSealingVat` and tar-sealed / pitch-aged goods.
- **Art.** None of ours. Every cold-storage building and item def reads a borrowed vanilla texture (the crock a plant
  pot, the supply unit and chamber a small shelf, the wall unit the vanilla cooler, the cryo unit the ship cryptosleep
  casket, sealed foods chocolate / kibble / chemfuel / beer). Whether artpipe holds unjudged candidates is UNMEASURED
  (`artpipe_state.py find` timed out at 60 s twice); the job list is
  `infrastructure/artpipe/art_lists/coldstorage_ladder_2026-10-26.csv`.
- **Tests.** `selftest_coldstorage.py`: 214 passed, 0 failed (one day at 25 C: floor 60000 rot ticks, chill unit
  2375, stasis 0, sealed 0). `coldstorage_live_proof.py` A1-A6: never run; its record
  `infrastructure/state/live_proofs/COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE.txt` holds the commands only.
- **Mod Settings.** `RM_ColdStorageMod.cs` has 23 widgets: chill, stasis, stasis flicker and seal aging on/off; power,
  insulation, aging and seal-failure multipliers; one switch per method; hoppers, wall light, wall airtight, readout;
  per-unit enable and fuel.
- **Mod lists.** In the live `ModsConfig.xml` (315 active, both `mandrake.rm.coldstorage` and `mandrake.rsw.cuisine`;
  no RimFridge) and in `infrastructure/state/modlists/manifest.FULL.json`. Deployed folders `ColdStorage` and
  `Cuisine` exist in the game's Mods folder.
- **RimFridge mentions.** None in defs or patches. Four C# comments name RimFridge as the design it replaces
  (`StorageClimateRegistry.cs:9`, `ColdStorageStartup.cs:255`, `HarmonyPatches.cs:15`, `:261`); no code reads it.

## The 0.1.0 vision (PROPOSAL)

A player who had RimFridge loses nothing: from the first powered research they can build cold storage of ours, in a
few sizes and tech levels (a small unit, a wall unit that serves the room, a larder-sized chamber, and a spacer cryo
unit cold enough to freeze), and food kept in it stays fresh in a hot room the way a fridge's food does. Each unit
looks like a Star Wars machine of its tier, not a borrowed shelf, and says on inspect what it holds and how cold it
is. With no power the units warm back toward the room, and a crude unit can frost up and need a pawn. Every unit can be
switched off in Mod Settings, and with everything off the game still loads and plays. (His words: "make them in a few
sizes and tech levels", 2026-10-26; "we need to reproduce rimfridge", 2026-11-20.)

## Proposed split (PROPOSAL for the Designer and the owner)

| Part | Version | Reason |
|---|---|---|
| Chill engine, `RSW_CoolingSupplyUnit`, `RSW_CoolingUnit_Wall`, `RSW_CoolingChamber`, `RSW_CryoUnit`, their research | 0.1.0 | This is what RimFridge gave him; without it, dropping RimFridge loses cold storage. |
| Own art for those five units and the crock | 0.1.0 | A shelf texture that keeps meat frozen is an experience he would reject as strange (a Problem, not Polish). |
| `RM_EvaporativeCrock` | 0.1.0 | The day-one cold box; the only cold of ours before power. |
| Mod Settings for the chill line, and a clean load of every def the mod ships | 0.1.0 | Superb Mod Settings is a standing rule; the built seals, lockers and press load in 0.1.0 whether or not they are judged. |
| `RSW_DrinksChiller` | later (0.2.0) | A label and filter variant of the chamber; RimFridge's drinks feature was dropped by design (line doc §1). |
| Stasis: `RM_AncientStasisLocker`, Rakatan casket and vault, ship unlock, ancient-complex and vault loot, held provisions | later | His Rakatan "full Stasis Chambers" is beyond a fridge; it needs loot and ship routes that are their own experience. |
| Carbon-freezing press and packs | later | Canon flavour, not fridge parity; its art is also owed. |
| The seals (resin, sand, brine, salt, tar, frost aging) | later | "the stranger versions"; their value is taste, which is the Cuisine work. |
| Preserved dishes, preservation-required tastes, VCE ration-sealer reskin | later | "required to impart particularly wonderful tastes" is a Cuisine experience and needs Cuisine's own design. |

Open question for the Designer: the built later-version parts stay loaded in 0.1.0. Either 0.1.0 holds a bar that they
break no load or save, or 0.1.0 ships them switched off by default. The rule that defaults equal shipped behaviour
decides the wording; the Designer picks.

## Old items mapped onto the mod (2026-11-20)

Each open item below carries a ledger note naming ColdStorage and its proposed version.

| Item | State | Version | Note |
|---|---|---|---|
| COLDSTORAGE_DESIGN_FIRST_TOUCH | proposed | 0.1.0 | The mod's first-touch Designer item; runs through the pipeline's Designer, not the retired loop its title names. |
| COLD_STORAGE_LADDER_ART_JUDGE_SHEET | proposed | 0.1.0 | Art for the five units and the crock. |
| COLD_STORAGE_ART_BUILD_SPRITE_BATCH | proposed | 0.1.0 for the cooling units; the rest later | Its stasis, seal and item icons wait with their parts. |
| COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE | built, block ended | 0.1.0 for A1, A5, A6; A2-A4 later | Never run live. Blocked on FLYER_GATE_FIX_NEGATION_READS_AS_FLIGHT, a retired-loop gate since dropped; unblocked. |
| COLD_STORAGE_RSW_RESEARCH_VERIFY_LAYOUT | proposed | 0.1.0 | Research tab placement of the two cooling projects. |
| COLD_STORAGE_DEFS_FIX_DOUBLED_CATEGORY | built | 0.1.0 | The clean-load bar; aged-food defs logged config errors. |
| COLD_STORAGE_CHAMBER_BUILD_DRINKS_CHILLER | built | later | See the split. |
| DRINKS_CHILLER_FIX_COMPS_DROP_STYLEABLE | built | later | Goes with the drinks chiller. |
| STASIS_LOCKER_BUILD_ANCIENT_COMPLEX_LOOT | built | later | Stasis as loot. |
| RAKATAN_STASIS_LOOT_BUILD_HELD_PROVISIONS | built | later | Stasis as loot (RUT). |
| STASIS_PROVISIONS_BUILD_RUT_LOOT_TOGGLE | proposed | later | Its setting goes with that loot. |
| COLD_STORAGE_CUISINE_BUILD_PRESERVE_DISHES | built | later | Cuisine tastes (line doc step 7). |
| COLD_STORAGE_CARBONFREEZE_REDRAW_INTERIM_ART | proposed | later | Carbon-freeze art. |
| VCE_CANFISH_FIX_RESKIN_SKIPS_BILL | built | later | VCE reskin. |
| COLD_STORAGE_BUILD_OWN_LINE_DROP_RIMFRIDGE | umbrella, block ended | superseded | Steps 1-6 and 10 done; every child above now hangs on the mod; superseded by COLDSTORAGE_DESIGN_FIRST_TOUCH. |

Already done before admission (no change): COLD_STORAGE_ENGINE_BUILD_CLIMATE_COMP (09a5462468),
COLD_STORAGE_COOLERS_BUILD_RSW_LADDER, COLD_STORAGE_SEALS_BUILD_RESIN_SAND_BRINE and COLD_STORAGE_TARSEAL_BUILD_SUMP_VAT
(dff5f0da7b), COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS, COLD_STORAGE_STASIS_BUILD_RAKATAN_CHAMBERS (367f0e9c26),
RIMFRIDGE_DROP_FIX_INBOUND_REFS (8eb6ed07b3).

## Tier

- ColdStorage is RimMandrake tier: packageId `mandrake.rm.coldstorage`, defs `RM_`, namespace
  `RimMandrake.ColdStorage`. Its defs and Keyed strings hold no Star Wars words (comments only). Under the
  engine-vs-content rule of `design/NAMING_SCHEME_PLAN.md` (the engine takes the highest tier it honestly passes, the
  content pack its own) that is right for the engine and the generic devices.
- The Star Wars ladder is RimStarWars tier (`RSW_`, in `mandrake.rsw.cuisine`), which is right for its names, but it
  sits in Cuisine, a food mod. So the pipeline unit "ColdStorage" and the fridges a player builds are in two packages.
- Owed, not done here: the Designer decides whether the ladder moves out of Cuisine into a RimStarWars cold-storage
  content pack, or whether ColdStorage's design covers Cuisine's ladder file. Also owed: on the RimMandrake tier alone
  (no Cuisine), a player has no powered fridge, only the dry-air crock; the Designer says whether the generic tier needs
  one.

## What must happen before it runs

The mod is admitted at intake and switched OFF (`./pipe off ColdStorage`). Before it may move, its readiness list
(`design/RimMandrake/standing_rulings.md` §No mod runs forward on a broken pipeline) must read READY, with every
component on its path looked at and each open pipeline ticket classed BLOCKS, RARE or NOT ON PATH:
- the move from intake (`maturation.py advance --to designer`, clause `intake_closed`), `designer_stage.py init`, the
  Designer role launch, its exam, coverage judge and `lock-bars`;
- preflight; the offline build of two packages (`winbuild.py` for ColdStorage and for Cuisine's DLL if the ladder
  stays there) and deploy;
- the tests-first stage, with `selftest_coldstorage.py` registered as a decider;
- the in-game stage: a mod list with ColdStorage, Cuisine, TheSump and all five DLC, the bridge, and
  `coldstorage_live_proof.py`;
- the walk brief and the road back;
- whether a pipeline record can span a mod whose content sits in two packages: UNMEASURED, and a likely BLOCKS row.

Then a word moves it from intake (spec §4 "Intake", exit row) and `./pipe on ColdStorage` cites the READY list.
