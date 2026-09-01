using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Hediffs;

[HarmonyPatch(typeof(Pawn_InteractionsTracker), "TryInteractWith")]
public static class VanillaExpandedFramework_Pawn_InteractionsTracker_TryInteractWith_Patch
{
	private static Dictionary<Hediff, HediffComp_Spreadable> cachedComps = new Dictionary<Hediff, HediffComp_Spreadable>();

	private static bool TryGetCachedSpreadableComp(this Hediff hediff, out HediffComp_Spreadable comp)
	{
		if (!cachedComps.TryGetValue(hediff, out comp))
		{
			cachedComps[hediff] = (comp = HediffUtility.TryGetComp<HediffComp_Spreadable>(hediff));
		}
		return comp != null;
	}

	public static void Postfix(bool __result, Pawn ___pawn, Pawn recipient)
	{
		if (!__result)
		{
			return;
		}
		if (___pawn.health?.hediffSet?.hediffs != null)
		{
			foreach (Hediff hediff in ___pawn.health.hediffSet.hediffs)
			{
				if (hediff.TryGetCachedSpreadableComp(out var comp) && Rand.Chance(comp.Props.socialInteractionTransmissionChance))
				{
					comp.TrySpreadDiseaseOn(recipient);
				}
			}
		}
		if (recipient.health?.hediffSet?.hediffs == null)
		{
			return;
		}
		foreach (Hediff hediff2 in recipient.health.hediffSet.hediffs)
		{
			if (hediff2.TryGetCachedSpreadableComp(out var comp2) && Rand.Chance(comp2.Props.socialInteractionTransmissionChance))
			{
				comp2.TrySpreadDiseaseOn(___pawn);
			}
		}
	}
}
