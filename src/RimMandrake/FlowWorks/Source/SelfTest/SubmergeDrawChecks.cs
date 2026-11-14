// RIMMANDRAKE_SUBMERGE_PIT_FITTINGS_BY_LEVEL, owner look 2026-11-12 (SUBMERGE_PIT_FITTINGS_MATRIX_20261112): "It's as
// though each case is independently set in these variables, badly (major fix)". Everything in a dug pit under liquid is
// now decided by ONE function, RM_UnderLiquid: one level (the quarter-note of the true level), one cut (the share from
// the thing's foot), one see-through law (clarity ^ metres over). These checks pin that law and that every drawer uses
// it. Each case has a can-fail.
// NOT proven here: the pictures on screen. Live proof owed (northstar/pit_fittings_matrix.py).
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

		private const float Water = 0.45f;

		public static void Run(Action<string, Action> Case)
		{
			Case("Submerge_one_law_seen_through_liquid", () =>
			{
				Assert(RM_UnderLiquid.Seen(Water, 0f) == 1f && RM_UnderLiquid.Seen(Water, -1f) == 1f, "can-fail: above the line: whole");
				Assert(RM_UnderLiquid.Seen(0f, 0.01f) == 0f && RM_UnderLiquid.Seen(0f, 4f) == 0f, "can-fail: opaque (tar): hidden at any depth");
				float prev = 1f;
				for (int n = 1; n <= 8; n++)
				{
					float s = RM_UnderLiquid.Seen(Water, n * RM_UnderLiquid.Notch);
					Assert(s > 0f && s < prev, "can-fail: clear water: deeper hides more, never all (n=" + n + ", " + s + ")");
					prev = s;
				}
				// D8 brim-full: the floor of a 4 m pit is still seen (the pit's own inside shadow shows through, owner 2026-11-12)
				Assert(RM_UnderLiquid.BandAlphaStep(Water, 4f) >= 1, "can-fail: a brim-full 4 m pit still shows its floor");
				Assert(RM_UnderLiquid.BandAlphaStep(0f, 0.1f) == 0, "can-fail: opaque bands are not drawn");
				Assert(RM_UnderLiquid.BandsFor(0f, 0f, 2f) == 0 && RM_UnderLiquid.BandsFor(Water, 0f, 2f) == RM_UnderLiquid.Bands,
					"can-fail: opaque draws no band, a clear deep part all of them");
			});
			Case("Submerge_one_cut_from_the_foot", () =>
			{
				Assert(RM_UnderLiquid.Share(0f, 0f, RM_UnderLiquid.StakeMetres) == 0f, "can-fail: dry: nothing under");
				Assert(Near(RM_UnderLiquid.Share(0.5f, 0f, RM_UnderLiquid.StakeMetres), 0.5f), "can-fail: half a stake under half a metre");
				Assert(RM_UnderLiquid.Share(2f, 0f, RM_UnderLiquid.StakeMetres) == 1f, "can-fail: never more than all");
				// items, packed furniture and the swale are covered (owner: "Items ... never become covered (fix)")
				Assert(Near(RM_UnderLiquid.Share(0.15f, 0f, RM_UnderLiquid.ItemMetres), 0.5f), "can-fail: a stack half under 15 cm");
				Assert(RM_UnderLiquid.Share(0.5f, 0f, RM_UnderLiquid.MinifiedMetres) > 0.6f, "can-fail: packed furniture covered by 0.5 m");
				Assert(RM_UnderLiquid.Share(0.1f, 0f, RM_UnderLiquid.SwaleMetres) == 1f, "can-fail: the swale is a floor liner: under at the first drop");
				// a gate stands on the floor and its head clears the bank (owner: pass)
				Assert(RM_UnderLiquid.Share(4f, 0f, RM_UnderLiquid.GateMetres(8)) < 1f, "can-fail: a brim-full gate's head still shows");
				Assert(RM_UnderLiquid.Step(0f) == 0 && RM_UnderLiquid.Step(1e-4f) == 1 && RM_UnderLiquid.Step(0.9999f) == RM_UnderLiquid.Steps - 1
					&& RM_UnderLiquid.Step(1f) == RM_UnderLiquid.Steps, "can-fail: steps: 0 only dry, full only all");
			});
			Case("Submerge_one_level_true_not_whole_notches", () =>
			{
				Assert(RM_UnderLiquid.LevelNote(0) == 0 && RM_UnderLiquid.LevelNote(0.01) == 1, "can-fail: 0 only when dry");
				int n15 = RM_UnderLiquid.LevelNote(1.5);
				Assert(Near(RM_UnderLiquid.NoteLevel(n15), 1.5f) && Near(RM_UnderLiquid.NoteMetres(n15), 0.75f),
					"can-fail: a part notch is kept (no fill steps)");
				// RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES (owner card 2026-11-13 "Waterline -> follow it smoothly"):
				// 0.70 m of water is drawn within 2.5 cm of 0.70 m (quarter-notch notes drew it at 0.75 m)
				Assert(System.Math.Abs(RM_UnderLiquid.NoteMetres(RM_UnderLiquid.LevelNote(1.4)) - 0.70f) <= 0.0125f,
					"can-fail: the drawn waterline follows the true level within 2.5 cm");
				Assert(System.Math.Abs(RM_UnderLiquid.NoteMetres(RM_UnderLiquid.LevelNote(0.9988 / 0.5)) - 0.9988f) <= 0.0125f,
					"can-fail: 0.9988 m (the 'fill 1' square of 2026-11-12) is drawn at ~1 m, not 0.5 m");
				Assert(Near(RM_UnderLiquid.NoteLevel(RM_UnderLiquid.LevelNote(40)), 40f) && RM_UnderLiquid.LevelNote(1000) == RM_UnderLiquid.LevelNote(40),
					"can-fail: the deepest dig (20 m) is drawn exactly, deeper is capped there");
				// the hung ladder's waterline is the wall's own dry foot at that level, and a part notch moves it
				float w1 = RM_UnderLiquid.Waterline(0, 4, 1f), w15 = RM_UnderLiquid.Waterline(0, 4, 1.5f);
				Assert(Near(w1, 1f - RM_WallFaceMath.NorthFaceHeight(3)), "can-fail: north line = the face left dry (whole notch)");
				Assert(w15 > w1 && w15 < RM_UnderLiquid.Waterline(0, 4, 2f), "can-fail: a part notch moves the line");
				Assert(Near(RM_UnderLiquid.Waterline(1, 4, 1f), 1f - RM_WallFaceMath.SideFaceWidth(3))
					&& Near(RM_UnderLiquid.Waterline(3, 4, 1f), RM_WallFaceMath.SideFaceWidth(3)), "can-fail: east/west lines mirror the side faces");
				Assert(RM_UnderLiquid.Waterline(2, 4, 3f) == RM_UnderLiquid.NoCut && RM_UnderLiquid.Waterline(0, 4, 0f) == RM_UnderLiquid.NoCut,
					"can-fail: hung south or dry: never cut");
				Assert(Near(RM_UnderLiquid.NorthFace(2.5f), (RM_WallFaceMath.NorthByDrop[2] + RM_WallFaceMath.NorthByDrop[3]) / 2f)
					&& RM_UnderLiquid.NorthFace(99f) == RM_WallFaceMath.NorthByDrop[RM_WallFaceMath.NorthByDrop.Length - 1],
					"can-fail: faces read the tables between notches, last entry past the end");
				Assert(RM_UnderLiquid.Exposed(8, 0, 9f) == 0f && Near(RM_UnderLiquid.Exposed(8, 0, 2.25f), 5.75f), "can-fail: exposed drop at the true level");
			});
			Case("Submerge_cut_keeps_the_right_part_of_the_texture", () =>
			{
				// PrintPlane corners (-x-z, -x+z, +x+z, +x-z), default uvs (0,0),(0,1),(1,1),(1,0)
				float[] uv = { 0f, 0f, 0f, 1f, 1f, 1f, 1f, 0f };
				float x0 = 0f, z0 = 0f, x1 = 2f, z1 = 4f;
				RM_UnderLiquid.Slice(RM_UnderLiquid.FromSouth, 0.25f, 1f, uv, ref x0, ref z0, ref x1, ref z1);
				Assert(Near(z0, 1f) && Near(z1, 4f) && x0 == 0f && x1 == 2f, "can-fail: the dry slice of a south cut drops the bottom quarter");
				Assert(Near(uv[1], 0.25f) && Near(uv[7], 0.25f) && Near(uv[3], 1f) && Near(uv[5], 1f), "can-fail: and the bottom quarter of the texture");
				float[] at = { 0.6f, 0.2f, 0.6f, 0.3f, 0.5f, 0.3f, 0.5f, 0.2f };   // a flipped atlas tile
				float a0 = 0f, b0 = 0f, a1 = 1f, b1 = 1f;
				RM_UnderLiquid.Slice(RM_UnderLiquid.FromWest, 0.5f, 1f, at, ref a0, ref b0, ref a1, ref b1);
				Assert(Near(a0, 0.5f) && Near(at[0], 0.55f) && Near(at[2], 0.55f) && Near(at[4], 0.5f) && at[1] == 0.2f,
					"can-fail: a west cut lerps u inside the atlas tile, flip kept");
				float[] e = { 0f, 0f, 0f, 1f, 1f, 1f, 1f, 0f };
				float c0 = 0f, d0 = 0f, c1 = 1f, d1 = 1f;
				RM_UnderLiquid.Slice(RM_UnderLiquid.FromEast, 0f, 0.4f, e, ref c0, ref d0, ref c1, ref d1);
				Assert(Near(c0, 0.6f) && Near(c1, 1f) && Near(e[0], 0.6f), "can-fail: the drowned slice of an east cut is the east side");
			});
			Case("Submerge_every_drawer_uses_the_one_function", () =>
			{
				string draw = RiverSwitchFlipChecks.Src("Superdeep/RM_SubmergeDraw.cs");
				string eng = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
				string spikes = RiverSwitchFlipChecks.Src("Superdeep/RM_Spikes.cs");
				string gates = RiverSwitchFlipChecks.Src("Superdeep/RM_FlowDoors.cs");
				string walls = RiverSwitchFlipChecks.Src("Superdeep/RM_ExcavationWalls.cs");
				string surface = RiverSwitchFlipChecks.Src("RM_LiquidSurface.cs");
				Assert(draw.Contains("TakePrintFrom") && draw.Contains("PrintPlane") && draw.Contains("RM_UnderLiquid.Share(levelM, 0f, ctxHeight)"),
					"can-fail: map-mesh things (ladders, ramp, items, packed furniture, swale) are split by the one cut");
				Assert(draw.Contains("RM_UnderLiquid.ItemMetres") && draw.Contains("RM_UnderLiquid.MinifiedMetres") && draw.Contains("RM_UnderLiquid.SwaleMetres"),
					"can-fail: items, packed furniture and the swale are covered");
				Assert(draw.Contains("RM_UnderLiquid.Waterline(rot, drop, levelM / RM_UnderLiquid.Notch)"), "can-fail: a hung ladder meets the liquid where its wall does");
				Assert(gates.Contains("RM_SubmergeDraw.DrawUnder(") && gates.Contains("RM_UnderLiquid.GateMetres"), "can-fail: gates draw through the one law");
				Assert(gates.Contains("HollowDepthAt(Position)") && gates.Contains("if (pit <= 0)"), "can-fail: a gate in a pit casts no shadow onto the bank");
				Assert(spikes.Contains("RM_UnderLiquid.Share(") && spikes.Contains("RM_UnderLiquid.BandAlphaStep(") && !spikes.Contains("SubmergedAlpha"),
					"can-fail: the stakes are cut and seen through by the one law, the old fade is gone");
				Assert(walls.Contains("RM_UnderLiquid.Seen(") && walls.Contains("RM_WaterLookDraw.LookFlag") && !walls.Contains("FillAt("),
					"can-fail: walls: the one law, re-meshed on a level move, no whole-notch fill");
				Assert(!walls.Contains("LookFor(") , "can-fail: see-through does not hang on a look the vanilla rungs lack");
				Assert(surface.Contains("RM_UnderLiquid.NorthFace(RM_UnderLiquid.Exposed("), "can-fail: the surface overlay stops at the same face line");
				int depthCheck = eng.IndexOf("a lake square is RM_LiquidStock.StagePond's", StringComparison.Ordinal);
				int hook = eng.IndexOf("RM_SubmergeDraw.FillPictured(", StringComparison.Ordinal);
				Assert(depthCheck > 0 && hook > depthCheck && hook - depthCheck < 400, "can-fail: the fill picture-writer re-meshes a noted cell");
				Assert(eng.Contains("if (submergeDrawn.Count != 0)"), "can-fail: nothing noted, nothing done (dry costs nothing)");
			});
			Case("Submerge_drowned_part_reads_as_under_the_liquid", () =>
			{
				// RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE (owner 2026-11-13 ~10 PM: "the vent does not appear to be under water. The
				// blue seems to fade away, and the vent looks on top of the water"; ~10:10 PM: "The ancient shopping Cart isn't
				// shown as under the water"). A drowned band is its own colour whole, under a cover in the liquid's colour at
				// CoverAlpha(q): own weight q/Steps = Seen, liquid weight 1 - Seen, so it reads lerp(liquid, own, Seen) as the floor
				// beside it does. Before: own at alpha q/Steps over the floor, liquid weight 0.
				foreach (float m in new[] { 1f, 2f, 4f })
				{
					int q = RM_UnderLiquid.BandAlphaStep(Water, m);
					float own = 1f - RM_UnderLiquid.CoverAlpha(q), seen = RM_UnderLiquid.Seen(Water, m);
					Assert(Math.Abs(own - seen) <= 0.5f / RM_UnderLiquid.Steps + 1e-4f, "can-fail: own weight is Seen at " + m + " m (" + own + " vs " + seen + ")");
					Assert(RM_UnderLiquid.CoverAlpha(q) > 0.25f, "can-fail: the liquid's colour is on a part " + m + " m under (cover " + RM_UnderLiquid.CoverAlpha(q) + ")");
				}
				Assert(RM_UnderLiquid.CoverAlpha(RM_UnderLiquid.Steps) == 0f && RM_UnderLiquid.CoverAlpha(0) == 1f, "can-fail: dry: no cover; hidden: all liquid");
				Assert(RM_UnderLiquid.CoverAlpha(RM_UnderLiquid.BandAlphaStep(Water, 4f)) < RM_UnderLiquid.CoverAlpha(0), "the 4 m plateau still lets the floor through (KEEP murk)");
				string draw = RiverSwitchFlipChecks.Src("Superdeep/RM_SubmergeDraw.cs");
				Assert(draw.Contains("ShaderDatabase.Silhouette") && draw.Contains("RM_UnderLiquid.CoverAlpha(q)") && !draw.Contains("Material Faded("),
					"can-fail: the cover is a Silhouette in the liquid colour; the old own-alpha fade is gone");
			});
			Case("Submerge_flat_vent_is_tinted_like_the_floor", () =>
			{
				// A geyser's vent and filth lie on the pit floor: drawn under the sheet (UnderSheetQueue), so the sheet tints them
				// exactly as the floor at the same depth (brief: 1 m tinted, 2 m barely visible). The law's plateau is 0.10 from
				// 4 m (images/3.png, KEEP): "not visible at 4 m" would need a new law, flagged, not done.
				float s1 = RM_UnderLiquid.Seen(Water, 1f), s2 = RM_UnderLiquid.Seen(Water, 2f), s4 = RM_UnderLiquid.Seen(Water, 4f);
				Assert(s1 > s2 && s2 > s4, "can-fail: deeper hides more (" + s1 + ", " + s2 + ", " + s4 + ")");
				Assert(s1 < 0.9f && s1 > 0.5f, "can-fail: 1 m: tinted, still seen (" + s1 + ")");
				Assert(s2 < 0.5f && s4 <= 0.11f, "can-fail: 2 m barely, 4 m about gone (" + s2 + ", " + s4 + ")");
				string draw = RiverSwitchFlipChecks.Src("Superdeep/RM_SubmergeDraw.cs");
				Assert(draw.Contains("t is Filth || (t is Building_SteamGeyser && RM_GeyserPit.On)") && draw.Contains("RM_FaceMaterial.UnderSheetQueue"),
					"can-fail: the vent and filth print under the sheet");
			});
			Case("Submerge_overlays_follow_their_thing", () =>
			{
				// RIMMANDRAKE_SINK_COOLER_ARROW_UNDER_TAR (owner ~10:15 PM: "the Cooler still keeps its little red arrow icon above
				// the surface"; ~10:25 PM: "if we could put the yellow power disconnect icons under the water too when the item is
				// under water that would be great").
				Assert(RM_UnderLiquid.OverlayAlpha(Water, 0f, RM_UnderLiquid.WallSlotMetres) == 1f, "dry: whole");
				float flush = RM_UnderLiquid.OverlayAlpha(Water, 1f, 1f);
				Assert(flush < 1f && flush > 0.5f, "can-fail: a thing flush with the line shows its icon dimmed, not whole (" + flush + ")");
				Assert(RM_UnderLiquid.OverlayAlpha(Water, 4f, 1f) < RM_UnderLiquid.OverlayAlpha(Water, 1f, 1f), "can-fail: deeper icons dimmer");
				Assert(RM_UnderLiquid.OverlayAlpha(0f, 1.5f, RM_UnderLiquid.WallSlotMetres) == 0f, "can-fail: a cooler under 1.5 m of tar: icons hidden");
				Assert(RM_UnderLiquid.Share(1.5f, 0f, RM_UnderLiquid.WallSlotMetres) == 1f, "can-fail: 1.5 m covers a wall-slot cooler (arrow and all)");
				string draw = RiverSwitchFlipChecks.Src("Superdeep/RM_SubmergeDraw.cs");
				// The paths an overlay can take (OverlayDrawer, RimWorld 1.6): DrawOverlay (gate), every Render*(Thing ...) (depth
				// set: NeedsPower, PowerOff, BrokenDown, Rechargine, OutOfFuel, Pulsing, Forbidden*, BurningWick, QuestionMark),
				// and DrawBatch.DrawMesh where they all land (material faded after vanilla's own pulse fade).
				Assert(draw.Contains("typeof(OverlayDrawer), \"DrawOverlay\"") || draw.Contains("nameof(OverlayDrawer.DrawOverlay)"), "can-fail: DrawOverlay gated");
				Assert(draw.Contains("m.Name.StartsWith(\"Render\")") && draw.Contains("typeof(DrawBatch)"), "can-fail: every Render* and DrawBatch.DrawMesh are patched");
				Assert(draw.Contains("Building_Cooler") && draw.Contains("RM_UnderLiquid.WallSlotMetres"), "can-fail: the cooler stands in a wall slot");
			});
			Case("Submerge_rim_clip_keeps_sprites_in_the_pit", () =>
			{
				// owner ~10:10 PM: "the chunks don't honor the pit, they overlap its edges unphysically".
				float[] o = new float[RM_UnderLiquid.ClipMaxVerts * RM_UnderLiquid.ClipStride];
				Assert(RM_UnderLiquid.ClipQuad(5f, 5f, 1f, 1f, 0f, 0f, 0f, 10f, 10f, o) == -1, "can-fail: inside: untouched");
				Assert(RM_UnderLiquid.ClipQuad(20f, 5f, 1f, 1f, 0f, 0f, 0f, 10f, 10f, o) == 0, "can-fail: outside: nothing");
				int n = RM_UnderLiquid.ClipQuad(0.1f, 5f, 1.6f, 1.6f, 30f, 0f, 0f, 10f, 10f, o);
				Assert(n >= 3, "can-fail: over the rim: a kept polygon (" + n + ")");
				for (int i = 0; i < n; i++)
				{
					float x = o[i * RM_UnderLiquid.ClipStride], s = o[i * RM_UnderLiquid.ClipStride + 2], t = o[i * RM_UnderLiquid.ClipStride + 3];
					Assert(x >= -1e-4f && s >= -1e-4f && s <= 1f + 1e-4f && t >= -1e-4f && t <= 1f + 1e-4f, "can-fail: nothing past the rim, uvs inside the quad");
				}
				Assert(RM_UnderLiquid.ClipQuad(0.1f, 5f, 1f, 1f, 0f, float.NegativeInfinity, 0f, 10f, 10f, o) == -1, "an open side does not clip");
			});
			Case("Submerge_murk_keeps_rising_to_the_plateau", () =>
			{
				// owner ~10:10 PM: "the murk looks really good. If it gets even deeper it keeps getting more murky right?" (KEEP)
				float prev = 1.01f;
				foreach (float m in new[] { 0.5f, 1f, 2f, 3f, 4f, 6f, 10f, 20f })
				{
					float s = RM_UnderLiquid.Seen(Water, m);
					Assert(s <= prev && s > 0f, "can-fail: never less murky deeper, never wholly hidden in clear water (" + m + " m: " + s + ")");
					prev = s;
				}
				Assert(Near(RM_UnderLiquid.Seen(Water, 20f), RM_UnderLiquid.Seen(Water, 4f), 1e-3f), "can-fail: flat from 4 m (the plateau)");
			});
			Case("Submerge_defs_tar_dark_gates_shadowless", () =>
			{
				string reg = RiverSwitchFlipChecks.Src("../Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml");
				string tar = RiverSwitchFlipChecks.Src("../Defs/LiquidTypes/TerrainDefs/RM_Tar.xml");
				string doors = RiverSwitchFlipChecks.Src("../Defs/Canals/ThingDefs/FlowWorks_Doors.xml");
				Assert(reg.Contains("<tint>(0.07,0.065,0.06)</tint>") && !reg.Contains("<tint>(0.24,0.24,0.24)</tint>"), "can-fail: tar's look is dark, not grey");
				Assert(!tar.Contains("<color>(86,82,88)</color>") && tar.Contains("<color>(18,17,16)</color>"), "can-fail: tar terrain is dark");
				int sluice = doors.IndexOf("<defName>RM_Sluice</defName>", StringComparison.Ordinal);
				int grate = doors.IndexOf("<defName>RM_SecurityGrateDoor</defName>", StringComparison.Ordinal);
				int s0 = doors.IndexOf("<staticSunShadowHeight>0</staticSunShadowHeight>", sluice, StringComparison.Ordinal);
				int g0 = doors.IndexOf("<staticSunShadowHeight>0</staticSunShadowHeight>", grate, StringComparison.Ordinal);
				Assert(sluice > 0 && grate > sluice && s0 > sluice && s0 < grate && g0 > grate, "can-fail: both gates override DoorBase's 1.0 sun shadow");
			});
		}
	}
}
