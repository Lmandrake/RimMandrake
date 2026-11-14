// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// The last say on a floor cord's length (bar cords_lie_slack, owner by card 2026-11-14 "Loosen the short cords": the 1.4x slack bar applies to every cord, the
// builder makes short leads droop more). A strand drawn shorter than Bar times its chord keeps both fitted ends exactly as laid (each fitting's straight bit, a
// machine's run under its art, a plug's tied loop) and has the cord between them laid again as one lobe of the length Aim asks, three arcs: it turns out of the
// head's way, sweeps round to the other side at an even rate and turns into the tail's way. Where no lobe passes, the spare cord lies as one broad loop at the
// middle (the bend bar's own loop). Either is kept only on clear floor, off every other fitting, and only when the bend bar (CordShapeAudit) counts nothing new
// on it; else the strand stays as it was. Why the turns out of the fittings are firm: a lead whose fittings face along a 2-cell chord cannot reach 1.4x with
// its curvature held under the bend bar's 90 degrees a cell (measured 2026-11-14, offline solver over the oracle scenes' leads).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public static class CordSlacken
    {
        /// <summary>The bar (drawn length over chord, cords_lie_slack's oracle); the length a slackened strand aims at, then the shortest it may settle for.</summary>
        public const double Bar = 1.4, Aim = 1.5, Settle = 1.45;
        /// <summary>A strand this close to its fittings (chord, cells) is a stub inside one cell: the bar does not read it.</summary>
        public const double MinChord = 1.0;
        /// <summary>A strand whose chord is over LongChord cells also strays at least MinExcursion off it (cord_slack_lay's oracle).</summary>
        public const double LongChord = 4.0, MinExcursion = 1.0;
        /// <summary>Shares of the lobe's length over which it turns out of each fitting's way, tried in order: a short lead's lobe must turn firmly out of a fitting
        /// that faces along it, or it bends past the bar's 90 degrees a cell in its middle (measured 2026-11-14 on the oracle scenes' 2-cell leads).</summary>
        private static readonly double[] Shoulders = { 0.12, 0.09, 0.15, 0.22, 0.3 };
        /// <summary>The most the lobe's swing may lean off its own chord (radians).</summary>
        private const double MaxSwing = 2.2;
        /// <summary>The broad loop a lobe that cannot pass falls back on: radii tried (cells), at or over the bar's 0.45 loop radius and <see cref="CordLayer.RoundLoopMinR"/>.</summary>
        private static readonly double[] LoopRadii = { 0.5, 0.55 };
        /// <summary>Where along the free stretch the loop is tried (share of it), the middle first.</summary>
        private static readonly double[] LoopAt = { 0.5, 0.35, 0.65 };
        private const double Step = 0.05;
        /// <summary>Lab trace: why a strand under the bar kept its lay (the geometry check prints it under GSS_GEOM_ALL=1).</summary>
        internal static Action<string> Why;
        /// <summary>The SelfTest's "before" switch (--no-slacken): the builder as it laid cords before this pass. Never set by the mod.</summary>
        internal static bool Off;

        /// <summary>Drawn length over endpoint chord; 0 for a strand with no chord.</summary>
        internal static double Ratio(List<V2> p)
        {
            if (p == null || p.Count < 2) return 0;
            double c = V2.Dist(p[0], p[p.Count - 1]);
            return c < 1e-9 ? 0 : Geo.Length(p) / c;
        }

        /// <summary>The strand laid again slack, or null when it is already slack, has no chord the bar reads, or no lobe passes.
        /// <paramref name="pinA"/>/<paramref name="pinB"/>: cord (cells) at each end left exactly as laid past where it reaches clear floor;
        /// <paramref name="clear"/>: any further ground rule (off other fittings); <paramref name="ties"/>: the
        /// strand's tied loops, kept inside the ends and moved along with the tail; <paramref name="side"/>: which side the lobe tries first.</summary>
        internal static List<V2> Slacken(CordWorld w, List<V2> P, double pinA, double pinB, string endA, string endB,
                                         Func<V2, bool> clear, List<CordTie> ties, int side)
        {
            if (Off || P == null || P.Count < 3) return null;
            int n = P.Count;
            double chordAll = V2.Dist(P[0], P[n - 1]);
            if (chordAll < MinChord) return null;
            double[] cum = Geo.CumLen(P);
            double L = cum[n - 1];
            bool flat = chordAll > LongChord && Excursion(P) < MinExcursion + 0.05;
            if (L / chordAll >= Bar + 0.02 && !flat) return null;
            bool Free(V2 q) => Open(w, q);
            // each end: past its run under a wall or art, past its tied loop, then its pin
            double headStart = 0, tailStart = 0;
            for (int i = 0; i < n && !Free(P[i]); i++) headStart = cum[i];
            for (int i = n - 1; i >= 0 && !Free(P[i]); i--) tailStart = L - cum[i];
            double hs = headStart + pinA, ts = tailStart + pinB;
            if (ties != null)
                foreach (CordTie t in ties)
                {
                    if (t.S0 + t.S1 < L) hs = Math.Max(hs, t.S1 + 0.15);
                    else ts = Math.Max(ts, L - t.S0 + 0.15);
                }
            int ia = -1, ib = -1;
            for (int i = 1; i < n - 1; i++) if (cum[i] >= hs) { ia = i; break; }
            for (int i = n - 2; i > 0; i--) if (L - cum[i] >= ts) { ib = i; break; }
            if (ia < 0 || ib < 0 || ib - ia < 2) { Why?.Invoke(endA + "|" + endB + " no room between the pins (" + hs.ToString("0.00") + "+" + ts.ToString("0.00") + " of " + L.ToString("0.00") + ")"); return null; }
            V2 m0 = P[ia], m1 = P[ib], d = m1 - m0;
            double W = d.Len;
            bool lobes = W >= 0.6;   // pins closer than this leave no room for a lobe: only the loop is tried
            double ang = Math.Atan2(d.Z, d.X);
            double ha = Wrap(Heading(P[ia] - P[ia - 1]) - ang), hb = Wrap(Heading(P[ib + 1] - P[ib]) - ang);
            double keep = cum[ia] + (L - cum[ib]);
            int uOld = CordShapeAudit.Unforced(w, endA, endB, P), kOld = CordShapeAudit.Corners(P).Count;
            var doorsOld = new HashSet<Cell>();
            foreach (V2 q in P) if (w.IsDoor(q.Floor)) doorsOld.Add(q.Floor);
            var no = new List<string>();
            int audits = 0;
            List<V2> Accept(List<V2> Q, string tag)
            {
                audits++;
                if (Ratio(Q) < Bar) { no.Add(tag + " ratio " + Ratio(Q).ToString("0.00")); return null; }
                if (chordAll > LongChord && Excursion(Q) < MinExcursion) { no.Add(tag + " flat " + Excursion(Q).ToString("0.00")); return null; }
                int uNew = CordShapeAudit.Unforced(w, endA, endB, Q), kNew = CordShapeAudit.Corners(Q).Count;
                if (uNew > uOld || kNew > kOld) { no.Add(tag + " bends " + uOld + ">" + uNew + " corners " + kOld + ">" + kNew); return null; }
                if (ties != null)
                {
                    double grow = Geo.Length(Q) - L;
                    for (int i = 0; i < ties.Count; i++)
                    {
                        CordTie t = ties[i];
                        if (t.S0 + t.S1 >= L) { t.S0 += grow; t.S1 += grow; ties[i] = t; }
                    }
                }
                return Q;
            }
            string Ground(List<V2> pts, int from, int to)
            {
                for (int i = from; i < to; i++)
                {
                    V2 q = pts[i];
                    if (!Free(q)) return "ground";
                    if (clear != null && !clear(q)) return "fitting";
                    if (w.IsDoor(q.Floor) && !doorsOld.Contains(q.Floor)) return "door";
                }
                return null;
            }
            int s0 = side >= 0 ? 1 : -1;
            foreach (double target in lobes ? (flat ? new[] { Aim, Aim + 0.15, Aim + 0.3 } : new[] { Aim, Settle, Bar + 0.02 }) : new double[0])
            {
                double Lm = target * chordAll - keep;
                if (Lm <= W * 1.03) { no.Add("ends-hold-length"); continue; }
                foreach (double r in Shoulders)
                    foreach (int sg in new[] { s0, -s0 })
                    {
                        if (audits >= MaxAudits) break;
                        if (!Solve(ha, hb, Lm, W, sg, r, out double tA, out double tB)) { no.Add("solve"); continue; }
                        List<V2> mid = Lobe(ha, hb, tA, tB, r, Lm, W, ang, m0, m1);
                        string bad = Ground(mid, 0, mid.Count);
                        if (bad != null) { no.Add(bad); continue; }
                        var Q = new List<V2>(ia + mid.Count + (n - ib));
                        for (int i = 0; i <= ia; i++) Q.Add(P[i]);
                        for (int i = 1; i < mid.Count - 1; i++) Q.Add(mid[i]);
                        for (int i = ib; i < n; i++) Q.Add(P[i]);
                        List<V2> ok = Accept(Q, "lobe");
                        if (ok != null) return ok;
                    }
            }
            // no lobe passes: the spare cord lies as one broad loop at the middle of the free stretch (the bar's own loop, not a bend)
            foreach (double at in LoopAt)
            {
            int im = ia;
            double sMid = cum[ia] + (cum[ib] - cum[ia]) * at;
            while (im < ib && cum[im] < sMid) im++;
            V2 tan = (P[Math.Min(n - 1, im + 1)] - P[Math.Max(0, im - 1)]).Norm();
            foreach (double rad in LoopRadii)
                foreach (int sg in new[] { s0, -s0 })
                {
                    if (audits >= MaxAudits + LoopAt.Length * 2) break;
                    List<V2> loop = CordLayer.Loop(P[im], tan, tan.Perp, rad, sg);
                    string bad = Ground(loop, 0, loop.Count);
                    if (bad != null) { no.Add("loop " + bad); continue; }
                    // the loop ends a little on along the cord: rejoin it there
                    V2 tip = loop[loop.Count - 1];
                    int jn = im + 1;
                    while (jn < n - 1 && Dot(P[jn] - tip, tan) < 0) jn++;
                    var Q = new List<V2>(n + loop.Count);
                    for (int i = 0; i < im; i++) Q.Add(P[i]);
                    Q.AddRange(loop);
                    for (int i = jn; i < n; i++) Q.Add(P[i]);
                    List<V2> ok = Accept(Q, "loop");
                    if (ok != null) return ok;
                }
            }
            Why?.Invoke(endA + "|" + endB + $" ha {ha * 180 / Math.PI:0} hb {hb * 180 / Math.PI:0} W {W:0.00} keep {keep:0.00} chord {chordAll:0.00}: " + string.Join("; ", no));
            return null;
        }

        /// <summary>The farthest any point strays off the strand's endpoint chord, cells.</summary>
        internal static double Excursion(List<V2> p)
        {
            V2 a = p[0], d = p[p.Count - 1] - a;
            double L = d.Len, m = 0;
            if (L < 1e-9) return 0;
            foreach (V2 q in p) m = Math.Max(m, Math.Abs((q.X - a.X) * d.Z - (q.Z - a.Z) * d.X) / L);
            return m;
        }

        /// <summary>A strand with a bend the bar counts (CordShapeAudit "unforced") eased: the cord round the bend, a window of <see cref="UnbendWindows"/> either side,
        /// is laid again as three arcs between the window's two ends (their points and headings kept), about its old length, so the turn the bend made is spread
        /// over the whole window. The ends' pins, a whip tail and a tied loop never move; a window that would put cord off clear floor or onto another fitting,
        /// add a corner, or leave the strand under a slack bar it met is not taken. Null when there is no such bend or none can be eased.</summary>
        internal static List<V2> Unbend(CordWorld w, List<V2> P, double pinA, double pinB, string endA, string endB, Func<V2, bool> clear,
                                        List<CordTie> ties, int whipA, int whipB)
        {
            if (Off || P == null || P.Count < 5) return null;
            int Counted(List<V2> q, out double at)
            {
                int k = 0;
                at = -1;
                foreach (CordShapeAudit.Bend b in CordShapeAudit.Bends(q, ties))
                    if (CordShapeAudit.Why(w, endA, endB, q, b) == "unforced") { if (k == 0) at = b.S; k++; }
                return k;
            }
            int count = Counted(P, out double S);
            if (count == 0) return null;
            double ratio0 = Ratio(P);
            int kOld = CordShapeAudit.Corners(P).Count;
            var no = new List<string>();
            int audits = 0;
            List<V2> cur = P;
            for (int round = 0; round < 4 && count > 0; round++)
            {
                List<V2> best = null;
                int bestCount = count;
                int n = cur.Count;
                double[] cum = Geo.CumLen(cur);
                double L = cum[n - 1];
                // the stretch the window may not reach into: pins, whip tails, ties, cord under walls or art
                double lo = pinA, hi = L - pinB;
                if (whipA > 0) lo = Math.Max(lo, cum[Math.Min(n - 1, whipA)]);
                if (whipB > 0) hi = Math.Min(hi, cum[Math.Max(0, n - 1 - whipB)]);
                for (int i = 0; i < n && !Open(w, cur[i]); i++) lo = Math.Max(lo, cum[i] + pinA);
                for (int i = n - 1; i >= 0 && !Open(w, cur[i]); i--) hi = Math.Min(hi, cum[i] - pinB);
                var tieSpans = new List<(double, double)>();
                if (ties != null) foreach (CordTie t in ties) tieSpans.Add((t.S0 - 0.1, t.S1 + 0.1));
                foreach ((double before, double after) in UnbendWindows)
                {
                    double s0 = Math.Max(lo, S - before), s1 = Math.Min(hi, S + after);
                    foreach ((double t0, double t1) in tieSpans)
                    {
                        if (t1 <= S && t1 > s0) s0 = t1;
                        if (t0 >= S && t0 < s1) s1 = t0;
                    }
                    int ia = 1, ib = n - 2;
                    while (ia < n - 2 && cum[ia] < s0) ia++;
                    while (ib > 1 && cum[ib] > s1) ib--;
                    if (ib - ia < 3) { no.Add("room"); continue; }
                    V2 m0 = cur[ia], m1 = cur[ib], d = m1 - m0;
                    double W = d.Len;
                    if (W < 0.2) { no.Add("short"); continue; }
                    double ang = Math.Atan2(d.Z, d.X);
                    double ha = Wrap(Heading(cur[ia] - cur[ia - 1]) - ang), hb = Wrap(Heading(cur[ib + 1] - cur[ib]) - ang);
                    double Lw = cum[ib] - cum[ia];
                    foreach (double grow in UnbendGrow)
                    {
                        double Lm = Math.Max(Lw * grow, W * 1.01);
                        foreach (double r in UnbendShoulders)
                            foreach (int sg in new[] { 1, -1 })
                            {
                                if (!Solve(ha, hb, Lm, W, sg, r, out double tA, out double tB)) { no.Add("solve"); continue; }
                                List<V2> mid = Lobe(ha, hb, tA, tB, r, Lm, W, ang, m0, m1);
                                bool ok = true;
                                foreach (V2 q in mid)
                                    if (!Open(w, q) || (clear != null && !clear(q))) { ok = false; break; }
                                if (!ok) { no.Add("ground"); continue; }
                                if (++audits > MaxAudits) goto spent;
                                var Q = new List<V2>(n + mid.Count);
                                for (int i = 0; i <= ia; i++) Q.Add(cur[i]);
                                for (int i = 1; i < mid.Count - 1; i++) Q.Add(mid[i]);
                                for (int i = ib; i < n; i++) Q.Add(cur[i]);
                                int c = Counted(Q, out _);
                                if (c >= bestCount) { no.Add("bends " + c); continue; }
                                if (CordShapeAudit.Corners(Q).Count > kOld) { no.Add("corners"); continue; }
                                if (ratio0 >= Bar && Ratio(Q) < Bar) { no.Add("ratio"); continue; }
                                best = Q; bestCount = c;
                                if (ties != null && Math.Abs(Geo.Length(Q) - L) > 1e-9)
                                {
                                    double dl = Geo.Length(Q) - L;
                                    for (int i = 0; i < ties.Count; i++) { CordTie t = ties[i]; if (t.S0 >= cum[ib]) { t.S0 += dl; t.S1 += dl; ties[i] = t; } }
                                }
                                goto taken;
                            }
                    }
                }
                taken:
                if (best == null) break;
                cur = best;
                count = Counted(cur, out S);
            }
            spent:
            if (count > 0)
            {
                var tally = new Dictionary<string, int>();
                foreach (string x in no) tally[x] = tally.TryGetValue(x, out int k) ? k + 1 : 1;
                Why?.Invoke(endA + "|" + endB + " unbend: still " + count + " at s " + S.ToString("0.00") + "; " + string.Join(" ", tally.Select(kv => kv.Key + ":" + kv.Value)));
                return null;
            }
            return cur;
        }

        /// <summary><see cref="Unbend"/>'s windows (cells of cord before and after the bend), its lengths (shares of the window's old length) and its shoulders.</summary>
        private static readonly (double, double)[] UnbendWindows = { (0.8, 0.8), (1.2, 1.2), (0.5, 1.5), (1.5, 0.5), (1.8, 1.8), (0.3, 2.2), (2.2, 0.3), (2.5, 2.5) };
        private static readonly double[] UnbendGrow = { 1.0, 1.08 };
        private static readonly double[] UnbendShoulders = { 0.3, 0.2 };
        /// <summary>The most candidates one strand's slackening or easing may lay and audit: an edge is laid whole inside one frame's budget (the slice gate's
        /// 30 ms bound), so a strand that cannot be eased gives up after this many, by count, never by clock (a build stays bit-identical).</summary>
        private const int MaxAudits = 30;

        /// <summary>Open floor a cord may be laid again on: walkable, no furniture, inside no machine's footprint.</summary>
        private static bool Open(CordWorld w, V2 q)
        {
            if (!w.IsWalkable(q.Floor) || w.IsFurniture(q.Floor)) return false;
            foreach (MachineInfo m in w.Machines) if (m.Contains(q.Floor)) return false;
            return true;
        }

        private static double Dot(V2 a, V2 b) => a.X * b.X + a.Z * b.Z;
        private static double Heading(V2 v) => Math.Atan2(v.Z, v.X);
        private static double Wrap(double a) { while (a > Math.PI) a -= 2 * Math.PI; while (a < -Math.PI) a += 2 * Math.PI; return a; }

        /// <summary>Heading at u along the lobe, relative to its chord: three arcs. Over the first share <paramref name="r"/> it turns from the head's way
        /// <paramref name="ha"/> to <paramref name="tA"/>, then sweeps at an even rate to <paramref name="tB"/>, then turns into the tail's way <paramref name="hb"/>.</summary>
        private static double H(double u, double ha, double hb, double tA, double tB, double r) =>
            u < r ? ha + (tA - ha) * u / r
            : u > 1 - r ? tB + (hb - tB) * (u - (1 - r)) / r
            : tA + (tB - tA) * (u - r) / (1 - 2 * r);

        private static void End(double ha, double hb, double tA, double tB, double r, double Lm, out double x, out double z)
        {
            int k = Math.Max(8, (int)Math.Ceiling(Lm / Step));
            double ds = Lm / k;
            x = 0; z = 0;
            for (int i = 0; i < k; i++)
            {
                double h = H((i + 0.5) / k, ha, hb, tA, tB, r);
                x += Math.Cos(h) * ds; z += Math.Sin(h) * ds;
            }
        }

        /// <summary>The two swing headings that bring a lobe of length <paramref name="Lm"/> from the head's point to the tail's, <paramref name="W"/> along its chord
        /// (Newton, two unknowns), swung first to side <paramref name="sg"/>.</summary>
        private static bool Solve(double ha, double hb, double Lm, double W, int sg, double r, out double tA, out double tB)
        {
            double t0 = Math.Acos(Math.Max(-1, Math.Min(1, W / Lm))) * 1.6;
            tA = sg * t0; tB = -sg * t0;
            for (int it = 0; it < 60; it++)
            {
                End(ha, hb, tA, tB, r, Lm, out double fx, out double fz);
                fx -= W;
                if (Math.Abs(fx) < 1e-4 && Math.Abs(fz) < 1e-4) return Math.Sign(tA - tB) == sg && Math.Abs(tA) <= MaxSwing && Math.Abs(tB) <= MaxSwing;
                const double e = 1e-5;
                End(ha, hb, tA + e, tB, r, Lm, out double ax, out double az);
                End(ha, hb, tA, tB + e, r, Lm, out double bx, out double bz);
                double j11 = (ax - W - fx) / e, j21 = (az - fz) / e, j12 = (bx - W - fx) / e, j22 = (bz - fz) / e;
                double det = j11 * j22 - j12 * j21;
                if (Math.Abs(det) < 1e-12) return false;
                double da = (-fx * j22 + fz * j12) / det, db = (-j11 * fz + j21 * fx) / det;
                double big = Math.Max(Math.Abs(da), Math.Abs(db));
                if (big > 0.3) { da *= 0.3 / big; db *= 0.3 / big; }
                tA += da; tB += db;
            }
            return false;
        }

        /// <summary>The lobe's points on the map, from <paramref name="m0"/> to <paramref name="m1"/> exactly (the solver's last ten-thousandth spread along it).</summary>
        private static List<V2> Lobe(double ha, double hb, double tA, double tB, double r, double Lm, double W, double ang, V2 m0, V2 m1)
        {
            int k = Math.Max(8, (int)Math.Ceiling(Lm / Step));
            double ds = Lm / k, x = 0, z = 0, co = Math.Cos(ang), si = Math.Sin(ang);
            var local = new List<V2>(k + 1) { new V2(0, 0) };
            for (int i = 0; i < k; i++)
            {
                double h = H((i + 0.5) / k, ha, hb, tA, tB, r);
                x += Math.Cos(h) * ds; z += Math.Sin(h) * ds;
                local.Add(new V2(x, z));
            }
            V2 err = new V2(W, 0) - local[k];
            var o = new List<V2>(k + 1);
            for (int i = 0; i <= k; i++)
            {
                V2 q = local[i] + err * ((double)i / k);
                o.Add(m0 + new V2(q.X * co - q.Z * si, q.X * si + q.Z * co));
            }
            o[0] = m0; o[k] = m1;
            return o;
        }
    }
}
