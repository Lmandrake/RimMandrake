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
	/// LAW 2 bounds what may read them: depth affects MOVEMENT and LIQUID and
	/// nothing else. It never affects sight, shooting, cover or projectile
	/// arcs — the one stated exception (ruling 23, a SUPERDEEP occupant may
	/// only trade fire with whoever is at their own lip) is a RESTRICTION on
	/// an existing check and is program 2's, not built here.
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

		public static string LabelOf(byte depth)
		{
			switch (depth)
			{
				case Shallow: return "shallow";
				case Mid: return "mid";
				case Deep: return "deep";
				case Superdeep: return "SUPERDEEP";
				default: return "surface";
			}
		}

		/// <summary>The dry terrain that expresses a given D. This is how an
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
				default: return null;
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

		/// <summary>Ruling 5's three-tier read of F, quantised against the
		/// cell's own D so a brimming shallow trench and a brimming deep one
		/// both read as brimming. 0 means dry.</summary>
		public static int FillTier(byte fill, byte depth)
		{
			if (fill <= 0 || depth <= 0)
			{
				return 0;
			}
			float ratio = (float)fill / depth;
			if (ratio <= 0.34f) return 1;
			if (ratio <= 0.67f) return 2;
			return 3;
		}
	}
}
