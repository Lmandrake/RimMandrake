using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED (owner by card 2026-10-22, "Pick for me: shadow band + navy"): the numbers of
	/// the two approved water looks, Verse-free so Source/SelfTest/ compiles THIS file. Both are drawn, never terrain:
	/// <list type="bullet">
	/// <item>DEEP TINT (mock Transient/fw_scenes/water_art/img/deep_T2_navy.png): water 5 m and deeper takes a navy overlay, 10 m and
	/// deeper a darker one (<see cref="RM_WaterLadder.DeepStep"/>). The mock's per-pixel rule was
	/// <c>out = under·(1 − 0.25·i)·(1 − f) + navy·f</c> with navy (28, 40, 66), f = 0.42 / 0.70 for i = 1 / 2; as an alpha overlay
	/// <c>out = under·(1 − α) + C·α</c> that is exactly α = 1 − (1 − 0.25·i)(1 − f) and C = navy·f / α (<see cref="TintFive"/>,
	/// <see cref="TintTen"/>).</item>
	/// <item>WALL SHADOW BAND (mock wall_1_shadow_band.png): a wet dug square whose water stands below the lip shows a soft dark band
	/// on its north and west edges, as thick as the gap between the water and the lip (0.34 of a square per 2 m of gap, at least
	/// 1/16, at most half), darkest at the lip (0.75, the west side 0.8 of that) and fading to nothing toward the water.</item>
	/// </list>
	/// The soft edge between tint steps (corner = mean of the four squares round it) is a first guess, to be judged in game.
	/// </summary>
	public static class RM_WaterLookMath
	{
		/// <summary>An 8-bit colour with alpha (Verse-free stand-in for Color32).</summary>
		public struct Rgba
		{
			public byte r, g, b, a;

			public Rgba(byte r, byte g, byte b, byte a)
			{
				this.r = r;
				this.g = g;
				this.b = b;
				this.a = a;
			}
		}

		public static readonly Rgba TintFive = new Rgba(21, 30, 49, 144);
		public static readonly Rgba TintTen = new Rgba(23, 33, 54, 217);

		/// <summary>Strength of a square's tint: its deep step as a number (0, 1, 2), so corners can average.</summary>
		public static float StepStrength(RM_WaterLadder.DeepStep step)
		{
			return (float)(int)step;
		}

		/// <summary>The overlay colour for a tint strength <paramref name="s"/> in [0, 2]: 0 nothing, 1 the 5 m tint, 2 the 10 m
		/// tint, linear between (0..1 fades the 5 m tint in by alpha; 1..2 moves toward the 10 m tint).</summary>
		public static Rgba TintAt(float s)
		{
			if (s <= 0f)
			{
				return new Rgba(TintFive.r, TintFive.g, TintFive.b, 0);
			}
			if (s <= 1f)
			{
				return new Rgba(TintFive.r, TintFive.g, TintFive.b, (byte)Math.Round(TintFive.a * s));
			}
			float k = s >= 2f ? 1f : s - 1f;
			return new Rgba(Lerp(TintFive.r, TintTen.r, k), Lerp(TintFive.g, TintTen.g, k), Lerp(TintFive.b, TintTen.b, k),
				Lerp(TintFive.a, TintTen.a, k));
		}

		private static byte Lerp(byte a, byte b, float k)
		{
			return (byte)Math.Round(a + (b - a) * k);
		}

		/// <summary>One channel of <paramref name="under"/> after the alpha overlay <paramref name="t"/> (what the shader does).</summary>
		public static double Over(double under, byte tintChannel, byte alpha)
		{
			double a = alpha / 255.0;
			return under * (1.0 - a) + tintChannel * a;
		}

		// ── the wall shadow band ──────────────────────────────────────────────────────────────────────────────

		public static readonly Rgba BandColour = new Rgba(48, 34, 24, 0);
		public const float BandPerTwoMetres = 0.34f;
		public const float BandMin = 1f / 16f;
		public const float BandMax = 0.5f;
		public const float BandLipAlpha = 0.75f;
		public const float BandWestFactor = 0.8f;

		/// <summary>Metres between the water and the lip on one side: the side's drop (this square's floor below its neighbour's,
		/// in notches) less the water standing here. Never negative; 0 when the neighbour is as deep or deeper.</summary>
		public static double GapMetres(int myHollowNotches, int neighbourHollowNotches, double waterMetres)
		{
			int drop = myHollowNotches - neighbourHollowNotches;
			if (drop <= 0)
			{
				return 0.0;
			}
			double gap = drop * RM_LevelSolve.Metres(RM_LevelSolve.U) - waterMetres;
			return gap > 0.0 ? gap : 0.0;
		}

		/// <summary>The band's thickness in squares for <paramref name="gapMetres"/> of dry wall above the water (0 for no gap).</summary>
		public static float BandThickness(double gapMetres)
		{
			if (gapMetres <= 0.0)
			{
				return 0f;
			}
			float t = (float)(BandPerTwoMetres * gapMetres / 2.0);
			return t < BandMin ? BandMin : (t > BandMax ? BandMax : t);
		}

		/// <summary>The band's alpha at the lip (it fades to 0 at its inner edge): the north band full, the west band 0.8 of it.</summary>
		public static float BandAlpha(bool west)
		{
			return west ? BandLipAlpha * BandWestFactor : BandLipAlpha;
		}

		// ── redraw rungs (FlowWorks GPT review 2026-10-22, RM_WaterLooks.cs:116/207) ────────────────────────────────────
		// The two layers used to redraw on a TERRAIN change only, so water crossing 5 m / 10 m, or a band's gap changing, inside
		// one terrain rung left the picture stale. The watcher (RM_WaterLookWatcher) now keys each square's picture by its rung
		// and dirties the layers' own mesh flag only when a key changes: a deep step, or a band edge moving by 1/32 of a square.

		/// <summary>Band rungs per square: the band is redrawn when its edge moves by this much (about 19 cm of gap).</summary>
		public const int BandRungsPerSquare = 32;

		/// <summary>The rung of a band <paramref name="thickness"/> (squares): 0 for no band, else at least 1.</summary>
		public static int BandRung(float thickness)
		{
			if (thickness <= 0f)
			{
				return 0;
			}
			int r = (int)Math.Round(thickness * BandRungsPerSquare);
			return r < 1 ? 1 : r;
		}

		/// <summary>One square's picture as a number: its deep step (0..2) and its north and west band rungs. Equal keys draw the
		/// same picture to within one band rung, so a changed key is the only reason to redraw.</summary>
		public static int LookKey(int deepStep, float bandNorth, float bandWest)
		{
			return (deepStep & 3) | (BandRung(bandNorth) & 63) << 2 | (BandRung(bandWest) & 63) << 8;
		}

		/// <summary>The last key seen per square (map-sized, allocated once). <see cref="Note"/> says whether it changed.</summary>
		public sealed class Watch
		{
			private int[] keys;

			public bool Note(int cell, int cells, int key)
			{
				if (keys == null || keys.Length != cells)
				{
					keys = new int[cells];   // 0 = nothing drawn, which is also the key of dry ground
				}
				if (keys[cell] == key)
				{
					return false;
				}
				keys[cell] = key;
				return true;
			}
		}
	}
}
