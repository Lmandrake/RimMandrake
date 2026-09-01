using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(TurretTop), "get_CurRotation")]
internal class VanillaExpandedFramework_TurretTop_get_CurRotation_Patch
{
	public static bool Prefix(ref Building_Turret ___parentTurret, ref int ___ticksUntilIdleTurn, ref float __result)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		if (___parentTurret.AttackVerb is Verb_ShootCone)
		{
			LocalTargetInfo currentTarget = ___parentTurret.CurrentTarget;
			if (!((LocalTargetInfo)(ref currentTarget)).IsValid)
			{
				Rot4 rotation = ((Thing)___parentTurret).Rotation;
				__result = ((Rot4)(ref rotation)).AsAngle;
				return false;
			}
		}
		return true;
	}
}
