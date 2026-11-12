# HOOKS_SCANGUARD_FIX_QUOTED_PIPE_SLIPS_PAST — done statement

Item: `block_blind_scan misses a scan when a quoted argument holds a separator`. Fixed at a2bac49a9a (blind PASS,
run-1), then reopened by the running-promise `hook=block_blind_scan.py` on 2026-11-08T20:49Z ("not wired in
~/.claude/settings.json, ~/rm/dispatch/.claude/settings.json"); a sweep read it running again 2026-11-09T04:33Z. The
ledger now says it OWES A GUARD: it closes only with a class guard test shown failing on the instance.

Done when (criteria copied from the item's spec, plus the ledger's close gate):
- `grep "a|b" /x/save.rws`, `grep -c "a;b" Player.log` and `bash -c "cd /tmp && grep -c biome /x/save.rws"` are refused
  by `.claude/hooks/block_blind_scan.py`. Evidence: the hook run on each payload at the closing sha.
- `.claude/hooks/selftest_block_blind_scan.py` pins those three. Evidence: the selftest passing at the closing sha.
- `names_scan_tool` (which shares `segments()`) still gates the measure import correctly. Evidence: a selftest row.
- A class guard test exists for the way this fix died (a `hook=` promise reads "not wired" when the hook drops out
  of the settings the check reads), recorded with `rimflow guard HOOKS_SCANGUARD_FIX_QUOTED_PIPE_SLIPS_PAST --test
  <selftest*.py>` and shown failing on the instance. Evidence: the guard event and the test's failing/passing runs.
- The item closes with a running-promise that `rimflow close` accepts (`hook=block_blind_scan.py`), the check passing
  at close. Evidence: the close event.
