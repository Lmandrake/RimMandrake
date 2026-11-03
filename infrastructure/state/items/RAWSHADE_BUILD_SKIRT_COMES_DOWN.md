# RAWSHADE_BUILD_SKIRT_COMES_DOWN

## What
Build `RM_Rawshade` as designed in `design/Jawa/worldbuilding/biomes/contagion_rawshade_2026-11-02.md`
(judge record beside it: KEEP on name, description, behaviour and numbers). Its "Wiring the build item owes"
section is the checklist: ThingDef + PawnKindDef (Crispling goo-bud pattern), render C installed through
`art install`, roster/BiomeDef/armoredNatives rows, the generic `RM_LivingCanopy` extension plus a fifth
`RM_SkyKernel.Exposed` input with an offline unit test, a `burn_forced` proof row, and the sheet amendment.

## Watch out
- Render C lives in `_artsrc/arteval_RM_Scaldhide_r1_*` under the Scaldhide's name. Install it under
  `RM_Rawshade`, and do not touch the Scaldhide's installed art (render B, which the owner kept).
- The canopy applies only while the pawn is standing. If a moving Rawshade sheltered anything, natives
  would chase it.
- `RM_SkyKernel.Exposed` is shared by the dive search and the damage pulse. Change it in one place only.
