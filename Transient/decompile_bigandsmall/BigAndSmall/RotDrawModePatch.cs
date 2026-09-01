using System;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class RotDrawModePatch
{
	public struct PGPRRCache
	{
		public Pawn pawn;

		public BSCache cache;

		public Rot4 lastRot;

		public bool hasForcedRotDrawMode;

		public RotDrawMode rotDrawMode;

		public int tick10;
	}

	private static readonly int maxUses = 1000;

	[ThreadStatic]
	private static PGPRRCache threadStaticCache;

	[HarmonyPostfix]
	public static void CurRotDrawModePostfix(PawnRenderer __instance, ref RotDrawMode __result, Pawn ___pawn)
	{
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Expected I4, but got Unknown
		if (___pawn != null)
		{
			if (threadStaticCache.pawn != ___pawn || threadStaticCache.tick10 != BS.Tick10)
			{
				threadStaticCache.cache = ___pawn.GetCachePrepatchedThreaded();
				threadStaticCache.pawn = ___pawn;
				threadStaticCache.hasForcedRotDrawMode = threadStaticCache.cache.forcedRotDrawMode.HasValue;
				threadStaticCache.rotDrawMode = (RotDrawMode)(((_003F?)threadStaticCache.cache.forcedRotDrawMode) ?? 1);
				threadStaticCache.tick10 = BS.Tick10;
			}
			if (threadStaticCache.hasForcedRotDrawMode)
			{
				__result = (RotDrawMode)(int)threadStaticCache.rotDrawMode;
			}
		}
	}
}
