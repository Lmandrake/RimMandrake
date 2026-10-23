# BodyPartDef `Shell` blast radius (2026-10-22, run S)

**DONE 2026-10-22 (owner, Biome card 1 → rename Cephaloid Shell to RUT_CephaloidShell):** our 2500-HP part is now `RUT_CephaloidShell`, used only by the Cephaloid and Nautiloid bodies; vanilla `Shell` is no longer overridden for the other bodies below. Ship save holds 0 Cephaloid/Nautiloid/`<def>Shell</def>` (grep-counted; `measure` not installed here). The analysis below is the pre-fix state.

Override lives in src/RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml (2500 HP, indestructible). Same defName `Shell` as vanilla/DLC body part, so it replaces it for EVERY body part row using def Shell, including vanilla bodies (e.g. insect/tortoise-class vanilla animals). Not renamed: needs owner OK.

BodyDefs in src with a part `<def>Shell</def>` (count of rows) and ThingDefs naming them:

- `<<BodyPartDef Shell DEFINITION>>` x1 in `src/RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml`
- `Cephaloid` x1 in `src/RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml`
    - used by `RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml`
- `Nautiloid` x1 in `src/RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml`
    - used by `RimUtinni/UtinniPatches/Defs/Absorbed_Cephaloids/Absorbed_Cephaloids_Defs.xml`
- `RM_BeetleLikeWithStinger` x1 in `src/RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_Bodies.xml`
    - used by `RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_ThingDefs_Races.xml`
- `RM_BodyVisceral` x1 in `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RM_Visceral.xml`
    - used by `RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RM_Visceral.xml`
- `RM_MantisLike` x1 in `src/RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_Bodies.xml`
    - used by `RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_ThingDefs_Races.xml`
- `RM_MothLike` x1 in `src/RimMandrake/LanternDeeps/Defs/Fauna/RM_LanternDeeps_Fauna_Bodies.xml`
    - used by `RimMandrake/LanternDeeps/Defs/Fauna/RM_LanternDeeps_Fauna_ThingDefs_Races.xml`
- `RM_RotMothLike` x1 in `src/RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_Bodies.xml`
    - used by `RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_ThingDefs_Races.xml`
- `RSW_Acklay` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveB_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Acklay.xml`
- `RSW_BeetleLikeWithHorn` x1 in `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/Bodies/RSW_BiomesTeamPort_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`
- `RSW_BeetleLikeWithStinger` x1 in `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/Bodies/RSW_BiomesTeamPort_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`
- `RSW_CanCell` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_CanCell.xml`
- `RSW_EnergySpider` x1 in `src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_W3d.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_EnergySpider.xml`
- `RSW_Gelagrub` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Gelagrub.xml`
- `RSW_GraniteSlug` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_GraniteSlug.xml`
- `RSW_Kinrath` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Kinrath.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_VentStalker.xml`
- `RSW_Klorslug` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Klorslug.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_TunnelSnake.xml`
- `RSW_Kreetle` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Kreetle.xml`
- `RSW_Krykna` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Krykna.xml`
- `RSW_KwazelMaw` x1 in `src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_W3d.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_KwazelMaw.xml`
- `RSW_LavaFlea` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_LavaFlea.xml`
- `RSW_Lylek` x1 in `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Lylek.xml`
- `RSW_MantisLike` x1 in `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/Bodies/RSW_BiomesTeamPort_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`
- `RSW_MothLike` x1 in `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/Bodies/RSW_BiomesTeamPort_Bodies.xml`
    - used by `RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`
- `RSW_Silooth` x1 in `src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_W3e.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Silooth.xml`
- `RSW_Taozin` x1 in `src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_W3e.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Taozin.xml`
- `RSW_TetnissCrab` x1 in `src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_W3e.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_TetnissCrab.xml`
- `RSW_Vapaad` x1 in `src/RimStarWars/SWBestiary/Defs/DonorPackPort/RSW_DonorPack_W2a.xml`
    - used by `RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Vapaad.xml`
- `VAEWaste_Megatardi` x1 in `src/RimUtinni/UtinniPatches/Defs/Absorbed_VAEWasteMegatardi/Absorbed_VAEWasteMegatardi_Defs.xml`
    - used by `RimUtinni/UtinniPatches/Defs/Absorbed_VAEWasteMegatardi/Absorbed_VAEWasteMegatardi_Defs.xml`

Vanilla bodies using Shell are NOT in src; use `measure`/def dump to count them (not done here).
