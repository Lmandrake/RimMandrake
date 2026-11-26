Provenance: one fresh Opus reader (rm-judge), 2026-11-25 7:30 PM PST, that had seen no Codex answer, no analyst label and no earlier relabel; it read only the control store's boundary page and the owner's rule (standing_rulings.md, Decisions 1 to 4) and the four claim texts. Owner's route: `RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS` note of 2026-11-26T02:49Z. Result: the reader sides with Codex on all four (c2.9, c3.4, c4.14 real; c4.1 not real), so each old label is corrected and no brief rule is added. c4.1 and c4.14 leave the `agreed` set (the pass mark is now read on 10 claims, 2 real). Confidences are 55 to 80 percent [measured: the reader's own].

# Blind relabel of four control-store claims, 2026-11-25
Read only: boundary.md (whole) and standing_rulings.md section "A boundary page before pipeline code", Decisions 1-4.
Each claim's behaviour is taken as true. I did not search call sites or code.

## c2.9: the speed test checked a pooled p95, so one slow verb could hide
- Class: problem. Confidence: 80%.
- Entry: PROMISES **verbs-answer-in-a-second**: "'usually' is each verb's own 95th-percentile time over its calls in `t_verbs` (`p95_of`), not every call. Tested by `t_verbs`."
- Why: if one verb takes 3 s on every call while ten fast verbs fill the pool, the pooled p95 stays under 1 s and `t_verbs` stays green. The promise is broken for that verb and no test goes red.
- Deciding fact: the page says "each verb's own" p95, so a pooled test is the wrong test for the promise.
- Page alone enough: yes. The page is silent only on whether today's `t_verbs` still pools, and I was told to take the claim as true.

## c3.4: the kill's final re-read treats "could not read the cgroup" as "empty", so it can report death unverified
- Class: problem. Confidence: 70%.
- Entries: PROMISES **probe-never-lies**: "an unreadable `cgroup.procs` file is reported as 'could not look'... It never reads as 'nothing there'." Also **kill-verified-dead**: "It reports 'killed' only after every process is seen gone."
- Why: say SIGKILL succeeds but the final read of `cgroup.procs` fails. That read is scored "empty", so the store reports "killed" without having seen the processes gone.
- Decision 4: "Ordinary also covers the one failure that a promise names as its own subject, met alone." `probe-never-lies` names an unreadable `cgroup.procs` as its own subject, so this failure, met alone, is not rare.
- Not polish, because: DOES NOT SURVIVE **two-failures-at-once** ("A kill that fails while the cgroup also cannot be read") covers only a failed kill plus a failed read. Here the kill did not fail.
- Deciding fact: the page names the unreadable `cgroup.procs` as the subject of a promise.
- Page alone enough: mostly. The page does not say which read "the cgroup" means: the folder listing or the `cgroup.procs` file.
  - If the claim means the folder cannot be listed, DOES NOT SURVIVE **cgroup-folder-that-cannot-be-listed** applies: "the kill's walk skips it and reads its processes as none". Then the class is polish.

## c4.1: killing an already-killed unit again re-runs its bookkeeping
The bookkeeping that re-runs: the record is re-marked killed, its `-return` unit is stopped and restarted, and the finish note is written again.
- Class: next_version. Confidence: 55%.
- Entries:
  - PROMISES **same-command-twice**: "A void, a settlement, an import or a keyed command sent twice has the effect of once."
  - DOES NOT SURVIVE (handled today, not promised) **a-keyed-kill-repeated-on-a-locked-store**: "`stop --idem` sent again".
  - ACCEPTS **stop-target**.
- Why: a person typing `pipe stop rm-x --kill` twice is ordinary, because stop-target accepts it at human pace. The page promises once-only effect only for a keyed command (`--idem`), so a plain repeated kill is not promised to act once.
  - "A repeated plain kill should also do nothing" is therefore a request for more, which is next_version.
- Deciding fact: same-command-twice limits idempotence to the named kinds, and a plain kill is not among them.
- Page alone enough: no. The page is silent on three points:
  - (a) whether a killed→killed re-mark counts as a "move" under LIFE CYCLES ("a move not listed here is a defect"; killed has no listed exit). If it counts, the class becomes problem.
  - (b) whether a clone that the second `-return` hands back again can by then belong to another run. If it can, real harm may follow, but no promise names it.
  - (c) whether any call site or timer sends a second kill. I could not search for one.

## c4.14: the per-verb p95 estimator lets one slow call in five pass
- Class: problem. Confidence: 65%.
- Entry: PROMISES **verbs-answer-in-a-second**: "'usually' is each verb's own 95th-percentile time ... (`p95_of`)".
- Why: suppose a verb has 5 calls and one of them takes 2 s. That is 20% of its calls over the bar, so its real 95th percentile is over 1 s. An estimator that passes this verb measures about the 80th percentile. The page names `p95_of` as the instrument, so here the page and its test disagree, and the promise can break with no test going red.
- Deciding fact: the page promises the 95th percentile in words, so a gate that reads about the 80th is a wrong test, not mere test strength.
- Page alone enough: partly. The page is silent on how many calls each verb gets in `t_verbs` and on the method `p95_of` uses (nearest-rank or interpolated).
  - Against problem: the page also defines "usually" by `p95_of`. A reader who takes `p95_of` as the definition would call this test strength with no broken component, which is polish. I weigh the page's words "95th-percentile" above the name of the instrument.
