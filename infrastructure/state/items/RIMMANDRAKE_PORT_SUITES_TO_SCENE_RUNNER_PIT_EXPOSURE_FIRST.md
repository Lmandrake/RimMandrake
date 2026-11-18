# RIMMANDRAKE_PORT_SUITES_TO_SCENE_RUNNER_PIT_EXPOSURE_FIRST

## spec
Child of `RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE` (first slice fd8e514b76: `jawa/run_scenes`, `[RMTest]`, one EK
suite of two scenes). The rest of the ticket's scope, after `RIMMANDRAKE_PROVE_SCENE_RUNNER_LIVE_SAME_ROWS_FEWER_CALLS`
shows the shape holds live:

1. FlowWorks `src/RimMandrake/FlowWorks/northstar/pit_exposure_live.py`, the tick-bound suite (465 to 529 s a run, about
   407 s of it in 10 tick calls; live_test_speed_assessment_2026-11-12.md section 2): its staging and verdicts move into a
   FlowWorks proof-build suite (RM_PROOFS) with `[RMTest]` scenes and at least one Outside count each.
2. The rest of Explosive Knockback's `RM_KnockbackProof.SceneNames` (one `[RMTest]` line each on `RM_KnockbackScenes.Scene`,
   the ticks each scene needs), so `knockback_runner.py` can retire.
3. Only then, other mods' proof classes (about 110 C# files with an `RM_*Proof` class, no common shape), one suite at a time,
   each keeping a row read from outside the mod (assessment section 3 (c)).

Not in scope: a flyer's flight (never live-tested without the owner), anything in an owner-held biome mod
(`mod_owner_hold.json`).

## criteria
- Each ported suite: one `jawa/run_scenes` call answers every scene it had, with the old driver's verdicts on the same map,
  and no row-set without an `outside` row (scene_runner.py's SUITE_OUTSIDE_READ guard reads UNMEASURED otherwise).
- Acceptance test (offline, per suite): a selftest that the suite type declares one `[RMTest]` per old scene name and that
  each has an Outside count; written with the port and watched failing on the base.

## verify
- Per suite, the live before/after record as in the parent's live proof (rows identical, wall time and calls recorded).

## refs
file: src/RimMandrake/FlowWorks/northstar/pit_exposure_live.py
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackScenes.cs
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneRunnerCore.cs
