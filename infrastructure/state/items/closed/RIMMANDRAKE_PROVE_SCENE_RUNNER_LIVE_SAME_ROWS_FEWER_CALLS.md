# RIMMANDRAKE_PROVE_SCENE_RUNNER_LIVE_SAME_ROWS_FEWER_CALLS

## spec
Child of `RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE` (first slice landed fd8e514b76, offline only). The ticket's own
proof, which needs the live game: run the ported Explosive Knockback suite (the showcase `storeroom_bomb_pit` and its
pit-filled control) both ways on the same scratch map and record wall time and bridge-call count, with every verdict row
identical.

- Before: `python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes storeroom_bomb_pit,storeroom_bomb_pit_control --ticks 900`
  (one bridge call per Stage, per clock step, per Verdict, plus a settings read and write per field).
- After: `python.exe src\RimMandrake\Utils\scene_runner.py --type RimMandrake.ExplosiveKnockback.RM_KnockbackScenes`
  (one `jawa/run_scenes` call, wrapped in the scene-begin save and its reload; prints its own time split and call count).
- Setup, both arms: the JawaBench companion built and deployed with `jawa/run_scenes`
  (`python3 src/RimMandrake/bridgetools/build.py --apply`, then a game restart: companions load at bridge start), and the
  EK proof build (`python3 src/RimMandrake/Utils/winbuild.py ExplosiveKnockback -- -p:RmProofs=true`, deploy, and the release
  build back afterwards). Quicktest map on the minimal list plus LWM's Deep Storage (scenes.json sc_storeroom_bomb_pit setup).
- Also read: the runner's Outside row (haulables on the pit rows >= 1, a vanilla count) agrees with the main lane's verdict.
  If it does not, that is a finding about one of them, not a reason to edit the count.

## criteria
- Both arms on the same map: the VERDICT rows have the same status per scene (PASS/FAIL; INVALID in the old runner =
  UNMEASURED in the new), and the evidence JSON of each is kept.
- The new arm makes fewer bridge calls (counted by scene_runner.py's CountingCall; the old arm counted from the bridge
  call log) and its wall time is recorded beside the old arm's. A differing row is itself a finding (frame-bound code).
- Acceptance test: none offline, a live-game proof (UNRUN; commands above). Its offline halves are
  `selftest_scene_runner_core.py` (58 units) and `selftest_scene_runner_driver.py` (17 checks), both green at fd8e514b76.

## verify
- `scene_runner.py` prints `OUTCOME PASS (exit 0)` or the same per-scene statuses as knockback_runner.py's table, plus
  `time: ...; bridge calls {...}`; both evidence files cited on the close.

## refs
file: src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSceneRunnerTools.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackScenes.cs
file: src/RimMandrake/Utils/scene_runner.py
file: src/RimMandrake/ExplosiveKnockback/knockback_runner.py
