# BENCH_REBOOT_HANDOFF_202610290250 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610290134`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The mineral sheet's biome list is wrong, and the error comes from upstream, not the sheet.** `minerals_where_they_belong_design_2026-10-02.md:100` calls the frozen twins RUT_Desert, RUT_ExtremeDesert and RUT_AridShrubland "RUT-only". The 10-03 registry and `RM_MineralPolicyKernel.cs:222-236` (which maps twins by `"RM_"+suffix`) inherited that error. Audit: `design/RimMandrake/biome_name_provenance_audit_2026-10-28.md` (0ee4faa48d). Of 37 columns, 26 are real biomes. Nothing about minerals ships until the sheet is rebuilt from the ruled list.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The audit's 4 questions were answered by him on 2026-10-28, and all 4 were already on record (painted worldmap, cauldron.md). The audit has been corrected and its 9 repairs filed for FOUNDRY. Item: `BIOME_AUDIT_TRIAGE_NINE_REPAIRS_WAITING`.
- The Dispatcher is PAUSED for his final public push: `D:\ClaudeWork\rimmandrake\dispatcher\PAUSE`. Delete it to resume.
- GitHub `main` was locked (lock_branch) for a while after 02:21Z and is unlocked now. Not touched, on his word: `MAINLOCK_DIAGNOSE_WHO_TURNED_THE_KEY`.
- Mineral sheet republished under steven: https://claude.ai/artifact/UshY3nFfXfApojZUHNdjUF. Its source is pinned at `Transient/mineral_matrix_round_two/`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `BIOME_AUDIT_TRIAGE_NINE_REPAIRS_WAITING` — filed, needs owner; NEXT: walk him through the audit's 4 questions, then file its 9 proposed tickets (namecheck each).
- `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` — trial paused for the push; NEXT: when he resumes, delete the PAUSE file, run Innovator `role_launch.py run-now --role Innovator --by BENCH --why "v3 trial night: first run" --apply`, then `v3_ready.py`.
- `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` — fixes fdd92bcdc1 (offline item rung past a bridge item; powershell path); NEXT: after unpause, confirm the journal shows a FOUNDRY ring with no 'powershell.exe' hold.
- `CONDUCTOR_NAME_RENAME_BENCH_STEPS_ASIDE` — filed for FOUNDRY; NEXT: FOUNDRY claims it after unpause.
- `MINERAL_MATRIX_DESIGN_ROUND_TWO_SPARSER` — sheet's biome columns wrong; NEXT: rebuild the sheet from the audit's ruled list before reading any of his edits.
- `V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY` — applied; NEXT: close once FOUNDRY claims a moved FlowWorks item.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A WSL systemd user unit has no Windows PATH, so a bare powershell.exe fails there (filed: lessons).
- ./publish refuses on an untracked file that origin also added: cmp it against origin, move it aside, re-run (filed: lessons).
- Seats may not message each other (a hook blocks it). To reach FOUNDRY mid-item, go through the owner or `broadcast.py` (see: CLAUDE.md).

## Closed since the last handoff (2)

- `OPS_DEADMAN_REVIVE_A054` — c530010fd0
- `CONDUCTOR_RESTART_EXPLAIN_ZSH_TOOK_THE_BLAME` — 488bb45d74

## Filed and still open (5) — the next seat's queue

- `TIMERS_PAUSE_DIAGNOSE_WHO_HIT_THE_BRAKES` — Someone ran timers_guard pause --hours 4 --all at 18:36:50 PDT, 40 s after the steven fleet relaunch; dispatcher dead 16 min. Find the caller (no tran
- `ACCOUNTPICK_HOLD_RESTORE_WHEN_HE_LANDS` — Restore dispatcher_schedule account_pick hold [role_launch, ring, recover] when the owner is back (Thu evening/Fri morning); emptied 434cf3a30d by his
- `SCRATCHREAP_FIX_HUNGRY_FOR_FOUR_GIGS` — rm-scratch-reap.service ran its full 30 min at 17:30 on 2026-10-28, peaked at 3.9 G memory and was killed (failed); it restarted 19:01 and is activati
- `MAINLOCK_DIAGNOSE_WHO_TURNED_THE_KEY` — GitHub lock_branch went ON for Lmandrake/RimMandrake main after 02:21Z 2026-10-29; every seat's ./publish now fails (GH006). Owner: don't touch it; re
- `BIOME_AUDIT_TRIAGE_NINE_REPAIRS_WAITING` — Mineral sheet biome columns are wrong (37 cols: 26 real, 5 layers, 3 frozen RUT_ twins, stale Umbra/Fuel Snows, ChillCrater as flat). Root: minerals_w

## Commits

```
ad7db12135 ledger: file BIOME_AUDIT_TRIAGE_NINE_REPAIRS_WAITING; mineral item note
9a3fe20d7d design: biome name provenance audit (mineral sheet)
6ec81dc8bd conversations: catch-up 4 record(s)
b0d5aadd95 ledger: RUNNER ingest of 1 testq job(s)
fdd92bcdc1 dispatcher: a bridge item on top no longer starves the seat; idle probe finds powershell without a Windows PATH
84f194e5f5 ledger: RUNNER ingest of 1 testq job(s)
bd0b6ffe4e ledger: file CONDUCTOR_NAME_RENAME_BENCH_STEPS_ASIDE, MAINLOCK_DIAGNOSE_WHO_TURNED_THE_KEY
e6be0830f3 ledger: RUNNER ingest of 1 testq job(s)
f1ba0713bc ledger: DISPATCHER notes (2)
b5300f21f8 ledger: RUNNER ingest of 1 testq job(s)
b5b2f5bf5b ledger: DISPATCHER notes (1)
f43ced6c77 ledger: RUNNER ingest of 1 testq job(s)
02aa98956e ledger: Operations 19:30 check — reaper timeout and pulse-deploy sparse items filed, Codex-callers item corrected
9ca2c776d7 Transient: pin mineral matrix round-two sheet source (publishable from any checkout)
d10802f8c6 ledger: close CONDUCTOR_RESTART_EXPLAIN_ZSH_TOOK_THE_BLAME
26393dbeb5 ledger: XENOTYPE_CANON_CORRECTION_1 partial + builder note
3aced38ff9 ledger: FOUNDRY lease/reconcile events
b6446f37f2 code_review: mark XCC1 signature gene files clean
9172fc72ae races: Kaminoan UV vision, Kel Dor antiox respiration, Defel light-absorbing fur genes
488bb45d74 ledger: Conductor wake: reap item filed, mineral sheet republished, restart-item progress
... 17 more: git log --oneline 0ff79ce2a4..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-28T23:39:24Z

Working tree clean apart from untracked `Transient/`.

