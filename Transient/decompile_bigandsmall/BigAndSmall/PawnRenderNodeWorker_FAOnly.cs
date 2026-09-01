using Verse;

namespace BigAndSmall;

public class PawnRenderNodeWorker_FAOnly : PawnRenderNodeWorker_FlipWhenCrawling
{
	protected bool initialized;

	protected bool shouldDraw;

	public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		if (!initialized)
		{
			shouldDraw = NalsToggles.FALoaded;
			BSCache cache = HumanoidPawnScaler.GetCache(node.tree.pawn);
			if (cache != null && cache.facialAnimationDisabled)
			{
				shouldDraw = false;
			}
		}
		if (shouldDraw)
		{
			return ((PawnRenderNodeWorker)this).CanDrawNow(node, parms);
		}
		return false;
	}
}
