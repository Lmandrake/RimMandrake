# 16 — Handoffs + lessons drain: progress (2026-10-11)

## 1. Handoff prune — DONE (PUBLISHED 6e78d4428)
git rm 85 handoffs with filename date < 2026-09-20 (none is a window's newest; 214 -> 128 files). CANON_REINTEGRATION_EXECUTION_1.md was
never a rimflow item and not in items/: moved to items/closed/. Harvest: every lesson section of the 85 (426 bullets; 133 already cited)
checked by three sonnet passes, results in 16_harvest_check_{0,1,2}.md; 28 still-true unrecorded lessons filed with --home.
harvest_pruned_pre0920.md is the extracted lesson text of the deleted files.

## 2. Orphaned pointers — DONE (PUBLISHED 44b8c5eeb)
Filed: VALIDATION_V2_IDENTITY_WIRE_READS_ZERO (was NORTHSTAR_VALIDATION_V2_RECORD_1), WASTELAND_CONTAGION_PROBE_FIVE_LOOSE_ENDS,
OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN, HOSE_PORT_QUESTIONS_ASK_SIX_ON_DEFAULTS (owner), ROT_REGEN_SHEET_FINISH_SIX_OPTIONS_SERVED (owner),
FLOWWORKS_LIQUID_KITS_WIRE_NO_REVIEW_ROW. Closed FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO at 67153b072 (its own NEXT).
Dropped (one check each): SCENE_HARNESS_1 (built: src/RimMandrake/Utils/scenes/scenelib.py), FLOWWORKS_PIT_CLAMP_LIVE_1 (FlowWorks full-list
live validation d08bca0b5), DEAD_OR_INERT_SETTINGS (filed as DEAD_OR_INERT_SETTINGS_1, built), CRACKEDLANDS_CHERRYPICKER_LASSO
(LASSO_CHERRYPICKER_REMOVAL_1 validated), RUT_ORPHAN_PNGS (both PNGs gone from src), FEVERWOOD_UNATTRIBUTED_XML (both files clean),
OLLOPOM_BEAUTY_DEPLOY (deployed per BENCH_HANDOFF_202610111523), JAWABENCH_DLL_GAME_COPY (10-11 live sessions ran the bridge; game-copy hash UNMEASURED).
Trap: land.sh with the ledger FILE path is refused by the ledger-writer hook (false positive); pass the directory.

## 3. Lessons curation — DONE (PUBLISHED 3e946befd)
34 duplicates merged into 14 (subagent wait-deadlock, sub-spawn/forks, verify subagent claims, pawn kill, map drift, mod-list restore,
composed deploy, stale DLL, full-tree deploy, artpipe camera words, sheet notes, biome two names, canon search controls, scratch placement).
38 deleted as stale or promoted: 8 worktree-era, 6 shared_sync.py (no caller; DEAD-FILE candidate), 32/172/278 fixed, 16/17/19/20/94/95/241
in CLAUDE.md, 155, 247/249/287 fixed, 33, 162, 47/69 (CLAUDE.md flyer ban + debug_process), 215 (live-review 8d), and the 5 rulings.
Kept 96: it says filed in CLAUDE.md but CLAUDE.md does not hold it. Git-cluster duplicate sets left for the git agent; harness lessons
already deleted by the proof-harness agent (33).
Owner rulings promoted verbatim: infrastructure/state/art_rulings/STANDING_ART_LAWS.md (realistic; palette variety; no geometric
placeholder selectable), abyss_cast_bible_2026-10-01.md §0 rows 18-19 (sibilant family + four yellow eyes), debug_process.md §4
(stop this live testing). Inbox now 235 lessons.

## 4. LESSONS_INBOX.md — DONE (PUBLISHED bef699a11)
Untracked (git rm --cached); .gitignore already listed it. handoff.py drain detection keeps working: the lessons/ dir is in .handoff.json's
lessons_file list and a deleted lesson file counts as a drain. Side effect: that untrack commit registers as a drain, so a default
--harvest now starts 2026-10-11; the 09-25..10-11 harvest is saved as harvest_20261011_since0925.md in this folder.

## 5. handoff.py (Lodestar) — DONE (Lodestar 8091cfd9, pushed)
dirty_cap (default 20) + per-top-dir count line; seat_family() merges *_REBOOT for newest protection; cull ages by filename stamp;
--harvest --out PATH (and help says it writes into the handoff dir); --owed (exit 1 when commits exist since this seat's newest handoff).
26 tests pass (PYTHONPATH=bin python3 -m unittest tests.test_handoff).

## 6. lessons.py — DONE (PUBLISHED 3be8e8315)
add --home (warning when missing; writes `home:` line), duplicate hint (Jaccard >= 0.35 vs first lines), `stats` verb; selftest_lessons.py OK.

## Published shas
