using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class AlienApperanceUtils
{
	public enum AlienState
	{
		VeryAlien,
		LittleAlien,
		Neutral
	}

	public static bool GeneIsSimilar(GeneDef geneA, GeneDef geneB)
	{
		if (geneA == geneB)
		{
			return true;
		}
		foreach (List<GeneDef> alienGeneGroup in GlobalSettings.GetAlienGeneGroups())
		{
			if (alienGeneGroup.Contains(geneA) && alienGeneGroup.Contains(geneB))
			{
				return true;
			}
		}
		return false;
	}

	public static ThoughtState GetAlienApperanceThoughtState(List<GeneDef> targetGenes, AlienState targetApperance, List<GeneDef> observerGenes, AlienState observerApperance, int offset = 0)
	{
		//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_013a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0150: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Unknown result type (might be due to invalid IL or missing references)
		//IL_0198: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		bool flag = false;
		bool flag2 = false;
		int sharedRomanceChanceGenes = 0;
		int unsharedRomanceChanceGenes = 0;
		if (observerApperance != AlienState.Neutral && targetApperance != observerApperance)
		{
			flag = true;
			flag2 = true;
		}
		else if (targetApperance == observerApperance)
		{
			flag = true;
		}
		observerGenes.Where((GeneDef x) => x != BSDefs.BS_AlienApperanceStandards && x != BSDefs.BS_AlienApperanceStandards_Lesser && x.missingGeneRomanceChanceFactor < 1f).ToList().ForEach(delegate(GeneDef x)
		{
			if (!GenCollection.Any<GeneDef>(targetGenes, (Predicate<GeneDef>)((GeneDef y) => GeneIsSimilar(x, y))))
			{
				unsharedRomanceChanceGenes++;
			}
			else
			{
				sharedRomanceChanceGenes++;
			}
		});
		targetGenes.Where((GeneDef x) => x != BSDefs.BS_AlienApperanceStandards && x != BSDefs.BS_AlienApperanceStandards_Lesser && x.missingGeneRomanceChanceFactor < 1f).ToList().ForEach(delegate(GeneDef x)
		{
			if (!GenCollection.Any<GeneDef>(observerGenes, (Predicate<GeneDef>)((GeneDef y) => GeneIsSimilar(x, y))))
			{
				unsharedRomanceChanceGenes++;
			}
		});
		float num = 0f;
		if (sharedRomanceChanceGenes != 0)
		{
			num = (float)sharedRomanceChanceGenes / (float)(sharedRomanceChanceGenes + unsharedRomanceChanceGenes);
			num -= (flag2 ? 0.25f : 0f);
		}
		else if (flag)
		{
			if (flag2 && unsharedRomanceChanceGenes == 0 && sharedRomanceChanceGenes == 0)
			{
				num = 0.26f;
			}
			else if (unsharedRomanceChanceGenes == 0)
			{
				num = 1f;
			}
		}
		if (flag)
		{
			float num2 = num;
			return ((double)num2 > 0.9) ? ThoughtState.ActiveAtStage(offset) : (((double)num2 > 0.44) ? ThoughtState.ActiveAtStage(1 + offset) : (((double)num2 > 0.24) ? ThoughtState.ActiveAtStage(3 + offset) : ((!((double)num2 > 0.0)) ? ThoughtState.ActiveAtStage(5 + offset) : ThoughtState.ActiveAtStage(4 + offset))));
		}
		float num3 = num;
		return ((double)num3 > 0.44) ? ThoughtState.ActiveAtStage(2 + offset) : ((!((double)num3 > 0.19)) ? ThoughtState.ActiveAtStage(5 + offset) : ThoughtState.ActiveAtStage(4 + offset));
	}
}
