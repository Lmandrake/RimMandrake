# Decision strings — the Scald round, 2026-09-26

Written BEFORE launch per `rimworld-load-round` §2/§3. Supersedes the
ExplosiveGrowth round's strings (that load ran; its file is spent).

**Test list:** `modset_builder --tier proof_terminalbiomes` (10 mods) **plus**
`mandrake.rm.environmentalhazards` and its closure. All five expansions in
(owner ruling 2026-09-19). Restore target: `ModsConfig.FULL.LATEST.xml`, **630
active** (the owner's 629 + `mandrake.rm.luminouspigment` added this round).

## 🔴 THREE assemblies ride this load, not one

The brief named one (`EnvironmentalHazards`). Measured before launch: the
TerminalBiomes deploy plan carried `~ Assemblies/RimMandrake.TerminalBiomes.dll`,
and `LuminousPigment` is brand new and has never been loaded at all. §3 requires
one distinguishable expected-failure signature per assembly, written now.

### A. `RimMandrake.EnvironmentalHazards.dll` (278,016 bytes, rebuilt 13:37)
PROVE  Its own prefix `[RM EnvironmentalHazards]` appears with no `Log.Error`
       level lines. The new `RM_MapComponent_WaterAgitation` must not throw.
EXPECT Zero lines matching `[RM EnvironmentalHazards] ... patch failed, rule NOT armed`,
       zero `RM_GenStep_*: biome` errors on a Scald map.
FAILS AS A Harmony patch-target miss — the class names its own failures
       (`live-prep-viability`, `creche-despoil-manhunter-factor`,
       `leachmoss-wild-spawn-gate`). Those strings belong to THIS assembly and
       to no other, so a hit is unambiguous attribution.
LIES   This assembly logs only on failure paths for most mechanisms. Silence is
       necessary, not sufficient — see the expected-PRESENT check in D.

### B. `RimMandrake.TerminalBiomes.dll` (15,360 bytes, rebuilt 13:37)
PROVE  🔴 **It emits NO log lines at all** (MEASURED: zero `Log.Message/Warning/Error`
       calls in `TerminalBiomes/Source/`). Its success is entirely silent, so it
       gets a def-read bar, not a log bar — see D.
FAILS AS `System.TypeLoadException` / `Could not resolve type ... from typeref` naming
       **`RimMandrake.EnvironmentalHazards`**, during `RebindAllDefOfs` →
       `GenTypes.AllTypesWithAttribute`, followed by RimWorld's own
       `Recovered from incompatible or corrupted mods`.
WHY THAT IS THE SIGNATURE `TerminalBiomes/Source/RM_TerminalBiomesMod.cs` line 2 is
       `using RimMandrake.EnvironmentalHazards;` and the `.csproj` carries a hard
       `<Reference Include="RimMandrake.EnvironmentalHazards">`. This is a **hard
       assembly dependency** that `About.xml` declares only as `loadAfter`.
       ⇒ It is also why the stock `proof_terminalbiomes` tier (which does
       `modDependencies` closure only) builds a list that cannot load this DLL.
       Filed as a finding; EH added to the list by hand for this round.

### C. `RimMandrakeLuminousPigment.dll` (41,472 bytes, NEVER LOADED BEFORE)
PROVE  Its own prefix is `[RimMandrake.LuminousPigment]`.
EXPECT No `[RimMandrake.LuminousPigment]` **warning** lines on a plain startup —
       both of its warnings are runtime map-component paths, not load paths.
FAILS AS Any error naming `RimMandrakeLuminousPigment` or `RimMandrake.LuminousPigment`
       at assembly-load / DefOf-rebind time. Distinct token from A and B: the DLL
       name has **no dots** (`RimMandrakeLuminousPigment.dll`), which nothing else
       in the tree spells that way.
LIES   A brand-new mod that fails to load quietly leaves its defs missing rather
       than erroring, which reads identically to "the def was never written".
       The def-read in D distinguishes those two.

## Expected-PRESENT strings (§2: absence of an error is necessary, not sufficient)

### D. The def set must actually contain this content
Read live with `jawa/get_defs`, `defs` as a **STRING** `"DefType/DefName"` (a list
raises `InvalidCastException` and returns `success:false`; a substring check on a
failed call reads as ABSENT — read `success`/`foundCount`/`notFound`, never the
payload text).

| item | expected-PRESENT def | baseline |
|---|---|---|
| `SCALD_MECHANICS_1` | `BiomeDef/RM_TheScald` present; `WeatherDef/RUT_ScaldSteam`; `ThingDef/RUT_SteamCatch`; `ThingDef/RUT_ScaldVent` | all present ⇒ the kit's defs parsed |
| `SCALD_ART_UPGRADE_WAVE_1` | `ThingDef/RUT_ScaldWreckHull`, `RUT_ScaldWreckTank`, `RUT_ScaldWreckFrame` load, each with its **own** `shadowData` (not ShipChunk's 1.39/0.5/1.25) | three distinct volumes |
| `SCALD_WATER_AGITATION_FLECKS_1` | `TerrainDef/RUT_ScaldWater*` carry tags `RM_WaterAgitationLight` / `RM_WaterAgitationHeavy`; `RUT_ScaldMargin` carries **neither** | tags present, margin clean |
| `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` (Scald) | `RM_TheScald.wildAnimals` resolves **10** species (`RM_ElderSando RM_Noohm RM_Shulla RM_Eesh RM_Doss RM_Muddal RM_Bladderboil RM_Thuum RM_Karrash RM_Ekkel`) with `animalDensity 0.15` | was 3 inline + 3 patch-added; 10 is the new claim |
| `SCALD_STEAM_WEATHER_DESIGN_1` | `WeatherDef/RUT_ScaldSteam` + the biome-wiring patch `RUT_ScaldSteamLock_BiomeWiring.xml` produced no no-op | weather present AND wired |
| LuminousPigment (new mod) | `ThingDef/RM_Crowncarpet` and `ThingDef/RM_Deepfire` present; `RM_WelcomeBlanket` and `RM_RainbowPigment` **ABSENT** (pruned) | the rename actually took |
| Grey Sea wave (rides along) | `BiomeDef/RM_GreySea` with **7** wildPlants and **15** wildAnimals; `animalDensity 0.1` | new content parsed |

### E. `animalDensity` is the gate, not `impassable`
Both seas are `impassable: true` with `animalDensity` 0.15 / 0.1. MEASURED from the
engine 2026-09-26: `impassable` is not read by `GenStep_Animals`/`WildAnimalSpawner`;
`animalDensity > 0` is. ⇒ nonzero is the correct state and needs no live proof here.

## Load-abort terminators (§9)
Watch **both**: `Recovered from incompatible or corrupted mods` **and**
`Caught exception while loading play data`. Ready signal is `Bridge token:` — NOT
the JawaBench ready line, which is lazy and never fires until the first tool call.
