using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HarmonyPatch(typeof(CastPositionFinder), "TryFindCastPosition")]
public static class VanillaExpandedFramework_CastPositionFinder_TryFindCastPosition_Patch
{
	public static void Prefix(ref CastPositionRequest newReq)
	{
		Verb verb = newReq.verb;
		ThingDef val = ((verb == null) ? null : ((Thing)(verb.EquipmentSource?)).def);
		if (val != null && StatExtension.StatBaseDefined((BuildableDef)(object)val, VEFDefOf.VEF_MeleeWeaponRange))
		{
			newReq.maxRangeFromTarget = Mathf.Max(newReq.maxRangeFromTarget, StatExtension.GetStatValueAbstract((BuildableDef)(object)val, VEFDefOf.VEF_MeleeWeaponRange, (ThingDef)null));
		}
	}
}
