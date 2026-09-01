using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[StaticConstructorOnStartup]
public static class VanillaExpandedFramework_PregnancyUtility_PregnancyChanceForPartners_Patch
{
	public static readonly Func<Pawn, Pawn, float> pregnancyChanceForPartnersWithoutPregnancyApproachInfo;

	static VanillaExpandedFramework_PregnancyUtility_PregnancyChanceForPartners_Patch()
	{
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Expected O, but got Unknown
		pregnancyChanceForPartnersWithoutPregnancyApproachInfo = (Func<Pawn, Pawn, float>)Delegate.CreateDelegate(typeof(Func<Pawn, Pawn, float>), AccessToolsExtensions.Method(typeof(PregnancyUtility), "PregnancyChanceForPartnersWithoutPregnancyApproach", (Type[])null, (Type[])null));
		VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(PregnancyUtility), "PregnancyChanceForPartners", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(AccessTools.Method(typeof(VanillaExpandedFramework_PregnancyUtility_PregnancyChanceForPartners_Patch), "Postfix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null);
	}

	public static void Postfix(Pawn woman, Pawn man, ref float __result)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		if (woman.gender != man.gender && woman.relations.GetAdditionalPregnancyApproachData().partners.TryGetValue(man, out var value))
		{
			if (value.pregnancyChanceForPartners.HasValue)
			{
				__result = value.pregnancyChanceForPartners.Value;
			}
			else if (value.pregnancyChanceFactorBase.HasValue)
			{
				float num = pregnancyChanceForPartnersWithoutPregnancyApproachInfo(woman, man);
				float value2 = value.pregnancyChanceFactorBase.Value;
				__result = num * value2;
			}
		}
	}
}
