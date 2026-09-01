using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

public static class Patch_Pawn_HealthTracker
{
	[HarmonyPatch(typeof(Pawn_HealthTracker), "CheckForStateChange")]
	public static class VanillaExpandedFramework_Pawn_HealthTracker_CheckForStateChange_Patch
	{
		public static void Postfix(Pawn_HealthTracker __instance, Pawn ___pawn)
		{
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			if (__instance.Downed)
			{
				return;
			}
			ThingWithComps obj = ___pawn.OffHandShield();
			Apparel val = (Apparel)(object)((obj is Apparel) ? obj : null);
			if (val == null)
			{
				return;
			}
			if (!___pawn.CanUseShields())
			{
				Apparel val2 = default(Apparel);
				___pawn.apparel.TryDrop(val, ref val2, ((Thing)___pawn).PositionHeld, true);
			}
			else if (!__instance.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
			{
				if (___pawn.kindDef.destroyGearOnDrop)
				{
					((Thing)val).Destroy((DestroyMode)0);
				}
				else if (((Thing)___pawn).SpawnedOrAnyParentSpawned)
				{
					Apparel val3 = default(Apparel);
					___pawn.apparel.TryDrop(val, ref val3, ((Thing)___pawn).PositionHeld, true);
				}
				else
				{
					((Thing)val).Destroy((DestroyMode)0);
				}
			}
		}
	}
}
