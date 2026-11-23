// LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB: the pipe piece drawn over the pump's south cap (PumpSouthSocket). The twin that reads the
// installed art is selftest_pump_south_socket.py. NOT proven here: the mesh in the game.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PumpSouthSocketChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static bool Inside(List<PumpSouthSocket.Vert> q, double x, double z)
        {
            for (int k = 0; k + 3 < q.Count; k += 4)
            {
                bool all = true;
                for (int j = 0; j < 4 && all; j++)
                {
                    PumpSouthSocket.Vert a = q[k + j], b = q[k + (j + 1) % 4];
                    // clockwise corners: the inside is on the right of every side
                    if ((b.X - a.X) * (z - a.Z) - (b.Z - a.Z) * (x - a.X) > 1e-9) all = false;
                }
                if (all) return true;
            }
            return false;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PumpSocket_pipe_covers_the_cap_and_leaves_the_rim", () =>
            {
                foreach (string look in new[] { "Scrapper", "Industrial", "Modern", "Futuristic" })
                {
                    Assert(PumpSouthSocket.TryCap(look, out PumpSouthSocket.Cap c), look + " has a measured cap");
                    List<PumpSouthSocket.Vert> q = PumpSouthSocket.Quads(c);
                    Assert(q.Count == PumpSouthSocket.Columns * 8, "two quads a column");
                    for (int d = 0; d < 360; d += 5)
                    {
                        double r = d * Math.PI / 180, cs = Math.Cos(r), sn = Math.Sin(r);
                        Assert(Inside(q, c.X + 0.97 * c.HalfW * cs, c.Z + 0.97 * c.HalfH * sn), $"{look}: the cap is covered at {d} degrees");
                        if (d <= 180)
                            Assert(!Inside(q, c.X + 1.08 * c.HalfW * cs, c.Z + 1.08 * c.HalfH * sn), $"{look}: the rim shows at {d} degrees");
                    }
                    Assert(Inside(q, 0.5, 0.001) && !Inside(q, 0.5, -0.001), look + ": the piece starts on the shared cell edge");
                    Assert(Inside(q, PumpSouthSocket.PipeLo + 0.001, 0.0005) && !Inside(q, PumpSouthSocket.PipeLo - 0.002, 0.0005),
                        look + ": at the edge it is as wide as the pipe");
                    foreach (PumpSouthSocket.Vert v in q)
                        Assert(v.X > 0 && v.X < 1 && v.Z >= 0 && v.Z < 0.25 && v.V == v.Z && v.U >= PumpSouthSocket.PipeLo - 1e-9 && v.U <= PumpSouthSocket.PipeHi + 1e-9,
                            look + ": inside the pump's cell, on the drawn pipe");
                }
                Assert(PumpSouthSocket.TryCap(null, out PumpSouthSocket.Cap un) && PumpSouthSocket.TryCap("Scrapper", out PumpSouthSocket.Cap sc) && un.Z == sc.Z,
                    "an unstyled pump reads the Scrapper art");
            });
            Case("PumpSocket_drawn_by_the_pipe_layer_only_with_a_pipe", () =>
            {
                string joins = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidJoins.cs"));
                Assert(joins.Contains("if (risers && di < 4 && d.z == 1 && RM_LiquidJoins.DrawsOwnFlanges(b)) nSockets += PrintSouthSocket(t, c, b);"),
                    "a pipe south of a pump prints the socket, under the pipe-arm setting");
                Assert(joins.Contains("if (RM_LiquidJoins.DrawsOwnFlanges(b)) continue;"), "no loose flange beside the pump's own");
            });
        }
    }
}
