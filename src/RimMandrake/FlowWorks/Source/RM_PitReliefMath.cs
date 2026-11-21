using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN (owner by card 2026-11-20, "In 0.1.0, full rebuild"): the pit
	/// is drawn as RELATIVE TERRAIN, the decisions of the walls layer (SectionLayer_RMExcavationWalls) that are not the face
	/// tables. Verse-free; its offline twin is model/pitdraw.py, which sweeps the whole range of situations and writes the golden
	/// table SelfTest/PitReliefParityChecks.cs checks this file against.
	///
	/// Owner, walk 2026-11-20, of his own stepped pit (rows 3.5, 3.5 and 5.5 m deep): <i>"Clearly you have not implemented the pit
	/// visuals as relative terrain representation, just "pit or no pit" floor. That won't do. Need more generalization."</i>
	///
	///   • every edge between two squares of different height is drawn by the deeper square (the planner already did this);
	///   • every change of a square's height re-meshes it and its 8 neighbours, at every depth (the layer used to re-mesh only
	///     on a floor TERRAIN change, and every floor past 2 m is one terrain, so a pit cut deeper past 2 m kept its old faces);
	///   • every dug floor is shaded by its own depth, darker at every notch over the whole dig range (past 2 m every floor was
	///     the one RM_Channel_Superdeep colour), and a 0.5 m canal floor is darker than plain gravel (his walk: "a darker floor
	///     would likely help");
	///   • a face keeps telling drops apart past the tallest face (2.5 m) by a dark foot;
	///   • the convex corner of a shallower block inside a deeper area is closed (outline quadrant, and the side face continued
	///     beside the block at a north corner);
	///   • a square under a concealed cover (a lid printing the ground) draws no pit art.</summary>
	public static class RM_PitReliefMath
	{
		/// <summary>Floor terrain colour by depth band (FlowWorks_Terrain.xml: plain Gravel, 0.78, 0.58, 0.38; every depth past 2 m
		/// is RM_Channel_Superdeep's 0.38) [measured, the defs].</summary>
		private static readonly float[] TerrainColour = { 1f, 1f, 0.78f, 0.58f, 0.38f };

		/// <summary>Floor brightness wanted at 0.5, 1, 1.5 and 2 m: even steps of 0.14 down to the 2 m floor, which keeps its look.</summary>
		private static readonly float[] BrightnessShallow = { 1f, 0.80f, 0.66f, 0.52f, 0.38f };

		/// <summary>Past 2 m: brightness 0.38 x (1 - FloorLogK x log2(d / 4)), never under FloorMin of 0.38 (a fixed share darker at
		/// every doubling of depth; the rate is a choice for his look, the bar is that two depths never draw alike).</summary>
		public const float FloorLogK = 0.22f;
		public const float FloorMin = 0.25f;

		/// <summary>The face foot past the tallest face (NorthByDrop index 5, 2.5 m): FaceFootK x log2(e / 5), at most FaceFootMax.</summary>
		public const float FaceFootFrom = 5f;
		public const float FaceFootK = 0.22f;
		public const float FaceFootMax = 0.70f;

		/// <summary>The floor's brightness at depth <paramref name="d"/> notches (1 = undug ground).</summary>
		public static float FloorBrightness(int d)
		{
			if (d <= 0) return 1f;
			if (d <= 4) return BrightnessShallow[d];
			double r = 1.0 - FloorLogK * (Math.Log(d / 4.0) / Math.Log(2.0));
			return TerrainColour[4] * (float)Math.Max(FloorMin, r);
		}

		/// <summary>The black alpha laid over a dug floor (its terrain) at depth <paramref name="d"/> notches, so the floor draws at
		/// <see cref="FloorBrightness"/>. 0 at 2 m (that floor keeps its look).</summary>
		public static float FloorShade(int d)
		{
			if (d <= 0) return 0f;
			float t = TerrainColour[d < 4 ? d : 4];
			float a = 1f - FloorBrightness(d) / t;
			return a > 0f ? (float)Math.Round(a, 5) : 0f;
		}

		/// <summary>The black alpha at the foot of a face whose exposed drop is <paramref name="exposed"/> notches (0 at its top):
		/// nothing up to the tallest face, then a fixed step per doubling of the drop.</summary>
		public static float FaceFootShade(float exposed)
		{
			if (exposed <= FaceFootFrom) return 0f;
			double a = FaceFootK * (Math.Log(exposed / FaceFootFrom) / Math.Log(2.0));
			return (float)Math.Round(Math.Min(FaceFootMax, a), 5);
		}

		/// <summary>A change of a square's height always re-meshes it and its 8 neighbours (the art of a square reads only its 3x3:
		/// model/pitdraw.py proves the locality over random fields, covers included).</summary>
		public static bool RedrawsOnDepthChange(int before, int after)
		{
			return before != after;
		}

		/// <summary>Does a square draw pit art? Not when it is undug, nor when a cover on it prints the ground (covered and none of
		/// its 8 neighbours shows a hole: RM_PitCoverLookMath.ShowsArt false). RIMMANDRAKE_HIDE_FLOWWORKS_PIT_WALLS_UNDER_CONCEALED_COVER:
		/// the faces draw at render queues after the cover's ground print, so a concealed square must draw none.</summary>
		public static bool DrawsPitArt(int hollow, bool covered, bool lidShowsArt)
		{
			return hollow > 0 && !(covered && !lidShowsArt);
		}

		/// <summary>The side face continued into a north corner of a square at depth <paramref name="d"/> whose north
		/// (<paramref name="dn"/>) and side (<paramref name="dSide"/>) neighbours are not shallower and whose north diagonal
		/// (<paramref name="dDiag"/>) is: width and height of the piece, from the drop to the diagonal less the liquid
		/// (<paramref name="level"/> notches). False when there is none.</summary>
		public static bool CornerPiece(int d, int dn, int dSide, int dDiag, float level, out float width, out float height)
		{
			width = 0f;
			height = 0f;
			if (d <= 0 || dn < d || dSide < d || dDiag >= d) return false;
			float e = RM_UnderLiquid.Exposed(d, dDiag, level);
			float w = RM_UnderLiquid.SideFace(e), h = RM_UnderLiquid.NorthFace(e);
			if (w <= 0f || h <= 0f) return false;
			width = w;
			height = h;
			return true;
		}

		/// <summary>The corner piece as a quad (x, z pairs in cell units from the square's south-west corner: bottom-left, top-left,
		/// top-right, bottom-right): the side face continued down by <paramref name="h"/> beside the block, its foot mitred at 45
		/// degrees away from the block.</summary>
		public static void CornerPoly(bool east, float w, float h, float[] xz)
		{
			float m = Math.Min(w, h);
			if (east)
			{
				Set(xz, 1f - w, 1f - h + m, 1f - w, 1f, 1f, 1f, 1f, 1f - h);
			}
			else
			{
				Set(xz, 0f, 1f - h, 0f, 1f, w, 1f, w, 1f - h + m);
			}
		}

		private static void Set(float[] xz, params float[] v)
		{
			Array.Copy(v, xz, 8);
		}

		/// <summary>Does the outline close a corner at a diagonal? The diagonal (<paramref name="dDiag"/>) is shallower and neither
		/// square beside it (<paramref name="dA"/>, <paramref name="dB"/>) is, so no line of this square's reaches the corner.</summary>
		public static bool ClosesCorner(int d, int dA, int dB, int dDiag)
		{
			return d > 0 && dA >= d && dB >= d && dDiag < d;
		}

		/// <summary>The floor left between the faces, as at most two rectangles (x0, z0, x1, z1) written into
		/// <paramref name="into"/> (8 floats): below the corner pieces the full width between the side faces, beside them the part
		/// between the pieces. Never under a face. Returns how many.</summary>
		public static int FloorRects(float ww, float ew, float h, float wnw, float hnw, float wne, float hne, float[] into)
		{
			float top = 1f - h;
			float x0 = ww, x1 = 1f - ew;
			if (x1 <= x0 || top <= 0f) return 0;
			float hc = Math.Max(hnw, hne);
			if (hc <= 0f)
			{
				Rect(into, 0, x0, 0f, x1, top);
				return 1;
			}
			float zc = Math.Min(top, 1f - hc);
			int n = 0;
			if (zc > 0f)
			{
				Rect(into, n++, x0, 0f, x1, zc);
			}
			float ux0 = Math.Max(x0, wnw), ux1 = Math.Min(x1, 1f - wne);
			if (ux1 > ux0 && top > zc)
			{
				Rect(into, n++, ux0, zc, ux1, top);
			}
			return n;
		}

		private static void Rect(float[] into, int k, float x0, float z0, float x1, float z1)
		{
			into[4 * k] = x0;
			into[4 * k + 1] = z0;
			into[4 * k + 2] = x1;
			into[4 * k + 3] = z1;
		}

		/// <summary>RIMMANDRAKE_DIM_FLOWWORKS_DROWNED_WALLS_PALE_FRAME_IN_WATER: the far wall's drowned band spans only between the
		/// side walls' full feet (each side strip carries its own corner). It spanned the whole square, so the wall light lay twice
		/// over the side strips: a pale frame.</summary>
		public static void DrownedBandX(float wFullWest, float wFullEast, out float x0, out float x1)
		{
			x0 = wFullWest;
			x1 = 1f - wFullEast;
		}

		/// <summary>The same item: a drowned side strip stops at the far wall's waterline; above it the dry north face is drawn. It
		/// ran the square's full height under that face, and its light lay twice there.</summary>
		public static float SideUnderTop(float wetTop)
		{
			return wetTop;
		}
	}
}
