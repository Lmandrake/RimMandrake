using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(BackstoryDef), "BodyTypeFor")]
public static class VanillaExpandedFramework_BackstoryDef_BodyTypeFor_Patch
{
	public static void Postfix(ref BodyTypeDef __result, Gender g)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Invalid comparison between Unknown and I4
		if (__result == null)
		{
			if (Rand.Value < 0.5f)
			{
				__result = BodyTypeDefOf.Thin;
			}
			else if ((int)g == 2)
			{
				__result = BodyTypeDefOf.Female;
			}
			else
			{
				__result = BodyTypeDefOf.Male;
			}
		}
	}
}
