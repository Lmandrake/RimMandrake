// HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (owner 2026-10-16): offline halves of the liquid-join draw hooks -- LiquidJoinRule's
// geometry, the hose thickness scale, and the shipped wiring (settings defaults, the section layer, the link patch).
// NOT proven here: the meshes on a map (validation.py rows owed when the art lands).
using System;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LiquidJoinChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static bool Near(double a, double b) => Math.Abs(a - b) < 1e-9;

        public static void Run(Action<string, Action> Case)
        {
            Case("LiquidJoin_flange_face_on_the_shared_edge", () =>
            {
                foreach (var (dx, dz, ang) in new[] { (1, 0, 0.0), (0, 1, 90.0), (-1, 0, 180.0), (0, -1, 270.0) })
                {
                    LiquidJoinRule.Flange(dx, dz, out double ox, out double oz, out double a);
                    // the flange's face = centre + half its size along the facing direction = the cell edge (0.5 from centre)
                    Assert(Near(Math.Abs(ox + dx * LiquidJoinRule.FlangeSize / 2) + Math.Abs(oz + dz * LiquidJoinRule.FlangeSize / 2), 0.5),
                        $"flange ({dx},{dz}) face on the cell edge, got ({ox},{oz})");
                    Assert(Near(a, ang), $"flange ({dx},{dz}) faces {ang}, got {a}");
                }
                bool threw = false;
                try { LiquidJoinRule.Flange(1, 1, out _, out _, out _); } catch (ArgumentException) { threw = true; }
                Assert(threw, "can-fail: a diagonal flange is refused");
            });
            Case("LiquidJoin_shared_edge", () =>
            {
                // pump 1x1 at (5,5), 2x2 tank east of it at (6,5): shared edge x=6, z 5..6, side east
                Assert(LiquidJoinRule.SharedEdge(5, 5, 1, 1, 6, 5, 2, 2, out double mx, out double mz, out int sx, out int sz)
                       && Near(mx, 6) && Near(mz, 5.5) && sx == 1 && sz == 0, $"east edge, got ({mx},{mz}) side ({sx},{sz})");
                // tank north of a 2x1 pump, offset by one: overlap x 6..7
                Assert(LiquidJoinRule.SharedEdge(5, 5, 2, 1, 6, 6, 2, 2, out mx, out mz, out sx, out sz)
                       && Near(mx, 6.5) && Near(mz, 6) && sx == 0 && sz == 1, $"north edge, got ({mx},{mz}) side ({sx},{sz})");
                Assert(LiquidJoinRule.SharedEdge(6, 5, 2, 2, 5, 5, 1, 1, out mx, out _, out sx, out _) && sx == -1 && Near(mx, 6), "west edge");
                Assert(LiquidJoinRule.SharedEdge(5, 7, 1, 1, 5, 5, 2, 2, out _, out mz, out _, out sz) && sz == -1 && Near(mz, 7), "south edge");
                // can-fail: corner-only touch, a gap, an overlap
                Assert(!LiquidJoinRule.SharedEdge(5, 5, 1, 1, 6, 6, 2, 2, out _, out _, out _, out _), "corner touch has no edge");
                Assert(!LiquidJoinRule.SharedEdge(5, 5, 1, 1, 7, 5, 2, 2, out _, out _, out _, out _), "a gap has no edge");
                Assert(!LiquidJoinRule.SharedEdge(5, 5, 2, 2, 6, 6, 2, 2, out _, out _, out _, out _), "an overlap has no edge");
            });
            Case("LiquidJoin_hose_thickness_scale", () =>
            {
                double was = HoseMath.WidthScale;
                try
                {
                    Assert(Near(HoseMath.WidthScale, 1.0), "the shipped hose width is unchanged until the owner rules");
                    double w0 = HoseMath.VisibleWidth(0, 1), w1 = HoseMath.VisibleWidth(1, 1);
                    HoseMath.WidthScale = LiquidJoinRule.ProposedHoseThickness;
                    Assert(Near(HoseMath.VisibleWidth(0, 1), w0 * 0.65) && Near(HoseMath.VisibleWidth(1, 1), w1 * 0.65), "the scale reaches every width");
                    Assert(HoseMath.VisibleWidth(0, 1) > 0.227, "the proposed hose stays at least as thick as the rigid pipe (0.227 cell)");
                }
                finally { HoseMath.WidthScale = was; }
            });
            Case("LiquidJoin_wiring_shipped", () =>
            {
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                string set = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_MachinerySettings.cs"));
                string hs = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_HoseSettings.cs"));
                string draw = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                Assert(set.Contains("public static bool joinFittings = false;") && set.Contains("\"joinFittings\", false"),
                    "connector fittings ship OFF (placeholder art) until the owner rules");
                Assert(set.Contains("public static bool pipeLinksIntoMachines = true;"), "pipes link into tanks/machines by default");
                Assert(hs.Contains("public static float thickness = 1f;") && hs.Contains("\"hose_thickness\", 1f"), "hose thickness ships at 1");
                Assert(hs.Contains("\"|T\" + thickness"), "a thickness change re-lays every hose (ShapeFingerprint)");
                Assert(joins.Contains("class SectionLayer_RM_LiquidJoins : SectionLayer") && joins.Contains("nameof(Graphic_Linked.ShouldLinkWith)"),
                    "the section layer and the pipe link patch are shipped");
                Assert(draw.Contains("RM_LiquidJoins.DrawHosePortFitting(fe.Port"), "the hose port draws the pipe's fitting");
            });
        }
    }
}
