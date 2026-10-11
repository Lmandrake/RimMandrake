# 17 — review-sheet hybrid build (option H) — progress

Writer: BENCH subagent, 2026-10-11. Owner chose "Hybrid fix (Recommended)" by question card.

| step | state | PUBLISHED |
|---|---|---|
| 1 content-based game-art gate at every chokepoint (serve, commit, artifact) + selftests | done | 7acc06233 |
| 2 scale_panel thing resolver (buildings/items) + art_sheet --subjects | done | 7acc06233 |
| 3 external review-sheets: true-size comparison option | done | review-sheet 3d1554b |
| 4 skill rename scaled-game-image-review -> rimworld-review-sheets | done | c1f890023 |
| run_selftests N/N | done: 388 PASS + 18 SKIPPED (deployed tier) / 406, FAIL 0, CRASH 0 (run in 10 --only chunks: a full run exceeds the 10-min foreground cap at load 35) | |

## Notes
- game_art.py classifies by pictures: cut-out alpha, facing/def file names, Textures/_artpipe paths. Of 49 non-biome
  Transient sheets, 38 classify GAME-ART (incl. sheet_conflicts_review, declared non-art); the 11 NOT-ART are charts,
  screenshots and flattened canon composites. All 28 live biome sheets pass delivery (stamped).
- Chokepoints: nonart_sheet.verify (so serve_gated), sheet_to_artifact (exit 4), infrastructure/githooks/pre-commit,
  block_hand_edited_sheet (Write of any game-art sheet HTML; Edit of any stamped HTML). selftest_game_art 26/26.
- art_sheet --subjects/--jobs --name: one-entry census Transient/biome_ffar/<name>.subjects.json, sheet in biome_ffar so
  refresh/serve/RimPulse treat it like a biome sheet; ground = vanilla Soil measured. Probe sheet (4 subjects) PASSED the
  gate first time after dropping a placeholder-only row (req 3 caught it); probe deleted.
- review-sheets: `trueSize` row field + `CONFIG.trueSize` required/optional; check_sheet validates; test_check_sheet 25/25;
  demo carries it; rendered and screenshotted served in Edge. Committed with the correct noreply identity via -c — the
  repo-local user.email is the WRONG `mandrake@users.noreply.github.com` (owner to fix; not changed by me).
- rimworld-review-sheets: lean SKILL.md (76 lines) + references art_requirements (14 rulings verbatim), lifecycle, traps;
  symlinked; README row; old skill deleted; inbound refs fixed (gate, ingest, art_sheet, hook, one lesson).
- Not done (outside the four asks, from study §5 item 6): validate_skills.py ERROR on an unwired project skill and
  warn_skill_unwired.py exit 2 — the defect that hid scaled-game-image-review for 6 days is still possible.
- For the owner: existing unstamped art sheets (e.g. sheet_conflicts_review_2026-10-09, sluice_panning_warden) are now
  refused at serve/commit/phone; rebuild through art_sheet.py --subjects if they are still wanted.
