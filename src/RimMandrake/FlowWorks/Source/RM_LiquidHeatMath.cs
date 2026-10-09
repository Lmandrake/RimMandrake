using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LIQUID_HEAT_PUSH_1 (FL-1 / X-8), the Verse-free arithmetic so the selftest drives the production numbers.
	/// Hot and icy liquid move the air through VANILLA heat only (owner 2026-09-29: "It can't be a new kind of heat"):
	/// energy goes into Room.Temperature exactly as a heater's does, and vanilla Heatstroke / Hypothermia do any harm.
	/// Bounded three ways: a room never passes the liquid's own target temperature, one room takes at most a fixed
	/// number of heaters' worth per interval, and a map processes at most a fixed number of cells per interval.
	/// Every number is PROVISIONAL.
	/// </summary>
	public static class RM_LiquidHeatMath
	{
		/// <summary>The push runs every 250 ticks (one rare tick; the default flow pulse).</summary>
		public const int IntervalTicks = 250;

		/// <summary>Vanilla's own seconds-per-rare-tick factor (CompTempControl: energyPerSecond * 4.1666665).</summary>
		public const float SecondsPerInterval = IntervalTicks / 60f;

		/// <summary>PROVISIONAL. Energy per second per fill level of hot liquid: a superdeep cell brim-full of boiling
		/// water (4 levels) is about half a vanilla heater (21/s).</summary>
		public const float HotPerLevelPerSecond = 3f;

		/// <summary>PROVISIONAL. Icy liquid draws a little less than boiling liquid gives.</summary>
		public const float ColdPerLevelPerSecond = 2f;

		/// <summary>PROVISIONAL. A room warmed by hot liquid levels off here (a steam room, well past heatstroke).</summary>
		public const float HotTargetC = 50f;

		/// <summary>PROVISIONAL. A room chilled by icy liquid levels off here (water at the freeze).</summary>
		public const float ColdTargetC = 0f;

		/// <summary>PROVISIONAL. One room takes at most this many vanilla heaters' worth per interval (8 x 21/s), so a
		/// hall roofed over a lake does not jump to the target in one step.</summary>
		public const float MaxRoomPerSecond = 8f * 21f;

		/// <summary>A natural liquid cell (a pond, the Scald) counts as this many fill levels.</summary>
		public const int NaturalCellLevels = 2;

		/// <summary>At most this many cells are visited per interval per map; the rest are visited on later intervals
		/// (round robin) and the energy is scaled up so the average power stays exact.</summary>
		public const int CellBudgetPerInterval = 3000;

		/// <summary>Signed energy one cell pushes in one interval: + for hot, - for cold, 0 for neither, a dry cell, or
		/// strength 0. <paramref name="levels"/> is the fill level (excavated) or NaturalCellLevels (terrain).</summary>
		public static float CellEnergy(int heatKind, int levels, float strength)
		{
			if (levels <= 0 || strength <= 0f || heatKind == 0)
			{
				return 0f;
			}
			float perSecond = heatKind > 0 ? HotPerLevelPerSecond : -ColdPerLevelPerSecond;
			return perSecond * levels * SecondsPerInterval * strength;
		}

		/// <summary>The heat kind from two flags: +1 hot, -1 cold, 0 neither. Both set reads as neither (a def that
		/// claims both is a data error, and pushing nothing is the safe reading).</summary>
		public static int Kind(bool hot, bool cold)
		{
			if (hot == cold)
			{
				return 0;
			}
			return hot ? 1 : -1;
		}

		/// <summary>The energy a room actually takes this interval: the summed cell energy, capped per room
		/// (scaled by strength), then clamped so Room.Temperature (+= energy / cellCount) never passes the target.
		/// A hot room already at or above its target takes nothing; a cold one at or below its target takes nothing.</summary>
		public static float RoomEnergy(float summed, float roomTempC, int roomCells, float strength)
		{
			if (summed == 0f || roomCells <= 0)
			{
				return 0f;
			}
			float cap = MaxRoomPerSecond * SecondsPerInterval * Math.Max(0f, strength);
			if (summed > 0f)
			{
				float room = (HotTargetC - roomTempC) * roomCells;
				return Math.Max(0f, Math.Min(Math.Min(summed, cap), room));
			}
			float roomCold = (ColdTargetC - roomTempC) * roomCells;   // negative while warmer than the target
			return Math.Min(0f, Math.Max(Math.Max(summed, -cap), roomCold));
		}

		/// <summary>How many cells to visit this interval out of <paramref name="total"/>, and the factor that scales
		/// their energy so a partial visit still delivers the full average power.</summary>
		public static int Budget(int total, out float scale)
		{
			if (total <= CellBudgetPerInterval)
			{
				scale = 1f;
				return Math.Max(0, total);
			}
			scale = (float)total / CellBudgetPerInterval;
			return CellBudgetPerInterval;
		}
	}
}
