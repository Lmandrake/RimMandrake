# BENCH_REBOOT_HANDOFF_202611081918 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611081607`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Mods close faster live with the owner as judge than in Artisan loops: he closed Pyrelands in one morning sitting (every bar passed live, "Mod Closed = 1! Celebration!") after the loop spent ~70M tokens at 21/22. His card 8:47 AM: "(3) and we're doing the rest of the bar closing manually. It is NOT a law that "an Artisan pass must agree" ... Some mods close when I say they do." Loops are STOPPED (STOP files in D:\ClaudeWork\rimmandrake\ralph_*). In a sitting: stage paused with raids off (difficulty_tune threatScale 0 + incident_queue_clear, re-apply after every load), NEVER touch game speed (he runs the clock), and never let a staging script lock pawn rotation.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Pyrelands CLOSED on his card (11:09 AM). Its code lives only on branch ralph/pyrelands (397 commits behind main; local commits 9994e0125f, eafc1a0436 unpushed because the push hook refuses the stale branch): landing is RIMMASTER_LAND_PYRELANDS_BRANCH_397_COMMITS_BEHIND.
- New game-wide fixes on main, both passed live: metal/stone/gem stuff non-flammable (ca4586309b) and "south draws in front" for pawns, buildings, plants (608a2a7bff), both in RimMandrake Patches (mandrake.rm.patches, now on the pyrelands/flowworks/gimmesomeslack tiers, 285a403024).
- Pocock: he adopted GSS-style failure-led scenario tests + a real-types pilot (card 9:06 AM). Mining result (d331b50a77, design/RimMandrake/2026-11-07-pocock-design/06-mined-live-bugs.md): 66 live-found bugs 11-05..11-08, 47 (71%) fixed in callers, 25 caller+wiring bugs a scenario could have caught; real game types run a gate outside the game in 2.9 s but stop at a Map. Bring him the seed set.
- infrastructure/state/art/events/BENCH.jsonl holds UNCOMMITTED install events (Eopie_north 4b3be661, RM_Mirrik_north 37b1d57e, ...) from the art-eval pipeline whose PNGs are not in the tree; the art guard refused a push carrying them. Not mine; someone must reconcile before that shard can be committed (Eopie north was his kept art per the previous handoff).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `RIMMASTER_REDESIGN_ARTISAN_JUDGMENT_NOT_CHECKLIST_GRIND` — FIRST JOB of the next window, owner's ask ~11:30 AM PST; seed with today's evidence, 6 concepts (A-F) and trade-offs at design/RimMandrake/artisan_judgment_seed_2026-11-08.md; NEXT: run an Opus high-effort review, then GPT blind round on the problem statement and evidence only, then GPT cross round with the seed and its own answer, merge into D:\Luke\dev\MandrakeWorkflows\artisan\ as PROPOSALS beside FINDINGS.md, and card him the propositions.
- `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN` — loop stopped; sitting prepared (1 bar, never_taut_straight_cord, still counts 7/7/8/5 sharp bends; braiding never built); NEXT: switch Archmagi to the gimmesomeslack tier per D:\ClaudeWork\rimmandrake\gss_sitting\PLAN.md and show him the counted bends so he rules which are really ugly.
- `RIMMASTER_FIX_ASH_FOOTPRINTS_AND_SAND_LABEL_AFTER_CLOSE` — fixed offline 38d347bfc2 on ralph/pyrelands (darker ash track sprites, buryDepth 0.3, RM_Ash label on ash maps), not deployed or seen; NEXT: at the next Pyrelands load deploy its DLL, biome XML, Languages English and Textures/Things/Tracks (plus 9994e0125f, eafc1a0436) and verify footprints and the label by bridge read.
- `RIMMASTER_LAND_PYRELANDS_BRANCH_397_COMMITS_BEHIND` — filed; NEXT: merge ralph/pyrelands onto main in a scratch clone resolving CLAUDE.md and FlowWorks DLL conflicts, publish, then run the Pyrelands proof suite on the landed build.
- `FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH` — loop stopped at 16 bars; NEXT: after GSS, prepare a live sitting the same way (offline plan first).
- `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL` — policy adopted, mining done (06-mined-live-bugs.md); NEXT: write the first seed-set scenario test under the real-types pattern and record the two-week measure start date (recheck 2026-11-22).
- `RIMMASTER_TRACE_PYRELANDS_PROOF_ROWS_THE_LOOP_DROPPED` — rows restored on the branch; NEXT: close it citing the landing sha once the Pyrelands branch lands.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `./game --why ... down` only stamps the ledger; it does not close RimWorld (a reboot helper lost ~15 min to it). (see: D:\ClaudeWork\rimmandrake\reboot3\PROGRESS.md)
- Staging scripts must not set lockRotation: stage_beast_grid.py locked every penned animal facing south and read as an art bug. (filed: lesson 35c4424806)
- A sitting map without raid controls lost a colonist to a raid while my advance loop unpaused over his pause. (filed: infrastructure/state/lessons/20261108T171957Z-BENCH-live-sitting-staging-must-apply-raid.md)
- jawa/spawn_pawn has no gender parameter; list_pawns has no gender: read it with jawa/pawn_get. (see: this handoff)

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (2) — the next seat's queue

