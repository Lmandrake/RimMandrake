using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Building_TurretGun), "DrawExtraSelectionOverlays")]
public static class VanillaExpandedFramework_Building_TurretGun_DrawExtraSelectionOverlays_Patch
{
	public static void Postfix(Building_TurretGun __instance)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		if (((Building_Turret)__instance).AttackVerb is Verb_ShootCone verb_ShootCone)
		{
			((Verb)verb_ShootCone).DrawHighlight(((Verb)verb_ShootCone).CurrentTarget);
		}
	}
}
