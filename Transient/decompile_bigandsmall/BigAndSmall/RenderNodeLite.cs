using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class RenderNodeLite : PawnRenderNode_Ultimate
{
	private PawnRenderingProps_Lite LProps => (PawnRenderingProps_Lite)(object)((PawnRenderNode)this).props;

	public override bool AllowTexPathFor => true;

	public RenderNodeLite(Pawn pawn, PawnRenderingProps_Lite props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
		LProps.TrySetup();
	}

	public RenderNodeLite(Pawn pawn, PawnRenderingProps_Lite props, PawnRenderTree tree, Apparel apparel)
		: base(pawn, (PawnRenderNodeProperties)(object)props, tree, apparel)
	{
		LProps.TrySetup();
	}

	public RenderNodeLite(Pawn pawn, PawnRenderingProps_Lite props, PawnRenderTree tree, Apparel apparel, bool useHeadMesh)
		: base(pawn, props, tree)
	{
		LProps.TrySetup();
	}

	public override Mesh GetMesh(PawnDrawParms parms)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		if (((Rot4)(ref parms.facing)).IsHorizontal && LProps.invertEastWest)
		{
			parms.facing = ((Rot4)(ref parms.facing)).Opposite;
		}
		return base.GetMesh(parms);
	}

	public override GraphicMeshSet MeshSetFor(Pawn pawn)
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		if (((PawnRenderNode)this).apparel == null)
		{
			return base.MeshSetFor(pawn);
		}
		if (((PawnRenderNode)this).Props.overrideMeshSize.HasValue)
		{
			return MeshPool.GetMeshSetForSize(((PawnRenderNode)this).Props.overrideMeshSize.Value.x, ((PawnRenderNode)this).Props.overrideMeshSize.Value.y);
		}
		if (useHeadMesh)
		{
			return HumanlikeMeshPoolUtility.GetHumanlikeHeadSetForPawn(pawn, 1f, 1f);
		}
		return HumanlikeMeshPoolUtility.GetHumanlikeBodySetForPawn(pawn, 1f, 1f);
	}
}
