using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class CompProperticesMimicOffEffect : CompAbilityEffect
{
	public CompPropertiesMimicOff Props => (CompPropertiesMimicOff)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		EndMimicry(((AbilityComp)this).parent.pawn, Props.genesToRetain, Props.spawnFilth);
	}

	public static void EndMimicry(Pawn pawn, List<GeneDef> genesToRetain, bool spawnFilith = false)
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0197: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		if (spawnFilith)
		{
			Gibblets.SpawnGibblets(pawn, ((Thing)pawn).Position, ((Thing)pawn).Map, 10, 20, 1, 3, 1f, 0f);
		}
		BodyTypeDef bodyType = pawn.story.bodyType;
		if (pawn != null)
		{
			Pawn_GeneTracker genes = pawn.genes;
			if (genes != null)
			{
				genes.GenesListForReading?.FirstOrDefault();
			}
		}
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Pawn_GeneTracker genes2 = pawn.genes;
			obj = ((genes2 == null) ? null : genes2.Xenogenes?.Where((Gene gene) => !genesToRetain.Contains(gene.def)).ToList());
		}
		List<Gene> list = (List<Gene>)obj;
		if (list != null)
		{
			foreach (Gene item in list)
			{
				if (pawn != null)
				{
					Pawn_GeneTracker genes3 = pawn.genes;
					if (genes3 != null)
					{
						genes3.RemoveGene(item);
					}
				}
			}
		}
		HashSet<Gene> allActiveGenes = pawn.GetAllActiveGenes();
		IEnumerable<Color?> source = from gene in allActiveGenes
			where gene.def.skinColorBase.HasValue
			select gene into x
			select x.def.skinColorBase;
		IEnumerable<Color?> source2 = from gene in allActiveGenes
			where gene.def.skinColorOverride.HasValue
			select gene into x
			select x.def.skinColorOverride;
		if (source2.Any())
		{
			pawn.story.skinColorOverride = source2.First().Value;
		}
		else if (source.Any())
		{
			pawn.story.skinColorOverride = null;
			pawn.story.SkinColorBase = source.First().Value;
		}
		pawn.story.bodyType = bodyType;
		foreach (Gene item2 in list)
		{
			pawn.genes.Notify_GenesChanged(item2.def);
		}
		HumanoidPawnScaler.GetCache(pawn, forceRefresh: true);
	}
}
