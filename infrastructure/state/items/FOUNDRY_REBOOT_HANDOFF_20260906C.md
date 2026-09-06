# FOUNDRY_REBOOT_HANDOFF_20260906C — READ FIRST on wake (evening session, 2026-09-06)

Follows `FOUNDRY_REBOOT_HANDOFF_20260906B`. Owner-requested agent reboot. Everything
below is committed and pushed unless a line says otherwise. **Game/bridge state at
wrap is in the last section — read it before touching the game.**

## The big thread: the map generator (owner's brief, the whole day)

`design/RimMandrake/map_content_injection_research.md` is the doc; §8 holds the
rulings, §9 the reviewed plan, §5.7/§5.8 the live proofs. Owner's three rulings that
bind everything: (1) the goal is a GENERATOR — the 44 hand-authored maps are
training/comparator data, never shipped content; (2) corpus statistics are
calibration + regression only, never acceptance — his eye on a comparator sheet is
the only acceptance; (3) *"Do both, accept they differ at first, then improve the
painter until they converge. Keep iterating until we get great results."*

**Built and proven today (all closed):**
- `LANDFORM_RECIPE_ROUNDTRIP_1` — Geological Landforms loads and renders a landform
  file we wrote (log: `Landforms: RUT_ProbePlateau`).
- `TERRAIN_GRID_RENDERER_1` — `rimbench/render_terrain.py`, grid→PNG, sheet mode,
  names palette misses (`unmatched_names=`).
- `CORPUS_MAP_STATISTICS_1` — `rimbench/corpus_stats.py`, 44 maps, hash-only;
  perimeter/area is flat across size+version (2.62-3.06) = the calibration target;
  chokepoint proxy is degenerate (filed `CORPUS_STATS_VANILLA_CONTROLS_1`).
- `GL_GRAPH_EMITTER_1` — `rimbench/gl_emit.py` writes GL recipes; live proof
  `Landforms: RUT_EmitterPlateau`. Now also `--from <any shipped landform>
  --rotate --freq-scale --topology`. Schema: `research/RimMandrake/reference/
  gl_landform_schema.md` (`gl_schema_census.py`).
- Design: `design/RimMandrake/map_generator_chooser_spec.md` (Fable; PLAN schema,
  11 rules, 5 example plans) — proposal, owner has not read it.

