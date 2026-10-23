// CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT (owner walk 2026-10-23, screenshot 20261023070639_1: a cord from a junction ran straight
// up into a pump's SOUTH pipe flange): "the electrical plug is shown going into a pipe slot. Weird. It should favor diagonal
// approaches sliding underneath, to avoid confusion."
//   flange   a cord into a 4-flange pump (ports at every edge midpoint) never meets the footprint at a cell-edge midpoint
//   diagonal the cord's last run outside the footprint comes in at a diagonal (30-60 degrees off the side's normal)
//   under    the cord ends at the footprint centroid, drawn at Conduits altitude, below the Building layer
//   can fail SlideUnder off brings back the straight, edge-midpoint plug (the screenshot)
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class CordSlideUnderChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "slideunder: " + msg);

        /// <summary>Vanilla AltitudeLayer.Building (RimSage, Verse/AltitudeLayer.cs, 1.6).</summary>
        private const int LayerBuilding = 15;

        private static double RectD(MachineInfo m, V2 v) =>
            Math.Max(Math.Max(m.X0 - v.X, v.X - (m.X0 + m.W)), Math.Max(m.Z0 - v.Z, v.Z - (m.Z0 + m.H)));

        /// <summary>Every cell-edge midpoint on a footprint's perimeter: where a pipe or hose port's flange sits.</summary>
        private static List<V2> PortMidpoints(MachineInfo m)
        {
            var o = new List<V2>();
            for (int i = 0; i < m.W; i++) { o.Add(new V2(m.X0 + i + 0.5, m.Z0)); o.Add(new V2(m.X0 + i + 0.5, m.Z0 + m.H)); }
            for (int j = 0; j < m.H; j++) { o.Add(new V2(m.X0, m.Z0 + j + 0.5)); o.Add(new V2(m.X0 + m.W, m.Z0 + j + 0.5)); }
            return o;
        }

        /// <summary>A battery feeding a pump through a straight conduit run that meets the pump from side d (0 S, 1 N, 2 W, 3 E).</summary>
        private static CordWorld Scene(int side, int w, int h, out MachineInfo pump)
        {
            var wd = new CordWorld(24, 24);
            pump = new MachineInfo { Id = "pump", Kind = MachineKind.Consumer, X0 = 10, Z0 = 10, W = w, H = h };
            for (int x = 10; x < 10 + w; x++) for (int z = 10; z < 10 + h; z++) wd.SetBlocked(new Cell(x, z), BlockKind.Device);
            Cell step = side == 0 ? new Cell(0, -1) : side == 1 ? new Cell(0, 1) : side == 2 ? new Cell(-1, 0) : new Cell(1, 0);
            Cell hook = side == 0 ? new Cell(10, 9) : side == 1 ? new Cell(10, 10 + h) : side == 2 ? new Cell(9, 10) : new Cell(10 + w, 10);
            Cell c = hook;
            for (int k = 0; k < 6; k++) { wd.SetConduit(c); c = c + step; }
            Cell batCell = c;
            wd.SetBlocked(batCell, BlockKind.Device);
            wd.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = batCell.X, Z0 = batCell.Z, Hookups = new List<Cell> { new Cell(c.X - step.X, c.Z - step.Z) } });
            pump.Hookups.Add(hook);
            wd.Machines.Add(pump);
            return wd;
        }

        /// <summary>For each strand end inside the pump: the last vertex outside the footprint, the run before it, the end.</summary>
        private static void Ends(List<LaidPiece> ps, MachineInfo m, Action<V2, V2, V2> each)
        {
            foreach (CordStrand s in ps.SelectMany(p => p.Strands).Where(s => !s.OverFace))
            {
                List<V2> q = new List<V2>(s.Pts);
                if (RectD(m, q[q.Count - 1]) > 0) q.Reverse();
                if (RectD(m, q[q.Count - 1]) > 0) continue;
                int i = q.Count - 1;
                while (i > 0 && RectD(m, q[i]) <= 0) i--;
                // the run outside: back along the strand ~0.12 cell from the last outside vertex
                int j = i;
                double run = 0;
                while (j > 0 && run < 0.12) { run += V2.Dist(q[j], q[j - 1]); j--; }
                each(q[i], q[i] - q[j], q[q.Count - 1]);
            }
        }

        public static void Run()
        {
            int ends = 0, onFlange = 0, square = 0, offCentre = 0, offCentreOld = 0, onFlangeOld = 0;
            var msg = new List<string>();
            foreach (var size in new[] { (1, 1), (2, 2), (3, 1), (1, 2) })
                for (int side = 0; side < 4; side++)
                {
                    CordWorld w = Scene(side, size.Item1, size.Item2, out MachineInfo pump);
                    var ports = PortMidpoints(pump);
                    V2 nrm = side == 0 ? new V2(0, 1) : side == 1 ? new V2(0, -1) : side == 2 ? new V2(1, 0) : new V2(-1, 0);
                    Ends(new CordBuilder().Build(w, new BuildOptions(), c => true), pump, (last, run, end) =>
                    {
                        ends++;
                        double gap = ports.Min(p => V2.Dist(p, last));
                        if (gap < 0.2) { onFlange++; msg.Add($"{size} side {side}: crosses at {last}, {gap:0.00} from a port midpoint"); }
                        double cos = (run.X * nrm.X + run.Z * nrm.Z) / Math.Max(1e-9, run.Len);
                        double ang = Math.Acos(Math.Max(-1, Math.Min(1, cos))) * 180 / Math.PI;
                        if (ang < 30 || ang > 60) { square++; msg.Add($"{size} side {side}: approach {ang:0} deg off the normal"); }
                        if (V2.Dist(end, CordBuilder.Centroid(pump)) > 1e-6) offCentre++;
                    });
                    Ends(new CordBuilder().Build(Scene(side, size.Item1, size.Item2, out MachineInfo p2), new BuildOptions { SlideUnder = false }, c => true), p2,
                         (last, run, end) => { if (PortMidpoints(p2).Min(p => V2.Dist(p, last)) < 0.2) onFlangeOld++; });
                }
            Check(ends >= 16 && onFlange == 0, $"flange: {onFlange}/{ends} cords meet the footprint on a port midpoint" + (msg.Count > 0 ? ": " + string.Join("; ", msg.Take(6)) : ""));
            Check(ends >= 16 && square == 0, $"diagonal: {square}/{ends} cords come in square, not diagonal");
            Check(offCentre == 0 && DrawOrder.LayerConduits < LayerBuilding, $"under: {offCentre}/{ends} cords end off the centroid; cord layer {DrawOrder.LayerConduits} vs Building {LayerBuilding}");
            Check(onFlangeOld >= 8, $"can fail: SlideUnder off plugs {onFlangeOld} cords into a port midpoint (screenshot 20261023070639_1)");
            Console.WriteLine($"  slideunder: {ends} pump ends, {onFlange} on a flange, {square} square; old rule {onFlangeOld} on a flange");
        }
    }
}
