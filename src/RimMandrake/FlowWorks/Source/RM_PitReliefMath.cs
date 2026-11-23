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
			float w = RM_UnderLiquid.SideFaceAt(d, dDiag, level), h = RM_UnderLiquid.NorthFaceAt(d, dDiag, level);
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

		// ── the stepped-pit rule (RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM) ─────────────────────────
		// Owner, 2026-11-22, of stepped-pit mock-ups: "it can't go all the way up to the original pit outside... that's what's
		// making it look like a standing wall. The inner "cliff" should only go part way up the side walls. It's all about the
		// side wall interactions. They need to extend deeper into the pit where it is deeper". Twin:
		// design/specs/2026-11-22-stepped-pit-inner-cliff/pitrule.py (metres; these take notches of 0.5 m).
		//   • two offset functions of depth, StepH (north face) and StepW (side strip), today's tables to 2.5 m, rising on to 20 m;
		//   • a wall between a shallow floor a and a deep floor b shows H(b) - H(a) / W(b) - W(a), so a riser's top meets each side
		//     wall at that wall's depth-a line, never at the ground rim, and the side wall runs on unbroken above it;
		//   • every surface darkens by StepK of its depth (a multiplier: it holds over any floor terrain laid later);
		//   • a fixed sun from the north-west lights the faces by their facing and casts a shadow past each face's foot.

		private static readonly float[] StepNorthTable = { 0f, 0.12f, 0.23f, 0.35f, 0.50f, 0.62f };
		private static readonly float[] StepSideTable = { 0f, 0.06f, 0.11f, 0.17f, 0.23f, 0.29f };
		private const double StepHTop = 0.97, StepWTop = 0.46, StepP = 0.6, StepDeepest = 20.0;
		private const double StepKScale = 0.75, StepKPow = 0.62;

		/// <summary>The sun: compass degrees the light comes from (315 = north-west, option B of the pick) and its elevation.</summary>
		public const float SunAzimuth = 315f, SunElevation = 55f;
		private const float Ambient = 0.55f, Direct = 0.45f, WallAmbient = 0.85f;
		/// <summary>A face darkens toward its foot by this share (a crisp foot, never a gradient that melts into the floor).</summary>
		public const float FaceFade = 0.30f;
		private const float ShadowK = 0.15f, ShadowPow = 0.7f, Penumbra = 0.04f, MarchStep = 1f / 32f;
		/// <summary>The pale edge of an upper floor at its lip (his "differently colored edge marked in black"): width and lift.</summary>
		public const float LipBand = 0.07f, LipLift = 1.45f;

		private static double Rise(double z) => (1.0 - Math.Pow(2.5 / z, StepP)) / (1.0 - Math.Pow(2.5 / StepDeepest, StepP));

		private static float Curve(float[] table, double top, float notches)
		{
			if (notches <= 0f) return 0f;
			double z = notches * 0.5;
			if (z <= 2.5) return RM_UnderLiquid.FaceAt(table, notches);
			return (float)(table[5] + (top - table[5]) * Rise(Math.Min(z, StepDeepest)));
		}

		/// <summary>How far south of its top edge a north-wall point at depth <paramref name="notches"/> shows (cells).</summary>
		public static float StepH(float notches) => Curve(StepNorthTable, StepHTop, notches);

		/// <summary>How far in from its edge a side-wall point at depth <paramref name="notches"/> shows (cells).</summary>
		public static float StepW(float notches) => Curve(StepSideTable, StepWTop, notches);

		/// <summary>The darkening of a surface point at depth <paramref name="notches"/>: about 30 % a doubling, at every depth.</summary>
		public static float StepK(float notches) => (float)Math.Pow(1.0 + Math.Max(0f, notches) * 0.5 / StepKScale, -StepKPow);

		/// <summary>A dry floor's brightness at depth <paramref name="d"/> notches under the stepped rule: StepK, anchored so the 2 m
		/// floor keeps its look (shade 0 there) and every other depth draws apart from it.</summary>
		public static float StepFloorBrightness(int d)
		{
			if (d <= 0) return 1f;
			return TerrainColour[4] * StepK(d) / StepK(4);
		}

		/// <summary>The black alpha laid over a dry floor's terrain at depth <paramref name="d"/> so it draws at StepFloorBrightness.</summary>
		public static float StepFloorShade(int d)
		{
			if (d <= 0) return 0f;
			float t = TerrainColour[d < 4 ? d : 4];
			float a = 1f - StepFloorBrightness(d) / t;
			return a > 0f ? (float)Math.Round(a, 5) : 0f;
		}

		/// <summary>The white alpha of the pale lip band on a floor at depth <paramref name="d"/>: lifts its terrain (about half bright
		/// times the terrain colour of its depth band) by LipLift; the floor's depth shade, laid above it, keeps the ratio.</summary>
		public static float StepLipAlpha(int d)
		{
			float ft = 0.5f * TerrainColour[d <= 0 ? 0 : (d < 4 ? d : 4)];
			float a = (LipLift - 1f) * ft / (1f - ft);
			return a <= 0f ? 0f : (a >= 1f ? 1f : a);
		}

		/// <summary>Everything one square draws under the stepped rule, sizes in cells, y DOWN from the north edge (as the twin).</summary>
		public struct StepPlan
		{
			public int D, Zn, Zw, Ze, Znw, Zne;
			public float T, L, R, Lt, Rt, HvL, HvR, Sl, CnwW, CnwH, CneW, CneH;
			public bool LipN, LipW, LipE, DotNw, DotNe, EdgeN, EdgeS, EdgeW, EdgeE;
			public float LipN0, LipN1, LipW0, LipE0;

			/// <summary>The west (or east) wall's width at height y: the strip at the floor below the north face; beside the face,
			/// straight down by hv at the top width, then a mitre to the floor strip.</summary>
			public float SideAt(bool east, float y)
			{
				float full = east ? R : L, top = east ? Rt : Lt, hv = east ? HvR : HvL;
				if (T <= 0f || y >= T) return full;
				if (y < hv) return top;
				if (T - hv <= 1e-6f) return full;
				return top + (full - top) * (y - hv) / (T - hv);
			}
		}

		/// <summary>The plan of a square at depth <paramref name="d"/> (notches) from its neighbours' depths, with
		/// <paramref name="lv"/> notches of liquid standing in it (the faces show down to the waterline only). The twin's plan_cell.</summary>
		public static StepPlan PlanStep(int d, int n, int s, int w, int e, int nw, int ne, float lv)
		{
			StepPlan p = new StepPlan { D = d, Zn = n, Zw = w, Ze = e, Znw = nw, Zne = ne };
			if (d <= 0) return p;
			float de = d - (lv > 0f ? lv : 0f);
			p.T = n < de ? StepH(de) - StepH(n) : 0f;
			p.L = w < de ? StepW(de) - StepW(w) : 0f;
			p.R = e < de ? StepW(de) - StepW(e) : 0f;
			p.Lt = n < de && w < n ? StepW(n) - StepW(w) : 0f;
			p.Rt = n < de && e < n ? StepW(n) - StepW(e) : 0f;
			p.HvL = n < de && w > n ? StepH(Math.Min(w, de)) - StepH(n) : 0f;
			p.HvR = n < de && e > n ? StepH(Math.Min(e, de)) - StepH(n) : 0f;
			p.Sl = s < d ? RM_WallFaceMath.SouthLining(d - s) : 0f;
			if (n >= d && w >= d && nw < de)
			{
				p.CnwW = StepW(de) - StepW(nw);
				p.CnwH = StepH(de) - StepH(nw);
			}
			if (n >= d && e >= d && ne < de)
			{
				p.CneW = StepW(de) - StepW(ne);
				p.CneH = StepH(de) - StepH(ne);
			}
			p.LipN = n < d;
			p.LipN0 = p.Lt;
			p.LipN1 = 1f - p.Rt;
			p.LipW = w < d;
			p.LipW0 = n < d ? p.HvL : 0f;
			p.LipE = e < d;
			p.LipE0 = n < d ? p.HvR : 0f;
			p.DotNw = n >= d && w >= d && nw < d;
			p.DotNe = n >= d && e >= d && ne < d;
			p.EdgeN = n > d;
			p.EdgeS = s > d;
			p.EdgeW = w > d;
			p.EdgeE = e > d;
			return p;
		}

		/// <summary>The depth (notches) a point casts from: a wall point stands at its wall's TOP, a floor point at its floor. The
		/// point is (<paramref name="x"/>, <paramref name="y"/>) cells from the north-west corner of the centre square of the 5x5
		/// window <paramref name="win"/> (depths in notches, north row first; y down), within one square of the centre.</summary>
		public static float PointTop(int[] win, float x, float y)
		{
			int c = (int)Math.Floor(x), r = (int)Math.Floor(y);
			int D(int rr, int cc) => win[(rr + 2) * 5 + (cc + 2)];
			int d = D(r, c);
			if (d <= 0) return 0f;
			StepPlan p = PlanStep(d, D(r - 1, c), D(r + 1, c), D(r, c - 1), D(r, c + 1), D(r - 1, c - 1), D(r - 1, c + 1), 0f);
			float fx = x - c, fy = y - r;
			if (p.CneW > 0f && 1f - fx < p.CneW && fy < p.CneH - Math.Min(p.CneW, p.CneH) * (1f - fx) / p.CneW) return p.Zne;
			if (p.CnwW > 0f && fx < p.CnwW && fy < p.CnwH - Math.Min(p.CnwW, p.CnwH) * fx / p.CnwW) return p.Znw;
			if (1f - fx < p.SideAt(true, fy)) return p.Ze;
			if (fx < p.SideAt(false, fy)) return p.Zw;
			if (fy < p.T) return p.Zn;
			return d;
		}

		private static float Height(float notches) => notches <= 0f ? 0f : -ShadowK * (float)Math.Pow(notches * 0.5, ShadowPow);

		/// <summary>1 lit .. 0 in shadow at a point (<paramref name="fx"/>, <paramref name="fy"/>) of the centre square of
		/// <paramref name="win"/> (y down): a march toward the sun over the heights, at a slope of 1, so a drop from a to b casts
		/// 0.15 x (b^0.7 - a^0.7) squares (metres) past the face's foot. Only a higher point casts. The twin's lit_at.</summary>
		public static float Lit(int[] win, float fx, float fy)
		{
			float h0 = Height(PointTop(win, fx, fy));
			double a = SunAzimuth * Math.PI / 180.0;
			float dx = (float)Math.Sin(a), dy = -(float)Math.Cos(a);
			float reach = ShadowK * (float)Math.Pow(StepDeepest, ShadowPow) + MarchStep;
			float excess = -1e9f;
			for (int k = 1; k * MarchStep <= reach; k++)
			{
				float s = k * MarchStep;
				float hq = Height(PointTop(win, fx + dx * s, fy + dy * s));
				if (hq > h0 + 1e-6f && hq - h0 - s > excess) excess = hq - h0 - s;
			}
			float lit = 0.5f - excess / (2f * Penumbra);
			return lit <= 0f ? 0f : (lit >= 1f ? 1f : lit);
		}

		/// <summary>Can any point of the centre square of <paramref name="win"/> lie in a cast shadow? Only when a square within reach
		/// toward the sun is shallower (else every point it marches over stands as deep or deeper).</summary>
		public static bool MayBeShaded(int[] win)
		{
			int d = win[12];
			for (int r = -2; r <= 1; r++)
			{
				for (int c = -2; c <= 1; c++)
				{
					if (win[(r + 2) * 5 + (c + 2)] < d) return true;
				}
			}
			return false;
		}

		/// <summary>A face's light against a lit floor: <paramref name="facing"/> 0 a north wall (faces south), 1 a west wall (faces
		/// east), 2 an east wall (faces west). Lambert by facing, with the sky and bounce light a wall in shade still sees.</summary>
		public static float FaceLight(int facing)
		{
			double a = SunAzimuth * Math.PI / 180.0, e = SunElevation * Math.PI / 180.0;
			double sx = Math.Cos(e) * Math.Sin(a), sy = Math.Cos(e) * Math.Cos(a), sz = Math.Sin(e);
			double nx = facing == 1 ? 1.0 : (facing == 2 ? -1.0 : 0.0), ny = facing == 0 ? -1.0 : 0.0;
			double flat = Ambient + Direct * sz;
			return (float)((WallAmbient + Direct * Math.Max(0.0, nx * sx + ny * sy)) / flat);
		}

		/// <summary>How much darker a floor in full shadow is than a lit one (the black alpha of a full shadow).</summary>
		public static float ShadowDark => (float)(1.0 - Ambient / (Ambient + Direct * Math.Sin(SunElevation * Math.PI / 180.0)));

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
