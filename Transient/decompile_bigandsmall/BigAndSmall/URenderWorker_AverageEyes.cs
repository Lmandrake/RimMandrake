using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class URenderWorker_AverageEyes : URenderWorker_FlipWhenCrawling
{
	public override Vector3 OffsetFor(PawnRenderNode node, PawnDrawParms parms, out Vector3 pivot)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		Vector3 val = base.OffsetFor(node, parms, out pivot);
		List<Vector3> list = new List<Vector3>();
		float num = default(float);
		if (TryGetWoundAnchor("RightEye", parms, out var anchor))
		{
			Vector3 item = default(Vector3);
			PawnDrawUtility.CalcAnchorData(parms.pawn, anchor, parms.facing, ref item, ref num);
			list.Add(item);
		}
		if (TryGetWoundAnchor("LeftEye", parms, out var anchor2))
		{
			Vector3 item2 = default(Vector3);
			PawnDrawUtility.CalcAnchorData(parms.pawn, anchor2, parms.facing, ref item2, ref num);
			list.Add(item2);
		}
		if (list.Count > 0)
		{
			val += list.Aggregate((Vector3 acc, Vector3 x) => acc + x) / (float)list.Count;
		}
		return val;
	}

	public override Vector3 ScaleFor(PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		return base.ScaleFor(node, parms) * (parms.pawn.ageTracker.CurLifeStage.eyeSizeFactor ?? 1f);
	}

	protected bool TryGetWoundAnchor(string anchorTag, PawnDrawParms parms, out WoundAnchor anchor)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		anchor = null;
		if (GenText.NullOrEmpty(anchorTag))
		{
			return false;
		}
		List<WoundAnchor> woundAnchors = parms.pawn.story.bodyType.woundAnchors;
		for (int i = 0; i < woundAnchors.Count; i++)
		{
			WoundAnchor val = woundAnchors[i];
			if (val.tag == anchorTag)
			{
				Rot4? rotation = val.rotation;
				Rot4 facing = parms.facing;
				if (rotation.HasValue && (!rotation.HasValue || rotation.GetValueOrDefault() == facing) && (parms.facing == Rot4.South || val.narrowCrown == true == parms.pawn.story.headType.narrow))
				{
					anchor = val;
					return true;
				}
			}
		}
		return false;
	}
}
