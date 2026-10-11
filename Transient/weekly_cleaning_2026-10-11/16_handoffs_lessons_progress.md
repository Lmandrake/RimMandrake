# 16 — Handoffs + lessons drain: progress (2026-10-11)

## 1. Handoff prune
pending

## 2. Orphaned pointers — DONE (PUBLISHED 44b8c5eeb)
Filed: VALIDATION_V2_IDENTITY_WIRE_READS_ZERO (was NORTHSTAR_VALIDATION_V2_RECORD_1), WASTELAND_CONTAGION_PROBE_FIVE_LOOSE_ENDS,
OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN, HOSE_PORT_QUESTIONS_ASK_SIX_ON_DEFAULTS (owner), ROT_REGEN_SHEET_FINISH_SIX_OPTIONS_SERVED (owner),
FLOWWORKS_LIQUID_KITS_WIRE_NO_REVIEW_ROW. Closed FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO at 67153b072 (its own NEXT).
Dropped (one check each): SCENE_HARNESS_1 (built: src/RimMandrake/Utils/scenes/scenelib.py), FLOWWORKS_PIT_CLAMP_LIVE_1 (FlowWorks full-list
live validation d08bca0b5), DEAD_OR_INERT_SETTINGS (filed as DEAD_OR_INERT_SETTINGS_1, built), CRACKEDLANDS_CHERRYPICKER_LASSO
(LASSO_CHERRYPICKER_REMOVAL_1 validated), RUT_ORPHAN_PNGS (both PNGs gone from src), FEVERWOOD_UNATTRIBUTED_XML (both files clean),
OLLOPOM_BEAUTY_DEPLOY (deployed per BENCH_HANDOFF_202610111523), JAWABENCH_DLL_GAME_COPY (10-11 live sessions ran the bridge; game-copy hash UNMEASURED).
Trap: land.sh with the ledger FILE path is refused by the ledger-writer hook (false positive); pass the directory.

## 3. Lessons curation
pending

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
