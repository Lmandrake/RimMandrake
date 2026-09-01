using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class ThoughtWorker_RaidRestlessness : ThoughtWorker
{
	protected override ThoughtState CurrentStateInternal(Pawn p)
	{
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)p).Faction == Faction.OfPlayer)
		{
			StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
			if (modExtension != null && modExtension.raidRestlessness != null)
			{
				int thoughtState = modExtension.raidRestlessness.GetThoughtState();
				if (thoughtState == -1)
				{
					return ThoughtState.Inactive;
				}
				if (thoughtState > base.def.stages.Count - 1)
				{
					return ThoughtState.ActiveAtStage(base.def.stages.Count - 1);
				}
				return ThoughtState.ActiveAtStage(thoughtState);
			}
		}
		return ThoughtState.Inactive;
	}
}
