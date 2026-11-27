# Wrecked Machines 0.1.0: how the mod is built

Design Version 0.1.0. The bars are in `design/concepts/WreckedMachines/tree.json`, the owner's view of them in `sheet.md`, the
order of the build and its risks in `plan.md`, the scenes in `scenes.json`. This page is the build's own contract: the names, the
files and the behaviours that the code, the defs, the tests and the proof script agree on. Change a name here and in the code in
one landing. The last section says what is not built yet; keep it true.

A **level** is Wrecked, Kludged, Refurbished or Original. A **line** is one ancient machine with its three level defs and its
donor (the Original: the factory mod's or the base game's own def). Twenty lines: the 18 production machines of Vanilla
Furniture Expanded - Factory (17 without Vanilla Cooking Expanded), the vanometric power cell and the psychic emanator.

## The onboarding table

One def for each line, written by hand, in `Defs/MachineLines/*.xml`:

```xml
<RimMandrake.WreckedMachines.RM_MachineLineDef>          <!-- the cannery's: MayRequire="VanillaExpanded.VCookE" -->
  <defName>RM_WM_Line_smelter</defName>
  <key>smelter</key>                                     <!-- the Mod Settings key and the proof type's line name -->
  <label>automated smelter</label>                       <!-- the Mod Settings line's text is made from it -->
  <original>VFEFactory_AutomatedSmelter</original>
  <wrecked>RM_WM_AutomatedSmelter_Wrecked</wrecked>
  <kludged>RM_WM_AutomatedSmelter_Kludged</kludged>
  <refurbished>RM_WM_AutomatedSmelter_Refurbished</refurbished>
  <firstProject>RM_WM_AutomatedSmelterKludging</firstProject>       <!-- opened by the study of the Wrecked def -->
  <secondProject>RM_WM_AutomatedSmelterRestoration</secondProject>  <!-- opened by the study of the Kludged def -->
  <kludgedProcesses><li>VFEFactory_SmeltMetalFromSlag</li>...</kludgedProcesses>  <!-- a part of the donor's processes, not empty -->
  <kludgedProcessCount>0</kludgedProcessCount>           <!-- for a donor whose processes are made at startup: the first N of them -->
  <kludgeCost><Steel>120</Steel><ComponentIndustrial>3</ComponentIndustrial></kludgeCost>
  <kludgeWork>3000</kludgeWork>
  <refurbishCost><Steel>200</Steel><ComponentIndustrial>5</ComponentIndustrial><RM_WM_AncientComponent>1</RM_WM_AncientComponent></refurbishCost>
  <refurbishWork>4000</refurbishWork>
  <kludgedMovable>false</kludgedMovable>
  <refurbishedMovable>true</refurbishedMovable>
</RimMandrake.WreckedMachines.RM_MachineLineDef>
```

Keys and donors (the keys in bold are named by the proof script): **smelter** `VFEFactory_AutomatedSmelter`, **autoloom**
`VFEFactory_Autoloom`, **alloyforge** `VFEFactory_AutomatedAlloyForge`, **drill** `VFEFactory_AutomatedDrillPlatform`,
**cannery** `VFEFactory_AutomatedCannery`, **powercell** `VanometricPowerCell`, **emanator** `PsychicEmanator`, autofarmer
`VFEFactory_Autofarmer`, biofuelrefinery `VFEFactory_AutomatedBiofuelRefinery`, masonrysaw `VFEFactory_AutomatedMasonrySaw`,
mincer `VFEFactory_AutomatedMincer`, conveyoroven `VFEFactory_ConveyorOven`, assembler `VFEFactory_AutomatedAssembler`,
neutroamine `VFEFactory_NeutroamineSynthesizer`, ammopress `VFEFactory_AutomatedAmmunitionPress`, distillery
`VFEFactory_AutomatedDistillery`, granulator `VFEFactory_MedicineGranulator`, machiningbay `VFEFactory_AutomatedMachiningBay`,
crematorium `VFEFactory_AutomatedCrematorium`, fishfarm `VFEFactory_AutomatedFishfarm`.

A machine enters the table only when its Wrecked and Kludged pictures have passed the art judge (plan.md, risks). Until then
it has no line and is the factory mod's ordinary machine.

