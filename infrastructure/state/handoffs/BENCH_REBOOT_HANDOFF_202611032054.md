# BENCH_REBOOT_HANDOFF_202611032054 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611031955`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
THE JOINT SESSION WITH THE OWNER IS PAUSED, NOT OVER. He is home sick and asked to continue after this reboot. Resume it: the game is saved as JointSession_20261103_pits (tick 25328); the order and staging plans are in D:\ClaudeWork\rimmandrake\conductor\session_2026-11-03\PRODUCER_PROGRESS.md; the trial notes (lessons on how these sessions should run) are in D:\ClaudeWork\rimmandrake\conductor\joint_session_2026-11-03.md. Format he praised: he watches the live game on Archmagi; the Conductor relays each observation to a Producer helper (rm-builder opus) which re-stages, frames the camera, reports one line. Scenes are BUILT FROM THE MOD'S PROOF SCRIPTS (lesson be8f0ca2af6b), never hand-staged. Take the bridge for the session (rimflow bridge take --for "owner joint session") and release it when he stops.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Session queue: (1) PIT_ACCESS re-stage as 3 pits on dry ground: shallow control / ladder-depth (refused without, passes with) / too deep (flat ladder, refused); he click-tests himself. (2) 06 DRAWBRIDGE is staged: D:\ClaudeWork\rimmandrake\conductor\session_2026-11-03\06_DRAWBRIDGE (5 PNGs + ask.md; 2 drawbridge findings already filed). (3) 03 THRIXWEAVE (needs a trade ship). (4) Flyer live tests with him watching: gravship sea-floor round trip, WEEPINGSTONES_NET_FLEEING_FLIER_1, steadier flier bodies; stage only, he must watch. (5) GRAFFITI last (needs a mod-list switch and reload).
- Done this session: HOSE pipe looks ACCEPTED (closed); WATER S5 third draft APPROVED (record in the scenes file); TITAN_CAMPS not accepted (design intent recorded: corpse = time limit + competition; two scenarios S1/S2; titan art rejected -> THRUMBUNGUS_ART_REDRAW_CARTOON_NO_MORE; meat rots at the vanilla rate); Tellurox never turns -> TELLUROX_FACINGS_REDRAW_ALWAYS_SIDEWAYS + FACING_ART_CENSUS_FIND_UNWIRED_SIDES.
- His card rulings today: EXPEDITE_LANE (two levels Interrupt/Expedited, no count cap, game last); RimPulse retired for script-built brown status pages (STATUS_PAGES_BUILD_REPLACE_RIMPULSE); resource sim waits until 2026-11-10; system-first = first pick, no preemption, no idling.
- DESIGNER_LESSONS_ABSORB_JOINT_SESSION_DAY: a sitting he asked for, to fold today's lessons into the Designer and mature every mod's test script.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `CALL_DEADLINES_ENFORCE_130_OPEN_ENDED` — proposed, raised (research top-5 #2); NEXT: leave it to Relentless; check it has started at the next quick check
- `RED_COP_BUILD_NO_ORPHAN_REDS` — proposed, raised (research top-5 #4); NEXT: leave it to Relentless; check it has started at the next quick check

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Owner-look scenes hand-staged by a helper flooded from a river and tested a pit climbable without a ladder; the proof scripts already prevent both (filed: lessons, be8f0ca2af6b)
- Relentless's tick takes 4-12 min and starves the live game (see: TICK_SPEED_FIX_GAME_IDLES_WAITING)
- testq filler brakes on deliberate cancels and machine-down jobs and nobody releases it (see: STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE)

## Closed since the last handoff (1)

- `LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT` — b1f10e63a7

## Filed and still open (14) — the next seat's queue

- `STATUS_PAGES_BUILD_REPLACE_RIMPULSE` — Build the Relentless status page live, and plan its successor to RimPulse. Owner feedback on the mockup (card 2026-11-03): the English is superb; ever
- `REPEAT_ALARM_ENFORCE_GUARD_OR_STAY_OPEN` — Design idea 5 rule not yet enforced: a twice-seen alarm (rimflow live_repeats>=1) must close only with a class guard test shown failing on the instanc
- `STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE` — Operations owns Steve-lane unsticking. Today the testq filler BRAKED on two non-DONE jobs that were both known non-faults (the 11-02 hardware crash an
- `EXPEDITE_LANE_BUILD_JUMPS_THE_GAME_QUEUE` — An expedite tier above everything, the priority list and live testing included, for: threats to machine health, critical-bug repair, or the owner in s
- `TICK_SPEED_FIX_GAME_IDLES_WAITING` — Relentless's own tick is now the live-game bottleneck: 4-12 min per cycle (median 396 s) because deploy plans run serially and are never cached, so at
- `CORPSE_VISITORS_FIX_NEVER_ARRIVE` — Corpse-site visitors stall: camp (LordJob_VisitColony, 2 pawns) sat at east edge ~6000 ticks; 3 RSW_PustuleHornet scavengers barely moved despite canR
- `CORPSE_YIELD_TUNE_SPOILAGE_OUTRUNS_EATING` — Corpse-site meat: 100000 at birth (round, maybe a clamp, untraced); spoilage 15%/day (84999->72181) vs visitors eating 80/day, so racing scavengers fo
- `PASSAGE_LETTER_FIX_SAYS_FOREIGN_WHEN_NATIVE` — Titan passage letter 'Footfall tremors' says 'it does not live here' but the chosen kind (RSW_Thrumbungus T2, homedHere=True) is native and 2 already 
- `THRUMBUNGUS_ART_REDRAW_CARTOON_NO_MORE` — Redraw RSW_Thrumbungus (tier-2 titan): owner judged it in game 2026-11-03 as cartoonish and wholly unlike the project's modern art. Redraw through the
- `DRAWBRIDGE_DECK_FIX_STEEL_READS_TIMBER` — Lowered steel drawbridge deck draws the bridge look's deck atlas (rust plates + rope rails, default look) and at play zoom reads the same brown as a l
- `DRAWBRIDGE_EDGE_FIX_RAISED_READS_AS_POLE` — A raised drawbridge leaf on an east/west span draws the Edge view (58/256 px wide art), a thin 4-cell pole at the hinge; the raised state is readable 
- `TELLUROX_FACINGS_REDRAW_ALWAYS_SIDEWAYS` — RM_Tellurox (SleepingIce) body uses Graphic_Single with one PNG, so it never turns: the owner saw it walk around live 2026-11-03 without changing faci
- `FACING_ART_CENSUS_FIND_UNWIRED_SIDES` — Census every creature PawnKind (all our tiers, every lifestage and female/male variant): a body graphic on Graphic_Single while _south/_east/_north PN
- `DESIGNER_LESSONS_ABSORB_JOINT_SESSION_DAY` — Owner + Conductor sitting: fold the 2026-11-03 lessons into the Designer role (src/RimMandrake/rimflow/roles/designer.md) and the debug process: deter

## Commits

```
d1320d7a14 conversations: catch-up 2 record(s)
4e9fbfa629 joint session: pit-site flooding lesson, titan meat ruling, drawbridge findings
be8f0ca2af lesson: build owner-look scenes from the proof scripts
dbfcdeea4a ledger: live sweep OPS_RELENTLESS_READING_RESTORE_IUUR broken, OPS_STAFFING_RESTORE_UNDER_BUDGET broken, RELENTLESS_OWNER_DESIGN_NEVER_LETS_GO broken, TOKEN_LIMITS_TAME_BARK_NO_BITE broken
c15c181f6f lesson: cell_rect shot stale after destroy_batch on a paused game; ProofResetRect keeps plants
1ff10ab15f ledger: ops_watch alarm(s) NIGHTLY_COP_FIX_RED_BXSKPY_FGXD, NIGHTLY_COP_FIX_RED_CIXTEN_JSWD, NIGHTLY_COP_FIX_RED_COZRWL_ZNEU, NIGHTLY_COP_FIX_RED_CYEFOF_PQFZ, NIGHTLY_COP_FIX_RED_CYJJIB_ARBP, NIGHTLY_COP_FIX_RED_EGQAPE_WLOU, NIGHTLY_COP_FIX_RED_EMGZHY_NURS, NIGHTLY_COP_FIX_RED_ENVEHB_GOEW
01a3df5035 lesson + findings: cell_rect shot culls offscreen pawns; three TITAN_CAMPS staging findings filed
19ffd9e416 ledger: relentless supervisor
eef19a6d82 ledger: DISPATCHER notes (3)
5b2bbc4881 TIRED_SWIMMER_FIX_UNREACHABLE_SHORE: shore wrapper runs in the dotnet lane
1e0decc769 lesson: relentless tick is the live bottleneck; proof defects belong before the slot
294453dfb9 lesson: Steve power loss corrupts testq runner clone
390d2a28e2 ledger: Operations triage of OPS_FINDINGS_DIAGNOSE_XZLM (Steve runner clone repaired after power loss); acks flow/seats incidents
e39b3f6399 ledger: ops_watch alarm(s) note:CLONE_POOL_BREACH:disk.pool_breach, OPS_ERROR_BUDGET_DIAGNOSE_CIRG, NIGHTLY_COP_FIX_RED_ADEAUS_MRKD, NIGHTLY_COP_FIX_RED_AQJSGV_CFVH, NIGHTLY_COP_FIX_RED_ATJKEB_FBYD, NIGHTLY_COP_FIX_RED_AYQENC_HIKO, NIGHTLY_COP_FIX_RED_BGARNK_COXO, NIGHTLY_COP_FIX_RED_CYGHVG_QCWJ, NIGHTLY_COP_FIX_RED_CZZSPJ_OFFZ, NIGHTLY_COP_FIX_RED_HMGHDI_RQAA, OPS_RED_OVERDUE_CHASE_AEUZ
fefc0066ca ledger: RUNNER ingest of 1 testq job(s)
8c677f9d93 ledger: DISPATCHER notes (1)
1ff82747f3 RED_COP_BUILD_NO_ORPHAN_REDS: build cop, one raised item per nightly red root cause, overdue reds alarm Groups are ops_watch readings testing.red_<id> (alarm NIGHTLY_COP_FIX); deadline selftest.red_fix_deadline_h; NIGHTLY_NEWS now alarms only on known-red list faults.
9f11ed2e81 HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS: live check runs under python.exe (no numpy); live list adds StarWarsPatches
75f415aeb9 CALL_DEADLINES_ENFORCE_130_OPEN_ENDED: review marks for the deadline lint and robocopy hook
f99ab1839f CALL_DEADLINES_ENFORCE_130_OPEN_ENDED: subprocess deadline lint, robocopy hook, timeouts on external calls
... 15 more: git log --oneline 9ce40b96a7..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-03T20:53:12Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/art/events/BENCH.jsonl   Relentless/art pipeline, not this window
 D infrastructure/state/items/HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD.md   this window (committed just now)
 M infrastructure/state/ledger/events/RUNNER.jsonl   RUNNER seat
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   Relentless FlowWorks worker
?? cards.json   unknown earlier window, untouched
?? infrastructure/state/items/closed/HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD.md   this window (committed just now)
?? shortcuts.ps1.txt   Steve-restore helper, scratch
```

