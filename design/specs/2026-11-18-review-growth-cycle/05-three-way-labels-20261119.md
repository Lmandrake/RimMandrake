# Three readings of 35 old control-store review claims (2026-11-19)

Item: `RIMMANDRAKE_RELABEL_OLD_CLAIMS_BLIND_CODEX_AGREED_ON_SIXTEEN`. The third reader (an Opus judge) labelled the
claims blind first. Blind file: `D:\ClaudeWork\rimmandrake\conductor\blind_relabel_20261119\blind_labels.json`,
sha256 `b46c2b855c14d8a0811e17f019c9fc5a6451fce095ae8ff4d4bb271f01424e3b` (recorded on the item before phase 2).

## For the owner

- Three readers sorted 35 old claims. Each claim got PROBLEM or POLISH.
- Codex and the blind reader agree on 27 of 35. [measured]
- Each of them agrees with the old labels on only 16 of 35. [measured]
- All three agree on 12 claims. [measured]
- The old labels call 4 claims PROBLEM. Codex and the blind reader each call 21 PROBLEM. [measured]
- So the old labels are the outlier, not Codex. [guess ~80%]
- You ruled on rare failures by card 2026-11-19 13:27:48Z: the page says "not handled" and no fix is built.
- By that rule, 14 of 35 claims are real and 21 are not. The new labels and one reason each are below the old table.
- Of the 21 that Codex and the blind reader called PROBLEM, 8 move to "not handled" or polish and 13 stay real.
  So most of the 21 were not rare: they break a promise in ordinary use. [measured, by my labelling]
- All 14 real ones are already fixed and tested. No fix was built for this card.
- The new labels agree with the 12 claims all three readers agreed on, so the pass mark below is unchanged.

## The table

PROBLEM = the analyst's `expect: refuse`; POLISH = `expect: pass`. Nobody used NEXT-VERSION.

| claim | analyst | Codex | blind reader (me) | who agrees |
|---|---|---|---|---|
| c2.1 | POLISH | PROBLEM | POLISH | analyst + me |
| c2.2 | POLISH | POLISH | PROBLEM | analyst + Codex |
| c2.3 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c2.4 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c2.5 | PROBLEM | POLISH | POLISH | Codex + me |
| c2.6 | PROBLEM | PROBLEM | PROBLEM | all three |
| c2.7 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c2.8 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c2.9 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c3.1 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c3.2 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c3.3 | POLISH | PROBLEM | POLISH | analyst + me |
| c3.4 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c3.5 | POLISH | POLISH | PROBLEM | analyst + Codex |
| c3.6 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c3.7 | POLISH | POLISH | PROBLEM | analyst + Codex |
| c3.8 | POLISH | PROBLEM | POLISH | analyst + me |
| c3.9 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c3.10 | POLISH | PROBLEM | POLISH | analyst + me |
| c3.11 | POLISH | POLISH | POLISH | all three |
| c4.1 | PROBLEM | PROBLEM | PROBLEM | all three |
| c4.2 | PROBLEM | PROBLEM | PROBLEM | all three |
| c4.3 | POLISH | POLISH | POLISH | all three |
| c4.4 | POLISH | POLISH | POLISH | all three |
| c4.5 | POLISH | POLISH | POLISH | all three |
| c4.6 | POLISH | POLISH | POLISH | all three |
| c4.7 | POLISH | POLISH | POLISH | all three |
| c4.8 | POLISH | POLISH | POLISH | all three |
| c4.9 | POLISH | POLISH | POLISH | all three |
| c4.10 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c4.11 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c4.12 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c4.13 | POLISH | PROBLEM | PROBLEM | Codex + me |
| c4.14 | POLISH | POLISH | POLISH | all three |
| c4.15 | POLISH | POLISH | PROBLEM | analyst + Codex |

Pairwise agreement [measured, from `src/RimMandrake/rimflow/code_review_calibration_set.json`,
`D:\ClaudeWork\rimmandrake\conductor\code_review_calibration_answer.md` and the blind file]:

