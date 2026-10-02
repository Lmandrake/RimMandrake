# Git X2 history replay (2026-10-01)

Window: 3403 non-merge commits on origin/main, 2026-09-17..10-01 (14 days). Harness: scratchpad replay.py/ana.py.

Model: for commit C (parent P), author's base B = P~K (first-parent). Conflict = `git merge-tree --write-tree --merge-base=P B C`
(C cherry-picked onto the stale base; conflicts = C overlaps lines changed in B..P). Probe: constructed known conflict detected, control clean.

| K | commits | conflicted | after (a) union ledger+append md | after (c) also no generated (queue views, health, CODE_REVIEW_STATUS) |
|---|---|---|---|---|
| 1 | 3403 | 483 (14.2%) | 358 | 134 (3.9%) |
| 5 | 3403 | 1484 (43.6%) | 1214 | 463 (13.6%) |
| 20 | 3403 | 1975 (58.0%) | 1677 | 856 (25.2%) |

Conflicted commits by class (a commit may hit several), K=1 / 5 / 20:
- ledger jsonl: 298 / 962 / 1181
- queue/*.md views: 229 / 810 / 962
- LESSONS_INBOX/append md: 8 / 32 / 81
- health html/json: 2 / 22 / 64
- CODE_REVIEW_STATUS.json: 3 / 15 / 33
- DLL/.srchash: 20 / 71 / 119
- source (.cs/.py/.xml/csproj): 27 / 111 / 208
- other (docs, item md, dashboards): 106 / 352 / 649

(b) one-file-per-record for ledger/append md = same result as (a) (no cross-record conflicts). Queue views are the biggest
non-union class (FOUNDRY.md 738, BENCH.md 647 path-conflicts at K=5), and are what (c) removes.
Residual at K=5 is mostly docs/item md (505 path hits), DLLs+srchash (133), source (193); residual "other" also includes
generated-ish files my regex missed: items/DIRTY_CODE_REVIEW_STANDING_LOOP_1.md (62), state/codebase_health_last.json (30),
dashboards/hub/data/health.json (23) -> true residual is somewhat lower.
Caveat: ledger/events.jsonl (frozen pre-shard file, 375 K=5 hits) inflates ledger counts for the pre-2026-09-23 part of the window.

Activity: 3403 commits / 15 calendar days (peak 488 on 09-24, 279 on 10-01). Authors: Lmandrake 3264, mandrake 137, Lukas Mandrake 2
(seat not distinguishable by author). Subject patterns: 1909 free-form, rimflow 258+19, Ledger/ledger sync ~475, chore 32, LESSONS_INBOX 18,
CODE_REVIEW_STATUS/code_review_status 27, FOUNDRY handoff 12. 1218 commits (36%) touch a ledger jsonl; 212 touch generated artifacts only.
