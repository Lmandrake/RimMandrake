using UnityEngine;
using Verse;

namespace BigAndSmall;

public class URenderWorker_Hair : URenderWorker_FlipWhenCrawling
{
	public override Vector3 ScaleFor(PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		Vector3 result = base.ScaleFor(node, parms);
		HeadTypeDef headType = parms.pawn.story.headType;
		if (parms.facing == Rot4.East || parms.facing == Rot4.West)
		{
			result.x *= headType.hairMeshSize.x / 1.5f;
		}
		result.z *= headType.hairMeshSize.y / 1.5f;
		return result;
	}
}
