namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL: ONE rule for everything in a dug square under liquid (owner's live look
	/// 2026-11-12, SUBMERGE_PIT_FITTINGS_MATRIX_20261112: "It's as though each case is independently set in these variables,
	/// badly (major fix)"). Root cause: D:\ClaudeWork\rimmandrake\conductor\submerge_matrix_20261112\owner_look\ROOT_CAUSE.md
	/// (the offline twin of this class: model\underliquid.py there).
	///
	/// Every caller (ladders hung or lying, the ramp, gates, stakes, items, minified things, the swale, the pit's own floor
	/// and walls) asks the same two questions, at the cell's TRUE level (whole notch + part-notch, kept to quarter notches by
	/// <see cref="LevelNote"/>, no fill steps):
	///  - How much of it is under the line? <see cref="Share"/>: the liquid line climbs a thing standing on the floor by its
	///    drawn height, from its foot (owner: things "stand on their bottom"). A thing hung on the N/E/W wall spans floor to
	///    rim and is cut where that wall's own face meets the liquid (<see cref="Waterline"/>, the walls' projection).
	///    Hung south (only its top shows above the near rim) or standing on the bank: never under.
	///  - How much of the drowned part is seen? <see cref="Seen"/> = clarity ^ (metres of liquid over it + the surface's
	///    own <see cref="SurfaceMetres"/>): clear water shows it tinted by depth ("a cut between clear water and unobscured
	///    view"), an opaque liquid (clarity 0: tar, oil, blood) hides it. Clarity is the liquid's surfaceLook.seeThrough,
	///    read as the share of the view left after 1 m.
	/// Drawn: the part above the line as it is; the drowned part over the liquid's terrain at alpha = Seen (so it reads as
	/// lerp(liquid, thing, Seen)), in up to <see cref="Bands"/> bands by depth. The pit's own shade is the walls' (from the
	/// full wall depth, inside the outline only) and is seen through the liquid by the same law (owner 2026-11-12: "it should
	/// simply be transparent to them as usual. It's much more that they're only inside the pit").
	/// Verse-free: SelfTest SubmergeDrawChecks runs this.
	/// </summary>
	public static class RM_UnderLiquid
	{
		public const float Notch = RM_Volume.MetresPerLevel;

		/// <summary>The liquid's surface itself takes this much from the view, so the line where liquid starts always reads.</summary>
		public const float SurfaceMetres = 0.35f;

		// drawn heights (m): how far up a thing the liquid line must climb before it is all under
		public const float StakeMetres = 1.0f;
		public const float ItemMetres = 0.3f;
		public const float MinifiedMetres = 0.75f;
		public const float SwaleMetres = 0.05f;
		public const float LyingLadderMetres = 0.1f;

		/// <summary>A gate stands on the channel floor and its head clears the bank by one notch.</summary>
		public static float GateMetres(int depthNotches) => (depthNotches + 1) * Notch;

		public const int Bands = 4;
		public const float NoCut = -1f;

		public static float Clamp01(float v) => v <= 0f ? 0f : (v >= 1f ? 1f : v);

		/// <summary>The one see-through law: 1 above the line; else clarity ^ (metres over + SurfaceMetres); 0 for an opaque
		/// liquid.</summary>
		public static float Seen(float clarity, float metresOver)
		{
			if (metresOver <= 0f)
			{
				return 1f;
			}
			if (!(clarity > 0f))
			{
				return 0f;
			}
			if (clarity >= 1f)
			{
				return 1f;
			}
			return (float)System.Math.Pow(clarity, metresOver + SurfaceMetres);
		}

		/// <summary>The one cut: the share of a thing standing <paramref name="baseMetres"/> above the floor and
		/// <paramref name="heightMetres"/> tall under <paramref name="levelMetres"/> of liquid, from its foot. A thing with no
		/// height is all under once any liquid stands over its base.</summary>
		public static float Share(float levelMetres, float baseMetres, float heightMetres)
		{
			if (levelMetres <= baseMetres)
			{
				return 0f;
			}
			return heightMetres <= 0f ? 1f : Clamp01((levelMetres - baseMetres) / heightMetres);
		}

		/// <summary>The metres of liquid over the point <paramref name="at"/> of a drowned part that runs from the line at
		/// <paramref name="linePos"/> (<paramref name="lineMetres"/> under: 0 when the thing pokes out, more when all of it is
		/// under) to its foot at <paramref name="footPos"/> (<paramref name="footMetres"/> under). Straight between the two.</summary>
		public static float MetresAt(float at, float linePos, float footPos, float lineMetres, float footMetres)
		{
			float span = footPos - linePos;
			if (span == 0f)
			{
				return footMetres;
			}
			return lineMetres + (footMetres - lineMetres) * Clamp01((at - linePos) / span);
		}

		/// <summary>How much is seen of a drowned band lying <paramref name="metresOver"/> under at its middle (alpha steps of
		/// 1/<see cref="Steps"/>; 0 = not drawn).</summary>
		public static int BandAlphaStep(float clarity, float metresOver)
		{
			float a = Seen(clarity, metresOver);
			int q = (int)(a * Steps + 0.5f);
			return q < 0 ? 0 : (q > Steps ? Steps : q);
		}

		/// <summary>Bands worth drawing for a drowned part lying <paramref name="lineMetres"/>..<paramref name="footMetres"/>
		/// under: 0 for an opaque liquid (hidden), 1 when the law barely changes over it, else <see cref="Bands"/>.</summary>
		public static int BandsFor(float clarity, float lineMetres, float footMetres)
		{
			if (!(clarity > 0f))
			{
				return 0;
			}
			float top = lineMetres <= 0f ? 0.0001f : lineMetres;
			return Seen(clarity, top) - Seen(clarity, footMetres) < 0.06f ? 1 : Bands;
		}

		// ── the level ──────────────────────────────────────────────────

		/// <summary>Quarter notches the drawn level is kept to: the map mesh re-prints only when the level moves a quarter
		/// notch (12.5 cm, RM_LevelSolve.LookStickyMargin), so a level swinging by a few decilitres never re-meshes.</summary>
		public const int LevelSteps = 4;

		/// <summary>A true level in notches as the quarter-notch note everything is drawn at: 0 only when dry, at least 1 when
		/// any liquid stands, at most 255.</summary>
		public static int LevelNote(double levelNotches)
		{
			if (levelNotches <= 0.0) return 0;
			int n = (int)(levelNotches * LevelSteps + 0.5);
			return n < 1 ? 1 : (n > 255 ? 255 : n);
		}

		/// <summary>The level (notches) a note draws.</summary>
		public static float NoteLevel(int note) => note <= 0 ? 0f : (float)note / LevelSteps;

		public static float NoteMetres(int note) => NoteLevel(note) * Notch;

		// ── the walls' projection ────────────────────────────────────────

		/// <summary>How far (notches, fractional) this cell's floor sits below its neighbour's, less the liquid standing in it
		/// (RM_WallFaceMath.ExposedDrop at the true level). Never negative.</summary>
		public static float Exposed(int myDepth, int neighbourDepth, float levelNotches)
		{
			int drop = myDepth - neighbourDepth;
			if (drop <= 0) return 0f;
			float e = drop - (levelNotches < 0f ? 0f : levelNotches);
			return e < 0f ? 0f : e;
		}

		/// <summary>A face table (RM_WallFaceMath.NorthByDrop / SideByDrop) read at a fractional exposed drop: the whole-notch
		/// entries exactly, a straight line between them, the last entry past the end.</summary>
		public static float FaceAt(float[] table, float exposed)
		{
			if (exposed <= 0f) return 0f;
			int last = table.Length - 1;
			if (exposed >= last) return table[last];
			int lo = (int)exposed;
			float t = exposed - lo;
			return table[lo] + (table[lo + 1] - table[lo]) * t;
		}

		public static float NorthFace(float exposed) => FaceAt(RM_WallFaceMath.NorthByDrop, exposed);

		public static float SideFace(float exposed) => FaceAt(RM_WallFaceMath.SideByDrop, exposed);

		/// <summary>The cell-local waterline of a thing hung on rotation <paramref name="rot"/> (0 N, 1 E, 2 S, 3 W) over a
		/// wall of <paramref name="drop"/> notches with <paramref name="levelNotches"/> standing: exactly where the wall layer
		/// draws that face's waterline (z for N, x for E/W). NoCut when dry or hung south.</summary>
		public static float Waterline(int rot, int drop, float levelNotches)
		{
			if (levelNotches <= 0f || rot == 2) return NoCut;
			float exposed = Exposed(drop, 0, levelNotches);
			if (rot == 0) return 1f - NorthFace(exposed);
			float w = SideFace(exposed);
			return rot == 1 ? 1f - w : w;
		}

		// ── cutting a sprite ─────────────────────────────────────────────

		/// <summary>Sprite sides a cut starts from: the drowned part is the one nearest this side.</summary>
		public const int FromSouth = 0, FromWest = 1, FromNorth = 2, FromEast = 3;

		/// <summary>The side a hung thing's drowned part starts from (N: its foot is south; E: west; W: east).</summary>
		public static int HungFrom(int rot) => rot == 1 ? FromWest : (rot == 3 ? FromEast : FromSouth);

		/// <summary>The share of a sprite spanning [<paramref name="lo"/>, <paramref name="hi"/>] (cell-local, along the cut
		/// axis) below a waterline at <paramref name="cut"/>, from the low end (South/West) or the high end (North/East).</summary>
		public static float SpanShare(float lo, float hi, float cut, bool fromLow)
		{
			if (cut < 0f || hi <= lo) return 0f;
			return fromLow ? Clamp01((cut - lo) / (hi - lo)) : Clamp01((hi - cut) / (hi - lo));
		}

		/// <summary>A share as a step 0..Steps (the realtime meshes' key): 0 only when nothing is under, Steps only when all is.</summary>
		public const int Steps = 32;

		public static int Step(float share)
		{
			if (share <= 0f) return 0;
			if (share >= 1f) return Steps;
			int s = (int)(share * Steps + 0.5f);
			return s < 1 ? 1 : (s > Steps - 1 ? Steps - 1 : s);
		}

		/// <summary>Keeps the slice [<paramref name="a"/>, <paramref name="b"/>] (shares measured from side
		/// <paramref name="from"/>) of a quad given as its four corners in PrintPlane order (0 = -x-z, 1 = -x+z, 2 = +x+z,
		/// 3 = +x-z): <paramref name="uv"/> (8 floats, atlas sub-rects and flips included) and its rect, both moved in place.</summary>
		public static void Slice(int from, float a, float b, float[] uv, ref float x0, ref float z0, ref float x1, ref float z1)
		{
			a = Clamp01(a);
			b = Clamp01(b);
			float u0 = uv[0], v0 = uv[1], u1 = uv[2], v1 = uv[3], u2 = uv[4], v2 = uv[5], u3 = uv[6], v3 = uv[7];
			switch (from)
			{
				case FromSouth:
					Edge(uv, 0, u0, v0, u1, v1, a); Edge(uv, 1, u0, v0, u1, v1, b);
					Edge(uv, 3, u3, v3, u2, v2, a); Edge(uv, 2, u3, v3, u2, v2, b);
					float zs = z0, hz = z1 - z0; z0 = zs + hz * a; z1 = zs + hz * b; break;
				case FromNorth:
					Edge(uv, 1, u1, v1, u0, v0, a); Edge(uv, 0, u1, v1, u0, v0, b);
					Edge(uv, 2, u2, v2, u3, v3, a); Edge(uv, 3, u2, v2, u3, v3, b);
					float zn = z1, hn = z1 - z0; z1 = zn - hn * a; z0 = zn - hn * b; break;
				case FromWest:
					Edge(uv, 0, u0, v0, u3, v3, a); Edge(uv, 3, u0, v0, u3, v3, b);
					Edge(uv, 1, u1, v1, u2, v2, a); Edge(uv, 2, u1, v1, u2, v2, b);
					float xw = x0, hw = x1 - x0; x0 = xw + hw * a; x1 = xw + hw * b; break;
				default:
					Edge(uv, 3, u3, v3, u0, v0, a); Edge(uv, 0, u3, v3, u0, v0, b);
					Edge(uv, 2, u2, v2, u1, v1, a); Edge(uv, 1, u2, v2, u1, v1, b);
					float xe = x1, he = x1 - x0; x1 = xe - he * a; x0 = xe - he * b; break;
			}
		}

		private static void Edge(float[] uv, int corner, float us, float vs, float ue, float ve, float s)
		{
			uv[corner * 2] = us + (ue - us) * s;
			uv[corner * 2 + 1] = vs + (ve - vs) * s;
		}
	}
}
