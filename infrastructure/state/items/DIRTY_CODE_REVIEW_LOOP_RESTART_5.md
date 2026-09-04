# DIRTY_CODE_REVIEW_LOOP_RESTART_5

**Superseded by `DIRTY_CODE_REVIEW_LOOP_RESTART_6`.**

Continuity note for resuming the standing dirty-code-review loop (FOUNDRY).
Successor to `DIRTY_CODE_REVIEW_LOOP_RESTART_4` (resumed this session,
closed below). This session also cleared the entire immediately-offered
FOUNDRY queue and did a live bridge session — see the non-review section at
the bottom, it matters for what to do first on wake.

## Code-review state at handoff

`infrastructure/state/CODE_REVIEW_STATUS.json`: **311 clean entries** (was
296 at the last restart). 656 `.cs`/`.py` files total under `src/` — still
well under half clean; explicitly multi-session, never claim it's finished.

This session's waves (12 files, 3 waves of 4, all fanned out as parallel
subagents — sonnet for workaday single-mod/tool files, no opus needed this
round since nothing this session's files touched was central/live-companion
tier):

- **`ashkarr_paint.py`** — stale `--write` docstring (there is no `--write`
  flag; a bare invocation always writes) + an unguarded hardcoded
  `basin_of==0`/`sea_id==0` meaning "the Scald" (added a tripwire assertion).
- **`world_hydro.py`** — real bug: lake-terminus classification checked the
  wrong tile (`lake[term]` instead of `lake[nxt]`), silently misclassifying
  every lake-terminated river system as "land" in the printed audit line.
  Also removed a dead `if False` branch.
- **`vivify_world.py`** — docstring falsely claimed `--live` measures
  `river_flow`; RimWorld stores no flow scalar anywhere, so it's always
  CARRIED, never MEASURED.
- **`shipbuild.py`** — real bug, file was **completely non-functional**:
  loaders pointed at `mapsynth/` instead of `mapsynth/runs/`, where the
  generated artifacts actually live. `--selftest` couldn't even start;
  fixed, now 44/44 pass.
- **`build_designs.py`**, **`gen_turret_doctrine.py`**, **`gen_armoury_patch.py`**
  (re-confirmed clean), **`VehicleIonPatches.cs`**, **`Building_OpenPit.cs`**,
  **`ColonyVisibilityRaidPatch.cs`**, **`RuthlessPursuingMechanoids.cs`**,
  **`DefReflector.cs`**, **`worldmap.py`** — see commit messages for detail;
  three of these had real bugs fixed:
  - `RuthlessPursuingMechanoids.cs`: non-first-period raid/warning timer
    rolls had no floor (unlike the first-period branch) — a
    variance-≥-mean scenario-editor setting could schedule a timer at or
    before "now", permanently stalling that map's raid/warning letter.
    **Severity note**: this is a live gameplay-breaking bug fixed and
    deployed, worth flagging to the owner if raids ever seem to stop.
  - `DefReflector.cs`: 3 defects in the "dump loses more than it should"
    family (unguarded `FieldInfo.FieldType` resolution costing a whole
    def-type file on one bad field; the `IDictionary` branch missing the
    try/catch + cap its sibling has; `path.RemoveAt` not in a `finally`,
    corrupting the cycle guard after any escape).
  - `worldmap.py`: the landmark-parsing regex silently dropped any `<li>`
    with a trailing field before `</li>` and then misaligned every
    subsequent landmark's name via `zip()` — hit 4 of 6 real `.rws` files
    checked, corrupting landmark identity, not just losing entries.
- **`ashkarr_settle.py`** — reviewed, correctly left DIRTY: the file's own
  header already documents 4 places it's stale relative to a 2026-08-24
  owner ruling (Hutt "palaces" subset, organics-distance gating, a barren
  exemption region, and — most concerning — re-running its road-laying could
  recreate 91 road edges into Tusken/Deep Desert Tribes holdings that were
  deliberately removed). Needs the owner's eye on the actual world map
  before any of those four get touched; not a hidden bug, a known blocker.

Everything through `01dcfe30` is committed and pushed to `origin/main`.

## Doctrine, unchanged from RESTART_4 — still the process

Check reachability before reviewing. Fix ≠ clean. Subagents `mark-clean`,
never commit `CODE_REVIEW_STATUS.json` — the coordinator does, once per
wave, after a fresh `git pull --rebase` (stash `codebase_health_last.json`
separately if it's flapped — it's never FOUNDRY's to commit but still blocks
a rebase). Central/live-companion files get `model: opus`; workaday tool
files run fine at `sonnet`. Every `Agent` call needs an explicit `model`.
A C# fix is not real until rebuilt (`dotnet.exe build ... -c Release`,
Windows-native, `D:\...` path form) and deployed
(`deploy_custom_mods.py --mod <name> --apply`) — do this in the same wave,
game must be down for the DLL write.

