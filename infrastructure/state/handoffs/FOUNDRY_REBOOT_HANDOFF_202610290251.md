# FOUNDRY_REBOOT_HANDOFF_202610290251 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610261818`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
nothing this wave

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Nothing needs his veto. Pending his word: Bothan mood fur / Kel Dor mask oxygen / Defel invisibility (owner Q3, Q5; spec design/RimStarWars/species_signature_mechanics_spec.md), and his reaction to the must-show drafts in design/validation_walks/_drafts/must_show_drafts_2026-10-18.md. Pit walk ran 21/21 PASS live (acceptance still owed).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `MINERAL_SURFACE_BUILD_PER_BIOME` — a doing item inherited from the 2026-10-28 window, untouched by this one (lease lapsed); NEXT: claim it again with `rimflow next --seat FOUNDRY`, or release it if still too big (released 5x before)

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
origin/main was LOCKED (GH006) for ~30 min this window; it cleared on its own, `./publish` fails on an untracked conversations/ file that origin already has or on a locally-modified FOUNDRY.jsonl: delete the identical untracked copy / commit the shard by path first (see: this handoff)

## Closed since the last handoff (2)

- `MONITORING_CONCEPTS_DESIGN_HALF_DRAWN` — 0881ebd877ed
- `ARTPIPE_FOREIGN_COPY_AUDIT_111_DONE_JOBS` — 8cea1c2d5f

## Filed and still open (11) — the next seat's queue

- `LEDGER_MOD_FIELD_DECIDE_OR_DROP` — Decide whether rimflow items get a mod field; close-from-proposed inflates throughput
- `METRICS_FOLLOWUPS_FINISH_STILL_STRETCHING` — rimflow_metrics follow-ups: cold-load numbers into script, --now flag, RimPulse row group
- `COLD_STORAGE_CARBONFREEZE_REDRAW_INTERIM_ART` — Carbon-freezing press line draws vanilla interim art: own art for RSW_CarbonFreezingPress (2x2, Graphic_Multi, drawSize 3, now SerumCentrifuge), 4 RSW
- `CASTROSTER_FIX_STILL_NAMES_CUT_XENOTYPES` — selftest_xenotype_defcut RED: 5 cast rows still name Hussar/Yttakin (cut) as race
- `ARTSHEET_FIX_REFERENCE_TEXTURES_PICKABLE` — selftest_reference_textures RED: 7 built sheets make reference textures pickable or hide them
- `FOUNDRY_CLONE_SYNC_STALE_TIMERS` — /home/mandrake/rm/foundry sits at c837e3ddb1 (no close_evidence.py, 135 untracked) while rm-codebase-health and rm-mirror timers run code from it. Whe
- `MUTATION_COLLECT_FIX_COPYTO_SILENTLY_EMPTY` — run_mutation collect --copy-to copied nothing for Steve runs 20261028T095621/013440 (summaries had to be scp'd by hand); make it copy or fail loudly
- `FOUNDRY_SHARD_RESCUE_STRANDED_EVENTS` — Commit + ./publish your FOUNDRY.jsonl: 17 events since 2026-10-28T21:48Z only in /home/mandrake/rm/foundry (clone 87 behind origin); if the push is re
- `TIMERS_PAUSE_DIAGNOSE_WHO_HIT_THE_BRAKES` — Someone ran timers_guard pause --hours 4 --all at 18:36:50 PDT, 40 s after the steven fleet relaunch; dispatcher dead 16 min. Find the caller (no tran
- `SCRATCHREAP_FIX_HUNGRY_FOR_FOUR_GIGS` — rm-scratch-reap.service ran its full 30 min at 17:30 on 2026-10-28, peaked at 3.9 G memory and was killed (failed); it restarted 19:01 and is activati
- `CONDUCTOR_NAME_RENAME_BENCH_STEPS_ASIDE` — Name the v3 Conductor 'Conductor' everywhere a human or agent reads it: window/tab title and WT profile, set_agent_window role, seat-ready line, ident

## Commits

```
7ccd4a71e1 ledger: FOUNDRY shard (triage notes, leases)
197a943a3f ledger: FOUNDRY pit walk 21/21 PASS, reconciles
50ae47e5d8 conversations: catch-up 7 record(s)
2a877eca9b handoff: BENCH 202610290250 (wind-down for the public push) + 2 lessons
86b689337b conversations: catch-up 1 record(s)
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
... 1143 more: git log --oneline 3905d705fc..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-29T02:25:33Z

Working tree clean apart from untracked `Transient/`.

