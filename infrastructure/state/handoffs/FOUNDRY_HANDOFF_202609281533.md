# FOUNDRY_HANDOFF_202609281533 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202609280319`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

A full 11-item Chill biome wave (rename → fire ban → thermal engine → heated suit → garden
defense → 10 flora → thermal footprints → rime terraces → world crater → V-Wake verify →
drowned aurora → aurora surge) plus 9 other biome items closed this wave — **none of it is
deployed to the live Mods folder, and none of it has been watched in game.** Every "not
live-tested" note across ~20 closed items this session is real, not boilerplate: the game
was up the whole time (can't write DLLs while running), and reaching a real Chill-seabed
pocket map was judged not-cheap by every subagent that considered it. The next session's
first move should be a deliberate game-down window: deploy every touched mod
(TerminalBiomes, DivingInteraction, Stillsand, LongShade, FlowWorks, SeaShores,
LanternDeeps, StructureInjectionsRUT, PropaneLakeMechanics, UtinniPatches — `git log
cf05611..HEAD --stat` for the exact set), cold-load, and actually look at the Chill floor,
the sand busters, the Long Shade/Stillsand rosters. A wave this size with zero live
confirmation is the load-bearing risk to close next, not new content.

## What the owner should see

- **`STRANDED_DEFORMATION_DEFNAME_CLASH_1`** (filed, OWNER decision) — `RUT_StrandedDeformation`
  HediffDef exists twice (Miasma vs UtinniPatches, genuinely different defs), found by
  `BAROQUE_BIOMES_COMPOSE_1`'s collision sweep. Blocks Baroque Biomes Wave 1. Needs a human
  call on which survives — not something to auto-resolve.
- **`STILLSAND_RULED_CONTENT_1`** has a self-contradictory qorrax passage (item text lists it
  as buildable-now in one section, excludes it in another) — noted on the item, not resolved;
  whoever picks the Stillsand roster up next should re-read both sections before touching
  qorrax.
- Two shipped-code defects found and fixed on sight this session (Charter's "correctness
  outranks seat ownership"): `WarLabCraterMutation` was targeting a placeholder biome
  (`RUT_Wasteland`) instead of the real crater def now that it exists — retargeted. A stale
  doc comment in `PropaneLakeMechanics` claimed a dead method was load-bearing — corrected.
  Both are in the commit log if you want to see exactly what changed.

## What is half-done, and where it stops

- `GREYSEA_RULED_CONTENT_1` — 8 of 11 rulings landed (commit `7a09c160c`), explicitly
  left open and blocked; NEXT: check whether BENCH's `GREYSEA_SHIP_CRYSTALLISATION_1` /
  `DARKSEA_LIGHT_ATTRACTION_1` design has landed, then build Q10/Q11/Q12 (ship crust ladder,
  giant-lamp response) against it.
- `BAROQUE_BIOMES_WAVE1_JOIN_1` — filed, not started; NEXT: resolve
  `STRANDED_DEFORMATION_DEFNAME_CLASH_1` first (owner decision), then retarget the 3
  RimUtinni `MayRequire`s + 1 `FindMod` naming folded packageIds, delete the 12 now-stale
  standalone mod folders, and do the actual ModsConfig swap at a game-down window.
- `WARLAB_CRATER_ACCIDENTAL_TRIGGER_1` — filed, not started; NEXT: design the deliberate
  Route-1 arming mechanism (per `the_chill_warlab_routes_spec_2026-09-27.md`) and replace
  `RUT_WarLabReactorCore`'s unconditional destroy-hook with it.
- `RUSTCATHEDRAL_SETTINGS_DOUBLE_READ_BUG_1` — filed, not started; NEXT: fix
  `RM_RustCathedralMod`'s `GetSettings<T>()` called 3× on one Mod instance (pre-existing bug,
  found live during Baroque Biomes' wave-0 load-prove).
- `JAWA_MAP_INFO_BIOME_DIVERGE_DOCSTRING_WRONG_1` — filed, not started; NEXT: fix
  `jawa/map_info`'s tool description (claims map/tile biome "diverge after a live
  world_tile_set" — false per vanilla source, needs a DLL rebuild + its own commit).
- The whole Chill wave — see "one thing to carry forward" above; NEXT: deploy at a
  game-down window and live-verify.

## Traps learned

- Back-to-back commits in this shared tree hit `.git/index.lock` repeatedly this session —
  always self-resolved with a short retry, never a stale lock; watch for a push landing while
  the very next commit in the same sequence fails (filed: LESSONS_INBOX).
- A subagent's "this is unfiled" claim about a prerequisite item was wrong twice this
  session (`CHILL_WORLD_CRATER_1`'s feasibility question, `CHILL_GARDEN_DEFENSE_1`'s Q10-12
  successors) — both times the real items already existed under a different, non-obvious
  name; always `rimflow show`/grep the ledger yourself before trusting a "nothing exists for
  this" report (see: `queue-items-decay-verify-first` memory, same family).
- A subagent's own `About.xml` prose edit can break the file's XML with an unescaped `<li>`
  inside description text — `validate_patch.py`'s own clean-pass claim did not catch it
  (About.xml apparently isn't in its parse scope). Always independently `ET.parse()` every
  touched XML file before committing a subagent's work, not just trust its validator claim
  (filed: LESSONS_INBOX).

## Commits

```
3c95ccf3c rimflow: close CHILL_AURORA_SURGE_1 at d2ab077fa
d2ab077fa CHILL_AURORA_SURGE_1: surge storms, harvest or hide
61d3e053d rimflow: close CHILL_FLOOR_LIGHT_1 at 917dadfac
917dadfac CHILL_FLOOR_LIGHT_1: drowned aurora over bioluminescent points
aab49a1af rimflow: close CHILL_VWAKE_WIRING_VERIFY_1 at 5c82fe04a
5c82fe04a CHILL_VWAKE_WIRING_VERIFY_1: V-Wake pump agitation confirmed wired, correctly split
d42eba0aa rimflow: close CHILL_WORLD_CRATER_1 at 4c2ecaca1; file two follow-ups
5f0245e26 Fix: WarLabCraterMutation targeted RUT_Wasteland, a placeholder pre-dating RM_ChillCrater
4c2ecaca1 CHILL_WORLD_CRATER_1: the crater biome + swap feasibility verdict
aa0fc7abb rimflow: close CHILL_RIME_TERRACES_1 at c2c1ace03
c2c1ace03 CHILL_RIME_TERRACES_1: sparkling ice bedrock + Krellik-correlated terrace districts
a88c2452e rimflow: close CHILL_THERMAL_FOOTPRINTS_1 at 2684ac857
2684ac857 CHILL_THERMAL_FOOTPRINTS_1: warmth writes on the ice
7d1af2a67 rimflow: close CHILL_FLORA_BUILD_1 at 3815690b5
3815690b5 CHILL_FLORA_BUILD_1: the ten Chill plants + the hydrocarbon fuel chain
51de4ae4b rimflow: close CHILL_GARDEN_DEFENSE_1 at 0c11dd089
0c11dd089 CHILL_GARDEN_DEFENSE_1: the garden's tiered immune system
3f00541ef rimflow: close CHILL_HEATED_SUIT_1 at 5eaa306e4
5eaa306e4 CHILL_HEATED_SUIT_1: the heated EVA suit, one charge clock
905f24b73 rimflow: close CHILL_THERMAL_ENGINE_1 at d23e31584
... 48 more: git log --oneline cf05611..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed (HEAD at `3c95ccf3c` when this was written)

Uncommitted at wrap — **none of it is this session's FOUNDRY work** (everything closed this
session is committed and pushed, verified per-commit with `git merge-base --is-ancestor`,
not just an empty `git log origin/main..HEAD`). Categorized rather than itemized (~900 lines
of `git status`, mostly pre-existing):

- **Another window's concurrent uncommitted edits — do not touch, not FOUNDRY's:**
  `infrastructure/state/ledger/events/BENCH.jsonl`, `infrastructure/state/queue/BENCH.md`,
  7 `design/*.md`/`.json` files (BENCH's own design-doc propagation in progress),
  `src/RimMandrake/FeverWood/Defs/ThingDefs_Races/RM_Sekkulaath_Juvenile.xml`.
- **Live background processes' own continuous churn — not owned by any agent turn:**
  `Transient/codebase_health*.{html,json}` (auto-regenerated health dashboard),
  `infrastructure/dashboards/hub/data/health.json`,
  `infrastructure/state/codebase_health_last.json`,
  `infrastructure/artpipe/{registry,throughput}.jsonl`,
  `infrastructure/artpipe/daemon_run_20260927_derivefacings.log` (the artpipe daemon).
- **Artpipe daemon continuing to process jobs this session committed** — expected, not a
  defect: `infrastructure/artpipe/active/rm_chillauroracollector_v1.json` shows `AD` (I
  committed it in `active/`, the daemon has since moved it further); the 7 deleted
  `infrastructure/artpipe/pending/RM_{Oorrik,Ruukka,SandBusterMound}*.json` are the
  `SANDBUSTER_CASTES_BUILD_1` jobs I committed, now claimed out of `pending/` by the live
  daemon. Nobody needs to "fix" this — it's the daemon doing its job after the fact.
- **Pre-existing Transient/ scratch, confirmed predating this session** (screenshots,
  quota-failure manifests, one-off debug scripts, `ModsConfig` cold-load backups,
  `LanternDeeps_RUT` rescued assemblies, `firehawk_flight_probe.py`) — this exact set was
  already flagged "pre-existing, not mine" by this session's own wake-triage at the start;
  see `python3 ~/dev/Lodestar/bin/handoff.py --wake`'s output from this session's first turn,
  or just `git status --porcelain` and compare timestamps if in doubt.

If any of the above looks wrong to whoever wakes next (something here actually needs
attention), say so — this categorization is my honest read at wrap, not a claim that
nothing in that list ever matters.
