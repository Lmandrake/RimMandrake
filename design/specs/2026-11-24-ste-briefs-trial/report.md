# Trial: the Conductor writes six helper briefs in Simplified Technical English, checked before the launch

Item: `RIMMANDRAKE_TRIAL_STE_BRIEFS_CHECK_BEFORE_LAUNCH_NOT_AFTER`. The owner, 2026-11-24: *"Perhaps you should use STE
on your briefs. Would be an interesting trial."* The shape of the trial, his words: *"Just do binding then STE. Let's get
a single snapshot."* The length of a brief, his words: *"It's ok for your briefs to run longer. They're not re-used, so
no need to trim."*

## What the trial measures

Each trial brief is written in two passes of the clear-findings skill. The binding pass makes each word point at a thing
that the reader can name in one step. The STE pass then puts each sentence into Simplified Technical English. The
Conductor then corrects the brief until `guiding_prose.py` reads 0 faults, and launches it. Three readings are taken for
each brief:

1. the faults that the launch check read at the start;
2. the correction notes that the Conductor wrote on the item after the start;
3. whether the run's report shows that it did the task as meant.

The source of reading 1 is the run records of the check: `runs.jsonl` in `D:\ClaudeWork\rimmandrake\dispatcher\guiding_prose`.
A row with door `launch-returned` is a brief that the launch gave back before the start.

## The baseline: eleven Conductor briefs of 2026-11-24, 1:35 to 8:20 AM PST

Each brief had 1 to 6 faults in its new sentences at the start. Four of the eleven needed a correction note after their
run had started (the item's title, written by the Conductor on 2026-11-24).

## The six trial briefs

| n | item | words | faults at the start | correction notes | did the task as meant |
|---|---|---|---|---|---|
| 1 | `RIMMANDRAKE_PROPOSE_FULL_LIST_WALK_NOT_PER_MOD_ARCHBIG_IS_THE_LINE` | 855 | 2 in 79 new sentences | 1 | owed |
| 2 | `RIMMANDRAKE_RESTORE_FIVE_BAR_CLAIMS_THE_NIGHT_SHRINK_TOOK_OUT` | 793 | 3 in 72 new sentences | 0 | yes: five claims restored at `383784cb3ede`, about 9 minutes |
| 3 | `RIMMANDRAKE_READ_STEWARD_FORECAST_FIX_ONCE_FRESH_EYES` | 643 | 0 in 37 new sentences | 1 (the page that the brief names moved when its item closed) | owed |
| 4 | `RIMMANDRAKE_RETURN_CLONE_UNDER_OLD_POOL_NAME_KEPT_SILENT` | 699 | 3 in 43 new sentences, returned before the start; 0 at the second launch | 0 | owed |
| 5 | `RIMMANDRAKE_SPARE_RESTART_CUT_BY_ACCOUNT_END_FIRST_SWITCH` | 822 | 3 in 50 new sentences, returned before the start; 0 at the second launch | 1 (a false sentence: the brief said that the Conductor had started a run by hand, and the launch of that run was refused) | owed |
| 6 | `RIMMANDRAKE_READ_FRESH_HOST_FACTS_NEGATIVE_AGE_CRIED_STALE` | 718 | 0 in 38 new sentences | 0 | owed |

Rows 3 to 6 were launched on 2026-11-26 between 3:48 AM and 4:03 AM PST. The Conductor wrote each of them in one pass,
with the binding rule and the STE rules in mind. The Conductor did not run the two passes of the clear-findings skill
on them. The six faults that the launch gave back were 3 pronouns and 3 undefined terms. Both correction notes repair
a wrong fact, not unclear wording: the prose check does not read facts.

Briefs 1 and 2 were launched with faults, so the step "correct until 0 faults" was not done for them. The launch check at
that time ran after the start only.

## The trial stopped after brief 2 (measured 2026-11-25)

The six Conductor launches after brief 2 were not written or recorded as trial briefs. Their faults at the start were 2,
3, 6, 8, 5 and 1 (2026-11-24, 9:32 to 11:36 AM PST). From brief 2 to 2026-11-25 6:18 AM PST, 59 Conductor launches have
a record, and 8 of them read 0 faults at the start. A check that the writer must remember to run before the launch was
not run.

## The launch now gives the faults back before the start

From the commit that lands this page, a launch from the Conductor window reads the brief before the start. A brief with
a fault starts nothing, exits 5, and names each fault with its repair. A corrected brief is read again. The same brief,
launched again with no change, starts as written. Page: `design/specs/2026-11-23-guiding-prose-check/boundary.md`,
promise `a-principal-launch-gets-its-faults-before-the-start`.

Rows 3 to 6 are the next four Conductor briefs written binding then STE, launched through this check.

## Report

The line below is written when the report of the six briefs goes into his daily digest.
