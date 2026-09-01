using UnityEngine;
using Verse;

namespace BigAndSmall;

public class UltimateRenderNodeWorker : PawnRenderNodeWorker
{
	public override Vector3 ScaleFor(PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		Vector3 result = ((PawnRenderNodeWorker)this).ScaleFor(node, parms);
		if (node is PawnRenderNode_Ultimate { ScaleSet: not false } pawnRenderNode_Ultimate)
		{
			result.x *= pawnRenderNode_Ultimate.CachedScale.x;
			result.z *= pawnRenderNode_Ultimate.CachedScale.y;
		}
		return result;
	}

	public override Vector3 OffsetFor(PawnRenderNode node, PawnDrawParms parms, out Vector3 pivot)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		Vector3 result = ((PawnRenderNodeWorker)this).OffsetFor(node, parms, ref pivot);
		if (parms.pawn.story.headType.narrow && node.Props.narrowCrownHorizontalOffset != 0f && ((Rot4)(ref parms.facing)).IsHorizontal)
		{
			if (parms.facing == Rot4.East)
			{
				result.x -= node.Props.narrowCrownHorizontalOffset;
			}
			else if (parms.facing == Rot4.West)
			{
				result.x += node.Props.narrowCrownHorizontalOffset;
			}
			result.z -= node.Props.narrowCrownHorizontalOffset;
		}
		return result;
	}
}
