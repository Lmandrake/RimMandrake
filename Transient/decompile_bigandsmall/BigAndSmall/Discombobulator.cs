using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class Discombobulator
{
	public static void Discombobulate(Pawn pawn, bool addComa = true)
	{
		List<Gene> list = pawn.genes.Xenogenes.ToList();
		List<string> invalidTags = new List<string> { "VU_", "BS_Corrupted", "BS_Damaged_Genes", "BS_Xenolocked", "Titan" };
		List<string> exclusionTags = new List<string> { "BS_Pilotable" };
		List<GeneDef> validGenes = GetValidGenes(pawn, invalidTags, exclusionTags);
		int count = list.Count;
		count = ((count < 3) ? 3 : count);
		int num = GeneHelpers.GetAllActiveEndoGenes(pawn).Sum((Gene x) => x.def.biostatMet);
		count = ((num < 0) ? (count + Rand.Range(-2, 5)) : (count + Rand.Range(0, 5)));
		HashSet<GeneDef> hashSet = new HashSet<GeneDef>();
		for (int i = 0; i < count; i++)
		{
			GeneDef item = GenCollection.RandomElementByWeight<GeneDef>((IEnumerable<GeneDef>)validGenes, (Func<GeneDef, float>)((GeneDef x) => x.selectionWeight));
			hashSet.Add(item);
		}
		if (!hashSet.Any((GeneDef x) => ((Def)x).defName.Contains("Frame")) && Rand.Chance(0.4f))
		{
			IEnumerable<GeneDef> enumerable = validGenes.Where((GeneDef x) => ((Def)x).defName.Contains("Frame"));
			GeneDef val = ((enumerable != null) ? GenCollection.RandomElement<GeneDef>(enumerable) : null);
			if (val != null)
			{
				hashSet.Add(val);
			}
		}
		GeneHelpers.RemoveRandomToMetabolism(num, hashSet.ToList());
		foreach (Gene item2 in list)
		{
			pawn.genes.RemoveGene(item2);
		}
		foreach (GeneDef item3 in hashSet)
		{
			pawn.genes.AddGene(item3, true);
		}
		if (addComa)
		{
			Hediff val2 = HediffMaker.MakeHediff(HediffDefOf.XenogerminationComa, pawn, (BodyPartRecord)null);
			pawn.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}

	private static List<GeneDef> GetValidGenes(Pawn pawn, List<string> invalidTags, List<string> exclusionTags)
	{
		return (from x in (from x in (from x in (from x in DefDatabase<GeneDef>.AllDefsListForReading.Where((GeneDef x) => !GenCollection.Any<string>(invalidTags, (Predicate<string>)((string y) => ((Def)x).defName.StartsWith(y)))).ToList()
						where !GenCollection.Any<string>(exclusionTags, (Predicate<string>)((string y) => x.exclusionTags?.Contains(y) ?? false))
						select x).ToList()
					where x.canGenerateInGeneSet
					select x).ToList()
				where !((Def)x).defName.ToLower().Contains("eye")
				select x).ToList()
			where x.prerequisite == null || pawn.genes.GenesListForReading.Select((Gene y) => y.def).Contains(x.prerequisite)
			select x).ToList();
	}

	public static void IntegrateGenes(Pawn pawn, bool removeOverriden = true)
	{
		List<Gene> list = pawn.genes.Xenogenes.ToList();
		list.RemoveAll((Gene x) => AccessTools.Property(((object)x).GetType(), "IsMutation") != null || AccessTools.Property(((object)x).GetType(), "IsEvolution") != null);
		if (removeOverriden)
		{
			foreach (Gene allInactiveGene in GeneHelpers.GetAllInactiveGenes(pawn))
			{
				pawn.genes.RemoveGene(allInactiveGene);
			}
		}
		foreach (Gene item in list)
		{
			pawn.genes.RemoveGene(item);
		}
		foreach (Gene item2 in list)
		{
			pawn.genes.AddGene(item2.def, false);
		}
	}

	public static void XenoCopy(Pawn pawn)
	{
		foreach (Gene gene in (from x in pawn.genes.Endogenes.ToList()
			where Rand.Chance(0.66f) && x.Active
			select x).ToList())
		{
			if (!GenCollection.Any<Gene>(pawn.genes.Xenogenes, (Predicate<Gene>)((Gene x) => ((Def)x.def).defName == ((Def)gene.def).defName)))
			{
				pawn.genes.AddGene(gene.def, true);
			}
		}
	}
}
