// Owner question cards 2026-10-22 (joints study D2, D3, D7), offline halves:
//   REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST  "Player turns the reel": the outlet, nozzle and picture turn with the reel's rotation.
//   PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID   the pipe-into-tank arm rises to the tank's flange, where the hose ends.
//   HOSE_GIRTH_TUNE_MUCH_THINNER         "Darker shadow first": the empty hose's contact shadow darker and a little wider.
// Production geometry is compiled in (HoseMath, HoseRelay, ReelIntakeGeometry, LiquidJoinRule); the game wiring
// (Graphic_HoseReel, CompHoseReel, PlaceWorker_HoseReelOutlet, RM_LiquidJoins, RM_MapComponent_Hoses, the reel def) is read
// as text. NOT proven here: the pictures on a map (live look owed).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ReelRiserShadowChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static bool Near(double a, double b, double tol = 1e-9) => Math.Abs(a - b) < tol;
        private static bool Near(V2 a, V2 b, double tol = 1e-9) => V2.Dist(a, b) < tol;
        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));
        private static string ModFile(params string[] rel) => Regex.Replace(File.ReadAllText(Path.Combine(
            Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("FluidDef.cs"))), Path.Combine(rel))), @"\s+", " ");

        private static readonly string[] Facing = { "north", "east", "south", "west" };

        /// <summary>Rotate (x, z) clockwise seen from above by deg (RimWorld's Rot4.AsAngle sense: 90 takes north to east).</summary>
        private static V2 Cw(V2 v, double deg)
        {
            double a = -deg * Math.PI / 180, c = Math.Cos(a), s = Math.Sin(a);
            return new V2(v.X * c - v.Z * s, v.X * s + v.Z * c);
        }

        /// <summary>The lay a reel's own hose makes in an open world, its footprint solid (as RM_MapComponent_Hoses.LayFrom).</summary>
        private static HoseLay LayFrom(HoseReelRect reel, Cell target)
        {
            var w = new CordWorld(50, 40);
            for (int x = reel.X0; x < reel.X0 + reel.W; x++)
                for (int z = reel.Z0; z < reel.Z0 + reel.H; z++) w.SetBlocked(new Cell(x, z), BlockKind.Device);
            return HoseMath.Lay(w, reel.Mouth, target.Centre, new HoseShapeParams { MinBendRadius = 1.2 }, 7, null, reel.Outward);
        }

        /// <summary>How far the lay runs BEHIND the reel: the furthest any point goes against the target's direction past the
        /// reel's own edge on that side (0 = never behind; the old west outlet to an east target ran ~1.6 + a bend behind).</summary>
        private static double Behind(HoseReelRect reel, HoseLay lay, V2 toTarget)
        {
            V2 c = reel.Centre;
            double edge = Math.Abs(toTarget.X) > 0 ? reel.W / 2.0 : reel.H / 2.0, worst = 0;
            foreach (V2 p in lay.Flat)
            {
                double along = (p.X - c.X) * toTarget.X + (p.Z - c.Z) * toTarget.Z;
                worst = Math.Max(worst, -along - edge);
            }
            return worst;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("ReelFacing_outlet_nozzle_and_picture_turn_with_the_reel", () =>
            {
                Assert(new HoseReelRect(10, 10, 2, 2).Rot == 3, "a reel built with no facing faces west (the picture's own outlet)");
                V2[] want = { new V2(0, 1), new V2(1, 0), new V2(0, -1), new V2(-1, 0) };
                foreach (string look in ReelIntakeGeometry.Looks)
                {
                    var tips = new List<V2>();
                    for (int rot = 0; rot < 4; rot++)
                    {
                        var r = new HoseReelRect(10, 10, 2, 2) { Look = look, Rot = rot };
                        V2 u = r.Outward.Value, tip = r.NozzleTip - r.Centre, mouth = r.Mouth;
                        Assert(Near(u, want[rot]), look + " " + Facing[rot] + ": outlet faces " + u + ", want " + want[rot]);
                        HoseReelRect.ArtPose(rot, out float ang, out bool mirror);
                        Assert(ang == 0f && mirror == (rot == 1), Facing[rot] + ": the picture is drawn unturned, mirrored only facing east");
                        // REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED: the facing's own picture's nozzle, measured in its art frame
                        // (west/east: the west art, mirrored east; north/south: their own art turned into that frame), lands on the tip
                        ReelIntakeGeometry.OutletTip(look, true, out double dx, out double dz, rot);
                        V2 drawn = rot == 1 ? new V2(-dx, dz) : rot == 0 ? new V2(dz, -dx) : rot == 2 ? new V2(-dz, dx) : new V2(dx, dz);
                        Assert(Near(drawn, tip, 1e-6), look + " " + Facing[rot] + ": the tip " + tip + " is where the drawn nozzle lands " + drawn);
                        Assert(tip.X * u.X + tip.Z * u.Z > 0.5, look + " " + Facing[rot] + ": the drawn nozzle sits on the outlet side (" + tip + ")");
                        // the routing start sits inside the footprint, in the outlet-side cells, at the nozzle's height across the outlet
                        Assert(r.Contains(mouth.Floor), look + " " + Facing[rot] + ": the hose starts inside the reel " + mouth);
                        Cell edge = r.EdgeCells(new Cell((int)u.X, (int)u.Z))[0];
                        Assert(u.X != 0 ? mouth.Floor.X == edge.X : mouth.Floor.Z == edge.Z, look + " " + Facing[rot] + ": start in the outlet-side cells");
                        Assert(u.X != 0 ? Near(mouth.Z, r.NozzleTip.Z) : Near(mouth.X, r.NozzleTip.X), look + " " + Facing[rot] + ": start level with the nozzle");
                        tips.Add(tip);
                    }
                    Assert(Near(tips[1], new V2(-tips[3].X, tips[3].Z)), look + ": east is west mirrored");
                    Assert(tips.Distinct().Count() == 4, look + " can-fail: the four facings put the nozzle in four places");
                }
                var west = new HoseReelRect(10, 10, 2, 2);
                Assert(Near(west.ToArt(west.FromArt(0.3, -0.7).X, west.FromArt(0.3, -0.7).Z), new V2(0.3, -0.7)), "west: ToArt undoes FromArt");
                for (int rot = 0; rot < 4; rot++)
                {
                    var r = new HoseReelRect(10, 10, 2, 2) { Rot = rot };
                    V2 f = r.FromArt(0.3, -0.7), b = r.ToArt(f.X, f.Z);
                    Assert(Near(b, new V2(0.3, -0.7)), Facing[rot] + ": ToArt undoes FromArt (" + b + ")");
                }
                Assert(new HoseReelRect(4, 4, 1, 1) { Rot = 1 }.Outward == null, "a 1x1 reel has no outlet to turn");
            });

            Case("ReelFacing_target_on_the_outlet_side_lays_with_no_U_loop", () =>
            {
                // a target 12 squares out on each side; the reel turned to face it lays straight out, never behind the reel
                var targets = new[] { (rot: 1, cell: new Cell(32, 20), dir: new V2(1, 0)), (rot: 3, cell: new Cell(0, 20), dir: new V2(-1, 0)),
                                      (rot: 0, cell: new Cell(20, 33), dir: new V2(0, 1)), (rot: 2, cell: new Cell(20, 8), dir: new V2(0, -1)) };
                foreach (var t in targets)
                {
                    var reel = new HoseReelRect(19, 20, 2, 2) { Look = "Scrapper", Rot = t.rot };
                    if (t.rot == 3) reel = new HoseReelRect(11, 20, 2, 2) { Look = "Scrapper", Rot = 3 };
                    HoseLay lay = LayFrom(reel, t.cell);
                    Assert(lay.Ok && lay.Outlet, Facing[t.rot] + "-facing reel to a " + Facing[t.rot] + " target: laid through the outlet (" + (lay.Reason ?? "ok") + ")");
                    double back = Behind(reel, lay, t.dir);
                    Assert(back < 0.05, Facing[t.rot] + "-facing reel: the hose runs " + back.ToString("0.00") + " behind the reel, want none");
                    double straight = V2.Dist(reel.Mouth, t.cell.Centre);
                    Assert(lay.PathLen < straight * 1.25 + 1.0, Facing[t.rot] + ": route " + lay.PathLen.ToString("0.0") + " vs straight " + straight.ToString("0.0") + " (no loop)");
                }
                // can-fail: the old reel (west outlet) to the east target loops back round behind itself
                var old = new HoseReelRect(19, 20, 2, 2) { Look = "Scrapper" };
                HoseLay oldLay = LayFrom(old, new Cell(32, 20));
                Assert(oldLay.Ok && Behind(old, oldLay, new V2(1, 0)) > 1.0,
                    "can-fail: a west outlet to an east target runs " + Behind(old, oldLay, new V2(1, 0)).ToString("0.00") + " behind the reel (the U-loop)");
            });

            Case("ReelFacing_relay_inlet_turns_with_the_relay", () =>
            {
                foreach (string look in ReelIntakeGeometry.Looks)
                    foreach (bool dep in new[] { false, true })
                    {
                        ReelIntakeGeometry.WestInlet(look, dep, out double perp, out double depth);
                        // west-facing relay (the drawn picture): a hose from the west couples on the brass inlet, as before
                        var w = new HoseReelRect(20, 20, 2, 2) { Rot = 3 };
                        V2 pw = HoseRelay.DrawnEnd(w, new Cell(19, 20), look, dep, out V2 iw);
                        Assert(Near(pw, new V2(20 - depth, 21 + perp)) && Near(iw, new V2(1, 0)), look + " west relay: inlet at " + pw);
                        // east-facing (mirrored): the inlet is now on the EAST side, same height
                        var e = new HoseReelRect(20, 20, 2, 2) { Rot = 1 };
                        V2 pe = HoseRelay.DrawnEnd(e, new Cell(22, 21), look, dep, out _);
                        Assert(Near(pe, new V2(22 + depth, 21 + perp)), look + " east relay: the mirrored inlet at " + pe);
                        // north-facing (its own picture, measured turned into the art frame): the inlet is on the NORTH side
                        ReelIntakeGeometry.WestInlet(look, dep, out double nPerp, out double nDepth, 0);
                        var n = new HoseReelRect(20, 20, 2, 2) { Rot = 0 };
                        V2 pn = HoseRelay.DrawnEnd(n, new Cell(20, 22), look, dep, out V2 inn);
                        Assert(Near(pn, new V2(21 + nPerp, 22 + nDepth)) && Near(inn, new V2(0, -1)), look + " north relay: the north picture's inlet at " + pn);
                        // can-fail: an east-facing relay's WEST side is no longer the inlet (it is the picture's east outline)
                        V2 pew = HoseRelay.DrawnEnd(e, new Cell(19, 20), look, dep, out _);
                        Assert(!Near(pew, pw, 1e-6) || Math.Abs(perp) < 1e-6, look + " can-fail: the mirrored relay's west side reads the outline, not the inlet");
                        Assert(Math.Abs(pew.X - 20) <= HoseRelay.EndTolerance && Math.Abs(pn.Z - 22) <= HoseRelay.EndTolerance,
                            look + ": turned ends stay on the drawn outline");
                    }
            });

            Case("ReelFacing_def_rotatable_west_default_preview_and_legacy_saves", () =>
            {
                string def = ModFile("Defs", "Hose", "RM_HoseReel.xml");
                Assert(def.Contains("<rotatable>true</rotatable>") && !def.Contains("<rotatable>false</rotatable>"), "the reel def is rotatable");
                Assert(def.Contains("<defaultPlacingRot>West</defaultPlacingRot>"), "a new reel places facing west (the picture as drawn)");
                Assert(def.Contains("RimMandrake.FlowWorks.Hose.PlaceWorker_HoseReelOutlet"), "the build preview draws the exit side");
                string g = Src("Hose", "Graphic_HoseReel.cs");
                Assert(g.Contains("public override void Print(") && g.Contains("public override void DrawWorker(") && g.Contains("public override Mesh MeshAt(")
                       && Regex.Matches(g, @"HoseReelRect\.ArtPose\(").Count >= 3, "the reel picture is placed by ArtPose (mesh, draw and print)");
                string comp = Src("Hose", "CompHoseReel.cs");
                Assert(comp.Contains("Rot = parent.Rotation.AsInt"), "the reel's rect carries its rotation");
                Assert(comp.Contains("\"rmReelFacing\"") && comp.Contains("parent.Rotation = Rot4.West") && comp.Contains("parent.Position += IntVec3.East"),
                    "a reel saved before it turned loads facing west, footprint kept");
                Assert(!comp.Contains("Placeholder picture"), "north/south have their own pictures: no placeholder line (REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED)");
                Assert(g.Contains("\"_north\", \"_south\"") && g.Contains("Reel_Deployed"), "the graphic loads each art's _north / _south picture");
                string pw = Src("Hose", "PlaceWorker_HoseReelOutlet.cs");
                Assert(pw.Contains("public override void DrawGhost(") && pw.Contains("Rot = rot.AsInt") && pw.Contains("r.Outward"),
                    "the preview reads the ghost's rotation and the outlet");
                string hoses = Src("Hose", "RM_MapComponent_Hoses.cs");
                // HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES: the seat and axis moved into HoseJoints.NozzleCoupling (HoseRelay.cs), -Outward
                Assert(hoses.Contains("HoseJoints.NozzleCoupling(r.Rect, out V2 inw)") && Src("Hose", "HoseRelay.cs").Contains("inward = -(r.Outward")
                       && !hoses.Contains("new V2(HoseReelRect.NozzleSeat, 0), new V2(1, 0)"),
                    "the reel-end coupling points into the turned nozzle, not always east");
                Assert(Src("RimMandrake_FlowWorks.csproj").Contains(@"Hose\PlaceWorker_HoseReelOutlet.cs"), "the preview is in the mod build");
            });

            Case("PipeTankRiser_ends_on_the_hose_flange_not_under_the_skid", () =>
            {
                // tank 2x2 at (20, 20); pipes west of it on the lower row (19, 20) and upper row (19, 21), east on (22, 20)
                foreach (string look in TankPortGeometry.Looks)
                {
                    Assert(TankPortGeometry.PortPoint(look, 20, 20, 2, 2, 1, 0, out V2 portW), look + " west port");
                    Assert(TankPortGeometry.PortPoint(look, 20, 20, 2, 2, -1, 0, out V2 portE), look + " east port");
                    foreach (var (cx, cz, dx, port) in new[] { (19, 20, 1, portW), (19, 21, 1, portW), (22, 20, -1, portE) })
                    {
                        double[] r = LiquidJoinRule.RiserStub(cx, cz, dx, 0, 20, 20, 2, 2, port.Z, false);
                        Assert(r != null && r.Length == 6, look + " riser from (" + cx + "," + cz + ")");
                        Assert(Near(r[0], cx + 0.5) && Near(r[1], cz + 0.5), "the riser leaves the pipe cell's centre");
                        Assert(Near(r[2], cx + 0.5) && Near(r[3], port.Z), "it rises to the flange's height " + port.Z.ToString("0.000"));
                        Assert(Near(r[4], port.X) && Near(r[5], port.Z), look + ": it ends ON the flange the hose ends on (" + r[4] + "," + r[5] + ") vs " + port);
                        Assert(Math.Abs(r[3] - 21.0) < 0.1, look + ": the flange is at mid-height, z + 1.0 (" + r[3].ToString("0.000") + ")");
                        double[] u = LiquidJoinRule.RiserStub(cx, cz, dx, 0, 20, 20, 2, 2, port.Z, true);
                        Assert(u.Length >= 8 && Near(u[u.Length - 2], 21) && Near(u[u.Length - 1], 21), "with the under-run it goes on to the centre");
                        // can-fail: the old stub enters at the pipe's own row, under the skid on the lower row
                        double[] old = LiquidJoinRule.CentreStub(cx, cz, dx, 0, 20, 20, 2, 2);
                        if (cz == 20) Assert(Math.Abs(old[1] - port.Z) > 0.4, "can-fail: the old arm met the edge at z " + old[1] + ", half a square under the flange");
                    }
                    Assert(LiquidJoinRule.RiserStub(20, 19, 0, 1, 20, 20, 2, 2, portW.Z, false) == null, "a pipe from the south gets no riser (no flange there)");
                    Assert(LiquidJoinRule.RiserStub(19, 22, 1, 0, 20, 20, 2, 2, portW.Z, false) == null, "a pipe beside the corner, not the tank, gets none");
                }
            });

            Case("PipeTankRiser_wiring_link_stops_layer_prints_flange_follows", () =>
            {
                string j = Src("Machinery", "RM_LiquidJoins.cs");
                Assert(j.Contains("public static bool RiserInto(") && j.Contains("b.def.defName != Hose.TankPortGeometry.TankDef")
                       && j.Contains("Hose.TankPortGeometry.PortPoint(PipeLook.LookOfThing(b)"), "RiserInto: the universal tank's measured flange, as the hose's PortEnd");
                Assert(j.Contains("RM_LiquidJoins.RiserInto(parent.Position, c - parent.Position, partner, out _)) return;"),
                    "the pipe's own arm stops at its centre where a riser takes over");
                Assert(j.Contains("LiquidJoinRule.RiserStub(c.x, c.z, d.x, d.z, r.minX, r.minZ, r.Width, r.Height, portZ, under)"),
                    "the stub layer prints the riser");
                Assert(j.Contains("public override bool Visible => RM_MachinerySettings.pipesUnderToCentre || RM_MachinerySettings.pipeLinksIntoMachines;"),
                    "the riser shows with the links on even when the under-run is off");
                Assert(j.Contains("p.z = (float)pz;"), "the (off) flange fitting moves onto the riser's end");
                string hoses = Src("Hose", "RM_MapComponent_Hoses.cs");
                string hoseMath = Src("Hose", "HoseMath.cs");
                Assert(hoses.Contains("TankPortGeometry.HosePort(fe.Port.def.defName")
                    && hoseMath.Contains("if (def == TankDef) return PortPoint(look, bx, bz, bw, bh, sx, sz, out port);"),
                    "the hose ends on the same table the riser reads (HosePort hands the tank to PortPoint)");
            });

            Case("HoseShadow_empty_is_darker_and_wider_full_unchanged", () =>
            {
                Assert(HoseMath.ShadowAlpha(0) >= 0.75 && HoseMath.ShadowAlpha(0) > 0.55 + 0.15, "empty hose shadow darker: " + HoseMath.ShadowAlpha(0) + " (was 0.55)");
                Assert(HoseMath.ShadowWidth(0) > 1.15 && HoseMath.ShadowWidth(0) <= 1.5, "empty hose shadow a little wider: " + HoseMath.ShadowWidth(0) + "x (was 1.15x)");
                Assert(Near(HoseMath.ShadowAlpha(1), 0.85) && Near(HoseMath.ShadowWidth(1), 1.5), "the full hose's shadow is unchanged (0.85, 1.5x)");
                Assert(HoseMath.ShadowAlpha(0.5) >= HoseMath.ShadowAlpha(0) && HoseMath.ShadowWidth(0.5) >= HoseMath.ShadowWidth(0), "filling never thins the shadow");
                Assert(HoseMath.ShadowWidth(0) * HoseMath.FlatVisible > HoseMath.MeshWidthFlat(HoseMath.FlatVisible) * HoseMath.FlatBand + 0.03,
                    "the empty shadow shows past the hose's edges");
                string hoses = Src("Hose", "RM_MapComponent_Hoses.cs");
                Assert(Regex.Matches(hoses, @"HoseMath\.ShadowWidth\(").Count >= 3 && Regex.Matches(hoses, @"HoseMath\.ShadowAlpha\(").Count >= 2,
                    "the laid, carried and dragged shadows all read the rule");
                Assert(!hoses.Contains("Shadow(0.55f") && !hoses.Contains("vis * 1.15f"), "can-fail: no draw keeps the old 0.55 / 1.15x literal");
                Assert(HoseStyles.SharedShadow == "Strand_Shadow", "one shared shadow picture serves all four looks (no picture touched)");
            });
        }
    }
}
