namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT (owner 2026-10-24, of a plank lid on the centre square of an open 3x3 pit: "says
	/// it's a plank covered pit, but it sure doesn't look like it (empty pit appearance?)"). A lid prints the ground round the
	/// pit so a WHOLLY covered pit is invisible (bar pit_covered_invisible, the 2026-10-21 card "the disguised look is right").
	/// A lid with an open pit square beside it disguises nothing (the hole is in plain view) and its ground print reads as a
	/// floating square of dirt, so such a lid draws its own tier texture instead: planks over the hole. Covering the last
	/// open square of the pit turns every lid back into ground. No Verse types: linked into the SelfTest project.
	/// </summary>
	public static class RM_PitCoverLookMath
	{
		/// <summary>Does a lid draw its own art? <paramref name="neighbourSeenDepths"/>: the depth each of its 8 neighbours
		/// SHOWS (RM_SuspensionUnderpass.SeenDepthAt: a lidded or decked square shows its deck, ground shows 0, off the map
		/// is -1). Any neighbour showing a hole betrays the pit.</summary>
		public static bool ShowsArt(int[] neighbourSeenDepths)
		{
			if (neighbourSeenDepths == null)
			{
				return false;
			}
			for (int i = 0; i < neighbourSeenDepths.Length; i++)
			{
				if (neighbourSeenDepths[i] > 0)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Did a change of a square's shown depth from <paramref name="before"/> to <paramref name="after"/> flip
		/// whether it betrays the lids round it (open hole vs not)? Only then do they re-print.</summary>
		public static bool FlipsNeighbourLids(int before, int after)
		{
			return (before > 0) != (after > 0);
		}

		/// <summary>Steps per cell edge of the occluder's art-piece UV grid: a piece's texture window is snapped to it (one
		/// texel of a 64 px lid), so the mesh cache holds a bounded set.</summary>
		public const int UvSteps = 64;

		/// <summary>The texture window of the piece [l,r] x [a,b] of cell (cx, cz), as snapped grid steps u0 &lt; u1, v0 &lt;
		/// v1 in [0, UvSteps]: the lid texture spans its cell exactly (drawSize 1x1, unrotated), so the piece shows the same
		/// texels the lid shows under it. False when the piece is empty after clamping to the cell.</summary>
		public static bool PieceUv(int cx, int cz, float l, float r, float a, float b, out int u0, out int u1, out int v0, out int v1)
		{
			u0 = u1 = v0 = v1 = 0;
			if (r <= cx || l >= cx + 1f || b <= cz || a >= cz + 1f)
			{
				return false;
			}
			u0 = Snap(l - cx);
			u1 = Snap(r - cx);
			v0 = Snap(a - cz);
			v1 = Snap(b - cz);
			if (u1 <= u0 && r - l > 0f)
			{
				u1 = u0 < UvSteps ? u0 + 1 : u0;
				u0 = u1 - 1;
			}
			if (v1 <= v0 && b - a > 0f)
			{
				v1 = v0 < UvSteps ? v0 + 1 : v0;
				v0 = v1 - 1;
			}
			return u0 >= 0 && v0 >= 0 && u1 > u0 && v1 > v0;
		}

		/// <summary>One key per snapped window (the mesh cache's key).</summary>
		public static int UvKey(int u0, int u1, int v0, int v1)
		{
			const int n = UvSteps + 1;
			return ((u0 * n + u1) * n + v0) * n + v1;
		}

		private static int Snap(float f)
		{
			if (f <= 0f)
			{
				return 0;
			}
			if (f >= 1f)
			{
				return UvSteps;
			}
			return (int)System.Math.Round(f * UvSteps);
		}
	}
}
