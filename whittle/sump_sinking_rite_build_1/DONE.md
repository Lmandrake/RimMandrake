# Done claim

Offline lane: the logic of every bullet is shown by the kernel selftest and the mod builds clean, but no bullet has been seen in a running game. That is why none says true.

- unseen: Offering a stack of pitch: the map holds `RM_TarLull_Beast` with ~15 days left; a construction wake
 | evidence: `whittle/sump_sinking_rite_build_1/evidence/kernel_selftest.txt` `whittle/sump_sinking_rite_build_1/evidence/build.log`
- unseen: Offering a dig find: the map's trap counter reads 3; forcing three trap rolls leaves every
 | evidence: `whittle/sump_sinking_rite_build_1/evidence/kernel_selftest.txt` `whittle/sump_sinking_rite_build_1/evidence/build.log`
- unseen: Any Sinking: the map holds `RUT_ImperialHoldOff` with 5 x the configured interval left and the next
 | evidence: `whittle/sump_sinking_rite_build_1/evidence/kernel_selftest.txt` `whittle/sump_sinking_rite_build_1/evidence/build.log`
- unseen: The offered Thing is destroyed (no longer spawned or held); trying to offer a pawn or corpse is refused
 | evidence: `whittle/sump_sinking_rite_build_1/evidence/kernel_selftest.txt` `whittle/sump_sinking_rite_build_1/evidence/build.log`
- unseen: Each Mod Settings toggle off removes exactly its effect (one case per toggle).
 | evidence: `whittle/sump_sinking_rite_build_1/evidence/kernel_selftest.txt` `whittle/sump_sinking_rite_build_1/evidence/build.log`

## What I'm least sure about
- The game glue (`src/RimUtinni/Rites/Source/Sinking/*.cs`) has never run. The Harmony targets and the reflected cross-mod names (RimProperty, EnvironmentalHazards, EmpirePursuit) were checked against the source in this repo, but the vanilla signatures were not checked against a 1.6 decompile.
- After the code review (54c32aae1b), the offering must lie within 3 cells of tar, it is forbidden while the rite runs, and its value feeds quality. EmpirePursuit's forced raids, second waves and ladder rungs are held past the hold-off. All of this is new, compiled and kernel-tested (74/74), but none of it has run. A ladder bombardment announced before the hold-off may still land. The live probe pours one tar cell beside the offering when no tar is near, so the scripted chain does not show a player finding tar.
- The raid lull rolls at `Storyteller.TryFire`, where a raid's faction is often still unset. A raid that rolls past the lull and then picks the Empire is still refused by the hold-off, but the lull cannot tell non-Empire raids apart before their faction is chosen.

## What I did not test
- Anything in a live game. That includes the `sinking` cases in `src/RimUtinni/Rites/validation.py`, performing the rite through the ritual dialog, save/reload mid-effect, and a real explosion near a lulled bulge.
- The `selftest_ninefold_fuzz` test running in the same `--only` call as the kernel test (they crash on a shared build). Each passes on its own.
