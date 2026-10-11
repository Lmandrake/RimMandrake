# Mines 2.0 (`Cain.Mineshaft`) assessment, 2026-10-11

Item: `CANON_MATERIALS_BUILD_1`. The owner's ruling, by question card on 2026-10-11 (these are his typed words):
*"The mine mod is here just to study so we can make similar structures as part of generators or inhabited. Examine the
mod now. If it is trivial to reproduce this for out own purposes then retire the mod and make our own. If the mod
remains valuable or difficult to reproduce then we reconfigure it"*

## 1. Verdict

**TRIVIAL TO REPRODUCE: retire the mod and use our own.** Our own is built: `mandrake.rm.mineshaft`
(`src/RimMandrake/MineShaft/`), §5.

Mines 2.0 has no structures, no map generation and nothing a pawn could live in. It is **one work table with
generated bills**: a 5x4 "mine" building where a miner turns work into ore from nothing, one bill per mineable rock. Its
only "structure" is one sprite (`Mineshaft_north/south/west.png`). So there is nothing in it to study for the generator
or inhabited structures he named: it has no layout, no room, no prefab, no gen step.

What makes it a mod at all is a short C# pass (about 120 lines that matter) that builds the recipes at startup. The
rest is a settings screen, a player-made "custom resource" editor (681 lines), compat shims for other mods, and fixes to
its own interaction-cell bug. Our version does the same core job in 84 + 275 lines of C#, with the canon rules built in
as data instead of gated afterwards.

The retirement is half done, on purpose. The game is running, and the canonical save still names `cain.mineshaft` in its
mod list. Taking it off the live list now could stop another window's load. §6 lists what was done and what is left.

## 2. What the mod is

Measured from the installed copy, workshop `2503894706` (1.6 folder plus `Common/`, read-only; GitHub source
`ekremyk2/Mine`).

