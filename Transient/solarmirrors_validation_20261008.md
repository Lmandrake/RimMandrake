# Solar Mirrors — offline validation (FOUNDRY, 2026-10-08)

Owner order: implement and run offline validation until no apparent bugs remain. Offline only (no bridge, game, deploy).
Subject: `src/RimMandrake/SolarMirrors` at `6765c094e`, plus `jawa/shade_probe` and the Long Shade patch.

## Pass 1 — full-file review

Read in full: the 9 mod `.cs` files, both kernels, `JawaBenchShadeProbeTools.cs`, every def/patch XML, the fuzz and
`validation.py`. Harmony targets checked against the decompiled 1.6 engine (RimSage): `GlowGrid.GroundGlowAt(IntVec3, bool
ignoreCavePlants, bool ignoreSky)` with private `map` (VERIFIED), `Building_WorkTable.UsableForBillsAfterFueling()` (VERIFIED;
an IBillGiver interface method, so WorkGiver_DoBill's call cannot be inlined), `Thing.AmbientTemperature` getter (VERIFIED),
`CompProperties_Power.basePowerConsumption` private float (VERIFIED). Placeholder texPaths all resolve (vanilla
SolarCollector/ElectricSmelter/Wall/Column/HorseshoesPin and Stillsand's RM_SunLance_Base, which ships inside the
mandrake.rm.biomes dependency). `ParentName="Wall"` resolves (vanilla `Name="Wall"`). `MapGenerator.GenerateMap` read:
biome `extraGenSteps` run, then `map.FinalizeInit()`, then `MapComponent.MapGenerated()`.

Defects (class, then what was wrong):

- **D1 MOD/save.** `RM_MapComponent_MirrorField` PostLoadInit did `mirrors.RemoveAll(null)` / `stones.RemoveAll(null)`. A
  configuration code is positional (mirror i = digit i), so after a field mirror was destroyed and the game reloaded,
  hints decoded with the wrong mirror count and named the wrong mirror/detent; a destroyed stone dropped from the list let
  the vault open with fewer stones, but only after a reload.
- **D2 MOD/puzzle bypass.** Field sun-stones are claimable and minifiable (RM_MirrorBase), and `CurrentlySolved` checked only
  `Spawned && Lit`: claim, uninstall, reinstall every stone under one mirror, vault opens, no puzzle.
- **D3 MOD/puzzle guarantee.** The solver counted a configuration solved only when every stone had light >= litAt, but the
  stones keep `Lit` down to unlitBelow (hysteresis, design §3.4). A stone lit in one configuration stays lit in a
  neighbouring one at 0.35-0.5, so the vault can latch in configurations the solver never counted, and the "nearest
  solution >= N re-aims" guarantee (setting 2-4, default 3) did not hold.
- **D4 MOD/mapgen.** The field is solved at GenStep 955; later steps (the Long Shade's sun graves at 960, the detent pins
  this step spawns afterwards, anything wiping plants) can change shade or blockers, and nothing re-checked.
- **D5 MOD/mapgen.** `Lay` and `SimulateLight` gated on `TrySun`, which multiplies the weather's SunFactor and, off a pinned
  sun, the clock: whether a field could be laid depended on the initial weather/time.
- **D6 HARNESS.** `jawa/shade_probe` appended a missing member once per mirror/receiver (200 copies of one miss).

Validation gaps found by reading the fuzz (not mod defects):

- **G1.** The field GENERATOR (candidate detents, intended solution, start pick, acceptance) lived in Verse code and was
  never fuzzed; only the solver primitives were.
- **G2.** Relay chains were barely exercised: "deep chains 3" across 5,500 pass/sequence cases.
- **G3.** No mutation reached the generator, the settings clamps, or the hysteresis lower bound.

Reviewed and found sound (no change): the beam walk, relay accounting, Publish/glow dirtying, receiver hysteresis, jobs
and reservations, heliograph faction filter (same layer, non-hostile, humanlike), dazzle stat part, settings Scribe and
all-off, DefOf, def XML (no MayRequire on an Operation, Conditional-guarded patch, no dangling refs).
Minor, recorded not fixed: a failed field site leaves its cleared grass/filth cleared (trees are never cleared: TryPlan
needs standable cells); the design's "every mirror's interaction cell reachable along a survivable route" is not built.

## Validation strengthened

- **Generator extracted and fuzzed (G1).** `RM_MirrorFieldKernel.Generate` is the whole mapgen layout search behind delegates
  (candidates, apply, evaluate, rand); `RM_MirrorFieldBuilder.TryLayout` now calls it. Clamps moved to the kernel
  (`FieldMirrors/FieldMinReAims/FieldDetents`) so the fuzz sweeps out-of-range settings too.
- **`generate` family** (600 cases, `SelfTest/SolarMirrorsFieldFuzz.cs`): random sites (ancient-style 3x3 mirrors, stones,
  walls, roofs, random sun) with the real kernel pass as the evaluator. Independent oracles: every configuration re-lit by
  the fuzz's reference pass and classified by hand (strict/held); >= 1 strict solution; start neither solved nor held; every
  held configuration >= want jobs from the start; minReAims/minStrict equal the reference distances; PickStart called
  directly lands >= want from every held configuration; an exhaustive walk of every job order shorter than `want`, with the
  stones' hysteresis played by hand, never latches the vault; same seed -> same layout; attempts and evaluations bounded;
  clamps hold for every setting. Blind-checked: accepted 92, refused 473, held-only configurations 2,212, accepted with a
  negative chain setting 9, out-of-range settings 317, oversized spaces 35, early-latch walks 92.
- **`chain` family** (3,000 cases, G2): explicit relay chains vs the reference pass and invariants: 1,567 shots at depth >= 2
  (the random families together reached 3 before).
- **Red before green.** With the old solver behaviour put back (held set never recorded) the new oracles fail at once:
  "held configuration 21 is 3 jobs from the start, want >= 4"; with every set/distance check disabled, the walk alone
  fails: "the vault latches after 1 jobs, fewer than the generator promised" (seed 64). D3 is a real early-open, not a
  theory.
- **Mutations: 42 -> 56** (`Utils/mutations_solarmirrors_fuzz.json`): held lower bound in PickStart and in Rebase, held set,
  LevelOf (2), each clamp (3), intended solution dropped, duplicate detents, raw depth setting (D7), attempt bound, start one
  job too near, relays capped at depth 1 (needs the chain family).
- **Static bars** (`validation.py`): every texPath resolves (own Textures, the mods folded into mandrake.rm.biomes per
  `Biomes.compose.json`, or a recorded vanilla set checked in RimSage) with a sanity probe; ParentName resolves; no
  `MayRequire` on a top-level Operation; guards for D1, D2, D3 (LevelOf), D4, D5, seal reference, G1 (Generate) and the
  kernel clamps. Each new bar was seen RED on a planted edit and restored (the D4 regex was first blind: it matched the
  method's own declaration; fixed to need the call).
- Walk `design/validation_walks/RimMandrake/SolarMirrors.md`: three anti-guessing notes (D3 ruled out as harmless, D2, the
  `MapGenerated` warning to watch for in a live log).

## Fixes and rebuild

- D1: lists never compacted (null slots kept); Hint/NextMove skip unspawned slots.
- D2: `stoneCells` saved; a stone counts only on its mapgen cell (hint count uses the same test).
- D3: kernel solves strict AND held sets (`EvaluateLevel`, `LevelOf`); start and minReAims use the held set, existence and
  hints the strict set; mapgen's evaluator reports the level (`StonesLevel`).
- D4: `RM_MapComponent_MirrorField.MapGenerated` re-solves the laid field with the same light after the whole map exists,
  restores the start, updates solutions/minReAims and logs a warning if it lost every solution or its start came closer.
- D5: `TrySun(..., ignoreWeather)`; mapgen and `SimulateLight` use the weather-free sun.
- D6: probe `missingMembers` de-duplicated, order kept.
- D7 (found by the new generator fuzz's settings sweep): mapgen passed the raw `maxChain` setting to the acceptance test, so
  a hand-edited setting below 0 refused every field; `Generate` now clamps it the way the pass does.
- Opened vault drops its destroyed seal reference.
- `winbuild.py SolarMirrors`: 0 warnings, 0 errors; JawaBench companion `build.py --gm` builds (plan only, not deployed).
- Published `3306b9a1a` (pass 1). The clone's worktree holds other agents' unstaged edits, so `pull --rebase` refused; the
  commit was replayed onto origin/main through a private index (worktree and their files untouched) and pushed as a
  fast-forward. The local branch still carries the pre-graft `e92ee8259`; a later `pull --rebase` drops it as identical.

## Reruns on the final kernel

- Fuzz: 14,300 cases, 0 failures (math 4000, pass 4000, sequence 1500, field 1200, generate 600, chain 3000), ~15 s.
- Mutations: **56/56 caught** (one run of #47 reported BUILD BROKEN, a staging flake; rerun alone: caught).
- `selftest_solarmirrors.py`: lint 0 ERROR 0 WARN, static PASS.
- `run_selftests.py`: 333/336. Not this mod: `artpipe/selftest_artpipe_state.py` (art ledger image read),
  `rimflow/selftest_items_glob_live.py` (ledger row), `modcheck/selftest.py` (240 s timeout). Both SolarMirrors selftests
  and walklint pass.

## Pass 2 — looking for a new kind of problem

An independent read-only reviewer (Opus, briefed with D1-D7 as excluded) checked engine APIs in RimSage and found four
NEW kinds, all confirmed against the code here and fixed:

- **P2-1 MOD/light provenance.** The latch credited any mirror light: one 10-wood signal mirror per stone opened the vault
  with zero re-aims, skipping the solver and the hints. Fix: `CurrentlySolved` also needs `FieldConfigurationSolves()` (the
  heliostats' detents encode to a stored strict solution). Sun-stones still answer any light for display (§3.2). So the
  colony now needs >= minStrict >= minReAims >= setting jobs. INTERPRETATION: design §3.4 never says colony mirrors may
  count; flag for the owner if he wants them to.
- **P2-2 MOD/night aim.** `CommitAim` with no incoming light fell back to a sun straight overhead, so a static mirror
  re-aimed at night threw wide all next day. Fix: `aimDeferred` (saved); the next sunlit pass sets the normal.
- **P2-3 MOD/range.** A held target is never range-checked after the targeter; a minified mirror reinstalled elsewhere kept
  throwing at its old cell at any distance. Fix: `PostSpawnSetup` (not on load, not ancient) drops an aim out of reach.
- **P2-4 MOD/mapgen cost.** Worst case 40 sites x 30 attempts x 729 light passes (~875k) with no cap. Fix:
  `maxEvaluations` (GenStep, 60,000, PROVISIONAL) shared by all sites, enforced inside `Generate` before a solve; fuzz
  oracle (random budgets, 52 budget stops) and mutation #56.
- Also: dead `RM_CompMirror.NormalFor` (state-mutating, no caller) removed. Reviewer note checked: "stone k is no mirror's
  detent" can only fail on accepted layouts but did catch mutation #50 (seed 82), so it is not blind. Unverified nit: the
  unclaimable brass pins may refuse blueprints on their 12-18 cells.

Offline instruments for P2-1..3 are static guards (Verse code, not kernel); each seen RED on a planted edit. Mutations
57/57 caught (#56 new).

## Pass 3 — the pass-2 fixes reviewed

A second independent reviewer found two defects the pass-2 fixes introduced and one older path:
- **P3-1** a shaded RELAY aimed at night resolved its normal for the sun (wrong beam all day). Now resolved before the pass
  only for a mirror standing in sun; a relay resolves after the pass from the beam that reached it (`r.inDir`).
- **P3-2** once the budget could not pay one solve, the remaining ~37 sites still spawned, recomputed shade twice and tore
  down. The site loop now stops at `budget < d^n`.
- **P3-3** a mirror landed by gravship (plain `GenSpawn.Spawn`, engine `GravshipPlacementUtility`) kept an absolute target
  on the new map whenever it happened to be in range. Aims now record `aimFrom`/`aimMapId` (saved); a mirror spawned
  anywhere else drops its aim (covers reinstall too; range check kept).
Each has a static guard seen RED on a planted edit. Rebuilt clean; fuzz 14,300/0; static PASS.

## Only a live run can prove

(pending)

## Pass 4 — fresh full read, no new kind

Read all 11 C# files, both kernels, the 5 def files, the patch, About, settings screen and the language file fresh (no
reviewer, no bridge). Checked: kernel acyclicity and relay order, hysteresis/held/strict sets, Generate budget, aim
provenance (aimFrom/aimMapId, aimDeferred), save/load of positional lists, mapgen order (engine MapGenerator: FinalizeInit
runs before MapGenerated, so Reverify reads a fresh shade grid; BiomeDef.extraGenSteps exists), Translate arity of all 108
keys against the language file (0 missing, 0 unused, every placeholder count matches), XML inheritance, patch xpaths.
Results: validation.py STATIC PASS (0), fuzz 14,300/0 (foreground, one run). No code changed, DLL untouched.
No new KIND of problem. One nit left unfixed on purpose: a hand-edited negative `heliostatPower` in the settings file makes
heliostats produce power (the slider is 50-500; no other setting can benefit from an out-of-range value). Same class as the
settings clamps already swept in pass 1, so it is not a new kind.
