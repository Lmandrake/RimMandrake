# BENCH_REBOOT_HANDOFF_202611101050 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611091157`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->

Claude is nearly out for the week; Codex has about 35% left, and it resets Tue 2026-11-10 ~10:40 PM PST. Owner, 2026-11-09: "Please switch to as much of the work as possible done by GPT. We are nearly out." So run work as Codex directly (`codex.exe exec --sandbox danger-full-access ...`, the batch pattern in design/RimMandrake/designer_codex_2026-11-09/run_batch.sh) or through the new `--runner codex` on Designer/Relentless/Whittle/Artisan (src/RimMandrake/Utils/agent_runner.py; roles/runner_options.md). Keep Claude to thin orchestration. He also granted full machine access to every Codex agent (standing_rulings.md, "Codex agents run with full machine access").

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->

- 23 owner-ready Designer question sets (at most 3 questions each), Codex dry runs of stages 0-1 for 22 Baroque biomes + AtmosphericBase: design/RimMandrake/designer_codex_2026-11-09/<Mod>/QUESTIONS_OWNER.md. A fresh GPT judge graded the drafts all B (JUDGE.md) and the owner versions apply its fixes. Show the judge's top five first: LeaningScrub, LongShade, GelatinousSlime, TheSump, Contagion. One file per sitting, by phone if he's away.
- HugeThings: GPT deep review (3 P1 bugs) and the Designer's questions 01-02 are waiting on him: design/RimMandrake/hugethings_codex_2026-11-09/.
- Audio: all 7 tools are installed except Freesound (needs his API key); 1,661 unique canon droid clips from 22 archives; GPT's pipeline review, audio-as-code review and ten experiments are in D:\Luke\dev\MandrakeAudio\research\2026-11-09_*.md. The first experiments to run, as GPT ranked them: 1 → 2 → 3 → 4.
- GSS cords approved and landed (a148b06ad4); the log alarm is split into load and play limits (ce04ffdae3), with its DLL deploy pending the next game-down.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->

- `RIMMASTER_RUN_CODEX_DESIGNER_TO_QUESTIONS_23_MODS` -- question sets committed (f147b68a38); NEXT: show him LeaningScrub's QUESTIONS_OWNER.md first, and record his answers with --owner-said.
- `RIMMASTER_FIX_HUGETHINGS_GPT_REVIEW_THREE_P1_FOUND` -- filed, unstarted; NEXT: run it with Codex (Relentless --runner codex, or a codex exec in a scratch clone), starting with review action 1 (strict live-runner aggregation).
- `RIMMASTER_TRY_CODEX_WHITTLE_ON_ONE_MOD_INTRIGUING` -- feasible (runner built, but no RimWorld Whittle has ever run, and Claude's hooks don't run under Codex); NEXT: once he answers one mod's questions, run `whittle/run.py --runner codex` on one small piece in a scratch clone.
- `LOG_BOUND_DECIDE_COLD_LOAD_ALWAYS_GUILTY` -- built ce04ffdae3, the companion DLL isn't deployed, and the close needs an Operations run (Ops is OFF by his choice); NEXT: at the next game-down, `python3 src/RimMandrake/bridgetools/build.py --gm --apply`.
- `RIMMASTER_TRACE_FULL_LIST_LOG_CRUD_SIX_OFFENDERS` -- report D:\ClaudeWork\rimmandrake\logspam\REPORT.md; NEXT: on the next full-list session, re-measure after the Intimacy/MCR silencing patch and the Beer guard.
- `RIMMASTER_POLISH_GSS_CORD_LEFTOVERS_AFTER_APPROVAL` -- about 20 deferred Codex findings; NEXT: give them to Codex one at a time, with no change to the cord look.
- Audio pipeline: no item yet; NEXT: file it, then run GPT's experiment 1 (recover the meaning of his audition decisions) with Codex in D:\Luke\dev\MandrakeAudio.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->

- Codex's Windows sandbox can't reach WSL, and Computer Use stops itself on an unconfirmed Chrome URL; use the Machinist route for bot-checked downloads (filed: lessons; Machinist LESSONS.md e61297e).
- A `rimflow note` on an item in `file` state flips it to `proposed`/`doing`; harmless, but don't read the state as progress (see: ledger).

## Closed since the last handoff (1)

- `STEVE_LANE_UNSTICK_PAUSED_UNOWNED_DD30` — c0000a4029

