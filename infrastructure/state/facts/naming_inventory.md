# Naming inventory — what is called what, measured

**MEASURED 2026-08-23 by CHECK** (a retired seat name). CHECK ran two read-only censuses over the working tree at
`301d1299..15a635c7`. This file exists so that the writer of the rename spec for `GREAT_NAMESPACE_RENAME_1`
(`design/V2_DREAMS.md`) never pays for this census again.

⚠️ **A number here is only true of the tree on that date.** Re-measure before you act on any count. The
reason on 2026-08-23: four seats share this checkout.

## Mods — 25, all authored by us

Each mod is `<author>Mandrake</author>` with a `mandrake.*` packageId. The deployed game folder holds exactly these 25
mods and nothing else.

| folder | packageId | assembly |
|---|---|---|
| `src/Jawa/DesertVehicleReskin` | `mandrake.desertvehiclereskin` | DesertVehicleReskin.dll |
| `src/Jawa/Inhabited` | `mandrake.inhabited` | Inhabited.dll |
| `src/Jawa/JawaFactionSlate` | `mandrake.jawafactionslate` | — |
| `src/Jawa/JawaIkee` | `mandrake.jawaikee` | JawaIkee.dll |
| `src/Jawa/JawaIonWeapons` | `mandrake.jawaionweapons` | JawaIonWeapons.dll |
| `src/Jawa/JawaPlantGrowth` | `mandrake.jawaplantgrowth` | JawaPlantGrowth.dll |
| `src/Jawa/JawaVoice` | `mandrake.jawavoice` | — |
| `src/Jawa/Jawa_Armoury` | `mandrake.jawa.armoury` | — |
| `src/Jawa/Jawa_Doctrine` | `mandrake.jawa.doctrine` | — |
| `src/Jawa/Jawa_Patches` | `mandrake.jawa.patches` | — |
| `src/Jawa/RimMandrake_StarWarsRaces` | `mandrake.starwarsraces` | — |
| `src/RimMandrake/BlastDoorFrameAsyncFix` | `mandrake.blastdoorframeasyncfix` | — |
| `src/RimMandrake/CereanManeFix` | `mandrake.cereanmanefix` | — |
| `src/RimMandrake/GravshipAstronautFix` | `mandrake.gravshipastronautfix` | — |
| `src/RimMandrake/JawaRules` | `mandrake.jawarules` | JawaRules.dll |
| `src/RimMandrake/KotORBandolierNorthFix` | `mandrake.kotorbandoliernorthfix` | — |
| `src/RimMandrake/MSEDroidFix` | `mandrake.msedroidfix` | — |
| `src/RimMandrake/PhytokinBarkHeadFix` | `mandrake.phytokinbarkheadfix` | — |
| `src/RimMandrake/PlanetPresetPrime` | `mandrake.planetpresetprime` | PlanetPresetPrime.dll |
| `src/RimMandrake/ResearchKitEastFix` | `mandrake.researchkiteastfix` | — |
| `src/RimMandrake/RimDefDump` | `mandrake.rimdefdump` | — |
| `src/RimMandrake/SauridFrillFix` | `mandrake.sauridfrillfix` | — |
| `src/RimMandrake/StrandedQuest` | `mandrake.strandedquest` | — |
| `src/RimMandrake/ToolBeltFix` | `mandrake.toolbeltfix` | — |
| `src/RimMandrake/WreckedMachines` | `mandrake.wreckedmachines` | — |

- **One prefix, two shapes:** 22 flat (`mandrake.jawaikee`), 3 dotted
  (`mandrake.jawa.armoury`, `.doctrine`, `.patches`). No `rimmandrake.*` id exists.
- **9 folders carry "Jawa"; exactly 1 carries "RimMandrake"; 15 carry neither.**
- **The tree is crossed against its content.** `JawaRules` sits under `src/RimMandrake/`. `RimMandrake_StarWarsRaces`
  sits under `src/Jawa/`.
- Live `ModsConfig.xml` lists 21 of the 25 (4 deployed-but-inactive).

### The edges a packageId rename would break

- **2 About.xml edges only**, both `<loadAfter>mandrake.starwarsraces</loadAfter>`:
  `JawaIkee/About/About.xml` and `Jawa_Patches/About/About.xml`.
