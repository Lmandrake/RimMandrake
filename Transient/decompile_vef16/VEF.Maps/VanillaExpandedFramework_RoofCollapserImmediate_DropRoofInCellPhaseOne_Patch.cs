using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Maps;

[HarmonyPatch(typeof(RoofCollapserImmediate), "DropRoofInCellPhaseOne")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_RoofCollapserImmediate_DropRoofInCellPhaseOne_Patch
{
	private static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		foreach (RoofDef allDef in DefDatabase<RoofDef>.AllDefs)
		{
			RoofExtension modExtension = ((Def)allDef).GetModExtension<RoofExtension>();
			if (modExtension != null && !modExtension.AlwaysDealsDamageOnCollapsed)
			{
				return true;
			}
		}
		return false;
	}

	private static bool Prefix(IntVec3 c, Map map)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		RoofDef val = map.roofGrid.RoofAt(c);
		RoofExtension roofExtension = ((val != null) ? ((Def)val).GetModExtension<RoofExtension>() : null);
		if (roofExtension == null || roofExtension.DealDamageOnCollapsed(map, c, val))
		{
			return true;
		}
		FleckMaker.ThrowDustPuff(((IntVec3)(ref c)).ToVector3Shifted() + Gen.RandomHorizontalVector(0.6f), map, 2f);
		return false;
	}
}