## The level defs

Level def names: `RM_WM_<donor name without VFEFactory_>_<Level>`; the three built lines keep `RM_WM_AutomatedSmelter_*`,
`RM_WM_PowerCell_*`, `RM_WM_PsychicEmanator_*`. Every level def carries
`<li Class="RimMandrake.WreckedMachines.WreckedMachineGrade"><grade>Level</grade><line>key</line></li>` in `modExtensions`
and no `designationCategory`, no `researchPrerequisites`, no `replaceTags` and no build-over place worker: nobody builds a
level, a level is reached by repair.

- **Wrecked.** `minifiedDef` MinifiedThing and a `thingCategories` entry (every wreck has a carried form, rule `R_lift`), the
  donor's `Mass`, no `terrainAffordanceNeeded` (rule `R_ground`), no comp that joins a power or pipe net (rule `R_wreck_inert`;
  the draw-in `buildingTags` stay), `tickerType` Normal only if a comp needs it. Comps: the study comp and
  `RimMandrake.WreckedMachines.CompProperties_WreckedMachine`. A picture of its own.
- **Kludged.** The donor's def with the row's part of the processes, more breakdowns, no overclock, the donor's ground need,
  the study comp (its own analysis id) and the machine comp. `minifiedDef` only when the row's `kludgedMovable` is true. A
  picture of its own.
- **Refurbished.** The donor's def with every process, the donor's ground need, the machine comp (no further repair, so no
  study comp). `minifiedDef` only when `refurbishedMovable`. It may draw the donor's picture (rule `R_whole_picture`).

The study comp is the base game's own, with this mod's comp class for the toggle:

```xml
<li Class="CompProperties_CompAnalyzableUnlockResearch">
  <compClass>RimMandrake.WreckedMachines.CompMachineStudy</compClass>
  <analysisID>77120011</analysisID>            <!-- unique in the game: 77120000 + 10 x the line's number + the step (1 or 2) -->
  <requiresMechanitor>false</requiresMechanitor>
  <canStudyInPlace>true</canStudyInPlace>
  <analysisRequiredRange>3~3</analysisRequiredRange>
  <analysisDurationHours>4</analysisDurationHours>
  <cooldownTicks>20000</cooldownTicks>
  <destroyedOnAnalyzed>false</destroyedOnAnalyzed>
  <activateTexPath>UI/Icons/Study</activateTexPath>
  <jobString>study the wrecked automated smelter</jobString>
  <inspectString>Can be studied by a researcher.</inspectString>
  <completedLetterLabel>...</completedLetterLabel><completedLetter>...</completedLetter><completedLetterDef>PositiveEvent</completedLetterDef>
  <targetingParameters><canTargetBuildings>false</canTargetBuildings><canTargetAnimals>false</canTargetAnimals><canTargetMechs>false</canTargetMechs><onlyTargetControlledPawns>true</onlyTargetControlledPawns></targetingParameters>
</li>
```

Each line's two `ResearchProjectDef`s are on the tab `RM_WM_Restoration`; the first has `<requiredAnalyzed>` with the Wrecked
def, the second has the Kludged def and the first project as its prerequisite. `Source/onboard.py` stamps a line's three
level defs and two projects from the donor's XML and the row (dev tooling; the row is the hand-written part).

