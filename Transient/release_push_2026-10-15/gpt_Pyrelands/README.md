# Pyrelands — GPT pre-release dossier (BENCH, 2026-10-15)

Owner, 2026-10-15: *"do a full ConsultGPT on each mod individually with all of its information, the design goals, the
known behaviors, and information on how we debug rimworld so that it can help grind out any strange hidden behaviors."*

**Result: `TRIAGE.md`** (19 filed items, 9 rejected). The raw answers are `answer1a_burn_regrowth.md`,
`answer1b_ash_terrain.md`, `answer1c_lightning_dig.md`, `answer2_creatures.md` and `answer3_plumbing.md`.

## How it was asked
- Tool: `src/RimMandrake/Utils/gpt_consult.py` (gpt-6.1-sol, high effort), with every file inlined.
- Five consults. One prompt file each: `q1a_burn_regrowth.md`, `q1b_ash_terrain.md`, `q1c_lightning_dig.md`,
  `q2_creatures.md`, `q3_plumbing.md`. Each shares `question_common.md` (hunt list + output format).
- The first fire-ecology consult (≈450 k chars) timed out at 575 s, so it was split into 1a/1b/1c.
- Source files were inlined with line numbers (a `NNNNN| ` prefix on a scratch copy), so the cited line numbers are repo line numbers.

## Context every consult carried
- `shared_context.md`: what Pyrelands is, the owner rulings that bound it (one kind of heat; Plant ticks only `TickLong`;
  no animal vanishes without a sign; no worldgen; every DLC assumed; Mod Settings rule; flyers never live-tested
  without the owner), and a summary of how we debug.
- A known-behaviours digest (59 ledger items matching PYRE/FURNACE/FIREHAWK/SCORCH/EMBER/BURROW/…, every non-claim event,
  plus the open item prose, lessons and the 2026-10-15 r5–r7 SITTING Pyrelands lines). It was generated into the
  scratchpad and not committed. Rebuild it from `infrastructure/state/ledger/events/*.jsonl` and
  `infrastructure/state/items/PYRELANDS_*.md`.
- `design/RimMandrake/debug_process.md`
- `skills/rimworld-modding/references/project-engine-facts.md`
- `infrastructure/state/facts/instrument_traps.md`
- `design/Jawa/worldbuilding/biomes/the_pyrelands.md`
- `design/validation_walks/RimMandrake/Pyrelands.md` (north star)
- `design/validation_walks/RimStarWars/FireEcology.md`
- 1b also got `design/RimMandrake/pyrelands_ash_redesign_2026-10-12.md`.

## Source per consult (all under `src/RimMandrake/Pyrelands/` unless noted)
- **1a burn and regrowth:** `Source/FireEcologyHook.cs`, `Source/Kernel/RM_BurnKernel.cs`, `Source/Kernel/RM_FireEcoKernel.cs`,
  `Source/MapComponent_BurnLine.cs`, `Source/PlantGrowthStages.cs`, `Source/PyrelandsFireFront.cs`, `Defs/ThingDefs_Plants/*`,
  `Defs/ThingDefs_ScorchFruit/*`, `Patches/RM_PyrelandsIgniters_Comps.xml`
- **1b ash and terrain:** `Source/PyrelandsAshField.cs`, `Source/WildPlantAllowlist.cs`, `Source/RM_PyrelandsDensityEnforcer.cs`,
  `Defs/TerrainDefs/*`, `Defs/WeatherDefs/*`, `Defs/ThingDefs_Ash/*`
- **1c lightning and dig:** `Source/Kernel/RM_BreakerKernel.cs`, `Source/RM_LightningBreaker.cs`, `Source/RM_TerrainDig.cs`,
  `Defs/ThingDefs_Fulgurite/*`, `Defs/LightningBreaker/*`, `Defs/ThingDefs_Sprayer/*`
- **2 creatures:** the `Source/` comps, jobs and patches for furnace-beast, fire-hawk, burrow, giants and world herd (17 files);
  `Defs/ThingDefs_Races/*`, `ThinkTreeDefs/*`, `JobDefs/*`, `HediffDefs/*`, `DamageDefs/*`, `ToolCapacityDefs/*`, `ThingDefs_Items/*`;
  `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`
- **3 plumbing:** `Source/RM_PyrelandsMod.cs`, `Source/PyrelandsTuning.cs`, `Source/PyrelandsMechanicsGate.cs`, the DefOfs,
  `Source/PyrelandsFireRiteHook.cs`, `Source/FireEcologyHook.csproj`, `About/About.xml`, `Defs/BiomeDefs/*`, `Defs/GenStepDefs/*`,
  `Defs/WorldObjectDefs/*`, `Defs/SandShovel/*`, `Patches/RM_AcousticPayload_Pyrelands.xml`, `Patches/RM_ShovelSand_Orders.xml`,
  Keyed; `src/RimUtinni/UtinniPatches/Patches/AshStorms_Pyrelands.xml`; all of `src/RimUtinni/PyrelandsMechanics/`
  (Source, Defs, Patches, About, Keyed)
