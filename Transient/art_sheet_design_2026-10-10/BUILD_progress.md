# Art review sheet redesign — build progress (2026-10-10)

Started 11:26 PDT. Spec: `DESIGN.md` §6. Owner rulings: decision taken by question card 2026-10-10.

| stage | state | selftests | commit |
|---|---|---|---|
| 0 snapshot decisions files | DONE 11:30 — `decisions_snapshot_2026-10-10T1130/` (27 files + SHA256SUMS + their 27 sheet snapshots) | | |
| 1 quick fixes (4) | DONE — playback img constrained; no laundering; no pre-ticks, tick only on pool lanes; enact refuses non-pool ticks | sheet_hit, sheet_letters, enact_ws (3 new checks fail on old enact) | e4a158506 |
| 2 schema 2 + migration + proof | DONE (tooling; files migrate at rebuild) — decisions_v2.py, migration_proof.py dry run PASS: 27 files, 789 decided rows, 1291 letters same pictures, plan diffs only legacy-tick (499) | enact_v2 | (stage 2) |
| 3 slots / ✕ split / redraw / notes controls | pending | | |
| 4 enact.py schema 2 | DONE with stage 2 (slots, pool add/remove+baseline, slot redraw jobs, asks, legacy confirm, schema gate; ingest too; fill_queue carries slot/ask) | enact_v2 | (stage 2) |
| 5 old-ticks confirm sheet + pulse hand | pending | | |
| 6 rebuild served sheets, URLs 200, screenshots | pending | | |

## Notes
