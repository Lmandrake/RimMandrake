using System;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class PlaceWorker_CompCustomCauseHediff_AoE : PlaceWorker
{
	public override void DrawGhost(ThingDef def, IntVec3 center, Rot4 rot, Color ghostCol, Thing thing = null)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		CompProperties_CustomCauseHediff_AoE compProperties = def.GetCompProperties<CompProperties_CustomCauseHediff_AoE>();
		if (compProperties == null)
		{
			return;
		}
		Map map = Find.CurrentMap;
		Room room = RegionAndRoomQuery.RoomAt(center, map, (RegionType)15);
		if ((!compProperties.worksInside || !compProperties.worksOutside) && (!compProperties.worksInside || room == null || room.PsychologicallyOutdoors) && (!compProperties.worksOutside || (room != null && !room.PsychologicallyOutdoors)))
		{
			return;
		}
		float range = compProperties.range;
		bool sameRoomOnly = compProperties.sameRoomOnly;
		bool flag = room != null && room.AnyPassable;
		if (range > 0f)
		{
			if (sameRoomOnly && flag)
			{
				GenDraw.DrawRadiusRing(center, compProperties.range, Color.white, (Func<IntVec3, bool>)((IntVec3 cell) => room == GridsUtility.GetRoom(cell, map)));
			}
			else
			{
				GenDraw.DrawRadiusRing(center, compProperties.range);
			}
		}
		else if (sameRoomOnly && flag)
		{
			GenDraw.DrawRadiusRing(center, GenRadial.MaxRadialPatternRadius - 1f, Color.white, (Func<IntVec3, bool>)((IntVec3 cell) => room == GridsUtility.GetRoom(cell, map)));
		}
	}
}
