namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_SINK_GEYSER_INTO_PIT_BUBBLING_HOT_TUB: the pure verdicts of a steam geyser in a dug pit (owner 2026-11-12:
	/// "Digging a pit on a Geyser allows the Geyser to descend to the bottom of the pit (it remains and descends). Filling the
	/// pit with water or any fluid still works and generates distinctive bubbles where the geyser is. When pawns are near those
	/// bubbles, they will treat it like a hot tub"). Spec: design/specs/geyser_in_pit_hot_tub_2026-11-12.md. The game side is
	/// RM_GeyserPit. Verse-free: SelfTest GeyserTubChecks runs this.
	/// </summary>
	public static class RM_GeyserTubMath
	{
		/// <summary>The vent mound's drawn height (m): liquid deeper than this over the seat covers the vent mouth.</summary>
		public const float GeyserMetres = 0.4f;

		/// <summary>Standalone Hot Spring's numbers, copied as our own defaults (no dependency on that mod).</summary>
		public const int SoakTicks = 3000;
		public const float RestEffectiveness = 1.111f;
		public const float JoyGainFactor = 1.4f;
		public const int MaxBathers = 6;
		public const float DefaultReach = 2.5f;
		public const float DefaultHealing = 1.25f;

		/// <summary>Liquids by how they bathe (owner by card 2026-11-12: "Water plus harmless liquids"): None is never a pool
		/// (acid, poison, boiling, icy, the fuels, reaction liquor); Water always is; the others each follow their own setting
		/// and carry their own cost (FluidDef.bathCost).</summary>
		public enum BathGroup
		{
			None,
			Water,
			Tar,
			Oil,
			Blood,
			Slime
		}

		public static bool GroupAllowed(BathGroup g, bool tar, bool oil, bool blood, bool slime)
		{
			switch (g)
			{
				case BathGroup.Water: return true;
				case BathGroup.Tar: return tar;
				case BathGroup.Oil: return oil;
				case BathGroup.Blood: return blood;
				case BathGroup.Slime: return slime;
				default: return false;
			}
		}

		/// <summary>The seat: the SHALLOWEST dug depth of the geyser's cells (it sits on ground that is there, never floats).
		/// Null, empty or any cell at or under 0 is the surface.</summary>
		public static int SeatNotches(int[] depths)
		{
			if (depths == null || depths.Length == 0)
			{
				return 0;
			}
			int seat = int.MaxValue;
			for (int i = 0; i < depths.Length; i++)
			{
				if (depths[i] <= 0)
				{
					return 0;
				}
				if (depths[i] < seat)
				{
					seat = depths[i];
				}
			}
			return seat;
		}

		/// <summary>The vent mouth is under once the liquid over the seat is deeper than the mound.</summary>
		public static bool Covered(float levelMetresOverSeat) => levelMetresOverSeat > GeyserMetres;

		/// <summary>A pool: a bathable fluid stands over an uncovered-by-generator vent that it covers.</summary>
		public static bool PoolSafe(bool hasFluid, bool bathable, bool covered, bool capped) => hasFluid && bathable && covered && !capped;

		/// <summary>A cell (<paramref name="dx"/>, <paramref name="dz"/> from the 2x2 centre to the cell's centre) is in the
		/// pool's reach when strictly nearer than <paramref name="reach"/>.</summary>
		public static bool InReach(float dx, float dz, float reach) => dx * dx + dz * dz < reach * reach;

		/// <summary>Days a hediff of <paramref name="severity"/> falling <paramref name="perDay"/> lasts.</summary>
		public static float AfterglowDays(float severity, float perDay) => perDay > 0f ? severity / perDay : 0f;

		// ── the plume ───────────────────────────────────────────────────

		/// <summary>Bubbles a second over the footprint while the vent sprays; between sprays a fifth of it keeps going, so a
		/// sunk geyser is always findable by eye.</summary>
		public const float SprayBubblesPerSecond = 6f;
		public const float BetweenShare = 0.2f;

		/// <summary>A liquid this slow (FluidDef.ticksPerTile; water 60) is thick: fewer, bigger, slower bubbles, no ring.</summary>
		public const int ThickTicksPerTile = 120;

		public static bool Thick(int ticksPerTile) => ticksPerTile >= ThickTicksPerTile;

		public static float PlumeRate(bool spraying, int ticksPerTile, float density)
		{
			if (!(density > 0f))
			{
				return 0f;
			}
			float r = SprayBubblesPerSecond * (spraying ? 1f : BetweenShare);
			return (Thick(ticksPerTile) ? r * 0.4f : r) * density;
		}

		public static float PlumeScaleMin(int ticksPerTile) => Thick(ticksPerTile) ? 2.2f : 1.5f;

		public static float PlumeScaleMax(int ticksPerTile) => Thick(ticksPerTile) ? 3f : 2.2f;

		/// <summary>Bubbles to throw this tick for <paramref name="perSecond"/>, with a uniform <paramref name="roll"/> in [0,1):
		/// averages the rate exactly.</summary>
		public static int BubblesThisTick(float perSecond, float roll)
		{
			if (!(perSecond > 0f))
			{
				return 0;
			}
			return (int)(perSecond / 60f + roll);
		}

		// ── the drawn seat ──────────────────────────────────────────────

		/// <summary>How far south (cells) the print is lowered: the pawns' sink for the seat (<paramref name="perLevel"/> a
		/// notch), never more than the <paramref name="roomCells"/> rows of pit at least as deep south of the footprint, so the
		/// print stays inside the pit's outline.</summary>
		public static float SeatSink(int seatNotches, float perLevel, int roomCells)
		{
			if (seatNotches <= 0 || !(perLevel > 0f) || roomCells <= 0)
			{
				return 0f;
			}
			float s = seatNotches * perLevel;
			return s < roomCells ? s : roomCells;
		}
	}
}
