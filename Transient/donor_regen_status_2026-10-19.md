# dregen_ job status, 2026-10-19 04:10 (measured: job lists x _artpipe pending/active/done/failed x collected.jsonl x this hour's applied log)

Unit = artpipe job FILE (a creature row makes one file per facing). Rows: donor 627, SWBestiary 208 (835). Job files found: donor 765, SW 227.
The donor job list was deleted by eaf051b8f0 along with art_accept_finished.py; read from `git show eaf051b8f0^:design/RimMandrake/donor_regen_jobs_2026-10-18.json`.

| state | donor files | SWBestiary files | total |
|---|---:|---:|---:|
| installed (in collected.jsonl; 116 of these landed in the 04:07 run) | 248 | 97 | 345 |
| finished, refused by the art ledger: owner-KEPT picture | 155 | 0 | 155 |
| finished, not installed (no plan row; bulk_accept plan also lists 19 unresolved + 8 skipped) | 110 | 103 | 213 |
| failed in generation (codex, 3 attempts, no image) | 252 | 27 | 279 |
| pending / active | 0 | 0 | 0 |
| never submitted (row with no job file) | 0 | 0 | 0 |

Rows with at least one failed file: donor 252 of 627, SW 17 of 208.
The task's "149 KEPT" measures 155 job files (some destinations share a kept picture). Rejected/purged refusals: 0.

Refusal categories printed by the retired art_accept_finished at 04:00:39 (it could not be re-run; its finished-not-installed groups):
no single def of ours to repoint 64, target_def draws 2+ texPaths 61, Graphic_Random folder naming 48, graphicClass inherited with facing '' 43, flowworks 38, unbound / no def stem 28.

04:07 run (bulk_accept_renders, owner-override disabled): 271 planned, 116 installed, 155 refused (all owner-KEPT).
