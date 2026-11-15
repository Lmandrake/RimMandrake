# BENCH_REBOOT_HANDOFF_202611151956 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611151833`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner ruled the **Evidence-for-Ask rule** (2026-11-15 ~11:40 AM PST, verbatim on the ledger item RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME): no agent pauses for him unless it holds concrete evidence that the obvious answer is wrong; take the obvious answer, log it `--per-ruling` that item plus `--why "delegated: evidence-for-ask: ..."`, never as his approval. It already cleared Contagion (6 asks), ExplosiveKnockback and FlowWorks (7), the four pipeline-hardening decisions; he certified Contagion himself. This window was written while preparing an **account switch** from system (2% of its week left, reset ~72 h) to lukas (100%): `claude-account use lukas --confirm archmagi` kills every Claude process, detached runs included, and refuses when run from inside Claude. If you are reading this after the switch: first measure `claude-account --json status` (live account), then every run that was live at the kill (below), then restart the paused tick.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
He is at the keyboard (last typed ~11:56 AM PST). Nothing is waiting on a card. Owed to him as reports, not questions:
- Whether Contagion left "waiting on him" after his certification note (11:53 AM PST) and whether the grown-limb decision `d_efa_q07` was removed from 0.1.0 and filed for 0.2.0 (he moved it: "I would like to move the grown limb work to the next version"). UNVERIFIED at wrap.
- Whether the pipeline fixes a known, specified defect before launching a judge on that mod (promised to check; not checked).
- The Pyrelands triage result (4 questions, 18 round-6 gaps, the PyrelandsMechanics hold): helper was still running at wrap; if it died in the switch, relaunch it from `/home/mandrake/.seat-tmp/BENCH/claude-1000/-home-mandrake-rm-bench/6a30b35a-1380-4354-9ac2-53c767c75228/scratchpad/efa_common.md` (copy the brief into the new launch; the scratchpad may not survive).
- SteveDesktop: under the rule the Conductor TOOK the free step (install Intel XTU remotely, small voltage increase, reversible); not launched yet. A CPU purchase (USD 150-250) goes to him only if that fails, with the fault readings. Evidence `D:\ClaudeWork\rimmandrake\steve_diag\hw_20261115\efa_20261115\`. Lane stays PAUSED; do not `testq.py resume`.
- Spend limit: his card raised `stage_ceiling_usd` 60 -> 100 and made the per-mod release the Conductor's (told after, daily digest). Step 1 evidently landed (a Knockback blind cycle launched at ~11:42 AM PST); step 2 (per-mod release) was still being built by the detached run.
- Graffiti is locked 0.1.0 (badf27d77a), at Stage 2; its hidden-face paint defect was being fixed by a helper at wrap, and the helper was asked whether "graffiti on one side does not influence people on the other side" (his stated intention) is a bar, enforced and tested.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME` -- in-process opus builder was writing the rule into CLAUDE.md, standing_rulings, delegation_policy, CHARTER and the role files, auto-locking a new mod at 0.1.0, making designer_stage.py accept a delegated root/flagship approval and closing the any-OWNER-tsn hole; told to land in pieces; NEXT: `git log origin/main --grep EVIDENCE -i` and `rimflow show` it, then relaunch a builder on whatever is not landed.
- `RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT` -- filed, unworked; NEXT: after the switch read the book entries of the killed runs (GimmeSomeSlack blind cycle 2 unit ...-1794767619, ExplosiveKnockback blind cycle unit ...-1794771710); if either reads as a spent cycle, launch a builder on this item BEFORE restarting the tick, so the mods do not pause on a kill.
- `RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB` -- detached opus run ...-1794771363 live at wrap, step 1 landed, step 2 in progress; NEXT: read its DETACHED RUN ENDED line in the Conductor log; if killed, relaunch from the item (brief: raise is done, build the per-mod release and digest line).
- `RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL` -- in-process opus builder fixing at the brush, live row to run if the bridge was free; NEXT: `rimflow show` it; if open, check `./game` and `rimflow bridge who` first (it may have left a game up when killed), then relaunch.
- `RIMMANDRAKE_ADMIT_CONTAGION_AS_NEXT_BIOME` -- owner certified 5 decisions and moved the limb work to 0.2.0 (owner-said note 11:53 AM PST); NEXT: run `maturation_dispatch.py status` and confirm Contagion no longer reads OWNER and record.json no longer carries d_efa_q07 in 0.1.0.
- `RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY` -- decided under the rule: build it (locked leaf thrown_into_pit_falls); still proposed; NEXT: launch a builder.
- `RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF` -- filed by the triage helper, proposed; NEXT: launch a fixer.
- `RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS` (and the certificate and calibration items beside it; grep the ids) -- decisions recorded 876b15fe6a, ready for a builder; NEXT: launch one builder per item, tests first.
- `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_EB2A` -- lane paused; NEXT: launch a helper to install Intel XTU over ssh and try a small voltage step, reversible, then watch the fault timer.
- `RIMMANDRAKE_TRACE_PHONE_IMAGE_TMP_FILE_VANISHED_ONCE` -- filed, unworked; NEXT: launch a sonnet fixer.
- `RIMMANDRAKE_DRAIN_NIGHTLY_REDS_WHILE_PIPELINE_SLEEPS` -- untouched, 13 reds of 1654 last night; NEXT: launch fixers for unparked reds.
- `RIMMANDRAKE_PROVE_COMPANION_REFUSALS_THE_MINIMAL_LIST_CANNOT` -- four companion checks unrun, needs the game; NEXT: run it on a list with FlowWorks and Gimme Some Slack.
- `WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE` -- live check queued; NEXT: queue it through Dispatch when the game is idle.
- `RIMMANDRAKE_CARRY_OWNER_CERTIFICATE_THROUGH_HIS_OWN_CARD_EDIT` -- untouched; NEXT: check whether 876b15fe6a's certificate decision covers it, then launch a builder that writes the test first.
- `RIMMANDRAKE_SET_CONDUCTOR_WINDOW_TO_FABLE_POLICY_ALREADY_SAID` -- untouched; NEXT: verify the launch profile and close it.
- `RIMMANDRAKE_UNPARK_DESIGNER_WHEN_IT_CAN_FIX_GAPS_ALONE` -- rule landed f9436a1fe, live no-park branch UNRUN; NEXT: close it on the first second refusal that does not park.
- `RIMMANDRAKE_FIT_DISPATCH_TICK_IN_ITS_BEAT` -- proposed; NEXT: read the 10:42 AM PST retry-judge run's report (`rimflow show RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE`) for whether it took this, else launch a builder.
- `RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT` -- the pipeline tick `rm-maturation-dispatch.timer` was PAUSED at 11:56 AM PST for 1 h by `timers_guard.py pause` (restart armed as timer-resume-20261115-115612.timer); NEXT: after the switch and the killed-run check, run `systemctl --user start rm-maturation-dispatch.timer` if the armed restart has not fired.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `claude-account use` refuses inside a Claude session and kills detached runs; a killed started run is not retried by the tick (filed: lessons, 2026-11-15; item RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT).
- Any owner-ledger line naming a concept's item id wakes its waiting Designer; a root citing any OWNER:<tsn> passed the owner check (filed: lessons 20261115T194521Z-BENCH-designer-owner-event-traps).
- `./publish` from a sparse pool clone fails whole-tree checks that cannot see mod sources (filed: lessons 20261115T194926Z-BENCH-publish-tree-checks-blind-sparse-clone).