| Part | What it is | Size |
|---|---|---|
| `MinesAutomated_ThingDef_Mine` | `Building_WorkTable`, 5x4, wood or stone plus 10 steel, bills tab. 1.6 swaps in `MinesAutomated.Building_Mine`, which only moves the interaction cell. | 1 def + 3 textures |
| `MinesAutomated_ResearchProjectDef_minecraft` | Medieval research, 1000 points, needs Stonecutting + Smithing | 1 def |
| `DoBillsMine` | `WorkGiver_DoBill` under Mining | 1 def |
| `MinesAutomated_ThingDef_UnfinishedMineWork` | unfinished thing for bill progress | 1 def + 1 texture |
| `MinesAutomated_RecipeDef_Base` | abstract recipe: MiningYield / MiningSpeed, Mining skill | 1 def |
| `CreateRecipeDefs.cs` | **the core**: one RecipeDef per def that is `mineable`, has `mineableThing` and is `isResourceRock` (plus natural stone when stone chunks are on). One bill per product. Work = ceil(HP/80) x 60 ticks; yield = the rock's `mineableYield`. | 270 lines |
| `MineRecipes.cs` | registers the generated defs, clears the table's recipe cache, labels duplicates, clamps yield (chunks fixed at 1) | 330 lines |
| `MinesAutomatedExtension` (`OnStartup.cs`, `MineableSettings.cs`) | a `DefModExtension` that turns any item def into a bill (how LK's Outer Rim compat makes tibanna, beskar and hypertech components mineable) | 149 lines |
| `MinesAutomated.cs` | GameComponent (re-applies settings on load), the interaction-cell fix, `RecipeWorker_Mine` ("only deep deposits on this map", off by default), a deep-deposit cache | 214 lines |
| `Settings*.cs` | global and per-recipe work/yield multipliers, toggles for logging, extensions, stone chunks, deep-only | 629 lines |
| `CustomResources.cs` | an in-game editor for adding a bill for any item by hand | 681 lines |
| Patches | `Patch_Mine_1_6.xml` (thingClass + interaction cell), `Patch_MedievalOverhaul.xml` (drops 3 bills when Medieval Overhaul is active) | 2 files |

Totals for 1.6: 9 C# files, **2,312 lines** (2,308 without the generated obj file); 6 def files, 149 lines; 2 patch
files; 4 textures plus a preview. It depends on nothing. Two other mods depend on it: `leutiankane.mines2patchouterrim`
(LK's Outer Rim compat, one patch file adding `MineableSettings` to OuterRim tibanna, hypertech component, beskar,
duracrete, durafiber, ...) and our own `mandrake.rut.researchretag` (patches its research, §3).

On the live capture (DefDump 2026-10-11T05-02-19Z) it generates **76** bills. That includes shafts for things the canon
rulings forbid: beskar, durasteel, plasteel, doonium, all three component tiers, and gold and gems on any map. That is
why `RSW_MineShaftCanonGate.cs` exists.

## 3. What we use from it, and what depends on it

**We use nothing from it except the bench itself.** No def, class or texture of ours inherits from it or calls it.
Every reference we have is there to *contain* it:

| Reference | What it does | After retirement |
|---|---|---|
| `src/RimStarWars/Armoury/Source/CanonMaterials/RSW_MineShaftCanonGate.cs` (+ `RSW_MaterialsKernel.MineShaftBanned`, setting `mineShaftCanonGateEnabled`, fuzz family `materials`, `prove_canon_materials.py` `mineshaft_check`) | removes 7 of the 76 bills after Mines builds them | does nothing once Mines is off the list (`Apply` returns 0 when the type is absent). Delete it at the list swap (§6). |
| `src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml`, `RUT_TechprintGating.xml`, `RUT_ResearchTabAssign.xml` | retag `MinesAutomated_ResearchProjectDef_minecraft` (Industrial, no techprint, Refinery tab) | each is a `PatchOperationConditional` on the def, so it skips silently. These files are generated (`design/Jawa/research_review/build_retag_patches.py`), so the generator owns their removal. Whether `RM_Research_MineShaft` gets the same retag is the generator's call. |
| `src/RimUtinni/ResearchRetag/About/About.xml` `loadAfter cain.mineshaft` | load order | leave it until the list swap, then remove it |
| `src/RimUtinni/UtinniPatches/About/About.xml` `loadAfter leutiankane.mines2patchouterrim`, `Patches/TibannaEmbargo_CutMineableRoute.xml` | removes LK's tibanna mine route | the patch is guarded and skips once LK is gone. Removing the loadAfter **before** the swap could run the embargo before LK's patch and re-open the tibanna route, so it goes in the same step. |
| The canonical save `CANONICAL_ASHKARR_START_2026-09-12.rws` (17.5 MB, read 2026-10-11) | **no placed Thing** of the mod: 0 `<def>MinesAutomated_ThingDef_Mine</def>`, 0 `MinesAutomated_RecipeDef_` (no bills). What it does hold: `meta/modIds` lists `cain.mineshaft`; `researchManager/progress` has a key for its research; two packing filters (`packUpFilter/allowedDefs`) and `priceHistoryRecorders` name its defs; `components` holds `MinesAutomated.GameComponent`. Sanity probe on the same read: `<def>Steel</def>` 29, `Zeddo` 3. | all of these are Scribe "could not load reference" entries that the game drops. The only real effect is the mod-mismatch check on load: `meta/modIds` makes `rimworld/load_game` refuse with `missing_mods` until the save is loaded once with the new list and saved again. No `ignoreModCompatibility` force-load is needed or advised (the Lumi doors incident). |

## 4. What reproducing it takes

| Feature | Needed? | Cost for us |
|---|---|---|
| The bench, research, work giver | yes | ~90 lines of XML |
| One bill per resource rock, work from HP, yield from `mineableYield`, chunks fixed at 1, cache reset | yes | ~80 lines of C# |
| Canon bars | yes | policy defs read at generation time (XML, any mod can add one). This replaces a gate that has to undo another mod's code. |
| Home-biome minerals (gold, silver, uranium, jade, gems only in their home biomes, MINERALS_WHERE_THEY_BELONG_1) | yes | a `RecipeWorker` that offers a bill only when the map holds the vein (rock still on the map, or a deep deposit). Mines' nearest feature was "deep deposits only", off by default, and it ignored rock on the surface. |
| Settings: bills on/off, vein rule, stone chunks, yield and work multipliers | yes (house rule) | ~100 lines on our SettingsKit |
| Per-recipe multipliers, the custom-resource editor, `MineableSettings` for arbitrary items, compat shims | **no** | Every canon question about the extension route (tibanna, hypertech components, beskar) went the same way: shut it. It would only bring back what the gates fight. |
| Its own sprites | no (no donor art kept) | our own sprite is owed (§5) |

Total: about a day of work. It was done in this pass: 359 lines of C# (including the Verse-free kernel), 106 lines of
XML, a 168-line fuzz and a 287-line first script. It costs no Harmony and nothing to maintain against an upstream.

## 5. The replacement that was built

`src/RimMandrake/MineShaft/`, packageId **`mandrake.rm.mineshaft`**, "Mandrake Mine Shaft". It is in the RimMandrake
tier because nothing in it is Star Wars. Namespace `RimMandrake.MineShaft`.

- **Defs**: `RM_MineShaft` (3x3 work table, wood or stone plus 10 steel), `RM_Research_MineShaft` (Medieval, 1000,
  Stonecutting + Smithing), `RM_DoBillsMineShaft` (Mining), `RM_MineShaftPolicy_Base` (bars `ComponentIndustrial`,
  `ComponentSpacer`).
- **C#** (`Source/MineShaftMod.cs`, `Source/Kernel/RM_MineShaftKernel.cs`): at startup it reads every `MineShaftPolicyDef`,
  makes `RM_MineShaft_<rock>` for each eligible rock, ranked as Mines ranked them (ore before stone, scattering before
  event-only, commoner, weaker, then defName), skips barred products, and resets the table's recipe cache.
  `RecipeWorker_MineShaft` applies the master toggle and the vein rule. No Harmony, no dependency.
- **Canon bars**: `src/RimStarWars/Armoury/Defs/ThingDefs/RSW_MineShaftCanonPolicy.xml`, guarded by
  `MayRequire="mandrake.rm.mineshaft"`. It covers the Mines gate's eight products (`KOTOR_IngotBeskar`, `KOTOR_RawBeskar`,
  `OuterRim_Beskar`, `OuterRim_PureBeskar`, `RSW_Durasteel`, `KotORChunk_durasteel`, `Plasteel`, `RSW_DooniumOre`) plus
  `OuterRim_ComponentHypertech`. With the base policy, that makes components never mined (owner, typed 2026-09-25). The
  vein rule covers gold and gems. The earlier open question, whether to ban the industrial, spacer and hypertech
  components from the Mines shafts, is superseded: those bills do not exist in our mod.
