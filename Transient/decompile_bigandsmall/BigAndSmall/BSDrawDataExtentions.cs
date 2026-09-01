using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class BSDrawDataExtentions
{
	public static List<Vector3> GetCombinedOffsetsByRot(this List<BSDrawData> offsets, float multipler = 1f)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		bool flag = false;
		List<Vector3> list = new List<Vector3>
		{
			Vector3.zero,
			Vector3.zero,
			Vector3.zero,
			Vector3.zero
		};
		foreach (int item in Enumerable.Range(0, 4))
		{
			foreach (BSDrawData offset in offsets)
			{
				List<Vector3> list2 = list;
				int index = item;
				list2[index] += ((DrawData)offset).OffsetForRot(new Rot4(item)) * multipler;
				flag = true;
			}
		}
		if (!flag)
		{
			return null;
		}
		return list;
	}
}