- `RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES` — More south draws in front, game-wide: pawns among pawns, buildings among buildings, plants (MandrakePatches SouthDrawsFront)
- `RIMMASTER_LAND_PYRELANDS_BRANCH_397_COMMITS_BEHIND` — Land ralph/pyrelands on main (da4c0d4d9e + 9994e0125f, eafc1a0436, 58f0e73ade, the footprint/label fix): 397 commits behind; conflicts in CLAUDE.md an

## Commits

```
7933171e82 conversations: catch-up 1 record(s)
07144905b9 ledger: Pyrelands closed on the owner's card; sitting passes, follow-up landing item
423e9a7fe5 conversations: catch-up 2 record(s)
e024b2a5ac art_eval auto-judge pass 20261108_1037: fauna_auto_20261108_1037 (1 decision(s), 0 installed file(s)) (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE)
5a5f477145 lesson: selftest_gss_proof_drivers M21d expects 36 drip points, oracle now gives 48
00bc950e6f ledger: PYRELANDS_FINISH_ARTISAN_THIRD_TIME_WISER clone bundled
b20f2fccc9 conversations: catch-up 1 record(s)
9190458ffb ledger: detached run on PYRELANDS_FINISH_ARTISAN_THIRD_TIME_WISER ended
608a2a7bff MandrakePatches: more south draws in front, game-wide (pawns, buildings, plants)
4ad0fef2f6 ledger: sitting rulings (ash/plants/furnace passes, Quickgrass tint, sand ash, Firehawk and Porg flyer pass)
35c4424806 lesson: a rotation lock on staged live creatures freezes them on their south art; hot reload does not reload textures
457c107b2b stage_beast_grid: face the pens south without a rotation lock
7d3bffb389 stage_beast_grid: one of every beast of ours in a penned, labelled grid with a scale human per row (prepared, not yet run live)
f47a1cf8ac lesson: live sitting staging applies the raid controls; never touch time speed during a sitting
34478d316c ledger: RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL clone bundled
728376fecb ledger: RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL returned its clone
91cda5717e conversations: catch-up 1 record(s)
f9ef7f109b ledger: detached run on RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL ended
b059b5d39c ledger: RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL note
d331b50a77 Pocock 06: 66 live-found bugs mined (47 in callers), seed set, real-types pilot
... 7 more: git log --oneline df61f96b20..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-08T19:11:35Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   — previous window / art-scale tooling, not this session
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   — modset_builder backup written by today's tier applies (tool output)
 M infrastructure/state/art/events/BENCH.jsonl   — art-eval pipeline installs, NOT this session; see What the owner should see
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
?? cards.json   — previous window
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   — previous window (Nov 4 swap)
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   — today's prep helper renamed a stale Nov-4 swap marker
?? design/RimMandrake/2026-11-07-pocock-design/05-gpt-review-trial1.md   — pre-existing at session start (art_eval briefs / FlowWorks loop files), not this session
?? design/RimMandrake/designer_drawing_out.md   — Designer role, previous window
?? design/concepts/Pyrelands/coverage_verdict.json   — previous window
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   — Conductor 2026-11-05, unfiled lesson
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   — rimflow temp file left by a crashed projection
?? shortcuts.ps1.txt   — previous window
```

