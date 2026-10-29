# BENCH_REBOOT_HANDOFF_202610290748 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610290250`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Owner's standing order (night 2026-10-29): Conductor is a LIGHT ORCHESTRATOR whose job is talking with him in plain words; never block his window on long foreground waits; less caution, more progress. Before asking him any biome question, look at the painted worldmap and existing sheets (lesson filed). Owner words are on the ledger (OWNER.jsonl, notes on FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Morning cards, 4 (A-D): `D:\ClaudeWork\rimmandrake\conductor\morning_cards_2026-10-29.md`. A sorting-trial (blocked on auto-undo for trials), B venomvine sitting, C second test PC SteveDesktop (router reservation, BIOS power-restore, Wi-Fi so no network wake), D hose/wall-reach hitch waiver: needs his "ready" and the game, save BENCH_r17_midrain.rws. Present when he returns.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET` — FOUNDRY's; no live restart_kill seen 05:47-07:47Z while FOUNDRY took a ticket about every 4 min; NEXT: read dispatcher journal.jsonl for the first restart_kill and confirm the relaunched window ran seat_restart.py wake, then close it.
- `ACCOUNTPICK_HOLD_RESTORE_WHEN_HE_LANDS` — hold off until he is back (Thu evening / Fri morning); NEXT: restore the account-pick hold when he reports he has landed.
- `V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY` — closed d302fbbcea, v3 roles item still open; NEXT: confirm FOUNDRY claims a moved FlowWorks item.
- `DISPATCHER_VERIFY_SAME_SECOND_HANDOFF` — open; NEXT: check the journal for a same-second handoff and verify the dispatcher handles it.
- `SEAT_RESTART_VERIFY_QUIET_AT_KILL` — open; NEXT: verify a restart_kill only fires when the seat is quiet.
- `CODE_REVIEW_DIRTY_FILES` — seat_restart.py, dispatcher.py, model.py, cli.py, v3_ready.py and the pulse files are DIRTY; NEXT: run code_review_status.py check on each and review, paced for Codex runway.
- `MORNING_CARDS_2026_10_29` — 4 cards written, none shown; NEXT: show the owner cards A-D when he wakes (D only with the game and his ready).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
Filed this night: conductor-stays-conversational, look-at-worldmap-before-biome-question, owner-route-reasons-read-ledger (infrastructure/state/lessons/20261029T043741Z..., T051840Z..., T053351Z...) (filed: lessons)

## Closed since the last handoff (6)

- `BIOME_AUDIT_TRIAGE_NINE_REPAIRS_WAITING` — 2b8cc93c8f
- `ARTPIPE_FACING_COHERENCE_1` — 6c258908c8
- `V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY` — d302fbbcea
- `STEVEDESKTOP_REBOOT_PROVE_HANDS_FREE` — 8fb1d221fe
- `MAINLOCK_DIAGNOSE_WHO_TURNED_THE_KEY` — 8fb1d221fe
- `STEVE_LANE_UNSTICK_PAUSED_UNOWNED_BE53` — 8fb1d221fe

## Filed and still open (1) — the next seat's queue

- `MODCHECK_VALIDATE_BUILD_DELEGATED_NEW_BARS` — modcheck validate binds a north-star hash only with --owner-said/--by-card, but NEW bars are delegated (owner 2026-10-26 'Both autonomy questions are 

## Commits

```
3f7b5a1d0d conversations: catch-up 7 record(s)
abd2be4d75 ledger: RUNNER ingest of 1 testq job(s)
d5e0d52876 ledger: PIT_ENTRY_PROVE_DONE_BUT_STILL_RED done; test profile renewed, 5 items unblocked
44fb13dfda ledger: findings COMPLETION_FIX_PARTIAL_VERIFY_PAINTS_RED, WET_PROOF_FIX_SWIMMER_LEFT_TO_DROWN
db5ac8336a ledger: RUNNER ingest of 1 testq job(s)
56c3ba9483 ledger: RUNNER ingest of 1 testq job(s)
e5340ca802 ledger: DISPATCHER notes (1)
dc154c8c7a ledger: RUNNER ingest of 1 testq job(s)
b1189cb797 ledger: RUNNER ingest of 1 testq job(s)
b272ecd850 ledger: DISPATCHER notes (1)
0b9d1b1b74 ledger: HOSE_SPILL_FIX_OFF_SWITCH_STILL_POURS blocked (bridge profile expired)
fed69037f3 ledger: DISPATCHER notes (1)
3c3cf832d9 ledger: LIQUID_WAKES_FIX_FOOTPRINTS_GONE_QUIET blocked (bridge profile expired)
4868586e2e ledger: RUNNER ingest of 1 testq job(s)
38582ce30f ledger: DISPATCHER notes (1)
2672a8280b ledger: GLOWTANK_SALT_FIX_ONE_PINCH_ONLY blocked (bridge profile expired)
62a1aefff6 ledger: RUNNER ingest of 1 testq job(s)
97ca317423 ledger: AUDITOR_PRESCREEN_FIX_WINDOW_SINCE_LAST_RUN done
f5a15a22cd Auditor pre-screen: window starts at the last FINISHED run's stamp, not now-1d (AUDITOR_PRESCREEN_FIX_WINDOW_SINCE_LAST_RUN)
e71f6ba4bb ledger: RUNNER ingest of 1 testq job(s)
... 56 more: git log --oneline ea08f7e015..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     PIT_ENTRY_PROVE_DONE_BUT_STILL_RED live proof

Working tree clean apart from untracked `Transient/`.

