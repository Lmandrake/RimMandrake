using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_DEPTH_DRAW_OFFSET_1 — the arithmetic of a pawn sinking with canal depth,
	/// Verse-free on purpose so Source/SelfTest/ compiles THIS production file (same
	/// discipline as RM_PitTrapMath).
	///
	/// Owner, 2026-10-02: <i>"The pawn should visibly rise up and lower down as they move
	/// over the depths. They should be low enough that it is visually clear how they could
	/// not possibly climb out (the walls are higher than their head by 20%)"</i>.
	///
	/// RimWorld's oblique view draws "lower" as further south on screen (vanilla's own
	/// flying lift is +0.6 z in Pawn_DrawTracker.FlyingOffset), so a pawn on a cell of
	/// depth D is drawn D × <see cref="DefaultSinkPerLevel"/> cells south of its tweened
	/// position. Between two cells the sink is interpolated by how far the tween has
	/// travelled, so the pawn rises and lowers smoothly rather than stepping.
	///
	/// PROVISIONAL (owner has not set a number beyond the 20 %): 0.3 cells per level, so a
	/// SUPERDEEP floor sits 1.2 cells below the lip. A humanlike reads about
	/// <see cref="HumanlikeFeetToHeadTop"/> = 1.0 cell feet-to-crown (PROVISIONAL, measure
	/// from a live frame), so at D = 4 the wall stands 1.2 × head height — his 20 %.
	/// Larger bodies poke further up; the 20 % bar is stated for a person.
	/// </summary>
	public static class RM_PitDrawMath
	{
		public const int MaxDepth = 4;

		/// <summary>PROVISIONAL: cells of southward draw offset per level of depth.</summary>
		public const float DefaultSinkPerLevel = 0.3f;

		/// <summary>PROVISIONAL: a humanlike's on-screen height, feet to crown, in cells.</summary>
		public const float HumanlikeFeetToHeadTop = 1.0f;

		/// <summary>Sink (cells, positive = drawn lower) for a pawn standing on depth D.</summary>
		public static float SinkFor(int depth, float sinkPerLevel)
		{
			if (depth <= 0 || !(sinkPerLevel > 0f))
			{
				return 0f;
			}
			return Math.Min(depth, MaxDepth) * sinkPerLevel;
		}

		/// <summary>Sink partway from a cell of depth <paramref name="fromDepth"/> to one of
		/// <paramref name="toDepth"/>; <paramref name="t"/> is the tween's progress 0..1.</summary>
		public static float SinkBetween(int fromDepth, int toDepth, float t, float sinkPerLevel)
		{
			if (t <= 0f || float.IsNaN(t))
			{
				return SinkFor(fromDepth, sinkPerLevel);
			}
			if (t >= 1f)
			{
				return SinkFor(toDepth, sinkPerLevel);
			}
			float a = SinkFor(fromDepth, sinkPerLevel);
			float b = SinkFor(toDepth, sinkPerLevel);
			return a + (b - a) * t;
		}

		/// <summary>PIT_LIP_OCCLUDES_OUTSIDE_1 — the most a pawn on a cell whose centre is at
		/// <paramref name="cellCentreZ"/> may sink when the near (south) lip in its column is at
		/// <paramref name="lipZ"/>: its drawn centre never drops past the lip, so the sprite stays
		/// inside the pit opening and only its lower half goes behind the near bank. Without this a
		/// pawn on the pit's south row at D4 (sink 1.2) was drawn wholly south of the pit, over the
		/// ground outside it (owner's muffalo, 2026-10-06). NaN lipZ (no lip found) leaves the sink.</summary>
		public static float ClampSinkToLip(float sink, float cellCentreZ, float lipZ)
		{
			if (!(sink > 0f) || float.IsNaN(lipZ))
			{
				return sink > 0f ? sink : 0f;
			}
			float room = cellCentreZ - lipZ;
			if (room <= 0f)
			{
				return 0f;
			}
			return sink < room ? sink : room;
		}

		/// <summary>Tween progress from the centre of the cell a pawn is leaving
		/// (<paramref name="ax"/>,<paramref name="az"/>) toward the next cell's centre, given the
		/// drawn position (<paramref name="px"/>,<paramref name="pz"/>). Projected onto the
		/// step, clamped 0..1.</summary>
		public static float StepProgress(float ax, float az, float bx, float bz, float px, float pz)
		{
			float dx = bx - ax;
			float dz = bz - az;
			float len2 = dx * dx + dz * dz;
			if (len2 <= 1e-6f)
			{
				return 1f;
			}
			float t = ((px - ax) * dx + (pz - az) * dz) / len2;
			return t < 0f ? 0f : (t > 1f ? 1f : t);
		}

		/// <summary>The wall above an occupant's crown as a ratio of their height: the lip is
		/// D × sink above the floor. 1.2 is the owner's 20 % bar.</summary>
		public static float WallOverHeadRatio(int depth, float sinkPerLevel, float feetToHeadTop)
		{
			if (!(feetToHeadTop > 0f))
			{
				return 0f;
			}
			return SinkFor(depth, sinkPerLevel) / feetToHeadTop;
		}
	}
}
