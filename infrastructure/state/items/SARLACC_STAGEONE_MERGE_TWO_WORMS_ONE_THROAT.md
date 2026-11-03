# SARLACC_STAGEONE_MERGE_TWO_WORMS_ONE_THROAT — one Stage-I young sarlacc def, not two

**Owner, by question card 2026-10-09 (ledger note on SARLACC_SEEKER_ROOTING_1):** merge the two stage-one
young-sarlacc defs into one.

**The two today:**
- `RSW_SarlaccSwimmer` (`src/RimStarWars/Sarlacc/Defs/ThingDefs_SarlaccSwimmer.xml`): Anomaly Devourer body, think
  tree and **placeholder Devourer art**; CompDevourer swallow-whole, which is the ONLY trigger of the seven
  changed-return hediffs (Fork 8, `CompSarlaccSwimmer.GrantChangedReturn`); spawned by the two once-per-map incidents
  (`IncidentDefs_SwimmerRoad.xml` RM_LongShade, `IncidentDefs_SwimmerSeep.xml` RM_Stillsand) through
  `RSW_SwimmerRoad.cs` (pawnKind default `RSW_SarlaccSwimmer`, Devourer_PreWander job giver, CompDevourer reads).
- `RM_Gulloth` (`src/RimMandrake/LongShade/Defs/ThingDefs_Races/RM_LongShade_Fauna.xml`): ordinary predator with
  **real art**, egg layer, wild in RUT_Desert / RM_LongShade, renamed into the RM tier by owner card 2026-10-08; the
  Sarlacc mod patches CompSarlaccSwimmer onto it (`Patches/RSW_SarlaccSeeker_Rooting.xml`; kill top-up, fed-then-water,
  roots only in light/extreme desert — SARLACC_SEEKER_ROOTING_1).

**Why it was split off SARLACC_SEEKER_ROOTING_1:** merging either way rewires the two incidents and their job logic,
and folding the swimmer into the gulloth drops the Devourer swallow and with it Fork 8's only trigger. Decide first,
from these facts: which def survives (the gulloth has the art and the roster place and the owner's latest name), and
how the swallow / changed-return survives (a gulloth swallow comp like `RM_HwelgrueSwallow.cs` / Titanoslime's hold,
or a kill-path grant). Then delete the loser and fix every inbound reference (incidents, `RSW_SwimmerRoad.cs`,
`validation.py` SWIMMER, `selftest_sandswim_owner.py`, About.xml, the Qorrax comment), with selftests, and a live
proof of both incidents on the merged def.