## Closed since the last handoff (2)

- `RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE` — 0258fe7637d1a6089c5c85b22e97993ca291db9f
- `RIMMANDRAKE_SHOW_VERSIONLESS_MOD_GRAFFITI_ON_MAP` — 19cda97745c29a5204109ecae25f60581e6d7097

## Filed and still open (5) — the next seat's queue

- `RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME` — Evidence-for-Ask rule: a pausing agent takes the obvious answer unless it holds evidence it is wrong; a new mod's first Design Version is 0.1.0 withou
- `RIMMANDRAKE_TRACE_PHONE_IMAGE_TMP_FILE_VANISHED_ONCE` — maturation_now.py: regenerating the page raised FileNotFoundError on a phone .png.tmp.png once, then passed on the second run; cause not found. Also t
- `RIMMANDRAKE_ADMIT_INGAME_SPAWN_RUNNER_REFUSES_GAME_UP` — Maturation in-game launch is refused by rimflow's RUNNER spawn rule (BENCH may only get needs offline), so no automatic in-game run can ever start
- `RIMMANDRAKE_READ_CONTAINER_JOLT_OFFSET_IN_PROOF` — ExplosiveKnockback sc_closed_containers jolt rows print drawnOffset=UNMEASURED (RM_KnockbackProof_StageThree.cs) though the jolt is drawn since 587529
- `RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT` — Maturation tick and detached runs: a run killed by an account switch (claude-account use SIGTERMs every Claude process) must be relaunched on the new 

