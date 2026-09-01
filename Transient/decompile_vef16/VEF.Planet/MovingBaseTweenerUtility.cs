using System.Collections.Generic;
using System.Linq;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Planet;

public static class MovingBaseTweenerUtility
{
	private const float BaseRadius = 0.15f;

	private const float BaseDistToCollide = 0.2f;

	public static Vector3 PatherTweenedPosRoot(MovingBase movingBase)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		WorldGrid worldGrid = Find.WorldGrid;
		if (!((WorldObject)movingBase).Spawned)
		{
			return worldGrid.GetTileCenter(((WorldObject)movingBase).Tile);
		}
		if (movingBase.pather.Moving)
		{
			float num = (movingBase.pather.IsNextTilePassable() ? (1f - movingBase.pather.nextTileCostLeft / movingBase.pather.nextTileCostTotal) : 0f);
			int num2 = PlanetTile.op_Implicit((movingBase.pather.nextTile != ((WorldObject)movingBase).Tile || movingBase.pather.previousTileForDrawingIfInDoubt == PlanetTile.op_Implicit(-1)) ? ((WorldObject)movingBase).Tile : movingBase.pather.previousTileForDrawingIfInDoubt);
			return worldGrid.GetTileCenter(movingBase.pather.nextTile) * num + worldGrid.GetTileCenter(PlanetTile.op_Implicit(num2)) * (1f - num);
		}
		return worldGrid.GetTileCenter(((WorldObject)movingBase).Tile);
	}

	public static Vector3 MovingBaseCollisionPosOffsetFor(MovingBase movingBase)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		if (!((WorldObject)movingBase).Spawned)
		{
			return Vector3.zero;
		}
		bool flag = ((WorldObject)movingBase).Spawned && movingBase.pather.Moving;
		float num = 0.15f * Find.WorldGrid.AverageTileSize;
		if (!flag || movingBase.pather.nextTile == movingBase.pather.Destination)
		{
			PlanetTile val = ((!flag) ? ((WorldObject)movingBase).Tile : movingBase.pather.nextTile);
			int movingBasesCount = 0;
			int movingBasesWithLowerIdCount = 0;
			GetMovingBasesStandingAtOrAboutToStandAt(val, out movingBasesCount, out movingBasesWithLowerIdCount, movingBase);
			if (movingBasesCount == 0)
			{
				return Vector3.zero;
			}
			return WorldRendererUtility.ProjectOnQuadTangentialToPlanet(Find.WorldGrid.GetTileCenter(val), GenGeo.RegularPolygonVertexPosition(movingBasesCount, movingBasesWithLowerIdCount, 0f) * num);
		}
		if (DrawPosCollides(movingBase))
		{
			Rand.PushState();
			Rand.Seed = ((WorldObject)movingBase).ID;
			float num2 = Rand.Range(0f, 360f);
			Rand.PopState();
			Vector2 val2 = new Vector2(Mathf.Cos(num2), Mathf.Sin(num2)) * num;
			return WorldRendererUtility.ProjectOnQuadTangentialToPlanet(PatherTweenedPosRoot(movingBase), val2);
		}
		return Vector3.zero;
	}

	private static void GetMovingBasesStandingAtOrAboutToStandAt(PlanetTile tile, out int movingBasesCount, out int movingBasesWithLowerIdCount, MovingBase forMovingBase)
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		movingBasesCount = 0;
		movingBasesWithLowerIdCount = 0;
		List<MovingBase> list = Find.WorldObjects.AllWorldObjects.OfType<MovingBase>().ToList();
		for (int i = 0; i < list.Count; i++)
		{
			MovingBase movingBase = list[i];
			if (((WorldObject)movingBase).Tile != tile)
			{
				if (!movingBase.pather.Moving || movingBase.pather.nextTile != movingBase.pather.Destination || movingBase.pather.Destination != tile)
				{
					continue;
				}
			}
			else if (movingBase.pather.Moving)
			{
				continue;
			}
			movingBasesCount++;
			if (((WorldObject)movingBase).ID < ((WorldObject)forMovingBase).ID)
			{
				movingBasesWithLowerIdCount++;
			}
		}
	}

	private static bool DrawPosCollides(MovingBase movingBase)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		Vector3 val = PatherTweenedPosRoot(movingBase);
		float num = Find.WorldGrid.AverageTileSize * 0.2f;
		List<MovingBase> list = Find.WorldObjects.AllWorldObjects.OfType<MovingBase>().ToList();
		for (int i = 0; i < list.Count; i++)
		{
			MovingBase movingBase2 = list[i];
			if (movingBase2 != movingBase && Vector3.Distance(val, PatherTweenedPosRoot(movingBase2)) < num)
			{
				return true;
			}
		}
		return false;
	}
}
