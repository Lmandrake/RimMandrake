namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON (owner's walk 2026-11-22: the "water sheet" was the
	/// life stage's generic silhouette icon, misplaced; by card he picked concept A of
	/// design/specs/2026-11-22-pawn-in-liquid-look/design.md, "her own picture cut at the liquid's surface"). The pure rule:
	/// how much of which pawn shows at which depth. RM_SubmergeDraw.PawnCut applies it to every node the pawn's own render
	/// tree draws (body, apparel, head, hair, headgear), clipped in world space at one line.
	///
	///  - Standing (or wading): the line climbs the pawn's picture (its body and head nodes, from the lowest drawn pixel to
	///    the highest) by BODY LANDMARKS, not straight metres (design section 5): a humanlike's head is half its picture, so
	///    1 m of water on a 1.75 m colonist is at the waist, not the chin. Animals, mechanoids and other bodies take the
	///    straight share of their picture (no landmark table yet; the design says so).
	///  - Above the line: drawn as vanilla draws it. Below the line: in a clear liquid drawn dimmed in the liquid's body
	///    colour (the law's Seen at the full depth, as the floor beside it is seen); in an opaque liquid not drawn.
	///  - Lying, downed or dead (design section 5, GPT's warning): never cut (a horizontal line across a lying body cuts
	///    through her face). Her whole picture is tinted towards the liquid as the liquid rises over her lying height; once
	///    the liquid is over it, she is wholly under: dimmed in a clear liquid, hidden in an opaque one.
	///  - Carried: not in the liquid (her carrier is); drawn whole.
	/// Verse-free: SelfTest PawnCutChecks runs this.
	/// </summary>
	public static class RM_PawnCutMath
	{
		public enum Mode
		{
			/// <summary>Drawn as vanilla draws it.</summary>
			Whole,
			/// <summary>Cut at the line: the upper part as vanilla, the lower part tinted (clear) or not drawn (opaque).</summary>
			Cut,
			/// <summary>Whole, every part tinted (lying in the liquid, or wholly under a clear one).</summary>
			Tinted,
			/// <summary>Wholly under an opaque liquid: nothing of the picture shows (the realtime gate hides it).</summary>
			Hidden
		}

		/// <summary>A humanlike's body landmarks: the share of its HEIGHT (metres, from the feet) at which the liquid
		/// reaches the knee, the crotch, the waist, the shoulder, the chin and the crown.</summary>
		public static readonly float[] HumanHeight = { 0f, 0.28f, 0.47f, 0.60f, 0.82f, 0.87f, 1f };

		/// <summary>Where each landmark lies in a vanilla humanlike's PICTURE (share from the lowest drawn pixel to the crown).
		/// Measured 2026-11-22 from Naked_Female_south (content rows 0.117..0.703 of the 1.5-cell body quad: hips widest at
		/// 0.25..0.32, waist narrowest at 0.41, shoulders widest at 0.48..0.51) with the head (content 0.305..0.695 of its
		/// 1.5 quad) at BodyTypeDef Female headOffset z 0.34: feet -0.574, crown +0.632 about the body's centre.</summary>
		public static readonly float[] HumanPicture = { 0f, 0.10f, 0.19f, 0.365f, 0.476f, 0.52f, 1f };

		/// <summary>The share of the pawn's picture (from its lowest drawn pixel) under the line, for liquid
		/// <paramref name="levelMetres"/> deep on a pawn <paramref name="heightMetres"/> tall standing in it.</summary>
		public static float PictureShare(bool humanlike, float levelMetres, float heightMetres)
		{
			if (!(levelMetres > 0f))
			{
				return 0f;
			}
			if (!(heightMetres > 0f))
			{
				return 1f;
			}
			float d = levelMetres / heightMetres;
			if (d >= 1f)
			{
				return 1f;
			}
			return humanlike ? Lerp(HumanHeight, HumanPicture, d) : d;
		}

		/// <summary>Piecewise straight between the knots (x ascending), clamped to the ends.</summary>
		public static float Lerp(float[] xs, float[] ys, float x)
		{
			if (x <= xs[0])
			{
				return ys[0];
			}
			for (int i = 1; i < xs.Length; i++)
			{
				if (x <= xs[i])
				{
					float t = (x - xs[i - 1]) / (xs[i] - xs[i - 1]);
					return ys[i - 1] + (ys[i] - ys[i - 1]) * t;
				}
			}
			return ys[ys.Length - 1];
		}

		/// <summary>The most a lying pawn partly in an opaque liquid is tinted towards it (it still reads as her, down in it).</summary>
		public const float LyingOpaqueTint = 0.6f;

		/// <summary>The decision for one pawn draw. <paramref name="lyingMetres"/> is the law's lying height
		/// (RM_UnderLiquid.CorpseMetres). <paramref name="lineShare"/>: the share of the picture under the line (Cut);
		/// <paramref name="tintStrength"/>: how far the tinted part moves from its own colour to the liquid's (0..1).</summary>
		public static Mode Decide(bool lying, bool carried, bool humanlike, float levelMetres, float heightMetres, float lyingMetres,
			float clarity, out float lineShare, out float tintStrength)
		{
			lineShare = 0f;
			tintStrength = 0f;
			if (carried || !(levelMetres > 0f))
			{
				return Mode.Whole;
			}
			bool clear = clarity > 0f;
			if (lying)
			{
				float s = RM_UnderLiquid.Share(levelMetres, 0f, lyingMetres);
				if (s >= 1f)
				{
					tintStrength = 1f;
					return clear ? Mode.Tinted : Mode.Hidden;
				}
				tintStrength = clear ? s : s * LyingOpaqueTint;
				return tintStrength > 0f ? Mode.Tinted : Mode.Whole;
			}
			float p = PictureShare(humanlike, levelMetres, heightMetres);
			if (p <= 0f)
			{
				return Mode.Whole;
			}
			if (p >= 1f)
			{
				tintStrength = 1f;
				return clear ? Mode.Tinted : Mode.Hidden;
			}
			lineShare = p;
			tintStrength = 1f;
			return Mode.Cut;
		}

		/// <summary>The world z of the line on a picture spanning <paramref name="footZ"/>..<paramref name="crownZ"/>.</summary>
		public static float LineZ(float footZ, float crownZ, float share) => footZ + (crownZ - footZ) * share;

		/// <summary>The colour factor a tinted part is multiplied by: white lerped to the liquid's colour <paramref name="liquid"/>
		/// by the liquid's hiding power (1 - <paramref name="seen"/>) at <paramref name="strength"/>. Clear water: dimmer and
		/// bluer the deeper; an opaque liquid (seen 0) at full strength would be the liquid itself.</summary>
		public static RM_UnderLiquid.Float3 TintFactor(RM_UnderLiquid.Float3 liquid, float seen, float strength)
		{
			float k = RM_UnderLiquid.Clamp01(strength) * (1f - RM_UnderLiquid.Clamp01(seen));
			return new RM_UnderLiquid.Float3(1f + (liquid.r - 1f) * k, 1f + (liquid.g - 1f) * k, 1f + (liquid.b - 1f) * k);
		}

		// ── the cut (geometry) ─────────────────────────────────────────────

		/// <summary>The most corners a triangle keeps after one cut (a triangle cut by a line keeps a triangle or a quad).</summary>
		public const int MaxPolyCorners = 4;

		/// <summary>Cuts one triangle (corners a, b, c: x, y, z, u, v each, in the mesh's own space) by the plane
		/// k·(x, y, z) + w = 0 (world z minus the line, read through the node's matrix), keeping the side where the value is
		/// >= 0 (<paramref name="keepAbove"/>) or &lt; 0. Writes up to <see cref="MaxPolyCorners"/> corners (5 floats each) to
		/// <paramref name="outPoly"/> and returns their count (0, 3 or 4).</summary>
		public static int ClipTriangle(float[] a, float[] b, float[] c, float kx, float ky, float kz, float w, bool keepAbove,
			float[] outPoly)
		{
			float da = Side(a, kx, ky, kz, w, keepAbove), db = Side(b, kx, ky, kz, w, keepAbove), dc = Side(c, kx, ky, kz, w, keepAbove);
			int n = 0;
			n = Edge(a, b, da, db, outPoly, n);
			n = Edge(b, c, db, dc, outPoly, n);
			n = Edge(c, a, dc, da, outPoly, n);
			return n < 3 ? 0 : n;
		}

		private static float Side(float[] p, float kx, float ky, float kz, float w, bool keepAbove)
		{
			float v = kx * p[0] + ky * p[1] + kz * p[2] + w;
			return keepAbove ? v : -v;
		}

		/// <summary>Sutherland-Hodgman for one edge p->q: p if kept, then the crossing point if the edge crosses.</summary>
		private static int Edge(float[] p, float[] q, float dp, float dq, float[] outPoly, int n)
		{
			bool pIn = dp >= 0f, qIn = dq >= 0f;
			if (pIn)
			{
				n = Put(outPoly, n, p, p, 0f);
			}
			if (pIn != qIn)
			{
				n = Put(outPoly, n, p, q, dp / (dp - dq));
			}
			return n;
		}

		private static int Put(float[] outPoly, int n, float[] p, float[] q, float t)
		{
			if (n >= MaxPolyCorners)
			{
				return n;
			}
			for (int i = 0; i < 5; i++)
			{
				outPoly[n * 5 + i] = p[i] + (q[i] - p[i]) * t;
			}
			return n + 1;
		}

		/// <summary>The world-space picture extent of one drawn node: the world z of its lowest and highest drawn pixel, for a
		/// mesh whose local z runs <paramref name="zMin"/>..<paramref name="zMax"/> over texture rows
		/// <paramref name="vMin"/>..<paramref name="vMax"/>, whose texture holds pixels in rows
		/// <paramref name="c0"/>..<paramref name="c1"/> (0 bottom, 1 top), placed by a matrix whose world z is
		/// m22 x local z + m23 (an upright node; its turn about the vertical moves x, not z).</summary>
		public static void NodeExtent(float zMin, float zMax, float vMin, float vMax, float c0, float c1, float m22, float m23,
			out float lo, out float hi)
		{
			float span = vMax - vMin;
			float z0 = span == 0f ? zMin : zMin + (c0 - vMin) / span * (zMax - zMin);
			float z1 = span == 0f ? zMax : zMin + (c1 - vMin) / span * (zMax - zMin);
			float w0 = m22 * z0 + m23, w1 = m22 * z1 + m23;
			lo = w0 < w1 ? w0 : w1;
			hi = w0 < w1 ? w1 : w0;
		}
	}
}
