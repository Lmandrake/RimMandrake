using System;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(PawnRenderer), "BaseHeadOffsetAt")]
public static class PawnRenderer_BaseHeadOffsetAt
{
	public static void Postfix(PawnRenderer __instance, ref Vector3 __result, ref Rot4 rotation)
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = __instance.pawn;
		BSCache cachePrepatchedThreaded = pawn.GetCachePrepatchedThreaded();
		if (cachePrepatchedThreaded != null)
		{
			__result = new Vector3(__result.x * cachePrepatchedThreaded.headPositionMultiplier, __result.y, __result.z * cachePrepatchedThreaded.headPositionMultiplier);
			if (cachePrepatchedThreaded.hasComplexHeadOffsets)
			{
				PawnDrawParms parms = __instance.results.parms;
				if (!((Enum)parms.flags).HasFlag((Enum)(object)(PawnRenderFlags)1))
				{
					Vector3 val = (Vector3)(((Rot4)(ref rotation)).AsInt switch
					{
						0 => cachePrepatchedThreaded.complexHeadOffsets[0], 
						1 => cachePrepatchedThreaded.complexHeadOffsets[1], 
						2 => cachePrepatchedThreaded.complexHeadOffsets[2], 
						3 => cachePrepatchedThreaded.complexHeadOffsets[3], 
						_ => Vector3.zero, 
					});
					__result += val;
				}
			}
		}
		if (pawn == null)
		{
			Log.Warning($"PawnRenderer_BaseHeadOffsetAt: pawn is null ({__instance}");
		}
	}
}
