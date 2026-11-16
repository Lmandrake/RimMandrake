## spec
Contagion 0.1.0 must be whole without what the owner moved to Design Version 0.2.0 on 2026-11-16
(OWNER:1794842455892769878: the Coalescence, the Grown Limbs, Helix trade). Their code stays built, and a built
capability ships until removed, so 0.1.0 ships each one switched OFF: in `src/RimMandrake/Contagion/Source/RM_ContagionMod.cs`
set `coalescenceEnabled`, `grownLimbsEnabled` and `draftprintsEnabled` to `false` (update their comments: "Design
Version 0.2.0; off at shipped defaults"). Then make the old live suite opt in where it tests them: `validation.py`
`DEFAULTS` gets the three as `False`; the `coalescence` chain, the genome chain's Monstrous components
(`monstrous_gestation_grows_one_limb`, `grown_limbs_off_grows_organs`) and the touched chain's Coalescence-contact arm
turn their switch ON for their own span (note `_setting` restores the SHIPPED default, now off, so a chain-wide opt-in
must not be undone by an inner `_setting(..., False)`); the walk's `## must be true` lines 27-28 read "defaults off".
Rebuild with `winbuild.py Contagion`; the DLL travels with its `.srchash`. Today a player meets all three ON.

## verify
The acceptance test passes; `run_selftests.py --only selftest_contagion` passes; the live suite's coalescence and
genome chains are recorded UNRUN with their command until a bridge run.

## criteria
Acceptance test (offline, watched FAIL on base e620e75af1: `0 of 6`, exit 1; passes at `6 of 6`, exit 0):
python3 -c "import re,sys; s=open('src/RimMandrake/Contagion/Source/RM_ContagionMod.cs').read(); v=open('src/RimMandrake/Contagion/validation.py').read(); F=('coalescenceEnabled','grownLimbsEnabled','draftprintsEnabled'); ok=[re.search(r'public static bool %s = false;'%f, s) is not None for f in F]+[re.search(r'\"%s\": False'%f, v) is not None for f in F]; print(sum(ok),'of 6'); sys.exit(0 if all(ok) else 1)"
plus `python3 src/RimMandrake/Contagion/selftest_contagion.py` still passing (the fake game reads `V.DEFAULTS`).
Live: `sc_settings_superb` reads the three off at shipped defaults (design/concepts/Contagion/scenes.json), UNRUN.
