using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNodeWorker_BodyTypeOffsets : PawnRenderNodeWorker_Body
{
	public override Vector3 OffsetFor(PawnRenderNode node, PawnDrawParms parms, out Vector3 pivot)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = node.tree.pawn;
		Vector3 result = ((PawnRenderNodeWorker)this).OffsetFor(node, parms, ref pivot);
		result.x *= pawn?.story?.bodyType?.bodyGraphicScale.x ?? 1f;
		result.z *= pawn?.story?.bodyType?.bodyGraphicScale.y ?? 1f;
		return result;
	}
}
