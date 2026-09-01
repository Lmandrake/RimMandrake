using Verse;

namespace BigAndSmall;

public class PawnRenderNodeWorker_HAnimalPack : PawnRenderNodeWorker
{
	public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		if (node is PawnRenderNode_HAnimalPack { isPackAnimal: false })
		{
			return false;
		}
		if (((PawnRenderNodeWorker)this).CanDrawNow(node, parms) && !((PawnDrawParms)(ref parms)).Portrait && parms.pawn.inventory != null)
		{
			return ((ThingOwner)parms.pawn.inventory.innerContainer).Count > 0;
		}
		return false;
	}
}
