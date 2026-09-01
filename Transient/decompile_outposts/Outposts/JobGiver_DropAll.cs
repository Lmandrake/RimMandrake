using Verse;
using Verse.AI;

namespace Outposts;

public class JobGiver_DropAll : ThinkNode_JobGiver
{
	public override Job TryGiveJob(Pawn pawn)
	{
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		if (pawn?.inventory == null)
		{
			return null;
		}
		pawn.inventory.UnloadEverything = true;
		pawn.inventory.DropAllNearPawn(((Thing)pawn).Position, false, true);
		return null;
	}
}