## Next-session priority order

1. **Keep broadening beyond bridgetools/rimflow/WeatherSuite** (WeatherSuite
   mods confirmed NOT currently active in the live 589-mod list — skip
   reviewing them until they're enabled, per the reachability doctrine).
   Same method: `python3 -c "import json; print(len(json.load(open('infrastructure/state/CODE_REVIEW_STATUS.json'))))"`
   for a fast count, `code_review_status.py check <path>...` to confirm
   DIRTY/NO-ENTRY on candidates, size/centrality to pick the wave,
   reachability check before dispatch.
2. MapTools.cs 6th round (bridgetools, ~4 minor items from round 5), whenever
   bridgetools comes back up in rotation.
3. A real, unrelated finding surfaced in passing this session, not yet
   filed as its own item: `ColonyVisibilityRaidPatch.cs`'s reviewer flagged
   that the SIBLING file `GameComponent_ColonyVisibility.cs`'s
   `tileMemory` dictionary is keyed only by `PlanetTile.tileId`, not also
   `layerId` — two different planet layers sharing a tileId would collide.
   Worth filing and fixing whenever that file comes up for review.
4. Scale: 656 `.cs`/`.py` files under `src/`, 311 clean (~47%). Still
   explicitly multi-session per the owner — never claim it's finished.

## Non-review work this session — the queue is otherwise CLEARED

This was a long session. Beyond the code-review waves, it closed the entire
immediately-offered FOUNDRY queue:

- **`KOTOR_HEADBAND_DANGLING_REFS_1`** — closed. Root cause was an
  accidental file deletion in an unrelated commit (`8c946ec9`), not a
  Cherry-Picker cut as filed; restored from `66207f15`.
- **`SELFTEST_SWEEP_EXCEEDS_COMMIT_BUDGET_1`** + **`PARALLELIZE_SELFTEST_CLI_INTERNAL_1`**
  — closed. `run_selftests.py` (parallel runner, explicit N/N, never
  truncates) + `selftest_cli.py` internals (per-case scratch dirs, thread
  pool) took the full sweep from ~150s+ silently-truncating to a clean 28s.
  CLAUDE.md's Tools line now points at the new runner.
- **`LIGHTSABER_RECIPE_GATE_1`** — closed, live-verified. BENCH's own
  finding read a donor mod's raw XML instead of the resolved (patched)
  state; the actual gate was about to become a dangling research reference
  resolving to NO prerequisite at all post-cut, worse than filed. Fixed by
  removing `recipeUsers` on the shared abstract parent regardless of which
  research field ends up governing it. Confirmed live post-fix:
  `recipeUsers: null`.
- **`DEFDUMP_ONDEMAND_BRIDGE_UNREACHABLE_1`** — closed. New bridge tool
  `jawa/rimdefdump_run` (`JawaBenchDefDumpTools.cs`) calls
  `DefDumper.RunOnDemand` directly, bypassing both bridges' debug-action
  discovery surfaces entirely rather than repairing them. Live-verified: a
  fresh capture directory appeared with `modCount` matching the live
  session.
- **`FLUID_CANAL_DEBUG_SURFACE_1`** — left `doing`, substantial progress:
  identified the exact two-cache mechanism behind why some mods' debug
  actions never register (`GenTypes.AllTypes`, a lazily-cached list, vs.
  `GetTypeInAnyAssemblyRaw`, always fresh — explains why `FluidDef` resolves
  fine while its debug actions don't) and **disproved load-order as the
  cause with a live before/after experiment** (moved FluidCanals from
  position 19/20 to 14/20, identical symptom). Next step is a small
  reflection-probe bridge tool to read `allTypesCached`'s live contents —
  real, separate C# work, not more reading.
- **`VANILLA_COUNT_PSEUDO_DEF_1`** — left `doing`, substantial progress: the
  five dangling pseudo-defNames (`MealSimple10` etc.) are `ThingDefCountClass`
  parse failures from a defName+count concatenated with no space. Ruled out
  a static XML typo with an exhaustive scan (68,641 files, the ENTIRE
  Workshop library, zero hits) — the value is built at runtime by some
  mod's C#, not written in any XML. Narrows the search from "which mod's
  XML" to "which mod's compiled assembly", a harder, different search.

**On wake**: `rimflow next --seat FOUNDRY` will likely offer nothing fresh
immediately (only continuity items + whatever BENCH filed meanwhile) — check
`FLUID_CANAL_DEBUG_SURFACE_1` and `VANILLA_COUNT_PSEUDO_DEF_1` for
resumption if a bridge session is available, otherwise this review loop is
the default offline work. **Bridge is FREE and game is UP** (589-mod full
list) as of handoff — no restart needed to pick either back up immediately.
