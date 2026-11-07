# BENCH_REBOOT_HANDOFF_202611071556 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611070331`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Artisan (`D:\Luke\dev\MandrakeWorkflows\artisan`, the owner's name for the Ralph loop) is the live experiment; the pipeline stays stopped until his sitting. The evidence that decides everything so far: his one look beat every bar and judge, so his eye gets spent early and cheaply. Queue for Archmagi's game: Pyrelands (rm-ralph-pyrelands), then GSS, then FlowWorks. The loops are units and survive this restart; only the watch dies, so re-arm it (Monitor on both events.log, DONE.md and the units; hourly check). On any DONE.md, a fresh rm-judge reviews the shots blind to its verdicts, and the owner's words go first in its brief. A note reaches a running pass by writing ralph/OWNER_NOTE in its clone: the hook refuses one command to deliver it. Mods accepted: 0 of 135. Nothing has landed on main.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Contrast sheet is open in Typora, unanswered:** `D:\ClaudeWork\rimmandrake\ralph_graffiti\contrast\contrast.md`, options A current, B bolder inside the face, C climbing onto the wall top, D both, or both wrong. He chose this by card. Ask him by card once he's read it; his pick drives Graffiti's next pass (limit 20M, used 7.07M).
- **Offline composites, not the game:** B and D's paint is a filter, and C and D's bent wall geometry doesn't exist yet. A helper added D.
- **GSS claim two is owed his look after the next pass:** blind verdict `D:\ClaudeWork\rimmandrake\ralph_gss\blind_judge_verdict_pass1.md`; junctions it changed in looks he approved need his eye.
- **Graffiti's October 22 card:** the loop drew marks on the wall cell and made paint die with its wall, both against the card. He has not ruled on those two.
- **Spend:** lukas 67% at 07:28 PST, down 8 points in 10.7 h across three loops. He authorized it; there's no total limit.
- **Test grant set to 2036 on his word.** It must go back to campaign when he starts playing.
- **Landing:** all three branches hold art that bypassed the art ledger (`art install` owed), and none has run on the full list.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `GRAFFITI_FINISH_RALPH_LOOP_PLAYS_FIRST` — second claim judged no, unit stopped, contrast sheet built; NEXT: card him on the contrast sheet, put his pick verbatim at the top of ralph/PROMPT.md, and restart with the Pyrelands gate pattern.
- `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN` — sent back with judge findings, limit 20M, unit rm-ralph-gss2 waiting free, unless the Steve helper moved it to rm-ralph-gss-steve; NEXT: read which unit is live and re-arm the watch on it.
- `PYRELANDS_FINISH_ARTISAN_THIRD_TIME_WISER` — pass 4 running, 6.03M tokens, own count 9 true and 12 unseen, grant renewed so its tools work; NEXT: on DONE.md run the blind rm-judge, and show him its first_look shots.
- `FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH` — filed, not started; NEXT: after GSS claims done or pauses, launch one opus helper to set it up from the Pyrelands prompt and D:\Luke\dev\MandrakeWorkflows\artisan\consult\2026-11-07_gpt_brainstorm.md, one aspect first if splitting looks right.
- `STEVE_BUILD_ARTISAN_LOOPER_THIRTEEN_MINUTES` — detached opus helper running from 07:57 PST: turbo-off test, then GSS driving Steve's game with the agent on Archmagi; NEXT: read its note on the item and tell him whether a loop reached Steve's game.
- `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO` — faults about 13 minutes into each boot, the helper sets PROCTHROTTLEMAX 99 as a reversible test; NEXT: read onset over 3 boots with fault_monitor.py report, and restore 100 if nothing changes.
- `GRANT_RESTORE_CAMPAIGN_WHEN_HE_PLAYS` — grant runs to 2036; NEXT: switch to campaign the day he starts playing.
- `PIPELINE_RETHINK_OWNER_STOPPED_BURN` — stopped, PAUSE set; NEXT: keep it stopped until his in-person sitting, then use the item's undo list.
- `RALPH_LOOP_SCRIPT_ENV_BETWEEN_PASSES` — Graffiti's loop lacks the Windows PATH that GSS and Pyrelands get; NEXT: add the exports when restarting Graffiti, since it's already in the other two.
- `RELENTLESS_BUILD_DAILY_RELEASE_WITH_ROLLBACK`, `RELENTLESS_DECIDE_EXAM_KEEP_OR_DELETE` and the other items frozen by his stop — unchanged; NEXT: leave them for the first Relentless pass after his sitting.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `ssh stevedesktop true` fails even when the machine is up, because it lands in PowerShell, so a wait on it never fires (filed: lessons)
- Lodestar's `handoff.py --wake` prints a stale October handoff in this repo; use `src/RimMandrake/Utils/handoff.py --wake` (filed: lessons)
- `./publish` printed PUBLISHED while my commit had failed on a lock, so check the shard on origin (see: D:\Luke\dev\MandrakeWorkflows\artisan\POLICIES.md)
- A pushed branch tracking origin/main hits the art guard from a Conductor session, not from a loop's own session (see: `GRAFFITI_FINISH_RALPH_LOOP_PLAYS_FIRST`)
- Starting a loop under a unit name another running loop's in-memory function checks can deadlock them, hence rm-ralph-gss2 (see: `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN`)

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (6) — the next seat's queue

