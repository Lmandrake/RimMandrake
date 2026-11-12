# Judge verdict: AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO

Judge: fresh blind judge, CLAUDE_ARCHMAGI_OFFLINE1 clone, 2026-11-11. I did not read DONE.md, BROADEN.md or the earlier JUDGE.md.
What I read: STATEMENT.md, NOTES.md, the evidence files, the diff 66ab8395fd..HEAD of agent_improve.py, lessons.py and
design §4.3, and `rimflow show`. What I ran myself: the five selftests (GREEN 5/5), `measure_kindless.py` with no
argument, `attribution_audit.py`, and `rimflow show`.

## Line 1: a change below L2 either records source kinds, or design 4.3 says with a reason that it stays uncheckable. TRUE (option b)
- §4.3 now has a paragraph dated 2026-11-11 that names the item. In bold it says: "A change at L0 or L1 whose cited
  pieces still name no item is applied, and its record says `source_kinds: []`: it stays uncheckable by design". It
  gives the reasons: a guessed kind would give a held-out sample that is not held out; the two other sources were
  measured and both failed (the seat touched 8 or 41 items within the hour, and the adding commits name no item);
  refusing such a change at L0/L1 would add a new gate, which the freeze forbids, and would lower the acceptance rate.
- The code agrees with the doc:
  - `need_general` is True only at L2 (LEVELS), so `general_gate`'s refusal of empty kinds runs only there.
  - `_prepare_record` writes `source_kinds(row, entry)`, which can be `[]`.
  - `piece()` takes the kind from the piece's own item when the source records one (lesson `item:` footer, Relentless
    reject/learned item, alarm `item` or `clones/<item>`, ops alarm name, owner note id). `NONE`, or an id with no
    intent word, gives None with no fallback to the text. Otherwise the kind comes from the whole text.
  - The cites in each record carry `task_kind`, as the doc says.
  - `lessons.py add --item` and the RIMFLOW_ITEM/WC_ITEM environment variables write the footer, as the doc says.
- Selftests: GREEN 5/5 when I ran them. `selftests_old_code.out` shows the new footer and alarm-item tests fail on
  the old code. Option (b) does not strictly need this, but it is there.

## Line 2: the share of kindless change records is measured, has a sanity probe, and is stated on the item and in 4.3. TRUE
- I re-ran `measure_kindless.py`. It printed "KINDLESS 2 of 2 records" (rimworld-modding_v1, using-rimflow_v1),
  which matches the saved `evidence/measure_kindless.out` and the 2 files in `changes/`.
- The sanity probe is real. It runs the production `apply_change` at L0 in a temp repo on a real inbox lesson that
  has an `item:` footer, and writes `probe_v1.json` with `source_kinds ['AUDIT']`. The same `count()` reader then
  counts 0 of 1. So the reader can see a non-empty list, and the probe would fail if it could not.
- The item's note (2026-11-12T04:41:56Z) states the 2 of 2 figure. §4.3 states it too, along with the inbox counts
  (8 of 114 name an item, 5 have footers). My re-run reproduced those counts.

## Staged or flattering
- The probe lesson is the builder's own, filed in this round with WC_ITEM set. It is a real inbox file read by
  production code, so the probe is honest, but it is a best case.
- The item note describes an older probe ("a copy with ['REPAIR']"), while the current evidence shows the
  apply_change probe with ['AUDIT']. This is drift in the note only. The share the criterion asks for is stated
  correctly.
- The evidence is candid about what the change does not achieve:
  - §4 (ordinary use) shows the same signalled targets on old and new code.
  - The attribution audit shows the whole-text fallback is only a proxy: 49% corroborated against 27% for the first
    line. §4.3 says so.
  - The doc admits most skill changes will stay unmeasured until lessons carry an `item:` line.
- Nothing here needs motion or a live game. Everything is offline and reproducible.

would show: yes
