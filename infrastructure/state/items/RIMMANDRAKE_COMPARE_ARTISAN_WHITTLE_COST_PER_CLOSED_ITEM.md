# Compare builders: Whittle, Artisan, Relentless (cost per accepted item)

As of 2026-11-11 12:20 PST. Whittle may still move: fw-drain round 13 and ht-loop round 8 were still finishing
after the 12:00 PST stop. Every figure is tagged MEASURED, ESTIMATE or UNMEASURED.

"Accepted" means closed in the rimflow ledger, or approved by the owner. A builder's own claim does not count.

## findings

| | Whittle fw-drain (Codex, Archmagi) | Whittle ht-loop (Codex, SteveDesktop) | Artisan (Claude ralph loops) | Relentless (Claude pipeline) |
|---|---|---|---|---|
| Window | 2026-11-10 22:58 to 11-11 11:36 PST, about 12.6 h (MEASURED) | 11-11 01:17 to 10:12 PST, about 8.9 h (MEASURED) | from 11-06 22:00 PST; 4 loops, 65.2 run-hours in total (MEASURED) | 10-31 to 11-06 18:22 PST, when the owner stopped it; about 6 to 7 days, up to 8 workers at a time (MEASURED) |
| Accepted | 15 items: 14 closes and 1 supersede; open lane 68 to 53 (MEASURED) | 9 closes. It also filed 9 new items, so the lane went 44 to 49 to 44 (MEASURED) | 3 whole mods: Graffiti, GSS, Pyrelands. FlowWorks is still open at 14 of 30 bars (MEASURED) | 1039 distinct items closed with "relentless: blind check passed" (1155 close events) (MEASURED) |
| Size of one accepted unit | One small defect or proof: a selftest fix, a harness fix, a live proof | Same, but more live-game work | One whole mod, finished to the owner's eye | Mostly small system items. The largest name groups are OPS 102, RELENTLESS 68, SELFTEST 54, NIGHTLY 51, GAMEENV 24 and CHECKER 21: 320 of 1039 (MEASURED) |
| Tokens per accepted unit | Outer rounds 1-12: 3.27M tokens for 13 items, about 0.25M each (MEASURED). The inner build and judge processes are extra: 193M input (mostly cached) plus 0.61M output over the 10 items that recorded spend, about 19M input each (MEASURED). The killed round 1 and the tank-theft timeout run are UNMEASURED | UNMEASURED: the outer run logs are not mirrored. Four inner runs read 13M to 45M input each (MEASURED) | Graffiti 53.7M, GSS 57.2M, Pyrelands 70.7M; 60.6M per closed mod. Counting FlowWorks' 54.4M as overhead, 78.7M per closed mod; adding its 10.7M of helpers too, 82.2M (MEASURED, Artisan weighting). The Conductor's finishing work on GSS outside the loop is not in these figures (UNMEASURED) | 1.88B input-equivalent tokens in total, at most 1.81M per closed item (MEASURED, Relentless weighting; see caveats) |
| Quota per accepted unit | Both loops share one Codex login: 3% used at 01:17, 38% at 12:13 PST, so 35 points while 21 of the 24 items closed. About 1.7% of a weekly allowance per item (ESTIMATE) | (shared with fw-drain) | UNMEASURED per item. The owner's own figure is about 1.5 Claude Max accounts used up per week across all Claude work (ESTIMATE). The two Artisan accounts read 99% and 91% of the week used (MEASURED) | UNMEASURED per item |
| Wall time per accepted unit | about 50 min (12.6 h / 15) (MEASURED) | about 59 min (8.9 h / 9) (MEASURED) | about 18.5 run-hours per closed mod (55.4 h / 3), or 21.7 h counting FlowWorks' 9.8 h (65.2 h / 3), with about 15 h of waiting for a game across the loops (MEASURED) | About 9 to 10 min of calendar time per close with up to 8 workers in parallel (ESTIMATE). An item built for live proof took a median of 21 h to its first live verdict (95th percentile 78 h, 106 items) (MEASURED) |
| Live-test yield | Live proofs passed on reel inlet, railing toggle, pump outflow and tank theft. The first railing reader failed and was fixed; the first tank-theft runner timed out and was retried. One item was superseded, not built. The other 10 closes were offline fixes (MEASURED) | Two live L2 closes, settings and titan passage. The juvenile-passage item needed 5 live attempts and 2 Test Pilot sittings (MEASURED) | Pyrelands and GSS passed live with the owner (MEASURED) | 1363 live-proof rows: PASS 195 (14%), FAIL 134, UNMEASURED 659 (48%), REFUSED 149, NOT_ADMITTED 128, void 98. Of the 329 rows that measured anything, 59% passed (MEASURED) |
| Judge pass rate | All 12 completed rounds had an independent judge, and every one passed (MEASURED) | Every close had a judge. Redone judges: reefback-calf had 2 interrupted before the third was accepted; reefback-combat's first judge was refused for input scope; two-hour-warning had 1 aborted judge (MEASURED) | Graffiti blind judge: 21 true, 0 false, 1 cannot-tell at done (earlier pass 2: 6/3/1). GSS pass 1: 9/1/1. Pyrelands was judged by the owner live (MEASURED) | A shadow exam re-checked 65 done items: 39 green, 25 red, 1 unclear. The exam was new: its own code records that 16 of the first 18 shadow reds were faults in the exam (relentless_exam.py), so this is weak evidence either way (MEASURED, weak) |
| Owner questions raised | None new; its questions file predates the loop (MEASURED) | 3 parked and none sent (MEASURED) | FlowWorks 7 (answered), Pyrelands 1, GSS has a QUESTIONS.md (count UNMEASURED), 3 LOOK.md requests; the dashboard shows "Needs you: 10" (MEASURED) | UNMEASURED (no owner-question tally found) |
| Redone work | Two retried runners (railing, tank theft). 1 item superseded rather than built (MEASURED) | 2 failed runs, then a third, on passage-pool; 1 failed launch on native-letter (MEASURED) | GSS was finished by the Conductor outside the loop. FlowWorks spent 54.4M against a 20M cap and is half done (MEASURED) | 54 items were closed more than once, for 116 repeat closes. The pipeline itself took 109 commits to relentless*.py on 11-06 alone (MEASURED) |

