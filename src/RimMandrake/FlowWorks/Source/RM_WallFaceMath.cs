namespace RimMandrake.FlowWorks
{
	/// <summary>EXCAVATION_WALL_ART_1 — the geometry of the wall faces (Verse-free, selftested).
	/// Quarry perspective (ruling 33): the camera looks down from the south, so the inner face of a cut's
	/// NORTH bank is what you see; east/west banks show as narrow side faces; the south bank is hidden behind
	/// its own lip. Every depth must read differently (owner, 2026-09-17), so face height grows with the drop.
	/// PROVISIONAL numbers.</summary>
	public static class RM_WallFaceMath
	{
		/// <summary>North-face band height (cells) per level of drop: D=4 under open ground shows 0.9 of a cell.</summary>
		public const float NorthPerLevel = 0.225f;
		public const float NorthMax = 0.92f;

		/// <summary>Side-face strip width (cells) per level of drop.</summary>
		public const float SidePerLevel = 0.06f;
		public const float SideMax = 0.24f;

		/// <summary>The exposed drop: how far this cell's floor sits below its neighbour's floor, less whatever
		/// liquid stands in this cell (water covers the foot of the wall). Never negative.</summary>
		public static int ExposedDrop(int myDepth, int neighbourDepth, int myFill)
		{
			int drop = myDepth - neighbourDepth;
			if (drop <= 0) return 0;
			int exposed = drop - (myFill < 0 ? 0 : myFill);
			return exposed < 0 ? 0 : exposed;
		}

		public static float NorthFaceHeight(int exposedDrop)
		{
			if (exposedDrop <= 0) return 0f;
			float h = exposedDrop * NorthPerLevel;
			return h > NorthMax ? NorthMax : h;
		}

		public static float SideFaceWidth(int exposedDrop)
		{
			if (exposedDrop <= 0) return 0f;
			float w = exposedDrop * SidePerLevel;
			return w > SideMax ? SideMax : w;
		}

		/// <summary>0..1 darkness at the FOOT of a face for a cell of total depth D (deeper = darker), so even two
		/// faces of equal height read as different depths.</summary>
		public static float FootDarkness(int depth)
		{
			if (depth <= 0) return 0f;
			float d = 0.35f + 0.15f * depth;
			return d > 0.95f ? 0.95f : d;
		}
	}
}
