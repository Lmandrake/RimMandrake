## spec
Filed 2026-11-23 about 3:40 AM PST by the detached run on `RIMMANDRAKE_BUILD_FOLLOW_THROUGH_AUDIT_LOWER_RATE_IS_HEADLINE`.

`./publish` refused a change because `src/RimMandrake/rimflow/selftest_game_lock.py` was red. That test was red on
origin/main too, with the same FAIL line. Only its measured times differed: `batch medians ['391', '1495', '916'] ms` at
the door, `['1107', '650', '670'] ms` on origin/main (machine load average 57). `publish.py` `_norm` keeps numbers of
1 to 3 digits, so `red_signature` reads the two lines as different, and `split_pre_existing` calls the old red new.
The fix: mask measured quantities before the compare (a number with a unit such as `ms`, `s`, `MB` or `%`, and quoted
numbers in a list), and keep a bare case number ("unit 2" is not "unit 1"). `publish.py` has no boundary page; the fix
writes it first (root `CLAUDE.md` §Code is clean when its promises are tested).

## verify
Acceptance test: the command below. Watched failing on c5ca6ebd78 (base of this filing): `same-timing-equal False`, exit 1.
Expected on a correct fix: `same-timing-equal True distinct-cases-differ True`, exit 0.

    python3 -c "import sys;sys.path.insert(0,'src/RimMandrake/Utils');import publish as P;a,_=P.red_signature(\"FAIL a query answers in under 100 ms (median of 9, in one of up to three batches)  batch medians ['391', '1495', '916'] ms, CPU ['111', '189', '118'] ms\",'/x',1);b,_=P.red_signature(\"FAIL a query answers in under 100 ms (median of 9, in one of up to three batches)  batch medians ['1107', '650', '670'] ms, CPU ['113', '102', '114'] ms\",'/x',1);c,_=P.red_signature('FAIL unit 2 missing','/x',1);d,_=P.red_signature('FAIL unit 1 missing','/x',1);print('same-timing-equal',a==b,'distinct-cases-differ',c!=d);sys.exit(0 if (a==b and c!=d) else 1)"

## criteria
- The acceptance command in ## verify exits 0 and prints `same-timing-equal True distinct-cases-differ True`.
- `publish.py` has a boundary page whose promise covers the compare, with a test of the same name.
