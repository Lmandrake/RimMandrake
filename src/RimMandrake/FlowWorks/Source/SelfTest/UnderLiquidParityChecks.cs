// RIMMANDRAKE_FIX_BIG_PIT_SCENE_BUILDINGS_STAY_DRY and RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE: RM_UnderLiquid
// against its offline twin, model/underliquid.py. The golden table below is WRITTEN by
// selftest_flowworks_underliquid_parity.py --write from the model (that selftest also fails when it drifts); these checks
// fail when the C# law drifts from it. NOT proven here: the pictures on screen (LIVE_LOOK_CHECKLIST.md).
using System;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class UnderLiquidParityChecks
	{
		// BEGIN GOLDEN (selftest_flowworks_underliquid_parity.py --write)
		internal static readonly float[,] Golden =
		{
			{ 0.45f, 0.0f, 1.0f },
			{ 0.45f, 0.01f, 0.87508f },
			{ 0.45f, 0.25f, 0.80967f },
			{ 0.45f, 0.5f, 0.75363f },
			{ 0.45f, 1.0f, 0.67014f },
			{ 0.45f, 1.5f, 0.61413f },
			{ 0.45f, 2.0f, 0.57656f },
			{ 0.45f, 3.0f, 0.53445f },
			{ 0.45f, 4.0f, 0.5155f },
			{ 0.25f, 0.0f, 1.0f },
			{ 0.25f, 0.01f, 0.80355f },
			{ 0.25f, 0.25f, 0.71764f },
			{ 0.25f, 0.5f, 0.65389f },
			{ 0.25f, 1.0f, 0.57695f },
			{ 0.25f, 1.5f, 0.53847f },
			{ 0.25f, 2.0f, 0.51924f },
			{ 0.25f, 3.0f, 0.50481f },
			{ 0.25f, 4.0f, 0.5012f },
			{ 0.0f, 0.0f, 1.0f },
			{ 0.0f, 0.01f, 0.0f },
			{ 0.0f, 0.25f, 0.0f },
			{ 0.0f, 0.5f, 0.0f },
			{ 0.0f, 1.0f, 0.0f },
			{ 0.0f, 1.5f, 0.0f },
			{ 0.0f, 2.0f, 0.0f },
			{ 0.0f, 3.0f, 0.0f },
			{ 0.0f, 4.0f, 0.0f }
		};
		// END GOLDEN

		private static void Assert(bool ok, string msg)
		{
			if (!ok) throw new Exception(msg);
		}

		private static bool Near(float a, float b, float eps = 2e-5f) => Math.Abs(a - b) < eps;

		public static void Run(Action<string, Action> Case)
		{
			Case("UnderLiquid_seen_matches_the_offline_model", () =>
			{
				RM_UnderLiquid.DeepOpacity = RM_UnderLiquid.DefaultDeepOpacity;
				for (int i = 0; i < Golden.GetLength(0); i++)
				{
					float s = RM_UnderLiquid.Seen(Golden[i, 0], Golden[i, 1]);
					Assert(Near(s, Golden[i, 2]), "can-fail: Seen(" + Golden[i, 0] + ", " + Golden[i, 1] + ") = " + s + ", model " + Golden[i, 2]);
				}
				// the setting moves the law: fully opaque at depth is the old law's ceiling
				RM_UnderLiquid.DeepOpacity = 1f;
				Assert(RM_UnderLiquid.Seen(0.45f, 4f) < 0.05f, "can-fail: DeepOpacity 1 hides 4 m of water almost whole");
				RM_UnderLiquid.DeepOpacity = RM_UnderLiquid.DefaultDeepOpacity;
				Assert(RM_UnderLiquid.Seen(0.45f, 4f) > 0.45f, "can-fail: shipped water still shows a 4 m floor about half");
			});
			Case("UnderLiquid_buildings_shadows_labels_match_the_model", () =>
			{
				RM_UnderLiquid.ThingShadowAlpha = RM_UnderLiquid.DefaultThingShadowAlpha;
				Assert(Near(RM_UnderLiquid.BuildingMetres(0.4f), 0.8f) && RM_UnderLiquid.BuildingMetres(0f) == RM_UnderLiquid.MinThingMetres,
					"can-fail: a 0.4-fill bed stands 0.8 m; a 0-fill building the floor minimum");
				Assert(RM_UnderLiquid.Share(2f, 0f, RM_UnderLiquid.BuildingMetres(0.4f)) == 1f, "can-fail: 2 m of water covers a bed");
				Assert(Near(RM_UnderLiquid.ThingShadow(0.45f, 0f), RM_UnderLiquid.ThingShadowAlpha), "can-fail: a dry pit's floor shadow at full");
				Assert(RM_UnderLiquid.ThingShadow(0f, 0.5f) == 0f, "can-fail: tar hides the floor shadow");
				Assert(Near(RM_UnderLiquid.ThingShadow(0.45f, 2f), RM_UnderLiquid.ThingShadowAlpha * RM_UnderLiquid.Seen(0.45f, 2f)),
					"can-fail: the shadow is seen through the liquid by the law");
				Assert(RM_UnderLiquid.LabelAlpha(0.45f, 0.1f, 0.3f) == 1f, "can-fail: a label over a thing poking out is whole");
				Assert(RM_UnderLiquid.LabelAlpha(0f, 1f, 0.3f) == 0f, "can-fail: a label over a thing under tar is hidden");
				float l = RM_UnderLiquid.LabelAlpha(0.45f, 2f, 0.3f);
				Assert(l > 0f && l < 1f, "can-fail: a label over a thing under clear water fades (" + l + ")");
			});
		}
	}
}
