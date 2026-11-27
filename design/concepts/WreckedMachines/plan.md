# Wrecked Machines 0.1.0: plan (Designer, stage 3)

Written by run `rm-role-designer-1795773471`, 2026-11-27, and closed by run `rm-role-designer-1795776308` (the item,
the next-version list and the fresh reader's fixes). The bars are in `tree.json`, his view of them in `sheet.md`, the scenes
in `scenes.json`, the models in `models.md`. This page says how the build is put together, in what order, what it
reuses, what can go wrong, and where a real choice of design is left to the builder. The Designer writes no code.

The mod is half built and almost none of it was played. About a third of the built mod stays as it is (the kernel, the
settings kit, the smelter's three pictures, the Ancient Component as an item). The rest changes: how a repair is made,
when study happens, what a wreck is, and 19 machines that are not onboarded yet.

## the case for and against a generic version

His first question on 2026-11-19 was "whether we even bother with the generic version". The Conductor's call
(`d_generic_is_the_mod`) is that the generic mod is 0.1.0. The case, as this design leaves it:

- **For.** Four of our mods already use this mod as a library and none says so (Cold Storage, the Cuisine mod's
  stasis, the Armoury, ResearchRetag). A ladder that stands alone, with its names checked, is worth having for them
  alone. His ruling of 2026-09-15 puts the mod at the RimMandrake level, and the campaign's holy repair needs a plain
  mechanism under it to be holy about. The generic journey (find, carry, study, repair) is complete without a story.
- **Against.** In a stranger's game the mod takes away more than it gives at first: a factory that could be built must
  now be found. The reward is the two machines that nobody can build and the pleasure of the repair, and that
  pleasure rests on pictures that do not exist yet (136 for the factory). Without the campaign there is no reason in
  the fiction why the factory is ancient. The switch for each machine is the answer to the first point, and it is a
  weak one: a mod whose best setting for a stranger may be "most lines off".
- **What decides it here.** The mod is built for the campaign first (his words: "we must first prioritize Utinni
  service") and published by him or not at all. The generic tier costs the campaign nothing and keeps the mechanism
  honest. The prediction that a stranger enjoys it is a prediction, not a bar.

## structure and reuse

- **Kept as built.** The Verse-free kernel (`Source/Kernel/RM_WreckedMachinesKernel.cs`: the ordered ratios, the
  clamps) and its fuzz. The shared settings kit and the re-derivation of every def edit from the shipped def when a
  setting is applied. The smelter's Wrecked and Kludged pictures and the art tooling in `Source/` (`sheet.py`,
  `fit_sprite.py`, `check_sprite.py`, `briefs.py`). The Ancient Component as an item. The patch that takes the donor
  smelter out of the build menu, made general for all 18. The one salvage rule and the distillation machine, untouched
  (rule `R_riders`).
- **Changed.** The ladder by `replaceTags` and the place rule `PlaceWorker_BuildOverLowerGrade` go: a repair is an
  order on the machine with a repair record (bar `repair_on_the_machine`). Every wreck gets a carried form and stands
  on any firm ground (rules `R_lift`, `R_ground`). The power-cell wreck gives nothing. The Refurbished smelter gets
  every job of the donor. The first repair needs study and research (two projects for each machine). The setting
  words leave every text, and no text calls a level Repaired. The wreck leaves the build menu.
- **New.** Placement in ruin rooms and the rare wreck on ordinary maps; the component's place in ruin rooms; the
  study on a building; the repair mechanism; the level-changed signal; the onboarding table and 19 more rows; one
  Mod Settings line for each machine; 137 pictures.
- **Leaves the mod when the forge is onboarded.** The projects `RM_WM_AlloyForgeRestoration` and
  `RM_WM_PlasteelAlloying`, the settings `alloyForgeProgressiveGate` and `plasteelAlloyEnabled`, and the patch
  `Patches/WreckedMachines_AlloyForgeGates.xml`. In the same landing: the Armoury adds its durasteel recipe to the
  forge's Kludged and Refurbished levels, and ResearchRetag stops naming the two projects (rule `R_neighbour_names`,
  check `C_forge_gates_gone`). The ticket `WM_PLASTEEL_RESTORE_FIX_FORGE_FORGETS` tests a switch that this removes;
  the builder drops it with that reason when the switch is gone. Nobody spends a live visit on it first.
- **Reused from neighbours, with no new C# in this mod where that is possible.** Cold Storage's route into Odyssey's
  ruin rooms (a prefab added to the room lists: `src/RimMandrake/ColdStorage/Patches/ColdStorage_AncientComplexLoot.xml`).
  The shared set-piece scatterer of Environmental Hazards (`RM_GenStep_PlacedSetPieces`) or a plain
  `GenStep_ScatterThings` def for the rare wreck. The shared scene runner and test hooks (`src/RimMandrake/_Shared/
  SceneRunner`, `TestHooks`) and the scene library (`src/RimMandrake/Utils/scene.py`) for the proof script.
- **Proof script.** `src/RimMandrake/WreckedMachines/validation.py` keeps its ten settings rows (they already assert a
  start, restore in a finally step and compare off with on). Its three spawn-and-inspect scenes and its four
  UNMEASURED rows are replaced by the scenes of `scenes.json`. Its `alloy_forge_gated` scene ends with the gates.

## order

Instruments and unknowns first, then one machine end to end, then the other 19.

1. **The spike "Study on a building"** (`models.md`; scene `sc_study_spike`). One wreck def with the base game's study
   comp, one project, one researcher, one live look. It decides rule `R_study_carrier` before anything leans on it.
2. **The bridge functions that the scenes need** (generic C# in the bridge, test first; the census of 2026-11-27 found
   them missing): run a ThingSetMakerDef or a TraderKindDef's stock N times and list the defs; place the install
   blueprint of a carried building; read the game's study record for a kind of thing; place the inputs of a factory
   process if `jawa/container_fill` does not reach the factory mod's processor. Found present and not owed:
   `jawa/architect_designator_visible`, `jawa/research_availability`, `jawa/ordered_job`, `jawa/designate_batch`,
   `jawa/thing_minify`, the gizmo reads, `jawa/power_net`, `jawa/pawn_thoughts`, `jawa/mod_settings_field`,
   `jawa/static_call`, `jawa/world_tile_map_generate`, `jawa/run_genstep`, `rimworld/save_game` and `load_game`,
   `play_zoom.shoot`, `LogTap`.
3. **The repair mechanism in the kernel, with its offline walk** (`models.md`, Repair state walk; check
   `C_repair_state_walk`). Red first on the three statements.
4. **The smelter end to end**: wreck with a carried form on any ground, study, two projects, the repair order, the
   Kludged and Refurbished rows of its onboarding table, the component gate, the text without setting words. The
   scenes of showcase 1 run on it. This is the flagship.
5. **Placement**: wrecks and the component in ruin rooms, the rare wreck on ordinary maps, the two placement switches.
6. **The power cell and the emanator**: Wrecked and Kludged pictures of their own, the wreck that gives nothing, the
   base game's hand-outs stopped while their lines are on. The scenes of showcase 3 run on them.
7. **The onboarding read against the donor** (`models.md`; check `C_onboarding_table_offline`), then the other 17
   factory machines in the order in which the campaign needs them, the alloy forge among the first because the
   Armoury's durasteel waits for it. Each machine: its table row, 8 pictures through the art pipeline and its judge,
   its two projects, its settings line. The scenes of showcase 2 fill as the machines land.
8. **The whole run** (`sc_whole_journey`, `sc_whole_second_order`) and the blind reader's rows
   (`sc_three_looks_rows`).

The stage-5 coverage judge added four acceptance scenes on 2026-11-27 (record decision `d_stage5_judge_fix_read`). They
join the order as follows, and the build item's acceptance test already counts their entry points.

- `sc_study_without_research_reinvented` runs with step 4, on a tier of its own: the small list without Research
  Reinvented. It reads the loaded mod list with `jawa/running_mods`.
- `sc_caravan_wreck_home` runs with step 4. Its instruments are `jawa/caravan_mass`, `jawa/caravan_form_load`,
  `jawa/world_tile_map_generate` and `jawa/install_blueprint`.
- `sc_every_machine_onboarded` runs with step 7 and grows with it: a machine is read once its onboarding has landed.
- `sc_cannery_tier` runs last in step 7, on a tier of its own: the small list plus Vanilla Cooking Expanded.
- The reachability read that the judge added to `sc_rare_wreck_ordinary_map` (step 5) uses `jawa/reach_edge`.

Each of the two tiers serves one scene. `version/small_list.json` allows the first ("Tests may run on a smaller tier
of their own"), and `floor.json` (line `test_isolation`) names the second. His walk and every other scene stay on the
mod's small list.

The old walk file `design/validation_walks/RimMandrake/WreckedMachines.md` describes the mod before this design. Four
of its north-star lines judge a reading that the root replaced. The builder rewrites the walk to the bars of 0.1.0
when the smelter is end to end (step 4), and the Conductor re-validates its north star in that sitting (CLAUDE.md,
North-star validation). Until then `tree.json` cites `root.md`, not the walk.

## build item filed at this stage

`RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL`: write the entry points of `scenes.json` in the
mod's proof script, each with its asserted start and its control, and the bridge functions of step 2 that they need.
Every acceptance and interaction scene names this item as `entry_point_item`. A reset is the harness's job and is not
part of the item.

Acceptance test (fails on the base: every entry point but the link-tag selftest is missing; passes with 0 missing):

```
python3 -c "import json,sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import designer_stage as D; s=json.load(open('design/concepts/WreckedMachines/scenes.json')); m=[x['id'] for x in s['scenes'] if x.get('kind')!='exploration' and not D.entry_point_exists('.', x.get('entry_point'))]; print('missing', len(m), m); sys.exit(1 if m else 0)"
```

The test shows that the entry points exist. That each scene truly asserts its start and has its control is read by
the tester at the mod's first in-game visit, scene by scene, against `scenes.json`.

No other ticket is filed. The changes to the built mod are the bars' own work, in the mod's folder. The work for
later versions is in `version/next_version/README.md`.

## risks

- **Study on a building does not behave** (the one `unknown` meeting). Then the build writes a study job of its own.
  The bar does not move; rule `R_study_carrier` does. The spike is first so that this costs one look and not a
  rebuild.
- **The repair mechanism is the largest new code.** Three designs are below. All three must keep the machine's
  identity on a level change: its power connection, its facing, its place in a stockpile filter or bill list where the
  donor has one. The offline walk reads the logic; `sc_repair_on_machine` reads the identity.
- **Ground.** A wreck on a plain floor, at home or in its ruin, cannot be repaired until factory floor is under it.
  Read from the game's source on 2026-11-27 (`GenConstruct.CanPlaceBlueprintOver`, through RimSage) and from the
  factory mod's `Terrain_Floors.xml`, and not yet seen in play: the game accepts a floor under a standing building
  only when the building names no ground need or the new floor gives that need, and the factory floor gives one kind
  of ground only, its own. So the wreck's def names no ground need of the base game's kind (rule `R_ground`); a wreck
  def that named Heavy ground could neither get factory floor laid under it nor be installed on factory floor.
  `sc_repair_needs_ground` reads both ways in play. If the game refuses in play what its source allows, rule
  `R_ground` is attacked: the alternative is that a wreck placed by the mod brings a patch of ancient factory floor
  with it and keeps the donor's rule at every level.
- **Art is most of the work**: 136 pictures for 17 machines, 4 for the two carried machines and 1 for the component.
  A machine enters the onboarded set only when its pictures pass the art judge. Until then the machine has no line
  in Mod Settings and is the factory mod's ordinary machine, so no machine is ancient with a borrowed picture during
  the build. Every line that exists ships on. 0.1.0 passes only with all 20 machines in the set (check
  `C_onboarded_set`). That is a build rule of this plan, and it keeps bar `levels_told_apart` true for every
  ancient machine.
- **The base game's hand-outs** (call B of turn 5). Odyssey, Ideology and Anomaly name the two base-game machines in
  loot and reward lists by defName. A patch that matches nothing logs nothing, so `sc_no_handouts` reads the
  generators' output and not the absence of an error.
- **Research Reinvented on top of the base game's study.** The small list holds it. If two study offers on one wreck
  confuse a player, the mod's own Research Reinvented defs go (they are a convenience; the base game's study is the
  design).
- **Neighbours.** Cold Storage reads `RatioFor`, the level extension and the place rule by reflection. The place rule
  goes, so Cold Storage's lockers change in the same landing or keep a thin copy of the name (check
  `C_neighbour_names`; rule `R_neighbour_names`).
