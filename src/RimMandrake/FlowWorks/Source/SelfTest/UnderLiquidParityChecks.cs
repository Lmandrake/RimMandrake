// RIMMANDRAKE_FIX_BIG_PIT_SCENE_BUILDINGS_STAY_DRY, RIMMANDRAKE_TUNE_WATER_CLARITY_DARKER_AND_HALF_AS_OPAQUE and
// RIMMANDRAKE_TINT_PIT_WATER_READS_AS_WATER_NOT_MUD: RM_UnderLiquid
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
			{ 0.45f, 0.01f, 0.99685f },
			{ 0.45f, 0.25f, 0.92225f },
			{ 0.45f, 0.5f, 0.84654f },
			{ 0.45f, 1.0f, 0.70163f },
			{ 0.45f, 1.5f, 0.5661f },
			{ 0.45f, 2.0f, 0.44104f },
			{ 0.45f, 3.0f, 0.22923f },
			{ 0.45f, 3.5f, 0.14897f },
			{ 0.45f, 4.0f, 0.1f },
			{ 0.45f, 6.0f, 0.1f },
			{ 0.25f, 0.0f, 1.0f },
			{ 0.25f, 0.01f, 0.99454f },
			{ 0.25f, 0.25f, 0.86632f },
			{ 0.25f, 0.5f, 0.739f },
			{ 0.25f, 1.0f, 0.50566f },
			{ 0.25f, 1.5f, 0.30612f },
			{ 0.25f, 2.0f, 0.15282f },
			{ 0.25f, 3.0f, 0.1f },
			{ 0.25f, 3.5f, 0.1f },
			{ 0.25f, 4.0f, 0.1f },
			{ 0.25f, 6.0f, 0.1f },
			{ 0.0f, 0.0f, 1.0f },
			{ 0.0f, 0.01f, 0.0f },
			{ 0.0f, 0.25f, 0.0f },
			{ 0.0f, 0.5f, 0.0f },
			{ 0.0f, 1.0f, 0.0f },
			{ 0.0f, 1.5f, 0.0f },
			{ 0.0f, 2.0f, 0.0f },
			{ 0.0f, 3.0f, 0.0f },
			{ 0.0f, 3.5f, 0.0f },
			{ 0.0f, 4.0f, 0.0f },
			{ 0.0f, 6.0f, 0.0f }
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
				RM_UnderLiquid.FullMetres = RM_UnderLiquid.DefaultFullMetres;
				for (int i = 0; i < Golden.GetLength(0); i++)
				{
					float s = RM_UnderLiquid.Seen(Golden[i, 0], Golden[i, 1]);
					Assert(Near(s, Golden[i, 2]), "can-fail: Seen(" + Golden[i, 0] + ", " + Golden[i, 1] + ") = " + s + ", model " + Golden[i, 2]);
				}
				// the settings move the law: strength 1 hides 4 m of water whole; full at 8 m leaves 4 m well short of full
				RM_UnderLiquid.DeepOpacity = 1f;
				Assert(RM_UnderLiquid.Seen(0.45f, 4f) < 0.01f, "can-fail: DeepOpacity 1 hides 4 m of water whole");
				RM_UnderLiquid.DeepOpacity = RM_UnderLiquid.DefaultDeepOpacity;
				RM_UnderLiquid.FullMetres = 8f;
				Assert(RM_UnderLiquid.Seen(0.45f, 4f) > 0.2f, "can-fail: full at 8 m shows a 4 m floor more");
				RM_UnderLiquid.FullMetres = RM_UnderLiquid.DefaultFullMetres;
				float s4 = 1f - RM_UnderLiquid.Seen(0.45f, 4f), s05 = 1f - RM_UnderLiquid.Seen(0.45f, 0.5f);
				Assert(s4 > 0.85f && s4 < 0.95f && s05 < 0.2f, "can-fail: shipped water is a body at 4 m (" + s4 + "), faint at 0.5 m (" + s05 + ")");
			});
			Case("UnderLiquid_buildings_shadows_labels_match_the_model", () =>
			{
				RM_UnderLiquid.ThingShadowAlpha = RM_UnderLiquid.DefaultThingShadowAlpha;
				Assert(Near(RM_UnderLiquid.BuildingMetres(0.4f), 0.8f) && RM_UnderLiquid.BuildingMetres(0f) == RM_UnderLiquid.MinThingMetres,
					"can-fail: a 0.4-fill bed stands 0.8 m; a 0-fill building the floor minimum");
				Assert(RM_UnderLiquid.Share(2f, 0f, RM_UnderLiquid.BuildingMetres(0.4f)) == 1f, "can-fail: 2 m of water covers a bed");
				Assert(Near(RM_UnderLiquid.ThingShadow(0.45f, 0f), RM_UnderLiquid.ThingShadowAlpha), "can-fail: a dry pit's floor shadow at full");
				Assert(RM_UnderLiquid.ThingShadow(0f, 0.5f) == 0f, "can-fail: tar hides the floor shadow");
				Assert(Near(RM_UnderLiquid.ThingShadow(0.45f, 2f), RM_UnderLiquid.ThingShadowAlpha),
					"can-fail: under clear liquid the shadow keeps its alpha (the sheet over it hides it by the law)");
				RM_UnderLiquid.Darken = RM_UnderLiquid.DefaultDarken;
				RM_UnderLiquid.Float3 b = RM_UnderLiquid.Body(RM_UnderLiquid.WaterColour);
				Assert(b.b > b.g && b.g > b.r && b.r + b.g + b.b < 0.75f,
					"can-fail: fresh water's body is a dark blue (" + b.r + ", " + b.g + ", " + b.b + ")");
				Assert(RM_UnderLiquid.LabelAlpha(0.45f, 0.1f, 0.3f) == 1f, "can-fail: a label over a thing poking out is whole");
				Assert(RM_UnderLiquid.LabelAlpha(0f, 1f, 0.3f) == 0f, "can-fail: a label over a thing under tar is hidden");
				float l = RM_UnderLiquid.LabelAlpha(0.45f, 2f, 0.3f);
				Assert(l > 0f && l < 1f, "can-fail: a label over a thing under clear water fades (" + l + ")");
			});
			Case("UnderLiquid_flat_things_cast_no_floor_shadow_and_edges_are_soft", () =>
			{
				// RIMMANDRAKE_REMOVE_DARK_SQUARE_AROUND_SUNK_GEYSER_UNWELCOME_BOX: a geyser or rug (fill 0, no vanilla shadow)
				// casts none; a bed, bench, battery or lamp does
				Assert(!RM_UnderLiquid.CastsFloorShadow(0f, 0f, false), "can-fail: a geyser or rug casts no floor shadow");
				Assert(!RM_UnderLiquid.CastsFloorShadow(0.15f, 0f, false), "can-fail: a 0.15-fill flat thing casts none");
				Assert(RM_UnderLiquid.CastsFloorShadow(0.4f, 0f, false), "can-fail: a 0.4-fill bed casts one");
				Assert(RM_UnderLiquid.CastsFloorShadow(0.1f, 0.2f, false), "can-fail: a sun-shadow caster casts one");
				Assert(RM_UnderLiquid.CastsFloorShadow(0f, 0f, true), "can-fail: a thing with vanilla shadowData casts one");
				// the shadow's edge is feathered to nothing, never a hard rectangle
				Assert(RM_UnderLiquid.ShadowFeather(0f, 0.5f) == 0f && RM_UnderLiquid.ShadowFeather(0.5f, 1f) == 0f,
					"can-fail: the shadow is 0 at its edge");
				Assert(RM_UnderLiquid.ShadowFeather(0.5f, 0.5f) == 1f, "can-fail: the shadow is whole at its middle");
				float a = RM_UnderLiquid.ShadowFeather(0.05f, 0.5f), b = RM_UnderLiquid.ShadowFeather(0.15f, 0.5f);
				Assert(a > 0f && a < b && b < 1f, "can-fail: the shadow rises smoothly from its edge (" + a + ", " + b + ")");
			});
		}
	}
}
