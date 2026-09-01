using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class HealthHelpers
{
	public static List<Hediff_Injury> GetAllInjuries(Pawn pawn)
	{
		List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
		if (hediffs == null || hediffs.Count == 0)
		{
			return new List<Hediff_Injury>();
		}
		return (from x in hediffs.OfType<Hediff_Injury>()
			where ((Hediff)x).def.isBad && ((Hediff)x).Visible && ((Hediff)x).def.everCurableByItem
			select x).ToList();
	}

	public static Hediff_Injury GetRandomScar(Pawn pawn)
	{
		List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
		if (hediffs == null || hediffs.Count == 0)
		{
			return null;
		}
		List<Hediff_Injury> list = (from x in hediffs.OfType<Hediff_Injury>()
			where ((Hediff)x).def.isBad && ((Hediff)x).Visible && HediffUtility.IsPermanent((Hediff)(object)x) && ((Hediff)x).def.everCurableByItem
			select x).ToList();
		if (list.Count == 0)
		{
			return null;
		}
		return GenCollection.RandomElement<Hediff_Injury>((IEnumerable<Hediff_Injury>)list);
	}

	public static Hediff_MissingPart GetMissingPart(Pawn pawn)
	{
		List<Hediff_MissingPart> missingPartsCommonAncestors = pawn.health.hediffSet.GetMissingPartsCommonAncestors();
		if (missingPartsCommonAncestors == null || missingPartsCommonAncestors.Count == 0)
		{
			return null;
		}
		missingPartsCommonAncestors = missingPartsCommonAncestors.Where((Hediff_MissingPart missingPart) => !pawn.health.hediffSet.PartOrAnyAncestorHasDirectlyAddedParts(((Hediff)missingPart).Part)).ToList();
		if (missingPartsCommonAncestors.Count == 0)
		{
			return null;
		}
		return missingPartsCommonAncestors.OrderByDescending((Hediff_MissingPart missingPart) => ((Hediff)missingPart).Part.coverageAbsWithChildren).FirstOrDefault();
	}

	public static void CureWorstInjury(Pawn pawn)
	{
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ad: Unknown result type (might be due to invalid IL or missing references)
		Hediff_Injury val = null;
		List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
		for (int i = 0; i < hediffs.Count; i++)
		{
			Hediff obj = hediffs[i];
			Hediff_Injury val2 = (Hediff_Injury)(object)((obj is Hediff_Injury) ? obj : null);
			if (val2 != null && ((Hediff)val2).def?.isBad == true && ((Hediff)val2).Visible && HediffUtility.IsPermanent((Hediff)(object)val2) && ((Hediff)val2).def.everCurableByItem && (val == null || ((Hediff)val2).Severity > ((Hediff)val).Severity))
			{
				val = val2;
			}
		}
		if (val != null)
		{
			HealthUtility.Cure((Hediff)(object)val);
			return;
		}
		BodyPartRecord val3 = null;
		float coverageAbsWithChildren = ThingDefOf.Human.race.body.GetPartsWithDef(BodyPartDefOf.Hand).First().coverageAbsWithChildren;
		foreach (Hediff_MissingPart missingPartsCommonAncestor in pawn.health.hediffSet.GetMissingPartsCommonAncestors())
		{
			if (!(((Hediff)missingPartsCommonAncestor).Part.coverageAbsWithChildren < coverageAbsWithChildren) && !pawn.health.hediffSet.PartOrAnyAncestorHasDirectlyAddedParts(((Hediff)missingPartsCommonAncestor).Part) && (val3 == null || ((Hediff)missingPartsCommonAncestor).Part.coverageAbsWithChildren > val3.coverageAbsWithChildren))
			{
				val3 = ((Hediff)missingPartsCommonAncestor).Part;
			}
		}
		if (val3 != null)
		{
			pawn.health.RestorePart(val3, (Hediff)null, true);
		}
		else if (val3 == null)
		{
			IEnumerable<Hediff> enumerable = pawn.health.hediffSet.hediffs.Where((Hediff x) => x != null && x.def?.isBad == true && x.def.everCurableByItem);
			if (enumerable.Any())
			{
				HealthUtility.Cure(GenCollection.RandomElement<Hediff>(enumerable));
			}
		}
	}
}
