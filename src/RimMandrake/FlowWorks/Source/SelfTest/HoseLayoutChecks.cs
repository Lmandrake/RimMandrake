// HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS step 4: a reel laid to a fixture's port right beside it must never be DRAWN through
// the reel or the fixture. The placements are the offline explorer's port sweep (FlowWorks/Tools/hose_geometry_explore.py
// sweep_cases("port")) cut to the near ring |fx|, |fz| <= 3 -- every one of its 126 "layout" cases (the port's end run
// inside the reel, or the fixture in the nozzle's way) lies there. Each placement is laid as EnsureLay does
// (HoseMath.PortLay over LayAlong, the reel's own footprint solid) and drawn flat and charged as DrawAll does
// (HoseMath.DrawnPose); a lay is either refused with a reason or drawn clear of both bodies.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseLayoutChecks
    {
        /// <summary>World offset of the reel's cell (0, 0) and the world's size: room on every side for a hose that swings round.</summary>
        internal const int O = 16, Size = 36;
        /// <summary>The reel's mouth sits up to 0.31 inside its own rect (HoseReelRect.Mouth, N facing): the first stretch of
        /// the lead-out is on the drum by design.</summary>
        internal const double MouthExempt = 0.5;
        /// <summary>A drawn point counts as through a body when it is this far inside the body's rect.</summary>
        internal const double Inset = 0.02;

        internal sealed class Placement
        {
            public string Key;
            public Cell Dir;          // the reel's nozzle facing
            public int Fx, Fz;        // the 2x2 fixture's corner, relative to the reel's corner
            public char Face;         // the fixture face carrying the port
            public bool Tank;         // RM_LiquidTank E/W port height (z + 1.025); else the edge midpoint
        }

        internal sealed class Result
        {
            public Placement P;
            public HoseLay Lay;
            /// <summary>Null = refused or drawn clear; else which body the drawn hose runs through, and where.</summary>
            public string Hit;
        }

        private static readonly (char c, Cell d)[] Facings = { ('E', new Cell(1, 0)), ('N', new Cell(0, 1)), ('W', new Cell(-1, 0)), ('S', new Cell(0, -1)) };

        /// <summary>The explorer's port sweep order, cut to |fx|, |fz| &lt;= <paramref name="span"/>.</summary>
        internal static List<Placement> Sweep(int span = 3)
        {
            var o = new List<Placement>();
            foreach (var f in Facings)
                for (int fx = -span; fx <= span; fx++)
                    for (int fz = -span; fz <= span; fz++)
                    {
                        if (Math.Abs(fx) < 2 && Math.Abs(fz) < 2) continue;   // the fixture would stand on the reel
                        foreach (var (face, tank) in new[] { ('E', true), ('W', true), ('N', false), ('S', false) })
                            o.Add(new Placement { Key = $"{f.c} {fx} {fz} {face}", Dir = f.d, Fx = fx, Fz = fz, Face = face, Tank = tank });
                    }
            return o;
        }

        /// <summary>The port's flange point (on the fixture's edge) and the axis into the fixture.</summary>
        internal static (V2 at, V2 axis) Port(Placement p)
        {
            double x0 = O + p.Fx, z0 = O + p.Fz, zc = z0 + (p.Tank ? 1.025 : 1.0);
            switch (p.Face)
            {
                case 'W': return (new V2(x0, zc), new V2(1, 0));
                case 'E': return (new V2(x0 + 2, zc), new V2(-1, 0));
                case 'S': return (new V2(x0 + 1, z0), new V2(0, 1));
                default: return (new V2(x0 + 1, z0 + 2), new V2(0, -1));
            }
        }

        private static bool Inside(V2 q, double x0, double z0, double x1, double z1)
            => q.X > x0 + Inset && q.X < x1 - Inset && q.Z > z0 + Inset && q.Z < z1 - Inset;

        /// <summary>Where the drawn centreline runs through the reel (past its mouth) or the fixture; null when clear.</summary>
        internal static string BodyHit(IList<V2> pts, HoseReelRect reel, int fx0, int fz0)
        {
            double s = 0;
            for (int i = 0; i < pts.Count; i++)
            {
                if (i > 0) s += V2.Dist(pts[i - 1], pts[i]);
                V2 q = pts[i];
                if (s > MouthExempt && Inside(q, reel.X0, reel.Z0, reel.X0 + reel.W, reel.Z0 + reel.H)) return $"through the reel at s {s:0.00}";
                if (Inside(q, fx0, fz0, fx0 + 2, fz0 + 2)) return $"through the fixture at s {s:0.00}";
            }
            return null;
        }

        internal static Result LayOne(Placement p)
        {
            var w = new CordWorld(Size, Size);
            int fx0 = O + p.Fx, fz0 = O + p.Fz;
            for (int x = 0; x < 2; x++) for (int z = 0; z < 2; z++) w.SetBlocked(new Cell(fx0 + x, fz0 + z), BlockKind.Wall);
            HoseReelRect reel = HoseCurveChecks.Facing(O, O, p.Dir);
            // LayFrom: an unfed nozzled reel's own footprint is solid and its hose leaves along Outward
            for (int x = 0; x < 2; x++) for (int z = 0; z < 2; z++) w.SetBlocked(new Cell(O + x, O + z), BlockKind.Device);
            var (at, axis) = Port(p);
            V2 cellEnd = (at - axis * 0.5).Floor.Centre;
            var sp = new HoseShapeParams();
            HoseLay lay = HoseMath.PortLay((e1, in1) => HoseMath.LayAlong(w, reel.Mouth, new List<Cell>(), e1, sp, 1, in1, reel.Outward),
                cellEnd, null, at, axis, l => HoseMath.BodyHit(l, at, axis, reel, fx0, fz0, 2, 2));
            var r = new Result { P = p, Lay = lay };
            if (!lay.Ok) return r;
            foreach (double e in new[] { 0.0, 1.0 })
            {
                List<V2> drawn = HoseMath.DrawnPose(lay, e, int.MaxValue / 2, HoseCurveChecks.T, sp.PlumpAmount, at, axis);
                string hit = BodyHit(drawn, reel, fx0, fz0);
                if (hit != null) { r.Hit = (e == 0 ? "flat " : "plump ") + hit; break; }
            }
            return r;
        }

        internal static List<Result> RunAll(int span = 3) => Sweep(span).Select(LayOne).ToList();

        internal static string Summary(List<Result> all)
        {
            int refused = all.Count(r => !r.Lay.Ok), hit = all.Count(r => r.Hit != null);
            int tooClose = all.Count(r => !r.Lay.Ok && r.Lay.Reason == HoseMath.TooCloseToBend);
            int body = all.Count(r => !r.Lay.Ok && r.Lay.Reason == HoseMath.BodyInTheWay);
            return $"{all.Count} placements: {all.Count - refused - hit} laid clear, {refused} refused ({tooClose} too close to bend, {body} body in the way), {hit} drawn through a body";
        }

        /// <summary>The nine placements the old PortLay fallback DREW through the reel or the fixture (step4/base.txt).</summary>
        internal static readonly string[] WasDrawnThrough = { "E -2 -1 E", "N -2 -1 E", "N 1 3 S", "N 2 -1 W", "W 0 -2 N", "W 0 2 S", "W 2 -1 W", "S -2 0 E", "S 2 0 W" };
        /// <summary>Too close for any G2 curve: the old LayAlong kept a kinked shaped pose; step 5 refuses them.</summary>
        internal static readonly string[] TooClose = { "N -1 2 W", "E 3 1 W", "N 1 2 N", "W -3 1 E" };
        /// <summary>Room to spare: these must lay, G2, so a solve that refuses everything cannot pass.</summary>
        internal static readonly string[] Roomy = { "E 3 3 E", "N 3 3 S", "W -3 3 E", "E 3 -3 W" };

        internal static Placement Parse(string key)
        {
            string[] f = key.Split(' ');
            Cell d = Facings.First(x => x.c == f[0][0]).d;
            return new Placement { Key = key, Dir = d, Fx = int.Parse(f[1]), Fz = int.Parse(f[2]), Face = f[3][0], Tank = f[3][0] == 'E' || f[3][0] == 'W' };
        }

        /// <summary>The default-run guard: a fixed 17-placement sample (the full near ring is --hose-layouts full, ~220 s).</summary>
        internal static void Run(Action<string, Action> Case)
        {
            // the placements are laid INSIDE each case, so a filtered run (--only) does not pay ~27 s for cases it skips
            Case("HoseLayout_old_drawn_through_placements_now_refused_or_clear", () =>
            {
                Result[] was = WasDrawnThrough.Select(k => LayOne(Parse(k))).ToArray();
                var bad = was.Where(r => r.Hit != null).ToList();
                if (bad.Count > 0) throw new Exception(bad.Count + " drawn through a body: " + string.Join(" | ", bad.Select(r => r.P.Key + ": " + r.Hit)));
                var mute = was.Where(r => !r.Lay.Ok && string.IsNullOrEmpty(r.Lay.Reason)).ToList();
                if (mute.Count > 0) throw new Exception("refused without a reason: " + mute[0].P.Key);
            });
            Case("HoseLayout_too_close_to_bend_is_refused_with_the_player_reason", () =>
            {
                Result[] close = TooClose.Select(k => LayOne(Parse(k))).ToArray();
                foreach (Result r in close)
                    if (r.Lay.Ok || r.Lay.Reason != HoseMath.TooCloseToBend)
                        throw new Exception(r.P.Key + ": " + (r.Lay.Ok ? "laid (" + (r.Lay.G2 ? "g2" : "shaped: " + r.Lay.G2Why) + ")" : "refused '" + r.Lay.Reason + "'"));
            });
            Case("HoseLayout_roomy_placements_still_lay_g2_and_clear", () =>
            {
                Result[] roomy = Roomy.Select(k => LayOne(Parse(k))).ToArray();
                foreach (Result r in roomy)
                    if (!r.Lay.Ok || !r.Lay.G2 || r.Hit != null)
                        throw new Exception(r.P.Key + ": " + (!r.Lay.Ok ? "refused '" + r.Lay.Reason + "'" : r.Hit ?? "not g2: " + r.Lay.G2Why));
            });
        }

        /// <summary>The whole near ring (slow): nothing drawn through, every refusal has a reason, most of it lays.</summary>
        internal static void RunFull(Action<string, Action> Case)
        {
            List<Result> all = RunAll();
            Case($"HoseLayout_never_drawn_through_its_reel_or_fixture ({Summary(all)})", () =>
            {
                var bad = all.Where(r => r.Hit != null).ToList();
                if (bad.Count > 0)
                    throw new Exception(bad.Count + " drawn through a body: " + string.Join(" | ", bad.Take(4).Select(r => r.P.Key + ": " + r.Hit)));
                var mute = all.Where(r => !r.Lay.Ok && string.IsNullOrEmpty(r.Lay.Reason)).ToList();
                if (mute.Count > 0) throw new Exception(mute.Count + " refused without a reason, e.g. " + mute[0].P.Key);
                // the instrument can see: most of the near ring lays (a sweep that refuses everything proves nothing)
                if (all.Count(r => r.Lay.Ok) < all.Count / 2) throw new Exception("fewer than half the placements lay: " + Summary(all));
            });
        }

        /// <summary>One line per placement (the step 4 record).</summary>
        internal static void Report(string path, int span)
        {
            List<Result> all = RunAll(span);
            var sb = new StringBuilder(Summary(all) + "\n");
            foreach (Result r in all)
                sb.Append(r.P.Key).Append(": ").Append(!r.Lay.Ok ? "REFUSED " + r.Lay.Reason : r.Hit != null ? "HIT " + r.Hit : "CLEAR")
                    .Append(r.Lay.Ok && r.Lay.PortWhy != null ? " {port: " + r.Lay.PortWhy + "}" : "").Append(r.Lay.Ok ? (r.Lay.G2 ? " [g2]" : " [shaped: " + r.Lay.G2Why + "]") : "")
                    .Append(r.Lay.Ok ? $" bend {r.Lay.MinBendFlat:0.00}/{r.Lay.MinBendPlump:0.00} lead {r.Lay.Lead0:0.00}" : "").Append('\n');
            System.IO.File.WriteAllText(path, sb.ToString());
        }
    }
}
