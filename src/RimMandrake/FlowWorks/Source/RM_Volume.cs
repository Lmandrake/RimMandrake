using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK: one volume yardstick for every square that holds liquid (design
	/// natural_bodies_as_canals_design_2026-10-11.md §8, §9.6). Owner, 2026-10-12: <i>"1 tank square, 1 deep water
	/// square/pond, 1 deep canal square should all be the same volume."</i> and <i>"deep water is an at least 4 notches
	/// deep ... A tall tank should hold twice as much."</i>
	///
	/// One square = one DEEP NOTCH = <see cref="LevelsPerSquare"/> levels = <see cref="UnitsPerSquare"/> tank units.
	/// This is its own constant, NOT <see cref="RM_ExcavationDepth.MaxDepth"/>: a deeper natural bed (§9) or a deeper
	/// dig never changes what a tank square holds.
	///
	/// ⛔ Verse-free: compiled into Source/SelfTest/ as the production file.
	/// </summary>
	public static class RM_Volume
	{
		/// <summary>One deep notch: a tank square, a deep canal square, the shallowest deep-pond square.</summary>
		public const int LevelsPerSquare = 4;

		/// <summary>The unit bridge between the channel ledger (levels) and the tank ledger (units): a level is a
		/// bucket's worth.</summary>
		public const int UnitsPerLevel = 5;

		/// <summary>Tank units in one square (20).</summary>
		public const int UnitsPerSquare = LevelsPerSquare * UnitsPerLevel;

		/// <summary>Ruling 3/7 (2026-10-12): a shallow-water pond square holds 2 levels, which is also its bed depth.</summary>
		public const int ShallowBedLevels = 2;

		/// <summary>Deep water is told from shallow by the engine's own walking numbers, not by defName: vanilla's
		/// WaterDeepBase is Impassable (pathCost 300) and WaterChestDeepBase costs 42, while WaterShallowBase and
		/// Marsh cost 30 (Core Terrain_Water.xml, read 2026-10-13). Any liquid terrain at this cost or above is deep.</summary>
		public const int DeepPathCostFloor = 40;

		/// <summary>The save format of every volume this file defines. 1 = before this item (5 levels a pond square,
		/// 300/600-unit tanks); 2 = one square = one square. Scribed by RM_MapComponent_Excavation.</summary>
		public const int CurrentModel = 2;

		/// <summary>Bed depth, and so budget, of one natural liquid square in levels.</summary>
		public static int BedLevels(bool impassable, int pathCost)
		{
			return impassable || pathCost >= DeepPathCostFloor ? LevelsPerSquare : ShallowBedLevels;
		}

		// ── POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE step 2: the hollow (design §4 B, owner rulings 2-4) ──────────────

		/// <summary>The depth a square reads as a hole (climb, sink, wall faces, DepthAt): the dug depth when dug, else a
		/// dry pond square's bed depth when hollows are on, else 0. A dug square is never bed (one owner per square).</summary>
		public static int HollowDepth(int dugDepth, int bedDepth, bool hollowsOn)
		{
			if (dugDepth != 0)
			{
				return dugDepth;
			}
			return hollowsOn && bedDepth > 0 ? bedDepth : 0;
		}

		/// <summary>The lakebed terrain a dried square shows at its bed depth (owner look (b), 2026-10-13): the deep bed at
		/// a deep notch or more, the shallow bed below it.</summary>
		public static string LakebedFor(int bedDepth)
		{
			return bedDepth >= LevelsPerSquare ? "RM_Lakebed_Deep" : "RM_Lakebed_Shallow";
		}

		/// <summary>§7 #8 / Option B: does a dug square of depth <paramref name="dugDepth"/> holding <paramref name="fill"/>
		/// levels pour one level into a neighbouring dry bed square of depth <paramref name="bedDepth"/>? Its water stands at
		/// fill − dugDepth against the ground and the bed's floor at −bedDepth, so it runs while the water is above the floor:
		/// a brim-full canal always does, and it stops once its surface is down at the bed's floor.</summary>
		public static bool RunsIntoBed(int dugDepth, int fill, int bedDepth)
		{
			return dugDepth > 0 && fill > 0 && bedDepth > 0 && dugDepth - fill < bedDepth;
		}

		/// <summary>Body capacity in fill-units: Σ bed levels × volumePerTile × budgetMultiplier, never below the
		/// stock model's per-cell floor (a slider at its lowest notch must not make every pond capacity 0).</summary>
		public static float BodyCapacity(int bedLevelSum, int cellCount, float volumePerTile, float budgetMultiplier)
		{
			if (cellCount <= 0 || bedLevelSum <= 0)
			{
				return 0f;
			}
			float cap = bedLevelSum * volumePerTile * budgetMultiplier;
			float floor = cellCount * RM_StockMath.MinPerCellVolume;
			return cap < floor ? floor : cap;
		}

		/// <summary>Tank capacity in units: footprint squares × <see cref="UnitsPerSquare"/> × (2 when tall) × the
		/// tank slider, never below one level (a tank that cannot hold one level cannot take a pump's level).</summary>
		public static int TankCapacity(int footprintArea, bool tall, float multiplier)
		{
			return TankCapacity(footprintArea, tall ? 2f : 1f, multiplier);
		}

		/// <summary>Same, with an explicit height factor (1 = ordinary, 2 = tall, 4 = extra-tall) in place of the tall flag.</summary>
		public static int TankCapacity(int footprintArea, float heightFactor, float multiplier)
		{
			int area = Math.Max(1, footprintArea);
			double units = area * (double)UnitsPerSquare * Math.Max(0.0, heightFactor) * multiplier;
			return Math.Max(UnitsPerLevel, (int)Math.Round(units, MidpointRounding.AwayFromZero));
		}

		/// <summary>§8.3 migration of a limited pond: keep its FILL FRACTION when its capacity is recomputed. A pond's
		/// volume was a budget, never water the player put there, so this is the one sanctioned volume change.</summary>
		public static float MigratedStock(float oldStock, float oldCapacity, float newCapacity)
		{
			if (oldCapacity <= 0f || newCapacity <= 0f)
			{
				return newCapacity > 0f ? newCapacity : 0f;
			}
			float frac = oldStock / oldCapacity;
			if (frac < 0f) frac = 0f;
			if (frac > 1f) frac = 1f;
			return frac * newCapacity;
		}

		/// <summary>§8.3: a tank loaded from an older model keeps every unit it stored, even above its new capacity.
		/// It is overfull: it refuses input and drains normally.</summary>
		public static bool Overfull(int storedUnits, int capacity)
		{
			return storedUnits > capacity;
		}
	}
}