- analyst and Codex: **16 / 35**
- analyst and me: **16 / 35**
- Codex and me: **27 / 35**
- all three: **12 / 35** (3 PROBLEM: c2.6, c4.1, c4.2; 9 POLISH)

Pattern of the 23 non-unanimous claims [measured]: the analyst alone 15, Codex alone 4, me alone 4. With two classes
in use no claim splits three ways; each line below is one 2-to-1 split and what in the page or instructions lets it
happen.

## New labels by the page rule (owner card 2026-11-19 13:27:48Z)

The rule is in `design/RimMandrake/standing_rulings.md` §A boundary page, Decision 4, and in
`src/RimMandrake/rimflow/roles/code_review.md` §A Problem. **REAL** means the claim breaks a promise in ordinary
operation: an input inside ACCEPTS at human or timer pace, with the world answering, plus the one failure the broken
promise itself names, met alone. **not** means a rare failure (a failure the promise does not name, two failures at
once, two events in one instant, or a shape no call site makes) or polish. Each rare one is now a line on the control
page (`design/specs/2026-11-18-pipeline-control-surface/boundary.md`), under DOES NOT SURVIVE or under "handled today,
not promised". Each claim is judged against today's page.

| claim | analyst | Codex | blind | new | reason |
|---|---|---|---|---|---|
| c2.1 | POLISH | PROBLEM | POLISH | not | rare: two threads launching one name in one instant; no launcher does it (DNS two-threads-one-name) |
| c2.2 | POLISH | POLISH | PROBLEM | REAL | a spec unit with no `--unit` in args is inside launch-through-one-door ("never read"); fixed be673ed895, round-two test 2 |
| c2.3 | POLISH | PROBLEM | PROBLEM | REAL | another writer's lock is the failure kill-works-without-the-store names, met alone; fixed be673ed895, round-two test 3 |
| c2.4 | POLISH | PROBLEM | PROBLEM | not | rare: a failed kill and a fork in its gap at once (DNS a-fork-while-a-kill-fails) |
| c2.5 | PROBLEM | POLISH | POLISH | not | polish: LIFE CYCLES allows ended -> killed and no promise names the word the record holds; changed anyway in be673ed895 |
| c2.6 | PROBLEM | PROBLEM | PROBLEM | REAL | a second stop with a shorter deadline is ordinary; three-named-stops' deadline not kept; fixed be673ed895, round-two test 6 |
| c2.7 | POLISH | PROBLEM | PROBLEM | REAL | `--idem` is a documented key; same-command-twice; fixed be673ed895, round-two test 7 |
| c2.8 | POLISH | PROBLEM | PROBLEM | REAL | a list starting `systemd-run` is the census's own shape; one-admission-point; fixed be673ed895 (census per argv), t_sites |
| c2.9 | POLISH | PROBLEM | PROBLEM | not | polish: test strength with no broken verb; "usually" is now each verb's own p95 |
| c3.1 | POLISH | PROBLEM | PROBLEM | REAL | a re-admission refused on a limit is ordinary and lost the first admission; fixed 53cb713db1, round-three test 1 |
| c3.2 | POLISH | PROBLEM | PROBLEM | not | rare: a lock during a kill while the run ends (DNS a-lock-while-a-killed-run-ends) |
| c3.3 | POLISH | PROBLEM | POLISH | not | rare: a locked store plus a repeat, a lock same-command-twice does not name; the second SIGKILL does nothing (DNS) |
| c3.4 | POLISH | PROBLEM | PROBLEM | not | rare: a failed kill and an unreadable cgroup at once (DNS two-failures-at-once) |
| c3.5 | POLISH | POLISH | PROBLEM | not | rare: two timers due in the same second (DNS two-timers-in-one-second) |
| c3.6 | POLISH | PROBLEM | PROBLEM | REAL | today's callers carry a payload `--unit` (left_open_continue.py:370); fixed 53cb713db1, round-three test 6 |
| c3.7 | POLISH | POLISH | PROBLEM | not | polish: a builder or alias is launch-code-in-a-new-shape |
| c3.8 | POLISH | PROBLEM | POLISH | not | rare shape: needs `Delegate=`, which no unit sets (DNS a-child-cgroup) |
| c3.9 | POLISH | PROBLEM | PROBLEM | REAL | a survivor is the failure kill-verified-dead names; LIFE CYCLES escalated -> back to pending; fixed 53cb713db1, round-three test 9 |
| c3.10 | POLISH | PROBLEM | POLISH | not | outside plain-paths: no path has a space (DNS a-path-with-a-space) |
| c3.11 | POLISH | POLISH | POLISH | not | outside ACCEPTS: a deadline is 1 s or more; refused today |
| c4.1 | PROBLEM | PROBLEM | PROBLEM | REAL | killing again is ordinary; same-command-twice; fixed 9a8593dc91, t_review_round_four_p1 |
| c4.2 | PROBLEM | PROBLEM | PROBLEM | REAL | `.service` is systemctl's own spelling, inside stop-target; fixed 9a8593dc91, t_review_round_four_p1 |
| c4.3 | POLISH | POLISH | POLISH | not | outside: option forms no launch site uses |
| c4.4 | POLISH | POLISH | POLISH | not | rare: a cgroup folder that cannot be listed (DNS, 0 of 66 measured) |
| c4.5 | POLISH | POLISH | POLISH | not | polish: an annotated alias is launch-code-in-a-new-shape |
| c4.6 | POLISH | POLISH | POLISH | not | polish: a builder in a builder is launch-code-in-a-new-shape |
| c4.7 | POLISH | POLISH | POLISH | not | rare: a failed escalation and a second kill at once (DNS two-failures-at-once) |
| c4.8 | POLISH | POLISH | POLISH | not | outside plain-paths: a `$` is refused by name |
| c4.9 | POLISH | POLISH | POLISH | not | rare: a void in a judge's own second (DNS hand-command-in-a-run's-own-second) |
| c4.10 | POLISH | PROBLEM | PROBLEM | REAL | a new hold with new words is his ordinary input; his-hold-refuses-launch "with his words"; fixed a6aac8a6fc, t_his_hold_refuses_launch |
| c4.11 | POLISH | PROBLEM | PROBLEM | REAL | a corrupt store is an unreadable store, the failure probe-never-lies names; doctor said OK; fixed 9a8593dc91 |
| c4.12 | POLISH | PROBLEM | PROBLEM | REAL | an unreadable store on pipe off's follow-up read is probe-never-lies' own failure, met alone; fixed 9a8593dc91 |
| c4.13 | POLISH | PROBLEM | PROBLEM | REAL | run ids rm-probe-1 and rm-probe-10 are ordinary; void-never-moves-a-stage "flags no other run"; fixed a6aac8a6fc, t_void_never_moves_a_stage |
| c4.14 | POLISH | POLISH | POLISH | not | polish: test strength |
| c4.15 | POLISH | POLISH | PROBLEM | not | polish: test strength with no broken component described |

