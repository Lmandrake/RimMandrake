# Titanic harness fixes 2026-10-07 (uncommitted)
File: src/RimMandrake/TitanicCreatures/validation.py (only file changed). py_compile OK; `python3 validation.py` -> STATIC: PASS (0 findings). Not run live.
- Control lane: 6 -> 22 cells from the beast; clear_area now 60 (site half 30), so lane is inside the cleared site.
- _sweep_filth: destroy_batch categories=Filth over the whole site, before spawning and again right before the Goto orders; baseline now asserts zero rubble on both lanes (else UNMEASURED).
- wake_off_leaves_no_trail and crush_damage_multiplier: run with_control=False (lone Elephant, no Rat), assertions unchanged (0 rubble and 6/6 plants; 6/6 plants at 0.1x).
- t1 component: Rat control lane still must show 0 filth and 6/6 plants, assertions unchanged.
- Pre-existing static fail fixed: crush-rule count probe compared the bare tag, but XML tags are namespaced (ty.endswith("RM_CrushRuleDef")).
Remaining UNMEASURED: the five not_driven rows. Vanilla Core/Royalty/Biotech/Anomaly/Odyssey race baseBodySize max is 5.0 (Dreadmeld, Moose); none >= 8, so none spawnable. Proposal (not added): a debug-set pawn BodySize/tier override tool in JawaBench, or a tiny test-only race def with baseBodySize 8 (and 20) in a test-only mod.
