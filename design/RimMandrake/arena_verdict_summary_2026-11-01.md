# The arena trial: what it showed and what it did not (1 November 2026)

## What it was
Three ways of having agents fix things were each given the same frozen list of 25 old repair jobs to redo, oldest first. Two judges (an Opus model and a GPT model) scored each result without knowing which way made it. The three ways were today's way ("v3"), a loop with an immediate separate tester ("ralph_a"), and a builder plus a critic ("trio"). The design asked for a rule, written before the first day, that names a winner only once enough jobs are in, including the newest third of the list. Until then the answer is "continue".

## How far each got (MEASURED, from the arm records)
| Way | Jobs finished | Why it stopped |
|---|---|---|
| v3 | 25 of 25 (MEASURED) | Finished the whole list on 31 October. |
| ralph_a | 9 of 25 (MEASURED) | Its own brake refused new work at job 10 on 1 November: the weekly account allowance looked too low (0.14 against a floor of 0.15, MEASURED). Then you ended the trial. |
| trio | 9 of 25 (MEASURED) | The same brake, 22 minutes later. Then you ended the trial. |

The brake is a spending guard built into the two new ways; it was not changed. At the last check the allowance reading was 0.09 and a watcher was still waiting at 9 jobs done. Job 10 had been started in both new ways and one failed build was thrown away, so it is not counted.

## Pass rates (MEASURED)
On the first nine jobs, the only ones all three finished, each way got 6 of 9 past both judges. The ways won different jobs: the two new ways passed two that v3 failed (jobs 4 and 6), and v3 passed two that both new ways failed (jobs 8 and 9). On those two the new ways never got their own tests clean, so they kept nothing and the unchanged code was rejected. Over its own first 12 jobs v3 had 7 accepted, 4 rejected and 1 the checker could not measure. Over all 25, v3 had 17 accepted, 5 rejected and 5 judged invalid in the log (of the 5, 3 are work the checks could not run on; 2 were a judge failing to start, later re-judged and accepted).

## Spend
Only a partial reading exists, so treat these as ESTIMATE and low trust. The meter was run once, early on 1 November, before the last jobs. It covered 6 tasks for ralph_a, 7 for trio and 25 for v3. Averaged per measured task, v3 cost roughly 500,000 weighted tokens, ralph_a roughly 200,000 and trio roughly 160,000 (ESTIMATE). That is not a fair comparison. The tasks differ, v3's total includes the hardest jobs, and the meter found no record at all of what trio's tester runs spent. GPT token counts came back as exactly zero in the meter; I did not probe why, so treat GPT spend as UNMEASURED. Cost per accepted job: UNMEASURED.

## What the data does not show
- No winner. The scoring program was last run on 1 November at 05:34 and returned UNMEASURED, not a verdict. The stopping rule needs jobs 18 to 25 from the new ways, and they stopped at 9. The rule's own status for this case is "trial cut short, undecided".
- No claim that either new way is better or worse. Nine jobs, tied 6 to 6 to 6, cannot separate them.
- Nothing about speed, about running jobs in parallel, or about spend per accepted job.

## What could bend even the nine-job tie
- Before job 9 the record of today's way was moved out of the workers' reach, because a safety check found a job's answer in it. Whether any earlier worker read it was not checked.
- The new ways ran later in the week and were stopped by the allowance; v3 ran when it was not low. As far as the records show, that limited how many jobs they did, not how any one came out.
- The trial program was updated once during the runs of v3 and ralph_a. For about two hours ralph_a's tests used newer code; that touched only job 2, which everyone failed.

## Honest bottom line
The trial can say that on nine matched jobs the three ways tied, and that the new ways never kept work their own tests failed, at the price of keeping nothing on two jobs. It cannot say which way is better, and no amount of reading the data will turn it into a verdict. Getting one would take both new ways running all 25 jobs and a fix to how tester spend is recorded.

Full job-by-job page and evidence: D:\ClaudeWork\rimmandrake\foundry_arena\verdict\arena_verdict.md
