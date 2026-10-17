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

		public const byte MaxDepth = Superdeep;

		/// <summary>Base dig work for one level, before the depth multiplier.
		/// Unchanged from the shipped single-level value so a shallow channel
		/// still costs exactly what it always did.</summary>
		public const int WorkPerLevel = 3200;

		/// <summary>Work to take a cell from <paramref name="fromDepth"/> to the
		/// next level down. Each level is deeper spoil to move and further to
		/// throw it, so the cost rises with the level being cut.</summary>
		public static int WorkToDeepen(byte fromDepth)
		{
			int toLevel = fromDepth + 1;
			if (toLevel < 1)
			{
				toLevel = 1;
			}
			if (toLevel > MaxDepth)
			{
				toLevel = MaxDepth;
			}
			return WorkPerLevel * toLevel;
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

		/// <summary>The dry terrain that expresses a given D (a lake bed deeper than <see cref="MaxDepth"/> reads as SUPERDEEP's). This is how an
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
				// POND_ELEVATION_BUILD_LAKES_RUN_DEEP: only a drained lake's bed reads deeper than a dig goes; its climb
				// is priced as the deepest dug cell's (a null here made a step in a deep bowl free).
				default: return depth > Superdeep ? RimMandrakeFlowWorks_DefOf.RM_Channel_Superdeep : null;
			}
		}

		/// <summary>The inverse: D re-derived from terrain. Used once per map
		/// to rehydrate a save written before the depth grid existed, where
		/// every dug cell is RM_Channel_Empty and therefore shallow.</summary>
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
