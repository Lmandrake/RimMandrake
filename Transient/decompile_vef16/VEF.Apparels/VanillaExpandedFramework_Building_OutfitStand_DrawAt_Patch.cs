using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Building_OutfitStand), "DrawAt")]
public static class VanillaExpandedFramework_Building_OutfitStand_DrawAt_Patch
{
	public static void Postfix(Building_OutfitStand __instance, Vector3 drawLoc)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		foreach (Thing heldItem in __instance.HeldItems)
		{
			if (heldItem is Apparel_Shield apparel_Shield)
			{
				apparel_Shield.DrawShield(apparel_Shield.CompShield, drawLoc, ((Thing)__instance).Rotation);
			}
		}
	}
}
