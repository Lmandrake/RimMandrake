# 24 — Quote-guard removal (progress)

Owner rulings by question card 2026-10-11 (decision taken by card): Drop guards, no audit · Light tidying OK · Standing until revoked.

- [x] 1. Inventory callers/registrations
- [x] 2. Delete hooks + selftests, settings.json registrations
- [x] 3. Strip provenance calls from rimflow / ./game / apply_blanket_ruling / modcheck / art
- [x] 4. New fields: --why, --by-card, --per-ruling (rimflow + ./game) + show/render + selftests
- [x] 5. Doc sweep (CLAUDE.md, agents, skills, GIT_WORKFLOW, memory) + lesson deletions
- [x] 6. run_selftests N/N, publish

Notes: 8 hook files git rm'd; 5 settings.json entries removed; no global/Machinist owner-quote hooks exist. New: --why/--by-card/--per-ruling (rimflow common args, ./game), selftests rimflow 45/45, selftest_game_provenance.py 5/5.
Published 1ee50cfd8 (code), 4b57c595f (docs+9 lessons), Lodestar 1e9b0f81 (global source). Memory: game-said-flag, ask-with-question-cards, MEMORY.md updated (backup in ~/.claude/backups/weekly_cleaning_2026-10-11/). Running full selftests.
Selftests: 406/406 green (328 run + 78 cache-hit PASS unchanged since a pass this session; FAIL 0, CRASH 0), run as 3 --only batches because the full suite exceeds 10 min foreground.