- **The whole run is long.** It is two machines through two repairs with real studies. If one visit cannot afford
  it, it splits at its mid-way save (the scene says so). No bar asks for a season.
- **His reaction to the first look is not on the ledger.** A word from him on the 9 captures reopens stage 2.

## three designs for the repair on the machine (the builder's choice)

The bar says what the player sees. These are three ways to build it; the plan recommends the first.

1. **A repair record on the machine and a job of this mod.** A comp on each level holds the order, the delivered
   materials and the work done. A work giver hauls to the machine and works at it. On completion the mod swaps the
   def in place and carries the identity over. Cancel returns the materials from the comp. For: every statement of
   the bar is one field of one record, the record lives in the kernel and walks offline, and nothing depends on how
   the base game treats blueprints. Against: the most new C# (a comp, two jobs, a gizmo, the swap).
2. **A frame of this mod's own that keeps the machine.** The repair is a blueprint and frame placed on the machine's
   own cells that does not wipe what it stands on. For: the base game's hauling, work and cancel come free, and the
   player reads a familiar frame. Against: the base game's spawn-wipe and construction-blocking rules must be patched
   (read through RimSage on 2026-11-27: `GenSpawn.SpawningWipes`, `GenConstruct.BlocksConstruction`), and a frame drawn
   over the wreck may hide it, which the bar forbids.
