using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class PawnRenderNode_Omni : PawnRenderNode
{
	private bool useHeadMesh;

	private PawnRenderNodeProperties_Omni OProps => base.props as PawnRenderNodeProperties_Omni;

	public PawnRenderNode_Omni(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
	}

	public PawnRenderNode_Omni(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree, Apparel apparel)
		: base(pawn, props, tree)
	{
		base.apparel = apparel;
		useHeadMesh = props.parentTagDef == PawnRenderNodeTagDefOf.ApparelHead;
		base.meshSet = ((PawnRenderNode)this).MeshSetFor(pawn);
	}

	public PawnRenderNode_Omni(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree, Apparel apparel, bool useHeadMesh)
		: base(pawn, props, tree)
	{
		base.apparel = apparel;
		this.useHeadMesh = useHeadMesh;
		base.meshSet = ((PawnRenderNode)this).MeshSetFor(pawn);
	}

	protected override string TexPathFor(Pawn pawn)
	{
		throw new NotImplementedException("TexPath is not meant to be used with the PawnRenderNode_Omni RenderNode.");
	}

	public override Graphic GraphicFor(Pawn pawn)
	{
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		ConditionalGraphicSet activeGraphicsSet = OProps.conditionalGraphics.GetActiveGraphicsSet(pawn, (PawnRenderNode)(object)this);
		if (activeGraphicsSet == null)
		{
			Log.Warning($"No active set of graphics found for {pawn} in {this}");
			return null;
		}
		string text = activeGraphicsSet.TexPathFor(pawn, (PawnRenderNode)(object)this);
		string text2 = activeGraphicsSet.MaskPathFor(pawn, (PawnRenderNode)(object)this);
		Shader val = activeGraphicsSet.ShaderFor(pawn);
		if (val == null)
		{
			val = ShaderTypeDefOf.CutoutComplex.Shader;
		}
		Color colorA = activeGraphicsSet.GetColorA((PawnRenderNode)(object)this, Color.white);
		Color colorB = activeGraphicsSet.GetColorB((PawnRenderNode)(object)this, Color.white);
		if (!GenText.NullOrEmpty(text))
		{
			TaggedText stringByTag = ((ILoadReferenceable)(object)pawn).GetStringByTag(text);
			if (stringByTag != null)
			{
				text = stringByTag.value;
			}
		}
		if (!GenText.NullOrEmpty(text2))
		{
			TaggedText stringByTag2 = ((ILoadReferenceable)(object)pawn).GetStringByTag(text2);
			if (stringByTag2 != null)
			{
				text2 = stringByTag2.value;
			}
		}
		if (OProps.autoBodyTypeMasks)
		{
			if (text2 == null)
			{
				text2 = text;
			}
			text2 = GetBodyTypedPath(pawn.story.bodyType, text2);
		}
		if (OProps.autoBodyTypePaths)
		{
			text = GetBodyTypedPath(pawn.story.bodyType, text);
		}
		return GraphicDatabase.Get<Graphic_Multi>(text, val, Vector2.one, colorA, colorB, (GraphicData)null, text2);
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
		if (useHeadMesh)
		{
			return HumanlikeMeshPoolUtility.GetHumanlikeHeadSetForPawn(pawn, 1f, 1f);
		}
		return HumanlikeMeshPoolUtility.GetHumanlikeBodySetForPawn(pawn, 1f, 1f);
	}

	public string GetBodyTypedPath(BodyTypeDef bodyType, string basePath)
	{
		if (bodyType == null)
		{
			Log.Error("Attempted to get graphic with undefined body type.");
			bodyType = BodyTypeDefOf.Male;
		}
		if (GenText.NullOrEmpty(basePath))
		{
			return basePath;
		}
		return basePath + "_" + ((Def)bodyType).defName;
	}
}
