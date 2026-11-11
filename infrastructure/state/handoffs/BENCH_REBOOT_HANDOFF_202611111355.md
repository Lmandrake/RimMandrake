# BENCH_REBOOT_HANDOFF_202611111355 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611111231`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The 05:15 PST window deaths were the account switcher's planned HARD STOP (every account at its line; `claude-account fleet-stop`), not a crash; it is silent, so a waking window blames "a boot, crash or account switch". Read `D:\ClaudeWork\rimmandrake\switching_plan\notice.json` first. Codex is fixing it (codex_wsl/worker-names). The 23:59 reboot was Windows Update KB5132061.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
Owner orders this window (2026-11-11, verbatim):
- "Please ensure that you switch to the System account before it resets today, to ensure you can resume the Artisan runs on the mods we're trying to finish when the reset occurs." Scheduled: rm-switch-system-1157 (11:57 PST, `use system --no-relaunch`), rm-fleetstart-system-1208 (12:08, fleet-start only if no claude runs); log D:\ClaudeWork\rimmandrake\conductor\switch_to_system_20261111.log.
- "Yes." to: resume Pyrelands and GSS Artisan loops at noon (GSS gets more tokens past its 43M limit), run the Graffiti blind judge, keep the FlowWorks Artisan loop paused while Codex drains FlowWorks.
- "once System is restored, please wind down the CODEX workers. They are a stopgap workforce while we're waiting to get more Claude tokens, so they should not continue past the rest except to finish out their round and store their work". Scheduled rm-codex-winddown-1200 (12:00): kills the fw-drain round loop (current round finishes), STOP file + disable codex-ht-loop on SteveDesktop, then resumes testq on both lanes once both rounds end; log D:\ClaudeWork\rimmandrake\conductor\codex_winddown_20261111.log.
- Worker naming: Conductor recommended CODEX_<MACHINE>_<LANE> over his CODEXWhittle#; he did not object.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- PYRELANDS_FINISH_ARTISAN_THIRD_TIME_WISER -- Artisan loop dead 2.9 days, 1 bar left (unit rm-ralph-pyrelands, Archmagi game); NEXT: after 12:08 confirm the fleet is on system, read its last pass, restart rm-ralph-pyrelands.
- GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN -- GSS Artisan paused at its 43M limit, 1 left (unit rm-ralph-gss-steve, SteveDesktop game); NEXT: once codex_winddown log says DONE, raise its limit and restart rm-ralph-gss-steve.
- GRAFFITI_NORTHSTAR_SHIP_1 -- Graffiti Artisan claims done; NEXT: spawn an rm-judge blind judge on it, then put it to the owner.
- RIMMANDRAKE_COMPARE_ARTISAN_WHITTLE_COST_PER_CLOSED_ITEM -- filed 25a1da95d0, first ticket after the reset; NEXT: spawn one opus helper to write the comparison from ARTISAN_NOW + both Codex progress.md files.
- RIMMASTER_FIX_HUGETHINGS_GPT_REVIEW_THREE_P1_FOUND -- P2/design rest was in the Steve Codex lane, which winds down at noon; NEXT: put HugeThings OWNER_QUESTIONS (D:\ClaudeWork\rimmandrake\codex_steve\ht-loop\OWNER_QUESTIONS.md) to him at the next sitting.
- Codex job worker-names (no item; D:\ClaudeWork\rimmandrake\codex_wsl\worker-names\final.md) -- worker names + visible hard stop; NEXT: read final.md and report its shas to the owner.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- WSL Keepalive task pointed at the pre-fold claude-remote-control path; repointed with Set-ScheduledTask (schtasks /change needs a password) (filed: MandrakeWorkflows incident-log dbaeb00).
- Silent account hard stop kills every window (filed: lessons c0c80027dc). Codex drain wrote BENCH handoffs (filed: lessons 49866df663).
- `claude-account use` closes every Claude window even with --no-relaunch (dry-run says so) (see: this handoff; switch_to_system_20261111.sh relies on it at 11:57).

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (1) — the next seat's queue

- `RIMMANDRAKE_COMPARE_ARTISAN_WHITTLE_COST_PER_CLOSED_ITEM` — Compare Artisan loops (Claude, per-mod, bars) with Codex Whittle loops (fw-drain, codex-ht-loop): items accepted, tokens/quota per accepted item, wall

## Commits

```
68bdb1445b conversations: catch-up 4 record(s)
55c26b2175 Render queues for the registered Codex worker seats
21944c5d4d Prove land-only native titan passage arrivals
25a1da95d0 ledger: file RIMMANDRAKE_COMPARE_ARTISAN_WHITTLE_COST_PER_CLOSED_ITEM
5d3a2a8bec Give Codex loops distinct seats and refuse BENCH handoffs
8de445f9c2 Record Codex FlowWorks drain round nine handoff
1643479310 Close repaired railing toggle
5eed07366f Record railing toggle proof and independent acceptance
5e808f72c6 Expand railing test and proof code for readability
49866df663 lesson: Codex drain publishes handoffs under the BENCH seat key
c0c80027dc lesson: 05:15 seat deaths were the switching plan's silent hard stop
16caafc7ef Handle omitted fields in railing live proof
2c1d3f3879 Cancel pending railing removal when re-enabled
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-11-11T13:08:21Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   (pre-existing at wake, not this window's)
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   (pre-existing at wake, not this window's)
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   (pre-existing at wake, not this window's)
 M infrastructure/state/ledger/events/OWNER.jsonl   (pre-existing at wake, not this window's)
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   (pre-existing at wake, not this window's)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   (pre-existing at wake, not this window's)
?? cards.json   (pre-existing at wake, not this window's)
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   (pre-existing at wake, not this window's)
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   (pre-existing at wake, not this window's)
?? design/RimMandrake/designer_drawing_out.md   (pre-existing at wake, not this window's)
?? design/concepts/Pyrelands/coverage_verdict.json   (pre-existing at wake, not this window's)
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   (pre-existing at wake, not this window's)
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   (pre-existing at wake, not this window's)
?? ralph/.context_warned   (pre-existing at wake, not this window's)
?? shortcuts.ps1.txt   (pre-existing at wake, not this window's)
```

