// PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL (bridge run 1, save e C3 boar pit 38-39,22-23, D8): the wild boar, logically on 39,23,
// was DRAWN at about (38.5, 21.0), on the room's south wall, with lip-cover soil squares either side of it.
// Mechanism: the sink clamp (PIT_LIP_OCCLUDES_OUTSIDE_1) measured the room above the near lip from the LOGICAL cell's
// centre (Position), but the sink is subtracted from the TWEENED draw position. Vanilla's PawnTweener lags the logical
// position (spring 0.09/frame, ~0.85 cell behind a walking boar at any speed) and freezes entirely while paused, so after
// the boar stepped 38,22 -> 39,23 its tween still sat on 38,22: room 1.5 (from 23.5) taken off 22.5 put it 1.0 below the lip.
// The fix holds the drawn centre itself above the near lip in the DRAWN column (RM_PitDrawMath.HoldToDrawnLip).
// Each case has a can-fail. NOT proven here: the live frame (re-capture C3 on save e).
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitDrawHoldChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            return j < 0 ? src.Substring(i) : src.Substring(i, j - i);
        }

        // save e's boar pit: 38-39 x 22-23 dug to 8, ground (0) all round; -1 = off the map
        private static int BoarPit(int x, int z)
        {
            if (x < 0 || z < 0 || x >= 250 || z >= 250) return -1;
            return x >= 38 && x <= 39 && z >= 22 && z <= 23 ? 8 : 0;
        }

        // PIT_SINK_FIX_SOIL_STRIP_OVER_WALL: save e map 0's real edifices round the pit (read from RM_fw_walkthrough_20261023e.rws):
        // the room's south wall on row z 20 (x 35..42) and its east wall on column x 42 (z 20..25)
        private static bool SaveEWall(int x, int z) => (z == 20 && x >= 35 && x <= 42) || (x == 42 && z >= 20 && z <= 25);

        // the cover's own piece loop (RM_PitLipOcclusion): cells floor(z0) .. ceil(z1)-1 of a column, each painted in its terrain
        private static bool PaintsAWall(int x, float z0, float z1, Func<int, int, bool> wall)
        {
            if (z1 <= z0 + 0.001f) return false;
            for (int cz = (int)Math.Floor(z0); cz < (int)Math.Ceiling(z1); cz++)
            {
                if (wall(x, cz) && Math.Min(z1, cz + 1f) > Math.Max(z0, cz)) return true;
            }
            return false;
        }

        // PIT_COVER_FIX_DROPS_THE_SUN_SHADOW: save e's walls as SectionLayer_SunShadows sees them (vanilla Wall staticSunShadowHeight 1.0)
        private static float SaveEHeight(int x, int z) => SaveEWall(x, z) ? 1f : 0f;

        // the fraction of a grid of points over [l,r]x[a,b] that lie in a sun shadow
        private static float ShadedShare(float l, float r, float a, float b, float vx, float vz, Func<int, int, float> h)
        {
            int n = 0, hit = 0;
            for (int i = 0; i <= 10; i++)
                for (int k = 0; k <= 10; k++, n++)
                    if (RM_PitDrawMath.SunShadowed(l + (r - l) * i / 10f, a + (b - a) * k / 10f, vx, vz, 1f, h)) hit++;
            return hit / (float)n;
        }

        // PIT_LIP_FIX_MUFFALO_OVERHANGS_RIM: bridge run 1 br1f s8's pit, read from s8_pitlip.json's rect rows: 132-135 x 114-117
        // dug to 4, ground (0) all round. The muffalo stood on 132,114 (SW corner), the colonist on 135,114 (SE corner).
        private static int S8Pit(int x, int z)
        {
            if (x < 0 || z < 0 || x >= 250 || z >= 250) return -1;
            return x >= 132 && x <= 135 && z >= 114 && z <= 117 ? 4 : 0;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PitSide_s8_muffalo_west_overhang_is_hidden", () =>
            {
                // at rest on 132,114 the sink is clamped to the lip: drawn centre (132.5, 114.0). Adult Muffalo drawSize 3: box
                // x 131..134, z 112.5..115.5. Measured in s8_pitlip_close.png: the visible body reaches x 131.73 and z 114.69.
                float bottom = 112.5f, top = 115.5f;
                Assert(RM_PitDrawMath.BesideOpening(131, 114, 132, 4, S8Pit), "can-fail: 131,114 is ground beside the pit's row 114");
                Assert(RM_PitDrawMath.BesideOpening(131, 115, 132, 4, S8Pit), "131,115 is ground beside the pit's row 115");
                Assert(!RM_PitDrawMath.BesideOpening(133, 114, 132, 4, S8Pit), "a pit column is never a side bank");
                Assert(!RM_PitDrawMath.BesideOpening(131, 113, 132, 4, S8Pit), "row 113 is south of the pit: the near lip's job, not the side's");
                float hid = RM_PitDrawMath.SideHiddenTop(bottom, top, 4, 0.3f, RM_PitDrawMath.BodyHeightCells(2.4f));
                Assert(hid >= 114.69f, "D4: the side bank hides the flank up to the visible top 114.69, got " + hid);
                Assert(hid <= top + 1e-4f, "never above the sprite's top");
                // the old cover reached column 131 only below its south lip (114): the flank above 114 showed (the bug)
                float lip = RM_PitDrawMath.LipZBelow(131, 114, 4, S8Pit, 16);
                Assert(lip == 114f, "column 131's south lip is 114, got " + lip);
                Assert(hid > lip + 0.5f, "can-fail: the side band adds cover above the south lip");
            });

            Case("PitSide_far_rim_and_shallow_depth", () =>
            {
                // muffalo on the north row 132,117: west ground on row 118 lies beyond the far (north) rim, so it stays drawn
                Assert(!RM_PitDrawMath.BesideOpening(131, 118, 132, 4, S8Pit), "can-fail: beyond the far rim the sprite is not hidden");
                Assert(RM_PitDrawMath.BesideOpening(131, 117, 132, 4, S8Pit), "the north row itself has a side bank");
                Assert(!RM_PitDrawMath.BesideOpening(-1, 117, 0, 4, S8Pit), "off the map is no bank");
                // D1 (0.5 m): only the lower part of a muffalo is below ground, so only that much goes behind the side bank
                float h = RM_PitDrawMath.BodyHeightCells(2.4f);
                float d1 = RM_PitDrawMath.SideHiddenTop(112.5f, 115.5f, 1, 0.3f, h);
                Assert(d1 > 112.5f && d1 < 113.5f, "D1 hides under a third of the muffalo box, got " + d1);
                Assert(RM_PitDrawMath.SideHiddenTop(112.5f, 115.5f, 0, 0.3f, h) == 112.5f, "D0: nothing hidden");
                Assert(Math.Abs(RM_PitDrawMath.SideHiddenTop(13f, 14f, 8, 0.3f, RM_PitDrawMath.BodyHeightCells(1f)) - 14f) < 1e-4f,
                    "a colonist at D8 is wholly below the bank");
            });

            Case("PitLip_s8_colonist_feet_under_the_cover", () =>
            {
                // the colonist on 135,114, drawn centre z 114.0; s8_pitlip_close.png shows the feet 0.75 cells below it (vanilla's
                // humanlike body mesh is 1.5 x 1.5). The cover's bottom must reach them.
                float est = RM_PitDrawMath.BodyEstimateHalf(1f);
                Assert(114f - est > 113.25f + 1e-4f, "can-fail: the body-size estimate (" + est + ") stops above the feet (the bug)");
                float half = RM_PitDrawMath.HumanlikeHalfHeight(1f);
                Assert(114f - half <= 113.25f + 1e-4f, "the humanlike cover reaches the feet at 113.25, half " + half);
                Assert(RM_PitDrawMath.HumanlikeHalfHeight(4f) >= RM_PitDrawMath.BodyEstimateHalf(4f), "never below the estimate");
            });

            Case("PitSide_lip_occlusion_wires_the_side_bank", () =>
            {
                string src = Src("Superdeep", "RM_PitLipOcclusion.cs");
                string update = Between(src, "public override void MapComponentUpdate()", "private void DrawBand(");
                Assert(update.Contains("RM_PitDrawMath.SideHiddenTop("), "the side band's height comes from the depth");
                Assert(src.Contains("RM_PitDrawMath.BesideOpening("), "side pieces only on ground beside the opening");
                string half = Between(src, "private static Vector2 HalfExtent(Pawn p)", "private struct PawnRect");
                Assert(half.Contains("RM_PitDrawMath.HumanlikeHalfHeight("), "humanlikes cover their whole body mesh");
            });


            Case("PitSun_save_e_east_wall_shades_the_band", () =>
            {
                // C3's cover band: x 37.2..39.8, z 21..22, between the pit's south lip (22) and the south wall (row 20)
                // afternoon cast vector (GenCelestial: x in -15..15, z = -1.5 - 2.5 x^2/100): the east wall's (x 42) shadow runs west
                float vx = -6f, vz = -1.5f - 2.5f * 36f / 100f;
                Assert(RM_PitDrawMath.SunShadowed(38.5f, 21.5f, vx, vz, 1f, SaveEHeight), "can-fail: band centre lies in the east wall's shadow");
                Assert(ShadedShare(37.2f, 39.8f, 21f, 22f, vx, vz, SaveEHeight) > 0.5f, "most of the band is shaded in the afternoon");
                // morning: the shadow runs east, away from the band; noon: straight south, so the south wall (row 20) never reaches z >= 21
                Assert(ShadedShare(37.2f, 39.8f, 21f, 22f, 6f, vz, SaveEHeight) == 0f, "morning: no shadow on the band");
                Assert(ShadedShare(37.2f, 39.8f, 21f, 22f, 0f, -1.5f, SaveEHeight) == 0f, "noon: the south wall's shadow falls south of it");
                Assert(RM_PitDrawMath.SunShadowed(38.5f, 19.5f, 0f, -1.5f, 1f, SaveEHeight), "noon: the ground south of the south wall is shaded");
            });

            Case("PitSun_sweep_matches_the_vanilla_mesh", () =>
            {
                // one caster at (0,0): its shadow is the unit square swept by height x cast vector (skirt verts displaced by alpha = height)
                Func<int, int, float> one = (x, z) => x == 0 && z == 0 ? 1f : 0f;
                Func<int, int, float> half = (x, z) => x == 0 && z == 0 ? 0.5f : 0f;
                Assert(RM_PitDrawMath.SunShadowed(0.5f, -1.4f, 0f, -1.5f, 1f, one), "inside the swept length");
                Assert(!RM_PitDrawMath.SunShadowed(0.5f, -1.6f, 0f, -1.5f, 1f, one), "beyond the tip");
                Assert(RM_PitDrawMath.SunShadowed(0.5f, -0.7f, 0f, -1.5f, 1f, half), "height 0.5 casts half as far");
                Assert(!RM_PitDrawMath.SunShadowed(0.5f, -0.8f, 0f, -1.5f, 1f, half), "height 0.5: past its tip");
                Assert(!RM_PitDrawMath.SunShadowed(0.5f, 1.2f, 0f, -1.5f, 1f, one), "never north of the caster");
                Assert(RM_PitDrawMath.SunShadowed(3.5f, -1.2f, 4f, -1.9f, 1f, one), "slanted: the parallelogram's far corner");
                Assert(!RM_PitDrawMath.SunShadowed(1.5f, -1.8f, 4f, -1.9f, 1f, one), "slanted: off the parallelogram");
                Assert(!RM_PitDrawMath.SunShadowed(0.5f, -1.4f, 0f, -1.5f, 1f, (x, z) => 0f), "no caster, no shadow");
                // the per-piece caster list gives the same answer as the per-point search, over the C3 band at three times of day
                var list = new System.Collections.Generic.List<(int x, int z, float h)>();
                foreach (float vx in new[] { -15f, -6f, 0f, 6f, 15f })
                {
                    float vz = -1.5f - 2.5f * vx * vx / 100f;
                    RM_PitDrawMath.SunCasters(37.2f, 39.8f, 21f, 22f, vx, vz, 1f, SaveEHeight, list);
                    for (int i = 0; i <= 26; i++)
                        for (int k = 0; k <= 10; k++)
                        {
                            float x = 37.2f + 0.1f * i, z = 21f + 0.1f * k;
                            Assert(RM_PitDrawMath.SunShadowedBy(x, z, vx, vz, list) == RM_PitDrawMath.SunShadowed(x, z, vx, vz, 1f, SaveEHeight),
                                "caster list agrees at " + x + "," + z + " v " + vx);
                        }
                }
            });

            Case("PitSun_lip_occlusion_carries_the_sun_shadow", () =>
            {
                string src = Src("Superdeep", "RM_PitLipOcclusion.cs");
                Assert(src.Contains("Shader.GetGlobalVector(ShaderPropertyIDs.MapSunLightDirection)"), "the cast vector vanilla's shader displaces by (_CastVect)");
                Assert(src.Contains("MatBases.SunShadow.color"), "the shadow tint SkyManager sets each frame");
                Assert(src.Contains("RM_PitDrawMath.SunShadowedBy(x, z, sunVx, sunVz, sunCasters)"), "each shade vertex tests the vanilla sweep");
                Assert(src.Contains("RM_PitDrawMath.SunCasters(l, r, a, b, sunVx, sunVz, SunHMax, SunHeightAt, sunCasters)"), "casters gathered per piece");
                Assert(src.Contains("ed.def.staticSunShadowHeight") && src.Contains("map.edificeGrid["), "casters are edifices with a static sun shadow height");
                Assert(src.Contains("!MatBases.SunShadow.shader.isSupported"), "only where vanilla draws the layer at all");
                string update = Between(src, "public override void MapComponentUpdate()", "// cover cell by cell");
                Assert(update.Contains("ReadSunShadow(edgeShadows);"), "read once per frame, gated like SectionLayer_SunShadows.Visible");
                Assert(src.Contains("if (casters != 0 || sun)"), "a piece with only a sun shadow on it is shaded too");
            });

            Case("PitSoil_cover_stops_at_save_e_south_wall", () =>
            {
                // the C3 boar held on the lip (drawn centre 22), adult WildBoar drawSize 2.65: sprite band 20.675 .. 22
                float lip = RM_PitDrawMath.LipZBelow(38, 22, 8, BoarPit, 16);
                Assert(lip == 22f, "lip 22, got " + lip);
                float bottom = 22f - 0.5f * 2.65f;
                Assert(RM_WallFaceMath.OccludedBand(lip, bottom, 22f + 1.325f, out float z0, out float z1), "a band hangs below the lip");
                Assert(PaintsAWall(38, z0, z1, SaveEWall), "can-fail: the unclipped band paints soil on wall 38,20 (the bug)");
                for (int x = 37; x <= 39; x++)
                {
                    float stop = RM_PitDrawMath.CoverStopZ(x, lip, z0, SaveEWall);
                    Assert(Math.Abs(stop - 21f) < 1e-4f, "column " + x + ": the cover stops at the wall's north edge 21, got " + stop);
                    Assert(!PaintsAWall(x, Math.Max(z0, stop), z1, SaveEWall), "column " + x + ": no cover piece on the wall row");
                }
                Assert(RM_PitDrawMath.CoverStopZ(38, lip, z0, (x, z) => false) == z0, "no edifice in the band: the band is untouched");
            });

            Case("PitSoil_cover_edges", () =>
            {
                Assert(RM_PitDrawMath.CoverStopZ(38, 22f, 21.2f, SaveEWall) == 21.2f, "band ending above the wall row: unchanged");
                // a pit dug right against the wall: the lip cell IS the wall -> no cover at all
                Assert(RM_PitDrawMath.CoverStopZ(38, 21f, 19.5f, SaveEWall) == 21f, "lip cell is a wall: the cover stops at the lip (empty band)");
                // ground row, then wall two rows down: the ground row keeps its cover
                Assert(RM_PitDrawMath.CoverStopZ(38, 23f, 20.4f, SaveEWall) == 21f, "ground rows 21-22 covered, the wall row 20 not");
                Assert(RM_PitDrawMath.CoverStopZ(43, 22f, 20.4f, SaveEWall) == 20.4f, "can-fail: a column outside the room has no wall");
            });

            Case("PitSoil_lip_occlusion_wires_the_stop", () =>
            {
                string src = Src("Superdeep", "RM_PitLipOcclusion.cs");
                string update = Between(src, "public override void MapComponentUpdate()", "// cover cell by cell");
                Assert(update.Contains("z0 = Mathf.Max(z0, RM_PitDrawMath.CoverStopZ(cx, lipZ, z0, BlocksCover));"), "the band is clipped at the first edifice south of the lip");
                string blocks = Between(src, "private System.Func<int, int, bool> BlocksCover", "private int EdgeCasters(");
                Assert(blocks.Contains("GetEdifice(map)") && blocks.Contains("!(ed is Pits.Building_PitCover)"), "an edifice blocks, a pit lid does not");
            });

            Case("PitDrawHold_lip_found_in_the_drawn_column", () =>
            {
                Assert(RM_PitDrawMath.LipZBelow(39, 23, 8, BoarPit, 16) == 22f, "north row: the lip is the ground row's north edge, 22");
                Assert(RM_PitDrawMath.LipZBelow(38, 22, 8, BoarPit, 16) == 22f, "south row: the same lip, right under the cell");
                Assert(float.IsNaN(RM_PitDrawMath.LipZBelow(38, 23, 9, (x, z) => z < 0 ? -1 : 9, 16)), "can-fail: no shallower cell -> NaN");
                Assert(float.IsNaN(RM_PitDrawMath.LipZBelow(38, 2, 8, (x, z) => z < 0 ? -1 : 8, 16)), "can-fail: the map edge stops the search");
            });

            Case("PitDrawHold_boar_with_a_lagging_tween_stays_in_the_pit", () =>
            {
                // the per-cell clamp for Position 39,23 lets 1.5 through (centre 23.5, lip 22)
                float perCell = RM_PitDrawMath.ClampSinkToLip(RM_PitDrawMath.SinkFor(8, 0.3f), 23.5f, 22f);
                Assert(Math.Abs(perCell - 1.5f) < 1e-4f, "per-cell clamp on 39,23 is 1.5, got " + perCell);
                // the tween still on 38,22 (frozen while paused / lagging while walking)
                float held = RM_PitDrawMath.HoldToDrawnLip(perCell, 38.5f, 22.5f, 8, BoarPit);
                float drawnZ = 22.5f - held;
                Assert(drawnZ >= 22f - 1e-4f, "drawn centre held on/above the near lip (22), got " + drawnZ);
                Assert(Math.Abs(held - 0.5f) < 1e-4f, "held sink 0.5, got " + held);
                Assert(22.5f - perCell < 22f - 0.5f, "can-fail: the per-cell clamp alone draws the boar a cell below the lip (21.0)");
            });

            Case("PitDrawHold_tween_on_the_cell_changes_nothing", () =>
            {
                float s = RM_PitDrawMath.SinkFor(8, 0.3f);
                float atCell = RM_PitDrawMath.ClampSinkToLip(s, 23.5f, 22f);
                Assert(Math.Abs(RM_PitDrawMath.HoldToDrawnLip(atCell, 39.5f, 23.5f, 8, BoarPit) - atCell) < 1e-4f, "at rest the hold equals the per-cell clamp");
                Assert(Math.Abs(RM_PitDrawMath.HoldToDrawnLip(s, 38.5f, 30.5f, 8, (x, z) => z < 0 ? -1 : 8) - s) < 1e-4f, "a long trench with no lip within reach: full sink");
                Assert(RM_PitDrawMath.HoldToDrawnLip(s, 38.5f, 22.9f, 8, BoarPit) < s, "can-fail: drawn on the south row the hold does bite");
                Assert(RM_PitDrawMath.HoldToDrawnLip(s, 38.5f, 22.5f, 0, BoarPit) == s, "d <= 0: nothing to hold (no sink came from a hole)");
                Assert(RM_PitDrawMath.HoldToDrawnLip(0f, 38.5f, 22.5f, 8, BoarPit) == 0f, "no sink stays none");
            });

            Case("PitDrawHold_SinkOf_holds_the_drawn_position", () =>
            {
                string src = Src("Superdeep", "RM_PitDepthDraw.cs");
                string sinkOf = Between(src, "public static float SinkOf(", "private static float Clamped(");
                Assert(sinkOf.Contains("return Held(Clamped(ex, pawn.Map, from, dFrom, perLevel), drawPos, dFrom);"), "at rest SinkOf holds the drawn position");
                Assert(sinkOf.Contains("return Held(sa + (sb - sa) * t, drawPos,"), "moving, SinkOf holds the drawn position");
                string held = Between(src, "private static float Held(", "private static readonly Func<int, int, int> SeenDepth");
                Assert(held.Contains("HoldToDrawnLip(sink, drawPos.x, drawPos.z, d, SeenDepth)"), "the hold reads the TWEENED draw position, not Position");
                Assert(held.Contains("pitSinkClampEnabled"), "the hold sits under the clamp switch (X rows run with it off)");
                string clamped = Between(Src("Superdeep", "RM_PitDepthDraw.cs"), "private static float Clamped(", "private static RM_MapComponent_Excavation ExcavationOf(");
                Assert(clamped.Contains("LipZBelow("), "the per-cell clamp uses the same lip finder");
            });

            // DRAFTED_SWIMMER_FIX_PIT_BOTTOM_ROW / DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS / SWIM_DEPTH_FIX_TWO_METRES_WALKED (owner review
            // 2026-10-24 rows 4 and 7): vanilla's swim pose came only from a joy-swim job, so a drafted pawn (or any other job)
            // walked through water over its head; and the pit sink drew every pawn on the FLOOR, so a swimmer in a brim-full 5 m
            // pit "jumped" in and walked the bottom.
            Case("SwimPose_head_under_swims_whatever_the_job", () =>
            {
                const float H = 1.75f, F = 0.9f;
                Assert(RM_SwimMath.SwimPose(false, true, false, false, 2.0f, true, H, false, F), "2.0 m over a 1.75 m person: the swim pose (b)");
                Assert(RM_SwimMath.SwimPose(false, true, false, false, 5.0f, true, H, false, F), "5 m: swims (c), drafted or not (d)");
                Assert(!RM_SwimMath.SwimPose(false, true, false, false, 1.5f, true, H, false, F), "can-fail: 1.5 m: wades");
                Assert(!RM_SwimMath.SwimPose(false, true, false, true, 5.0f, true, H, false, F), "on a deck: never");
                Assert(!RM_SwimMath.SwimPose(false, true, true, false, 5.0f, true, H, false, F), "flying: never");
                Assert(!RM_SwimMath.SwimPose(false, true, false, false, 5.0f, false, H, false, F), "an unswimmable liquid: never");
                Assert(!RM_SwimMath.SwimPose(false, false, false, false, 5.0f, true, H, false, F), "swimming off: vanilla only");
                Assert(!RM_SwimMath.SwimPose(false, true, false, false, 5.0f, true, H, true, F), "lying: not the swim pose (the drowning rule's)");
                Assert(RM_SwimMath.SwimPose(true, false, false, false, 0f, false, H, false, F), "vanilla's joy swim is never taken away");
                string sw = Src("Swimming", "RM_Swim.cs");
                Assert(sw.Contains("[HarmonyPatch(typeof(Pawn), nameof(Pawn.Swimming), MethodType.Getter)]")
                    && sw.Contains("__result = SwimsAt(__instance, __instance.Position);"), "the Pawn.Swimming getter reads the rule (renderer, ripples)");
                Assert(sw.Contains("[HarmonyPatch(typeof(Pawn), nameof(Pawn.WaterCellCost), MethodType.Getter)]")
                    && sw.Contains("if (__result || inWaterCost ||"),
                    "can-fail: Pawn.WaterCellCost (path cost) still sees vanilla's pose only: our pose never makes deep water nearly free");
                Assert(sw.Contains("return RM_SwimMath.SwimPose(false, true, false, deck, RM_SwimWater.WaterMetresAt(map, ex, c),"), "SwimsAt runs the pure rule");
            });

            Case("PitSink_a_swimmer_floats_at_the_surface", () =>
            {
                Assert(RM_SwimMath.SurfaceDrawDepth(10, 10) == 0, "brim-full 5 m pit: drawn at ground level (sink 0)");
                Assert(RM_SwimMath.SurfaceDrawDepth(10, 4) == 6, "2 m of water in a 5 m pit: 3 m down, at the surface");
                Assert(RM_SwimMath.SurfaceDrawDepth(4, 9) == 0 && RM_SwimMath.SurfaceDrawDepth(0, 4) == 0, "never above the ground");
                Assert(RM_SwimMath.SurfaceDrawDepth(10, 0) == 10, "can-fail: no water: the floor");
                Assert(RM_PitDrawMath.SinkFor(RM_SwimMath.SurfaceDrawDepth(10, 10), 0.3f) == 0f && RM_PitDrawMath.SinkFor(10, 0.3f) > 2f,
                    "can-fail: pre-fix the 5 m swimmer sank the full cap (the 'jump')");
                string src = Src("Superdeep", "RM_PitDepthDraw.cs");
                string sinkOf = Between(src, "public static float SinkOf(", "public static int DrawHollow(");
                Assert(sinkOf.Contains("DrawDepth(pawn, from, DrawHollow(pawn, ex, from))") && sinkOf.Contains("DrawDepth(pawn, to, DrawHollow(pawn, ex, to))")
                    && !sinkOf.Contains("ex.HollowDepthAt("), "both ends of a step read the drawn (surface) depth");
                string dh = Between(src, "public static int DrawHollow(", "public static float RestingSinkAt(");
                Assert(dh.Contains("Swimming.RM_Patch_Pawn_SwimPose.SwimsAt(pawn, c)") && dh.Contains("RM_SwimMath.SurfaceDrawDepth(h,"),
                    "a floating pawn reads the surface; a wader the floor");
            });

            // PIT_CLICK_FIX_SHIFTED_ONE_DOWN (owner 2026-10-24: "even in a waterless pit clicking the colonist appears to only allow
            // them to move 'shifted one down' by what you would expect where you clicked").
            Case("PitClick_the_click_means_where_the_pawn_is_drawn", () =>
            {
                // a 1 m pit (2 notches, sink 0.6) rows z 10..14, ground elsewhere; no lip clamp bites mid-pit
                Func<int, float> pit1m = z => z < 0 ? float.NaN : (z >= 10 && z <= 14 ? 0.6f : 0f);
                Assert(RM_PitDrawMath.PickRowForDrawnClick(12, 12.5f, pit1m, 4) == 13,
                    "can-fail: a click on row 12's centre means row 13 (drawn at 12.9), not row 12 (drawn at 11.9: 'one down')");
                Assert(RM_PitDrawMath.PickRowForDrawnClick(12, 12.95f, pit1m, 4) == 13, "near row 13's drawn centre: row 13");
                Assert(RM_PitDrawMath.PickRowForDrawnClick(14, 14.5f, pit1m, 4) == 14, "the north row: nothing sunk beyond it, stays");
                Assert(RM_PitDrawMath.PickRowForDrawnClick(5, 5.5f, pit1m, 4) == 5, "ground: ground");
                Assert(RM_PitDrawMath.PickRowForDrawnClick(9, 9.9f, pit1m, 4) == 9, "the ground row south of the pit stays ground");
                Assert(RM_PitDrawMath.PickRowForDrawnClick(3, 3.5f, z => float.NaN, 4) == 3, "off the map: unchanged");
                // ties keep the clicked row: a collapsed south lip (every row drawn at 10.0)
                Func<int, float> flat = z => z >= 10 && z <= 12 ? (z + 0.5f - 10f) : 0f;
                Assert(RM_PitDrawMath.PickRowForDrawnClick(10, 10.2f, flat, 4) == 10, "equal drawn rows: the clicked row");
                string src = Src("Superdeep", "RM_PitDepthDraw.cs");
                string patch = Between(src, "public static class RM_Patch_PitClickDrawnRow", "[HarmonyFinalizer]");
                Assert(src.Contains("[HarmonyPatch(typeof(RimWorld.FloatMenuOptionProvider_DraftedMove), \"GetSingleOption\")]"), "on the drafted 'go here' option");
                Assert(patch.Contains("RM_PitDrawMath.PickRowForDrawnClick(c.z, context.clickPosition.z,")
                    && patch.Contains("RM_Patch_PitDepthDrawOffset.RestingSinkAt(pawn, q)"), "the pure picker over the production sink");
                Assert(Between(src, "[HarmonyFinalizer]", "private static RM_MapComponent_Excavation ExcavationOf(").Length > 0
                    && src.Contains("ClickedRef(context) = __state;"), "the vanilla clicked cell is put back after the option is built");
                string rest = Between(src, "public static float RestingSinkAt(", "private static float Clamped(");
                Assert(rest.Contains("Clamped(ex, pawn.Map, c, d, RimMandrakeFlowWorksSettings.pitSinkPerLevel)"), "the resting sink is the drawn one (same clamp)");
            });
        }
    }
}
