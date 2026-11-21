# RIMMANDRAKE_OWN_CLEARED_TICK_RUNS_ALARM_CRIED_FIVE

## spec

`maturation_hands.tick_units(s)` decides which runs on a mod the Dispatch tick launched. It reads the books
`launches`, `blind_auto`, `ingame_auto`, `holder_road_back`, `steward`, `fixers` and `voided`. It does not read
`cleared[*].released`. `maturation_dispatch.py clear` moves ended blind and in-game entries (and released steward and
fixer keys) out of their books into `cleared[-1].released` (maturation_dispatch.py, the clear verb, about line 4014).
After a clear, the tick's own runs read as `hand_run` acts, and a day later `OPS_MATURATION_HAND_ACT_UNFOLDED` fires.

Measured 2026-11-20 7:40 PM PST (state.json, hand_acts list): all 5 overdue acts are blind judges that the tick
launched (ledger title "launched by the Dispatch step", reason "delegated: maturation_dispatch.py"; ticks.jsonl reads
`launched` for the mod at that moment).

- 3 sit in `cleared[].released.blind_auto`: FlowWorks …1794833834, …1795134465; Pyrelands …1794925887.
- 2 are in no book at all: FlowWorks …1794849266 (cycle 3), Pyrelands …1794863242 (cycle 2). Find what removed
  them (a new visit or cycle replacing `blind_auto`, a regress, a trim) and make that path keep the unit as the tick's
  own, the same way `voided` does (RIMMANDRAKE_OWN_VOIDED_TICK_RUNS_ARCHIVE_HID_THEM).

Same class as the voided fix: an archive of the tick's own books hid its runs.

Fix: `tick_units` also reads `cleared[*].released` (list books and dict books alike), and the book that dropped the
two other units keeps them findable. Then fold the 5 open acts with `maturation_hands.py fold <id> --item
RIMMANDRAKE_OWN_CLEARED_TICK_RUNS_ALARM_CRIED_FIVE` only if the fixed code would not re-record them; better, the fix
makes the next tick read them as the tick's own.

## verify

Acceptance test (fails on base 6d31a96a4b, seen FAIL 2026-11-20 7:41 PM PST; must PASS on the fix), from the repo root:

```
python3 -c "
import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import maturation_hands as H
s={'blind_auto':[],'cleared':[{'at':1,'released':{'blind_auto':[{'unit':'U1','item':'I1'}],'ingame_auto':[{'unit':'U3','item':'I3'}],'steward':{'k':{'unit':'U2','item':'I2'}}}}]}
u,i=H.tick_units(s); ok={'U1','U2','U3'}<=u and {'I1','I2','I3'}<=i
e,_=H.tick_units({'cleared':[{'at':1,'released':{}}, {'at':2}]}); ok=ok and e==set()
print('PASS' if ok else 'FAIL', sorted(u), sorted(i)); sys.exit(0 if ok else 1)"
```

Expected: one line `PASS …`, exit 0. Also add the case to `selftest_maturation_hands.py` and run it with
`run_selftests.py --only selftest_maturation_hands.py`. The two no-book units need their own red case once their path
is found.

## criteria

- The acceptance test passes; `selftest_maturation_hands.py` passes.
- On the live state, `maturation_hands.py list` no longer shows the 3 cleared blind judges as open hand acts, and the
  2 no-book ones are explained and fixed or named UNMEASURED with the cause.
- `maturation.hand_acts_overdue` reads 0 for these 5 at the next tick (other genuine hand acts may remain).
