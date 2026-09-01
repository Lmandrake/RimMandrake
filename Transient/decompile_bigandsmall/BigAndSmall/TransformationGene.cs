using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class TransformationGene
{
	public List<string> genesRequired = new List<string>();

	public int genesRequiredMinCount = 1;

	public List<string> genesForbidden = new List<string>();

	public int genesForbiddenMinCount = 1;

	public List<string> genesToAdd = new List<string>();

	public string xenotypeToAdd;

	public List<string> genesToRemove = new List<string>();

	public bool removeSelfOnTrigger = true;

	public bool TryTransform(Pawn pawn)
	{
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		if (CanTransform(pawn))
		{
			Gene val = null;
			foreach (Gene item in pawn.genes.GenesListForReading)
			{
				if (GenCollection.Any<PawnExtension>(item.def.GetAllPawnExtensionsOnGene(), (Predicate<PawnExtension>)((PawnExtension x) => x.transformGene == this)))
				{
					val = item;
					break;
				}
			}
			if (val == null)
			{
				Log.ErrorOnce($"[BigAndSmall] TransformationGene {this} tried to transform a pawn but no parent gene was found. This is likely a bug.", 0x75BCD15 ^ ((object)pawn).GetHashCode());
				return false;
			}
			if (removeSelfOnTrigger && pawn != null)
			{
				Pawn_GeneTracker genes = pawn.genes;
				if (genes != null)
				{
					genes.RemoveGene(val);
				}
			}
			bool flag = pawn.genes.Xenogenes.Contains(val);
			if (genesToRemove.Count > 0)
			{
				foreach (string geneName in genesToRemove)
				{
					object obj;
					if (pawn == null)
					{
						obj = null;
					}
					else
					{
						Pawn_GeneTracker genes2 = pawn.genes;
						obj = ((genes2 != null) ? genes2.GenesListForReading.Where((Gene x) => ((Def)x.def).defName == geneName).ToList() : null);
					}
					List<Gene> list = (List<Gene>)obj;
					if (list != null && GenCollection.Any<Gene>(list) && pawn != null)
					{
						Pawn_GeneTracker genes3 = pawn.genes;
						if (genes3 != null)
						{
							genes3.RemoveGene(list.First());
						}
					}
				}
			}
			if (xenotypeToAdd != null)
			{
				XenotypeDef named = DefDatabase<XenotypeDef>.GetNamed(xenotypeToAdd, false);
				if (named != null)
				{
					pawn.genes.xenotype = named;
					pawn.genes.xenotypeName = TaggedString.op_Implicit(((Def)named).LabelCap);
					pawn.genes.iconDef = null;
					for (int i = 0; i < named.genes.Count; i++)
					{
						pawn.genes.AddGene(named.genes[i], !named.inheritable);
					}
				}
			}
			if (genesToAdd.Count > 0)
			{
				foreach (string item2 in genesToAdd)
				{
					GeneDef named2 = DefDatabase<GeneDef>.GetNamed(item2, false);
					if (named2 != null && pawn != null)
					{
						Pawn_GeneTracker genes4 = pawn.genes;
						if (genes4 != null)
						{
							genes4.AddGene(named2, flag);
						}
					}
				}
			}
			return true;
		}
		return false;
	}

	private bool CanTransform(Pawn pawn)
	{
		IEnumerable<string> activeGeneNames = from x in pawn.GetAllActiveGenes()
			select ((Def)x.def).defName;
		if (genesRequired.Count > 0 && genesRequired.Where((string x) => activeGeneNames.Contains(x)).Count() < genesRequiredMinCount)
		{
			return false;
		}
		if (genesForbidden.Count > 0 && genesForbidden.Where((string x) => activeGeneNames.Contains(x)).Count() >= genesForbiddenMinCount)
		{
			return false;
		}
		return true;
	}
}
