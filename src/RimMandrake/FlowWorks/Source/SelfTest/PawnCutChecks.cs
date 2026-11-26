// RIMMANDRAKE_DRAW_PAWN_OWN_PICTURE_CUT_AT_LIQUID_SURFACE_NOT_ICON (owner's walk 2026-11-22; card: "A now, rest next"): a pawn
// in a liquid is its own picture cut at the surface, the line placed by body landmarks. These checks pin the pure rule
// (RM_PawnCutMath): how much of which pawn shows at which depth, standing, lying, carried, by body size; and the cut's
// geometry. Each case has a can-fail. NOT proven here: the pictures on screen (the live matrix,
// northstar/pawn_in_liquid_matrix.py).
using System;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class PawnCutChecks
	{
		private static void Assert(bool ok, string msg)
		{
			if (!ok) throw new Exception(msg);
		}

		private const float Water = 0.45f, Tar = 0f, Lie = RM_UnderLiquid.CorpseMetres;

		public static void Run(Action<string, Action> Case)
		{
			// RIMMANDRAKE_SHIFT_SUNK_BODY_OFF_THE_EAST_PIT_WALL (his walk 2026-11-25, station 33): a body lying on a pit's east
			// column square drew its 1.5-square picture half a square onto the east wall
			Case("PitDraw_lying_body_kept_inside_the_dug_squares", () =>
			{
				const float H = RM_PitDrawMath.LyingHalfLength;
				// east column of a pit (east neighbour not dug): the picture's east end at the pit edge (x = 11)
				float x = RM_PitDrawMath.LyingInsideX(10.5f, 10, eastDug: false, westDug: true);
				Assert(Math.Abs(x + H - 11f) < 1e-4f, "east wall: the body's east end is on the pit edge, not past it: " + x);
				x = RM_PitDrawMath.LyingInsideX(10.5f, 10, eastDug: true, westDug: false);
				Assert(Math.Abs(x - H - 10f) < 1e-4f, "west wall: the body's west end is on the pit edge: " + x);
				Assert(RM_PitDrawMath.LyingInsideX(10.5f, 10, true, true) == 10.5f, "a middle square: no shift");
				Assert(RM_PitDrawMath.LyingInsideX(10.5f, 10, false, false) == 10.5f, "a 1-wide pit: nothing fits, no shift");
				Assert(RM_PitDrawMath.LyingInsideX(10.2f, 10, false, true) == 10.2f, "a body already inside is not moved");
			});

			Case("PawnCut_human_waist_not_chin", () =>
			{
				// 1 m of water on a 1.75 m colonist: the straight law put the line at 57% of her picture, over her chin (0.52)
				float p = RM_PawnCutMath.PictureShare(true, 1f, 1.75f);
				Assert(p > RM_PawnCutMath.HumanPicture[2] && p < RM_PawnCutMath.HumanPicture[4],
					"can-fail: 1 m on 1.75 m is between the hips and the shoulders, not at the chin (" + p + ")");
				Assert(RM_PawnCutMath.PictureShare(true, 0.9f * 1.75f, 1.75f) > RM_PawnCutMath.HumanPicture[5],
					"can-fail: at the drowning line (0.9 H) the line is over the chin: her mouth is under");
				Assert(RM_PawnCutMath.PictureShare(false, 1f, 1.75f) == 1f / 1.75f, "can-fail: a non-humanlike keeps the straight share");
			});
			Case("PawnCut_share_rises_with_depth_and_ends_whole", () =>
			{
				foreach (bool human in new[] { true, false })
				{
					Assert(RM_PawnCutMath.PictureShare(human, 0f, 1.75f) == 0f, "can-fail: dry: nothing under");
					Assert(RM_PawnCutMath.PictureShare(human, 1.75f, 1.75f) == 1f && RM_PawnCutMath.PictureShare(human, 3f, 1.75f) == 1f,
						"can-fail: over her height: all under");
					float prev = 0f;
					for (int i = 1; i < 35; i++)
					{
						float p = RM_PawnCutMath.PictureShare(human, i * 0.05f, 1.75f);
						Assert(p > prev && p <= 1f, "can-fail: deeper never shows more (" + human + ", " + i + ")");
						prev = p;
					}
				}
				Assert(RM_PawnCutMath.HumanHeight.Length == RM_PawnCutMath.HumanPicture.Length, "can-fail: one picture landmark per height landmark");
			});
			Case("PawnCut_body_size_sets_the_line", () =>
			{
				// a small animal (0.5 m), a colonist (1.75 m) and a huge one (4 m) in the same 0.5 m of water
				float small = RM_PawnCutMath.PictureShare(false, 0.5f, 0.5f), mid = RM_PawnCutMath.PictureShare(false, 0.5f, 1.75f),
					huge = RM_PawnCutMath.PictureShare(false, 0.5f, 4f);
				Assert(small == 1f && mid > huge && huge > 0f, "can-fail: the same depth covers a small body whole and a huge one least");
			});
			Case("PawnCut_standing_cut_clear_and_opaque", () =>
			{
				Assert(RM_PawnCutMath.Decide(false, false, true, 0f, 1.75f, Lie, Water, out _, out _) == RM_PawnCutMath.Mode.Whole,
					"can-fail: dry: whole");
				Assert(RM_PawnCutMath.Decide(false, false, true, 1f, 1.75f, Lie, Water, out float l1, out float t1) == RM_PawnCutMath.Mode.Cut
					&& l1 > 0f && l1 < 1f && t1 == 1f, "can-fail: waist deep in water: cut, the lower part tinted");
				Assert(RM_PawnCutMath.Decide(false, false, true, 1f, 1.75f, Lie, Tar, out float l2, out _) == RM_PawnCutMath.Mode.Cut
					&& l2 == l1, "can-fail: waist deep in tar: cut at the same line (the lower part is not drawn)");
				Assert(RM_PawnCutMath.Decide(false, false, true, 2f, 1.75f, Lie, Water, out _, out _) == RM_PawnCutMath.Mode.Tinted,
					"can-fail: wholly under clear water: her whole picture, dimmed");
				Assert(RM_PawnCutMath.Decide(false, false, true, 2f, 1.75f, Lie, Tar, out _, out _) == RM_PawnCutMath.Mode.Hidden,
					"can-fail: wholly under tar: hidden (tar is opaque)");
			});
			Case("PawnCut_lying_is_never_cut", () =>
			{
				// GPT's warning (design section 10): a horizontal line across a lying body cuts through her face
				for (int i = 0; i <= 40; i++)
				{
					foreach (float c in new[] { Water, Tar })
					{
						var m = RM_PawnCutMath.Decide(true, false, true, i * 0.05f, 1.75f, Lie, c, out float line, out _);
						Assert(m != RM_PawnCutMath.Mode.Cut && line == 0f, "can-fail: lying at " + i * 0.05f + " m was cut");
					}
				}
				Assert(RM_PawnCutMath.Decide(true, false, true, Lie * 0.5f, 1.75f, Lie, Water, out _, out float half) == RM_PawnCutMath.Mode.Tinted
					&& Math.Abs(half - 0.5f) < 1e-4f, "can-fail: half under her lying height: tinted half way");
				Assert(RM_PawnCutMath.Decide(true, false, true, Lie * 0.5f, 1.75f, Lie, Tar, out _, out float halfTar) == RM_PawnCutMath.Mode.Tinted
					&& halfTar > 0f && halfTar < half, "can-fail: half in tar: tinted, still her (not black)");
				Assert(RM_PawnCutMath.Decide(true, false, true, 1f, 1.75f, Lie, Water, out _, out float all) == RM_PawnCutMath.Mode.Tinted && all == 1f,
					"can-fail: lying under 1 m of water: whole and dimmed");
				Assert(RM_PawnCutMath.Decide(true, false, true, 1f, 1.75f, Lie, Tar, out _, out _) == RM_PawnCutMath.Mode.Hidden,
					"can-fail: lying under 1 m of tar: hidden");
			});
			Case("PawnCut_carried_is_whole", () =>
			{
				foreach (bool lying in new[] { false, true })
				{
					Assert(RM_PawnCutMath.Decide(lying, true, true, 1.5f, 1.75f, Lie, Tar, out _, out _) == RM_PawnCutMath.Mode.Whole,
						"can-fail: a carried pawn is not in the liquid; her carrier is");
				}
			});
			Case("PawnCut_tint_factor", () =>
			{
				var water = new RM_UnderLiquid.Float3(0.2f, 0.4f, 0.6f);
				var none = RM_PawnCutMath.TintFactor(water, 1f, 1f);
				Assert(none.r == 1f && none.g == 1f && none.b == 1f, "can-fail: fully seen: own colour");
				var full = RM_PawnCutMath.TintFactor(water, 0f, 1f);
				Assert(Math.Abs(full.r - 0.2f) < 1e-5f && Math.Abs(full.b - 0.6f) < 1e-5f, "can-fail: not seen at all: the liquid's colour");
				var mid = RM_PawnCutMath.TintFactor(water, 0.5f, 1f);
				Assert(mid.r < 1f && mid.r > 0.2f, "can-fail: half seen: between");
			});
			Case("PawnCut_clip_triangle_splits_area", () =>
			{
				// a unit square (two triangles) in local x,z, cut by the world line z = 0.3 (plane z - 0.3)
				float[] a = { 0f, 0f, 0f, 0f, 0f }, b = { 0f, 0f, 1f, 0f, 1f }, c = { 1f, 0f, 1f, 1f, 1f }, d = { 1f, 0f, 0f, 1f, 0f };
				float up = 0f, lo = 0f, vUpMin = 9f, vLoMax = -9f;
				float[] poly = new float[RM_PawnCutMath.MaxPolyCorners * 5];
				foreach (var tri in new[] { new[] { a, b, c }, new[] { a, c, d } })
				{
					int n = RM_PawnCutMath.ClipTriangle(tri[0], tri[1], tri[2], 0f, 0f, 1f, -0.3f, true, poly);
					up += Area(poly, n);
					for (int i = 0; i < n; i++) vUpMin = Math.Min(vUpMin, poly[i * 5 + 4]);
					n = RM_PawnCutMath.ClipTriangle(tri[0], tri[1], tri[2], 0f, 0f, 1f, -0.3f, false, poly);
					lo += Area(poly, n);
					for (int i = 0; i < n; i++) vLoMax = Math.Max(vLoMax, poly[i * 5 + 4]);
				}
				Assert(Math.Abs(up - 0.7f) < 1e-4f && Math.Abs(lo - 0.3f) < 1e-4f, "can-fail: the cut keeps 0.7 above and 0.3 below (" + up + ", " + lo + ")");
				Assert(Math.Abs(vUpMin - 0.3f) < 1e-4f && Math.Abs(vLoMax - 0.3f) < 1e-4f, "can-fail: the picture is cut at its own row 0.3, not stretched");
				Assert(RM_PawnCutMath.ClipTriangle(a, b, c, 0f, 0f, 1f, 5f, true, poly) == 3
					&& RM_PawnCutMath.ClipTriangle(a, b, c, 0f, 0f, 1f, 5f, false, poly) == 0, "can-fail: a line under it keeps all above, none below");
				// a turned node (a lying body's part): the cut is in world space, through the node's matrix (here x counts too)
				int k = RM_PawnCutMath.ClipTriangle(a, b, c, 0.7071f, 0f, 0.7071f, -0.7071f, true, poly);
				Assert(k >= 3, "can-fail: a slanted plane still cuts");
			});
			Case("PawnCut_node_extent", () =>
			{
				// the vanilla female body: a 1.5 quad (local z -0.75..0.75, v 0..1), pixels in rows 0.117..0.703, at body z 10
				RM_PawnCutMath.NodeExtent(-0.75f, 0.75f, 0f, 1f, 0.117f, 0.703f, 1f, 10f, out float lo, out float hi);
				Assert(Math.Abs(lo - (10f - 0.5745f)) < 1e-3f && Math.Abs(hi - (10f + 0.3045f)) < 1e-3f,
					"can-fail: the drawn pixels, not the quad (" + lo + ", " + hi + ")");
				Assert(RM_PawnCutMath.LineZ(lo, hi, 0f) == lo && Math.Abs(RM_PawnCutMath.LineZ(lo, hi, 1f) - hi) < 1e-5f, "can-fail: line ends");
			});
		}

		private static float Area(float[] p, int n)
		{
			float s = 0f;
			for (int i = 0; i < n; i++)
			{
				int j = (i + 1) % n;
				s += p[i * 5] * p[j * 5 + 2] - p[j * 5] * p[i * 5 + 2];
			}
			return Math.Abs(s) * 0.5f;
		}
	}
}