- `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN` — Ralph loop finishes Gimme Some Slack on branch ralph/gss, offline until the Graffiti loop ends
- `PYRELANDS_FINISH_ARTISAN_THIRD_TIME_WISER` — Artisan loop finishes Pyrelands on branch ralph/pyrelands, third experiment, behind Graffiti and GSS for the game
- `FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH` — Artisan on FlowWorks, fourth experiment, after Pyrelands; set up from its lessons and the GPT brainstorm; maybe several sequential aspects
- `FLOWWORKS_FIX_NATIVE_WATER_AUDIT_RED` — Natives-drink-own-water audit is red: RM_Miasma brackish deep and shallow (NotDrinkable), RM_TheChill RM_PropaneDeep (Propane) read BLOCKED
- `GRANT_RESTORE_CAMPAIGN_WHEN_HE_PLAYS` — When the owner starts playing, switch companion_profile.json to campaign: the test grant now runs to 2036
- `STEVE_BUILD_ARTISAN_LOOPER_THIRTEEN_MINUTES` — Run an Artisan loop against SteveDesktop's game when it comes back: faults arrive about 13 minutes into each boot, so keep the model on Archmagi

## Commits

```
ead072714a conversations: catch-up 4 record(s)
7a7e8fde15 ledger: steward retired a recovered incident
224c6ec2d4 ledger: SteveDesktop to try an Artisan loop, owner's words
567ca66c3d ledger: owner's card answers on Graffiti, GSS and Pyrelands
5f8f2be839 companion grant set to 2036 by the owner; back to campaign when he starts playing
35b783f0d8 companion grant: the Conductor renews it, owner by card
dbbccef641 ledger: RUNNER ingest of 0 testq job(s)
d6cf619978 ledger: RUNNER ingest of 1 testq job(s)
70920224c7 ledger: Steve lane not restored, CPU fault onset now about 13 min per boot
548a88820c ledger: RUNNER ingest of 2 testq job(s)
d45048a8a8 ledger: RUNNER ingest of 0 testq job(s)
3e6c9b7b34 ledger: steward retired a recovered incident
b6989d7f59 selftest_natives_drink_own_water: a red run leaves the tracked report alone A dirty copy in the dispatch clone stopped RUNNER publishes (STEVE_LANE_UNSTICK_PAUSED_UNOWNED_D87C).
8c8ba47051 ledger: RUNNER ingest of 0 testq job(s)
87bf1d3acd ledger: RUNNER ingest of 0 testq job(s)
13b5db742b ledger: RUNNER ingest of 0 testq job(s)
159edd6f11 ledger: live sweep LIVE_RESTORE_DISPATCHER broken
a75c0cb949 ledger: live sweep TESTQ_MODS_WIRE_BEYOND_FLOWWORKS kept, LIVE_RESTORE_DISPATCHER kept
80c5d5b067 ledger: GSS done claim, blind verdict
c1780ec820 ledger: live sweep TESTQ_MODS_WIRE_BEYOND_FLOWWORKS broken
... 25 more: git log --oneline 3f85f72509..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-07T13:34:17Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   not mine; seen dirty at wrap, not touched
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   the art auto-judge's, still running
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   not mine; seen dirty at wrap, not touched
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   not mine; seen dirty at wrap, not touched
?? cards.json   not mine; seen dirty at wrap, not touched
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   not mine; seen dirty at wrap, not touched
?? design/RimMandrake/designer_drawing_out.md   not mine; seen dirty at wrap, not touched
?? design/concepts/Pyrelands/coverage_verdict.json   not mine; seen dirty at wrap, not touched
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   not mine; seen dirty at wrap, not touched
?? shortcuts.ps1.txt   not mine; seen dirty at wrap, not touched
```