Agreement of the new labels [measured]: analyst 23 / 35, Codex 26 / 35, blind reader 28 / 35, and 12 / 12 on the
unanimous set. Four labels rest on the "failure the promise names" reading and are the likeliest to be contested: c2.3,
c3.9, c4.11, c4.12.

### Real in ordinary operation (14), each already fixed; no fix built for this card

- **c2.2**: a spec unit with no `--unit` in args is inside launch-through-one-door ("never read"); fixed be673ed895, round-two test 2
- **c2.3**: another writer's lock is the failure kill-works-without-the-store names, met alone; fixed be673ed895, round-two test 3
- **c2.6**: a second stop with a shorter deadline is ordinary; three-named-stops' deadline not kept; fixed be673ed895, round-two test 6
- **c2.7**: `--idem` is a documented key; same-command-twice; fixed be673ed895, round-two test 7
- **c2.8**: a list starting `systemd-run` is the census's own shape; one-admission-point; fixed be673ed895 (census per argv), t_sites
- **c3.1**: a re-admission refused on a limit is ordinary and lost the first admission; fixed 53cb713db1, round-three test 1
- **c3.6**: today's callers carry a payload `--unit` (left_open_continue.py:370); fixed 53cb713db1, round-three test 6
- **c3.9**: a survivor is the failure kill-verified-dead names; LIFE CYCLES escalated -> back to pending; fixed 53cb713db1, round-three test 9
- **c4.1**: killing again is ordinary; same-command-twice; fixed 9a8593dc91, t_review_round_four_p1
- **c4.2**: `.service` is systemctl's own spelling, inside stop-target; fixed 9a8593dc91, t_review_round_four_p1
- **c4.10**: a new hold with new words is his ordinary input; his-hold-refuses-launch "with his words"; fixed a6aac8a6fc, t_his_hold_refuses_launch
- **c4.11**: a corrupt store is an unreadable store, the failure probe-never-lies names; doctor said OK; fixed 9a8593dc91
- **c4.12**: an unreadable store on pipe off's follow-up read is probe-never-lies' own failure, met alone; fixed 9a8593dc91
- **c4.13**: run ids rm-probe-1 and rm-probe-10 are ordinary; void-never-moves-a-stage "flags no other run"; fixed a6aac8a6fc, t_void_never_moves_a_stage

