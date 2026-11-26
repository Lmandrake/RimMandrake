using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED (owner by card 2026-10-22, "Pick for me: shadow band + navy"): the numbers of
	/// the approved deep-water look, Verse-free so Source/SelfTest/ compiles THIS file. It is drawn, never terrain. (The shadow
	/// band went with RIMMANDRAKE_DRILL_FLOWWORKS_WATER_LAYERS_HE_SAW_STACKED_BLUE: the dry pit's own faces show the wall above dug
	/// water, under one sheet.)
	/// <list type="bullet">
	/// <item>DEEP TINT (mock Transient/fw_scenes/water_art/img/deep_T2_navy.png): water 5 m and deeper takes a navy overlay, 10 m and
	/// deeper a darker one (<see cref="RM_WaterLadder.DeepStep"/>). The mock's per-pixel rule was
	/// <c>out = under·(1 − 0.25·i)·(1 − f) + navy·f</c> with navy (28, 40, 66), f = 0.42 / 0.70 for i = 1 / 2; as an alpha overlay
	/// <c>out = under·(1 − α) + C·α</c> that is exactly α = 1 − (1 − 0.25·i)(1 − f) and C = navy·f / α (<see cref="TintFive"/>,
	/// <see cref="TintTen"/>).</item>
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

		// ── redraw rungs (FlowWorks GPT review 2026-10-22) ────────────────────────────────────────────────────────────
		// The tint layer used to redraw on a TERRAIN change only, so water crossing 5 m / 10 m inside one terrain rung left the
		// picture stale. The watcher (RM_WaterLookWatcher) keys each square's picture by its deep step and dirties the layer's own
		// mesh flag only when a key changes.

		/// <summary>One square's picture as a number: its deep step (0..2).</summary>
		public static int LookKey(int deepStep)
		{
			return deepStep & 3;
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