- **Mod Settings** ("Mine Shaft"): shaft bills on/off (takes effect at once), only the veins this map holds (at once),
  stone chunk bills, yield multiplier and work multiplier (0.25x to 4x, all three at the next start).
- **Proof**:
  - `python3 src/RimMandrake/MineShaft/validation.py`: static checks, plus a replay of the generator rule over the newest
    capture. Result: **PASS**, 248 eligible rocks, **62 bills**, 25 rocks barred (every beskar, durasteel, plasteel,
    doonium and component rock, including the GravTide crossable variants). Steel and gold bills are present as sanity
    probes. A planted defect (Plasteel dropped from the canon policy) goes red twice.
  - `python3 src/RimMandrake/Utils/selftest_mineshaft_fuzz.py`: 6 families, 64,002 cases, 0 failures. It first caught a
    real int overflow in the yield clamp, now fixed.
  - The DLL builds clean through `winbuild.py MineShaft`.
  - Walk: `design/validation_walks/RimMandrake/MineShaft.md`.
- **Not yet proven**: anything live. Never loaded; the vein rule's per-map answer has no bridge reader yet (UNMEASURED,
  first poke in the script). **Art owed**: the shaft draws vanilla's deep drill texture as a stand-in (artpipe search for
  mineshaft/minehead: 0 hits).

## 6. Retirement: what was done, and what is left for the owner

**Done in this pass:** the assessment; our mod built and proven offline; the canon policy; nothing deleted, and no
installed mod touched.

**Left, in one sitting with the game down** (filed as an item, see the ledger note on `CANON_MATERIALS_BUILD_1`):
1. `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod MineShaft --apply` (and redeploy the Armoury for the
   policy def).
2. Live `ModsConfig.xml` and `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`: drop `cain.mineshaft` and
   `leutiankane.mines2patchouterrim` (LK's compat cannot outlive it) and add `mandrake.rm.mineshaft`. Use an ElementTree
   edit that keeps order and CRLF, as the Mo'Events retirement did.
3. Add both to `infrastructure/state/facts/retired_mods.json`.
4. Remove the two `loadAfter` lines (`src/RimUtinni/ResearchRetag/About/About.xml`, `src/RimUtinni/UtinniPatches/About/About.xml`).
5. Delete `RSW_MineShaftCanonGate.cs`, its setting, `MineShaftBanned`/`MineShaftPrefixes`/`UnlistMineShaft` from the
   kernel, the fuzz cases and `prove_canon_materials.py`'s `mineshaft_check`. The canon policy XML is then the single
   list. Drop the cross-check in `MineShaft/validation.py` that reads `MineShaftBanned`. Rebuild the Armoury DLL.
6. Load the canonical save once on the new list (accept the mod-mismatch dialog; no placed Things depend on it) and save it,
   so `meta/modIds` stops naming `cain.mineshaft`.

**Only the owner can do:** unsubscribe Mines 2.0 and LK's compat in Steam, if he wants them off disk. Deleting installed
mods is not an agent's job, and nothing here needs it.