3. **The base game's replace-by-tag, patched to put the lower machine back on cancel.** The smallest change to the
   built mod. Against: between the two steps no machine stands there, so "stays in sight" is false in every repair;
   the first look already refused this reading. It is listed so that nobody takes it by default.

## offline simulation

Yes, for two parts; no for the rest.

- **Yes: the repair state machine.** It covers every state of a machine under repair (level x study x project x
  order x ground x component) and every event (order, cancel, deliver, work, uninstall, destroy, save and load, the
  machine's line off and on), by visiting every reachable pair and by seeded event strings. It leaves out colonist
  jobs and paths, the base game's study comp, placement and pictures. Form: the shipped code, the Verse-free kernel,
  against a fake game, as the existing fuzz already runs it. It pays because the logic is a state machine with many
  cases and each live reading of one case costs a staged scene with a colonist and the clock. Detail: `models.md`,
  Repair state walk.
- **Yes: the onboarding table against the donor's defs.** It covers all 20 rows, with and without Vanilla Cooking
  Expanded: the Kludged list is a part that is not empty, the Refurbished list is the whole. It leaves out whether
  the part is useful and what the C# changes at startup. Form: an offline read of data with the existing patch
  interpreter; one live read of two machines checks it. Detail: `models.md`, Onboarding table against the donor.
- **No: study, carrying, placement and the pictures.** Each is the game's own machinery (a job on a building, the
  uninstall chain, map generation, the renderer), and a fake of it would be a copy that proves only itself. One cheap
  live look decides each.