## Filed and still open (5) — the next seat's queue

- `RIMMASTER_POLISH_GSS_CORD_LEFTOVERS_AFTER_APPROVAL` — GSS cord leftovers after the owner's approval: Scrapper lead S-bend, plug-join slope, r3_13 crossing, faded wall plug, deferred Codex findings
- `RIMMASTER_TRACE_FULL_LIST_LOG_CRUD_SIX_OFFENDERS` — Owner asked what generates the crud in the full list log. Attribution in D:\ClaudeWork\rimmandrake\logspam\REPORT.md (logs ee0fbaa8, e50b27df). Follow
- `RIMMASTER_FIX_HUGETHINGS_GPT_REVIEW_THREE_P1_FOUND` — HugeThings: fix the GPT deep review's findings (3 P1: trunk-closure trapping is only checked locally, unbounded footprint work per tick, T3 meat-mount
- `RIMMASTER_RUN_CODEX_DESIGNER_TO_QUESTIONS_23_MODS` — Codex Designer dry runs (stages 0-1) on 22 Baroque biomes + AtmosphericBase: outputs in D:\ClaudeWork\rimmandrake\designer_codex\<Mod>\; commit them t
- `RIMMASTER_TRY_CODEX_WHITTLE_ON_ONE_MOD_INTRIGUING` — Trial Whittle (or Artisan) with --runner codex on one small whole piece from a mod with answered Designer questions; report how far it gets

## Commits

```
54d760c917 conversations: catch-up 3 record(s)
f147b68a38 design: owner-facing question sets (<=3 questions, plain words) for the 23 Codex Designer dry runs
fe0ce0b480 ledger: RUNNER ingest of 1 testq job(s)
ef9ba9d570 design: fresh GPT judge of the 23 Codex Designer question sets (all B; template faults named)
5fc1b7baaf design: Codex Designer dry runs (stages 0-1) for 22 Baroque biomes + AtmosphericBase, questions ready for the owner
1db614cc18 ledger: RUNNER ingest of 1 testq job(s)
120eec18ad ledger: RUNNER ingest of 1 testq job(s)
e778203767 ledger: RUNNER ingest of 1 testq job(s)
16f0422549 ledger: RUNNER ingest of 1 testq job(s)
b38ac112aa ledger: RUNNER ingest of 1 testq job(s)
4c3da9726b ledger: RUNNER ingest of 1 testq job(s)
bc9b4bbb74 ledger: RUNNER ingest of 1 testq job(s)
0c1219cd48 ledger: RUNNER ingest of 1 testq job(s)
36fd201477 ledger: RUNNER ingest of 1 testq job(s)
27a9c378b0 ledger: RUNNER ingest of 1 testq job(s)
ebae8a2d6d ledger: RUNNER ingest of 1 testq job(s)
bde007eb11 ledger: RUNNER ingest of 1 testq job(s)
bc9dba6c84 ledger: RUNNER ingest of 1 testq job(s)
db3efe23c5 ledger: RUNNER ingest of 1 testq job(s)
dbc554a611 ledger: RUNNER ingest of 1 testq job(s)
... 97 more: git log --oneline 9390ac1b5e..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-09T23:32:19Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   pre-existing at session start (not this session's; left untouched)
 M deployed/config/ModsConfig.before-tier-pyrelands.xml   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   pre-existing at session start (not this session's; left untouched)
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   pre-existing at session start (not this session's; left untouched)
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   pre-existing at session start (not this session's; left untouched)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   pre-existing at session start (not this session's; left untouched)
?? cards.json   pre-existing at session start (not this session's; left untouched)
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   pre-existing at session start (not this session's; left untouched)
?? deployed/config/ModsConfig.swap-active.weepingstones_solo.stale-20261108.json   pre-existing at session start (not this session's; left untouched)
?? design/RimMandrake/designer_drawing_out.md   pre-existing at session start (not this session's; left untouched)
?? design/concepts/Pyrelands/coverage_verdict.json   pre-existing at session start (not this session's; left untouched)
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   pre-existing at session start (not this session's; left untouched)
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   pre-existing at session start (not this session's; left untouched)
?? ralph/.context_warned   pre-existing at session start (not this session's; left untouched)
?? shortcuts.ps1.txt   pre-existing at session start (not this session's; left untouched)
```

