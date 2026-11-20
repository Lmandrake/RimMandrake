# Context kept, not reloaded: where the pipeline throws away a loaded context (scan of 2026-11-20)

Item: RIMMANDRAKE_SCAN_PIPELINE_FOR_CONTEXT_THROWN_AWAY_THEN_RELOADED. Window: the 291 detached runs that started from
2026-11-17 04:33 to 2026-11-20 04:33 PST, and the Conductor and role transcripts of the same 3 days. This run changes no
code, brief, rule or record. The Conductor files tickets from the ranked list (§4).

The owner's words (2026-11-20, about 4:55 AM PST): "I'm trying to avoid the constant reloading of context for no gain
here. The needless churn of shutdown->reload context->figure out what to do when you literally started that way before
shutdown. That needs to STOP. I want you to scan for all places in the pipeline where we have wasteful loss of context
like that and figure out ways to route around it."

Not re-derived here (ruled tonight, items RIMMANDRAKE_ENACT_WRONG_CHECK_FIXED_IN_SITTING_NOT_RETURNED and
RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION): a wrong check and a judge-fixable mod fault are fixed in
the sitting; a blind judge that fixes gets one fresh reader; any role takes an available game.

## 1. The answer: the five costliest losses and the route around each

All figures are weighted_v2 tokens (Opus 5.5 unless named). "Orientation" is the part of a run before its first file
edit (the first Edit, Write, commit or `./publish`): the run reads its brief, the item, the code and the evidence. Over
all 284 measured runs, orientation was 193.6M of 722.9M weighted (27%), median 458k and 5.0 min per run [measured,
`runs_orientation.tsv`]. Orientation is not all loss: a judge or a blind reader must read. The five rows below are the
places where a run that had just ended held that context, and the next run paid for it again.

