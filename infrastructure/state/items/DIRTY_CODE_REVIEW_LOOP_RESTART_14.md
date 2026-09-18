# DIRTY_CODE_REVIEW_LOOP_RESTART_14

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor
to `DIRTY_CODE_REVIEW_LOOP_RESTART_13` — read that file (and its own chain)
for fuller history. This file is the short version: what this session did,
current numbers, and what to do first.

## Where things stand

`infrastructure/state/CODE_REVIEW_STATUS.json`, freshly re-listed this
session: **2903 clean / 2942 tracked (98.7%)**, up from RESTART_13's
2897/2942. Re-run `list` fresh rather than trusting this number — it decays
fast on a shared four-seat worktree.

**39 files are DIRTY right now.** Notable clusters, still open:

- `src/RimMandrake/FlowWorks/*` (9 files) — `LIQUID_BOTTLE_LOOP_1` is STILL
  `doing` (re-verified this session via `rimflow show` — a tank v1 build
  landed mid-session, commit `52b9c584e`); leave this cluster alone until it
  closes.
- `src/RimStarWars/SWBestiary/*` (6 files) — `MLIE_FAUNA_ABSORPTION_1` is
  STILL `doing` (Pass 12 committed same day this session ran, 51 species
  remaining); confirmed via `rimflow show`. Do not touch, not even
  file-by-file, while this stays `doing`.
- `src/RimMandrake/Utils/handoff.py` / `selftest_handoff.py` — newly dirty
  this session, a SIBLING AGENT'S live in-progress rewrite (a bridge-holder
  substring-match fix, commit `2d48e8c5d`, plus further uncommitted work
  sitting in a stash — see the git note below). Not touched this session;
  do not review mid-edit.
- `src/RimMandrake/rimflow/model.py` — still deliberately deferred
  ("pending an owner ask").
- `design/Jawa/fauna/BiomeCast_Ashkarr.xml`, `src/RimUtinni/UtinniPatches/
  Patches/BiomeCast_Ashkarr.xml` — both still churning under
  `MLIE_FAUNA_ABSORPTION_1`'s active species ports (each species pass touches
  both copies); leave alone for the same reason as the SWBestiary cluster.

## What this session actually did

1. Re-ran `code_review_status.py list` fresh (45 dirty at start) and
   `check` on the specific next-picks named by RESTART_13. Confirmed
   `LIQUID_BOTTLE_LOOP_1` and `MLIE_FAUNA_ABSORPTION_1` both still `doing`
   via `rimflow show` — skipped FlowWorks/LiquidTypes and all of SWBestiary
   entirely, per the brief.
