// RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL (owner 2026-11-12: "a ladder hanging into water is shown entirely over the
// water regardless of depth. The water really should go up to some level on the ladder as though it is part submerged.
// Same for spikes and other pit installations."). Offline checks on RM_SubmergeMath: the share of a fitting the liquid
// covers follows the true level (notches, part-notch included) against depth, and the sprite cut keeps the right part of the texture. Each case has a can-fail.
// NOT proven here: the cut sprites on screen (RM_SubmergeDraw.PrintCut, Building_RM_Spikes.DrawAt); live proof owed
// (northstar/wall_art_scene.py submerge).
using System;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class SubmergeDrawChecks
	{
		private static void Assert(bool ok, string msg)
		{
			if (!ok) throw new Exception(msg);
		}

		private static bool Near(float a, float b, float eps = 1e-4f) => Math.Abs(a - b) < eps;

		public static void Run(Action<string, Action> Case)
		{
			Case("Submerge_ladder_share_follows_fill_against_depth", () =>
			{
				// D4 pit, ladder hung on the north wall (drop 4)
				Assert(RM_SubmergeMath.LadderInPitShare(0, 4, 0) == 0f, "can-fail: dry: nothing covered");
				float f1 = RM_SubmergeMath.LadderInPitShare(0, 4, 1);
				Assert(f1 > 0.2f && f1 < 0.4f, "can-fail: depth 4 at fill 1: about the bottom quarter covered (got " + f1 + ")");
				float f2 = RM_SubmergeMath.LadderInPitShare(0, 4, 2), f3 = RM_SubmergeMath.LadderInPitShare(0, 4, 3);
				Assert(f1 < f2 && f2 < f3 && f3 < 1f, "can-fail: rises with every level");
				Assert(RM_SubmergeMath.LadderInPitShare(0, 4, 4) == 1f && RM_SubmergeMath.LadderInPitShare(0, 4, 9) == 1f,
					"can-fail: brim-full: only what stands above the surface shows");
				// the waterline is the wall face's own (the ladder's waterline meets the wall's)
				Assert(Near(RM_SubmergeMath.LadderWaterline(0, 4, 1), 1f - RM_WallFaceMath.NorthFaceHeight(3)),
					"can-fail: north waterline = top of the face left showing");
				Assert(Near(RM_SubmergeMath.LadderWaterline(1, 4, 1), 1f - RM_WallFaceMath.SideFaceWidth(3)), "can-fail: east waterline");
				Assert(Near(RM_SubmergeMath.LadderWaterline(3, 4, 1), RM_WallFaceMath.SideFaceWidth(3)), "can-fail: west waterline");
				float e1 = RM_SubmergeMath.LadderInPitShare(1, 4, 1), w1 = RM_SubmergeMath.LadderInPitShare(3, 4, 1);
				Assert(e1 > 0f && e1 < 1f && Near(e1, w1), "can-fail: east and west mirror");
				Assert(RM_SubmergeMath.LadderWaterline(2, 4, 3) == RM_SubmergeMath.NoCut, "can-fail: hung south: only the rim top shows, never cut");
				Assert(RM_SubmergeMath.LadderWaterline(0, 4, 0) == RM_SubmergeMath.NoCut, "can-fail: dry: no cut at all (costs nothing)");
				Assert(RM_SubmergeMath.LadderFrom(0) == RM_SubmergeMath.FromSouth && RM_SubmergeMath.LadderFrom(1) == RM_SubmergeMath.FromWest
					&& RM_SubmergeMath.LadderFrom(3) == RM_SubmergeMath.FromEast, "can-fail: cut from the pit side");
			});
			Case("Submerge_true_level_not_the_integer_fill", () =>
			{
				// coordinator 2026-11-12: one notch = 0.5 m; depth and fill in notches; each cell carries a part-notch below the
				// whole-notch fill: the waterline follows the true level
				float f1 = RM_SubmergeMath.LadderInPitShare(0, 4, 1f), f2 = RM_SubmergeMath.LadderInPitShare(0, 4, 2f);
				float f15 = RM_SubmergeMath.LadderInPitShare(0, 4, 1.5f);
				Assert(f1 < f15 && f15 < f2, "can-fail: a part-notch raises the waterline between the whole notches (got " + f15 + ")");
				Assert(RM_SubmergeMath.LadderInPitShare(0, 4, 0.25f) > 0f, "can-fail: a quarter notch already wets the ladder foot");
				Assert(Near(RM_SubmergeMath.FaceAt(RM_WallFaceMath.NorthByDrop, 3f), RM_WallFaceMath.NorthFaceHeight(3))
					&& Near(RM_SubmergeMath.FaceAt(RM_WallFaceMath.SideByDrop, 2f), RM_WallFaceMath.SideFaceWidth(2))
					&& Near(RM_SubmergeMath.FaceAt(RM_WallFaceMath.NorthByDrop, 9f), RM_WallFaceMath.NorthFaceHeight(9)),
					"can-fail: at whole notches the face read is the wall's own");
				Assert(Near(RM_SubmergeMath.StakeShare(0.5f), 0.25f) && Near(RM_SubmergeMath.RampShare(1.5f, 3), 0.5f),
					"can-fail: stakes and ramp follow the part-notch");
				Assert(RM_SubmergeMath.LevelNote(0) == 0 && RM_SubmergeMath.LevelNote(0.01) == 1 && RM_SubmergeMath.LevelNote(2.0) == 8
					&& RM_SubmergeMath.LevelNote(2.1) == 8 && RM_SubmergeMath.LevelNote(2.2) == 9 && RM_SubmergeMath.LevelNote(999) == 255,
					"can-fail: quarter-notch notes: 0 only dry, a trace is 1, a few decilitres never re-mesh");
				Assert(RM_SubmergeMath.NoteLevel(RM_SubmergeMath.LevelNote(3.0)) == 3f, "can-fail: a whole notch draws as itself");
			});
			Case("Submerge_span_share_of_a_sprite", () =>
			{
				// the north ladder sprite spans cell-local z 0.50..1.105: a waterline at 0.65 covers a quarter of it
				float s = RM_SubmergeMath.SpanShare(0.5f, 1.105f, 0.65f, true);
				Assert(Near(s, 0.15f / 0.605f), "can-fail: covered from the foot");
				Assert(RM_SubmergeMath.SpanShare(0.5f, 1.105f, 0.3f, true) == 0f, "can-fail: waterline below the sprite");
				Assert(RM_SubmergeMath.SpanShare(0.5f, 1.105f, 1.2f, true) == 1f, "can-fail: waterline over the sprite");
				Assert(Near(RM_SubmergeMath.SpanShare(0.75f, 1.06f, 0.83f, false), 0.23f / 0.31f), "can-fail: covered from the high end");
				Assert(RM_SubmergeMath.SpanShare(0f, 1f, RM_SubmergeMath.NoCut, true) == 0f, "can-fail: no cut");
			});
			Case("Submerge_ramp_and_stakes", () =>
			{
				Assert(RM_SubmergeMath.RampShare(0, 4) == 0f, "can-fail: dry ramp whole");
				Assert(Near(RM_SubmergeMath.RampShare(1, 4), 0.25f), "can-fail: a quarter of a 4-level ramp under 1 level");
				Assert(RM_SubmergeMath.RampShare(4, 4) == 1f && RM_SubmergeMath.RampShare(2, 0) == 1f, "can-fail: brim-full ramp gone");
				Assert(RM_SubmergeMath.StakeShare(0) == 0f, "can-fail: dry stakes whole");
				float half = RM_SubmergeMath.StakeShare(1);
				Assert(Near(half, RM_Volume.MetresPerLevel / RM_SpikeDrawMath.SubmergeMetres) && half > 0f && half < 1f,
					"can-fail: one level covers its metres of a 1 m stake");
				Assert(RM_SubmergeMath.StakeShare(2) == 1f, "can-fail: gone at 1 m, as the old fade");
			});
			Case("Submerge_step_is_zero_and_full_only_at_the_ends", () =>
			{
				Assert(RM_SubmergeMath.Step(0f) == 0 && RM_SubmergeMath.Step(-1f) == 0, "can-fail: 0 only when dry");
				Assert(RM_SubmergeMath.Step(0.001f) == 1, "can-fail: a sliver still cuts");
				Assert(RM_SubmergeMath.Step(0.999f) == RM_SubmergeMath.Steps - 1, "can-fail: never full before 1");
				Assert(RM_SubmergeMath.Step(1f) == RM_SubmergeMath.Steps, "can-fail: full at 1");
			});
			Case("Submerge_cut_keeps_the_dry_part_of_the_texture", () =>
			{
				// PrintPlane corners (-x-z, -x+z, +x+z, +x-z), default uvs (0,0),(0,1),(1,1),(1,0)
				float[] uv = { 0f, 0f, 0f, 1f, 1f, 1f, 1f, 0f };
				float x0 = 0f, z0 = 0f, x1 = 2f, z1 = 4f;
				RM_SubmergeMath.Cut(RM_SubmergeMath.FromSouth, 0.25f, uv, ref x0, ref z0, ref x1, ref z1);
				Assert(Near(z0, 1f) && z1 == 4f && x0 == 0f && x1 == 2f, "can-fail: the bottom quarter of the quad is dropped");
				Assert(Near(uv[1], 0.25f) && Near(uv[7], 0.25f) && uv[3] == 1f && uv[5] == 1f, "can-fail: the bottom quarter of the texture too");
				// a flipped atlas tile: u runs 0.6..0.5, v 0.2..0.3
				float[] at = { 0.6f, 0.2f, 0.6f, 0.3f, 0.5f, 0.3f, 0.5f, 0.2f };
				float a0 = 0f, b0 = 0f, a1 = 1f, b1 = 1f;
				RM_SubmergeMath.Cut(RM_SubmergeMath.FromWest, 0.5f, at, ref a0, ref b0, ref a1, ref b1);
				Assert(Near(a0, 0.5f) && Near(at[0], 0.55f) && Near(at[2], 0.55f) && at[4] == 0.5f && at[1] == 0.2f,
					"can-fail: a west cut lerps u inside the atlas tile, flip kept");
				float[] e = { 0f, 0f, 0f, 1f, 1f, 1f, 1f, 0f };
				float c0 = 0f, d0 = 0f, c1 = 1f, d1 = 1f;
				RM_SubmergeMath.Cut(RM_SubmergeMath.FromEast, 0.4f, e, ref c0, ref d0, ref c1, ref d1);
				Assert(Near(c1, 0.6f) && Near(e[4], 0.6f) && Near(e[6], 0.6f) && e[0] == 0f, "can-fail: an east cut drops the east side");
				float[] n = { 0f, 0f, 0f, 1f, 1f, 1f, 1f, 0f };
				RM_SubmergeMath.Cut(RM_SubmergeMath.FromNorth, 0f, n, ref c0, ref d0, ref c1, ref d1);
				Assert(n[3] == 1f && Near(d1, 1f), "can-fail: share 0 cuts nothing");
			});
			Case("Submerge_wired_into_the_drawers_and_the_engine", () =>
			{
				string draw = RiverSwitchFlipChecks.Src("Superdeep/RM_SubmergeDraw.cs");
				string eng = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
				string spikes = RiverSwitchFlipChecks.Src("Superdeep/RM_Spikes.cs");
				Assert(draw.Contains("public partial class RM_Building_Ladder") && draw.Contains("public partial class RM_Building_PitRamp"),
					"can-fail: ladders and the ramp print through the cut");
				Assert(draw.Contains("TryGetTextureAtlasReplacementInfo") && draw.Contains("ShadowGraphic?.Print"),
					"can-fail: the cut print mirrors vanilla Graphic.Print (atlas, shadow)");
				Assert(!draw.Contains("new List<") || draw.IndexOf("new List<", StringComparison.Ordinal) > draw.IndexOf("ProofSubmerge", StringComparison.Ordinal),
					"can-fail: no allocation on the print path");
				int depthCheck = eng.IndexOf("a lake square is RM_LiquidStock.StagePond's", StringComparison.Ordinal);
				int hook = eng.IndexOf("RM_SubmergeDraw.FillPictured(", StringComparison.Ordinal);
				Assert(depthCheck > 0 && hook > depthCheck && hook - depthCheck < 400, "can-fail: the fill picture-writer re-meshes a noted fitting");
				Assert(eng.Contains("if (submergeDrawn.Count != 0)"), "can-fail: nothing noted, nothing done (dry costs nothing)");
				Assert(spikes.Contains("RM_SubmergeMath.StakeShare(level)") && spikes.Contains("RM_SubmergeDraw.NoteAt(eng, c)") && spikes.Contains("step << 22"),
					"can-fail: the spikes cut each stake and re-mesh when the level moves");
				Assert(spikes.Contains("RM_SpikeDrawMath.SubmergedAlpha(fill)"), "can-fail: setting off keeps the old fade");
			});
		}
	}
}
