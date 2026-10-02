# Donor swaps belt 2026-10-02

Skeleton. Entries: file | old | new | commonality | status
- src/RimMandrake/TheSump/Defs/BiomeDefs/RM_TheSump_Biome.xml | AA_TarGuzzler | RM_Gulveth | 0.5 | SWAPPED (guard dropped; own-mod def; stale header comment fixed)
- src/RimMandrake/TheSump/Defs/BiomeDefs/RM_TheSump_Biome.xml | AA_Bumbledrone | RM_Thrummel | 0.35 | SWAPPED
- src/RimMandrake/TheSump/Defs/BiomeDefs/RM_TheSump_Biome.xml | AA_BumbledroneHierophant | RM_ThrummelWarden | 0.2 | SWAPPED
- src/RimMandrake/TheSump/Defs/BiomeDefs/RM_TheSump_Biome.xml | AA_BumbledroneQueen | RM_ThrummelBroodmother | 0.5 | SWAPPED
- src/RimMandrake/Abyss/Defs/BiomeDefs/RM_Abyss.xml | AA_SandProwler | RM_Vosska (MayRequire mandrake.rm.longshade) | 0.075 | SWAPPED
- src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml (RM_FloodedCanyon value) | AA_SandSquid | RM_Ommok (MayRequire mandrake.rm.longshade) | 0.1 | SWAPPED
SKIPPED, port def exists but NO PNG anywhere in src (art not wired; texPath is donor path or placeholder):
- RM_LeaningScrub AA_Cactipine 0.25 -> RSW_Chikka; AA_Needlepost 0.1 -> RSW_Skorra; AA_Wildpawn 0.1 -> RSW_Durrok; AA_Wildpod 0.025 -> RSW_Mullgoth; Terrorworm 0.7 -> RSW_Vurra; Plant_Nysyllin_Wild 0.22 -> RSW_Plant_Nysyllin_Wild (donor placeholder texPath)
- WildAnimals_Greentide AA_Needlepost 0.3 -> RSW_Skorra; RM_TheRot AA_Wildpawn 0.2 -> RSW_Durrok, AA_Wildpod 0.2 -> RSW_Mullgoth; RM_Cauldron AA_Wildpod 0.05 -> RSW_Mullgoth
- RM_NightsideIce AA_Terramorph 0.003 -> RSW_Khorrak; AA_TetraSlug 0.002 -> RSW_Vozzik; RM_WeepingStones AA_Eyeling 0.1 -> RSW_Ikee (no PNG)
SKIPPED, tier law: RM_NightsideIce AA_BoulderMit 0.004 -> RSW_Korrum (art exists, but an RSW_ name in an RM_-tier biome file breaks Q11; needs routing via a Utinni patch = a placement decision)
NOTE: all RSW_ ports above also name Star Wars defs inside RM_ files, which Q11 forbids; art gating alone already skips them.
