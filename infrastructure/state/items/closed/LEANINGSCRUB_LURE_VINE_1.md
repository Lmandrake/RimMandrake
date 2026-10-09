## spec
RM_LureVenomvine drops RM_LureFruit (VegetableOrFruit, RawTasty, rots in 3 days) on its own cell while fewer than 3 lie within 3 cells. Wild animals that eat fruit are drawn to it and cross the thicket's venom to reach it. Setting `lureEnabled`. PROVISIONAL.
Code: `src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs` (kernel `Kernel/RM_FourFormsKernel.cs`, check `Source/SelfTest/LeaningScrubFourFormsCheck.cs`). Defs: `Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml`, `Defs/ThingDefs_Items/RM_VenomvineFourFormsSupport.xml`. Art: interim picture (thicket render), 5 jobs queued from `infrastructure/artpipe/art_lists/leaningscrub_fourforms_2026-10-09.csv`.

## criteria
- [ ] A1: A grown lure stand keeps up to 3 fruit near itself; off drops none. (`RM_FourFormsProof` lure)
- [ ] A2: UNMEASURED live: a hungry wild herbivore actually walks to the fruit. Watch with the owner or log a hunger-forced animal.
- [ ] A3: Fruit is edible by colonists too (it is bait both ways).

## verify
- Offline: `PYTHONPATH=src/RimMandrake/Utils python3 src/RimMandrake/LeaningScrub/validation.py`, `python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py`, `python3 src/RimMandrake/Utils/selftest_leaningscrub_fuzz.py --fuzz-scale 0.05`.
- Live (bridge free): `python.exe src/RimMandrake/Utils/modcheck/cli.py run LeaningScrub` chain `four_forms`; or `jawa/static_call` `RM_FourFormsProof.ProofForm` with `lure|on` then `lure|off`.
