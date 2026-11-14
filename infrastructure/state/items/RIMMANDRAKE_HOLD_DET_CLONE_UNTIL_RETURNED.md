## Finding (2026-11-14, CONDUCTOR helper)

`detached_helper.py launch` reuses the pool clone `<ITEM>.det` whenever its `.git` exists (`take_clone`). It does not
check whether the previous run on that clone is still being returned. The unit's `finish` step writes the
"ended" line to the Conductor log first, and the return step (bundle, then delete the clone) runs after it. A
Conductor that relaunches as soon as it reads "ended" starts the new run inside a clone that is deleted under it
a few seconds later.

It happened twice [measured: run records under `/mnt/d/ClaudeWork/rimmandrake/dispatcher/detached/` and the
unit journals]:
- `rm-detached-bench-rimmandrake-triple-firehawk-reach-prefer-1794599801` ended 2026-11-13 20:04:09Z, returned at
  20:04:31Z (bundle stamped 20:04:41Z). The next run `...-1794600299` was launched at 20:04:59Z and its sync was REFUSED
  on the "clone bundled" commit. The clone was then gone, and the run spent 0.66 USD doing nothing.
- `rm-detached-bench-rimmandrake-delete-fill-n-one-water-numb-1794614223` ended 01:06:19Z (bundle 01:06:55Z). The next
  run `...-1794618412` was launched at 01:06:52Z and lost its clone in its first minute, which cost 0.68 USD.

In both cases the unit's ExecStopPost then failed with `status=200/CHDIR`, so `finish` never ran and the record
stayed `running`. That stale record then blocked the return of LATER runs' clones ("kept ...: still in use by
<dead unit>"). The two records were finished by hand with `detached_helper.py finish --unit` on 2026-11-14 ~09:28Z,
and the later clones were returned with `return --unit`.

## Do
- In `launch`, refuse to reuse `<ITEM>.det` (or wait for it, or make a fresh clone) while a record that names that
  clone is not `returned`, or while its unit is not inactive.
- Run ExecStopPost from a path outside the clone (REPO, not the clone), so `finish` still runs when the clone is gone.

## Acceptance test
Add a selftest case to `src/RimMandrake/rimflow/selftest_detached_helper.py` (or the selftest that covers
`detached_helper.py`). A record for clone X with `status` finished and no `returned` makes `launch` on the same item
refuse or choose another clone. Watch it fail on the base commit, then pass after the fix.
