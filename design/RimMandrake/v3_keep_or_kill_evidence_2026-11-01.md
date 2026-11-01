# Keep or kill v3: what we know, what we don't, and the date (2026-11-01)

For the owner, to set the date on `V3_JUDGMENT_DATE_DECIDE_KEEP_OR_KILL`. Readings are from about 19:20 UTC on 1 November.
Written by a helper of the Conductor. Nothing here changes a running system.

**The short version.**

- v3 did not lose a measurement. On the nine jobs all three ways have finished, all three passed six.
- v3 fell because of a rule: when nothing wins, the simplest way wins, and v3 is the least simple. We agreed that rule in advance.
- The trial tested one small part of v3: how a single helper builds and is checked. It did not test the six roles you designed. Those are all still running.
- Recommended date: **Thursday 2026-11-19.** That is the earliest day the three missing pieces of evidence can all exist. If one is still missing, it counts as "not shown" and the decision goes ahead anyway.
- The allowance conflict needs no change to the brake. Moving to the lukas account reopens it. Two small jobs are owed before that move, listed in section 6.

## 1. Words used here

- **v3**: the design from 26 October, with six standing roles (Conductor, Arbiter, Auditor, Operations, Producer, Innovator) and a test for whether it worked.
- **The arena**: the replay trial. Three ways of working each redo the same 25 past jobs, one at a time, from frozen code. Two independent AI judges (Opus and GPT) accept or reject each result.
- **ralph_a**: one worker in a loop, with its own tests and no critic. The simplest way.
- **trio**: a builder, a critic and a loop that counts rounds.
- **"v3" in the arena**: today's FOUNDRY helper instructions plus a fresh tester after the close. This is not the six roles.
- **relentless**: the worker pool running on the live queue since 31 October. It was never in the arena.
- **The refit**: this morning's rerun of the simulator against 30 days of real records.
- **The brake**: the check in the arms' loop that refuses to start work when the weekly allowance looks short. The code calls it the runway gate.
- **The watcher**: a small script that relaunches a stopped arm when the brake would let it through.
- **MEASURED**: read from a real record. **ESTIMATE**: came out of the simulator, or is arithmetic of mine that assumes something.

## 2. Why v3 fell away

You were told a solid design was off the table as inefficient. No measurement says that. Four things happened instead.

1. **We agreed a tie rule.** On 30 October you gave GO to three rules written before the trial: no clear winner means the simplest way wins, then no architecture work for about a month. The order of simplicity is ralph_a, trio, v3. So v3 can only win by clearly beating the others, and a tie counts against it. The trial was built to answer "do we need the extra parts?", so a tie meant "no".
2. **The compare page never reached you.** Its six decisions were skipped when you moved straight to the trial. Nobody laid out what a smaller v3 would keep. "Collapse" was decided as a test outcome, not by you looking at the jobs.
3. **The word "inefficient" was ours and had no number behind it.** The trial's analysis assumes ralph_a has half the capacity of v3. The refit showed that figure came from an unequal comparison: it credited v2 and v3 with parallel work and denied it to ralph_a. The Conductor has also said that writing "fewer roles" into this morning's plan was its own error, and took the line out (`eee6f85960`).
4. **v3 had real faults, but not the ones the trial tests.** The 29 October review found the rules lived in role prose that no program enforced. The Producer's limit on work in progress was one example. That points to weak enforcement. It does not show the jobs were wrong. Relentless then produced visible results fast, on different work, and it looked like a replacement. Nothing has compared the two.

## 3. What we have measured

**The arena, first nine jobs.** MEASURED. The source is FOUNDRY's page, `D:\ClaudeWork\rimmandrake\foundry_arena\verdict\arena_verdict.md`.

| Job | v3 | ralph_a | trio |
|---|---|---|---|
| 1, 3, 5, 7 | accepted | accepted | accepted |
| 2 | could not be measured | rejected | rejected |
| 4, 6 | rejected | accepted | accepted |
| 8, 9 | accepted | rejected, nothing kept | rejected, nothing kept |
| **Total** | **6 of 9** | **6 of 9** | **6 of 9** |

