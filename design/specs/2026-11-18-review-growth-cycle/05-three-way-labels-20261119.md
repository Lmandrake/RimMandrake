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
- The old labels often say "this needs a rare event". The instructions have no rule for rare events.
- The instructions say: an input on the page that breaks a promise is a Problem. They do not say "unless rare".
- The page already has a place for rare failures. That place is DOES NOT SURVIVE.
- Recommendation: keep the instructions strict. Move each accepted rare failure to DOES NOT SURVIVE.
- The Conductor makes each move, and you see it in the digest. That rule already exists.
- Do not use the old labels as an answer key. Use only claims that all readers agree on.
- A draft of the wording changes and a fair pass mark is below. Nothing is changed yet.

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
