using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 2. Same shape as vanilla
	/// Designator_ZoneAdd_Growing/Designator_ZoneAdd_Fishing (both read via
	/// rimsage against the decompiled source before writing this) — the
	/// husbandry pen designator, restricted to water cells only. Icon reuses
	/// the vanilla Odyssey fishing-zone texture (placeholder, same "marked, not
	/// a considered choice" precedent as wave 1's retinted-vanilla creature art;
	/// no bespoke icon exists for this yet).
	/// </summary>
	public class RM_Designator_ZoneAdd_PoolPen : Designator_ZoneAdd
	{
		protected override string NewZoneLabel => "Pool pen";

		public override bool Visible => RM_WeepingStonesSettings.stockedPoolsEnabled;

		public RM_Designator_ZoneAdd_PoolPen()
		{
			zoneTypeToPlace = typeof(RM_Zone_PoolPen);
			defaultLabel = "Pool pen";
			defaultDesc = "Designate a stocked-pool pen over open water. Nets breeding stock, "
				+ "not a building — pen walls (ordinary low walls at the waterline) are placed "
				+ "separately to raise the escape bar.";
			icon = ContentFinder<Texture2D>.Get("UI/Designators/ZoneCreate_Fishing");
			tutorTag = "ZoneAdd_RM_PoolPen";
		}

		public override AcceptanceReport CanDesignateCell(IntVec3 c)
		{
			if (!c.InBounds(base.Map))
			{
				return false;
			}
			if (!c.GetTerrain(base.Map).IsWater)
			{
				return "Pool pens can only be designated over open water.";
			}
			return base.CanDesignateCell(c);
		}

		protected override Zone MakeNewZone()
		{
			return new RM_Zone_PoolPen(Find.CurrentMap.zoneManager);
		}
	}
}
