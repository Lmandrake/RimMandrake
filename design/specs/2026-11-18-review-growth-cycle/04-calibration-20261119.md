# The code_review brief's first calibration: 16 of 35, FAILED

Run once, 2026-11-19 about 12:50 AM PST, by `RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS` on the
owner's card of 2026-11-19 about 12:40 AM PST (*"Codex sorts the 35 old complaints one time. It reviews no new code
and no ticket comes from it."*). Command: `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --model
code_review` (one `gpt_consult.py --lockdown` call: no tools, only the brief, the page and the claim text). Codex's
raw answer: `D:\ClaudeWork\rimmandrake\conductor\code_review_calibration_answer.md`. No ticket was filed from it, and
reviews of pipeline code stay stopped until he says start.

## Result

- **16 of 35 sorted as the labels say** [measured]. The registry row `code_review` reads **FAILED**.
- Codex called 21 claims Problems and 14 polish; the labels say 4 and 31 [measured].
- Of the 4 labelled Problems, Codex agreed on 3 (c2.6, c4.1, c4.2) and called c2.5 polish [measured].
- Of the 31 labelled polish, Codex called 18 Problems [measured].

## Why they disagree [guess ~70%]

The labels and the page answer different questions. The analyst labelled the claims on 2026-11-18 evening by
**reachability on an ordinary day**, before any page existed. The page (`boundary.md`, written about 11:50 PM the same
night) was cut partly from these claims and states its promises absolutely ("reports killed only after every process
is seen gone", "a unit kill does not wait", "flags no other run"). The brief tells the reviewer to take each claim as
true and sort it against the page, so a claim that breaks an absolute promise reads as a Problem even when nothing
reaches it. Most of the 18 are that. A few are Codex misreading the page, and two show holes in the page.

## Each disagreement: label, Codex, and which looks wrong [guess per line]

| Claim | Label | Codex (page entry it quoted) | Which looks wrong |
|---|---|---|---|
| c2.1 | polish | problem (one-name-one-run) | either, ~50%: the page does not say whether one process launching one name twice is inside ACCEPTS |
| c2.3 | polish | problem (a-store-locked-over-3-seconds: "a unit kill does not wait") | labels ~75%: the page now promises exactly this |
| c2.4 | polish | problem (kill-verified-dead) | labels ~55%: a failed `systemctl kill` plus a fork is not on DOES NOT SURVIVE |
| c2.5 | problem | polish (killed-run-needs-no-hand-step) | labels ~55%: the LIFE CYCLES line allows ended → killed but does not require it |
| c2.7 | polish | problem (same-command-twice) | either, ~50%: the page does not say whether `stop --idem` is a "keyed command" |
| c2.8 | polish | problem, untested (one-admission-point) | labels ~55%: the claim does describe a site that would get through |
| c2.9 | polish | problem, untested (verbs-answer-in-a-second) | Codex ~70%: the promise says "usually" |
| c3.1 | polish | problem (LIFE CYCLES run) | either, ~50% |
| c3.2 | polish | problem (stopped-run-spends-no-trial) | Codex ~55%: needs a lock held during a kill plus the end race |
| c3.3 | polish | problem (same-command-twice) | Codex ~60%: no caller passes `stop --idem` |
| c3.4 | polish | problem (kill-verified-dead) | **Codex ~85%**: a failed kill with an unreadable cgroup is DOES NOT SURVIVE two-failures-at-once, word for word |
| c3.6 | polish | problem (launch-through-one-door: args "are never read") | labels ~65%: the page now forbids reading args |
| c3.8 | polish | problem (kill-verified-dead) | Codex ~60%: child cgroups are unreachable (no unit sets `Delegate=`), but the page does not list them under DOES NOT SURVIVE |
| c3.9 | polish | problem (LIFE CYCLES stop order: "escalated → back to pending or seen") | labels ~70%: the page lists this move |
| c3.10 | polish | problem (stop-reaches-the-agent) | Codex ~65%: estate paths have no spaces, but plain-paths names only `$` |
| c4.10 | polish | problem (his-hold-refuses-launch) | either, ~55% |
| c4.11 | polish | problem (corrupt-or-lost-store: "pipe doctor names the fix") | labels ~65% |
| c4.12 | polish | problem (probe-never-lies) | labels ~75%: a failed read reported as "no run is live" is the promise's own case |
| c4.13 | polish | problem (void-never-moves-a-stage: "flags no other run") | labels ~75% |

Reading the table: labels look wrong about 9 times, Codex about 6, and 4 are open [guess ~60%]. Against the page as
written, a corrected label set would agree with Codex on roughly 25 of 35 [guess ~55%].

## What this means for passing

- **The labels need re-sorting against the page before they can calibrate anything.** They were sorted against
  reachability, the page against promises. Re-labelling is analyst work, not a model call.
- **The brief needs one rule it lacks:** that a claim whose failure needs two failures, a race inside one instant, or
  an input no call site makes, is polish even when it would break an absolute promise (design 5.3 says so for inputs
  outside ACCEPTS, not for failures). Editing the brief resets it to UNTESTED and a second calibration needs another
  Codex call, which needs his word.
- **`refusal_contract.judge_cases` needs every planted case to come out as planted.** With labels about 70% sure,
  about 10 of 35 labels are wrong [guess], so 35 of 35 cannot be reached on this set as labelled, whatever the brief
  says. Either the labels are corrected first or the Conductor decides a different bar for a noisy set.
- Two holes in the page showed up (c3.8 child cgroups, c3.10 spaces in paths). They are noted here only: no ticket
  comes from this call.