What the game's files cannot give is set by C# at startup and whenever settings are applied, from the donor def, never from a
copy: the Refurbished def's process list is the donor's list as loaded (the factory mod adds the autoloom's, the machining
bay's and the fish farm's processes to its own defs in code) plus anything a neighbour patched onto ours; the Kludged list
is the row's part of it plus everything on the Kludged def's own list as loaded, so a neighbour's process stays whether or
not the donor has it too. The two rules are `KludgedProcesses` and `RefurbishedProcesses` in the kernel, read offline by the
fuzz family `process` of `T_KERNEL_FUZZ`. Work speed of a level is the donor's speed times the level's ratio (`kludgedRatio`,
`refurbishedRatio` in Mod Settings), applied by one Harmony postfix on `PipeSystem.CompAdvancedResourceProcessor.
GetNotInRoomRoleFactor` (the one place the factory's process time is scaled for a building).

## The C#

Namespace `RimMandrake.WreckedMachines`, assembly `RimMandrakeWreckedMachines`, project `Source/RM_WreckedMachines.csproj`
(build: `python3 src/RimMandrake/Utils/winbuild.py WreckedMachines`).

- `Kernel/RM_WreckedMachinesKernel.cs`, `Kernel/RM_WreckedMachinesRepair.cs`: Verse-free. The ratios, and the repair record
  with every transition of it (`OrderBlocks`, `Order`, `Deliver`, `Work`, `Cancel`, `Uninstall`, `Save`, `Load`,
  `ProofLine`). `Work` is the one place a level changes. No Verse code decides any of this again.
- `RM_MachineLineDef.cs`: the def above, and `RM_MachineLines`: `All`, `ByKey(key)`, `LineOf(ThingDef, out int level)`,
  `IsOn(line)` (the Mod Settings switch), `DefAt(line, level)`, `ProjectFor(line, step)`, cost and work of a step after the
  cost sliders, `Movable(line, level)`.
- `RM_MachineRepair.cs`: `CompWreckedMachine` (one `RM_RepairRecord`, saved as the kernel's text): the repair order and the
  cancel order as gizmos, the inspect text, the hooks that give delivered materials back (cancel, uninstall, destroy), the
  swap to the next level, the level-changed signal.
- `RM_RepairJobs.cs`: one work giver of the Construction work type and two jobs: carry a missing material to the machine,
  and work on it where it stands.
- `RM_MachineStudy.cs`: `CompMachineStudy : CompAnalyzableUnlockResearch` (the study toggle, progress in the inspect text)
  and a work giver of the Research work type that gives the base game's own `AnalyzeItem` job.
- `WreckedMachinesMod.cs`: Mod Settings and `WreckedMachinesPatcher.Apply` (re-derives every def edit from the shipped def).
- `RM_WreckedMachinesProof.cs`: the static type the proof script reads through `jawa/static_call`. Reads only.
- `WreckedMachinesLadder.cs`: the level extension, the emanator's thought worker, the power and mood ratios.
  `PlaceWorker_BuildOverLowerGrade` stays for the neighbours' own ladders (below); no def of this mod uses it.

**The repair on the machine.** The order is a gizmo on a standing machine of a line that is on, below Refurbished, with no
repair under way. It is unavailable, and its text names each reason, when the next level's project is not finished
("research"), when the machine does not stand on the ground the next level needs ("floor"), or when the repair needs an
Ancient Component and none lies unforbidden on the map ("component"). Giving it makes the record; colonists haul each
material into the machine (the stack is taken out of the world, the record counts it), then work on it until the work is
complete. Then the machine is swapped for the next level's def at the same cells, facing, faction and health share, **with
the same thing id number**, and one signal `RM_WM_LevelChanged` goes to `Find.SignalManager` with the named arguments
`SUBJECT` (the machine), `FROM` and `TO` (the level names). The mod names no listener. Cancel, an uninstall order and
destruction put every delivered unit back on the map beside the machine; the level does not change. With the line off or
the ground wrong a repair waits: nothing is delivered and no work is done, and cancel still gives everything back. No frame
or blueprint ever stands on the machine.

**Study.** The player turns "Study" on once on a wreck (or a Kludged machine); the toggle is this mod's, the progress and
the research lock are the base game's (`AnalysisManager`, `requiredAnalyzed`). A colonist who can research then studies the
machine where it stands, three sessions with a pause between them, by himself. The project is the colony's knowledge: a
second machine of the same def shows no study to do. Biotech must be installed for the lock (every DLC is assumed).

**Ground.** A working level's def keeps the donor's `terrainAffordanceNeeded`. The repair order reads
`GenConstruct.CanBuildOnTerrain` for the next level's def on the machine's own cells.

**Mod Settings.** `machineLines` (`Dictionary<string,bool>`, one switch for each row of the table, drawn from the table,
shipped on): off, the donor is in the build menu as its own mod has it, the line's projects are hidden, its wreck is not
placed, and its machines on the map stand unchanged and take no order. `placeInRuins`, `placeOnOrdinaryMaps`. The cost and
ratio sliders and the two salvage switches stay. A label says when its switch takes effect.

**The proof type.** `RM_WreckedMachinesProof`, every method static, string arguments, text out, one entry a line; the
contract is written above the scenes in `validation.py` (Loaded, Machines, Settings, Projects, Level, Repair, SignalLog,
Placement, InRuinRoom, Speed, Onboarding, LineLabels, TextureIds, PlantLighterWrecked). A thing argument is the thing's id
text; the proof finds the thing by the number at its end, so an id read before a repair still names the machine after it.

## Names that neighbours read (rule R_neighbour_names)

Change one only together with the neighbour's file, in one landing. `T_NEIGHBOUR_NAMES` will read them.

- Cold Storage and the Cuisine mod put `WreckedMachineGrade` (fields `grade`, `line`) and `PlaceWorker_BuildOverLowerGrade` on
  their own lockers and caskets, and Cold Storage calls the static `WreckedMachineGrade.RatioFor(MachineGrade)` by reflection.
  Both find this mod by its name, `Wrecked Machines`. Both cost `RM_WM_AncientComponent`. The Cuisine mod's casket research
  follows `RM_WM_PowerCellRestoration`.
- The Armoury adds alloy processes to `RM_WM_AutomatedSmelter_Kludged` and `_Refurbished`, and its durasteel process to
  `RM_WM_AutomatedAlloyForge_Kludged` and `_Refurbished`.
- ResearchRetag sets a tab on `RM_WM_AutomatedSmelterRestoration`. The forge's two old projects are gone
  (`T_FORGE_GATES_GONE`).

## The pictures

Each large machine needs a Wrecked and a Kludged picture in four facings (8 files), on the donor's own canvas. One image
call for each facing, edited from the donor's facing with an approved sibling as the style anchor (`MACHINES.md`); the model
is reached only through the Codex door. `Source/facing.py` runs one facing (the call, `fit_sprite.py`, `check_sprite.py`, a
look sheet); `Source/judge_packet.py` makes what a judge that did not make the picture is given
(`design/RimMandrake/art_judge_brief.md`); `Source/install_pictures.py` writes the record and installs each kept picture
through `art.py install`; `Source/onboard.py land <key>` then moves the line into `Defs/`. The judge's record for each file, with
the file's hash, goes in `design/concepts/WreckedMachines/version/evidence/art/`; `T_ONBOARDING_COMPLETE` refuses a picture
without one.

## The checks

`design/concepts/WreckedMachines/version/test_table.md` lists them. Offline, built: `T_KERNEL_FUZZ`, `T_REPAIR_STATE_WALK`,
`T_SALVAGE_RULE`, `T_DISTILLATION_LOADS`, `T_LATER_STAYS_OUT`, `T_ONBOARDED_SET`, `T_ONBOARDING_COMPLETE`. The live
scenes are the chains `scene_*` of `validation.py`, read through the proof type.

## Not built yet

As of 2026-11-27 10:00 AM PST (the run on RIMMANDRAKE_AUTOBUILD_WRECKEDMACHINES_SEVEN_BARS_LEFT, stopped by an order):

- **Lines.** 17 of 20 are on the table. Staged, waiting for pictures: `granulator` (8 pictures made, not judged), `fishfarm`
  (Wrecked made, Kludged not), `autofarmer` (5 of 6 made). The fish farm's and the autofarmer's Kludged level is filled by
  the C# at startup (no process list in the donor's XML): not yet seen in the game.
- **Pictures of the two carried machines.** The power cell's and the emanator's Wrecked and Kludged defs still tint the base
  game's picture (`Defs/ThingDefs_Buildings/Buildings_WreckedMachines_Mobile.xml`). When their pictures land, each def names
  its own `texPath` and `graphicClass` and loses its `color`. The component still tints the base game's icon.
- **In the game.** Loaded clean on tier `wreckedmachines_solo`; the repair on the machine, its cancel, the component gate and
  the uninstall during a repair pass their scenes. Not run yet: every other scene (study, levels, menu, placement, settings).
- **Not started.** Placement in ruin rooms and on ordinary maps (the three placement proof methods answer "not built yet"),
  the stop of the base game's hand-outs, the autofarmer's Kludged speed, who may lift a wreck as data (rule `R_lift`), the
  scene `sc_old_save`.
