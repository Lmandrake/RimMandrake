using System.Collections.Generic;
using System.Text;

namespace RimMandrake.FlowWorks
{
	/// <summary>Ruling #19 (owner, 2026-10-11, card: "Every liquid gets a wading wake value"): the V-wake's two ripples per
	/// wader, from the liquid's 0..1 <c>wake</c>. Verse-free so the C# selftest covers it (RM_LiquidSurface draws it).</summary>
	public static class RM_WakeMath
	{
		/// <summary>Fleck speed, cells per second: 0.55 at wake 1 (water's clear spreading V), near 0 for tar.</summary>
		public static float Speed(float wake)
		{
			return 0.55f * Clamp01(wake);
		}

		/// <summary>Ripple size: 0.35 per body size (clamped 0.5..2), scaled from half (a thick liquid's small stir) to full.</summary>
		public static float Size(float bodySize, float wake)
		{
			float body = bodySize < 0.5f ? 0.5f : (bodySize > 2f ? 2f : bodySize);
			return body * 0.35f * (0.5f + 0.5f * Clamp01(wake));
		}

		private static float Clamp01(float v)
		{
			return v < 0f || float.IsNaN(v) ? 0f : (v > 1f ? 1f : v);
		}
	}

	/// <summary>LIQUID_WAKES_FIX_FOOTPRINTS_GONE_QUIET: how many wakes (one V = one count) RM_LiquidSurface has thrown, per
	/// terrain defName under the wader, since the game started or the last <see cref="Reset"/>. The instrument for live row
	/// W1_wakes_terrain_walked (src/RimMandrake/FlowWorks/northstar/wakes_checks.py), read through jawa/static_call; a fleck
	/// leaves no other trace. Main thread only (MapComponentTick). Verse-free so the C# selftest covers it.</summary>
	public static class RM_WakeCount
	{
		private static readonly Dictionary<string, int> byTerrain = new Dictionary<string, int>();

		public static void Note(string terrain)
		{
			if (string.IsNullOrEmpty(terrain))
			{
				return;
			}
			byTerrain[terrain] = On(terrain) + 1;
		}

		/// <summary>Wakes thrown over <paramref name="terrain"/> (0 when none, or unknown).</summary>
		public static int On(string terrain)
		{
			return terrain != null && byTerrain.TryGetValue(terrain, out int n) ? n : 0;
		}

		public static int Total()
		{
			int n = 0;
			foreach (int v in byTerrain.Values)
			{
				n += v;
			}
			return n;
		}

		/// <summary>"RM_TarShallow=2;RM_WaterThin=5", sorted by defName; "" when nothing was thrown.</summary>
		public static string Render()
		{
			List<string> keys = new List<string>(byTerrain.Keys);
			keys.Sort(System.StringComparer.Ordinal);
			StringBuilder sb = new StringBuilder();
			foreach (string k in keys)
			{
				sb.Append(sb.Length == 0 ? "" : ";").Append(k).Append('=').Append(byTerrain[k]);
			}
			return sb.ToString();
		}

		/// <summary>Clear every count; returns the total cleared.</summary>
		public static int Reset()
		{
			int n = Total();
			byTerrain.Clear();
			return n;
		}
	}
}
