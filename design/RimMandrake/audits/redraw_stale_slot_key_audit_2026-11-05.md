# Redraw/accept slots keyed by a stale lane — audit, 2026-11-05 (REDRAW_STALE_SLOT_KEY_AUDIT_DUPES)

Tool: `src/RimMandrake/Utils/art/redraw_stale_slot_audit.py` (read-only; selftest
`src/RimMandrake/Utils/art/selftest_redraw_stale_slot_audit.py`). Rerun:
`python3 src/RimMandrake/Utils/art/redraw_stale_slot_audit.py --out <report.md>`.

Inputs measured 2026-11-05: 360 `*.decisions.json` in the clone (107 name no snapshot: not sheet records,
enact refuses them too), 11046 artpipe jobs (339 enact jobs, 702 carrying a `slot`).

## Verdict

- **No duplicate redraw jobs.** No stale-keyed ask has a job under both the old key and the lane it maps to today,
  so leaving those slots unmapped in 93d799120b caused no double renders.
- **No accept on a stale key.**
- **5 misrouted (done) jobs**, all on `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json`:
  filed while the key was a lane, then the sheet was rebuilt. Their `slot` names no lane today, and
  `art_sheet.py` (`_slot_of_family`, "filed FOR another graphic") keeps an unbound render with such a slot out of
  every lane, so these renders can drop out of review.
- **6 stale redraw asks with no job yet**; an enact dry run of that file confirms **3 are queued at the old lane**
  (RSW_KraytDragon `KraytDragon_f`, `KraytDragon_j`; RSW_Taozin `Taozin`). `job_rows` picks facings from today's
  columns whose lane equals the slot, and no lane today does, so the job is filed at a dead lane. The other 3
  (Wampa_j, Yobshrimp swimming ×2) are not queued by enact today (held back elsewhere in the plan).

The fix (refuse or resolve a stale redraw key at filing, keep the existing job id when one exists, and re-home
the done renders) is filed as `REDRAW_STALE_SLOT_FIX_ORPHANS_ADRIFT`.

Sanity probe of the 0 (the duplicate check only compares against a lane the stale key RESOLVES to): every
`enact_` job of the five flagged rows was listed against today's lanes. Each stale-keyed job is the only job for
its old slot; the rows' other jobs are different asks (a row redo with no slot, the HssissA / Hssiss_Swimming slot
asks). No two jobs answer the same ask.

## Audit output

decisions files read: 360; unreadable or without a snapshot: 107

| class | count |
|---|---|
| DUPLICATE | 0 |
| MISROUTED | 5 |
| WOULD_FILE | 6 |
| ACCEPT_OVERRIDDEN | 0 |
| ACCEPT_STALE | 0 |

## MISROUTED
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_Hssiss slot slot `swanimals/Hssiss/HssissB` -> unresolved (its pictures are unassigned (found by name) on today's sheet); stale jobs enact_77873763_hssiss_v1_east[done], enact_77873763_hssiss_v1_north[done], enact_77873763_hssiss_v1_south[done]
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_Hssiss slot slot `swanimals/Hssiss/HssissC` -> unresolved (its pictures are unassigned (found by name) on today's sheet); stale jobs enact_3c4de41e_hssiss_v1_east[done], enact_3c4de41e_hssiss_v1_north[done], enact_3c4de41e_hssiss_v1_south[done]
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_Shyrack slot slot `_flip:swanimals/Shyrack/Shyrack_Flying_` -> unresolved (its pictures moved to Shyrack, a lane that already existed (not a rename)); stale jobs enact_52752dc1_shyrack_v1[done]
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_Taozin slot slot `swanimals/Taozin/Taozin_j` -> Things/Pawn/Animal/RSW_Taozin/RSW_Taozin; stale jobs enact_50f92153_taozin_v1_east[done], enact_50f92153_taozin_v1_north[done], enact_50f92153_taozin_v1_south[done]
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_Whisperbird slot slot `_flip:swanimals/Whisperbird/Whisperbird_Flying_` -> unresolved (its pictures moved to Whisperbird, a lane that already existed (not a rename)); stale jobs enact_23e1bbcd_whisperbird_v1[done]

## WOULD_FILE
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_KraytDragon slot slot `swanimals/KraytDragon/KraytDragon_f` -> unresolved (its pictures moved to KraytDragon_m, a lane that already existed (not a rename))
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_KraytDragon slot slot `swanimals/KraytDragon/KraytDragon_j` -> unresolved (its pictures moved to KraytDragon_m, a lane that already existed (not a rename))
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_Taozin slot slot `swanimals/Taozin/Taozin` -> unresolved (its pictures are not under the same letters on today's sheet)
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_Wampa slot slot `swanimals/Wampa/Wampa_j` -> unresolved (its pictures moved to Wampa, a lane that already existed (not a rename))
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_YobshrimpLand slot slot `swanimals/Yobshrimp/Yobshrimp_Swimming` -> unresolved (its pictures moved to Yobshrimp, a lane that already existed (not a rename))
- `Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json` RSW_YobshrimpLand slot slot `swanimals/Yobshrimp/Yobshrimp_j_Swimming` -> unresolved (its pictures moved to Yobshrimp, a lane that already existed (not a rename))

