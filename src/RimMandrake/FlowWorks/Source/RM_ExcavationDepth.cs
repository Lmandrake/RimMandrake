using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// The D/F primitive of ruling 18, and the four depths of ruling 19.
	///
	/// Every excavated cell carries two small integers and everything the
	/// family does is a function of them on one cell:
	///
	///   D (depth) — how far below floor level. 0 = surface. Set by digging,
	///               and by nothing else (LAW 1: we dig down, we never build up).
	///   F (fill)  — how much liquid is in it, 0 &lt;= F &lt;= D. Set by the engine.
	///
	/// LAW 2 bounds what may read them: depth affects MOVEMENT and LIQUID. It
	/// never affects sight, cover or projectile arcs. Exactly TWO stated, narrow
	/// exceptions exist, and neither is a precedent for any other system:
	///   • ruling 23 — a SUPERDEEP occupant may only trade fire with whoever is
	///     at its own lip (a RESTRICTION on an existing check;
	///     RM_Patch_SuperdeepShooting);
	///   • [D] (owner, 2026-09-17) — a SUPERDEEP cell may bound a ROOM: the pit
	///     wall splits regions, districts and rooms (RM_PitRooms). Only D = 4,
	///     only room membership; D 1-3 bound nothing.
	/// </summary>
	public static class RM_ExcavationDepth
	{
		public const byte Surface = 0;

		public const byte Shallow = 1;

		public const byte Mid = 2;

		public const byte Deep = 3;

		/// <summary>Ruling 19: the trapping level, and what a natural liquid
		/// source reads as (ruling 24 — a source is not a building, it is a
		/// SUPERDEEP cell at F = D).</summary>
		public const byte Superdeep = 4;

		// PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT (owner R5, 2026-10-17): the dig cap is no longer Superdeep. MaxDepth is deleted
		// so that no reader can keep meaning both: the absolute pit is Superdeep (= RM_DigDepthMath.PitDepth), the cap is
		// MaxDigDepth (a Mod Setting, default 8 m, 2 to 20 m), the deepest a dug square may hold is MaxDigCeiling (20 m).

		/// <summary>The colonist dig cap in notches, from the Mod Setting (default 16 = 8 m, range 4..40).</summary>
		public static int MaxDigDepth => RimMandrakeFlowWorksSettings.MaxDigDepth;

		/// <summary>The deepest a dug square may be (20 m): the load repair's clamp. Lowering the cap never shallows a cell.</summary>
		public const byte MaxDigCeiling = (byte)RM_DigDepthMath.MaxDigCeiling;

		/// <summary>Base dig work for one level, before the depth multiplier.
		/// Unchanged from the shipped single-level value so a shallow channel
		/// still costs exactly what it always did.</summary>
		public const int WorkPerLevel = RM_DigDepthMath.WorkPerNotch;

		/// <summary>Work to take a cell from <paramref name="fromDepth"/> to the next notch down: 3,200 × the notch being cut
		/// (P6, V1; RM_DigDepthMath.WorkToCut), flat past 2 m when the "deeper costs more" setting is off.</summary>
		public static int WorkToDeepen(byte fromDepth)
		{
			return RM_DigDepthMath.WorkToCut(fromDepth + 1, RimMandrakeFlowWorksSettings.digCostRisesWithDepth);
		}

		/// <summary>A hole's depth for a player, in metres (unified depth spec §2.1: "deep" is never a number): "0.5 m",
		/// "1 m", "1.5 m", "pit 2 m", deeper "pit 3.5 m". "surface" for 0.</summary>
		public static string LabelOf(byte depth)
		{
			if (depth == Surface)
			{
				return "surface";
			}
			string m = RM_Volume.FormatMetres(depth);
			return depth >= Superdeep ? "pit " + m : m;
		}

		/// <summary>The dry terrain that expresses a given D (anything deeper than <see cref="Superdeep"/>, a deep dig or a lake bed, reads as SUPERDEEP's: the four terrains are BANDS; the depth lives in the grid). This is how an
		/// integer becomes a pathCost the vanilla pathfinder already honours
		/// (ruling 17's 30 at shallow, rising with depth) without a Harmony
		/// patch on PathGrid.</summary>
		public static TerrainDef DryTerrainFor(byte depth)
		{
			switch (depth)
			{
				case Shallow: return RimMandrakeFlowWorks_DefOf.RM_Channel_Empty;
				case Mid: return RimMandrakeFlowWorks_DefOf.RM_Channel_Mid;
				case Deep: return RimMandrakeFlowWorks_DefOf.RM_Channel_Deep;
				case Superdeep: return RimMandrakeFlowWorks_DefOf.RM_Channel_Superdeep;
				// POND_ELEVATION_BUILD_LAKES_RUN_DEEP / PIT_DEPTH_WIDEN: a drained lake's bed or a dig past 2 m; its climb is
				// priced as the deepest band's (a null here made a step in a deep bowl free).
				default: return depth > Superdeep ? RimMandrakeFlowWorks_DefOf.RM_Channel_Superdeep : null;
			}
		}

		/// <summary>The inverse: D re-derived from terrain. Used once per map
		/// to rehydrate a save written before the depth grid existed, where
		/// every dug cell is RM_Channel_Empty and therefore shallow.
		/// ⛔ PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: NEVER a depth for digging, pricing or drawing. Terrain cannot say more than
		/// "2 m or deeper" (every cell past 2 m is RM_Channel_Superdeep); the grid (RM_MapComponent_Excavation.ExcavatedDepthAt)
		/// is the depth. Its remaining callers ask only "is this a dug-channel terrain at all".</summary>
		public static byte DepthOfDryTerrain(TerrainDef terrain)
		{
			if (terrain == null)
			{
				return Surface;
			}
			if (terrain == RimMandrakeFlowWorks_DefOf.RM_Channel_Empty) return Shallow;
			if (terrain == RimMandrakeFlowWorks_DefOf.RM_Channel_Mid) return Mid;
			if (terrain == RimMandrakeFlowWorks_DefOf.RM_Channel_Deep) return Deep;
			if (terrain == RimMandrakeFlowWorks_DefOf.RM_Channel_Superdeep) return Superdeep;
			return Surface;
		}

		/// <summary>LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §4.1): the water picture band by METRES OF WATER, never
		/// by how full the hole is: 0 dry, 1 under 25 cm, 2 ≈ 0.5 m, 3 ≈ 1 m, 4 ≈ 1.5 m, 5 = 2 m and deeper
		/// (<see cref="RM_LevelSolve.LookBand"/>). The same in a canal, a pit or a pond: 1 m of water looks like 1 m of water
		/// in a 1 m canal and in a 2 m pit. The hole's own depth is the walls' and the readout's to show.</summary>
		public static int FillTier(long waterDl)
		{
			return RM_LevelSolve.LookBand(waterDl);
		}

		/// <summary><see cref="FillTier(long)"/> of whole notches of liquid (the hole's depth is not an input).</summary>
		public static int FillTier(byte fill)
		{
			return RM_LevelSolve.LookBand(fill * (long)RM_LevelSolve.U);
		}
	}
}
