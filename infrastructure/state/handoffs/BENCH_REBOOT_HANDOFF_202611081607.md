# BENCH_REBOOT_HANDOFF_202611081607 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611080051`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Done means PROVABLY OK, not judge-approved (owner, 2026-11-08 ~1:20 AM: "I don't need the Judge to say it's ok. I just need it to be provably OK... if you have that evidence, call it, stop the spend, close the mod."). Each Artisan loop now has ralph/RATCHET.md (Remaining first, Proven locked with evidence) and its PROMPT reads it first; the evidence rule counts measurements for behaviour bars. That ratchet took Graffiti from 11 unseen to closed in five passes. The overnight watch is a SESSION-ONLY cron (dies with this window): re-arm an hourly round if loops are still running.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Graffiti CLOSED provably done** 7:30 AM (landed b967d9e9cb, deployed, not in his ModsConfig). He owes one wording line: mark_reads_at_play_zoom "every mark" -> "every face-on mark". Caveats in its DONE.md: daylight reshot not taken; "confront over painted-out work" unseen; proven on graffiti_solo, not his full list.
- **Pyrelands' 3-day replay on pass 20's build lost two colonists** (fire, a barbslinger): read before accepting its DONE.
- **GSS (1 bar left, 57.2M) and FlowWorks (16 left, 54.3M) are paused at their limits**; overnight top-ups stopped at the 15% weekly floor (lukas ~15% left, ~80 h to reset at 8 AM). Both need his token call.
- **His "nearly done, judging is wrong?" tested by four audits** (`D:\ClaudeWork\rimmandrake\conductor\apparatus_audit_<loop>_2026-11-08.md`): Graffiti ~70% apparatus, Pyrelands ~35%, FlowWorks ~20-38%, GSS 0%. Conductor edits he can veto: the evidence-rule rewrite and ratchet paragraph in each loop's PROMPT.md (backups `conductor\<loop>_PROMPT.before_*_20261108.md`); GSS's measurable pass rule for never_taut_straight_cord; game rank on SteveDesktop A and B = GSS first (`/home/mandrake/rm/scratch/BENCH/steve_games.py`).
- **Pocock trial 1 verdict** (offline selftests catch 0 of 25 caller mutants across Graffiti/KeelHoist/HugeThings, all kernel mutants; a scenario test caught 16/20): bring it to him in plain words.
- **Art push-through**: 7 creatures at the redraw cap (Niim, Noolim, Smogapillar, Vennick, Aveluthia, Candler, Gorg); a stray Eopie north candidate restored to his kept art, candidate at `D:\ClaudeWork\backups\eopie_north_stray_2026-11-07\`.
- Morning brief lines are at the end of `D:\ClaudeWork\rimmandrake\conductor\log.md`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `PYRELANDS_FINISH_ARTISAN_THIRD_TIME_WISER` — pass 21 running (69M limit), 21/22 proven, pyre_ashfall_darkens_drifts reopened by pass 20's ground-cover ash; NEXT: when its DONE.md lands, check the proof (and the two replay deaths) and close it per his provably-OK rule.
- `GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN` — paused 57.2M at 07:46, 1 bar (lamp hook / mast foot / heap fixed and deployed; 12-shot look half and braiding owed); NEXT: card him on more tokens.
- `FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH` — paused 54.3M at 06:06, 16 bars, GPT batch plan in its OWNER_NOTE; NEXT: card him on more tokens.
- `RIMMASTER_TRACE_PYRELANDS_PROOF_ROWS_THE_LOOP_DROPPED` — both dropped rows restored by the loop (16ded20755) and passing on the cleaned save; NEXT: close it citing the restored rows once the Pyrelands branch lands.
- `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL` — trial 1 finished 01:34Z; NEXT: give him the verdict in plain words and ask the next step by card.
- `RIMMASTER_WEIGH_ARCHMAGI_TWO_GAMES_ARTISAN_ONLY_HOW_MANY` — he chose one Steam account for both games (card 6:52 PM); NEXT: apply the 28 GB WSL cap and run the doc's Archmagi trial plan.
Every other pointer of BENCH_REBOOT_HANDOFF_202611080051 stands unchanged with its own NEXT.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- An open question card blocks the Conductor's hourly cron rounds; four loops paused unseen 20:08-00:32 (filed: lessons).
- A running ralph loop.sh reads its gate once at launch; an edited gate does nothing until restarted in GAME_WAIT (see: MandrakeWorkflows artisan/FINDINGS.md).
- steve_games: a holder restarting passes instantly starved a higher-ranked waiter; fixed in the live script (filed: lessons).
- A headless pass's background helpers are killed 10 min after its last turn (filed: lessons).
- ARTISAN_NOW counted a trap note as a bar and could not read tables or ratchets; fixed cd2f3266a9 (filed: lessons).
- Pyrelands suite passes never reached its count (behind an unrun visual step) (filed: lessons).
- Testing a gate hook delivers and overwrites the loop's pending OWNER_NOTE (filed: lessons).

## Closed since the last handoff (1)

- `RIMMASTER_STRIP_CANONICAL_SAVE_OF_CUT_FURNACE_HERDS` — 07ea56fac58b13e5d596bb76b5b577f83247ec86

## Filed and still open (1) — the next seat's queue

- `RIMMASTER_RESTORE_HOURLY_INSTALL_TIMER_PILE_GREW_UNSEEN` — Restore an hourly install of finished art renders (rm-donor-regen-install.timer is gone, last collect 2026-11-03; 61 finished renders sat up to 12.5 d

## Commits

```
4402dbf8c0 conversations: catch-up 2 record(s)
2e8222475d ledger: Graffiti closed provably done (verify L0 + close at b967d9e9cb)
fbf8b6594a lesson: the first Artisan landing (Graffiti): branch tip red on its own lint, the landing route, close wants a verify on the landing sha
8a84c64248 ledger: Graffiti landed b967d9e9cb, called provably done; close refused (no level-tagged pass), left open with a note
b967d9e9cb Graffiti: land the Artisan loop's mod (ralph/graffiti fd650c5589), closed provably done on the owner's order; 98 textures installed through the art ledger; lint: a stencil-run sigil (sigilCopies>1) needs no frame, as the mod's ConfigErrors already allows
db08bfe5fc lesson: a print-mode loop pass kills its background agents after 10 min idle
281944fe4e ledger: live sweep LIVE_RESTORE_DISPATCHER broken
f77216b9ef ledger: live sweep LIVE_RESTORE_DISPATCHER kept
afeaa58f06 ledger: overnight top-ups (FlowWorks, Graffiti)
cd2f3266a9 artisan_now: count bars from ralph/RATCHET.md when a loop has one
8db28948af lesson: steve_games starvation at pass boundaries
20e1ed0c72 ledger: his ratchet ruling for the Artisan loops
5a8cea46dc lesson: Pyrelands suite passes never credited
0c9ac9f102 lesson: Graffiti apparatus audit findings
dca9b90250 ledger: his 'provably OK' closing ruling for the four Artisan loops
238b8fceca ledger: his furnace-beast card (no heat cap; ignites grass it sleeps in)
77b2ec787b ledger: his 12:33 AM card, +10M to GSS, Pyrelands and Graffiti
439503bdbb lesson: an open question card blocks the Conductor's hourly rounds
2c60de73dd ledger+lesson: FlowWorks +10M by card; owner caps are absolute
51700c6694 ledger: his Graffiti look cards (trim wall mood, +10M)
... 33 more: git log --oneline 4746db686d..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-08T00:56:02Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art/events/BENCH.jsonl   art push-through helper (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE), left for its next run
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   predecessor seats: dirty before this session began, untouched by it
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   predecessor seats: dirty before this session began, untouched by it
 M src/RimMandrake/FlowWorks/Tools/native_water_audit.md   predecessor seats: dirty before this session began, untouched by it
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   predecessor seats: dirty before this session began, untouched by it
?? cards.json   predecessor seats: dirty before this session began, untouched by it
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   predecessor seats: dirty before this session began, untouched by it
?? design/RimMandrake/designer_drawing_out.md   predecessor seats: dirty before this session began, untouched by it
?? design/concepts/Pyrelands/coverage_verdict.json   predecessor seats: dirty before this session began, untouched by it
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   predecessor seats: dirty before this session began, untouched by it
?? infrastructure/state/queue/BENCH.md.tmp.1153431.1794098233190787055   predecessor seats: dirty before this session began, untouched by it
?? shortcuts.ps1.txt   predecessor seats: dirty before this session began, untouched by it
```

