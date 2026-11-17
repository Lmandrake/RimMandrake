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
        /// <summary>A varied short lead's lobe length, as a multiple of its chord (cords_never_repeat).</summary>
        public const double VaryLo = 1.55, VaryHi = 2.4;
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
                                         Func<V2, bool> clear, List<CordTie> ties, int side, int whipA = 0, int whipB = 0, List<V2> line = null, CordRng vary = null,
                                         CordRng jitter = null, int maxAudits = MaxAudits, List<CordTie> tieInto = null)
        {
            if (Off || P == null || P.Count < 3) return null;
            int n = P.Count;
            double chordAll = V2.Dist(P[0], P[n - 1]);
            if (chordAll < MinChord) return null;
            double[] cum = Geo.CumLen(P);
            double L = cum[n - 1];
            // the stray bar reads the conduit line (the polyline through the edge's chain, when the caller has one), not the strand's own chord
            bool longEdge = line != null ? LineLength(line) > LongChord : chordAll > LongChord;
            double Stray(List<V2> q) => line != null ? Excursion(q, line) : Excursion(q);
            bool flat = longEdge && Stray(P) < MinExcursion + 0.05;
            if (L / chordAll >= Bar + 0.02 && !flat && vary == null) return null;
            bool Free(V2 q) => Open(w, q);
            // each end: past its run under a wall or art, past its tied loop, then its pin
            double headStart = 0, tailStart = 0;
            for (int i = 0; i < n && !Free(P[i]); i++) headStart = cum[i];
            for (int i = n - 1; i >= 0 && !Free(P[i]); i--) tailStart = L - cum[i];
            double hs = headStart + pinA, ts = tailStart + pinB;
            // a live cut end's writhing tail (its last whip points) never moves: the lobe starts past it
            if (whipA > 0) hs = Math.Max(hs, cum[Math.Min(n - 1, whipA)] + 0.15);
            if (whipB > 0) ts = Math.Max(ts, L - cum[Math.Max(0, n - 1 - whipB)] + 0.15);
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
                if (longEdge && Stray(Q) < MinExcursion) { no.Add(tag + " flat " + Stray(Q).ToString("0.00")); return null; }
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
            // vary (cords_never_repeat): a short lead's lobe is drawn from the edge's own stream, its length and its two shoulders, so two equal runs
            // side by side lay two shapes (blind cycle 1: 4-cell runs settled to one curve, mean gap 0.01 cell)
            // jitter: any slackened lead tries a lobe from its own stream first, the fixed lengths after (two equal leads slackened alike were twins, gap 0)
            // jitter: the same candidates, the first length and the shoulders' order drawn from the edge's own stream (two equal leads slackened alike were
            // twins, gap 0); no candidate is added, so the slackening costs what it did
            double first = jitter != null ? jitter.Range(Aim - 0.03, Aim + 0.25) : Aim;
            double[] targets = vary != null ? new[] { vary.Range(VaryLo, VaryHi), vary.Range(VaryLo, VaryHi), Aim }
                : flat ? new[] { first, Aim + 0.15, Aim + 0.3 } : new[] { first, Settle, Bar + 0.02 };
            var shoulders = new List<(double, double)>();
            if (vary != null) { double ra = vary.Range(0.08, 0.34), rb = vary.Range(0.08, 0.34); shoulders.Add((ra, rb)); shoulders.Add((rb, ra)); }
            int rot = jitter != null ? jitter.Int(0, Shoulders.Length - 1) : 0;
            for (int k = 0; k < Shoulders.Length; k++) { double r = Shoulders[(k + rot) % Shoulders.Length]; shoulders.Add((r, r)); }
            foreach (double target in lobes ? targets : new double[0])
            {
                double Lm = target * chordAll - keep;
                if (Lm <= W * 1.03) { no.Add("ends-hold-length"); continue; }
                foreach ((double r, double rb) in shoulders)
                    foreach (int sg in new[] { s0, -s0 })
                    {
                        if (audits >= maxAudits) break;
                        if (!Solve(ha, hb, Lm, W, sg, r, out double tA, out double tB, rb)) { no.Add("solve"); continue; }
                        List<V2> mid = Lobe(ha, hb, tA, tB, r, Lm, W, ang, m0, m1, rb);
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
            // no lobe passes: the spare cord lies as one broad loop at the middle of the free stretch (the bar's own loop, not a bend); a varied lead keeps its lay
            if (vary != null) return null;
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
            // neither a lobe nor a broad loop lies between the pins (a lead whose fittings hold most of it: a box arm a cell from a machine's
            // seated plug): the spare cord is the owner's wire-tied loop (2026-11-08, "a tight wire-tied strain-relief LOOP"), an emergency device,
            // tried only here, after every bare lay has failed (RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN: the seated plug and the
            // 1.4 slack bar could not both hold on such a lead). The bars leave a tied loop's own arc out, as they do at a strip's plugs
            if (tieInto != null)
                foreach (double at in LoopAt)
                {
                    int im = ia;
                    double sMid = cum[ia] + (cum[ib] - cum[ia]) * at;
                    while (im < ib && cum[im] < sMid) im++;
                    V2 tan = (P[Math.Min(n - 1, im + 1)] - P[Math.Max(0, im - 1)]).Norm();
                    foreach (double rad in CordLiveEnd.LoopR)
                        foreach (int sg in new[] { s0, -s0 })
                        {
                            List<V2> loop = CordLayer.Loop(P[im], tan, tan.Perp, rad, sg);
                            string bad = Ground(loop, 0, loop.Count);
                            if (bad != null) { no.Add("tied loop " + bad); continue; }
                            V2 tip = loop[loop.Count - 1];
                            int jn = im + 1;
                            while (jn < n - 1 && Dot(P[jn] - tip, tan) < 0) jn++;
                            // the loop comes back onto the cord before the far end's own run, and where it lands: a loop a quarter cell
                            // from a wall plate landed inside the plate's run and was joined to the cord's last points by a jump across
                            // it (46 degrees off the plate, twice on the owner's review map)
                            if (jn > ib || V2.Dist(tip, P[jn]) > 0.1) { no.Add("tied loop lands in the far pin"); continue; }
                            var Q = new List<V2>(n + loop.Count);
                            for (int i = 0; i < im; i++) Q.Add(P[i]);
                            Q.AddRange(loop);
                            for (int i = jn; i < n; i++) Q.Add(P[i]);
                            if (Ratio(Q) < Bar) { no.Add("tied loop ratio " + Ratio(Q).ToString("0.00")); continue; }
                            double a0 = im > 0 ? Geo.Length(Q.GetRange(0, im + 1)) : 0;
                            // the band sits where the loop comes back over its own start (CordLayer.Loop lands 0.25 on along the cord)
                            var tie = new CordTie { S0 = a0, S1 = a0 + Geo.Length(loop), At = P[im] + tan * 0.12 + tan.Perp * (sg * 0.03), Angle = Heading(tan) + Math.PI / 2 };
                            var all = new List<CordTie>();
                            double grow = Geo.Length(Q) - L;
                            if (ties != null) foreach (CordTie t0 in ties) { CordTie t = t0; if (t.S0 + t.S1 >= L) { t.S0 += grow; t.S1 += grow; } all.Add(t); }
                            all.Add(tie);
                            int uNew = 0;
                            foreach (CordShapeAudit.Bend b in CordShapeAudit.Bends(Q, all)) if (CordShapeAudit.Why(w, endA, endB, Q, b) == "unforced") uNew++;
                            if (uNew > uOld || CordShapeAudit.Corners(Q, 0.05, all).Count > kOld) { no.Add("tied loop bends"); continue; }
                            if (ties != null) for (int i = 0; i < ties.Count; i++) ties[i] = all[i];
                            tieInto.Add(tie);
                            return Q;
                        }
                }
            Why?.Invoke(endA + "|" + endB + $" ha {ha * 180 / Math.PI:0} hb {hb * 180 / Math.PI:0} W {W:0.00} keep {keep:0.00} chord {chordAll:0.00}: " + string.Join("; ", no));
            return null;
        }

        /// <summary>A short lead's own broad loop (cords_never_repeat): one loop of the bend bar's own kind (<see cref="VaryLoopR0"/> or wider), laid at a
        /// point drawn from the edge's stream between the pins, on either side. A lobe alone leaves a short lead one free shape, its length, so two equal runs drew
        /// twins by chance; where the loop lies along the cord parts them. Kept only on clear floor, off every other fitting, with no new bend or corner the bars
        /// count; null when the draw skips the loop or none passes.</summary>
        internal static List<V2> VaryLoop(CordWorld w, List<V2> P, double pinA, double pinB, string endA, string endB, Func<V2, bool> clear, List<CordTie> ties, CordRng r,
                                          double chance, double maxLen)
        {
            if (Off || P == null || P.Count < 12 || r.Value() >= chance) return null;
            double[] cum = Geo.CumLen(P);
            double L = cum[cum.Length - 1];
            double at0 = r.Range(0.25, 0.75) * L, rad = r.Range(VaryLoopR0, VaryLoopR1);
            int first = r.Sign();
            if (L + 2 * Math.PI * rad > maxLen) return null;
            int uOld = CordShapeAudit.Unforced(w, endA, endB, P), kOld = CordShapeAudit.Corners(P).Count, audits = 0;
            // the loop goes in where the cord runs straight for a stretch either side: on a curving stretch its joins kink (a loop's own turn plus the cord's)
            foreach (double shift in VaryLoopShifts)
            {
            double at = at0 + shift * L;
            if (at < pinA + VaryLoopKeep || at > L - pinB - VaryLoopKeep) continue;
            int j = Array.BinarySearch(cum, at);
            if (j < 0) j = ~j;
            j = Math.Max(3, Math.Min(j, P.Count - 4));
            if (CordShapeAudit.InTie(ties, cum[j])) continue;
            V2 tan = (P[j + 1] - P[j - 1]).Norm();
            int jb = j, je = j;
            while (jb > 0 && cum[j] - cum[jb] < VaryLoopStraight) jb--;
            while (je < P.Count - 1 && cum[je] - cum[j] < VaryLoopStraight + 0.3) je++;
            V2 inDir = P[j] - P[jb], outDir = P[je] - P[j];
            if (inDir.Len < 1e-6 || outDir.Len < 1e-6 || Dot(inDir.Norm(), tan) < VaryLoopCos || Dot(outDir.Norm(), tan) < VaryLoopCos) continue;
            foreach (int sg in new[] { first, -first })
            {
                List<V2> loop = CordLayer.Loop(P[j], tan, tan.Perp, rad, sg);
                bool ok = true;
                foreach (V2 q in loop) if (!Open(w, q) || (clear != null && !clear(q))) { ok = false; break; }
                if (!ok) continue;
                V2 tip = loop[loop.Count - 1];
                int jn = j + 1;
                while (jn < P.Count - 1 && Dot(P[jn] - tip, tan) < 0) jn++;
                var Q = new List<V2>(P.Count + loop.Count);
                for (int i = 0; i < j; i++) Q.Add(P[i]);
                Q.AddRange(loop);
                for (int i = jn; i < P.Count; i++) Q.Add(P[i]);
                if (++audits > VaryLoopAudits) return null;
                if (Geo.Length(Q) > maxLen || CordShapeAudit.Unforced(w, endA, endB, Q) > uOld || CordShapeAudit.Corners(Q).Count > kOld || Ratio(Q) < Bar) continue;
                if (ties != null)
                {
                    double grow = Geo.Length(Q) - L;
                    for (int i = 0; i < ties.Count; i++) { CordTie tt = ties[i]; if (tt.S0 >= cum[j]) { tt.S0 += grow; tt.S1 += grow; ties[i] = tt; } }
                }
                return Q;
            }
            }
            return null;
        }

        /// <summary><see cref="VaryLoop"/>'s place: the drawn point and then shares of the cord either side of it; the stretch either side that must run within
        /// acos(<see cref="VaryLoopCos"/>) of the loop's own heading (cells).</summary>
        private static readonly double[] VaryLoopShifts = { 0, 0.1, -0.1 };
        /// <summary>The most loops <see cref="VaryLoop"/> lays and audits for one strand (it runs on every short lead, inside a frame's lay budget).</summary>
        private const int VaryLoopAudits = 4;
        /// <summary>The most a varied lead's lobe lays and audits (<see cref="Slacken"/>'s vary, on every short lead).</summary>
        public const int VaryAudits = 6;
        private const double VaryLoopStraight = 0.5, VaryLoopCos = 0.85;
        /// <summary>How far past each end's pin a <see cref="VaryLoop"/> keeps (cells): a strip socket's last 1.2 cells read any turn past 100 degrees as a hook.</summary>
        private const double VaryLoopKeep = 1.3;
        /// <summary><see cref="VaryLoop"/>'s radii (cells): 0.58 turns 99 degrees a cell, leaving room under a broad loop's 127 (radius 0.45) for the cord's own curve at its joins.</summary>
        private const double VaryLoopR0 = 0.58, VaryLoopR1 = 0.7;

        /// <summary>The share of short leads that take their own loop (<see cref="VaryLoop"/>).</summary>
        public const double VaryLoopP = 0.9, VaryLoop2P = 0.5;

        /// <summary>The farthest any point strays off a polyline (the edge's conduit line through its chain's cell centres), cells.</summary>
        internal static double Excursion(List<V2> p, List<V2> line)
        {
            if (line == null || line.Count == 0) return Excursion(p);
            double m = 0;
            foreach (V2 q in p)
            {
                double best = double.MaxValue;
                if (line.Count == 1) best = V2.Dist(q, line[0]);
                for (int i = 1; i < line.Count; i++)
                {
                    V2 a = line[i - 1], ab = line[i] - a;
                    double L2 = ab.X * ab.X + ab.Z * ab.Z;
                    double t = L2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, ((q.X - a.X) * ab.X + (q.Z - a.Z) * ab.Z) / L2));
                    best = Math.Min(best, V2.Dist(q, a + ab * t));
                }
                m = Math.Max(m, best);
            }
            return m;
        }

        /// <summary>A polyline's length, cells.</summary>
        internal static double LineLength(List<V2> line)
        {
            double s = 0;
            for (int i = 1; i < line.Count; i++) s += V2.Dist(line[i - 1], line[i]);
            return s;
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
                                        List<CordTie> ties, int whipA, int whipB, bool tipA = false, bool tipB = false)
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
                // a fitting's hook inside its pin (tipA/tipB: a junction arm, a plate, a pile port, never a cut end or a plug): the window may start at the
                // fitting's tip, leaving it at the fitting's own heading (blind cycle 1: a cut lead's junction end hooked 0.1 cell out of the arm, 48 times in 80 scenes)
                double loTip = 0, hiTip = L;
                for (int i = 0; i < n && !Open(w, cur[i]); i++) { lo = Math.Max(lo, cum[i] + pinA); loTip = Math.Max(loTip, cum[Math.Min(n - 1, i + 1)]); }
                for (int i = n - 1; i >= 0 && !Open(w, cur[i]); i--) { hi = Math.Min(hi, cum[i] - pinB); hiTip = Math.Min(hiTip, cum[Math.Max(0, i - 1)]); }
                if (tipA && S - lo < TipReach && whipA == 0) lo = loTip;
                if (tipB && hi - S < TipReach && whipB == 0) hi = hiTip;
                var tieSpans = new List<(double, double)>();
                if (ties != null) foreach (CordTie t in ties) tieSpans.Add((t.S0 - 0.1, t.S1 + 0.1));
                // every window's Dubins re-lay first, on its own budget, then the lobes: the lobes' audits spent on the narrow windows left a heap cable's
                // hook by its port with no wide window tried (blind cycle 1)
                int auditsD = 0;
                for (int kind = 0; kind < 2; kind++)
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
                    // first a Dubins re-lay at a radius the bar cannot read as a bend (1/r under 90 degrees a cell): it bounds every turn inside the window,
                    // where the three-arc lobe's even sweep cannot make an S or come back past its own head (blind cycle 1's residue: S-hooks between two
                    // arms a cell apart, near-loops of 235 degrees over 2.4 cells); never a ring where there was none
                    double turnCap = Math.Max(DubinsTurnMin, CordShapeAudit.TotalTurn(cur, ia, ib) + DubinsTurnSpare);
                    double hda = Heading(cur[ia] - cur[ia - 1]), hdb = Heading(cur[ib + 1] - cur[ib]);
                    if (kind == 0)
                    foreach (double rad in DubinsRadii)
                        foreach (CordShape.Dubins.Path dp in CordShape.Dubins.All(m0, hda, m1, hdb, rad))
                        {
                            if (dp.Turning > turnCap || dp.Len > Lw + 3.0) { no.Add("dubins turn/len"); continue; }
                            List<V2> arc = CordShape.Dubins.Sample(m0, hda, dp, Step);
                            if (arc.Count < 2) continue;
                            bool okd = true;
                            foreach (V2 q in arc)
                                if (!Open(w, q) || (clear != null && !clear(q))) { okd = false; break; }
                            if (!okd) { no.Add("dubins ground"); continue; }
                            if (++auditsD > MaxAudits) break;
                            var Qd = new List<V2>(n + arc.Count);
                            for (int i = 0; i < ia; i++) Qd.Add(cur[i]);
                            Qd.AddRange(arc);
                            for (int i = ib + 1; i < n; i++) Qd.Add(cur[i]);
                            int cd = Counted(Qd, out _);
                            if (cd >= bestCount) { no.Add("dubins bends " + cd); continue; }
                            if (CordShapeAudit.Corners(Qd).Count > kOld) { no.Add("dubins corners"); continue; }
                            if (ratio0 >= Bar && Ratio(Qd) < Bar) { no.Add("dubins ratio"); continue; }
                            best = Qd; bestCount = cd;
                            if (ties != null && Math.Abs(Geo.Length(Qd) - L) > 1e-9)
                            {
                                double dl = Geo.Length(Qd) - L;
                                for (int i = 0; i < ties.Count; i++) { CordTie tt = ties[i]; if (tt.S0 >= cum[ib]) { tt.S0 += dl; tt.S1 += dl; ties[i] = tt; } }
                            }
                            goto taken;
                        }
                    if (kind == 1)
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

        /// <summary><see cref="Unbend"/>'s Dubins radii (cells; 0.72 turns 80 degrees a cell, under the bar's 90) and its turn cap: no more than the window
        /// turned plus <see cref="DubinsTurnSpare"/>, and always a round U (<see cref="DubinsTurnMin"/>), as SmoothBends caps it.</summary>
        private static readonly double[] DubinsRadii = { 0.72, 0.85, 1.0 };
        private const double DubinsTurnMin = 1.3 * Math.PI, DubinsTurnSpare = 0.45 * Math.PI;

        /// <summary>How near its fitting's pin a bend lies for <see cref="Unbend"/> to lay its window again from the fitting's tip, cells.</summary>
        private const double TipReach = 0.6;

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
        private static double H(double u, double ha, double hb, double tA, double tB, double r, double rB = -1)
        {
            double b = rB < 0 ? r : rB;
            return u < r ? ha + (tA - ha) * u / r
                : u > 1 - b ? tB + (hb - tB) * (u - (1 - b)) / b
                : tA + (tB - tA) * (u - r) / (1 - r - b);
        }

        private static void End(double ha, double hb, double tA, double tB, double r, double Lm, out double x, out double z, double rB = -1)
        {
            int k = Math.Max(8, (int)Math.Ceiling(Lm / Step));
            double ds = Lm / k;
            x = 0; z = 0;
            for (int i = 0; i < k; i++)
            {
                double h = H((i + 0.5) / k, ha, hb, tA, tB, r, rB);
                x += Math.Cos(h) * ds; z += Math.Sin(h) * ds;
            }
        }

        /// <summary>The two swing headings that bring a lobe of length <paramref name="Lm"/> from the head's point to the tail's, <paramref name="W"/> along its chord
        /// (Newton, two unknowns), swung first to side <paramref name="sg"/>.</summary>
        private static bool Solve(double ha, double hb, double Lm, double W, int sg, double r, out double tA, out double tB, double rB = -1)
        {
            double t0 = Math.Acos(Math.Max(-1, Math.Min(1, W / Lm))) * 1.6;
            tA = sg * t0; tB = -sg * t0;
            for (int it = 0; it < 60; it++)
            {
                End(ha, hb, tA, tB, r, Lm, out double fx, out double fz, rB);
                fx -= W;
                if (Math.Abs(fx) < 1e-4 && Math.Abs(fz) < 1e-4) return Math.Sign(tA - tB) == sg && Math.Abs(tA) <= MaxSwing && Math.Abs(tB) <= MaxSwing;
                const double e = 1e-5;
                End(ha, hb, tA + e, tB, r, Lm, out double ax, out double az, rB);
                End(ha, hb, tA, tB + e, r, Lm, out double bx, out double bz, rB);
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
        private static List<V2> Lobe(double ha, double hb, double tA, double tB, double r, double Lm, double W, double ang, V2 m0, V2 m1, double rB = -1)
        {
            int k = Math.Max(8, (int)Math.Ceiling(Lm / Step));
            double ds = Lm / k, x = 0, z = 0, co = Math.Cos(ang), si = Math.Sin(ang);
            var local = new List<V2>(k + 1) { new V2(0, 0) };
            for (int i = 0; i < k; i++)
            {
                double h = H((i + 0.5) / k, ha, hb, tA, tB, r, rB);
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
