## spec
`design/concepts/Pyrelands/version/pilot_throwaway/make_test_table.py` rebuilds `version/test_table.json` from scratch, but
since 2026-11-14 other tools have written into that table directly: `testq_blocks.py` added a `testq` block to 35 live
tests (a3cc91d4bb), round-6 work added the tests `T_SELF_CONTAINED_OFFLINE` and `T_ROUND6_GAPS` and put the first in the
supports of `inv_biome_self_contained` and `inv_settings_gate` (6a4318a295), and a blind-cycle reconcile gave
`RECORD_ART_SHEET` its rerun `command` and `command_why` (2f13be3848). A plain remake erases all of it without a word
(measured 2026-11-16 by RIMMANDRAKE_LOCK_PYRELANDS_TWO_LEAVES_THE_TABLE_MAKER_REFUSES). Fix: the maker reads the table it
replaces and carries forward every test it does not define, every key of a test it does not write (never `runs_today` or
`new`), and every decides/supports entry naming a carried test; the carried offline tests are rerun with the rest; and it
asserts nothing of the previous table was lost.

## Acceptance test
`python3 design/concepts/Pyrelands/version/pilot_throwaway/make_test_table.py && python3 -c "import json,subprocess;a=json.loads(subprocess.run(['git','show','HEAD:design/concepts/Pyrelands/version/test_table.json'],capture_output=True,text=True).stdout);b=json.load(open('design/concepts/Pyrelands/version/test_table.json'));lost=[(t,k) for t,v in a['tests'].items() for k in v if k not in ('runs_today','new') and k not in b['tests'].get(t,{})]+[(x['id'],s) for x in a['bars'] for s in x['supports']+x['decides'] if s not in sum([y['supports']+y['decides'] for y in b['bars'] if y['id']==x['id']],[])];print(len(lost),'lost',lost[:5]);exit(bool(lost))"`
exits 0 with `0 lost`. Watched fail 2026-11-16 on the maker before the fix: 2 tests, 35 testq blocks, the record's command
and 2 supports entries lost.

## refs
file: design/concepts/Pyrelands/version/pilot_throwaway/make_test_table.py
file: design/concepts/Pyrelands/version/test_table.json