## What causes each split

- **c2.1** (Codex alone): `one-name-one-run` does not say whether two threads of one process are a launch the page accepts.
- **c2.2** (me alone): The claim was made on code where callers passed `--unit`; the page now says args are never read. Old producers or today's?
- **c2.3** (analyst alone): The analyst weighed harm (3 s, no wrong record); the page line "A unit kill does not wait" has no harm threshold.
- **c2.4** (analyst alone): The analyst ruled on rarity (a failed kill plus a fork); the instructions have no rarity test for inputs inside ACCEPTS.
- **c2.5** (analyst alone): LIFE CYCLES allows ended → killed on a crossed kill but does not say whether the record must move.
- **c2.7** (analyst alone): The analyst used "no caller passes `--idem`"; the call-site test covers only inputs outside ACCEPTS, and `--idem` is a documented key.
- **c2.8** (analyst alone): The analyst read census gaps as "test strength"; reason 2 makes them Problems when a broken site is described.
- **c2.9** (analyst alone): `usually` in verbs-answer-in-a-second is not defined, so a pooled p95 can be read as fair or as blind.
- **c3.1** (analyst alone): Rarity again (same reach as c2.1); the page lists no move that deletes an admission.
- **c3.2** (analyst alone): Rarity (a 0.2 s lock plus an end race) against stopped-run-spends-no-trial, which has no frequency limit.
- **c3.3** (Codex alone): Whether a locked store (DOES NOT SURVIVE) excuses an idempotence promise, and whether a no-op second SIGKILL is an effect.
- **c3.4** (analyst alone): probe-never-lies names cgroup.procs; the analyst ruled on rarity, Codex and I on the promise's words.
- **c3.5** (me alone): No promise says bookkeeping runs once per run; "a move not listed" is read as covering it (me) or not (Codex).
- **c3.6** (analyst alone): Today's callers carry a payload `--unit` (left_open_continue.py:370); the analyst counted the first-match order as safe.
- **c3.7** (me alone): The census half is a described broken site; the alias half sits under launch-code-in-a-new-shape. One claim, two classes.
- **c3.8** (Codex alone): kill-verified-dead does not say which cgroups count; no unit has child cgroups today [measured].
- **c3.9** (analyst alone): Rarity (a kill that leaves a survivor) against a LIFE CYCLES move written word for word.
- **c3.10** (Codex alone): plain-paths bars only `$`, so a space is inside ACCEPTS by the letter, yet no estate path has one.
- **c4.10** (analyst alone): The analyst checked that every reader honours the file row; the page promise is stated about the store's import.
- **c4.11** (analyst alone): The DOES NOT SURVIVE exception ("unless it reports something false") was not applied by the analyst.
- **c4.12** (analyst alone): Rarity (a read failure after a write) against probe-never-lies, which has none.
- **c4.13** (analyst alone): The analyst rated a wrong FLAG line with no gate as polish; the promise says "flags no other run" with no gate test.
- **c4.15** (me alone): Reason 2 needs "a broken component described"; how concrete that must be is not said.

