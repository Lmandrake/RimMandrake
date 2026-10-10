# Art review sheet redesign — build progress (2026-10-10)

Started 11:26 PDT. Spec: `DESIGN.md` §6. Owner rulings: decision taken by question card 2026-10-10.

| stage | state | selftests | commit |
|---|---|---|---|
| 0 snapshot decisions files | DONE 11:30 — `decisions_snapshot_2026-10-10T1130/` (27 files + SHA256SUMS + their 27 sheet snapshots) | | |
| 1 quick fixes (4) | DONE — playback img constrained; no laundering; no pre-ticks, tick only on pool lanes; enact refuses non-pool ticks | sheet_hit, sheet_letters, enact_ws (3 new checks fail on old enact) | e4a158506 |
| 2 schema 2 + migration + proof | DONE — all 27 files migrated 11:53 (originals: `decisions_premigration_2026-10-10T1153/`); proof on the migrated files PASS (`migration_proof_2026-10-10.txt`) — decisions_v2.py, migration_proof.py dry run PASS: 27 files, 789 decided rows, 1291 letters same pictures, plan diffs only legacy-tick (499) | enact_v2 | 2f732ee8a |
| 3 slots / ✕ split / redraw / notes controls | DONE — labelled slot lanes from the live dump (sexes, young, per-prefix flight, pool), unassigned + reference lanes, click-to-use, accept/redraw, 4 ✕ verbs + guards, pool tick only on pools + add-all, requests fields, schema-2 records | sheet_slots, sheet_hit, sheet_letters | (stage 3) |
| 4 enact.py schema 2 | DONE with stage 2 (slots, pool add/remove+baseline, slot redraw jobs, asks, legacy confirm, schema gate; ingest too; fill_queue carries slot/ask) | enact_v2 | 2f732ee8a |
| 5 old-ticks confirm sheet + pulse hand | DONE — 627 ticks (309 on pools), http://localhost:38677/?t=zqVPucphxnO2UDkfwfBpyA, hand:67385f229e | enact_v2 (confirm/drop) | (stage 3) |
| 6 rebuild served sheets, URLs 200, screenshots | DONE — 27/27 rebuilt through the gate, 28/28 serve URLs 200, letter mismatches 0; shots in `shots/` (Rot preview handed hand:694d197810) | | |

## Notes

- Pre-existing selftest failures (not touched): ledger_lint (FOUNDRY shard), one_path_seam + hugethings_footprint (hard-coded paths), bridgetools tool_metadata.
- Already-minted keep rulings in the art ledger from past default ticks are history; enact releases same-row/same-file keeps on ✕ as before.
- A stale browser tab still running the OLD page code can write a schema-1 record after migration; enact/ingest read it (its ticks become legacy on the next edit). The rebuilt-sheet banner asks him to reload.
