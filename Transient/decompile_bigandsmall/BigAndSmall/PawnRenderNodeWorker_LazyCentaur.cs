using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNodeWorker_LazyCentaur : PawnRenderNodeWorker_Body
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
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0118: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0257: Unknown result type (might be due to invalid IL or missing references)
		BodyTypeDef val = node?.tree?.pawn?.story?.bodyType;
		Rot4 facing = parms.facing;
		if (val == null)
		{
			return ((PawnRenderNodeWorker)this).OffsetFor(node, parms, ref pivot);
		}
		Vector3 result = ((PawnRenderNodeWorker)this).OffsetFor(node, parms, ref pivot);
		if (val == BodyTypeDefOf.Male)
		{
			result.x += ((facing == Rot4.East) ? (-0.009f) : ((facing == Rot4.West) ? 0.009f : 0f));
			result.z += 0.04f;
		}
		else if (val == BodyTypeDefOf.Female)
		{
			result.x += ((facing == Rot4.East) ? 0.01f : ((facing == Rot4.West) ? (-0.01f) : 0f));
			result.z += 0.005f;
		}
		else if (val == BodyTypeDefOf.Hulk)
		{
			result.x += ((facing == Rot4.East) ? (-0.08f) : ((facing == Rot4.West) ? 0.08f : 0f));
			result.z -= 0.08f;
		}
		else if (val == BodyTypeDefOf.Thin)
		{
			result.x += ((facing == Rot4.East) ? (-0.2f) : ((facing == Rot4.West) ? 0.2f : 0f));
		}
		else if (val == BodyTypeDefOf.Fat)
		{
			result.x += ((facing == Rot4.East) ? 0.16f : ((facing == Rot4.West) ? (-0.16f) : 0f));
			result.z += 0.12f;
		}
		else if (val == BodyTypeDefOf.Child)
		{
			result.z += 0.1f;
		}
		else if (val == BodyTypeDefOf.Baby)
		{
			result.z += 0.1f;
		}
		result.x *= val?.bodyGraphicScale.x ?? 1f;
		result.z *= val?.bodyGraphicScale.y ?? 1f;
		return result;
	}
}
