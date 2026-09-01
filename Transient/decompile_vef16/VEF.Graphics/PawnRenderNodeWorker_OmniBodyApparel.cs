using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class PawnRenderNodeWorker_OmniBodyApparel : PawnRenderNodeWorker_Body
{
	public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		if (!((PawnRenderNodeWorker_Body)this).CanDrawNow(node, parms))
		{
			return false;
		}
		if (!PawnRenderFlagsExtension.FlagSet(parms.flags, (PawnRenderFlags)64))
		{
			return false;
		}
		return true;
	}

	public override Vector3 OffsetFor(PawnRenderNode n, PawnDrawParms parms, out Vector3 pivot)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		Vector3 result = ((PawnRenderNodeWorker)this).OffsetFor(n, parms, ref pivot);
		PawnRenderNode_Omni pawnRenderNode_Omni = (PawnRenderNode_Omni)(object)n;
		if (((Thing)((PawnRenderNode)pawnRenderNode_Omni).apparel).def.apparel.wornGraphicData != null && PawnRenderUtility.RenderAsPack(((PawnRenderNode)pawnRenderNode_Omni).apparel))
		{
			Vector2 val = ((Thing)((PawnRenderNode)pawnRenderNode_Omni).apparel).def.apparel.wornGraphicData.BeltOffsetAt(parms.facing, parms.pawn.story.bodyType);
			result.x += val.x;
			result.z += val.y;
		}
		return result;
	}

	public override Vector3 ScaleFor(PawnRenderNode n, PawnDrawParms parms)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		Vector3 result = ((PawnRenderNodeWorker)this).ScaleFor(n, parms);
		PawnRenderNode_Omni pawnRenderNode_Omni = (PawnRenderNode_Omni)(object)n;
		if (((Thing)((PawnRenderNode)pawnRenderNode_Omni).apparel).def.apparel.wornGraphicData != null && PawnRenderUtility.RenderAsPack(((PawnRenderNode)pawnRenderNode_Omni).apparel))
		{
			Vector2 val = ((Thing)((PawnRenderNode)pawnRenderNode_Omni).apparel).def.apparel.wornGraphicData.BeltScaleAt(parms.facing, parms.pawn.story.bodyType);
			result.x *= val.x;
			result.z *= val.y;
		}
		return result;
	}

	public override float LayerFor(PawnRenderNode n, PawnDrawParms parms)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		if (parms.flipHead && n.Props.oppositeFacingLayerWhenFlipped)
		{
			PawnDrawParms val = parms;
			val.facing = ((Rot4)(ref parms.facing)).Opposite;
			val.flipHead = false;
			return ((PawnRenderNodeWorker)this).LayerFor(n, val);
		}
		return ((PawnRenderNodeWorker)this).LayerFor(n, parms);
	}
}
