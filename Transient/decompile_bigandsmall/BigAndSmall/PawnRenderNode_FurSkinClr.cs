using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNode_FurSkinClr : PawnRenderNode_Fur
{
	public PawnRenderNode_FurSkinClr(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
	}

	public override Color ColorFor(Pawn pawn)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		return pawn.story.SkinColor;
	}
}