## Commits

```
a6c57e4246 conversations: catch-up 6 record(s)
59a3ad796a ledger: RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB note
1c6aa67eac maturation: per-mod, per-stage ceiling release (release/releases verbs), digest source 'ceiling release'
07bada2a03 ledger: RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB card notes; file RIMMANDRAKE_ADMIT_INGAME_SPAWN_RUNNER_REFUSES_GAME_UP
197ddf7292 Pyrelands: Evidence-for-Ask takes questions 2, 4, 8; dry-ash text matches the 70% bar; round-6 gaps sorted
6321db9aac maturation: the pipeline locks a new mod's Design Version at 0.1.0 (Evidence-for-Ask ruling)
dae7a0bf00 lesson: publish tree checks go blind-red in a sparse clone on an items-only commit
876b15fe6a Evidence-for-Ask: take the three pipeline-hardening decisions and what Stage 7 must show; Steve CPU stays an ask
7444e5a20a ExplosiveKnockback blind cycle 3: lane 1 recorded blind (33 PASS, 0 FAIL, 12 not_kernel)
e3d439811e lesson: publish tree checks are blind in a sparse scratch clone
c107564784 EK q10-14, FW q3, pit cover: take the obvious answers (Evidence-for-Ask)
39e03ecb13 Contagion: Evidence-for-Ask takes four draft asks (q04 q05 q07 q08) as Conductor decisions
6dcc361c54 maturation: spend rows of ended runs (Dispatch step)
8741539cb6 ledger: maturation dispatch filed RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_THREE
badf27d77a Graffiti: lock Design Version 0.1.0 on his card (Lock as 0.1.0 now)
734282a542 ledger: close RIMMANDRAKE_SHOW_VERSIONLESS_MOD_GRAFFITI_ON_MAP
df6006605c ledger: close RIMMANDRAKE_SHOW_VERSIONLESS_MOD_GRAFFITI_ON_MAP
78978763af file RIMMANDRAKE_SKIP_PAUSED_MODS_IN_IDLE_OWED_PYRELANDS_WAITS with acceptance test (fails on base)
19cda97745 maturation_now: a mod with a Designer record but no VERSION.json is on the map (Graffiti)
39debe49b4 ledger: file RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME (owner's Evidence-for-Ask ruling)
... 17 more: git log --oneline d20eb34ee3..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-11-15T16:09:38Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
 M infrastructure/state/ledger/events/BENCH.jsonl   this window's: ledger notes and the owner's 11:53 AM PST Contagion certification; published with this handoff
 M infrastructure/state/ledger/events/OWNER.jsonl   this window's: ledger notes and the owner's 11:53 AM PST Contagion certification; published with this handoff
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? cards.json   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? deployed/config/ModsConfig.before-tier-mods__mandrake_rm_explosiveknockback__mandrake_rm_flowworks__mandrake_rm_gimmesomeslack__mandrake_rm_patches.xml   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? design/RimMandrake/designer_drawing_out.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_FWLIVE.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE2.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE3.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_FWLIVE.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE1.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE2.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE3.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE4.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE5.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE6.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE7.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CLAUDE_STEVEDESKTOP_OFFLINE8.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CODEX_ARCHMAGI_FWDRAIN.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? infrastructure/state/queue/CODEX_STEVEDESKTOP_HUGETHINGS.md   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? ralph/.context_warned   not this window's: present in git status at the 10:35 AM PST wake, left untouched
?? shortcuts.ps1.txt   not this window's: present in git status at the 10:35 AM PST wake, left untouched
```

