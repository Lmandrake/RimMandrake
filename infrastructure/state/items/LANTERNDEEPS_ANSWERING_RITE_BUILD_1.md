# LANTERNDEEPS_ANSWERING_RITE_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md` §6 R1; register `design/Jawa/salvation_rites_2026-10-01.md` B8; machinery §(d) there.

The Answering, for Ohm (settlement), campaign tier in `mandrake.rut.rites`. Found: a Working Dead chassis scratching the cousins' terms into a gallery wall. Asks: a colony droid stands at the edge of a mindstone's or Shard-mind's sight while the organiser speaks the clan's terms. Needs a mindstone or Shard-mind in line of sight and a colony droid present; NOT gated on darkness. Outcomes per §6 R1 (Poor: the droid stops and is carried out; Fair: Ohm settlement entry; Good: a log line it did not write; Excellent: the line names the next mindstone).

Depends on `LANTERNDEEPS_WORKING_DEAD_BUILD_1` and `LANTERNDEEPS_MINDSTONE_GALLERY_BUILD_1`.

## verify
- Learnable from the found inscription; performable anywhere with the condition; each tier's readable sign appears.

## built (FOUNDRY, 2026-10-09; every number PROVISIONAL)
- Engine, RM tier, names no faith: `src/RimMandrake/LanternDeeps/Source/RM_Answering.cs` (target worker, outcome worker, stall and log-line hediffs, Ninefold by reflection) + pure `RM_AnsweringKernel.cs` (unit-tested in the fuzz).
- Campaign data: `src/RimUtinni/Rites/Defs/RUT_Answering.xml` (precept, pattern, behaviour, outcome 20/40/30/10, memory). Hediffs: `src/RimMandrake/LanternDeeps/Defs/HediffDefs/RM_Answering.xml`.
- Poor: droid gets `RM_AnsweringStalled` (Moving max 0, so downed and carriable; clears out of every mind's sight). Fair: Ohm +6. Good: +8 and a log-line hediff. Excellent: +10, the line names a direction and distance, and a `RUT_MindstoneVein` is placed 15-45 cells away on natural rock.
- Mod Settings: `answeringRiteEnabled`, `answeringStallEnabled`, `answeringNextStoneEnabled`.
- The found inscription is the Working Dead's inspect line. NOT built: learning the rite. `RUT_ResearchMod_GrantRite` and the found-rites row do not exist (`SALVATION_RITES_UNIFICATION_1`, owner-blocked); until then the precept is unwired, same as the Joining Water.
- UNMEASURED live: whether `GenSight.LineOfSightToThing` sees a mind in rock (the vein) and a droid downed by `Moving` max 0 is carriable.
