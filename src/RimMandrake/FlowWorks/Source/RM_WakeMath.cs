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
}
