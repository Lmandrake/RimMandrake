namespace RimMandrake.FlowWorks
{
	/// <summary>EXCAVATION_WALL_ART_1 + FLOWWORKS_VISUAL_PRINCIPLES_1 — the geometry and shading numbers of the
	/// wall faces, the near-lip occluder and the scorch fade (Verse-free, selftested).
	///
	/// Owner, 2026-10-05 (principle 1): <i>"The canals, when dug deep enough to hold a man, should have the same
	/// perspective appearance as the walls do when viewed from above (tall enough to stop a man). The deeper canals
	/// should be even more extended in appearance."</i>
	///
	/// Vanilla's convention, MEASURED from Wall_Atlas_Smooth / Rock_Atlas (resources.assets, 2026-10-05): the
	/// camera looks down from the south, so a wall shows a LIT south face about a quarter of a cell tall and
	/// narrower lit side faces about an eighth of a cell wide, outlined dark at the top edge. A cut is the same
	/// thing inside out: the inner face of the NORTH bank is the one the camera sees, hanging down from the far
	/// rim; east/west banks show as narrow side faces; the south bank's face points away and is hidden behind
	/// the near lip — which is also what hides the lower body of a pawn standing deep in the cut.
	///
	/// So: D3 (deep enough to hold a person) gets a wall-height face, D4 a taller one, every level visibly more.
	/// PROVISIONAL numbers, judged on the review sheet art_source/visual_principles_2026-10-05.</summary>
	public static class RM_WallFaceMath
	{
		/// <summary>North-face band height (cells) by exposed drop 1..4. D3 = a vanilla wall's face (~0.25) plus
		/// its rim line; D4 "even more extended".</summary>
		public static readonly float[] NorthByDrop = { 0f, 0.12f, 0.23f, 0.35f, 0.50f };

		/// <summary>Side-face strip width (cells) by exposed drop 1..4 (vanilla side face ~0.125 at wall height).</summary>
		public static readonly float[] SideByDrop = { 0f, 0.06f, 0.11f, 0.17f, 0.23f };

		public const float NorthMax = 0.50f;
		public const float SideMax = 0.23f;

		/// <summary>Brightness multiplier at the TOP of a camera-facing face (vanilla draws those as the light tone).</summary>
		public const float FaceTopLight = 1.45f;

		/// <summary>MEASURED 2026-10-05 from the owner's in-game shot of steel walls round a D4 pit (cell ~126 px): flat
		/// dark top 52, south bevel band 96 (x1.85) and 44 px = 0.35 cell, side bevels 67 (x1.29) and ~22 px = 0.17 cell,
		/// mitred 45-degree ends, and a pure-black outline ~5 px = 0.04 cell on EVERY edge. The pit copies all of it:
		/// D3 face 0.35 and side bevel 0.17 = the wall's; the outline closes all four edges.</summary>
		public const float WallFaceLight = 1.85f;
		public const float WallSideLight = 1.29f;

		/// <summary>Thickness (cells) of the black outline on the far and side edges (vanilla's wall outline).</summary>
		public const float RimLine = 0.04f;

		/// <summary>Owner, 2026-10-05, looking at a pit in game: <i>"We need more of a black-lining on the southern edge
		/// of the pits so the human can see what is there."</i> The near (south) bank's face points away from the camera
		/// and is not drawn, so the pit's near edge gets a dark LINING instead: thicker than the north rim line and
		/// growing with the drop (D1 0.045 .. D4 0.08 cells), so all four edges read as one closed outline.</summary>
		public static readonly float[] SouthLiningByDrop = { 0f, 0.045f, 0.055f, 0.065f, 0.08f };

		/// <summary>Thickness (cells) of the outline along each side bank's outer edge (= the rim line).</summary>
		public const float SideLine = 0.04f;

		public static float SouthLining(int drop)
		{
			if (drop <= 0) return 0f;
			return SouthLiningByDrop[drop >= SouthLiningByDrop.Length ? SouthLiningByDrop.Length - 1 : drop];
		}

		/// <summary>Thickness (cells) of the contact shadow where a face meets the floor or the liquid.</summary>
		public const float ContactShadow = 0.06f;

		/// <summary>How much of a sunk pawn the near lip hides: 0.85 = a faint ghost stays so he can still be found.
		/// Overridden by the Mod Setting.</summary>
		public const float DefaultLipOcclusion = 0.85f;

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
			return NorthByDrop[exposedDrop >= NorthByDrop.Length ? NorthByDrop.Length - 1 : exposedDrop];
		}

		public static float SideFaceWidth(int exposedDrop)
		{
			if (exposedDrop <= 0) return 0f;
			return SideByDrop[exposedDrop >= SideByDrop.Length ? SideByDrop.Length - 1 : exposedDrop];
		}

		/// <summary>0..1 darkness at the FOOT of a face for a cell of total depth D (deeper = darker), so even two
		/// faces of equal height read as different depths.</summary>
		public static float FootDarkness(int depth)
		{
			if (depth <= 0) return 0f;
			float d = 0.35f + 0.15f * depth;
			return d > 0.95f ? 0.95f : d;
		}

		/// <summary>The x inset of a north face's bottom edge where it meets a side bevel: the mitre. Vanilla's bevel
		/// corners are 45 degrees, so the face's lower corner steps in by the bevel width.</summary>
		public static float MitreInset(float sideWidth, float faceHeight)
		{
			if (sideWidth <= 0f || faceHeight <= 0f) return 0f;
			return sideWidth;
		}

		/// <summary>Brightness multiplier at the FOOT of a lit face: the top is <see cref="FaceTopLight"/>, the foot
		/// is ambient-occluded more the deeper the cut (D1 0.98 .. D4 0.80).</summary>
		public static float FaceFootLight(int depth)
		{
			if (depth <= 0) return FaceTopLight;
			int d = depth > 4 ? 4 : depth;
			return 1.04f - 0.06f * d;
		}

		/// <summary>The near-lip occluder for a pawn: given the z of the lip edge (the north edge of the first cell
		/// south of the pawn that is SHALLOWER than its floor) and the drawn sprite's bottom/top z, the band
		/// [bottom, min(top, lip)] the occluder must cover. Returns false when nothing hangs below the lip.</summary>
		public static bool OccludedBand(float lipZ, float spriteBottomZ, float spriteTopZ, out float z0, out float z1)
		{
			z0 = spriteBottomZ;
			z1 = spriteTopZ < lipZ ? spriteTopZ : lipZ;
			return z1 > z0 + 0.001f;
		}

		/// <summary>PIT_LIP_OCCLUDES_OUTSIDE_1. The near-lip cover is drawn above every pawn, so it must never cover a
		/// pawn that is NOT sunk as deep as the one it hides (one standing on ground or the lip south of the pit,
		/// whose sprite the band overlaps). True when a cover piece [left,right]x[a,b] intersects the drawn rect of
		/// another pawn whose own depth is shallower than the sunk pawn's: that piece must be skipped.</summary>
		public static bool CoverPieceHitsShallowerPawn(float left, float right, float a, float b,
			float otherLeft, float otherRight, float otherBottom, float otherTop, int otherDepth, int sunkDepth)
		{
			if (otherDepth >= sunkDepth) return false;
			return right > otherLeft && left < otherRight && b > otherBottom && a < otherTop;
		}

		// ── scorch (principle 5) ────────────────────────────────────────────

		/// <summary>Remaining scorch strength 0..1 after <paramref name="ageTicks"/>; <paramref name="fadeDays"/> 0 =
		/// never fades. Rain on an unroofed cell ages it <paramref name="rainFactor"/>× faster (the caller passes the
		/// already-weighted age). Quantised to quarters so a fading pit redraws four times, not every tick.</summary>
		public static float ScorchStrength(long ageTicks, float fadeDays)
		{
			if (ageTicks < 0) ageTicks = 0;
			if (!(fadeDays > 0f)) return 1f;
			float t = ageTicks / (fadeDays * 60000f);
			if (t >= 1f) return 0f;
			float s = 1f - t;
			return (float)System.Math.Ceiling(s * 4f) / 4f;
		}

		// ── scorch look, round 3 (owner, 2026-10-06: "those look ridiculous" about black starbursts in a grid; redone
		//    from GPT concept art, Transient/scorch_concept_2026-10-06/). What sells post-fire at this scale: the floor
		//    turns GREY ash with soft char patches heaviest at the walls, the walls carry vertical soot plumes, and the
		//    ground round the rim is smoked in lumpy lobes that feather out ~1-1.5 cells, uneven from side to side.
		//    The grain comes from two textures (RM_Scorch_Ash / RM_Scorch_Soot); these numbers are their coverage. ──

		private static float Smooth(float t)
		{
			if (t <= 0f) return 0f;
			if (t >= 1f) return 1f;
			return t * t * (3f - 2f * t);
		}

		/// <summary>Coverage 0..1 of the ash texture over a burned floor at noise n (0..1): near-total at full scorch,
		/// the noise only thins it a little so the floor reads as ONE burned surface, not spots.</summary>
		public static float AshCover(float s, float n, bool dirt = false)
		{
			if (s <= 0f) return 0f;
			if (s > 1f) s = 1f;
			// round 4 (owner card 2026-10-06): scorched DIRT is its own look — the baked soil shows through its ash
			float a = dirt ? 0.42f + 0.40f * n : 0.80f + 0.20f * n;
			return s * (a > 1f ? 1f : a);
		}

		/// <summary>Coverage 0..1 of the soot/char texture over the ash: heavy within ~0.45 cell of a wall (smooth, so
		/// no inner frame) and in soft patches where the noise runs high. Never a full black floor: the middle of a
		/// low-noise floor is ash.</summary>
		public static float CharCover(float s, float n, float edgeDist, bool dirt = false)
		{
			if (s <= 0f) return 0f;
			if (s > 1f) s = 1f;
			float wall = 1f - Smooth(edgeDist / 0.45f);
			float patch = Smooth((n - (dirt ? 0.38f : 0.44f)) / 0.20f);
			float a = 0.88f * wall;
			float b = (dirt ? 0.9f : 0.80f) * patch;
			return s * (a > b ? a : b);
		}

		/// <summary>Warm rust heat tint (vertex colour) in a band just off the walls, where noise allows: a faint accent.</summary>
		public static float HeatTint(float s, float n, float edgeDist, bool dirt = false)
		{
			if (s <= 0f) return 0f;
			if (dirt)
			{
				// dirt: a reddish-brown bake over much of the floor, strongest a little off the walls, patchy
				float b = edgeDist < 0.08f ? edgeDist / 0.08f : 1f - 0.6f * Smooth((edgeDist - 0.08f) / 0.6f);
				return (s > 1f ? 1f : s) * 0.20f * b * Smooth((n - 0.30f) / 0.3f);
			}
			float band = edgeDist < 0.1f ? edgeDist / 0.1f : 1f - Smooth((edgeDist - 0.1f) / 0.35f);
			return (s > 1f ? 1f : s) * 0.20f * band * Smooth((n - 0.55f) / 0.2f);   // patchy: never a continuous frame
		}

		/// <summary>Black shade over a burned floor by depth (the ash would otherwise make every pit read shallow).</summary>
		public static float AshDepthShade(int depth)
		{
			if (depth <= 0) return 0f;
			return depth >= 4 ? 0.34f : 0.04f + 0.09f * depth;
		}

		/// <summary>Soot coverage on undug ground at <paramref name="dist"/> cells from the burned cut: darkest at the
		/// lip, feathering out over a reach of 0.45..1.4 cells that the low-frequency noise n sets, so the halo is
		/// lobed and uneven, never a ring of even width.</summary>
		public static float HaloCover(float s, float dist, float n)
		{
			if (s <= 0f) return 0f;
			if (s > 1f) s = 1f;
			float reach = 0.45f + 0.95f * n;
			float t = 1f - dist / reach;
			if (t <= 0f) return 0f;
			return s * (0.62f + 0.30f * n) * Smooth(t) * (0.55f + 0.45f * t);   // the lip itself varies too: no even band
		}

		/// <summary>Soot coverage on a wall face at height fraction v (0 foot .. 1 rim) with plume noise p (0..1, stretched
		/// vertically by the caller): a base stain heaviest at the foot, a band under the rim, and vertical plumes.</summary>
		public static float FaceSoot(float s, float v, float p)
		{
			if (s <= 0f) return 0f;
			if (v < 0f) v = 0f;
			if (v > 1f) v = 1f;
			float foot = (1f - v) * (1f - v);
			float rim = v > 0.7f ? (v - 0.7f) / 0.3f : 0f;
			float a = 0.45f + 0.35f * foot + 0.35f * rim + 0.60f * Smooth((p - 0.45f) / 0.25f);
			return (s > 1f ? 1f : s) * (a > 0.95f ? 0.95f : a);
		}

		// ── round 4: drip streaks and debris (owner card 2026-10-06: "All of that plus debris") ──

		/// <summary>How many soot drip-streaks hang from the rim of the far wall over cell (x,z): 3..6, seeded.</summary>
		/// <summary>Drip k's darkness at the rim, 0.45..0.9 — so the row never reads as a comb of equal teeth.</summary>
		public static float DripStrength(int x, int z, int k)
		{
			return 0.45f + 0.45f * Hash01(x * 7 + k, z * 5, 97);
		}

		public static int DripCount(int x, int z)
		{
			return 3 + (int)(Hash01(x, z, 41) * 4f);
		}

		/// <summary>Drip k on cell (x,z): u = position across the cell (0.06..0.94), width in cells (0.03..0.09),
		/// len = fraction of the face height it runs down from the rim (0.35..1).</summary>
		public static void Drip(int x, int z, int k, out float u, out float width, out float len)
		{
			u = 0.06f + 0.88f * Hash01(x, z * 7 + k, 43);
			width = 0.03f + 0.06f * Hash01(x * 3 + k, z, 47);
			len = 0.35f + 0.65f * Hash01(x + k * 11, z, 53);
		}

		/// <summary>Debris pieces on a burned floor cell: 0..4, seeded per cell, fewer as the scorch fades. Seeded from
		/// the cell, so the same pit draws the same debris after every save/load and redraw.</summary>
		public static int DebrisCount(float s, int x, int z)
		{
			if (s <= 0f) return 0;
			int n = (int)(Hash01(x, z, 61) * 5f);   // 0..4
			return (int)System.Math.Round(n * (s > 1f ? 1f : s));
		}

		/// <summary>Piece k on cell (x,z) of a floor <paramref name="hTop"/> deep (z extent): local position, size
		/// in cells, rotation in degrees, char (else ash) and which of <paramref name="variants"/> sprites.</summary>
		public static void DebrisPiece(int x, int z, int k, float hTop, int variants, out float lx, out float lz,
			out float size, out float rot, out bool isChar, out int variant)
		{
			lx = 0.12f + 0.76f * Hash01(x, z * 13 + k, 67);
			lz = 0.10f + (hTop - 0.20f > 0f ? hTop - 0.20f : 0f) * Hash01(x * 5 + k, z, 71);
			isChar = Hash01(x, z + k * 17, 73) < 0.55f;
			size = (isChar ? 0.18f : 0.22f) + 0.16f * Hash01(x + k, z * 3, 79);
			rot = 360f * Hash01(x * 9, z + k, 83);
			variant = (int)(Hash01(x + k * 5, z * 11, 89) * variants);
			if (variant >= variants) variant = variants - 1;
		}

		/// <summary>Deterministic 0..1 from integers (no UnityEngine.Random: the selftest pins it).</summary>
		public static float Hash01(int a, int b, int c)
		{
			unchecked
			{
				uint h = (uint)(a * 73856093) ^ (uint)(b * 19349663) ^ (uint)(c * 83492791);
				h ^= h >> 13;
				h *= 0x5bd1e995;
				h ^= h >> 15;
				return (h & 0xFFFFFF) / 16777216f;
			}
		}

		/// <summary>Char multiplier for a face/floor at scorch strength s: 1 untouched, down to 0.30 at full scorch.</summary>
		public static float ScorchDarken(float s)
		{
			if (s <= 0f) return 1f;
			if (s > 1f) s = 1f;
			return 1f - 0.70f * s;
		}
	}
}