Grouped: 12 of the 15 analyst-alone splits rest on "needs a rare event" (c2.4, c2.7, c3.1, c3.2, c3.4, c3.9, c4.11,
c4.12), "test strength" (c2.8, c2.9) or "small harm" (c2.3, c4.13). The instructions give neither as a reason for polish: the
call-site test applies only to an input OUTSIDE ACCEPTS, and reason 2 makes an untested promise a Problem. The
analyst labelled before the page existed, so this is a missing rule in the analyst's reading, not in Codex's.

## DRAFT, not applied: the smallest wording change

To `src/RimMandrake/rimflow/roles/code_review.md`, §A Problem (one added paragraph, one changed sentence):

> (overruled before it was applied: he picked "Page says 'not handled'" by card 2026-11-19 13:27:48Z, `standing_rulings.md`
> §A boundary page before pipeline code, Decision 4. A rare failure is not a Problem; what was applied is in
> `code_review.md` §A Problem.)

> (changed) "A failure listed under DOES NOT SURVIVE is never a Problem, unless the component **noticed it and** then
> reported something false about it."

> (added under reason 2) "The broken component must be a site or a change you can write down in one line. A census
> or test shape the page puts under DOES NOT SURVIVE is not one."

> (added under What you return) "A claim written against older code is judged against today's page and today's call
> sites."

To `design/specs/2026-11-18-pipeline-control-surface/boundary.md` (each a one-line edit; a new accepted input is
next-version work, so these only make the current lines say what they already mean, and the Conductor decides):

- **plain-paths:** "Paths of clones and of the store are made of letters, digits, `-`, `_`, `.` and `/`." (c3.10, c4.8)
- **one-name-one-run:** add "Each launch is its own process; two threads launching one name are outside." (c2.1, c3.1)
- **verbs-answer-in-a-second:** "Each verb's median answer is under 1 second." (c2.9, c4.14)
- **kill-verified-dead:** add "Processes in a child cgroup are outside: no unit sets `Delegate=`." (c3.8)
- **LIFE CYCLES run:** "A kill that killed a process records the run killed even when its end receipt came first." (c2.5)
- **same-command-twice:** add "A run's bookkeeping (record, clone return, finish note) is done once, however many kills
  or timers reach it." (c3.3, c3.5, c4.1)
- **DOES NOT SURVIVE, two-failures-at-once:** list the rare races the Conductor accepts by name (candidates: c2.4 a fork
  in a failed kill's gap, c3.2 a lock during an end race). Each move is a logged Conductor decision.

## DRAFT, not applied: a fair pass mark for uncertain labels

- **Do not score against the old labels.** A reviewer that reads the instructions exactly scores about 16 / 35 on them,
  as two independent readers just did.
- **Score only the agreed set.** Today that is the 12 unanimous claims. After the wording change, relabel the 23
  others with two fresh readers; a claim joins the set when every reader agrees.
- **Beat the lazy baseline.** "Always POLISH" scores 9 / 12 on today's set. So the mark is: every agreed PROBLEM caught
  (3 / 3), and at most one agreed POLISH called PROBLEM (8 / 9 or better).
- **Missing a Problem costs more than raising a polish.** A missed agreed PROBLEM fails the run on its own.
- **Contested claims are reported, never scored.** Readers that agree on 27 / 35 (77%) set the ceiling a brief can be
  held to on contested ground. [measured, Codex and me]
