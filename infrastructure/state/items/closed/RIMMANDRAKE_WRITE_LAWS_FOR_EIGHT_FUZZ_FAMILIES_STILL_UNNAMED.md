# RIMMANDRAKE_WRITE_LAWS_FOR_EIGHT_FUZZ_FAMILIES_STILL_UNNAMED

## spec
Child of `RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS`. The matrix runs eight families no written law names yet, so a red there reads "none named by a law"
(`python3 src/RimMandrake/Utils/vv_laws.py lint` lists them): FlowWorks fills_from_limitless, surface_random,
seq_sequences, seq_pitwidth, hose, trail; EmpirePursuit timers, math. For each: the laws its assertions enforce (a
sentence and the exact assertion text) in the mod's laws.json, and a planted break per new law family. Then the mods
with C# kernel fuzz (`selftest_*_fuzz.py` with a `mutate_<mod>_fuzz.py`), per the parent's step 1.

## criteria
- Acceptance test: `vv_laws.py lint` prints "matrix families with no law yet: none" for both mods and exits 0, and
  `vv_laws.py prove` shows every new family PROVEN; lint lists 8 today (watched 2026-11-18).

## verify
- The two commands above.

## refs
file: src/RimMandrake/FlowWorks/Source/SelfTest/VV/laws.json
file: src/RimUtinni/EmpirePursuit/Source/SelfTest/VV/laws.json
