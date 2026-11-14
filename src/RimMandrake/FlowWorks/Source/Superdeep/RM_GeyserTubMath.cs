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

		/// <summary>RIMMANDRAKE_RESTRICT_HEAT_TO_GEYSER_BENEATH_PIT_WATER_ONLY (owner 2026-11-13: "I had intended that the Geyser
		/// must itself be beneath the pit water itself, not just adjacent ... There's no way for the heat to get from the hole
		/// into the pit water in this configuration."): the squares of a <paramref name="width"/> x <paramref name="height"/>
		/// window (row-major, x fastest) the vent heats: the <paramref name="water"/> squares joined edge to edge, through water,
		/// to a vent square (<paramref name="vent"/>, window indices) that is itself under water. A vent under no water heats
		/// nothing; water in another pit or lake, however near, is never reached. Null or mismatched input: nothing.</summary>
		public static bool[] PoolRegion(int width, int height, bool[] water, int[] vent)
		{
			int n = width > 0 && height > 0 ? width * height : 0;
			bool[] reached = new bool[n];
			if (n == 0 || water == null || water.Length != n || vent == null)
			{
				return reached;
			}
			int[] stack = new int[n];
			int top = 0;
			for (int i = 0; i < vent.Length; i++)
			{
				int v = vent[i];
				if (v >= 0 && v < n && water[v] && !reached[v])
				{
					reached[v] = true;
					stack[top++] = v;
				}
			}
			while (top > 0)
			{
				int c = stack[--top];
				int x = c % width, z = c / width;
				for (int k = 0; k < 4; k++)
				{
					int nx = x + (k == 0 ? 1 : k == 1 ? -1 : 0), nz = z + (k == 2 ? 1 : k == 3 ? -1 : 0);
					if (nx < 0 || nz < 0 || nx >= width || nz >= height)
					{
						continue;
					}
					int j = nz * width + nx;
					if (water[j] && !reached[j])
					{
						reached[j] = true;
						stack[top++] = j;
					}
				}
			}
			return reached;
		}

		/// <summary>Days a hediff of <paramref name="severity"/> falling <paramref name="perDay"/> lasts.</summary>
		public static float AfterglowDays(float severity, float perDay) => perDay > 0f ? severity / perDay : 0f;

		// ── the plume ───────────────────────────────────────────────────

		/// <summary>The vent's bubbling (owner 2026-11-13, G2 under 1 m: "Bubbles are centered on vent itself, yes. They are too
		/// large and too transparent. It should be bubbling water, not faint ghost bubbles rising up."): many small, bright,
		/// mostly opaque bubbles (RM_Fleck_VentBubble, its own white art tinted per liquid) in a tight cluster on the vent's
		/// centre, short-lived and never stopping. A second while the vent sprays; between sprays some of it keeps going,
		/// so a sunk geyser is always findable by eye (round 7: three quarters). Before: 6 a second (1.2 between) of a 0.27..0.40-cell bubble at alpha
		/// 0.29, living 1.3 s, over a 0.95-cell circle.
		/// Round 7 (Conductor's ruling, round 6 read "a handful of specks"): a boiling patch about one square across centred
		/// on the vent, 30-60 bubbles alive at once of mixed sizes (0.06-0.25 squares), popping fast, with a soft froth ring
		/// (RM_Fleck_VentFroth). Rates are bubbles alive / life.</summary>
		public const float SprayBubblesPerSecond = 42f / BubbleLifeSeconds;
		public const float BetweenShare = 0.75f;

		/// <summary>Deeper liquid shows more of the column: the rate grows by DepthGain a metre over the seat, to DepthCap
		/// metres (x1.32 at 4 m and below). Cost: at most about 58 bubbles alive a geyser in view (pooled, one instanced batch).</summary>
		public const float DepthGain = 0.08f;
		public const float DepthCap = 4f;

		/// <summary>A liquid this slow (FluidDef.ticksPerTile; water 60) is thick: fewer, bigger, slower bubbles, no ring.</summary>
		public const int ThickTicksPerTile = 120;

		public static bool Thick(int ticksPerTile) => ticksPerTile >= ThickTicksPerTile;

		public static float DepthFactor(float levelMetres)
		{
			float m = levelMetres > 0f ? (levelMetres < DepthCap ? levelMetres : DepthCap) : 0f;
			return 1f + DepthGain * m;
		}

		/// <summary>Bubbles a second over the vent: 0 with the plume switched off (Mod Settings, RM_GeyserPitSettings.
		/// geyserPlumeEnabled) or density 0; else the spray or between rate, x0.4 in a thick liquid, x the depth factor, x the
		/// density slider.</summary>
		public static float PlumeRate(bool enabled, bool spraying, int ticksPerTile, float density, float levelMetres)
		{
			if (!enabled || !(density > 0f))
			{
				return 0f;
			}
			float r = SprayBubblesPerSecond * (spraying ? 1f : BetweenShare);
			return (Thick(ticksPerTile) ? r * 0.4f : r) * DepthFactor(levelMetres) * density;
		}

		/// <summary>How far from the vent's centre a bubble rises (cells): the boiling patch, about one square across.</summary>
		public const float PlumeRadius = 0.5f;

		/// <summary>RM_Fleck_VentBubble's drawSize (cells): the scale range below multiplies it.</summary>
		public const float BubbleDrawSize = 0.12f;

		public static float PlumeScaleMin(int ticksPerTile) => Thick(ticksPerTile) ? 0.8f : 0.5f;

		public static float PlumeScaleMax(int ticksPerTile) => Thick(ticksPerTile) ? 2.05f : 2.0f;

		/// <summary>A bubble's scale for a uniform <paramref name="roll"/>: mostly small, a few big (min + span x roll^2).</summary>
		public static float PlumeScale(int ticksPerTile, float roll)
		{
			float lo = PlumeScaleMin(ticksPerTile);
			return lo + (PlumeScaleMax(ticksPerTile) - lo) * roll * roll;
		}

		/// <summary>A bubble's life (s): RM_Fleck_VentBubble's fade-in + solid + fade-out.</summary>
		public const float BubbleLifeSeconds = 0.35f;

		/// <summary>RM_Fleck_VentFroth (a soft brighter ring of froth round the boiling patch): thrown this often a second over
		/// a covered vent in a thin liquid, each living about 1.2 s, drawn this wide (cells).</summary>
		public const float FrothPerSecond = 2.5f;
		public const float FrothDrawSize = 1.15f;

		/// <summary>Round 7 (owner: "the vent looks on top of the water"): under liquid the vanilla geyser art (a crisp hole,
		/// a pale ring and a 4-cell grey splotch) is replaced by RM_SunkVent, a soft dark hole this wide (cells) drawn under the
		/// liquid's sheet, so the water over the vent is the pit's water.</summary>
		public const float SunkVentDrawSize = 1.25f;

		/// <summary>The colour a vent bubbles in: a liquid look's own bubble colour when it sets one, else (the class default
		/// <paramref name="classDefault"/>) its own liquid colour lifted a quarter of the way to white, so tar bubbles dark grey,
		/// blood red, oil brown: every liquid in its own colour.</summary>
		public static RM_UnderLiquid.Float3 BubbleColour(RM_UnderLiquid.Float3 own, RM_UnderLiquid.Float3 classDefault, RM_UnderLiquid.Float3 liquid)
		{
			bool set = System.Math.Abs(own.r - classDefault.r) > 1e-3f || System.Math.Abs(own.g - classDefault.g) > 1e-3f
				|| System.Math.Abs(own.b - classDefault.b) > 1e-3f;
			if (set)
			{
				return own;
			}
			const float lift = 0.25f;
			return new RM_UnderLiquid.Float3(liquid.r + (1f - liquid.r) * lift, liquid.g + (1f - liquid.g) * lift, liquid.b + (1f - liquid.b) * lift);
		}

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
	}
}
