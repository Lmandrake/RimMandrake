using System;
using VEF.Hediffs;
using Verse;

namespace VEF.Weapons;

public static class VerbAccuracyUtility
{
	public static bool forceHit;

	public static bool forceMiss;

	public static void CheckAccuracyEffects(Verb verb, LocalTargetInfo target, out bool forceHit, out bool forceMiss)
	{
		forceHit = (forceMiss = false);
		Thing caster = verb.caster;
		Pawn val = (Pawn)(object)((caster is Pawn) ? caster : null);
		if (val != null && val.health?.hediffSet?.hediffs != null)
		{
			foreach (Hediff hediff in val.health.hediffSet.hediffs)
			{
				HediffComp_Targeting hediffComp_Targeting = HediffUtility.TryGetComp<HediffComp_Targeting>(hediff);
				if (hediffComp_Targeting != null)
				{
					forceHit = hediffComp_Targeting.Props.neverMiss;
					forceMiss = hediffComp_Targeting.Props.neverHit;
				}
			}
		}
		Thing thing = ((LocalTargetInfo)(ref target)).Thing;
		Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val2 != null && val2.health?.hediffSet?.hediffs != null)
		{
			foreach (Hediff hediff2 in val2.health.hediffSet.hediffs)
			{
				HediffComp_Targeting hediffComp_Targeting2 = HediffUtility.TryGetComp<HediffComp_Targeting>(hediff2);
				if (hediffComp_Targeting2 != null)
				{
					forceHit = hediffComp_Targeting2.Props.alwaysHit;
					forceMiss = hediffComp_Targeting2.Props.alwaysMiss;
				}
			}
		}
		Type type = VerbUtility.GetProjectile(verb)?.thingClass;
		if (type != null && typeof(TeslaProjectile).IsAssignableFrom(type))
		{
			forceHit = true;
		}
	}
}
