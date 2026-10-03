## Scope built (Pillar Arm + Lash, offline-checkable)

Design: `design/Jawa/worldbuilding/biomes/contagion_grown_limbs_2026-09-30.md`, built to its
recommendations (grade source A only, plain-random roll, first-pass numbers).

- `RM_PillarArm` / `RM_Lash` hediffs (`Defs/HediffDefs/RM_GrownLimbHediffs.xml`), Shoulder
  Hediff_AddedPart on Anomaly's `AddedMutationBase`, stats per the sheet.
- `RM_PillarArmItem` / `RM_LashItem` (`Defs/ThingDefs/RM_MonstrousLimbs.xml`), install recipes on
  vanilla `Recipe_InstallArtificialBodyPart` (`Defs/RecipeDefs/RM_InstallMonstrousLimbs.xml`).
- `HediffComp_UnfinishedEmerge`: surgical removal or replacement spawns a manhunter
  `RM_TheUnfinished` and sends a ThreatBig letter.
- `CompGenomeSample.monstrous` grade (Scribed); Coalescence death-spill samples are Monstrous;
  `AmoebaHostUtility.CompleteGestation` grows one unmatched limb from a Monstrous sample.
- Mod Settings: `grownLimbsEnabled` (off: a Monstrous sample grows the normal organ batch).

## Not built, filed or owed

- Live checks (need game up): install recipe appears on a colonist, the verb tools show and hit,
  removal spawns the Unfinished, Monstrous injection yields a limb.
- Art: render nodes reuse Anomaly's FleshWhipLimb/TentacleLimb textures as placeholders and the
  item icons are tinted vanilla HealthItem. Bespoke art: `CONTAGION_GROWN_LIMBS_ART_1`.
- Eyeburst, Caudal Spring, Bellows: `CONTAGION_GROWN_LIMBS_REST_1`.
- The inject job and float menu take the FIRST `RM_GenomeSample` in the colonist's inventory, so
  a carried Normal sample can be injected ahead of a Monstrous one. Fix when the live pass
  runs (pick the sample explicitly).
- The sheet's owner `Rule:` lines are blank; this build follows the sheet's own recommendations.
  The "shared rider" (limbs count as Contagion tissue under the Burn) is NOT built.