## caveats

- **Token units differ, so the rows above do not compare directly.**
  - Artisan counts input, output and cache writes once each, and cache reads at one tenth.
  - Relentless counts input once, output 5 times, cache writes 1.25 or 2 times, and cache reads at one tenth. Every one of its weights is at least Artisan's, so its 1.81M per item is an upper bound in Artisan units.
  - Codex reports raw input with cached input included and unweighted, plus output. The 19M inner figure is mostly cache, so a Codex token count must not be set against a Claude token count.
- **Codex against Claude: the closest basis available is share of a paid weekly allowance, and only the Codex side is measured.** Equal percentages of two different plans need not cost the same money.
  - Whittle used about 1.7% of one Codex login's week per item.
  - The Codex plan's price is UNMEASURED.
  - Claude's cost per item in account-weeks is UNMEASURED. To measure it, read an account's weekly percentage before and after a loop.
- **The Codex quota is shared.** gpt_consult and any other Codex use on that login count against the same 35 points, so 1.7% per item may overstate Whittle, by an amount that is UNMEASURED. fw-drain's first 3 items closed before the first quota reading, which is why the window counts 21 items, not 24.
- **The units of work differ a great deal.**
  - A Whittle item or a Relentless item is one small fix.
  - An Artisan close is a whole mod accepted by the owner, built from 10 to 22 bars.
  - If one bar were as big as one small item, a mod would be 10 to 22 times a Whittle item (ESTIMATE; that equivalence is not measured).
  - Cost per accepted item therefore favours Whittle and Relentless by construction. Compare like with like: a Whittle item against one Artisan bar, or a mod's worth of Whittle items against one Artisan mod.
- **Relentless closes were judged by its own blind checker, not by an outside judge or the owner.** The owner stopped it on 2026-11-06 at 18:22 PST ("Stop the pipeline immediately"). The night before, he had asked how to overcome "this failure of our testing apparatus, weak evidence, poorly specified tests". Its 1039 closes are ledger-closed but carry less evidence than a Whittle close. At least 320 of the 1039 (31%) carry system names (OPS, RELENTLESS, SELFTEST, NIGHTLY, GAMEENV, CHECKER), which fits the 2026-11-03 ruling that it fixes the system first.
- The Artisan "Tokens today" dashboard figure is wrong; old Pyrelands passes read as today. Filed as RIMMANDRAKE_FIX_ARTISANNOW_OLD_PASSES_DATED_TODAY.
- The Pyrelands ralph unit ran 3 empty passes after its item closed (rc 127), then stopped itself. Filed as RIMMANDRAKE_FIX_RALPH_PYRELANDS_SPINS_AFTER_CLOSE.
- Sources:
  - /mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/ and /mnt/d/ClaudeWork/rimmandrake/codex_steve/ht-loop/ (loop.log, final.N.md, run.N.log, whittle spend files)
  - /mnt/d/ClaudeWork/rimmandrake/conductor/ARTISAN_NOW.md and ralph_*/events.log
  - /home/mandrake/rm/relentless/live/runs.jsonl, /home/mandrake/rm/relentless/store/spend-*.json and `relentless.py reading`
  - the ledger shards
  - Working tallies: /mnt/d/ClaudeWork/rimmandrake/compare_builders/

## recommendation

- **Whittle: keep it as the default builder for bounded items.** That means one defect, one selftest, or one proof in a named lane.
  - It is the cheapest measured in allowance share, about 1.7% of a Codex week per item (ESTIMATE).
  - It closes roughly one item an hour per machine.
  - Every close has an independent judge, and it rarely asks the owner anything.
  - Live-heavy lanes such as HugeThings cost more retries, so give those lanes a Test Pilot early rather than a fifth attempt.
- **Artisan: use it only for whole-mod finishing, where the owner's eye is the acceptance.** It is the only builder that produced owner-accepted mods (3), but it costs about 60 to 82M weighted tokens and about 18 to 22 run-hours per mod.
  - Hold it to its token cap. FlowWorks went to 2.7 times its cap at 14 of 30 bars.
  - Stop a loop when its item closes.
  - Hand its small defects to Whittle rather than letting the loop grind them.
- **Relentless: do not bring it back in its 2026-11-06 form.**
  - It closed a great many small items, but about half of its live-proof rows measured nothing.
  - Its own checker was the only judge.
  - At least 31% of its closes carry system names (OPS, RELENTLESS, SELFTEST and so on), not mod content.
  - It spent 1.88B input-equivalent tokens (its own weighting) in about a week.
- **If it returns, return only the queue.** It would choose and order offline items, and each item would be built and judged Whittle-style: one fresh builder per item, an independent judge, and a ledger close. There would be no self-repair work and no live lane. Its first days would be read against the 11-06 baseline in RELENTLESS_MEASURE_THREE_DAY_CHECK_NOV9 before it is widened. This is a smaller pipeline, not a new rule inside the frozen one.