- Each side beat the other on two jobs. The new ways refused to ship on jobs 8 and 9 because their own tests never went clean. v3 shipped and the judges liked it.
- v3 alone has finished all 25 jobs: 17 accepted, 5 rejected, 3 could not be measured. In its first 12 it had 7 accepted, 4 rejected, 1 unmeasured.
- The official result is **UNMEASURED**. The analysis refuses to give a verdict, for reasons in section 5.

**Time.** MEASURED from the run logs, counting only the final attempt at each job, first nine jobs: v3 1.4 hours, trio 11.5, ralph_a 14.0. The refit counted differently and found ralph_a about three times slower on eight jobs. Both counts say v3 was much faster one job at a time, though the scoring reads no clock. I did not break down why.

**Spend.** No trustworthy number exists. On the six jobs all three have a spend record (reading from 05:34 today, in the project's weighted token units):

| Count | v3 | ralph_a | trio |
|---|---|---|---|
| Spend tagged to a job | 3.40M | 1.21M | 1.09M |
| Arm spend not tagged to any job (whole run so far) | 0.33M | 3.98M | 2.14M |

Depending on which row you count, ralph_a costs between about 0.35 and 1.4 times v3. The refit reads 0.85. Ralph_a's job 2 and every trio critic are missing from these counts. Treat spend as not known.

**Relentless.** MEASURED: 58 items done, 57 of them today, 76.5M spent, 0.62 returns per item on average. Blind checks fail about 20 to 25% of the time on the first 13 hours. Those are real items it chose from the live queue, so none of this compares with the arena.

**v3's own test.** The 26 October design said to stop and reconsider if, after a week, your keep-going messages had not dropped (31 a day to 26 or fewer) and accepted items had not risen. Both meters exist and both read **nothing** today (`v3.keep_going_per_day` and `v3.accepted_per_day` are empty). The test you set for v3 has never been read.

## 4. What the simulator estimates

Everything in this section is ESTIMATE, from `D:\Luke\dev\RimMandrake\design\RimMandrake\fanout_sim_refit_2026-11-01.md`.

- With several workers at once and no human, the simulator gives v3.4 about 39 sound closes a day (range 26 to 52) and ralph_a about 30 (range 17 to 47). The ranges overlap heavily.
- With you attending, v2, v3.0 and v3.4 are a dead heat.
- The simulator is known to miss. It under-predicts ralph-style throughput by about 40% against what relentless really did, and it over-credits the gain from adding workers. So its lean toward v3 is not firm.
- Its biggest unknown is the defect rate of ralph against v3. Nobody has measured that.

Honest reading: v3's only possible advantage over a simple loop appears when many workers run at once. The arena ran one at a time, so it could not see it. The simulator can see it but cannot be trusted on it.

## 5. Which comparisons are not yet valid

| Comparison | Why it is not valid today | Evidence needed | Earliest |
|---|---|---|---|
| Arena official verdict, v3 against ralph_a against trio | Only 9 jobs shared. The trial's rule requires the newest jobs (18 to 25) to have run. Spend not recorded. | Both arms run all 25, after the spend recording is fixed. About 13 more jobs each past 12, about 20 hours each. Spend on jobs already run cannot be recovered, so the spend half covers later jobs only (my reading). Neither step is ordered. | About 7 November if ordered after the weekly reset |
| Ralph or trio against v3 with many workers | Every arena job was one at a time. This is the question that could save v3's worker method. | The two-by-two experiment in section 8 of the refit: 2 and 6 workers, ralph and v3, 16 three-hour blocks, about 2 days, about 26M, with planted defects to measure defect rate. Not started. | About 10 to 12 November, after the test machine verdict around 7 November |
| Relentless against any arena arm | Different jobs, chosen by itself, checked by a different judge. Its numbers cannot be read against the arena's. | Run relentless as a side of that same experiment. | Same experiment |
| The six roles against no roles | Never tested. The trial's "v3" does not include them. | Your own test: a week of the keep-going count and the accepted-items count, read by the agreed tagger. | Tagger must be on by 12 November |
| Any way of working on a real mod | Every test so far is old jobs or queue items. | The pilot mission with its time ledger. Its finish line is not yet written with you. | Not before all 11 return-to-building rows are green; no date |

Other limits on the nine-job table: the new arms could read v3's record on jobs 1 to 8, because it was hidden only from job 9. ralph_a ran job 2 during a stretch the trial log marks as drift, and each arm crossed one code update. v3 got a second build on job 15 after a judge crash. Nine jobs is too few to separate three ways: a difference of one job means nothing.

## 6. The allowance conflict

**The conflict.** Both trial arms stopped themselves at job 10 this morning (ralph_a 10:46, trio 11:08 Pacific). Your card says to burn the system account down to about 10% and then move to lukas. The brake refuses below 0.15. That looks like a clash between 15% and 10%, but the two numbers are different kinds of thing.

The 0.15 is not a percentage of the week. It means "what is left would last 15% of the time until reset" (percent left, divided by burn per hour, divided by hours to reset). Today that is 23 / 2.3 / 72.9 = 0.14. At that burn the brake needs about 25% left, so it can never allow the run down to 10% unless burn drops a lot.

**Corrections to what has been written.**

- The lesson "arena runway gate stops ralph_a short of 12 while trio runs" says trio has no such brake. That is false. Trio and the v3 runner use the same code, and trio tripped 22 minutes later. Neither arm was starved relative to the other.
- FOUNDRY's page says neither arm had started job 10. That is also false. Each ran for over an hour on job 10 and finished one failed build.

**Does the stop harm the measurement?** Not the nine finished jobs. It affects job 10 a little, in both arms.

- Fair between arms: same brake, same job, both stopped between passes.
- Scoring reads no clock, so the pause costs nothing there.
- No judge had seen the work, so this is not a second look like job 15.
- Job 10 is altered. The build was in a temporary copy that is deleted on stop. Ralph_a keeps its count (1 of 3 tries used) and its failure note, but its next try starts from the original code. In a normal run it would continue on top of the failed try. Trio counts rounds from its log, so its round stays spent too. I did not check whether trio normally keeps code between rounds.
- So flag job 10 in both arms on the page and read results with and without it.
- The arms will also finish on a different account from the one they started on. That should not matter, since the model is the same, and the launch log records the model each time, which lets it be checked.

**The smallest fix: change no brake, no floor and no pinned code.** The brake reads whichever account is logged in. After the move to lukas it reads about 1.4 at today's burn (ESTIMATE), so it reopens without any edit and the watcher relaunches both arms. Everything stays comparable because no rule changed. System reaches 10% at about 01:00 to 03:30 UTC tomorrow (ESTIMATE); the Conductor's check is at 04:00 UTC. Jobs 10 to 12 then take about 4 to 7 hours.

Two jobs are owed, both for FOUNDRY and the Conductor:

1. **Re-arm the stop-at-12 watchers before 13:27 UTC on 2 November.** They were given 24 hours and quit then. After that an arm would run past 12 with nobody having decided that. Decide that on purpose (see section 7), do not let it happen by timeout.
2. **Check no arm is mid-pass at the moment of the switch.** The switch relaunches the fleet, and a killed pass burns a try. The brake could also reopen on system before the switch: with arms idle, burn may fall below about 2.0% an hour, and the 24-hour average was 1.92. So the switch step should look at the two arm units and wait for the current pass to end. Do not use the arms' STOP files for this: with both present the watcher exits and restores v3's record.

**If you want them running before the move:** set `RALPH_A_RUNWAY_MIN=0.06` in `launch_arm.sh` for both arms, and set the same floor in the watcher's script, where it is fixed separately. It would be comparable, because the floor only decides when a pass may start. But it invites a live build into the switch, so I do not recommend it for a gain of a few hours.

## 7. What can be saved

Nearly all of it. "Kill" in this plan has only ever meant fewer chairs doing the same jobs (`RIMFLOW_V3_SHRINK_FEWER_CHAIRS_SAME_JOBS`). Your list of what the human was doing is the part that stands. Against your four requirements:

| You asked for | v3 part that does it | State today |
|---|---|---|
| Windows restarted before they get too big, by Dispatch | The dispatcher and seat restarts | Working for FOUNDRY. Conductor's backstop is off, so it still needs a goodbye |
| A periodic Operations process that knows what sane looks like and tells someone who can act | Operations role, ops watch, bands and alarms | Caught and diagnosed the 6-hour jam, but the note went to nobody. Needs an acknowledgement and plan awareness |
| Relentless workers who know the testing traps and know when to call for review or help | Blind check at end of cycle, Test Pilot (adopted whatever the trial says), `--live` promises | Built. Blind rerun is enforced in one lane only |
| A Dispatch that keeps SteveDesktop busy, launches and cleans, finds idle agents, knows the plan | Dispatcher, Producer's picks, cleaner | Launching and cleaning work. Plan-aware busy-keeping is not proven |

Also worth keeping with no argument: the Arbiter's power to block a close (ruled this morning), pinned read-only trees for anything measured, pre-review before you see anything, and the six roles' job list as the checklist any smaller design must cover.

Your line "v2 thought it was done when it wasn't" is what the blind check and `--live` are for. They are the parts of v3 with the clearest claim.

## 8. Recommended date: Thursday 2026-11-19

**Why that day.** It is the option already recommended in the risk response, and it turns out to be the earliest date that works. Going backward:

| By | What must happen | Who |
|---|---|---|
| 2 Nov | Move accounts, arms reach 12, page corrected | FOUNDRY, Conductor |
| 4 Nov, about 20:00 UTC | Weekly reset. Allowance returns | none |
| 5 Nov | Order the spend fix and the arms' run to 25, or decide not to | Conductor |
| about 7 Nov | Test machine verdict | Conductor |
| 12 Nov | Keep-going and accepted-items meters reading, so a full week exists. Latest start for the many-workers experiment | FOUNDRY |
| 19 Nov | Reading day | Conductor reads, you rule |

An earlier date would mean ruling on the same nine-job tie. A later date gains nothing: the month of no architecture work ends about 1 December, and a 19 November answer leaves time to plan what comes next.

**What gets judged that day.** Two separate questions, because the evidence is separate.

1. **The worker method** (v3's helper brief against ralph_a). Keep v3's method only if it clearly beats ralph_a in the many-workers experiment, by more than the experiment's error of about 14 points. Otherwise the simpler method stands, as already agreed. Missing evidence counts as not shown.
2. **The six roles** against your own test: did keep-going messages fall to 26 a day or fewer, and did accepted items rise? For each role, also ask whether it changed any work that week. A role with no evidence counts as not shown. That sends it into the fewer-chairs design after 1 December with its job kept. It does not delete the job.

**Options I do not recommend.** "When data is complete" has no end: the spend gap on finished jobs can never close. "Retire the question because relentless replaced v3" is not supported, since relentless has never been compared with anything and uses much of v3 underneath. Judging by feel is what produced this confusion.

**If only one thing can be paid for,** run the many-workers experiment rather than finishing the 25. It is the only test that can show what v3 was built for.

## 9. Not checked

I read records and code and touched no arm. I did not verify the arena's judge verdicts, the simulator's arithmetic, or the role states in section 7 beyond the documents they come from. The experiment cost and the time for 25 jobs are estimates from the rates above. The role table's states are from `D:\Luke\dev\RimMandrake\design\RimMandrake\tentative_plan_after_v2_lessons_2026-11-01.md`, section 8a.
