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
		/// <summary>Floor terrain colour by depth band (FlowWorks_Terrain.xml: plain Gravel, 0.78, 0.69, 0.64; every depth past 2 m
		/// is RM_Channel_Superdeep's 0.64) [the defs]. Deep and Superdeep were lifted from 0.58 and 0.38
		/// (RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR) so a black shade can draw the stepped rule's lifted ladder; the
		/// FloorBrightness law keeps its brightness (its shade takes the difference).</summary>
		private static readonly float[] TerrainColour = { 1f, 1f, 0.78f, 0.69f, 0.64f };

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

		/// <summary>The colour (red channel) of the floor terrain a dry square at depth <paramref name="d"/> notches lies on.</summary>
		public static float FloorTerrainColour(int d) => TerrainColour[d <= 0 ? 0 : (d < 4 ? d : 4)];

		/// <summary>The floor's brightness at depth <paramref name="d"/> notches (1 = undug ground).</summary>
		public static float FloorBrightness(int d)
		{
			if (d <= 0) return 1f;
			if (d <= 4) return BrightnessShallow[d];
			double r = 1.0 - FloorLogK * (Math.Log(d / 4.0) / Math.Log(2.0));
			return BrightnessShallow[4] * (float)Math.Max(FloorMin, r);
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

		/// <summary>The depth shade's colour, one byte for red, green and blue: pure black. Only black makes a floor of colour t under
		/// alpha FloorShade(d) draw at (1 - alpha) x t, which is FloorBrightness. A dark brown (10, 8, 7) did not: over the dark deep
		/// floor (about 34 of 255) it drew the 16 m floor at 0.535 of the 2 m floor where the law says 0.34, and 3 m at 0.945 where
		/// the law says 0.871, alike to the eye [measured live, ArchBig 2026-11-22].</summary>
		public const byte FloorTint = 0;

		/// <summary>What a floor of brightness <paramref name="t"/> (0 to 1) draws at under the depth shade at depth
		/// <paramref name="d"/> notches: the game's alpha blend of FloorTint over it.</summary>
		public static float FloorDrawn(float t, int d)
		{
			float a = FloorShade(d);
			return (1f - a) * t + a * (FloorTint / 255f);
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
		//   • two offset functions of depth, StepH (north face, today's table x 0.7) and StepW (side strip, today's) to 2.5 m, rising on to 20 m;
		//   • a wall between a shallow floor a and a deep floor b shows H(b) - H(a) / W(b) - W(a), so a riser's top meets each side
		//     wall at that wall's depth-a line, never at the ground rim, and the side wall runs on unbroken above it;
		//   • every surface darkens by StepK of its depth (a multiplier: it holds over any floor terrain laid later);
		//   • a fixed sun from the north-west lights the faces by their facing and casts a shadow past each face's foot.

		// The north face (RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR, the art judge 2026-11-23: "carry 3 m against 4 m
		// by the wall"; twin design/specs/2026-11-23-pit-floor-depth-ladder/ladder.py): today's table at 0.7 to 2 m, then StepHSlope a
		// metre to 4 m, then StepHLog a doubling to 20 m. His L's 4 m north arm keeps 0.475 of a square ("the lower-right northern inner
		// shelf is incredibly narrow" at 0.26, 2026-11-22); a one-square north shelf keeps 0.4 in view to 8 m.
		private static readonly float[] StepNorthTable = { 0f, 0.7f * 0.12f, 0.7f * 0.23f, 0.7f * 0.35f, 0.7f * 0.50f };
		private const double StepHSlope = 0.085, StepHLog = 0.078;
		// The tone (the same twin): K(z) = KFloor + (1 - KFloor)(1 + z / KScale)^-KPow, a multiplier on undug ground. The 2 m floor
		// at 0.63 (it was 0.38, and 3 m to 16 m fit in a dozen grey levels); never under KFloor, so the deepest floor keeps its grain.
		private const double KFloor = 0.22, KScale = 1.6, KPow = 0.8;
		private static readonly float[] StepSideTable = { 0f, 0.06f, 0.11f, 0.17f, 0.23f, 0.29f };
		private const double StepWTop = 0.46, StepP = 0.6, StepDeepest = 20.0;

		/// <summary>The sun: compass degrees the light comes from (315 = north-west, option B of the pick) and its elevation.</summary>
		public const float SunAzimuth = 315f, SunElevation = 55f;
		private const float Ambient = 0.55f, Direct = 0.45f, WallAmbient = 0.85f;
		/// <summary>A face darkens toward its foot by this share (a crisp foot, never a gradient that melts into the floor).</summary>
		public const float FaceFade = 0.30f;
		private const float ShadowK = 0.12f, ShadowPow = 0.7f, Penumbra = 0.04f, MarchStep = 1f / 32f;
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
		public static float StepH(float notches)
		{
			if (notches <= 0f) return 0f;
			if (notches <= 4f) return RM_UnderLiquid.FaceAt(StepNorthTable, notches);
			double z = notches * 0.5, h2 = StepNorthTable[4];
			if (z <= 4.0) return (float)(h2 + StepHSlope * (z - 2.0));
			return (float)(h2 + 2.0 * StepHSlope + StepHLog * Math.Log(Math.Min(z, StepDeepest) / 4.0, 2.0));
		}

		/// <summary>How far in from its edge a side-wall point at depth <paramref name="notches"/> shows (cells).</summary>
		public static float StepW(float notches) => Curve(StepSideTable, StepWTop, notches);

		/// <summary>The tone of a surface point at depth <paramref name="notches"/> (a multiplier on undug ground; 1 at the ground).</summary>
		public static float StepK(float notches) => (float)(KFloor + (1.0 - KFloor) * Math.Pow(1.0 + Math.Max(0f, notches) * 0.5 / KScale, -KPow));

		/// <summary>A dry floor's brightness at depth <paramref name="d"/> notches under the stepped rule: StepK, the tone a face top at
		/// that depth also takes.</summary>
		public static float StepFloorBrightness(int d)
		{
			if (d <= 0) return 1f;
			return StepK(d);
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
			// any odd square window (5x5 for the golden tables, 7x7 from the walls layer); a read past its edge takes the edge square
			// (a slope-2 march reaches 2 squares and reads their neighbours: past a 5x5 it threw, live 2026-11-22, and the whole
			// section drew no relief)
			int n = win.Length == 49 ? 7 : 5, half = n / 2;
			int D(int rr, int cc)
			{
				rr = rr < -half ? -half : (rr > half ? half : rr);
				cc = cc < -half ? -half : (cc > half ? half : cc);
				return win[(rr + half) * n + (cc + half)];
			}
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
		/// 0.12 x (b^0.7 - a^0.7) squares (metres) past the face's foot. Only a higher point casts. The twin's lit_at.</summary>
		public static float Lit(int[] win, float fx, float fy) => Lit(win, fx, fy, FixedSun);

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

		// ---- The pit's sun is the game's own (RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM, step 3) ----
		// The baked shadow follows vanilla's one shadow vector, _CastVect (SkyManager.SkyManagerUpdate sets it every frame: x, z the
		// shadow's direction and length per unit of height, w GenCelestial.CurShadowStrength; by day the sun, by night the moon, 0
		// round dusk and dawn; a pinned-sun map overrides it). So every shadow on a map points one way, on Utinni and elsewhere.

		/// <summary>The light a pit square's relief is drawn under: (Dx, Dy) the unit direction TOWARD the light (x east, y DOWN = south),
		/// Slope the shadow length against the noon sun's (1 = the 55 degree sun of the pick), Strength 0 (no directional light) .. 1.</summary>
		public struct PitSun
		{
			public float Dx, Dy, Slope, Strength;
		}

		/// <summary>Vanilla's noon cast vector is (0, -1.5) (GenCelestial.GetLightSourceInfo): that length is slope 1.</summary>
		public const float NoonCastLength = 1.5f;
		/// <summary>The march reads a 5x5 window: from any point of the centre square it may reach 2 squares, so the slope stops at 2
		/// (a dawn vector is about 4.7 noon lengths; past 2 the shadow is drawn 2 long).</summary>
		public const float MinSlope = 0.5f, MaxSlope = 2f;
		/// <summary>Re-bake steps: the sun's compass turns by 15 degrees, the slope by 0.25, the strength and the sky glow by 0.1.</summary>
		public const float AzimuthStep = 15f, SlopeStep = 0.25f, StrengthStep = 0.1f, SkyStep = 0.1f;

		/// <summary>The sun from compass degrees, slope and strength.</summary>
		public static PitSun MakeSun(float azimuthDeg, float slope, float strength)
		{
			double a = azimuthDeg * Math.PI / 180.0;
			return new PitSun { Dx = (float)Math.Sin(a), Dy = -(float)Math.Cos(a), Slope = slope, Strength = strength };
		}

		/// <summary>The fixed north-west sun of the pick (option B), at full strength: the golden tables' sun, and the sun of a layer
		/// that has not yet read the game's.</summary>
		public static readonly PitSun FixedSun = MakeSun(SunAzimuth, 1f, 1f);

		private static float Clamp01(float v) => v <= 0f ? 0f : (v >= 1f ? 1f : v);

		/// <summary>The sun casting vanilla's shadow vector (<paramref name="vx"/>, <paramref name="vz"/>) (x east, z north) at strength
		/// <paramref name="strength"/>: the light comes from the opposite way, as long as the vector is against noon's.</summary>
		public static PitSun SunFromCastVect(float vx, float vz, float strength)
		{
			float len = (float)Math.Sqrt(vx * vx + vz * vz);
			if (len < 1e-4f)
			{
				return new PitSun { Dx = FixedSun.Dx, Dy = FixedSun.Dy, Slope = 1f, Strength = 0f };
			}
			float slope = len / NoonCastLength;
			slope = slope < MinSlope ? MinSlope : (slope > MaxSlope ? MaxSlope : slope);
			return new PitSun { Dx = -vx / len, Dy = vz / len, Slope = slope, Strength = Clamp01(strength) };
		}

		private static void Snap(float vx, float vz, float strength, out int az, out int sl, out int st)
		{
			PitSun s = SunFromCastVect(vx, vz, strength);
			double deg = Math.Atan2(s.Dx, -s.Dy) * 180.0 / Math.PI;
			az = ((int)Math.Round(deg / AzimuthStep) % 24 + 24) % 24;
			sl = (int)Math.Round(s.Slope / SlopeStep);
			st = (int)Math.Round(s.Strength / StrengthStep);
		}

		/// <summary>The sun the layer bakes: the game's, snapped to the re-bake steps (so the bake agrees with its key).</summary>
		public static PitSun QuantizedSun(float vx, float vz, float strength)
		{
			Snap(vx, vz, strength, out int az, out int sl, out int st);
			return MakeSun(az * AzimuthStep, sl * SlopeStep, Clamp01(st * StrengthStep));
		}

		/// <summary>One number per baked look: the snapped sun and the snapped sky glow. A change re-bakes the map's pit relief.</summary>
		public static int SunKey(float vx, float vz, float strength, float skyGlow)
		{
			Snap(vx, vz, strength, out int az, out int sl, out int st);
			int sky = (int)Math.Round(Clamp01(skyGlow) / SkyStep);
			return ((az * 16 + sl) * 16 + st) * 16 + sky;
		}

		/// <summary>How much of the sun's directional light reaches a square (0 .. 1): none under a roof (Direct Sun: a roof covers at
		/// every angle); none where lamp light outshines the sky (so no shadow points toward a lamp, and a lamp-lit floor is not left in
		/// a sun shadow); full while the lamp gives at most half the sky's glow. Vanilla's lamp glow is at most 0.5 (GlowGrid.GroundGlowAt),
		/// so by day (sky 1) a lamp changes nothing.</summary>
		public static float SkyShare(bool roofed, float skyGlow, float artificialGlow)
		{
			if (roofed)
			{
				return 0f;
			}
			if (artificialGlow <= 0f)
			{
				return 1f;
			}
			if (skyGlow <= 0f)
			{
				return 0f;
			}
			return Clamp01(2f * (skyGlow - artificialGlow) / skyGlow);
		}

		/// <summary>The sun as it reaches a square that gets <paramref name="share"/> of it.</summary>
		public static PitSun Reached(PitSun sun, float share)
		{
			sun.Strength *= Clamp01(share);
			return sun;
		}

		private static double Elevation(PitSun sun) => Math.Atan(Math.Tan(SunElevation * Math.PI / 180.0) / Math.Max(1e-3, sun.Slope));

		/// <summary>1 lit .. 0 in shadow at a point (<paramref name="fx"/>, <paramref name="fy"/>) of the centre square of
		/// <paramref name="win"/> (y down) under <paramref name="sun"/>: a march toward the sun over the heights; a drop from a to b casts
		/// 0.12 x (b^0.7 - a^0.7) x Slope squares past the face's foot. Only a higher point casts.</summary>
		public static float Lit(int[] win, float fx, float fy, PitSun sun)
		{
			float h0 = Height(PointTop(win, fx, fy));
			float slope = sun.Slope < MinSlope ? MinSlope : (sun.Slope > MaxSlope ? MaxSlope : sun.Slope);
			float reach = ShadowK * (float)Math.Pow(StepDeepest, ShadowPow) * slope + MarchStep;
			float excess = -1e9f;
			for (int k = 1; k * MarchStep <= reach; k++)
			{
				float s = k * MarchStep;
				float hq = Height(PointTop(win, fx + sun.Dx * s, fy + sun.Dy * s));
				if (hq > h0 + 1e-6f && hq - h0 - s / slope > excess) excess = hq - h0 - s / slope;
			}
			float lit = 0.5f - excess / (2f * Penumbra);
			return lit <= 0f ? 0f : (lit >= 1f ? 1f : lit);
		}

		/// <summary>A face's light against a lit floor under <paramref name="sun"/>: the sky light a wall always sees, plus the sun's
		/// direct light by its facing, times the strength. At strength 0 every face draws as a face in shade.</summary>
		public static float FaceLight(int facing, PitSun sun)
		{
			double e = Elevation(sun), ce = Math.Cos(e);
			double sx = ce * sun.Dx, sy = -ce * sun.Dy, sz = Math.Sin(e);
			double nx = facing == 1 ? 1.0 : (facing == 2 ? -1.0 : 0.0), ny = facing == 0 ? -1.0 : 0.0;
			double flat = Ambient + Direct * sz;
			return (float)((WallAmbient + Direct * Clamp01(sun.Strength) * Math.Max(0.0, nx * sx + ny * sy)) / flat);
		}

		/// <summary>The black alpha of a full cast shadow under <paramref name="sun"/> (0 at strength 0).</summary>
		public static float ShadowDarkFor(PitSun sun)
		{
			double sz = Math.Sin(Elevation(sun));
			return (float)((1.0 - Ambient / (Ambient + Direct * sz)) * Clamp01(sun.Strength));
		}

		/// <summary>Can any point of the centre square lie in a cast shadow under <paramref name="sun"/>? Only with some strength, and only
		/// when a square of the window is shallower (else every point a march reaches stands as deep or deeper).</summary>
		public static bool MayBeShaded(int[] win, PitSun sun)
		{
			if (sun.Strength <= 0f)
			{
				return false;
			}
			int d = win[win.Length / 2];
			for (int i = 0; i < win.Length; i++)
			{
				if (win[i] < d) return true;
			}
			return false;
		}

		// ── one water surface (RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE; twin model/water_surface.py) ────────────
		// Owner, walk 2026-11-25: "Station 6 still shows odd pit walls under water ... Look at the corners" and "I suspect you're
		// applying multiple layers over each other instead of calculating a single one". The census (jawa/cell_draw_census) counted
		// nine sheet pieces at alpha 0..229 on one square of station 22, beside the deep tint and a wall band, and the drowned walls drawn
		// as plain rectangles. The rule: a square under a clear liquid is drawn as the DRY pit, and over it lies ONE sheet, one colour
		// and one alpha, over the dry pit cut by the waterline on each face. The pieces never overlap.

		/// <summary>Which half-plane of a face lies under the waterline: the north face below z = 1 - cut, a west face (or a north-west
		/// corner piece) beyond x = cut, an east face (or north-east piece) short of x = 1 - cut.</summary>
		public const int CutNorth = 0, CutWest = 1, CutEast = 2;

		/// <summary>The part of polygon <paramref name="xz"/> (x, z pairs; z north, square-local) that lies under the waterline of a
		/// face of kind <paramref name="kind"/> (cut <paramref name="cut"/> cells from the face's edge, CutNorth/West/East) and inside
		/// the wet window [wx0, wx1] x [wz0, wz1]; added to <paramref name="into"/> when it has area. A kind below 0 cuts nothing (the
		/// floor).</summary>
		public static void AddUnderLine(float[] xz, int kind, float cut, float wx0, float wx1, float wz0, float wz1, System.Collections.Generic.List<float[]> into)
		{
			float[] q = xz;
			if (kind == CutNorth) q = ClipHalf(q, 1, 1f - cut, false);
			else if (kind == CutWest) q = ClipHalf(q, 0, cut, true);
			else if (kind == CutEast) q = ClipHalf(q, 0, 1f - cut, false);
			q = ClipHalf(q, 0, wx0, true);
			q = ClipHalf(q, 0, wx1, false);
			q = ClipHalf(q, 1, wz0, true);
			q = ClipHalf(q, 1, wz1, false);
			if (q.Length >= 6 && PolyArea(q) > 1e-6f)
			{
				into.Add(q);
			}
		}

		/// <summary>Sutherland-Hodgman against one axis-aligned half-plane: keep axis (0 x, 1 z) &gt;= bound when <paramref name="keepAbove"/>,
		/// else &lt;= bound.</summary>
		private static float[] ClipHalf(float[] q, int axis, float bound, bool keepAbove)
		{
			int n = q.Length / 2;
			if (n == 0) return q;
			var o = new System.Collections.Generic.List<float>(q.Length + 4);
			for (int i = 0; i < n; i++)
			{
				int j = (i + 1) % n;
				float pa = q[2 * i + axis], qa = q[2 * j + axis];
				bool pin = keepAbove ? pa >= bound : pa <= bound, qin = keepAbove ? qa >= bound : qa <= bound;
				if (pin)
				{
					o.Add(q[2 * i]);
					o.Add(q[2 * i + 1]);
				}
				if (pin != qin)
				{
					float t = (bound - pa) / (qa - pa);
					o.Add(q[2 * i] + (q[2 * j] - q[2 * i]) * t);
					o.Add(q[2 * i + 1] + (q[2 * j + 1] - q[2 * i + 1]) * t);
				}
			}
			return o.ToArray();
		}

		/// <summary>The area of polygon <paramref name="xz"/> (x, z pairs).</summary>
		public static float PolyArea(float[] xz)
		{
			int n = xz.Length / 2;
			float a = 0f;
			for (int i = 0; i < n; i++)
			{
				int j = (i + 1) % n;
				a += xz[2 * i] * xz[2 * j + 1] - xz[2 * j] * xz[2 * i + 1];
			}
			return Math.Abs(a) * 0.5f;
		}

		/// <summary>The face polygons of a stepped plan, as the walls layer draws them (x, z pairs, z north), with each one's cut kind:
		/// the north face, the west and east faces, the north-west and north-east corner pieces.</summary>
		public static void ReliefFaces(StepPlan p, System.Collections.Generic.List<float[]> polys, System.Collections.Generic.List<int> kinds)
		{
			float t = p.T;
			if (t > 0f)
			{
				polys.Add(new[] { p.Lt, 1f, 1f - p.Rt, 1f, 1f - p.Rt, 1f - p.HvR, 1f - p.R, 1f - t, p.L, 1f - t, p.Lt, 1f - p.HvL });
				kinds.Add(CutNorth);
			}
			for (int side = 0; side < 2; side++)
			{
				bool east = side == 1;
				float full = east ? p.R : p.L, top = east ? p.Rt : p.Lt, hv = east ? p.HvR : p.HvL;
				if (!(full > 0f)) continue;
				float[] q = t <= 0f
					? new[] { 0f, 0f, 0f, 1f, full, 1f, full, 0f }
					: new[] { 0f, 0f, 0f, 1f, top, 1f, top, 1f - hv, full, 1f - t, full, 0f };
				if (east)
				{
					for (int i = 0; i < q.Length; i += 2) q[i] = 1f - q[i];
				}
				polys.Add(q);
				kinds.Add(east ? CutEast : CutWest);
			}
			float[] xz = new float[8];
			if (p.CnwW > 0f)
			{
				CornerPoly(false, p.CnwW, p.CnwH, xz);
				polys.Add((float[])xz.Clone());
				kinds.Add(CutWest);
			}
			if (p.CneW > 0f)
			{
				CornerPoly(true, p.CneW, p.CneH, xz);
				polys.Add((float[])xz.Clone());
				kinds.Add(CutEast);
			}
		}

		/// <summary>The cut of a face kind in the plan at the liquid's level: how far the dry part reaches from the face's edge.</summary>
		public static float CutOf(StepPlan wet, int kind, int index, int cornerIndexWest, int cornerIndexEast)
		{
			if (kind == CutNorth) return wet.T;
			if (index == cornerIndexWest) return wet.CnwW;
			if (index == cornerIndexEast) return wet.CneW;
			return kind == CutWest ? wet.L : wet.R;
		}

		/// <summary>The ONE sheet over a square at depth <paramref name="d"/> with <paramref name="lv"/> notches of clear liquid under the
		/// stepped rule: the dry plan's floor whole, and each dry face cut at the waterline of the plan at the liquid's level; inside
		/// the wet window (a shut sluice's wet half, SluiceHalf; else the whole square). Polygons (x, z pairs, z north) into
		/// <paramref name="into"/>, never overlapping; none when no liquid stands. Returns how many.</summary>
		public static int SheetPieces(int d, int n, int s, int w, int e, int nw, int ne, float lv, float wx0, float wx1, float wz0, float wz1,
			System.Collections.Generic.List<float[]> into)
		{
			into.Clear();
			if (!(lv > 0f) || d <= 0) return 0;
			StepPlan full = PlanStep(d, n, s, w, e, nw, ne, 0f);
			StepPlan wet = PlanStep(d, n, s, w, e, nw, ne, lv);
			float[] r = new float[8];
			int nr = FloorRects(full.L, full.R, full.T, full.CnwW, full.CnwH, full.CneW, full.CneH, r);
			for (int i = 0; i < nr; i++)
			{
				float x0 = r[4 * i], z0 = r[4 * i + 1], x1 = r[4 * i + 2], z1 = r[4 * i + 3];
				AddUnderLine(new[] { x0, z0, x0, z1, x1, z1, x1, z0 }, -1, 0f, wx0, wx1, wz0, wz1, into);
			}
			var polys = new System.Collections.Generic.List<float[]>(5);
			var kinds = new System.Collections.Generic.List<int>(5);
			ReliefFaces(full, polys, kinds);
			int cw = full.CnwW > 0f ? polys.Count - (full.CneW > 0f ? 2 : 1) : -1;
			int ce = full.CneW > 0f ? polys.Count - 1 : -1;
			for (int i = 0; i < polys.Count; i++)
			{
				AddUnderLine(polys[i], kinds[i], CutOf(wet, kinds[i], i, cw, ce), wx0, wx1, wz0, wz1, into);
			}
			return into.Count;
		}

		/// <summary>The part of a shut sluice's square that carries the sheet. A gate turned east or west (rot 1, 3: the side view) parts
		/// its west half (low) from its east half (high); a gate turned north or south (rot 0, 2) parts south (low) from north (high).
		/// <paramref name="wetLow"/> / <paramref name="wetHigh"/>: the square across that side holds liquid. Only one wet side halves it.</summary>
		public static void SluiceHalf(int rot, bool wetLow, bool wetHigh, out float wx0, out float wx1, out float wz0, out float wz1)
		{
			wx0 = wz0 = 0f;
			wx1 = wz1 = 1f;
			if (wetLow == wetHigh) return;
			float a = wetLow ? 0f : 0.5f, b = wetLow ? 0.5f : 1f;
			if (rot == 1 || rot == 3)
			{
				wx0 = a;
				wx1 = b;
			}
			else
			{
				wz0 = a;
				wz1 = b;
			}
		}

		/// <summary>A face-on sluice (rot 0, 2: its leaf spans east-west and the camera sees its south face) whose south side is a
		/// drained dug square while its north side still holds liquid: the water stands behind it, so its face draws dry (station 10,
		/// walk 2026-11-25). The side view (rot 1, 3) never shows liquid over it (RM_UnderLiquid.GateShowsLiquid).</summary>
		public static bool GateFaceDry(int rot, bool southDrained, bool northDrained)
		{
			return (rot == 0 || rot == 2) && southDrained && !northDrained;
		}

		/// <summary>A dry dug square beside a square of liquid terrain prints its own floor, so vanilla's edge fade of that liquid (render
		/// precedence 39x over a dug floor's 32x) never lies over it: the drained side of a sluice, stations 7 to 10 (walk 2026-11-25).</summary>
		public static bool ReprintsFloor(bool dug, bool holdsLiquid, bool besideLiquidTerrain)
		{
			return dug && !holdsLiquid && besideLiquidTerrain;
		}

		/// <summary>The sheet's one alpha: the wet-ground darkening (<paramref name="wetAlpha"/>, black) under the liquid's own overlay
		/// (alpha 1 - <paramref name="seen"/>), composed as one overlay.</summary>
		public static float SheetAlpha(float seen, float wetAlpha)
		{
			float sa = 1f - Clamp01(seen);
			return 1f - (1f - Clamp01(wetAlpha)) * (1f - sa);
		}

		/// <summary>The share of the body colour in that one overlay (its colour is body x share): the liquid's alpha over the whole.</summary>
		public static float SheetBodyShare(float seen, float wetAlpha)
		{
			float a = SheetAlpha(seen, wetAlpha);
			return a > 0f ? (1f - Clamp01(seen)) / a : 0f;
		}

	}
}
