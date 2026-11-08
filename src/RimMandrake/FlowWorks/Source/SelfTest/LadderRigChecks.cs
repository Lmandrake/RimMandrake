// LADDER_RAILS_DRAWN_ON_THE_FACE, pass 8 (bars wall_ladder_rides_on_rails, ladder_state_legible,
// portable_ladder_leans_on_its_wall). Offline checks on the production geometry RM_LadderDraw prints under the oblique cut
// (RM_LadderRigMath.Strokes): rails fixed on all four walls in both states, each rail's stroke wide enough to see at 64 px a
// cell; a side-wall ladder drawn as posts and rungs, not as dotted rungs; a raised ladder out on the ground beyond its rim
// and a lowered one between its rails; a portable leaning on every wall; one too short for its wall lying flat with no
// access. Each case has a can-fail.
// NOT proven here: how the strokes look on screen against the real face and lip (the textures, the altitudes, the lip
// occlusion), nor a ladder re-printing when it is raised or the pit is dug deeper. Live look owed.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LadderRigChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const string Walls = "NESW";

        // A 3-row pit, its column's far rim at z 21 and near lip at z 18; the ladder's square per wall: the north row for the
        // far face, the south row for the near face, the middle row for a side wall.
        private const int X = 10;
        private const float Rim = 21f, Near = 18f;

        private static int CellZ(int rot) => rot == 0 ? 20 : rot == 2 ? 18 : 19;

        // Face heights the walls really print for this column (RM_PitLookMath.ObliqueFace at the default sink 0.3): 2 m, 4 m, 8 m.
        private static float Face(int levels) => RM_PitLookMath.ObliqueFace(levels, Rim - Near, 0.3f, 0.15f);

        private static List<RM_LadderRigMath.Stroke> Rig(int rot, float face, bool raised, bool portable = false, bool reaches = true, bool steel = false)
        {
            return RM_LadderRigMath.Strokes(rot, X, CellZ(rot), face, face, Rim, Near, raised, portable, reaches, steel);
        }

        private static List<RM_LadderRigMath.Stroke> Of(List<RM_LadderRigMath.Stroke> all, RM_LadderRigMath.Kind kind)
        {
            List<RM_LadderRigMath.Stroke> list = new List<RM_LadderRigMath.Stroke>();
            foreach (RM_LadderRigMath.Stroke s in all)
            {
                if (s.Kind == kind) list.Add(s);
            }
            return list;
        }

        private static float MinZ(List<RM_LadderRigMath.Stroke> l) { float m = float.MaxValue; foreach (var s in l) m = Math.Min(m, Math.Min(s.Z0, s.Z1)); return m; }
        private static float MaxZ(List<RM_LadderRigMath.Stroke> l) { float m = float.MinValue; foreach (var s in l) m = Math.Max(m, Math.Max(s.Z0, s.Z1)); return m; }
        private static float MinX(List<RM_LadderRigMath.Stroke> l) { float m = float.MaxValue; foreach (var s in l) m = Math.Min(m, Math.Min(s.X0, s.X1) - s.Width * 0.5f); return m; }
        private static float MaxX(List<RM_LadderRigMath.Stroke> l) { float m = float.MinValue; foreach (var s in l) m = Math.Max(m, Math.Max(s.X0, s.X1) + s.Width * 0.5f); return m; }

        private static bool Same(RM_LadderRigMath.Stroke a, RM_LadderRigMath.Stroke b)
        {
            return a.Kind == b.Kind && a.X0 == b.X0 && a.Z0 == b.Z0 && a.X1 == b.X1 && a.Z1 == b.Z1 && a.Width == b.Width && a.U0 == b.U0 && a.U1 == b.U1;
        }

        private static void Near1(float got, float want, string what)
        {
            Assert(Math.Abs(got - want) < 0.005f, what + ": " + got.ToString("0.000") + " (want " + want.ToString("0.000") + ")");
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("LadderRig_rails_fixed_on_every_wall_both_states", () =>
            {
                Assert(Face(4) > 0.5f && Face(8) > Face(4) && Face(16) > Face(8), "can-fail: the test pit's faces grow with depth");
                foreach (int levels in new[] { 4, 8, 16 })
                {
                    float face = Face(levels);
                    for (int rot = 0; rot < 4; rot++)
                    {
                        foreach (bool raised in new[] { false, true })
                        {
                            string at = Walls[rot] + (raised ? " raised" : " lowered") + " at " + levels + " levels: ";
                            List<RM_LadderRigMath.Stroke> rails = Of(Rig(rot, face, raised), RM_LadderRigMath.Kind.Rail);
                            Assert(rails.Count == 2, at + "two rails, got " + rails.Count);
                            RM_LadderRigMath.Stroke l = rails[0], r = rails[1];
                            float lx = RM_LadderRigMath.RailLine(l), rx = RM_LadderRigMath.RailLine(r);
                            Assert(l.U0 == 0f && r.U1 == 1f && l.U1 < 0.2f && r.U0 > 0.8f, at + "each rail is its own side's column of the rail texture");
                            foreach (RM_LadderRigMath.Stroke s in rails)
                            {
                                Assert(s.X0 == s.X1, at + "a rail runs straight down its wall");
                                Assert(s.Z0 > s.Z1, at + "a rail runs from its top down");
                                Assert(RM_LadderRigMath.RailStroke(s) * 64f >= 5f, at + "rail stroke " + (RM_LadderRigMath.RailStroke(s) * 64f).ToString("0.0") + " px at 64 px a cell (want >= 5)");
                                Assert(RM_LadderRigMath.RailStroke(s) * 23f >= 1.9f, at + "rail stroke at 23 px a cell (want ~2 px)");
                            }
                            float gap = rx - lx;
                            float cx = X + 0.5f;
                            switch (rot)
                            {
                                case 0:
                                    Near1(lx, cx - RM_LadderRigMath.RailHalf, at + "left rail line");
                                    Near1(rx, cx + RM_LadderRigMath.RailHalf, at + "right rail line");
                                    Near1(l.Z0, Rim + RM_LadderRigMath.RailAbove, at + "rails start just over the rim");
                                    Near1(l.Z1, Rim - face, at + "rails reach the face foot");
                                    break;
                                case 2:
                                    Near1(gap, 2f * RM_LadderRigMath.RailHalf, at + "rail spacing");
                                    Near1(l.Z1, Near, at + "the near face is hidden: rails end at the lip");
                                    Assert(l.Z0 - l.Z1 >= 0.3f, at + "the hooks stand over the lip (" + (l.Z0 - l.Z1).ToString("0.00") + ")");
                                    break;
                                default:
                                    float edge = rot == 1 ? X + 1f : X;
                                    Assert(Math.Abs(lx - edge) < 0.5f && Math.Abs(rx - edge) < 0.5f, at + "both rails on this side of the square, by its wall");
                                    Assert(lx > X && rx < X + 1f, at + "rails inside the square");
                                    Near1(l.Z1, Math.Max(Near, CellZ(rot) + 0.5f - face), at + "rails run down to the floor (or the lip that hides it)");
                                    Assert(l.Z0 > CellZ(rot) + 0.5f, at + "rails start above the square's middle (the rim's line)");
                                    break;
                            }
                            Assert(gap >= 0.3f, at + "two rails apart, not one blur: gap " + gap.ToString("0.00"));
                        }
                    }
                }
                // can-fail: one quad of the whole rail texture (pass 7) would draw each rail under 3 px at 64
                float wholeTexture = 0.74f * RM_LadderRigMath.RailStrokeInSlice * RM_LadderRigMath.RailSliceU;
                Assert(wholeTexture * 64f < 3f, "can-fail: the pass-7 whole-texture rail was " + (wholeTexture * 64f).ToString("0.0") + " px");
            });

            Case("LadderRig_side_wall_ladder_has_posts_and_rungs", () =>
            {
                float face = Face(8);
                foreach (bool steel in new[] { false, true })
                {
                    foreach (int rot in new[] { 1, 3 })
                    {
                        string at = Walls[rot] + (steel ? " steel: " : " wood: ");
                        List<RM_LadderRigMath.Stroke> all = Rig(rot, face, false, steel: steel);
                        List<RM_LadderRigMath.Stroke> slices = Of(all, RM_LadderRigMath.Kind.Ladder);
                        List<RM_LadderRigMath.Stroke> rails = Of(all, RM_LadderRigMath.Kind.Rail);
                        Assert(slices.Count == 3, at + "post, rungs, post: got " + slices.Count);
                        RM_LadderRigMath.Stroke pl = slices[0], rung = slices[1], pr = slices[2];
                        float l0 = steel ? RM_LadderRigMath.SteelPostL0 : RM_LadderRigMath.WoodPostL0;
                        float r1 = steel ? RM_LadderRigMath.SteelPostR1 : RM_LadderRigMath.WoodPostR1;
                        Assert(pl.U0 == l0 && pl.U1 == rung.U0 && rung.U1 == pr.U0 && pr.U1 == r1, at + "the slices are the texture's post, rung and post columns");
                        Assert(pl.Width * 64f >= 2.5f && pr.Width * 64f >= 2.5f, at + "posts at their full stroke (" + (pl.Width * 64f).ToString("0.0") + " px)");
                        Assert(rung.Width * 64f >= 6f, at + "rungs wide enough to read (" + (rung.Width * 64f).ToString("0.0") + " px)");
                        Near1(pl.X0 + pl.Width * 0.5f, rung.X0 - rung.Width * 0.5f, at + "left post meets the rungs");
                        Near1(rung.X0 + rung.Width * 0.5f, pr.X0 - pr.Width * 0.5f, at + "the rungs meet the right post");
                        foreach (RM_LadderRigMath.Stroke s in slices)
                        {
                            Assert(s.Front == RM_LadderRigMath.LadderWidth, at + "every slice keeps the ladder's rung spacing");
                            Assert(s.Z0 == pl.Z0 && s.Z1 == pl.Z1, at + "the slices run together");
                        }
                        float lx = RM_LadderRigMath.RailLine(rails[0]), rx = RM_LadderRigMath.RailLine(rails[1]);
                        Assert(MinX(slices) > lx && MaxX(slices) < rx, at + "the ladder rides between its rails");
                        Assert(MaxX(slices) - MinX(slices) >= 0.18f, at + "the ladder as drawn is at least 0.18 cells wide (11.5 px at 64)");
                    }
                }
                // can-fail: the pass-7 side ladder squeezed the whole 160-px texture into 0.24 cells: posts under 2 px
                float squeezed = 0.24f * (RM_LadderRigMath.WoodPostL1 - RM_LadderRigMath.WoodPostL0);
                Assert(squeezed * 64f < 2f, "can-fail: the pass-7 squeezed post was " + (squeezed * 64f).ToString("0.0") + " px");
            });

            Case("LadderRig_raised_and_lowered_look_different_on_every_wall", () =>
            {
                foreach (int levels in new[] { 4, 16 })
                {
                    float face = Face(levels);
                    for (int rot = 0; rot < 4; rot++)
                    {
                        string at = Walls[rot] + " at " + levels + " levels: ";
                        List<RM_LadderRigMath.Stroke> down = Rig(rot, face, false), up = Rig(rot, face, true);
                        List<RM_LadderRigMath.Stroke> dl = Of(down, RM_LadderRigMath.Kind.Ladder), ul = Of(up, RM_LadderRigMath.Kind.Ladder);
                        List<RM_LadderRigMath.Stroke> dr = Of(down, RM_LadderRigMath.Kind.Rail), ur = Of(up, RM_LadderRigMath.Kind.Rail);
                        Assert(dr.Count == 2 && ur.Count == 2 && Same(dr[0], ur[0]) && Same(dr[1], ur[1]), at + "the rails stay put in both states");
                        Assert(dl.Count >= 1 && ul.Count == 1, at + "a ladder in both states");
                        RM_LadderRigMath.Stroke u = ul[0];
                        Assert(Math.Abs(u.X1 - u.X0) + Math.Abs(u.Z1 - u.Z0) >= 0.69f, at + "the raised ladder is a whole ladder, not a stub");
                        int cz = CellZ(rot);
                        switch (rot)
                        {
                            case 0:
                                Assert(MinZ(ul) >= Rim - 0.1f && MaxZ(ul) >= Rim + 0.6f, at + "raised: out on the ground beyond the far rim");
                                Assert(MinZ(dl) <= Rim - face + 0.01f, at + "lowered: down the face to its foot");
                                break;
                            case 2:
                                Assert(MinZ(ul) <= Near - 0.6f && MaxZ(ul) <= Near + 0.1f, at + "raised: out on the near ground beyond the lip");
                                Assert(MinZ(dl) >= Near - 0.01f && MaxZ(dl) >= Near + 0.4f, at + "lowered: its top stands over the lip, in the pit");
                                break;
                            case 1:
                                Assert(Math.Min(u.X0, u.X1) >= X + 1f - 0.15f && Math.Max(u.X0, u.X1) >= X + 1.6f, at + "raised: out on the ground beyond the east rim");
                                Assert(MaxX(dl) <= X + 1f && MinX(dl) >= X, at + "lowered: inside the square, on its wall");
                                break;
                            default:
                                Assert(Math.Max(u.X0, u.X1) <= X + 0.15f && Math.Min(u.X0, u.X1) <= X - 0.6f, at + "raised: out on the ground beyond the west rim");
                                Assert(MaxX(dl) <= X + 1f && MinX(dl) >= X, at + "lowered: inside the square, on its wall");
                                break;
                        }
                        if (rot != 2)
                        {
                            // the wall between the rails is bare when raised: no ladder below the rim's line
                            float rimLine = rot == 0 ? Rim : cz + 0.5f;
                            Assert(rot == 0 ? MinZ(ul) > rimLine - 0.1f : Math.Abs(ul[0].Z0 - ul[0].Z1) < 0.01f, at + "raised: the rails are bare");
                            Assert(MinZ(dl) < rimLine - 0.3f, at + "lowered: the ladder is down the wall");
                        }
                    }
                }
            });

            Case("LadderRig_portable_leans_on_every_wall", () =>
            {
                foreach (int levels in new[] { 2, 4, 8, 16 })
                {
                    float face = Face(levels);
                    for (int rot = 0; rot < 4; rot++)
                    {
                        string at = Walls[rot] + " at " + levels + " levels: ";
                        // asked raised: a portable rides no rails, so it is never raised
                        List<RM_LadderRigMath.Stroke> all = Rig(rot, face, true, portable: true, reaches: true);
                        Assert(Of(all, RM_LadderRigMath.Kind.Rail).Count == 0, at + "a portable has no rails");
                        Assert(Of(all, RM_LadderRigMath.Kind.Flat).Count == 0, at + "a portable that reaches stands up");
                        List<RM_LadderRigMath.Stroke> l = Of(all, RM_LadderRigMath.Kind.Ladder);
                        Assert(l.Count == 1, at + "one leaning ladder");
                        RM_LadderRigMath.Stroke p = l[0];
                        float lean = RM_LadderRigMath.LeanDegrees(p);
                        Assert(lean >= 10f, at + "leans " + lean.ToString("0.0") + " degrees (want >= 10)");
                        Assert(p.Z0 > p.Z1, at + "top above foot");
                        int cz = CellZ(rot);
                        switch (rot)
                        {
                            case 0:
                                Assert(p.Z0 >= Rim, at + "top at the far rim");
                                Assert(p.Z1 <= Rim - face + 0.001f && p.Z1 >= Near, at + "foot out on the floor, below the face foot");
                                break;
                            case 2:
                                Assert(p.Z1 <= Near + 0.001f && p.Z0 >= Near + 0.5f, at + "top stands over the near lip");
                                break;
                            default:
                                float edge = rot == 1 ? X + 1f : X;
                                Assert(Math.Abs(p.X0 - edge) < 0.1f, at + "top at the side rim");
                                Assert(Math.Abs(p.X1 - edge) > Math.Abs(p.X0 - edge) + 0.2f && p.X1 > X && p.X1 < X + 1f, at + "foot out from its wall, in the square");
                                Assert(p.Z1 >= Near - 0.001f && p.Z1 < cz + 0.5f, at + "foot on the floor (or where the lip hides it)");
                                break;
                        }
                    }
                }
                // can-fail: a fixed ladder hangs straight
                Assert(RM_LadderRigMath.LeanDegrees(Of(Rig(0, Face(8), false), RM_LadderRigMath.Kind.Ladder)[0]) < 0.5f, "can-fail: a fixed lowered ladder does not lean");
            });

            Case("LadderRig_portable_too_short_lies_flat_and_frees_nobody", () =>
            {
                foreach (int levels in new[] { 4, 16 })
                {
                    float face = Face(levels);
                    for (int rot = 0; rot < 4; rot++)
                    {
                        string at = Walls[rot] + " at " + levels + " levels: ";
                        List<RM_LadderRigMath.Stroke> all = Rig(rot, face, false, portable: true, reaches: false);
                        Assert(all.Count == 1 && all[0].Kind == RM_LadderRigMath.Kind.Flat, at + "one flat ladder, nothing standing, no rails");
                        RM_LadderRigMath.Stroke f = all[0];
                        bool side = rot == 1 || rot == 3;
                        float half = side ? RM_LadderRigMath.FlatHalfLength : RM_LadderRigMath.FlatHalfThick;
                        Assert(f.Z0 - half >= Near - 0.001f, at + "in view: not under the near lip");
                        if (Rim - face - Near >= 2f * half)
                        {
                            Assert(f.Z0 + half <= Rim - face + 0.001f, at + "on the drawn floor, not on the face");
                        }
                        Assert(f.Angle == (side ? 90f : 0f), at + "lying along its wall");
                        Assert(f.X0 > X && f.X0 < X + 1f, at + "in its square");
                    }
                }
                Assert(Of(Rig(0, Face(4), false, portable: true, reaches: true), RM_LadderRigMath.Kind.Flat).Count == 0, "can-fail: a reaching portable is not flat");
                // ... and the code gives it no access: every way out asks the same reach rule the drawing is chosen by
                Assert(!RM_PitAccessMath.LadderReaches(7, 0, 6), "a 3 m portable does not span a 3.5 m wall");
                string u = RiverSwitchFlipChecks.Src("Superdeep/RM_LadderUtility.cs");
                RiverSwitchFlipChecks.Has(u, @"if \(ladder == null \|\| !RM_LadderUtility\.Reaches\(ladder\)\)", "LadderLetsOut frees nobody on a short ladder");
                RiverSwitchFlipChecks.Has(u, @"RM_PitAccessMath\.LadderReaches\(", "Reaches is the access rule");
                string d = RiverSwitchFlipChecks.Src("Superdeep/RM_LadderDraw.cs");
                RiverSwitchFlipChecks.Has(d, @"bool reaches = !portable \|\| RM_LadderUtility\.Reaches\(ladder\);", "the drawing asks the same rule");
                string m = RiverSwitchFlipChecks.Src("Superdeep/RM_CliffMask.cs");
                RiverSwitchFlipChecks.Has(m, @"!RM_LadderUtility\.Reaches\(ladder\)", "the masks' climb join asks it");
            });

            Case("LadderRig_draw_prints_the_rig", () =>
            {
                string d = RiverSwitchFlipChecks.Src("Superdeep/RM_LadderDraw.cs");
                RiverSwitchFlipChecks.Has(d, @"RM_LadderRigMath\.Strokes\(rot\.AsInt, c\.x, c\.z, face, drop, rim, near, comp\.EffectivelyRaised, portable, reaches, steel\)", "TryPrint prints RigMath's strokes");
                RiverSwitchFlipChecks.Has(d, @"case RM_LadderRigMath\.Kind\.Rail: Run\(layer, RailTile, RailCap", "rails print with the rail texture");
                RiverSwitchFlipChecks.Has(d, @"float capFull = s\.Front \* capAspect, tileH = s\.Front \* tileAspect;", "tile heights from the stroke's Front");
                RiverSwitchFlipChecks.Has(d, @"s\.Width, h, rot, y, s\.U0, s\.U1,", "each tile shows the stroke's own texture columns");
                RiverSwitchFlipChecks.Has(d, @"comp\.ShortGraphic\?\.MatSingle", "a short portable prints its flat art");
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(d, @"RailWidth|SideRailWidth"), "can-fail: no whole-texture rail width left in the drawing");
                string proj = RiverSwitchFlipChecks.Src("RimMandrake_FlowWorks.csproj");
                RiverSwitchFlipChecks.Has(proj, @"<Compile Include=""Superdeep\\RM_LadderRigMath\.cs"" />", "the mod compiles the rig geometry");
            });
        }
    }
}
