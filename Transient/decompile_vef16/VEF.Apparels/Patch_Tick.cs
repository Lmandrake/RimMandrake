using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Skyfaller), "Tick")]
public static class Patch_Tick
{
	public static void Prefix(Skyfaller __instance)
	{
		if (((Thing)__instance).Map == null || __instance.ticksToImpact > 20)
		{
			return;
		}
		ThingDefExtension thingDefExtension = ((Def)((Thing)__instance).def).GetModExtension<ThingDefExtension>();
		if (thingDefExtension == null || thingDefExtension.shieldDamageIntercepted <= -1)
		{
			return;
		}
		ShieldGeneratorUtility.CheckIntercept((Thing)(object)__instance, ((Thing)__instance).Map, thingDefExtension.shieldDamageIntercepted, DamageDefOf.Blunt, delegate
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			CellRect val = GenAdj.OccupiedRect((Thing)(object)__instance);
			return ((CellRect)(ref val)).Cells;
		}, () => thingDefExtension.shieldDamageIntercepted > -1, delegate(CompShieldField x)
		{
			Skyfaller obj = __instance;
			DropPodIncoming val2 = (DropPodIncoming)(object)((obj is DropPodIncoming) ? obj : null);
			return val2 == null || ShieldGeneratorUtility.CheckPodHostility(x, val2);
		}, delegate(CompShieldField s)
		{
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			if (s.Energy > 0f)
			{
				Skyfaller obj2 = __instance;
				DropPodIncoming val3 = (DropPodIncoming)(object)((obj2 is DropPodIncoming) ? obj2 : null);
				if (val3 == null)
				{
					if (!(__instance is FlyShipLeaving))
					{
						((Thing)__instance).Destroy((DestroyMode)0);
					}
				}
				else
				{
					ThingOwner innerContainer = val3.Contents.innerContainer;
					for (int i = 0; i < innerContainer.Count; i++)
					{
						Thing obj3 = innerContainer[i];
						Pawn val4 = (Pawn)(object)((obj3 is Pawn) ? obj3 : null);
						if (val4 != null)
						{
							ShieldGeneratorUtility.KillPawn(val4, ((Thing)val3).Position, ((Thing)val3).Map);
						}
					}
					((Thing)val3).Destroy((DestroyMode)0);
				}
			}
		});
	}
}
