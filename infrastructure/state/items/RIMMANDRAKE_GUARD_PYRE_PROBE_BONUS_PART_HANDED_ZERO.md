# RIMMANDRAKE_GUARD_PYRE_PROBE_BONUS_PART_HANDED_ZERO

T_ASH_PROBE_OFFLINE missed ProbeCell handing ProbeLine 0 for the bonus

## spec
Bar ash_fertility_probe asks for the fresh-burn bonus per cell; ProbeCell passing 0f instead of comp.BonusAt stayed green (the static check named only the grid fertility, switch, gate, roof and cap). Fixed: ProbeCell must pass the cell's own parts (BonusAt, IsWatered, burnTick, the black-rain stamp, the bonus clock).

## verify
Acceptance test: python3 design/concepts/Pyrelands/version/blind_challenge/cycle_3/lane2/catch.py probecell_bonus_dropped T_ASH_PROBE_OFFLINE: rc 1 on 912c1ee157, rc 0 at the fix.

## criteria
The named command passes at the fix sha; the planted fault (lane2/planted_faults.json) is caught.

## refs
file: src/RimMandrake/Pyrelands/selftest_pyrelands_ash_probe.py
