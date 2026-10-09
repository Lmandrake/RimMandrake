## spec
RM_SleeperVenomvine (labelled `dead venomvine`, grey-tinted, no venom comps, no barrier: a harmless-looking snarl) registers with RM_MapComponent_SleeperWatch; a grounded body of size >= 0.5 within 1.5 cells wakes it into RM_SleeperVenomvineAwake (a live stand) and lashes whoever is beside it for 6. Setting `sleeperEnabled`; off: it stays dead-looking. PROVISIONAL.
Code: `src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs` (kernel `Kernel/RM_FourFormsKernel.cs`, check `Source/SelfTest/LeaningScrubFourFormsCheck.cs`). Defs: `Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml`, `Defs/ThingDefs_Items/RM_VenomvineFourFormsSupport.xml`. Art: interim picture (thicket render), 5 jobs queued from `infrastructure/artpipe/art_lists/leaningscrub_fourforms_2026-10-09.csv`.

## criteria
- [ ] A1: A colonist next to a sleeper wakes it into RM_SleeperVenomvineAwake and is hurt; off leaves it asleep. (`RM_FourFormsProof` sleeper)
- [ ] A2: A hare-sized animal (< 0.5) does not wake it. Live.
- [ ] A3: Wild spawn placement is NOT done: the sleeper is not yet in any biome's plant list (owed: a placement choice for the owner's Leaning Scrub sitting).

## verify
- Offline: `PYTHONPATH=src/RimMandrake/Utils python3 src/RimMandrake/LeaningScrub/validation.py`, `python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py`, `python3 src/RimMandrake/Utils/selftest_leaningscrub_fuzz.py --fuzz-scale 0.05`.
- Live (bridge free): `python.exe src/RimMandrake/Utils/modcheck/cli.py run LeaningScrub` chain `four_forms`; or `jawa/static_call` `RM_FourFormsProof.ProofForm` with `sleeper|on` then `sleeper|off`.
