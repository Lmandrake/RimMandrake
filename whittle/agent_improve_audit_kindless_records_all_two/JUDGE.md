# AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO — fresh judge (2026-11-11, CLAUDE_ARCHMAGI_OFFLINE1 judge seat)

Read: STATEMENT.md, NOTES.md, evidence/*, `git diff 66ab8395fd HEAD` of agent_improve.py, lessons.py and design 4.3,
selftest_agent_improve_steps.py l.312-364, the item's ledger notes. Not read: DONE.md, BROADEN.md, the earlier JUDGE.md.
Re-ran: the five selftests (GREEN 5/5) and `measure_kindless.py` with no argument (sections 1-3 reproduce; section 4
needs the old-code path and is absent, as expected).

## Line 1 — a change below L2 records kinds, or the by-design decision is in 4.3 with its reason: TRUE (route b)
- 4.3 has a dated paragraph (2026-11-11, item id named): "A change at L0 or L1 whose cited pieces still name no item is
  applied, and its record says `source_kinds: []`: it stays uncheckable by design", with the reason (a guessed kind
  makes a held-out sample that is not held out; the seat-at-time and adding-commit sources were measured and fail,
  8 and 41 items, commits naming none; refusing would be a new gate and would depress the ramp's acceptance rate).
- Code agrees: the gate runs only where `LEVELS[...]["need_general"]` (L2 only, agent_improve.py l.326-330, l.771).
  Selftests "L0 applies a change from a lesson naming no item, recorded kindless" and "L1 applies it too" pass at HEAD.
  The where-kinds-come-from text matches `piece()`: own item decides (footer, reject/learned item, alarm item or
  clones/<item>, owner id, ops alarm name), else the whole text. I checked by hand: item NONE over a text naming
  WIDGET_REPAIR_SHAPE gives None; no item gives REPAIR; legacy `_1` ids (CATHEDRAL_DESCENT_REVEAL_SITE_1 etc.) give None;
  GSS_WATER_STUB_FIX_PASSED_LAST_WEEK gives FIX. Each change-record piece and each verdict cite carries `task_kind`.
- The extra kind sources (footer, whole text) are shown failing on old code (selftests_old_code.out) and passing now.

## Line 2 — the kindless share is measured, with a sanity probe, and stated on the item and in 4.3: TRUE
- measure_kindless.out and my re-run: KINDLESS 2 of 2 (rimworld-modding_v1, using-rimflow_v1). Independently, the
  changes/ dir holds exactly those 2 files (2 tracked), both `source_kinds: []`, 1 piece each.
- Sanity probe: production `apply_change` at L0 in a temp repo on a real inbox lesson writes `['AUDIT']`, and the same
  reader counts 0 of 1 — the reader can see a non-empty list.
- Stated on the item: ledger note 04:41Z ("2 of 2 ... source_kinds []") and a 05:18Z correction of its probe
  description. Stated in 4.3: "2 of 2 change records on file have `source_kinds: []`".
- 4.3's inbox figures (126 lessons, 17 footers: 6 NONE, 8 legacy, 3 kinded) match the cited frozen run
  measure_kindless_cited_in_4.3.out; I counted the 17 footer lines myself.

## Loose or flattering, none of them a false line
- The sanity probe's fixture is a lesson the builder filed on this same item: a real inbox file, but self-made.
- 4.3's "no less sound than the first line" rests on a +-3 h ledger-touch proxy (27% vs 49%) and an 8-row spot sample;
  4.3 itself calls it "a proxy, not provenance", so the paragraph is honest about it.
- 4.3's lesson totals (2412/584) differ from today's run (2416/585) because the inbox grows; the doc cites the saved run.

would show: yes
