using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompTargetEffect_CreateXenogerm : CompTargetEffect
{
	public CompProperties_XenogermCreator Props => (CompProperties_XenogermCreator)(object)((ThingComp)this).props;

	public override void DoEffectOn(Pawn _, Thing target)
	{
		Pawn val = (Pawn)(object)((target is Pawn) ? target : null);
		if (val != null)
		{
			CreateXenogerm(val, Props.archite, Props.endogenes, Props.xenogenes, Props.inactivegenes);
		}
	}

	public static void CreateXenogerm(Pawn pawn, bool archite, bool endoGenes, bool xenoGenes, bool inactive)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Expected O, but got Unknown
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		Xenogerm val = (Xenogerm)ThingMaker.MakeThing(ThingDefOf.Xenogerm, (ThingDef)null);
		val.Initialize(new List<Genepack>(), pawn.genes.xenotypeName, pawn.genes.iconDef);
		List<Gene> source = new List<Gene>();
		List<Gene> collection = pawn.genes.Endogenes.ToList();
		List<Gene> collection2 = pawn.genes.Xenogenes.ToList();
		source = source.Where((Gene x) => pawn.genes.Xenogenes.Contains(x) || pawn.genes.Endogenes.Contains(x)).ToList();
		if (endoGenes)
		{
			source.AddRange(collection);
		}
		if (xenoGenes)
		{
			source.AddRange(collection2);
		}
		if (!inactive)
		{
			source = source.Where((Gene x) => x.Active).ToList();
		}
		if (!archite)
		{
			source = source.Where((Gene x) => x.def.biostatArc == 0).ToList();
		}
		foreach (Gene item in source)
		{
			((GeneSetHolderBase)val).GeneSet.AddGene(item.def);
		}
		try
		{
			((GeneSetHolderBase)val).GeneSet.SetNameDirect(pawn.genes.xenotypeName);
		}
		catch
		{
		}
		GenPlace.TryPlaceThing((Thing)(object)val, ((Thing)pawn).Position, ((Thing)pawn).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
	}
}
