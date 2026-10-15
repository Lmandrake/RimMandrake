# TESTENV_SWEPT_BRUISE_HARDEN_OWN_HAZARD

Filed by BENCH 2026-10-15 (r6). Evidence: `Transient/bench_live_20261015_r6/live/river/ext_river.log` (the GOVERNOR_STOP
line) and `ext_river_swept2.log`.

What happened:
- FlowWorks' river extension row `swept/returns_home` stages throwaway colonists on moving water at the map edge and waits
  for the current to carry one off.
- The current bruised the swept colonist: Fitz went from health 1 to 0.95, Bruise/Torso, from
  `RM_MapComponent_RiverCurrent.ApplyHazards` with `bruiseChancePerStep` 0.15 (owner card 2: "being swept bruises").
- The vitals governor stopped the wait as damage. The row was restarted, and then it PASSed. The same thing happened in r4.
- So the row was a coin flip, decided by the mod's own designed hazard.

## the choice, and why

The hazard IS the mod under test. Three options were weighed:
- **Set `bruiseChancePerStep` to 0 for the row.** Rejected. The row would no longer run the shipped mod. A defect in the
  hazard path (for example a bruise that downs or kills a swept pawn, or a drop-carried bug) would never show up here.
- **Protect the staged colonists.** Rejected. It hides all harm, not just the expected one.
- **Classify the expected disturbance.** Chosen. Inside the wait, a vitals 'hurt' trigger is resumed past (and noted) only if
  all three hold:
  - it is on one of THIS row's staged throwaway pawns (ThingIDs from its own `spawn_pawn`),
  - its newest hediff is `Bruise` (Blunt on flesh, exactly what ApplyHazards inflicts),
  - every other trigger in the stop is either that or an info-severity ride-along (departed/hurt/downed, nobody critical).
  Anything else still stops the clock and restarts the row: another pawn hurt, another hediff, a downed or dead staged pawn,
  a hostile.
- The setting is never touched. The row measures exactly what it claims (swept to the edge, washed away, walks home) on the
  shipped mod. Each bruise it resumed past is recorded as evidence that the hazard ran.

## built (2026-10-15, offline)

- `Utils/modcheck/clockgate.py`: `expected_disturbance(label, pred)` is a context manager. `expected_stop_label` is pure,
  and `resumable_stop` covers the benign case or a declared one. `advance_chunk` resumes past a stop only when one of those
  accounts for it. Every resume lands in `BENIGN_STOPS` with `why` and `subjectId`.
- `governor.RowGovernor` is unchanged on purpose. It declares expected transitions through `RowContract(expected=...)`, and
  its verdict honours them.
- `Utils/modcheck/testenv_guards.py`: `expected_hurt(subject_ids, hediff)` is the predicate.
- `FlowWorks/northstar/extensions_rivers.py` `swept`: the wait loop runs inside
  `clockgate.expected_disturbance("swept bruise ...", expected_hurt(staged, "Bruise"))`. Resumed bruises become a component
  note.

## offline checks (can go red)

- `selftest_clockgate.py` `test_expected_disturbance` checks five things:
  - a declared bruise resumes the full chunk and is noted with its subject,
  - the same stop outside the block raises GovernorStop,
  - another colonist's bruise raises,
  - another hediff on the staged pawn raises,
  - a death riding along raises, and a predicate that throws never resumes.
- `selftest_testenv_guards.py` `test_expected_hurt` covers id forms, other pawns, other hediffs, a prefix lookalike and
  downed.
- `FlowWorks/northstar/selftest_extensions.py` runs the real `swept` chain. During its wait, only a Bruise on its own staged
  pawn is declared, and nothing is left declared after the row. It was checked red by changing the declared hediff.

## proof (next live round, bridge held, ratchet_pilot tier)

```
timeout 500 python.exe src/RimMandrake/FlowWorks/northstar/river_site.py 2>&1 | tr -d '\r' > "D:\Luke\dev\_rmscratch\<round>\river_site.log"
timeout 600 python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --chains swept --out "D:\Luke\dev\_rmscratch\<round>\ext_swept.json" 2>&1 | tr -d '\r' | tee "D:\Luke\dev\_rmscratch\<round>\ext_swept.log" | grep -E "returns_home|GOVERNOR_STOP|declared river bruises"
```
Run the swept chain 3 times (the bruise roll is 15% per step). Expect:
- `returns_home` PASS every time with no restart.
- Any bruise shows as the component note "declared river bruises resumed past", not as a GOVERNOR_STOP.
