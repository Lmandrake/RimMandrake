using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Cooking;

public class CompIngestedThoughtFromQuality : ThingComp
{
	private CompProperties_IngestedThoughtFromQuality Props => (CompProperties_IngestedThoughtFromQuality)(object)base.props;

	public override void PostIngested(Pawn ingester)
	{
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Expected I4, but got Unknown
		((ThingComp)this).PostIngested(ingester);
		if (ingester.needs.mood != null)
		{
			Thought_Memory firstMemoryOfDef = ingester.needs.mood.thoughts.memories.GetFirstMemoryOfDef(Props.ingestedThought);
			int num = (int)base.parent.compQuality.Quality;
			if (firstMemoryOfDef != null)
			{
				float num2 = (float)(((Thought)firstMemoryOfDef).CurStageIndex + num) / 2f;
				firstMemoryOfDef.SetForcedStage((num > ((Thought)firstMemoryOfDef).CurStageIndex) ? Mathf.RoundToInt(num2) : Mathf.FloorToInt(num2));
				firstMemoryOfDef.Renew();
			}
			else
			{
				Thought_Memory val = ThoughtMaker.MakeThought(Props.ingestedThought, num);
				ingester.needs.mood.thoughts.memories.TryGainMemory(val, (Pawn)null);
			}
		}
	}
}
