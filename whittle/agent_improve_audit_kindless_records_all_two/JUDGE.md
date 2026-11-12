# Judge verdict — AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO

Judge: fresh blind judge, CLAUDE_ARCHMAGI_OFFLINE1 seat clone, 2026-11-11 (HEAD 2452d42756, pre-change 66ab8395fd).
Read: STATEMENT.md, NOTES.md, evidence/*, `git diff 66ab8395fd HEAD` for agent_improve.py, lessons.py and the design doc,
the change records on file, `rimflow show`. Not read: DONE.md, BROADEN.md, the earlier JUDGE.md.
Re-ran myself: the five selftests (GREEN 5/5) and `measure_kindless.py` with no argument (sections 1-3 match the saved
output line for line).

## Line 1 — a change below L2 records source kinds, or the decision to leave it uncheckable is in 4.3 with its reason: TRUE
- Route (b) is met. `design/RimMandrake/daily_agent_improvement_2026-11-02.md` has a new paragraph inside **4.3** (4.3
  starts at l.120, 4.4 at l.201), dated 2026-11-11 and naming the item. In bold it says that a change at L0/L1 whose cited
  pieces name no item is applied with `source_kinds: []` and "stays uncheckable by design". It gives the reason: no other
  sound source is left, and a guessed kind would make a held-out sample that is not held out. It also says the two other
  sources were measured and rejected (seat touched 8 and 41 items within the hour; the adding commits name no item), and
  that refusing these changes would be a new gate.
- The builder also improved where kinds come from (this goes beyond route (b), and the doc describes it). `piece()` now
  stores `task_kind` taken from the piece's own item: a lesson's `item:` footer via the new `lessons.item_of`, the item on
  a Relentless reject/learned/alarm line, the name on an ops alarm, the id on an owner note. If the piece has no own item,
  `task_kind` comes from the whole text, not just the first line. An own item of NONE, or one with no intent word, gives
  no fallback. Change-record cites carry `task_kind`.
- Doc and code agree. I checked each claim in the paragraph against the diff. `general_gate` runs only where
  `LEVELS[...]["need_general"]` is set (L2 only, agent_improve.py l.771), so "refused only by the L2 gate" is true.
  selftest_agent_improve_steps checks that L0 and L1 apply a lesson that names no item and record `[]`, and that a
  late-named item and a footer item are recorded. These pass on the new code and fail on the old (selftests_old_code.out).

## Line 2 — the share of kindless records is measured, with a sanity probe, and stated on the item and in 4.3: TRUE
- Measurement: `evidence/measure_kindless.py` and its output `measure_kindless.out` (the header gives the command and HEAD).
  Result: KINDLESS 2 of 2 records. I checked this independently by loading both JSONs in
  `infrastructure/state/agent_improve/changes/` (each has `source_kinds []` and 1 piece). I also grepped both cited lessons
  at their adding commits for item-shaped tokens: there are none, which confirms that "neither lesson names an item anywhere".
- Sanity probe: the production `apply_change` at L0, run in a temp git repo on a real inbox lesson that has an `item:`
  footer, writes `probe_v1.json` with `source_kinds ['AUDIT']`. The same `count()` reader then reports 0 of 1. The probe
  could fail: it would read 1 of 1 if the writer or the reader were blind. It reproduced on my run.
- Stated on the item: ledger note 2026-11-12T04:41Z gives the 2 of 2. The 05:18Z note corrects that note's wrong
  description of the probe. Stated in 4.3: "Measured 2026-11-11: 2 of 2 change records on file have `source_kinds: []`".

## Where the evidence is flattering or thin
- The probe lesson was filed by the builder's own seat during this work, with a footer naming this item. It is the one
  case built to succeed. It proves the instrument can see a non-empty list. It says nothing about how often real lessons
  will carry a footer: 5 of 114 in the live inbox, and the doc says plainly that most changes will stay unmeasured.
- n = 2 records is a census, not a rate. The doc and the note both say so.
- The saved evidence `.out` files in the working tree are an uncommitted rerun at 21:19 (HEAD 2452d42756). Only the
  header lines differ from the committed copies (HEAD and temp path); the results are the same.
- selftest_lessons on the old code crashes (IndexError) rather than giving a clean FAIL. That is acceptable as
  "fails on old", but it is a crash, not an assertion.
- None of these changes a line's verdict.

would show: yes
