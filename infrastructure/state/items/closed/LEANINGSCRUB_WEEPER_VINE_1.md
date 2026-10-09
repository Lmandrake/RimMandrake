## spec
RM_WeeperVenomvine. RM_CompWeeper sheds RM_VenomPool filth within radius 2 (10% per long tick) and pollutes the ground under it (Biotech pollution), at most 12 cells per stand. Settings `weeperEnabled`, `weeperPollutes` (labelled as affecting the map). PROVISIONAL.
Code: `src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs` (kernel `Kernel/RM_FourFormsKernel.cs`, check `Source/SelfTest/LeaningScrubFourFormsCheck.cs`). Defs: `Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml`, `Defs/ThingDefs_Items/RM_VenomvineFourFormsSupport.xml`. Art: interim picture (thicket render), 5 jobs queued from `infrastructure/artpipe/art_lists/leaningscrub_fourforms_2026-10-09.csv`.

## criteria
- [ ] A1: A grown weeper sheds RM_VenomPool filth; off sheds none. (`RM_FourFormsProof` weeper)
- [ ] A2: With weeperPollutes on, each pool also pollutes its cell; stops at the cap of 12. Live: read map.pollutionGrid after a few days.
- [ ] A3: Pools fade in 6-10 days and clean as ordinary filth.

## verify
- Offline: `PYTHONPATH=src/RimMandrake/Utils python3 src/RimMandrake/LeaningScrub/validation.py`, `python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py`, `python3 src/RimMandrake/Utils/selftest_leaningscrub_fuzz.py --fuzz-scale 0.05`.
- Live (bridge free): `python.exe src/RimMandrake/Utils/modcheck/cli.py run LeaningScrub` chain `four_forms`; or `jawa/static_call` `RM_FourFormsProof.ProofForm` with `weeper|on` then `weeper|off`.