| rank | loss | measured cost, 3 days | route around it (cheapest first) |
|---|---|---|---|
| 1 | **A run that ends with work left is continued in a FRESH session.** `left_open_continue.run` calls `detached_helper.launch` with a new brief and no `resume_session`. | 24 continuations. 22 of 24 started under 2 min after their predecessor ended, so its prompt cache was warm. They spent **21.6M and 213 min before their first edit** [measured, `continue_gap.tsv`]. A warm `--resume` would have paid about 0.37M on turn one for those 22 [measured: predecessor's last context x the cache-read weight]. | Continue with `--resume` of the ended session when the gap is under the 1 h cache TTL and the predecessor's context is under the holder ceiling (400k, `modledger.json`). Else start fresh, as today. The machinery exists: `launch(resume_session=…)`, `stop_resume.session_of`. |
| 2 | **The Conductor window: 22 restarts in 3 days, and since 2026-11-18 13:00 a window held far over its limit.** The restart is held because the `run_end_wake.py` Stop-hook waiter counts as a "background command running", so the window never reaches a safe boundary. | Restart orientation **12.9M** (22 windows, median 527k and 5.2 min each) [measured, `conductor_windows_kind.tsv`]. Since 11-18 13:00 (12 windows): 1153 of 1585 Conductor turns ran over the 200k hard limit, peaks 224k to 467k; the re-read of the context above 200k cost **6.52M** [measured]. The Conductor log says why: "seat restart of BENCH held: background command(s) running: pid … run_end_wake.py" (7 escalations from 10:01Z to 12:31Z on 11-20). | (a) `seat_restart` ignores the `run_end_wake.py` waiter as a hold: it carries no work, and its pending file waits for the next window by design. (b) Then weigh the 200k hard limit by its danger (the "No limit without the danger it guards" rule): a restart costs about 527k; carrying 100k more context costs about 5k per turn, so a restart pays back only after about 100 turns at that excess [measured inputs; break-even is arithmetic]. (c) Compact in place instead of a kill and a fresh window [guess ~60% that the CLI's auto-compact threshold can be set for the window; not checked, a cheap check]. |
| 3 | **A stopped run is resumed after its cache died.** Two causes: an account switch (the prompt cache does not cross accounts), and a stop held over 1 h. | 18 of 33 resumes missed the cache on turn one: **13.8M** on those first turns alone [measured, `resume_first_turn.tsv`]. 9 of them are one batch at 19:00 to 19:04 PST on 11-18, after the switch stop at 18:43 ("steven read 55% … one point above the switching plan's soft line"): 4.73M, gaps of only 9 to 16 min. The other 9 waited 68 to 226 min (the write_now stop at 20:24 PST resumed at 22:15; the pause; a holder session 80 h old): 9.08M. The 15 resumes that hit the cache cost 0.85M in all. | (a) At the soft line, let live runs finish on the old account (no new starts); stop a run only at the hard line. (b) Resume a stopped run within 55 min. (c) A resume after 1 h is still not worse than a fresh run [guess ~80%: it rewrites the same context once], so keep resume as the route, only sooner. |
| 4 | **The road back: a router run, then one FRESH fixer per filed item, one at a time (max_live 1).** The pilot holder (`road_back_holder`, one run on every open road-back item from the 15k packet) runs only AFTER the per-item fixers are spent (`pilot_holders` reads `fixer_spent`). | 18 steward and fixer runs in 3 days: **8.31M orientation of 14.57M, 99 min** [measured]. Tonight's FlowWorks: router 518k plus four fixers 404k, 424k, 480k, 373k = 2.20M of 4.20M; 91 min from the visit's end (23:35) to the last fixer's end (01:06), 22 min of it in tick gaps between runs [measured]. Gimme Some Slack: router 501k, fixers 746k and 624k = 1.87M [measured]. | (a) For a pilot mod, the holder run comes FIRST: one run on all items of the visit (the fixer brief already tells each fixer to read every other failed line; one run does that once). (b) The in-game driver files its own failed lines at the end of its visit, while warm, and a zero-token check proves that each failed or UNMEASURED SUMMARY line maps to one filed item; the router run is then not launched. The drivers ended at 409k (FlowWorks) and 380k (Gimme Some Slack) context [measured], at the holder ceiling, so the driver files and the holder fixes; the driver does not fix. |
| 5 | **A certificate wait that no program and no role owns** (Gimme Some Slack, from 02:43 PST to past 04:46 PST, no run in flight). | 0 tokens, but at least **123 min** of the one advancing mod's time [measured: `reading.json` at 4:41 AM reads `for_min` 110 and the wait still stands]. The cause is in §2. | The fixer that edits a deciding test records `maturation.py red-seen` for it before it closes (it holds the fault knowledge then). If it did not, the tick resumes that fixer's session (warm: it ended 25 min before the wait began) with the one command. The strong check is red_seen itself: a planted fault applied, the test seen red, the fault reversed. |

The sum of the five measured costs is about 63M weighted over 3 days [measured, the rows above; row 2 counts restarts
and the over-limit excess, not the wakes]. Not all of it is saved by the routes: a resumed run reads a larger context on
every later turn. The saving is about 40M to 50M [guess ~60%: rows 1 and 3 save most of their figure, row 2 about half,
row 4 about the fixer orientations past the first].

## 2. Why the Gimme Some Slack certificate did not re-run by itself

[measured, every step]

1. Visit 2 ended 21:03 PST on 11-19. The mod then waited 227 min for the one launch slot (max_live 1, maturation_dispatch.json):
   FlowWorks held it with visit 2, its router and four fixers until 01:06. The router ran 01:10 to 01:23. The fixers
   ran 01:27 to 01:54 (RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES) and 01:58 to 02:18
   (RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE).
2. At 02:21 the tick started the zero-token certificate rerun `rm-cert-rerun-gimmesomeslack-1795170081` for build key
   `c40ef3151400`. It ended 02:43: ran 11 deciders, 0 failed, 24 skipped, published `4738210cf2`, `ok: false`.
3. The certificate now refuses only on clause `red_seen`: 18 bars on `T_CORE` and `T_STUB_JOINS`, "a deciding test
   nobody has seen fail (no recorded red run; it was grandfathered, then edited)". Every `green`, `ran_on_this_build` and
   `registered` row passes (29 of 29 each) [measured: `maturation.py certificate GimmeSomeSlack --json` at origin/main
   `0d60a3cf52`].
4. Both tests live in one file, `src/RimMandrake/Utils/selftest_gimmesomeslack.py`. The grandfather list
   (`design/concepts/GimmeSomeSlack/version/evidence/red_seen_grandfather.json`, written 11-18 14:17) holds blob
   `fb643ed3…` for both. The file is now `0c06e38e…`. The only commit to it since the grandfather list is `345366aa49`
   at 02:14 PST, by the second fixer: "GSS probe: a read of the laid set first finishes the build the component owes".
   There is no `version/evidence/red_seen.json` for the mod.
5. `stale_key` drops every `red_seen` refusal by design ("neither starts nor blocks the rerun"), so with only `red_seen`
   left it returns None, and `cert_rerun_decide` returns None. `cert_red_decide` acts only on deciders whose `green`
   clause is red; there are none, so it returns None too. Nothing launches. The row reads `wait`, so it is not an idle
   mod (`idle_owed_mods` is empty) and no idle alarm fires. Its fix is printed as a hand step ("plant a fault the test
   must catch and prove it: python3 src/RimMandrake/rimflow/maturation.py red-seen GimmeSomeSlack T_CORE --patch
   <fault.patch>") and the mod sits on the Needs Conductor list.
6. No brief tells a fixer to run `red-seen`: `fixer_brief`, `SELF_FIX_RULE`, `HOW_A_BAR_HOLDS`, the role files and the
   agent files do not name it [measured: grep].

So yes: the cause is a missing `red_seen` record for tests that a fixer edited. One edit to a shared test file
invalidated both deciders in it, the fixer that held the knowledge of the edit ended without the proof, and the only
road to the proof is a hand step that no tick, role or brief owns.

## 3. Every handoff, with the four answers

Columns: (1) what the ending run knows that the next run rebuilds, and what carries it today; (2) the measured cost;
(3) whether the fresh context buys something real; (4) the route, and the strong check that makes it safe.

| handoff | (1) lost, and what carries it | (2) measured cost, 3 days | (3) buys something? | (4) route and strong check |
|---|---|---|---|---|
| Run ends with a LEFT OPEN note, continued (`left_open_continue`) | Everything the run read and tried. Carried by the LEFT OPEN note and the old brief, quoted in a new brief. | 19 left-open continuations of the 24 (§1 row 1): 21.6M orientation for all 24 [measured] | Nothing: same model, same clone, same work. | `--resume` when warm and under 400k. Check: the item's own close or LEFT OPEN rule, as today; a missing transcript falls back to fresh, named in the record. |
| Lane ticket closed, the next lane ticket (`left_open_continue`, kind lane) | The lane's shared code and evidence. Carried by the lane brief. | 5 of the 24 continuations, gaps 0.3 to 0.5 min [measured] | Nothing. | Same as above. |
| Spend-cap stop, then resume (`spend_watchdog`, cap ≈3.75M) | Nothing is lost when resumed warm. Carried by the session. | 10 runs ended "exit-code/claude-error" at the cap [measured]. 8 were resumed in 1 to 38 min and hit the cache; 2 waited 68 and 121 min and missed: 1.68M [measured, `resume_first_turn.tsv`]. | The cap is the owner's spend stop: keep it. | Resume within 55 min (already the common case). |
| Account switch stops runs (`switching_plan.py`, at_easy_spot) | Nothing in the session; the cache dies with the account. | 9 resumes at 19:00 to 19:04 on 11-18 missed the cache: 4.73M [measured] | The switch is real; the stop at the soft line is not needed. | Drain at the soft line, stop at the hard line. Check: the switching plan's hard line still stops every run. |
| Owner or Conductor stop (write_now, pause), resumed later | Nothing in the session; the cache dies after 1 h. | 9 resumes after 68 to 226 min (incl. a holder 80 h old): 9.08M on turn one [measured] | The stop is his order: keep it. | Resume sooner where the stop allows; a stop that ends work for good should not be resumed at all. |
| Conductor window restart (`seat_restart`, hard 200k, soft 110k) | The whole sitting. Carried by the handoff and `seat_restart.py wake`. | 22 restarts, 12.9M orientation, median 527k, 5.2 min [measured] | It resets a growing context; the price of that is in §1 row 2. | §1 row 2. Check: a restart still happens at a real boundary (no helper alive, ledger shard published). |
| Conductor held over its hard limit (`run_end_wake.py` waiter) | Nothing lost; the cost is carrying. | 1153 of 1585 turns over 200k since 11-18 13:00; 6.52M excess; 187 run-end wakes in those windows [measured] | Nothing: a held restart is a defect. | `seat_restart` stops treating the waiter as a hold. Check: planted test, a window with only the waiter alive reads a boundary; a window with a real helper alive still holds. |
| Run end wakes the Conductor (`run_end_wake.py`) | Nothing lost; each wake is a turn on a 300k to 470k context. | 187 wakes since 11-18 13:00 [measured]; their own weighted cost is UNMEASURED (inside the window totals). | Real: he wanted results read at once. | Batch wakes that arrive within a few minutes; read with a zero-token summary first. Not ranked: could not separate its cost. |
| In-game visit, then the router (steward `exit_not_met`) | The live failures, what the driver saw and ruled out. Carried by SUMMARY.md and the rows. | 3 visit routers: 1.30M orientation [measured]; tonight FlowWorks 518k, Gimme Some Slack 501k | Little: routing is a classification the program can check. | The driver files its failed lines at visit end. Check: zero-token count, each failed or UNMEASURED line maps to one filed item caused by the visit. |
| Router, then one fixer per item (one at a time at max_live 1) | The mod's code and every failed line, read again by each fixer (its brief says to). Carried by the item prose. | 18 steward and fixer runs: 8.31M orientation of 14.57M, 99 min [measured]; FlowWorks tonight 22 min of tick gaps [measured] | Nothing: same model, same mod, same visit. | §1 row 4: the holder on all items first. Check: each item closes on its own before/after acceptance test, as today. |
| Fixers spent, then the holder (`pilot_holders`) | The order is the loss: the holder comes last. | Included above. | — | Flip the order for pilot mods. |
| Fixers end, certificate waits on red_seen | The planted-fault knowledge of the fixer that edited the test. Carried by nothing. | Gimme Some Slack: ≥123 min, 0 tokens [measured] | Nothing. | §1 row 5. Check: red_seen itself. |
| Certificate stale stamps, zero-token rerun (`cert_rerun_decide`) | Nothing: a program reruns. | Gimme Some Slack 02:21 to 02:43, 0 tokens [measured] | — | Already the cheap route. Keep. |
| Certificate red deciders, one builder (`cert_red_decide`) | The red rows; carried by the certificate rows in the brief. | 1 run in 3 days (RIMMANDRAKE_GREEN_GIMMESOMESLACK_T_STUB_ART_CENSUS_RED_DECIDER): 523k orientation, 17.7 min [measured] | Little; a red that a just-ended fixer made is warm in that fixer. | When the red's file was edited by a run that ended under 1 h ago, resume that run. Check: the decider goes green and red_seen holds. |
| Visit or cycle to the next blind judge | The judge's reading. Carried by nothing, on purpose. | 3 blind judge runs: 0.89M orientation [measured] | **Yes: an independent verdict** (spec §3.6; `holder_launch` refuses to resume a judge). | Keep fresh. |
| Judge to fixer | Ruled tonight (fixed in the sitting). | Not measured here. | — | Not re-derived. |
| Void, then a fresh relaunch of the same item | Everything the voided run did. Carried by its notes, if any. | 17 fresh relaunches of an item that had a run: 10.2M orientation, 101 min [measured] | Nothing when the void was a system fault; a model change when the Conductor changed it (not separated). | Resume the voided session when warm and under 400k; fresh only when the model changes. Check: the void still spends no trial. |
| Pilot holder rotation at 400k (`modledger.resume_plan`) | The holder session. Carried by the ledger packet (15k budget). | FlowWorks visit 2 resumed a holder 80 h old: 410k on turn one [measured] | Yes, past 400k: a smaller context. | Keep; the packet is the written state the next run needs. |
| Designer stage inner steps (`designer_stage.py`) | Could not look in depth. The exam Readers and the Challenger are fresh by rule. | 5 headless Designer role runs on 11-17: 2.11M [measured]; inner subagents UNMEASURED | The exam's fresh Readers buy a blind read. | Could not look: not classed clean. |
| Headless role runs (Conductor role, Operations role) | Each run read its role file again. | 38 runs from 11-17 05:15 to 11-18 11:53: 6.71M; none since [measured] | — | No run since 11-18 11:53; cause not looked at. |
| Fable rescue (`maturation_rescue.py`) | A model change. | 1 run (RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX): 8.91M total [measured] | **Yes: a model change.** | Keep fresh. |
| Coverage judge, walk brief (Stage 7), findings judge (timer) | Fresh by rule. | Findings judge 3 runs, 0.88M [measured]; the others UNMEASURED | **Yes: a blind read.** | Keep fresh. |
| Test Pilot (`rimflow pilot`, rm-testpilot) | Could not look: no run of it is named in the 3 days' records. | UNMEASURED | — | Could not look. |

## 4. Proposed changes, ranked

Each change names its files, its strong check, what could go wrong and its acceptance test in one line. The Conductor
files from this list.

1. **Continue by resume, not by a fresh brief.** Files: `src/RimMandrake/rimflow/left_open_continue.py` (`run`, `plan`),
   its boundary page `design/specs/2026-11-19-run-end-continue/boundary.md`. `run` passes
   `resume_session=SR.session_of(rec)` when the gap is under 55 min and the predecessor's last context is under
   `holder_context_ceiling_tokens`; the header text goes in as the resume prompt; else fresh, as today, with the reason
   in the record. Strong check: the item's close or LEFT OPEN rule is unchanged; a fixture where the transcript is gone
   must fall back to fresh. Could go wrong: a run that ended confused keeps its confusion (mitigation: the `owed` kind and
   the 3-per-day alarm stay; a second continuation of the same run goes fresh); a context near the ceiling grows past
   it. Acceptance test: a selftest where a success run with a LEFT OPEN note, session S, gap 1 min and context 300k makes
   `run` call launch with `resume_session=S`, and context 450k, gap 70 min or no transcript each call it with none.

2. **Stop the `run_end_wake.py` waiter from holding the Conductor's restart.** Files:
   `src/RimMandrake/rimflow/seat_restart.py` (the background-command hold), `src/RimMandrake/rimflow/run_end_wake.py`
   (the waiter's command line is the name to match). Strong check: a planted case with only the waiter alive reads a
   boundary; a planted case with a real background command alive still holds. Could go wrong: a match too wide lets a
   real command die (match the exact hook path only). Acceptance test: a selftest of the hold reader on a process list
   with `python3 …/.claude/hooks/run_end_wake.py` alone returns no hold, and with that plus `./sync` returns one hold.
   Then, as a second ticket, weigh `backstop_hard_tokens` 200000 against the measured 527k restart cost (the limit must
   name its danger and evidence) and look at compaction in place.

3. **Drain at the switching plan's soft line; resume within the hour.** Files: `src/RimMandrake/Utils/switching_plan.py`
   (the at_easy_spot stop), `src/RimMandrake/rimflow/stop_resume.py` (when a stopped run is resumed). Strong check: the
   hard line still stops every live run; the account order and leave lines are unchanged (they are his). Could go wrong:
   an account runs past its soft line by what the live runs spend (bounded by the hard line, which still stops them).
   Acceptance test: a selftest where the plan at soft line minus 1 point returns "no new starts" and no stop for live
   runs, and at the hard line returns a stop for each.

4. **The holder first on a pilot mod's road back, and the driver files its own failures.** Files:
   `src/RimMandrake/rimflow/maturation_dispatch.py` (`pilot_holders`: drop the `fixer_spent` precondition for pilot
   mods), `src/RimMandrake/rimflow/maturation_autonomy.py` (`steward_brief` `exit_not_met`), the in-game driver brief
   (`maturation.py` launch_stage text). Strong check: each item still closes on its own acceptance test (fail on base,
   pass on the fix); a zero-token check that every failed or UNMEASURED SUMMARY line of the visit maps to one filed item
   before the holder launches. Could go wrong: a driver classes its own faults as SITE or HARNESS to pass (the
   zero-token map check and the next blind judge or visit still see them); one holder on many items stops halfway (its
   LEFT OPEN goes through change 1). Acceptance test: a tick selftest where a pilot mod at in_game with 4 open road-back
   items launches one holder with all 4 ids and no per-item fixer.

5. **The fixer that edits a deciding test owes its red_seen proof.** Files: `src/RimMandrake/rimflow/maturation_autonomy.py`
   (`fixer_brief`: one line that names `maturation.py red-seen` for any decider whose file the run changed),
   `src/RimMandrake/rimflow/maturation_dispatch.py` (a certificate whose only refusals are `red_seen` reads `owed`, not
   `wait`, and resumes the run that last changed the decider's file when it ended under 1 h ago; else one fresh run on the
   item that owes it). Strong check: red_seen itself (the planted fault seen red and reversed). Could go wrong: a planted
   fault that is too weak passes red_seen (the planted patch must touch the code the decider reads; red_seen already
   refuses a patch to the test itself). Acceptance test: a dispatch selftest where a certificate with only red_seen
   refusals on a decider edited by unit U (ended 25 min ago) gives decision `launch` with `resume_session` of U, and with
   U ended 2 h ago gives `launch` of one fresh run; today both give None.

6. **Resume a voided run's session when the void was a system fault.** Files: `src/RimMandrake/rimflow/stop_resume.py`,
   `src/RimMandrake/rimflow/maturation_dispatch.py` (`void`). Strong check: the void still spends no trial; a model change
   still starts fresh. Could go wrong: a session voided because it went wrong is resumed into the same error (resume only
   on `void_system`, never on a hand void with a reason). Acceptance test: a selftest where a `void_system` run with a
   warm session relaunches with that session and a hand void relaunches fresh.

## 5. Method and sources

- Run records: `/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached/*.json` (fields `at`, `ended`, `result`, `tokens`,
  `session`, `resume_session`, `continued_from`), 291 runs in the window, 286 with a transcript found.
- Transcripts: `~/.claude/projects/<clone path>/<session>.jsonl`; each run is measured only inside its own launch-to-end
  window (a resumed session's file holds the runs before and after it). Weights: `role_launch.MODEL_PRICES`, through
  `role_launch._weigh` and `_split`. The record's `tokens` and the transcript measure agree within 10% on 236 of 273
  runs; the rest are resumed or killed runs and runs with subagents.
- Scripts, all read-only, in this folder: `measure_orientation.py` (→ `runs_orientation.tsv`),
  `measure_resume_first_turn.py` (→ `resume_first_turn.tsv`), `measure_continue_gap.py` (→ `continue_gap.tsv`),
  `measure_conductor.py` (→ `conductor_windows.tsv`; `conductor_windows_kind.tsv` adds the kind from each window's first
  prompt).
- Dispatch state: `/mnt/d/ClaudeWork/rimmandrake/dispatcher/maturation/{state.json,reading.json,voids.jsonl,cert_rerun/}`.
  Conductor log: `/mnt/d/ClaudeWork/rimmandrake/conductor/log.md`.
- Traps: "before first edit" is a proxy for orientation; a driver or a judge edits late by its nature, so their rows are
  not read as loss. A cache "MISS" is a first turn whose cache write is larger than its cache read. The warm-resume
  figure is turn one only; later turns of a resumed run read a larger context than a fresh run would.