## what the mod adds on every map, and what holds it back

`GUIDING_PRINCIPLES.md` entries 1, 3 and 5.

- **Conditions, not biomes.** Placement reads whether a ruin room or open ground exists. Repair, study and the levels
  read the machine, its research and its ground. Nothing reads a biome.
- **Load on every map.** Reading: one wreck now and then, and 40 research projects on a tab of their own. Chores:
  none that the player does not choose; a wreck that is ignored asks for nothing. Tick cost: no map component that
  runs each tick; a repaired machine ticks as its donor does; one repair record exists only while a repair is under
  way; the placement step runs once when a map is made.
- **What holds it back, in the world.** Nothing in the mod spreads or grows. The number of working ancient machines
  in a colony is held by what the player can find: wrecks in ruins, and one Ancient Component for each last repair.
  The player fights that limit by going to more ruins. No hidden count caps it.

## the showcase set

1. `smelter_comes_home`, the flagship (a delegated pick, CONDUCTOR:1795774540053514047; he can change it): found in a
   ruin, carried home, studied, repaired twice.
2. `ancient_factory_floor`: the Factory tab without its machines, the rows of three looks, the forge that gives
   plasteel only when Refurbished.
3. `relics_in_the_house`: the power cell and the emanator at each level beside the base game's own, and the settings
   line that gives one back.

Covered by ordinary checks (`coverage_rest`): the draw-in tags on wrecks (an offline read), the level-changed signal
(the repair scene's listener), and the two rules outside the promise (their regression readings).
