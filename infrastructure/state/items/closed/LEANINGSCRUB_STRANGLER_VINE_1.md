## spec
RM_StranglerVenomvine. Owner card 2026-10-08. RM_CompStrangler (Source/RM_VenomvineFourForms.cs) finds an adjacent wall or tree on each long tick, wraps it (progress 0..1) and blunt-damages it, harder as it tightens. A wrap round a player building designates the stand for cutting (trim). Setting `stranglerEnabled`, `stranglerDamageFactor`, `stranglerAutoTrim`. Numbers PROVISIONAL.
Code: `src/RimMandrake/LeaningScrub/Source/RM_VenomvineFourForms.cs` (kernel `Kernel/RM_FourFormsKernel.cs`, check `Source/SelfTest/LeaningScrubFourFormsCheck.cs`). Defs: `Defs/ThingDefs_Plants/RM_VenomvineFourForms.xml`, `Defs/ThingDefs_Items/RM_VenomvineFourFormsSupport.xml`. Art: interim picture (thicket render), 5 jobs queued from `infrastructure/artpipe/art_lists/leaningscrub_fourforms_2026-10-09.csv`.

## criteria
- [ ] A1: Wall beside a grown stand loses hit points each long tick; off leaves it alone. (`RM_FourFormsProof` strangler)
- [ ] A2: A stand wrapped round a player building gets a cut designation (stranglerAutoTrim); cutting it stops the squeeze. Live: a colonist works the designation.
- [ ] A3: Inspect text names the target and the wrap percent.

## verify
- Offline: `PYTHONPATH=src/RimMandrake/Utils python3 src/RimMandrake/LeaningScrub/validation.py`, `python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py`, `python3 src/RimMandrake/Utils/selftest_leaningscrub_fuzz.py --fuzz-scale 0.05`.
- Live (bridge free): `python.exe src/RimMandrake/Utils/modcheck/cli.py run LeaningScrub` chain `four_forms`; or `jawa/static_call` `RM_FourFormsProof.ProofForm` with `strangler|on` then `strangler|off`.
