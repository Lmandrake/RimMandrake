using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(FleshTypeDef), "ChooseWoundOverlay")]
public static class VanillaExpandedFramework__FleshTypeDef_ChooseWoundOverlay_Patch
{
	public static void Postfix(Hediff hediff, ref ResolvedWound __result)
	{
		if (StaticCollectionsClass.woundsFromFleshtype_gene_pawns.ContainsKey((Thing)(object)hediff.pawn))
		{
			ResolvedWound val = ChooseWoundOverlay(StaticCollectionsClass.woundsFromFleshtype_gene_pawns[(Thing)(object)hediff.pawn], hediff);
			if (val != null)
			{
				__result = val;
			}
		}
	}

	public static ResolvedWound ChooseWoundOverlay(FleshTypeDef def, Hediff hediff)
	{
		if (def.genericWounds == null)
		{
			return null;
		}
		if (def.hediffWounds != null)
		{
			foreach (HediffWound hediffWound in def.hediffWounds)
			{
				if (hediffWound.hediff != hediff.def)
				{
					continue;
				}
				ResolvedWound val = hediffWound.ChooseWoundOverlay(hediff);
				if (val != null)
				{
					if (HediffUtility.IsTended(hediff))
					{
						return def.ChooseBandagedOverlay();
					}
					return val;
				}
			}
		}
		Hediff_MissingPart val2;
		if (hediff is Hediff_Injury || ((val2 = (Hediff_MissingPart)(object)((hediff is Hediff_MissingPart) ? hediff : null)) != null && val2.IsFresh))
		{
			if (HediffUtility.IsTended(hediff))
			{
				return def.ChooseBandagedOverlay();
			}
			if (ReflectionCache.woundsResolved.Invoke(def) == null)
			{
				ReflectionCache.woundsResolved.Invoke(def) = def.genericWounds.Select((Wound wound) => wound.Resolve()).ToList();
			}
			return GenCollection.RandomElement<ResolvedWound>((IEnumerable<ResolvedWound>)ReflectionCache.woundsResolved.Invoke(def));
		}
		return null;
	}
}