2. **`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml`** and
   **`.../Defs/TerrainDefs/RUT_TarMoat.xml`** — full reads. Verified the
   `RM_Churnmud` -> `RM_GreentideChurnmud` rename (RESTART_13's fix) is
   consistent everywhere it's referenced; verified `RUT_TarMoat`'s header
   claim that its texturePath reuses `RM_TarDeep`'s own real path
   (`Terrain/Surfaces/WaterDeepRamp`) against the actual FlowWorks def —
   true. defName uniqueness checked for all 3 new defNames (`RUT_Greentide`,
   `RUT_TarMoat`, `RUT_TarSpent`) — no collisions. No functional bugs.
   Marked clean.
3. **`src/RimMandrake/Utils/code_review_status.py`** — the tool itself,
   dirty since 2026-09-09, first standalone full-file review. Read all 896
   lines; ran its own `selftest_code_review_status.py` (passes, exercises
   mark-clean/check/reopen/migrate-hashes/prune/list/untracked end to end).
   No functional bugs found — the file's own inline comments already
   document several past bugs fixed in earlier sessions, all still correctly
   guarded against. Marked clean. **Caveat for whoever reads this next**: my
   first mark-clean attempt on this exact file recorded a hash that didn't
   match the file's real bytes moments later, even though `git diff` showed
   zero difference from HEAD both before and after — almost certainly a
   drvfs stale-read hitting `file_hash()`'s own `open().read()` mid-session
   (see CLAUDE.md's `drvfs-stale-reads-mimic-revert` note), not a real edit.
   Caught by re-running `check` immediately after `mark-clean` rather than
   trusting the printed confirmation; re-ran `mark-clean` a second time and
   it settled. **Worth doing after any `mark-clean` on this shared
   worktree**: immediately `check` the same path again before moving on.
4. **`src/RimMandrake/Utils/artpipe/*`** — 5 files (`artpiped.py` 2435
   lines, `artreg.py` 986, `common.py` 341, `fill_queue.py` 281,
   `selftest_artpipe.py` 2869). Full reads of all five. Cross-checked
   against a sibling agent's same-session fix to `artpiped.repair()` (a
   byte-comparison fallback for a duplicate-id collision stuck in
   `active/`, commit `02498a0a2`) — confirmed it's covered by two new,
   genuinely behavioural tests (`test_repair_discards_byte_identical_
   duplicate_id_collision`, `test_repair_leaves_differing_duplicate_id_
   collision_for_a_human`), both exercising the real fork (identical bytes
   discarded vs. differing bytes left for a human), not a namelist. Ran the
   full `selftest_artpipe.py` suite (all ~90 scenarios) end to end: all
   pass. No functional bugs found anywhere in the cluster — this code is
   already extremely defensively written, with almost every subtle
   correctness issue (drvfs stale rename races, retry-vs-summed wall clock,
   gemini budget reservation windows, channel-preserving exception
   fallbacks) already found and fixed in prior sessions, documented inline.
   One minor, non-blocking observation not worth reopening for: `artreg.
   render()` writes its HTML output via a plain `out_html.write_text(html)`
   rather than the atomic-write helper `render()`'s own JSON output uses
   (`common.atomic_write_json`) — a theoretical half-written-HTML read
   window for a single local viewer, functionally harmless. All 5 marked
   clean.

Total this session: **8 files reviewed and marked clean** (2 UtinniPatches
defs + code_review_status.py + 5 artpipe files), **0 functional bugs found**
(this was a "confirm it's still correct" pass, not a bug hunt — RESTART_13's
`RM_Churnmud` collision was the wave's real finding). `run_selftests.py`:
55/58 (3 failures — `selftest_art_checks.py` and `selftest_one_path_seam.py`
are the same 2 pre-existing failures RESTART_13 already flagged as unrelated;
`selftest_handoff.py` is NEW but is failing against a sibling agent's own
mid-edit `handoff.py` rewrite, not anything reviewed this session — confirmed
via `git status`/`git log` on that file before treating it as pre-existing
noise, not mine to fix).

**Git note for whoever's next**: pushing this session's commit required a
`git pull --rebase` (remote had advanced), and `pull --rebase`'s autostash
of OTHER agents' uncommitted working-tree changes (queue/BENCH.md,
queue/FOUNDRY.md, ledger/events.jsonl, artpipe/registry.jsonl,
artpipe/throughput.jsonl, ModsConfig.MINIMAL.xml, handoff.py/
selftest_handoff.py, and the codebase-health dashboard files) hit conflicts
on re-apply. Git left it as a labeled stash rather than writing conflict
markers into the tree (`git status`/`git grep` for `<<<<<<<` both confirmed
clean) — some non-conflicting entries (the health-dashboard regen files)
applied cleanly and now sit as ordinary uncommitted changes; the rest is
intact in the stash list, NOT dropped, NOT force-applied. This was left
alone rather than resolved — it is other agents' in-progress work, not code
this pass reviewed or understands the intent of, matching the precedent
already sitting in this repo's own stash list ("wip: concurrent agent
auto-generated files, held during rebase"). **The stash list is now 15+
entries deep** — worth a dedicated look by whoever next has a quiet moment
with the owner, since it keeps growing session over session rather than
ever being drained.

## Recommended next steps, in order

1. Re-verify `LIQUID_BOTTLE_LOOP_1` and `MLIE_FAUNA_ABSORPTION_1` before
   touching FlowWorks or SWBestiary — both were still `doing` this session;
   if either has closed, its cluster is fair game (FlowWorks: 9 files;
   SWBestiary: 6 files, plus the two `BiomeCast_Ashkarr.xml` copies it keeps
   touching).
2. `design/Jawa/worldbuilding/biomes/rosters/_consolidate.py`,
   `skills/generating-images/scripts/codex_image.py`,
   `src/DEPLOY_HOLD.txt` — smaller, standalone dirty files with no
   apparent active-item gate, good quick picks.
3. `src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviorsMod.cs`,
   `src/RimMandrake/EnvironmentalHazards/Source/
   RM_RootCausewayBiomeExtension.cs`, `src/RimMandrake/MovingDunes/Source/
   RimMandrake_MovingDunes.csproj` — check each is still live/reachable
   (importer, csproj membership) before spending a review.
4. `src/RimStarWars/Armoury/*` (2 files), `src/RimUtinni/PawnFlavor/*`
   (2 files), `src/RimUtinni/PyrelandsMechanics/About/About.xml`,
   `src/RimUtinni/RustCathedralHum/*`, `src/RimUtinni/UtinniPatches/Defs/
   BiomeDefs/RUT_TheRot.xml` — no known active-item gate found this
   session; worth a `rimflow show`-style check on whatever item last
   touched each before reviewing, same discipline as this session's
   Greentide/TarMoat pass.
5. `src/RimMandrake/Utils/gm_blackboard_shadow.py`,
   `src/RimMandrake/Utils/structure_roster_lint.py`,
   `src/RimMandrake/Utils/selftest_code_review_status.py` (this session
   reviewed the tool it tests, not this file itself — a natural next pick
   given the context is already warm) — standalone, no apparent gate.
6. Always re-run `code_review_status.py list` fresh at the start of the next
   session rather than trusting this file's 2903/2942 numbers, and
   `check` immediately after any `mark-clean` on this shared worktree (see
   the drvfs stale-read caveat above).
