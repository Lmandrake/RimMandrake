# Judge: AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO

Judged 2026-11-11 by a fresh judge (CLAUDE_ARCHMAGI_OFFLINE1 judge seat), blind to DONE.md, BROADEN.md and the old JUDGE.md.
Read: STATEMENT.md, NOTES.md, every file in evidence/, `git diff 66ab8395fd HEAD` of agent_improve.py, lessons.py,
selftest_agent_improve.py, selftest_agent_improve_steps.py and design §4.3. Re-ran it myself: the five selftests (GREEN 5/5),
`measure_kindless.py` with no argument (exit 0, same section 1 output), `rimflow show` on the item, and my own count of
`infrastructure/state/agent_improve/changes/*.json`.

## Line 1: a change applied below L2 either records source kinds, or design 4.3 holds the dated by-design decision and its reason; doc and code agree. TRUE

- Route (b) is taken. `design/RimMandrake/daily_agent_improvement_2026-11-02.md` §4.3 has a new paragraph dated 2026-11-11
  that names the item, in bold: "A change at L0 or L1 whose cited pieces still name no item is applied, and its record says
  `source_kinds: []`: it stays uncheckable by design". It gives the reason: no other sound source remains, and a guessed kind
  would make a held-out sample that is not held out. It also says why the two other candidates were rejected (the seat at
  the time was busy on 8 and 41 items; the commits that added the lessons name no item), and why refusing the change would be a new gate.
- Some of route (a) is done too. Kinds now come from a piece's own item when its source records one (a lesson's `item:` footer
  written by `lessons.py add --item` / RIMFLOW_ITEM / WC_ITEM, a Relentless row's item, an alarm's `clones/<item>`, an owner note's id,
  an ops alarm's name). If there is none, they come from the whole text and no longer only from the 200-character first line.
  The new selftests in `selftest_agent_improve_steps.py` ("L0/L1 records the kind a lesson names past its first line",
  "a lesson's item: line is its kind", "L0/L1 applies ... recorded kindless") fail on 66ab8395fd (evidence/selftests_old_code.out:
  4 FAIL in steps, 3 in agent_improve, a crash in lessons) and pass at HEAD (evidence/selftests_new_code.out, and my re-run).
- Doc and code agree. I checked each sentence of the paragraph against the diff. `piece()` uses `kind_of_text(item) if item else
  kind_of_text(text)`, so `item: NONE` or a legacy id with no intent word gives None, with no fallback to the text, as the doc says.
  `apply_change` below L2 still writes `source_kinds: []` without refusing, and `general_gate` still runs only at L2.
  `verdict_record` cites now carry `task_kind`, as the doc says. Nothing elsewhere in the doc (l.110, l.140, l.173) contradicts it.
- Real use, which I checked myself: on the live inbox, footers written by other seats' `lessons.py add` calls give AUDIT/FIX.
  CATHEDRAL_MISSION_BOON_OFFERS_1 and WORLD_REMAKE_FINAL_STEP_1 give None, and the doc says this will happen. Section 4 of
  measure_kindless.out shows the L1 gather unchanged, old against new, over 8 real days.

## Line 2: the share of kindless change records is measured from changes/, saved with its command, with a sanity probe, and stated on the item and in §4.3. TRUE

- evidence/measure_kindless.out section 1 gives "KINDLESS 2 of 2 records" (rimworld-modding_v1, using-rimflow_v1) and the command line.
  My independent count of the directory agrees: two files, both `source_kinds == []`, one piece each. My re-run of the script reproduces it.
- The sanity probe is real, not a hand-made JSON. The production `apply_change` at L0, in a temp git repo, on a real inbox lesson with an
  `item:` footer, wrote `source_kinds ['AUDIT']`, and the same `count()` reader reads it as 0 of 1 kindless. It could have failed.
- It is stated on the item: the ledger notes of 04:41Z and 05:18Z say "2 of 2 change records on file have source_kinds []". It is stated in §4.3: "Measured
  2026-11-11: 2 of 2 change records on file have `source_kinds: []`".

## Where the evidence is flattering or loose (none of it changes a verdict)

- The sanity probe takes `real[0]`, the first footer lesson in sort order. That is the builder's own lesson, filed this round with a
  footer whose item has an intent word, so it is the tidy best case. Most real footers are `NONE` (7) or legacy ids with no intent
  word (3 of 6 non-NONE), and give no kind. The doc admits this ("most skill changes will stay unmeasured").
- The selftest fixtures are synthetic (WIDGET_REPAIR_SHAPE and the like). Only the measurement script shows real data.
- The secondary figures in §4.3 are stamped 21:31 PST (2406 lessons, inbox 120, 11 footers). They do not match the saved .out, which was
  re-run at 21:35 (2407, 121, 12). The inbox grew between the two runs. The figure the criterion asks for (2 of 2) matches everywhere.
- The sample is 2 records, both L0. This is the whole population, so it is a census and not an estimate.

would show: yes
