# LOADLOG C 2026-10-03 dispositions
1. RM_WarDust Chemfuel_Drop -> Standard_Drop (Scarlands/Defs/ThingDefs_Items/RM_WarDust.xml). SoundDef sweep of 8 mods (424 refs, probe ok) also fixed: Warg_Eat -> PredatorLarge_Eat (RM_WarscarFauna.xml), Shot_Sniper -> Shot_TurretSniper (RM_OldLineTurret.xml). BeamGraser_Shooting (Biotech) and Pawn_Pinniped_* (Odyssey) are DLC sounds, valid, left.
2. RM_Chotrix tool Mouth -> Teeth (QuadrupedAnimalWithPaws has Teeth group, no Mouth).
3. RM_Chatrak trainability Simple -> None (valid: None/Intermediate/Advanced).
4. RM_Velloch: NOT stale. Plant def exists in src TheSump RM_SumpFlora.xml; the deployed RimMandrake.Biomes/Biomes/TheSump has no ThingDefs_Races or RM_SumpFlora.xml, so all Sump flora+fauna rows fail (deploy staleness). No edit; needs deploy.
