using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNode_Ultimate : PawnRenderNode, IUltimateRendering
{
	protected readonly bool useHeadMesh;

	public virtual bool AllowTexPathFor => false;

	public PawnRenderNode Base => (PawnRenderNode)(object)this;

	public bool ScaleSet { get; set; }

	public Vector2 CachedScale { get; set; } = Vector2.one;

	public ShaderTypeDef ShaderOverride { get; set; }

	private PawnRenderingProps_Ultimate UProps => (PawnRenderingProps_Ultimate)(object)base.props;

	public PawnRenderNode_Ultimate(Pawn pawn, PawnRenderingProps_Ultimate props, PawnRenderTree tree)
		: base(pawn, (PawnRenderNodeProperties)(object)props, tree)
	{
	}//IL_0001: Unknown result type (might be due to invalid IL or missing references)
	//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	public PawnRenderNode_Ultimate(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree, Apparel apparel)
		: base(pawn, props, tree)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		base.apparel = apparel;
		useHeadMesh = props.parentTagDef == PawnRenderNodeTagDefOf.ApparelHead;
		base.meshSet = ((PawnRenderNode)this).MeshSetFor(pawn);
	}

	public PawnRenderNode_Ultimate(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree, Apparel apparel, bool useHeadMesh)
		: base(pawn, props, tree)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		base.apparel = apparel;
		this.useHeadMesh = useHeadMesh;
		base.meshSet = ((PawnRenderNode)this).MeshSetFor(pawn);
	}

	public override string TexPathFor(Pawn pawn)
	{
		if (!AllowTexPathFor)
		{
			throw new NotImplementedException("TexPath is not meant to be used with this RenderNode." + string.Format("Use {0} ({1}) instead.", "GraphicSet", typeof(ConditionalGraphicsSet)));
		}
		return ((PawnRenderNode)this).TexPathFor(pawn);
	}

	public override Graphic GraphicFor(Pawn pawn)
	{
		return PRN_Ultimate.GraphicFor(pawn, this, UProps);
	}

	public override Mesh GetMesh(PawnDrawParms parms)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		if (((Rot4)(ref parms.facing)).IsHorizontal && UProps.invertEastWest)
		{
			parms.facing = ((Rot4)(ref parms.facing)).Opposite;
		}
		return ((PawnRenderNode)this).GetMesh(parms);
	}

	public override GraphicMeshSet MeshSetFor(Pawn pawn)
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		if (base.apparel == null)
		{
			return ((PawnRenderNode)this).MeshSetFor(pawn);
		}
		if (((PawnRenderNode)this).Props.overrideMeshSize.HasValue)
		{
			return MeshPool.GetMeshSetForSize(((PawnRenderNode)this).Props.overrideMeshSize.Value.x, ((PawnRenderNode)this).Props.overrideMeshSize.Value.y);
		}
		if (useHeadMesh || UProps.useHeadMesh)
		{
			return HumanlikeMeshPoolUtility.GetHumanlikeHeadSetForPawn(pawn, 1f, 1f);
		}
		return HumanlikeMeshPoolUtility.GetHumanlikeBodySetForPawn(pawn, 1f, 1f);
	}
}
