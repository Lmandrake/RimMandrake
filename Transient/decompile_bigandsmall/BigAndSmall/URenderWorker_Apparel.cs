using UnityEngine;
using Verse;

namespace BigAndSmall;

public class URenderWorker_Apparel : PawnRenderNodeWorker_Body
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
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		Vector3 result = ((PawnRenderNodeWorker)this).OffsetFor(n, parms, ref pivot);
		IUltimateRendering ultimateRendering = (IUltimateRendering)n;
		if (((Thing)ultimateRendering.Base.apparel).def.apparel.wornGraphicData != null && PawnRenderUtility.RenderAsPack(ultimateRendering.Base.apparel))
		{
			Vector2 val = ((Thing)ultimateRendering.Base.apparel).def.apparel.wornGraphicData.BeltOffsetAt(parms.facing, parms.pawn.story.bodyType);
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
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		Vector3 result = ((PawnRenderNodeWorker)this).ScaleFor(n, parms);
		IUltimateRendering ultimateRendering = (IUltimateRendering)n;
		if (((Thing)ultimateRendering.Base.apparel).def.apparel.wornGraphicData != null && PawnRenderUtility.RenderAsPack(ultimateRendering.Base.apparel))
		{
			Vector2 val = ((Thing)ultimateRendering.Base.apparel).def.apparel.wornGraphicData.BeltScaleAt(parms.facing, parms.pawn.story.bodyType);
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
