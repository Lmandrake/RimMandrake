# Judge: AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO

Judged 2026-11-11 by a blind judge (CLAUDE_ARCHMAGI_OFFLINE1 clone, offline) at HEAD d43b5a55b1. I read STATEMENT.md,
NOTES.md, the evidence files, §4.3 of the design doc, the code (agent_improve.py piece/lesson_pieces/relentless_pieces/
ops_pieces/owner_pieces/task_kind/source_kinds/general_gate/_prepare_record, lessons.py item_of/add) and `rimflow show`.
I did not read DONE.md, BROADEN.md or the earlier JUDGE.md. I re-ran the five selftests and measure_kindless.py myself.

## Line 1: a change applied below L2 records source kinds, or the decision to leave it uncheckable is in 4.3 with its reason. TRUE (route b, with part of a as well)

- §4.3 (design/RimMandrake/daily_agent_improvement_2026-11-02.md, lines ~145-170) has a dated paragraph
  "(2026-11-11, AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO)" that says in bold that an L0 or L1 change whose cited
  pieces name no item is applied, gets `source_kinds: []`, and stays uncheckable by design. It gives reasons: a guessed
  kind would make a held-out sample that is not really held out; the two other candidate sources failed when measured
  (the seat touched 8 or 41 items within the hour, and the adding commits name no item); refusing at L0 or L1 would be a
  new gate and would pull down the acceptance rate.
- Doc and code agree. `piece()` takes the kind from the piece's own item when its source records one (lesson `item:`
  footer via `lessons.item_of`, Relentless attempts/learned item dir, alarm `item` or `clones/<item>[.qN]`, ops alarm
  name, owner note id). NONE or an id with no intent word gives None, and the text is not consulted. Otherwise the kind
  comes from the whole text. `_prepare_record` writes `source_kinds` plus a `task_kind` on every cited piece.
  `general_gate` refuses empty kinds only at L2. `lessons.py add` writes `item:` from --item, else RIMFLOW_ITEM, else
  WC_ITEM.
- selftest_agent_improve_steps.py l.359 and l.363 check that a kindless change is applied and recorded `[]` at L0 and
  at L1. The tests that read kinds past the first line and from the `item:` footer fail on the old code
  (evidence/selftests_old_code.out: 3 + 4 FAILs and a lessons crash) and pass on the new. My re-run: GREEN, 5/5 PASS.

## Line 2: the share of kindless change records is measured, has a sanity probe, and is stated on the item and in 4.3. TRUE

- `infrastructure/state/agent_improve/changes/` holds exactly two records, rimworld-modding_v1 and using-rimflow_v1. I
  read both: `source_kinds []`, 1 piece each. My re-run of measure_kindless.py printed "KINDLESS 2 of 2 records", the
  same as evidence/measure_kindless.out.
- Sanity probe: the production `apply_change` (L0, temp repo, fake publish) runs on a real inbox lesson that has an
  `item:` footer and writes a record with `['AUDIT']`. The same `count()` reads it back as 0 of 1. So the reader can see
  a non-empty list, and the probe could have failed.
- I checked by hand that neither source lesson names an item. Their bodies at the adding commits 51ca29c716 and
  aa1853fc18 contain no ITEM_TOKEN match. So the doc is right that the new reading gives them no kinds either.
- Stated in §4.3 ("Measured 2026-11-11: 2 of 2 ...") and in the item's ledger note of 2026-11-12T04:41:56Z. The other
  figures in 4.3 match my re-run: 2400 lessons, 159 (7%) and 582 (24%); inbox 8 of 114, 2 by first line, 5 footers.

## Where the evidence is flattering or thin

- The sanity probe uses a lesson the builder filed this round with a footer. That is a best case, but it is only meant
  to show the reader can see a non-empty list, and it does show that.
- The ledger note describes an earlier probe ("a copy with ['REPAIR']"), not the apply_change probe now in the
  evidence. The 2-of-2 figure in the note is still right. This is stale wording, not a wrong claim.
- 2 of 2 is a tiny sample, and the doc says so. Section 4 of the measurement is honest against the builder's interest:
  on real sources, L1 gather is the same under old and new code. §4.3 also admits that most skill changes will stay
  unmeasured until lessons are filed inside an item.
- I did not re-run attribution_audit.py (not on my list of allowed commands). I took its 27% / 49% from the saved
  output. It only supports the "whole text is no less sound than first line" remark, not either criterion.

would show: yes
