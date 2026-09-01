using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[DefOf]
public static class BSDefs
{
	public static ShaderTypeDef BS_CutoutThreeColor;

	public static ShaderTypeDef BS_TransparentThreeColor;

	public static ShaderTypeDef BS_FlatTransparentOverlay;

	public static ShaderTypeDef BS_EnergyShader;

	public static ShaderTypeDef BS_VoidShader;

	public static StatDef ButcheryFleshEfficiency;

	public static StatDef ButcheryMechanoidEfficiency;

	public static StatDef BS_MaxNutritionFromSize;

	public static StatDef SM_BodySizeOffset;

	public static StatDef SM_Cosmetic_BodySizeOffset;

	public static StatDef SM_BodySizeMultiplier;

	public static StatDef SM_Cosmetic_BodySizeMultiplier;

	public static StatDef SM_HeadSize_Cosmetic;

	public static StatDef SM_Minimum_Learning_Speed;

	public static StatDef SM_Food_Need_Capacity;

	public static StatDef SM_AttackSpeed;

	public static StatDef SM_UnarmedAttackSpeed;

	public static StatDef SM_GrowthPointAccumulation;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static StatDef BS_SoulPower;

	public static StatDef SM_FlirtChance;

	public static StatDef BS_BatteryCharging;

	public static PawnRenderNodeTagDef Root;

	public static FactionDef BS_ZombieFaction;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static TraitDef BS_Giant;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static TraitDef BS_Gentle;

	public static TraitDef Cannibal;

	public static TraitDef Beauty;

	public static TraitDef SpeedOffset;

	public static TraitDef Tough;

	public static TraitDef Masochist;

	[MayRequire("Ludeon.Rimworld.Biotech")]
	public static GeneDef BS_OverrideDummyGene;

	[MayRequire("Ludeon.Rimworld.Biotech")]
	public static GeneDef Robust;

	[MayRequire("Ludeon.Rimworld.Biotech")]
	public static GeneDef DiseaseFree;

	[MayRequire("Ludeon.Rimworld.Biotech")]
	public static GeneDef Ageless;

	[MayRequire("Ludeon.Rimworld.Biotech")]
	public static GeneDef Body_MaleOnly;

	[MayRequire("Ludeon.Rimworld.Biotech")]
	public static GeneDef Body_FemaleOnly;

	[MayRequire("Ludeon.Rimworld.Biotech")]
	public static GeneDef Superclotting;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static GeneDef BS_ReturningSoul;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static GeneDef BS_Immortal;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static GeneDef BS_AlienApperanceStandards;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static GeneDef BS_AlienApperanceStandards_Lesser;

	public static HediffDef BS_NoHands;

	public static HediffDef BS_PoorHands;

	public static HediffDef BS_SoulPowerHediff;

	public static HediffDef BS_Soulless;

	public static HediffDef BS_SoulCollector;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_SuccubusBond;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_SuccubusBond_Victim;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_WhiteRoseBite;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_WhiteRoseThrall;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_Euphoria;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_DraculVampirism;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_DraculAge;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_AnimalReturned;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_AnimalReturnedRotted;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_AnimalReturnedSkeletal;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef VU_DraculAnimalVampirism;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef BS_LesserDeathless_Death;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef BS_BurnReturnDenial;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static HediffDef BS_IndestructibelApparel;

	[MayRequire("RedMattis.BigSmall.Core,Ludeon.RimWorld.Ideology")]
	public static PreceptDef BS_AlienAppearanceTolerance_SomeTolerance;

	[MayRequire("RedMattis.BigSmall.Core,Ludeon.RimWorld.Ideology")]
	public static PreceptDef BS_AlienAppearanceTolerance_FullTolerance;

	public static ThingDef BS_MeatGeneric;

	public static WeaponClassDef BS_GiantWeapon;

	public static MentalStateDef BS_LostManhunter;

	public static MentalStateDef BS_LostManhunterPermanent;

	public static DamageDef Arrow;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static DamageDef BS_BiteDevourDmg;

	public static ThingDef Heart;

	public static ThingDef Lung;

	public static ThingDef Kidney;

	public static ThingDef Liver;

	public static ThingDef Filth_MachineBits;

	public static PawnCapacityDef Metabolism;

	public static ThoughtDef AteHumanlikeMeatDirectCannibal;

	public static ThoughtDef AteHumanlikeMeatDirect;

	[MayRequireIdeology]
	public static PreceptDef Cannibalism_Acceptable;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static ThoughtDef BS_DroneDied;

	[MayRequire("RedMattis.BigSmall.Core")]
	public static ThoughtDef BS_DroneLost;

	public static PawnRelationDef BS_Creator;

	public static BodyTypeDef BS_AnimalBodyType;

	public static BodyPartGroupDef Feet;

	public static BodyPartDef Brain;

	public static BodyPartDef ArtificialBrain;

	public static BodyPartDef Tail;

	public static BodyPartDef BS_Wing;

	public static RacialFeatureDef BS_Mechanical;

	public static ThingCategoryDef BS_RobotCorpses;

	public static ThingCategoryDef BS_CorpsesHumanlikeAnimals;

	public static ThingCategoryDef BS_CorpsesHumanlikeHybrids;

	public static RecipeDef BS_ShredRobot;

	public static RecipeDef BS_SmashRobot;

	public static JobDef BS_UseCharger;

	public static ShaderTypeDef CutoutComplexBlend;

	public static IncidentDef StrangerInBlackJoin;

	[MayRequireAnyOf("RedMattis.Undead,RedMattis.Yokai,RedMattis.Undead.ZombieApoc")]
	public static XenotypeDef VU_Returned_Intact;

	[MayRequireAnyOf("RedMattis.Undead,RedMattis.Yokai,RedMattis.Undead.ZombieApoc")]
	public static XenotypeDef VU_Returned;

	[MayRequireAnyOf("RedMattis.Undead,RedMattis.Yokai,RedMattis.Undead.ZombieApoc")]
	public static XenotypeDef VU_ReturnedSkeletal;

	public static PawnExtensionDef BS_DefaultAnimal_NoHands;

	public static PawnExtensionDef BS_DefaultAnimal_PoorHands;

	public static PawnExtensionDef BS_DefaultAnimal;

	public static PawnExtensionDef BS_DefaultMechanoid;

	public static ColorSettingDef BS_DefaultSapientAnimalColorA;

	public static ColorSettingDef BS_DefaultSapientAnimalColorB;

	public static bool IsBSShader(Shader shader)
	{
		if (!((Object)(object)shader == (Object)(object)BS_CutoutThreeColor.Shader) && !((Object)(object)shader == (Object)(object)BS_TransparentThreeColor.Shader) && !((Object)(object)shader == (Object)(object)BS_FlatTransparentOverlay.Shader) && !((Object)(object)shader == (Object)(object)BS_EnergyShader.Shader))
		{
			return (Object)(object)shader == (Object)(object)BS_VoidShader.Shader;
		}
		return true;
	}

	static BSDefs()
	{
		DefOfHelper.EnsureInitializedInCtor(typeof(BSDefs));
	}
}
