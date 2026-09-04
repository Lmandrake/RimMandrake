# DIRTY_CODE_REVIEW_LOOP_RESTART_8

Continuity note for resuming the standing dirty-code-review loop (FOUNDRY),
ahead of an agent reboot the owner just called. Successor to
`DIRTY_CODE_REVIEW_LOOP_RESTART_7` — read that file for the fuller
narrative if you need it (6 layered updates now, chronological,
most-recent first). This file is the short version: what happened this
session, current numbers, and what to do first.

## Where things stand

`infrastructure/state/CODE_REVIEW_STATUS.json`: **509 clean entries**
(was 501 at the start of this session). `find src -name "*.cs" -o -name
"*.py"` (excluding obj/bin/__pycache__) currently counts **559** — a
different number from RESTART_7's 653, almost certainly reorg/split churn
elsewhere in the tree this session did not cause or trace; don't quote
653 vs 559 as a real drop without checking `git log` first.

**Game state: UP, full 589-mod list, bridge FREE.** Both a minimal-list
(21 mods) and a full-list restart happened this session — both landed
clean, no new Config errors, no assembly-load exceptions. `run_selftests.py`
is **35/35 clean** (down from 36 — see retirement below).

## What this session actually did, in order

1. **`ANOMALY_EXCEPTION_ACCESS_1` — CLOSED** (`4217267e`, fix follow-up
   `46cdec42`). Built `mandrake.rut.shipmemory`: the Memory-Core revelation
   gate (`discoveryPrerequisites`, not a research row) for the 7 Anomaly
   containment/bioferrite buildables per
   `design/Jawa/anomaly_exception_access_spec.md`. **Live-verified end to
   end** on the minimal list: patch lands clean (14/14 xpath hits), def
   read confirms `researchPrerequisites` gone + `discoveryPrerequisites`
   set on all seven, the reveal letter fires exactly on the
   `GameComponentTick` interval once Bioferrite is stockpiled, and the
   `HoldingPlatform` architect designator flips `visible:true` post-reveal.
   A same-session self-review caught and fixed one real bug (fallback
   letter's lookTarget was `null` instead of the Bioferrite stack) before
   marking the 6 new files clean.
2. **`ARMOURY_SOUND_PATHS_RSW_PREFIX_1` — CLOSED** (`925bb3d2`). Stripped
   the `RSW_` naming-migration prefix off 18 Armoury `clipPath`s (never
   touched the defNames — that prefix is correct there). Added
   **`selftest_sound_paths.py`**, a permanent guard: every `clipPath`
   across RimMandrake/RimStarWars/RimUtinni resolves to a real
   `.ogg`/`.wav`/`.mp3` (851 checked clean). This class of defect is
   invisible to `validate_patch.py` and a def dump — RimWorld resolves an
   AudioClip lazily on first play, so 17 of the 18 broken paths logged
   nothing until now.
3. **`RIVER_LINK_ORDER_SELFTEST_DRIFT_1` — CLOSED on the owner's direct
   word** (`467998c4`, owner-said override — FOUNDRY's item, owner closed
   it directly). `selftest_river_link_order.py` itself then **retired and
   deleted** (`bf41228e`) — its reconstruction approach could not keep up
   with hand-authoring on `world/ASHKARR_WORLDMAP_links.csv`, and rather
   than leave it permanently red it's gone. Note written into the item
   file per supersession doctrine. **If anyone wants a river-link check
   back, it needs rebuilding against the CURRENT csv, not resurrecting the
   deleted file** — that was exactly what this item found could not work.
4. **`codebase_health.py`** — added `research/` to `EXCLUDE_PREFIXES`
   (owner: AI-workforce study notes, not reviewed code). Committed
   `c0a28153`, republished the artifact.

## 🔑 One open thread from this session, not yet started

**`LOAD_CONFIG_ERROR_SWEEP_1` is proposed, unclaimed, and directly answers
a question the owner asked this session** ("how are we gonna validate all
that xml"): freeze the current 31 `Config error` / 5 cross-reference lines
as a baseline (`infrastructure/state/facts/config_error_baseline_2026-09-03.txt`
already exists — MEASURED, not yet frozen-as-baseline in the item's own
sense) so any FUTURE load only flags *new* errors instead of burying one
new defect in 36 known ones. 12 of the 31 are OUR Fire Ecology ash ladder
and are ACCEPTED, not defects — do not touch `AshLadder.xml` or
`ScorchableGround.xml`'s `burnedDef`/`Flammability`. The other 19 are
third-party (nine sign buildings, two pawnkind null-refs, two
`MissingMethodException` config errors, one missing AudioClip) plus 5
dangling cross-references to vanilla-count pseudo-defs
(`MealSimple10`/`Chemfuel60`/`Steel75`/`ComponentIndustrial12`/`Silver120`
— see `VANILLA_COUNT_PSEUDO_DEF_1`, a separate open bug item on the same
root cause). Full spec: `infrastructure/state/items/LOAD_CONFIG_ERROR_SWEEP_1.md`.

**Recommended: claim this next.** It is offline-workable (writing/deploying
patches for the third-party fixes and building the baseline-diff mechanism
needs no bridge), and the owner is already primed on why it matters.

## Recommended next steps, in order

1. **`LOAD_CONFIG_ERROR_SWEEP_1`** (above) — the freshest, owner-primed
   thread.
2. Everything RESTART_7 already flagged as still-open and NOT resolved
   this session: the bridgetools `--gm` deploy debt (BENCH landed this
   mid-session — verify it actually rode the full-list restart rather than
   assuming), `RimDefDump/JsonWriter.cs` (rides any normal restart, check
   `code_review_status.py check` for its current state), the 49
   deprioritized files across 11 inactive mods (**re-verify activity
   first** — `grep -io '<li>mandrake[^<]*</li>' "<ModsConfig.xml>"` — the
   list decays and this session changed the live list twice), and
   `rimflow/` (still deliberately deferred — ask the owner before opening
   it, per RESTART_7 and RESTART_6 both).
3. Otherwise: keep pulling `rimflow next --seat FOUNDRY` — 2 items waiting
   as of this handoff (`LOAD_CONFIG_ERROR_SWEEP_1`, and this file's own
   predecessor `DIRTY_CODE_REVIEW_LOOP_RESTART_7`, superseded by this one
   — supersede it in the ledger too if the render didn't already).

## Process notes worth carrying forward

- **Two live restarts in one session, both self-initiated** (FOUNDRY's
  standing 2026-09-02 authorization: bridge free → reboot, no asking).
  Minimal-list (21 mods, ~22s) to prove the new mod's XML and behavior
  live before committing to the expensive full-list restart (~15 min this
  time, faster than the usual ~25). **Copy the old `Player.log` out before
  each restart** — done both times this session
  (`Transient/Player_log_prev_before_shipmemory_verify.log`,
  `Transient/Player_log_shipmemory_minimal_verify.log`).
- **`step_game_ticks` only advances `GameComponentTick`'s own modulus
  check if the stepped range actually crosses a multiple of the
  interval.** Cost real time this session: stepped 600 ticks from tick 1
  to 601 expecting a 600-tick interval check to fire — it does fire
  in-range, but a *second* mistake (Bioferrite spawned loose, not in a
  stockpile) meant `resourceCounter.GetCount` legitimately returned 0
  (`ResourceCounter.UpdateResourceCounts` only counts things inside a
  `SlotGroup` — a raw stack on open ground is invisible to it). Fixed by
  creating a real stockpile zone (`jawa/map_zones` `createZone`) before
  spawning. **This is a live-testing methodology trap, not a
  RimBridge/mod bug** — worth remembering before assuming a fallback
  trigger is broken.
- **`jawa/build_check` (`CanPlaceBlueprintAt`/`CanSpawnAt`) does NOT test
  the architect-menu visibility gate** (`Designator_Build.Visible`,
  `discoveryPrerequisites`/research/monolith gates). It tests whether a
  placement would be physically valid if attempted, which is a completely
  different check. Use `rimworld/list_architect_designators`
  (`includeHidden: true` to see the full picture, the `visible` field
  per-designator is the real signal) to test a reveal/discovery gate live.
- **`rimworld/start_debug_game_ready` really does exceed the 30s client
  timeout and succeed server-side anyway** (traps.md was right) — the
  client call raised an exception, a fresh connection right after found
  the map already ready.
- **A background `Bash` command piped through `| tail -N` reports the
  PIPELINE's exit code, not the piped command's** — cost one wasted
  ~110s wait early this session (a `timeout 110 codebase_health_publish.py
  --force | tail -30` looked like a clean exit-0 success while the
  `timeout` had actually killed the underlying script mid-run). Don't
  pipe a long-running background command through `tail` if you need its
  real exit status; use `run_in_background` and read the output file, or
  redirect to a file and `tail` that separately.
- **`codebase_health.py` and its `_publish.py` wrapper take 2–4+ minutes**
  on the current file count — routinely exceeds the tool's own 120s
  default foreground timeout. Always launch with `run_in_background:
  true` for these, never a bare foreground call.
