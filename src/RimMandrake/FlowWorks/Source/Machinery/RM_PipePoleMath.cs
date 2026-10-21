using System;

namespace RimMandrake.FlowWorks.Machinery
{
	// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P3;
	// widths: design/RimMandrake/flowworks_line_widths_2026-10-20.md): the pipe pole's numbers. Pure: no Verse, no UnityEngine,
	// so the offline SelfTest compiles this file itself (PipePoleChecks.cs). The span machinery is Gimme Some Slack's aerial
	// lines (AerialLineKind.Pipe); these values are what FlowWorks hands it (RM_PipePoles.RegisterWithGss).

	public static class RM_PipePoleMath
	{
		/// <summary>Owner, pipes-across-pits ruling P3: "Max span and sag are Mod-Settings tuning; proposal ... max span 12".</summary>
		public const float MaxSpanDefault = 12f;
		public const float MaxSpanMin = 4f, MaxSpanMax = 20f;
		/// <summary>Owner by card 2026-10-20 (line widths spec): "about a third of GSS wire sag, about 2% of span" (the ruled
		/// design's earlier proposal was 3 %; the card is later and specific).</summary>
		public const float SagDefault = 0.02f;
		public const float SagMin = 0f, SagMax = 0.06f;
		/// <summary>Owner's widths card: rigid pipe 30 cm, about 14 px of a 64 px cell; the pipe atlas measures 0.227 cell.</summary>
		public const float SpanWidthCells = 0.22f;

		private static float Clamp(float v, float lo, float hi) => float.IsNaN(v) ? lo : (v < lo ? lo : (v > hi ? hi : v));

		/// <summary>The longest span the slider allows, whole cells.</summary>
		public static float ClampSpan(float v) => (float)Math.Round(Clamp(v, MaxSpanMin, MaxSpanMax));

		/// <summary>The sag factor the slider allows.</summary>
		public static float ClampSag(float v) => Clamp(v, SagMin, SagMax);

		/// <summary>How far a span of this length hangs below its chord at mid-span, cells (GSS SpanCurve: sag = factor x |AB|).</summary>
		public static double SagDepth(double spanLength, float sag) => Math.Max(0, spanLength) * ClampSag(sag);

		/// <summary>May a span of (dx, dz) cells be strung at this max-span setting? (Euclidean, inclusive: GSS AerialMath.InRange.)</summary>
		public static bool InSpan(int dx, int dz, float maxSpan)
		{
			float r = ClampSpan(maxSpan);
			return (long)dx * dx + (long)dz * dz <= r * r + 1e-6;
		}

		/// <summary>P3 "Not ground, not support": a pole span is never walking ground, a climb exit, a deck or part of pawn
		/// topology. A span is two link records on two pole comps (GSS SpanLink), never a Thing on the cells under it, so the
		/// cells it crosses keep exactly the surface they had. This is the rule the map side keeps; the SelfTest checks the
		/// pawn-topology readers never look at aerial spans.</summary>
		public static LineSurface SurfaceUnderSpan(LineSurface ground) => ground;

		public static string SpanLabel(float maxSpan) => "Longest pipe span: " + ClampSpan(maxSpan).ToString("0") + " cells";

		public static string SagLabel(float sag) => "Pipe span sag: " + (ClampSag(sag) * 100f).ToString("0.0") + "% of its length";
	}
}
