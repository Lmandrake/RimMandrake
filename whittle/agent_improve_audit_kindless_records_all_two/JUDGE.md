# Judge — AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO (fresh-eyes, 2026-11-11, CLAUDE_ARCHMAGI_OFFLINE1 judge seat)

Read: STATEMENT.md, NOTES.md, evidence/*, `git diff 66ab8395fd HEAD` of agent_improve.py, lessons.py, the selftests and
design §4.3. Re-ran myself at HEAD cb52ef37dd: the 5 selftests -> PASS 5/5 GREEN; `measure_kindless.py` (no argument) ->
KINDLESS 2 of 2, probe source_kinds ['AUDIT'], identical to evidence/measure_kindless.out apart from the inbox moving
(127 lessons, 18 footers). I also opened both change records myself (source_kinds [] and 1 piece each) and grepped both
lessons' bodies at the commits that added them: neither names any id of the item grammar.

## Line 1 — below L2 a change records kinds, or the decision to leave it uncheckable is in §4.3 with its reason: TRUE
- (b) is met: §4.3 has a dated paragraph (2026-11-11, naming the item) saying in bold that an L0/L1 change whose cited
  pieces name no item is applied with `source_kinds: []` and "stays uncheckable by design". It gives the reasons: no
  sound source is left, a guessed kind would spoil the held-out sample, refusing the change would be a new gate, and a
  refusal would pull down the ramp's acceptance rate. The two other sources were measured and failed: the seat touched
  8/41 items within an hour, and the adding commits name no item (evidence §2, which I reproduced).
- (a) is partly done as well, and the doc matches the code: `piece()` now records `task_kind` from the piece's own item
  (lesson `item:` footer, Relentless item, alarm clone path, ops alarm name, owner id), and falls back to the whole
  text. Each cited piece carries `task_kind`. selftest_agent_improve_steps passes on the new code. On the old code
  (selftests_old_code.out) it fails 4 checks: "L0/L1 records the kind a lesson names past its first line" and "a
  lesson's item: line is its kind". selftest_agent_improve and selftest_lessons also fail on the old code. That the doc
  and code agree on the kindless case is shown by "L0/L1 applies it too, recorded kindless".
- Loose, not false: no apply_change test covers a lesson whose words name no item but whose footer gives a kind. Every
  footer fixture also names an item in its text. Footer precedence is tested, so footer-alone follows from it.

## Line 2 — share of kindless records measured, saved, sanity-probed, stated on the item and in §4.3: TRUE
- evidence/measure_kindless.py and its .out: "KINDLESS 2 of 2 records". The sanity probe runs the production
  apply_change at L0 in a temp repo on a real inbox lesson with a footer. It writes source_kinds ['AUDIT'] and the same
  `count()` reads 0 of 1, so the reader can see a non-empty list. The 2 of 2 appears in a ledger note on the item, and
  in a 05:18Z correction note that replaces an earlier note's wrong probe description. §4.3 states it too.
- Flattering, not fatal: the probe's lesson is the builder's own, filed during this item. It is still a real file going
  through the real code path. The .out header shows the run was given the old-code path as an argument. Without it
  section 1 is the same.

## Loose spots (none decide the verdict)
- lessons.py docstring: "never a line of that shape inside the lesson text". A lesson whose own last line is
  `item: X`, filed with no --item, no session item and no --home, has that line read as its footer.
- §4.3 gives 584 whole-text-kinded vs 159 first-line, but attribution_audit.out counts 422 "whole text only" (584-159 =
  425). 3 lessons are unexplained, and the 27%/49% corroboration rates rest on that base.
- The §4.3 inbox figures (126 lessons, 17 footers) are a snapshot. The doc says so and points at the saved
  measure_kindless_cited_in_4.3.out.

would show: yes
