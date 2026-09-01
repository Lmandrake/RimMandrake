using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(PawnRenderer), "ParallelGetPreRenderResults")]
public static class ParallelGetPreRenderResults_Patch
{
	public struct PGPRRCache
	{
		public Pawn pawn;

		public BSCache cache;

		public bool cachingDisabled;

		public bool doOffset;

		public bool doComplexBodyOffset;

		public bool spawned;

		public Rot4 rotation;

		public int tick10;

		public uint changeIndex;
	}

	[ThreadStatic]
	private static PGPRRCache threadStaticCache;

	public static bool skipOffset;

	private static bool SpawnedOrVisible(Pawn pawn)
	{
		if (!((Thing)pawn).Spawned)
		{
			return ((Thing)pawn).ParentHolder is PawnFlyer;
		}
		return true;
	}

	public static void Prefix(PawnRenderer __instance, ref Vector3 drawLoc, Rot4? rotOverride, bool neverAimWeapon, ref bool disableCache, Pawn ___pawn)
	{
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_021c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_0236: Unknown result type (might be due to invalid IL or missing references)
		//IL_023b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0243: Unknown result type (might be due to invalid IL or missing references)
		//IL_0258: Unknown result type (might be due to invalid IL or missing references)
		//IL_025d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0262: Unknown result type (might be due to invalid IL or missing references)
		//IL_026a: Unknown result type (might be due to invalid IL or missing references)
		//IL_027f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0284: Unknown result type (might be due to invalid IL or missing references)
		//IL_0289: Unknown result type (might be due to invalid IL or missing references)
		//IL_0291: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b0: Unknown result type (might be due to invalid IL or missing references)
		if (___pawn == null)
		{
			return;
		}
		bool flag = threadStaticCache.pawn != ___pawn || threadStaticCache.cache.IsTempCache;
		if (flag)
		{
			threadStaticCache.cache = ___pawn.GetCachePrepatchedThreaded();
			threadStaticCache.pawn = ___pawn;
			if (!threadStaticCache.cache.approximatelyNoChange)
			{
				threadStaticCache.spawned = SpawnedOrVisible(___pawn);
			}
		}
		if (threadStaticCache.cache.approximatelyNoChange || !threadStaticCache.spawned)
		{
			return;
		}
		Rot4 rotationInt = ((Thing)___pawn).rotationInt;
		if (flag || BS.Tick10 != threadStaticCache.tick10 || threadStaticCache.rotation != rotationInt)
		{
			threadStaticCache.tick10 = BS.Tick10;
			threadStaticCache.cachingDisabled = !disableCache && BigSmallMod.settings.disableTextureCaching && (threadStaticCache.cache.totalSizeOffset > 0f || threadStaticCache.cache.scaleMultiplier.linear > 1f || threadStaticCache.cache.renderCacheOff);
			int doOffset;
			if (BigSmallMod.settings.offsetBodyPos && (int)PawnUtility.GetPosture(___pawn) == 0)
			{
				if (!BigSmallMod.settings.offsetAnimalBodyPos)
				{
					RaceProperties raceProps = ___pawn.RaceProps;
					doOffset = ((raceProps != null && raceProps.Humanlike) ? 1 : 0);
				}
				else
				{
					doOffset = 1;
				}
			}
			else
			{
				doOffset = 0;
			}
			threadStaticCache.doOffset = (byte)doOffset != 0;
			threadStaticCache.doComplexBodyOffset = threadStaticCache.cache.complexBodyOffsets != null;
			threadStaticCache.rotation = (Rot4)(((_003F?)rotOverride) ?? ((Thing)___pawn).Rotation);
		}
		if (threadStaticCache.cachingDisabled)
		{
			disableCache = true;
		}
		if (skipOffset)
		{
			return;
		}
		if (threadStaticCache.doOffset)
		{
			drawLoc.z += threadStaticCache.cache.worldspaceOffset;
		}
		if (threadStaticCache.doComplexBodyOffset)
		{
			switch (((Rot4)(ref rotationInt)).AsInt)
			{
			case 0:
				drawLoc += threadStaticCache.cache.complexBodyOffsets[0];
				break;
			case 1:
				drawLoc += threadStaticCache.cache.complexBodyOffsets[1];
				break;
			case 2:
				drawLoc += threadStaticCache.cache.complexBodyOffsets[2];
				break;
			case 3:
				drawLoc += threadStaticCache.cache.complexBodyOffsets[3];
				break;
			}
		}
	}
}