**In progress (doing):**
- `MACRO_GENERATOR_V0_1` — `rimbench/mapgen_v0.py`: chooser/plan/validate/gates
  PASS; the owner has NOT yet marked keep/cut on a sheet (item's own bar).
- `MAPGEN_PAINTER_V1_1` — `rimbench/mapgen_paint.py`; v1 sheet
  `Transient/mapgen_v1/comparator_sheet.png`. FOUNDRY grade: diagram→sketch, but
  uniform salt-and-pepper speckle, no large coherent regions. Next round: low-
  frequency region structure first, speckle only at boundaries.
- `MAPGEN_GL_SHEET_1` — `rimbench/gl_sheet_run.sh` drives 8 restart+quicktest
  cycles; recipes `Transient/mapgen_gl/RUT_Gen_0[1-8].xml` (Canyon×4, Sinkhole×2,
  Crater, LoneMountain), shots to `Transient/mapgen_gl/shots/`. Three driver
  defects found and fixed today (quicktest fired before the menu was live;
  python.exe misreading `/mnt/d` as `D:\mnt\d`; Topology `CliffValley`/
  `CliffAllSides` never matching a quicktest tile → `--topology Any`). **Result of
  the final run: see the last section.**
- `MAPGEN_CONVERGENCE_LOOP_1` — the standing iteration; round table lives in its
  item file (empty until the first painter-vs-GL sheet exists).
- Filed, ready: `GL_EMITTER_OBJECT_GAP_1` (14/44 landforms rebuild one `<Object>`
  short — coast/river family, Gorge, Valley; make the selftest rebuild all 44),
  `UNUSED_MUTATORS_WORLD_ASSIGNMENT_1` (owner: put the ~290 unused mutators/GL
  landforms on the frozen world; zero `GL_*` there today).

**Traps learned today (also in LESSONS_INBOX):** GL logs `Caught exception while
loading landform from file …` then `N landforms … 0 are custom` — grep for the
exception whenever the custom count reads 0. `start_debug_game_ready` is a silent
no-op from inside a loaded game (call `go_to_main_menu` first) and does nothing if
fired within ~5 s of the bridge token. A custom landform gets no `TileMutatorDef`;
GL picks it by `worldTileReq` + `Commonness` only. A landform at commonness 1 left
in `Config\CustomLandforms-v1\` HIJACKS the owner's real world — always remove it.

## Code review loop (DIRTY_CODE_REVIEW_STANDING_LOOP_1) — 100+ files this session

Marked clean: Utils (5 diff), rimbench (3 new + gl_emit pending), UtinniPatches (6),
RaidRedesigner (8, 1 real fix), Ninefold (9), tooling scripts (5), Aftermath (16),
SWBestiary (15, 5 small fixes), VaultDungeons (10), StructureInjectionsRUT (18),
Armoury (3), RustChrome/DesertFixtures/AftermathRites/AshkarrFlora/
AshkarrWeatherSuite/MenuShell/FluidCanals/bridgetools (28), UtinniShell meta.xml,
`code_review_status.py` (Opus: prune race fixed; CLAUDE.md contract corrected to
content-hash), `deploy_custom_mods.py` (Opus: 5 defects fixed + my own regression
caught by a diff review: `--pull` tuple).

**Owner-requested reviews answered:** `JawaBenchSocietyTools.cs` (Opus: 7 fixes
committed `33e2e681` — **NOT BUILT**; companion DLL builds only with the game
closed: `taskkill` → `python.exe src/RimMandrake/bridgetools/build.py --gm --apply`
per the rimbridge-companion skill — then live-prove `force=` on `settlement_remove`
mode=map); `VehicleFuelPatches.cs` (Opus: unfiltered patch hits every VF vehicle —
`VEHICLE_FUEL_PATCH_UNFILTERED_1`, **owner ruling needed**; deployed DLL predates
the repo build); vaporators (fix present; absorbed file deployed against its own
header while donor kotorcore is active — dup defName risk noted on
`MOISTURE_VAPORATOR_WALL_CLIP_1`); JawaPawnFlavor (all 11 clean).

**Left DIRTY on purpose:** `Ninefold/Patch_GravshipLaunched.cs`
(`NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1`), `UtinniPatches/AnimalBiomeDuplicates_
Generated.xml` (hand-edited GENERATED file — regenerate), `loadsweep/sweep_load.sh`
(minor), `Oracle/About/About.xml` (superseded HTTP design, ORACLE_EXPERIMENT_SPIKE_1
owns), the 8 Armoury absorbed files with missing textures
(`KOTORCORE_ABSORPTION_MISSING_TEXTURES_1`), `VehicleFuelPatches.cs` (reopened),
`gl_emit.py` (edited after its review), `mapgen_v0.py`/`mapgen_paint.py` (new).

## RED review (owner: "review all RED items") — 16 open bug items, all verified

CLOSED: `ARMOURY_SWMODS_DONOR_GAP_1` (fix had landed 09-04, `94f8c6a9`).
UNBLOCKED: `ARMOURY_MELEEPOWER_STALE_1` (its blocker was that close; ⚠️
`gen_armoury_patch.py` has no dry-run and overwrites the committed XML).
KEEP, verified real: `ARMOURY_LEATHER_GEN_DESYNC_1`, `PAWNFLAVOR_MEGAFAUNA_GEN_
DESYNC_1` (both wait on the post-retirement def-dump refresh), `CODEX_WRAPPER_
HARVEST_FIX_1`, `KOTORCORE_ABSORPTION_MISSING_TEXTURES_1` (16 errors not 13; donor
never shipped 3 of the textures), `TILEGEN_SILENT_REUSE_1`, `GL_EMITTER_OBJECT_
GAP_1`, `NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1`, `STRUCTUREINJ_RUT_TEMPLATE_
DEFECTS_1`, `VEHICLE_FUEL_PATCH_UNFILTERED_1`, `MOISTURE_VAPORATOR_WALL_CLIP_1`.
PARTIAL: `NINEFOLD_MISSING_EVENT_HOOKS_1` (hooks exist; live proof owed),
`KOTORWEAPONS_ABSORPTION_DANGLING_REFS_1` (two of its claims corrected in a note:
mininglaser IS defined; kneerocket ammoDef is kotorcore's).
FLAGGED: `HELIX_TELLUROX_SHELL_LOAD_CRASH_1` — the crash string reproduces in logs
where HelixTellurox is not loaded at all; attribution undermined.

## Owner rulings recorded today (research doc §8)

#6 generator not transplant · #7 statistics calibration/regression only · #8 §9.3
ruled "yes, go" · #9 both terrain routes, converge, iterate until great.
Open ruling owed: `VEHICLE_FUEL_PATCH_UNFILTERED_1` (intended or filter?).

## Process notes for the next FOUNDRY

- 5-6 agents in flight is the working max; `pkill -f <script>` kills your own shell
  (kill by PID); `index.lock` collisions with BENCH are constant — wait-loop, never
  remove the lock.
- One of my `./game … up` stamps was WRONG for a few minutes (launched on the full
  list by mistake); corrected in the ledger. Check `ModsConfig` li count before
  every launch.
- Subagents return verdicts; the parent runs mark-clean and reads every diff. A
  verifier ran `gen_armoury_patch.py` and had to `git checkout` — generators without
  `--out` are dangerous to hand to a delegate.

## Game / bridge / mod-list state at wrap

(filled in at wrap — see the final commit)
