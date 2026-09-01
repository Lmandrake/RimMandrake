using System;
using System.Collections.Generic;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Pawn_PathFollower))]
[HarmonyPatch("CostToMoveIntoCell")]
[HarmonyPatch(new Type[]
{
	typeof(Pawn),
	typeof(IntVec3)
})]
public static class VanillaExpandedFramework_Pawn_PathFollower_CostToMoveIntoCell_Patch
{
	[HarmonyPostfix]
	public static void DisablePathCostForFloatingCreatures(Pawn pawn, IntVec3 c, ref float __result)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Invalid comparison between Unknown and I4
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Invalid comparison between Unknown and I4
		if (((Thing)pawn).Map == null || !AnimalBehaviours_Settings.flagHovering)
		{
			return;
		}
		if (StaticCollectionsClass.floating_animals.Contains((Thing)(object)pawn))
		{
			TerrainDef val = ((Thing)pawn).Map.terrainGrid.TerrainAt(c);
			float num = ((c.x != ((Thing)pawn).Position.x && c.z != ((Thing)pawn).Position.z) ? pawn.TicksPerMoveDiagonal : pawn.TicksPerMoveCardinal);
			if (val == null)
			{
				num = 10000f;
			}
			else if ((int)((BuildableDef)val).passability == 2 && !val.IsWater)
			{
				num = 10000f;
			}
			List<Thing> list = ((Thing)pawn).Map.thingGrid.ThingsListAt(c);
			for (int i = 0; i < list.Count; i++)
			{
				if ((int)((BuildableDef)list[i].def).passability == 2)
				{
					num = 10000f;
				}
			}
			__result = num;
		}
		if (StaticCollectionsClass.waterstriding_pawns.Contains((Thing)(object)pawn) && ((Thing)pawn).Map.terrainGrid.TerrainAt(c).IsWater)
		{
			float num2 = ((c.x != ((Thing)pawn).Position.x && c.z != ((Thing)pawn).Position.z) ? pawn.TicksPerMoveDiagonal : pawn.TicksPerMoveCardinal);
			__result = num2;
		}
	}
}
