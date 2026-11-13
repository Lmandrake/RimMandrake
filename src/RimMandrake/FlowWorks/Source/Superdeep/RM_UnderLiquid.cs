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
	///  - How much of the drowned part is seen? <see cref="Seen"/>, by the metres of liquid over it: clear water shows it
	///    tinted by depth ("a cut between clear water and unobscured view"), an opaque liquid (clarity 0: tar, oil, blood)
	///    hides it. Clarity is the liquid's surfaceLook.seeThrough; it sets how soon the liquid reaches its full body
	///    (<see cref="FullMetresFor"/>).
	/// Drawn: the part above the line as it is; the drowned part at alpha = Seen over the liquid's sheet (the pit floor under
	/// the body colour at 1 - Seen, RM_ExcavationWalls.SeeThrough), in up to <see cref="Bands"/> bands by depth. So a drowned
	/// thing still lets some sheeted floor through and shows less body colour than the floor around it at middle depths
	/// (RIMMANDRAKE_COVER_DROWNED_SPRITES_IN_BODY_COLOUR_NOT_FLOOR). The pit's own shade is the walls' (from the
	/// full wall depth, inside the outline only) and is seen through the liquid by the same law (owner 2026-11-12: "it should
	/// simply be transparent to them as usual. It's much more that they're only inside the pit").
	/// Retuned for RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE (owner 2026-11-12, 6:12 PM: "it becomes about
	/// twice too opaque as it should by the end. Its color should also be darkened"): a clear liquid's opacity is capped at
	/// <see cref="DeepOpacity"/>, and it is dark (<see cref="Darken"/>, now the body colour's darkness).
	/// Retuned for RIMMANDRAKE_TINT_PIT_WATER_READS_AS_WATER_NOT_MUD (owner by card 2026-11-12, "Blue that grows with
	/// depth"; 8:55 PM: "The water still does not read as water well even at 4m, looks more like faint blue mist patches. I
	/// think I asked you for too little opacity."): a gentle-start curve to <see cref="DeepOpacity"/> 0.90 at
	/// <see cref="FullMetres"/>, and the liquid drawn as ONE even sheet of its <see cref="Body"/> colour over an opaque
	/// floor (RM_ExcavationWalls.SeeThrough). Extended for
	/// RIMMANDRAKE_FIX_BIG_PIT_SCENE_BUILDINGS_STAY_DRY: installed buildings by their cover (<see cref="BuildingMetres"/>),
	/// pawns and corpses, one floor shadow (<see cref="ThingShadow"/>) and labels (<see cref="LabelAlpha"/>).
	/// The offline twin is model/underliquid.py; selftest_flowworks_underliquid_parity.py keeps the two equal.
	/// Verse-free: SelfTest SubmergeDrawChecks and UnderLiquidParityChecks run this.
	/// </summary>
	public static class RM_UnderLiquid
	{
		public const float Notch = RM_Volume.MetresPerLevel;

		// drawn heights (m): how far up a thing the liquid line must climb before it is all under
		public const float StakeMetres = 1.0f;
		public const float ItemMetres = 0.3f;
		public const float MinifiedMetres = 0.75f;
		public const float SwaleMetres = 0.05f;
		public const float LyingLadderMetres = 0.1f;
		public const float CorpseMetres = 0.3f;

		/// <summary>An installed building stands max(<see cref="MinThingMetres"/>, fillPercent x this) tall: a full-cover
		/// building (fillPercent 1) is this tall, a 0.4-fill bed or table 0.8 m.</summary>
		public const float FullCoverMetres = 2.0f;
		public const float MinThingMetres = 0.3f;

		public static float BuildingMetres(float fillPercent)
		{
			float h = fillPercent * FullCoverMetres;
			return h > MinThingMetres ? h : MinThingMetres;
		}

		/// <summary>RIMMANDRAKE_REMOVE_DARK_SQUARE_AROUND_SUNK_GEYSER_UNWELCOME_BOX (owner 2026-11-12: "a strange darker square
		/// around the geyser image that isn't welcome"): a building under this fill, with no vanilla sun shadow and no
		/// shadowData, is flat (a vent, a rug) and casts no floor shadow.</summary>
		public const float FlatFillPercent = 0.2f;

		public static bool CastsFloorShadow(float fillPercent, float sunShadowHeight, bool hasShadowData)
		{
			return fillPercent >= FlatFillPercent || sunShadowHeight > 0f || hasShadowData;
		}

		/// <summary>How far in from each edge of the floor shadow (a share of its side) it takes to rise from nothing to
		/// whole: the shadow is a soft-edged pool, never a hard rectangle.</summary>
		public const float ShadowFeatherWidth = 0.25f;

		/// <summary>The floor shadow's alpha share at (u, v) across its quad, each 0..1: 0 at the edge, smoothstep to 1 at
		/// <see cref="ShadowFeatherWidth"/> in.</summary>
		public static float ShadowFeather(float u, float v)
		{
			float e = System.Math.Min(System.Math.Min(u, 1f - u), System.Math.Min(v, 1f - v));
			if (e <= 0f)
			{
				return 0f;
			}
			if (e >= ShadowFeatherWidth)
			{
				return 1f;
			}
			float x = e / ShadowFeatherWidth;
			return x * x * (3f - 2f * x);
		}

		// the experience numbers; Mod Settings write them (RimMandrakeFlowWorksSettings.PushUnderLiquid), these are the
		// shipped defaults
		public const float DefaultDeepOpacity = 0.90f;
		public const float DefaultFullMetres = 4.0f;
		public const float DefaultDarken = 0.6f;
		public const float DefaultThingShadowAlpha = 0.30f;

		/// <summary>The most a clear liquid ever hides: its body at full depth (setting underLiquidDeepOpacity).</summary>
		public static float DeepOpacity = DefaultDeepOpacity;

		/// <summary>The depth (m) at which fresh water reaches <see cref="DeepOpacity"/> (setting underLiquidFullMetres).</summary>
		public static float FullMetres = DefaultFullMetres;

		/// <summary>How dark a clear liquid's body colour is (setting underLiquidDarken): <see cref="Body"/>.</summary>
		public static float Darken = DefaultDarken;

		/// <summary>Fresh water's seeThrough: the liquid <see cref="FullMetres"/> is stated for.</summary>
		public const float ReferenceClarity = 0.45f;

		/// <summary>rise(x) = 1 - (1 - x)^CurvePower: gentle at first ("very transparent at first"), steps a viewer can tell
		/// apart all the way to the full depth.</summary>
		public const float CurvePower = 1.4f;

		/// <summary>A body colour is the liquid's own colour to this power (darker and more saturated), x (1 - Darken).</summary>
		public const float BodyGamma = 3.0f;

		/// <summary>The floor shadow of a thing standing in a pit, dry (setting pitThingShadowAlpha).</summary>
		public static float ThingShadowAlpha = DefaultThingShadowAlpha;

		/// <summary>A label (quality, stack count, owner) is hidden once its thing is seen less than this.</summary>
		public const float LabelHidden = 0.05f;

		/// <summary>Fresh water's LiquidDef colour: the body of a clear liquid whose own colour is not known.</summary>
		public static readonly Float3 WaterColour = new Float3(0.62f, 0.80f, 0.98f);

		/// <summary>A clear liquid's body colour, the one sheet drawn over everything it covers (floor, walls, pawns): its
		/// own colour darker and more saturated, never a pale wash (owner: "a dark colour, not pale").</summary>
		public static Float3 Body(Float3 colour)
		{
			float k = 1f - Darken;
			return new Float3(Deepen(colour.r) * k, Deepen(colour.g) * k, Deepen(colour.b) * k);
		}

		private static float Deepen(float v) => (float)System.Math.Pow(Clamp01(v), BodyGamma);

		public struct Float3
		{
			public readonly float r, g, b;

			public Float3(float r, float g, float b)
			{
				this.r = r;
				this.g = g;
				this.b = b;
			}
		}

		/// <summary>The one floor shadow of a thing standing in a pit (owner 2026-11-12: shadows only inside the pit, "it
		/// should simply be transparent to them as usual"): its own alpha. It is drawn UNDER the liquid's sheet
		/// (RM_FaceMaterial.UnderSheetQueue), which hides it by the law like the floor it lies on; drawn over the liquid it was
		/// an untinted dark square under every thing. None under an opaque liquid.</summary>
		public static float ThingShadow(float clarity, float levelMetres) => levelMetres > 0f && !(clarity > 0f) ? 0f : ThingShadowAlpha;

		/// <summary>A thing's label fades with its top (<paramref name="heightMetres"/> up from the floor); 0 = hidden.</summary>
		public static float LabelAlpha(float clarity, float levelMetres, float heightMetres)
		{
			float a = Seen(clarity, levelMetres - heightMetres);
			return a < LabelHidden ? 0f : a;
		}

		/// <summary>A gate stands on the channel floor and its head clears the bank by one notch.</summary>
		public static float GateMetres(int depthNotches) => (depthNotches + 1) * Notch;

		public const int Bands = 4;
		public const float NoCut = -1f;

		public static float Clamp01(float v) => v <= 0f ? 0f : (v >= 1f ? 1f : v);

		/// <summary>The one see-through law: 1 above the line; 0 for an opaque liquid; else
		/// 1 - DeepOpacity x rise(metres over / FullMetresFor(clarity)).</summary>
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
			return 1f - DeepOpacity * Rise(metresOver / FullMetresFor(clarity));
		}

		/// <summary>The depth (m) at which a liquid of this clarity (0..1, exclusive) reaches <see cref="DeepOpacity"/>: fresh
		/// water at <see cref="FullMetres"/>, a murkier liquid sooner, a clearer one later.</summary>
		public static float FullMetresFor(float clarity) =>
			FullMetres * (float)(System.Math.Log(ReferenceClarity) / System.Math.Log(clarity));

		/// <summary>0 at the surface, 1 at the full depth and below: 1 - (1 - x)^CurvePower.</summary>
		public static float Rise(float x)
		{
			if (x <= 0f)
			{
				return 0f;
			}
			return x >= 1f ? 1f : 1f - (float)System.Math.Pow(1f - x, CurvePower);
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

		/// <summary>Steps per notch the drawn level is kept to (RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES, owner card
		/// 2026-11-13 "Waterline -> follow it smoothly"): 2.5 cm, under a pixel of a wall face, so the wall face, a hung ladder
		/// and the spikes are cut at the true waterline. The map mesh re-prints only when the level moves a step, so a level
		/// swinging by a few decilitres (under 500 dL a square) still never re-meshes. Was 4 (12.5 cm).</summary>
		public const int LevelSteps = 20;

		/// <summary>A true level in notches as the note everything is drawn at: 0 only when dry, at least 1 when any liquid
		/// stands; the deepest dig (RM_DigDepthMath.MaxDigCeiling) is drawn exactly (the old 255 cap drowned deep pits).</summary>
		public static int LevelNote(double levelNotches)
		{
			if (levelNotches <= 0.0) return 0;
			int cap = RM_DigDepthMath.MaxDigCeiling * LevelSteps;
			int n = levelNotches >= cap ? cap : (int)(levelNotches * LevelSteps + 0.5);
			return n < 1 ? 1 : (n > cap ? cap : n);
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
