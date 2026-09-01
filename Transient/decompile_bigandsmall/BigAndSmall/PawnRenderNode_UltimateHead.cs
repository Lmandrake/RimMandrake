using Verse;

namespace BigAndSmall;

public class PawnRenderNode_UltimateHead : PawnRenderNode_Ultimate
{
	public PawnRenderNode_UltimateHead(Pawn pawn, PawnRenderingProps_Ultimate props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
	}

	public override GraphicMeshSet MeshSetFor(Pawn pawn)
	{
		return HumanlikeMeshPoolUtility.GetHumanlikeHairSetForPawn(pawn, 1f, 1f);
	}
}
