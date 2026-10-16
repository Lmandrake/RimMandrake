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

		/// <summary>LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (owner 2026-10-16, "Count in Litres"; design
		/// liquid_litres_2026-10-16.md): one level is one cubic metre. A vanilla human draws 1.20 cells tall and is ~1.75 m, so a
		/// cell is ~1.46 m; deep water (4 levels) is ~2 m, so a level is ~0.5 m deep and 1.46² × 0.5 ≈ 1.07 m³. 1,000 L is
		/// within 7 % of that and makes every readout legible: a level = 1 kL, a deep square = 4 kL.</summary>
		public const int LitresPerLevel = 1000;

		/// <summary>The depth of one level in metres (mouseover readout).</summary>
		public const float MetresPerLevel = 0.5f;

		/// <summary>The integer tank unit is a DECILITRE: a 1.5 L bottle is exactly 15 units, and every integer ledger
		/// (tanks, hoses, pumps, nets) stays exact. Players only ever see litres (<see cref="FormatUnits"/>).</summary>
		public const int UnitsPerLitre = 10;

		/// <summary>The unit bridge between the channel ledger (levels) and the tank ledger (units): 10,000 dL = 1,000 L.</summary>
		public const int UnitsPerLevel = LitresPerLevel * UnitsPerLitre;

		/// <summary>Tank units in one square (40,000 dL = 4 kL).</summary>
		public const int UnitsPerSquare = LevelsPerSquare * UnitsPerLevel;

		/// <summary>Model 2's tank unit: a fifth of a level (200 L, "a drum"). Saves and settings written before model 3 hold
		/// amounts in it; <see cref="FromLegacyUnits(int)"/> converts them once.</summary>
		public const int LegacyUnitsPerLevel = 5;

		/// <summary>Decilitres in one model-2 unit (2,000).</summary>
		public const int LegacyUnitScale = UnitsPerLevel / LegacyUnitsPerLevel;

		/// <summary>Litres in one model-2 unit (200).</summary>
		public const int LegacyUnitLitres = LitresPerLevel / LegacyUnitsPerLevel;

		/// <summary>Litres → integer units, rounded half away from zero.</summary>
		public static int Units(float litres)
		{
			double u = Math.Round(litres * (double)UnitsPerLitre, MidpointRounding.AwayFromZero);
			return u >= int.MaxValue ? int.MaxValue : u <= int.MinValue ? int.MinValue : (int)u;
		}

		/// <summary>Integer units → litres.</summary>
		public static float Litres(int units) => units / (float)UnitsPerLitre;

		/// <summary>A model-2 amount (200 L units) in model-3 units, clamped to int.</summary>
		public static int FromLegacyUnits(int legacy)
		{
			long u = (long)legacy * LegacyUnitScale;
			return u >= int.MaxValue ? int.MaxValue : u <= int.MinValue ? int.MinValue : (int)u;
		}

		/// <summary>A model-2 float amount in model-3 units.</summary>
		public static float FromLegacyUnits(float legacy) => legacy * LegacyUnitScale;

		/// <summary>Litres for a player: "1.5 L", "15 L", "208 L", "4 kL", "12.5 kL". Invariant culture (inspect panes,
		/// probes and parsers read the same text).</summary>
		public static string FormatLitres(double litres)
		{
			var inv = System.Globalization.CultureInfo.InvariantCulture;
			double a = Math.Abs(litres);
			if (a >= 1000.0)
			{
				return (litres / 1000.0).ToString(a >= 100000.0 ? "0" : "0.#", inv) + " kL";
			}
			return litres.ToString(a >= 100.0 ? "0" : "0.#", inv) + " L";
		}

		/// <summary><see cref="FormatLitres"/> of an integer unit amount.</summary>
		public static string FormatUnits(int units) => FormatLitres(units / (double)UnitsPerLitre);

		/// <summary>Depth for a player: "0.5 m", "2 m" (levels may be fractional: a part-drained pond square).</summary>
		public static string FormatMetres(double levels) => (levels * MetresPerLevel).ToString("0.#", System.Globalization.CultureInfo.InvariantCulture) + " m";

		/// <summary>The mouseover line for a liquid square: "1.5 m deep, 3 kL" (levels of liquid standing in it).</summary>
		public static string DepthReadout(double levels, double litres)
		{
			return FormatMetres(levels) + " deep, " + FormatLitres(litres);
		}

		/// <summary>Ruling 3/7 (2026-10-12): a shallow-water pond square holds 2 levels, which is also its bed depth.</summary>
		public const int ShallowBedLevels = 2;

		/// <summary>Deep water is told from shallow by the engine's own walking numbers, not by defName: vanilla's
		/// WaterDeepBase is Impassable (pathCost 300) and WaterChestDeepBase costs 42, while WaterShallowBase and
		/// Marsh cost 30 (Core Terrain_Water.xml, read 2026-10-13). Any liquid terrain at this cost or above is deep.</summary>
		public const int DeepPathCostFloor = 40;

		/// <summary>The save format of every volume this file defines. 1 = before POND_VOLUME_UNIFY (5 levels a pond square,
		/// 300/600-unit tanks); 2 = one square = one square, 5 units a level; 3 = litres (a unit is a decilitre, 10,000 a level).
		/// Scribed by RM_MapComponent_Excavation (ponds) and by every holder of tank units (tanks, hoses, converters).</summary>
		public const int CurrentModel = 3;

		/// <summary>The model a unit holder reads when its save carries no marker: every save before model 3.</summary>
		public const int LegacyModel = 2;

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

		/// <summary>POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE (owner by card 2026-10-14, "When a colonist digs in a dried-out pond bed,
		/// what should happen? → Dig deeper from the bed"): the depth of the FIRST cut into a square that is not dug yet. On a dry
		/// pond bed with hollows on it starts from the bed and goes one deeper (2 → 3); elsewhere 0 → 1. -1 = refused: the bed
		/// is already as deep as digging goes (a deep bed at the max; deeper digging is DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL),
		/// or the cut would deepen past the first level while deepening is switched off.</summary>
		public static int FirstCutDepth(int bedDepth, bool hollowsOn, int maxDepth, bool deepeningOn = true)
		{
			int from = hollowsOn && bedDepth > 0 ? bedDepth : 0;
			if (from >= maxDepth || (from > 0 && !deepeningOn))
			{
				return -1;
			}
			return from + 1;
		}

		/// <summary>POND_ELEVATION_BUILD_LAKES_RUN_DEEP: from this bed depth a dried square shows the darker abyss bed (the deep
		/// lakebed art, tinted; no new art). Twice the deep notch, so a lake's middle reads deeper than its shelves.</summary>
		public const int AbyssBedLevels = 2 * LevelsPerSquare;

		/// <summary>The lakebed terrain a dried square shows at its bed depth (owner look (b), 2026-10-13): the deep bed at
		/// a deep notch or more, the shallow bed below it; past <see cref="AbyssBedLevels"/> the abyss bed.</summary>
		public static string LakebedFor(int bedDepth)
		{
			if (bedDepth >= AbyssBedLevels)
			{
				return "RM_Lakebed_Abyss";
			}
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