- No `modDependencies` names one of ours. No `loadBefore` blocks exist at all.
- No `PatchOperationFindMod` targets one of our own ids.
- 🔴 **166 of the 247 `mandrake.starwarsraces` occurrences are `MayRequire=` attributes**
  in `src/Jawa/Jawa_Patches/` — top holders `Patches/VanillaFaction_Xenotypes.xml` (72),
  `Defs/FactionDefs/JawaHuttCartel.xml` (21), `JawaJunkers.xml` (17),
  `JawaAscendantHelix.xml` (17), `JawaDeepwaterCompact.xml` (13).
  - ⚠️ **A `MayRequire` that names a dead packageId fails SILENTLY.** The game drops the element and logs nothing. This
    is the single most dangerous line in the whole rename.
- 3 source files hard-code their own id as a Harmony id: `JawaRules.cs`,
  `PlanetPresetPrime.cs`, `JawaPlantGrowth/Source/Patch_Plant_GrowthRate.cs`.

## defNames — 938 occurrences, 935 unique

| prefix family | unique | where |
|---|---|---|
| `RimMandrake_*` | 369 | StarWarsRaces (genes, heads, rulepacks) |
| `Inhabited_*` | 297 | Inhabited (294 are `Inhabited.CharacterDef`) |
| `RimMandrake<Species>` — **glued, no separator** | 138 | 69 XenotypeDef + 69 PawnKindDef |
| `Jawa_*` | 115 | Jawa_Patches (68 PawnKind, 12 Culture, 8 Faction, 18 RulePack…) |
| `JawaIon_*` | 5 | JawaIonWeapons |
| `SW_*` | 4 | StarWarsRaces |
| `WM_*` | 3 | WreckedMachines |
| `JawaPlantGrowth_*` | 1 | JawaPlantGrowth |
| **no project token at all** | **3** | below |

🔴 **`Jawa_Jawa` / `JawaJawa`: MEASURED ZERO.** A case-insensitive search found no match under `src/`. The doubling
exists only in PATHS (`src/Jawa/Jawa_Patches`).

**The 3 bare defNames:** `MandrakeJawa` (XenotypeDef — **the player species**, hard-named
twice by the ScenarioDef and by `MandrakeJawa.xtp`), `Stranded` (QuestScriptDef),
`StrandedTravellerTaken` (HistoryEventDef).

**Three incompatible species schemes coexist:** glued `RimMandrakeTwilek` (69),
`Jawa_Xeno_Gamorrean` (1), bare `MandrakeJawa` (1).

**Items use four different prefixes:** `JawaIon_Blaster`, `Jawa_ClaimRumour`,
`RimMandrake_GandMask`, `WM_AutomatedSmelter_Wrecked`.

## Assemblies — 9, every one flat-namespaced to itself

`DesertVehicleReskin` (net48) · `Inhabited` · `JawaIkee` · `JawaIonWeapons` ·
`JawaPlantGrowth` · `JawaRules` · `PlanetPresetPrime` · `RimDefDump` ·
`JawaBench.BridgeTools`.

All are net472 except `DesertVehicleReskin`. `AssemblyName == RootNamespace` in every case. **No shared `RimMandrake.*` or
`Utinni.*` root exists anywhere.** `JawaBench.BridgeTools` is the only dotted namespace in the codebase.

## Bridge tool protocol — 121 tools, all `jawa/`

CHECK counted the `[Tool(` attributes in the 10 `JawaBench*.cs` sources: 121 attributes, 121 unique names, zero
duplicates. ⛔ Do not count from the DLL. `strings` cannot census .NET metadata.

Per file: World 33 · Terrain 32 · Pawn 18 · Map 16 · Event 13 · Diagnostic 4 · Faction 3 ·
Cache 1 · Vehicle 1.

⚠️ **On 2026-08-23, `CLAUDE.md` said 115. The source declared 121.** The documented number had already drifted.

**The protocol has a split personality:** noun-first `jawa/world_tile_set` against verb-first `jawa/set_*` (21 tools). A
rename spec should settle that too.

## Scenario and player identity

| thing | defName / file | label |
|---|---|---|
| ScenarioDef | `Jawa_UtinniStart` | *the opened hull* |
| player species | `MandrakeJawa` (XenotypeDef) | named twice in the scenario |
| starting pawnKind | `Jawa_Colonist` | — |
| ideoligion | `src/Jawa/ideoligion/The Salvation.rid` | *The Salvation* |

🔴 **There is no authored player FactionDef.** `isPlayer` appears **zero** times in all of
`src/**/*.xml`. The player is vanilla `PlayerColony`/`PlayerTribe`. All 8 authored
FactionDefs are NPC factions. **A rename spec must not assume a player faction exists.**

⚠️ **Unrelated drift found in passing, not yet ruled on.** The scenario's GameStartDialog and `CLAUDE.md` call the clan's
faith **"the Second Hand"**. The shipped `.rid` is named **"The Salvation"**.
