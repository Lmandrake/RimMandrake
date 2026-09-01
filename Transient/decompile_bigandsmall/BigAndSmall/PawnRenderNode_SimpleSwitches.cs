using Verse;

namespace BigAndSmall;

public class PawnRenderNode_SimpleSwitches : PawnRenderNode
{
	private readonly string noImage = "BS_Blank";

	private PawnRenderNode_SimpleSwitchesProps ComplexProps => (PawnRenderNode_SimpleSwitchesProps)(object)base.props;

	public PawnRenderNode_SimpleSwitches(Pawn pawn, PawnRenderNode_SimpleSwitchesProps props, PawnRenderTree tree)
		: base(pawn, (PawnRenderNodeProperties)(object)props, tree)
	{
	}

	public override string TexPathFor(Pawn pawn)
	{
		if (ComplexProps.ShouldDisable(pawn))
		{
			return noImage;
		}
		return ((PawnRenderNode)this).TexPathFor(pawn);
	}
}
