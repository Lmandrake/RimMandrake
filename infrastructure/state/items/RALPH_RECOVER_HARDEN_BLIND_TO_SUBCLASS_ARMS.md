## problem
`RA.Loop._recover` and `RA.Loop.already_failed` call `RA.canon_records`, which filters to `ARM == "ralph_a"`. LoopC emits
arm `ralph_c`, TrioLoop arm `trio`, so both see zero records. Measured on LoopC: 4 records, canon 0, `_recover` returns
None, the next `build_pass` raises NotTested on every restart. So a crash between `build_end` and `_save` wedges ralph_c
for good (the ralph_a path is fine: sc_recover). Same blindness expected in TrioLoop and v3 (they inherit both; check).

## exact change (ralph_a_loop.py, ralph_c_loop.py, trio_loop.py; FOUNDRY is editing these, so BENCH did not)
1. ralph_a_loop.py: `def canon_records(recs, arm=ARM):`, filter on `r.get("arm") == arm`.
2. `class Loop:` add `arm = ARM` and `def my_records(self): return canon_records(self.writer.records(), self.arm)`.
3. Lines ~797 (`_recover`) and ~936 (`already_failed`): use `self.my_records()`.
4. LoopC: `arm = ARM`; override `my_records` to keep only run_ids starting `"ralph_c.%s." % self.member` (as
   ralph_c_loop.require_tested does), so a sibling member's build is not adopted. TrioLoop: `arm = ARM`. v3: same check.

## verify
- `selftest_arena_ralph_c.py`: `hasattr(RA.Loop, "arm")` un-skips sc_buildend_crash. Equivalent patch (RA.ARM set to
  ralph_c in a probe) turned it green on 2026-10-30: `['build_end'] ['published ...']`. Then delete the skip branch.
- Add the same scenario to selftest_arena_trio.
