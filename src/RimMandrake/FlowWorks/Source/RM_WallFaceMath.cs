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

		/// <summary>Owner, 2026-10-05: <i>"Scorched looks absolutely terrible, try again."</i> — the burned pit is now the
		/// SAME empty pit (same floor texture, faces, bevels, outline) with a dark-brown char laid over it as vertex colour,
		/// never a texture tile. Floor char alpha at a point: <paramref name="blotch"/> is low-frequency WORLD-space noise
		/// 0..1 (non-repeating patches), <paramref name="edgeDist"/> the distance in cells to the nearest wall (darker
		/// near the walls, lighter toward the middle). Capped at 0.72 so the floor detail and the depth still read and it
		/// is never pure black.</summary>
		public static float FloorCharAlpha(float s, float blotch, float edgeDist)
		{
			if (s <= 0f) return 0f;
			if (s > 1f) s = 1f;
			float wall = edgeDist <= 0f ? 1f : (edgeDist >= 0.6f ? 0f : 1f - edgeDist / 0.6f);
			wall = wall * wall * (3f - 2f * wall);   // smooth, so it never reads as an inner frame
			float a = 0.36f + 0.30f * blotch + 0.08f * wall;
			if (a > 0.72f) a = 0.72f;
			return a * s;
		}

		/// <summary>Warm grey ash drift alpha: only where the blotch noise is high (sparse drifts), never near walls.</summary>
		public static float AshDriftAlpha(float s, float blotch, float edgeDist)
		{
			if (s <= 0f || blotch < 0.62f) return 0f;
			float away = (edgeDist - 0.15f) / 0.35f;     // fades in smoothly away from the walls: no hard inner line
			if (away <= 0f) return 0f;
			if (away > 1f) away = 1f;
			float a = (blotch - 0.62f) / 0.38f * 0.35f * away;
			return (s > 1f ? 1f : s) * a;
		}

		/// <summary>Soot on a face at height fraction v (0 foot .. 1 rim): heaviest at the foot, a second band at the
		/// rim, lighter between — "soot fading upward from the floor and from the rim".</summary>
		public static float FaceSootAlpha(float s, float v)
		{
			if (s <= 0f) return 0f;
			if (v < 0f) v = 0f;
			if (v > 1f) v = 1f;
			float foot = 1f - v;
			float rim = v > 0.75f ? (v - 0.75f) / 0.25f : 0f;
			float a = 0.22f + 0.40f * foot * foot + 0.20f * rim;
			return (s > 1f ? 1f : s) * (a > 0.7f ? 0.7f : a);
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
