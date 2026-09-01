using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Building_TurretGun), "IsValidTarget")]
internal class VanillaExpandedFramework_Building_TurretGun_IsValidTarget_Patch
{
	public static void Postfix(Thing t, Building_TurretGun __instance, ref bool __result)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		if (((Building_Turret)__instance).AttackVerb is Verb_ShootCone verb_ShootCone)
		{
			__result &= verb_ShootCone.InCone(t.Position, ((Verb)verb_ShootCone).caster.Position, ((Verb)verb_ShootCone).Caster.Rotation, verb_ShootCone.VerbProps.coneAngle);
		}
	}
}
