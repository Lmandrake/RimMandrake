# dregen_ generation failures, 2026-10-19 (measured from `D:\Luke\dev\_artpipe\failed\dregen_*.manifest.json`, done\ manifests, file mtimes)

Instrument note: 280 failed manifests found (status table says 279; one has likely landed since). Counts below are over the 280.

## Verdict: one cause. HTTP 429 Too Many Requests from the codex backend, in a ~2 hour window. Not content, not prompt, not references.

| class | count | share | evidence |
|---|---:|---:|---|
| 429 rate limit on all 3 attempts (worker exit 1, `image_present=False`) | 270 | 96% | every one of the 270 `worker_stderr_tail` ends `ERROR: exceeded retry limit, last status: 429 Too Many Requests`. Attempts fail in 12-25 s each, total 38-120 s. `timed_out` false on all. |
| derived facing impossible: master east failed | 10 | 4% | note `master <id> failed; derivation impossible`; no worker run. Pure downstream of a 429 master. |
| content-policy refusal | 0 | 0% | no refusal text in any stderr/stdout tail (stdout empty) |
| timeout | 0 | 0% | `timed_out` false on all 270 |
| malformed prompt / reference / size | 0 | 0% | the same prompt shape succeeds elsewhere; see below |

Modes of the 270: generate 255 (RM_ 231, Force_KyberCrystal 15, RUT_ 7, RSW 2), edit 15 (RSW, with reference).
Examples, 429 class: `dregen_Force_KyberCrystal_crystal11_v1`, `dregen_RM_MealMurrinBroth_Simple_v1`, `dregen_RM_Borehulk` family (any RM_ job in the window). Derived class: `dregen_RSW_Acklay_AcklayA_v1_east` (and its north/south), `dregen_RSW_Jerba_Bantha_v1_east`, `dregen_RSW_Dianoga_DianogaSwimming_v1_east`.

## Time clustering (strong)
Failures all fall between 2026-10-18 23:45 and 2026-10-19 01:45 local (25 in 23:45-00:00, then 20-47 per 15 min, peaking 01:30). Before 23:45: ok about 33 per 15 min, 0 failed. From 01:45: 0 failed again, ok 34-46 per 15 min. In the window the success rate fell to about 9-21 per 15 min, so it was a throttle, not a cutoff: 121 generate and 1 edit succeeded inside it, 255+13 failed (generate fail rate 68%).
Failures hit all five workers (w0-w4: 46/53/43/63/63 failed vs 20/16/22/32/32 ok), so the limit is account/backend wide, not a bad worker.
The weekly meter was not the cause: successful runs read primary_used_percent 20-30%, grumpy false. Failed runs have no reading at all (`rollout has no token_count/rate_limits event yet`), i.e. the 429 arrives before the meter updates, so the meter cannot predict it. This is a burst/concurrency throttle on image calls.

## No content correlation
In-window fail rate by subject family is flat, around 52-77% everywhere (RM Plants 52%, Things 52%, Surfaces 60%, KyberCrystal 62%, RUT 54%; the 94-100% rows are tiny n or edit jobs clustered at the worst minutes). By prompt length: 0-200 chars 77%, 200-400 71%, 400-600 61%, 600-800 56%, 800+ 83% (n=18) - no trend. No Star Wars canon, gore, weapons or droid effect is visible; the same families that failed also succeeded in the window.

## What a prompt rewrite can fix
Nothing in this set. The prompts are healthy; the daemon's firm-retry text (`RETRY: ... replied in text before generating`) is also misleading, since the real stderr was 429 and the model never replied in text.

## Systematic (daemon behaviour) worth fixing
1. artpiped retries 3 times within about 2 minutes against a throttled backend, which burns the retry budget and parks the job in `failed/`. A 429 should back off minutes (or pause the queue) and not count as an attempt.
2. Failure notes should record the 429, not the generic `no image produced`; the firm-prompt retry should be skipped on 429.
3. Concurrency 5 workers x image calls triggered it after about 3 h at full rate (20:30-23:45). A cap of 3-4 or a cooldown after the first 429 would likely avoid the repeat.

## Recommendation
Requeue the 270 worker failures unchanged (same prompts, same references) now that the window is over; the 10 derived facings follow their masters automatically once the east masters pass. Expect roughly the 100% success seen after 01:45. Do not rewrite prompts. If the requeue meets 429 again, drop concurrency before touching content.
