# RIMMANDRAKE_DROP_RETIRED_SLACK_CHECK_STILL_OWED_AT_EXIT

## spec
GimmeSomeSlack's test table (design/concepts/GimmeSomeSlack/version/test_table.json) still lists P_B4_downed_wire_bursts
as a stage-6 live check (kind live_minimal, support_only, entry_exists true). Its entry was retired in
src/RimMandrake/GimmeSomeSlack/validation.py (comment at ~1179) by a8d27a3f6b, per the owner's 2026-11-16 ruling on
sparking wall ends (RIMMANDRAKE_RETIRE_SLACK_ROWS_WANTING_SPARKING_WALL_ENDS, done). No code writes its row now.
maturation.read_ingame_exit needs every stage-6 live check PASS on its last row, so visit 2's exit cannot be met.
The check decides no bar (support only), so dropping it loosens no bar.
Found 2026-11-19 by RIMMANDRAKE_PROVE_PIPELINE_READY_BEFORE_SLACK_CEILING_RELEASE (second pass).
Fix: drop the entry from the table (or mark it retired so ingame_tests skips it), and make the table check that each
stage-6 live entry still exists in its file.
Acceptance test (watched red 2026-11-19 06:20 PST: "STAGE6 ENTRIES MISSING 1 ['P_B4_downed_wire_bursts']", exit 1;
expected after the fix: "STAGE6 ENTRIES MISSING 0 []", exit 0):
python3 -c "import json;t=json.load(open('design/concepts/GimmeSomeSlack/version/test_table.json'))['tests'];bad=[k for k,v in t.items() if isinstance(v,dict) and str(v.get('stage'))=='6' and str(v.get('kind','')).startswith('live') and v.get('entry') and v.get('file') and not any(v['entry'] in l and not l.strip().startswith('#') for l in open(v['file'],encoding='utf-8'))];print('STAGE6 ENTRIES MISSING', len(bad), bad);raise SystemExit(1 if bad else 0)"

## criteria
- The acceptance test above exits 0.
- python3 src/RimMandrake/rimflow/maturation.py brief GimmeSomeSlack lists no P_B4_downed_wire_bursts.
- selftest_maturation.py stays green.

## verify
bash the acceptance command above; python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_maturation.py

## refs
file: design/concepts/GimmeSomeSlack/version/test_table.json
file: src/RimMandrake/rimflow/maturation.py
