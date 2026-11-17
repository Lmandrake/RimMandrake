// RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN: the live cut end swept over the worlds the game can make near one, as a permanent check.
// The suite's 36 whipping tails read green while 3,935 of 30,768 live ends over the wider space failed a bar; this check is that wider space
// (LiveEndCensus.Family, thinned to every region once) read by the three bars' own instruments, with the margins the lay is built to:
//   every live end holds the straight bar, the whip bar and the pinch bar (three whip seeds a tail);
//   no bend in the pinch window is under MarginR on any frame (1.5 x the bar: a result back at 0.101 against 0.10 is a failure here);
//   the lay never gives up (Kind.None), and an end with room for a tail whips (the owner's "a2, and where it does not apply then c");
//   the tied loop is a device: it is used nowhere on these worlds (zero is the measured reading; a use is a question, asked here);
//   and the instrument can fail: the cords as handed to the lay fail by the hundred, and the old whip pinches a straight cord.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class LiveEndSweepChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "live end sweep: " + msg);

        /// <summary>The margin the pinch bar is held with over the sweep: 1.5 x StubJoins.MinBendR (the lay builds to 2 x, a tied loop is 1.7 x).</summary>
        public const double MarginR = 1.5 * StubJoins.MinBendR;

        /// <summary>The whip before the bend wave (each point pushed sideways by amp u^4 f): kept here only so the check can show its instrument
        /// catches it.</summary>
        private static List<V2> OldWhip(IList<V2> tail, double t, ulong seed, double amp)
        {
            // the new whip's own wave, read back off a straight unit tail, then applied the old way
            int n = tail.Count;
            var o = new List<V2>(n);
            double H(int k) { ulong z = unchecked((seed ^ (ulong)(k * 0x9E3779B1L)) ^ 0x9E3779B97F4A7C15UL) + 0x9E3779B97F4A7C15UL; z = unchecked((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL); z = unchecked((z ^ (z >> 27)) * 0x94D049BB133111EBUL); z ^= z >> 31; return (z >> 11) * (1.0 / 9007199254740992.0); }
            double w1 = 5 + 3 * H(1), w2 = 11 + 5 * H(2), w3 = 2 + 1.5 * H(3), p1 = 6.283 * H(4), p2 = 6.283 * H(5), p3 = 6.283 * H(6);
            double since = -1, kick = 0, acc = H(7) * 2.0 - 2.0;
            for (int idx = 0; acc <= t && idx < 100000; idx++)
            {
                double len = 0.6 + 1.4 * H(1000 + idx);
                if (t < acc + len) { since = t - acc; kick = H(5000 + idx) < 0.5 ? -0.9 : 0.9; break; }
                acc += len;
            }
            for (int i = 0; i < n; i++)
            {
                double u = i / (double)(n - 1), lag = CordMotion.WhipLag * u, tu = t - lag;
                Geo.TanNorm(tail, i, out V2 tg, out V2 nrm);
                double wave = 0.5 * Math.Sin(w1 * tu + p1) + 0.25 * Math.Sin(w2 * tu + p2) + 0.15 * Math.Sin(w3 * tu + p3);
                double snap = since >= lag ? kick * (1 - Math.Exp(-(since - lag) / 0.035)) * Math.Exp(-(since - lag) / 0.15) : 0;
                o.Add(tail[i] + nrm * (amp * Math.Pow(u, 4) * Geo.Clamp(wave + snap, -1.9, 1.9)));
            }
            return o;
        }

        /// <summary>The tightest bend of a dead straight cord's whip over <paramref name="seeds"/> seeds and 20 seconds.</summary>
        private static double StraightWhipRadius(double tailLen, int seeds, bool old)
        {
            int cnt = (int)Math.Round(tailLen / 0.05) + 1;
            var lead = Enumerable.Range(0, 9).Select(k => new V2(k * 0.05, 0)).ToList();
            var tail = Enumerable.Range(0, cnt).Select(k => new V2(0.4 + k * 0.05, 0)).ToList();
            double best = double.MaxValue;
            for (int s = 0; s < seeds; s++)
            {
                ulong seed = unchecked((ulong)(s * 2654435761L + 17));
                for (int f = 0; f < 600; f++)
                {
                    List<V2> bent = old ? OldWhip(tail, f / 30.0, seed, CordMotion.WhipAmp) : CordMotion.Whip(tail, f / 30.0, seed, CordMotion.WhipAmp);
                    var whole = new List<V2>(lead);
                    whole.AddRange(bent.Skip(1));
                    best = Math.Min(best, StubJoins.MinRadius(whole));
                }
            }
            return best;
        }

        internal sealed class Tally
        {
            public int Worlds, Ends, Straight, Pinched, BadTail, None, Still, StillWithRoom, Devices, Thin, Kept, Joined, WholePigtail;
            public double MinR = double.MaxValue;
            public readonly List<string> Bad = new List<string>();
        }

        internal static Tally Sweep(IEnumerable<(string name, CordWorld w, BuildOptions opt, Func<Cell, bool> live)> worlds, bool layOff = false)
        {
            var t = new Tally();
            foreach (var x in worlds)
            {
                t.Worlds++;
                CordBuilder.LiveEndLayOff = layOff;
                List<LaidPiece> ps;
                var b = new CordBuilder();
                try { ps = b.Build(x.w, x.opt, c => x.live(c)); }
                finally { CordBuilder.LiveEndLayOff = false; }
                foreach (LiveEndCensus.End e in LiveEndCensus.Read(x.name, b.Graph, ps, x.live, null, new ulong[] { 0, 1, 5 }))
                {
                    t.Ends++;
                    string at = $"{x.name} {e.Cord} ({e.Len:0.00} of cord, {e.LayKind})";
                    if (e.NotStraight) { t.Straight++; t.Bad.Add($"{at}: not straight out of the conduit end (off {e.Off:0.00}, arrive {e.Arrive:0}, turn {e.Turn:0})"); }
                    if (e.Pinched) { t.Pinched++; t.Bad.Add($"{at}: pinched, radius {e.MinR:0.000}"); }
                    if (e.BadTail) { t.BadTail++; t.Bad.Add($"{at}: tail {e.Tail:0.00} outside 0.7-1.15"); }
                    if (layOff) continue;
                    if (e.Whip > 0) t.MinR = Math.Min(t.MinR, e.MinR);
                    // the owner's A2: on a short lead more than the outer half whips, right up to the fitting
                    if (e.Whip > 0 && e.Tail > e.Len * 0.5 + 0.01) t.WholePigtail++;
                    if (e.Whip > 0 && e.MinR < MarginR && !e.Pinched) { t.Thin++; t.Bad.Add($"{at}: holds the pinch bar by a thin margin, radius {e.MinR:0.000} under {MarginR:0.00}"); }
                    if (e.LayKind == "None")
                    {
                        t.None++;
                        t.Bad.Add($"{at}: the lay found nothing that holds");
                        if (Environment.GetEnvironmentVariable("GSS_LIVE_SWEEP_DUMP") == "1")
                            Console.WriteLine($"  DUMP {x.name} {e.Cord} pos ({e.Pos.X:0.00},{e.Pos.Z:0.00}) out ({e.Out.X:0},{e.Out.Z:0}): " + string.Join(" ", e.Pts.Select(q => $"({q.X:0.00},{q.Z:0.00})")));
                    }
                    if (e.LayKind == "Kept") t.Kept++;
                    if (e.LayKind.StartsWith("Join", StringComparison.Ordinal)) t.Joined++;
                    if (e.Device) { t.Devices++; t.Bad.Add($"{at}: a tied loop was used"); }
                    if (e.Whip == 0 && e.LayKind != "None")
                    {
                        t.Still++;
                        // "a2, and where it does not apply then c": only a cord with no room for the tail lies still
                        if (e.StillCouldWhip || !e.Still) { t.StillWithRoom++; t.Bad.Add($"{at}: lies still though a whipping tail holds the bars on it"); }
                    }
                }
            }
            return t;
        }

        public static void Run()
        {
            Tally t = Sweep(LiveEndCensus.Family(1, null, thin: true));
            Console.WriteLine($"  live end sweep: {t.Worlds} worlds, {t.Ends} live ends: {t.Kept} kept as handed, {t.Joined} joined, {t.WholePigtail} short pigtails whipping whole, {t.Still} lying still, {t.Devices} tied loops, {t.None} unlaid; "
                              + $"{t.Straight} not straight, {t.Pinched} pinched, {t.BadTail} tails off length; tightest bend {t.MinR:0.000}");
            foreach (string x in t.Bad.Take(8)) Console.WriteLine("  live end sweep refused: " + x);
            Check(t.Ends >= 1500, $"the sweep reads the family ({t.Worlds} worlds, {t.Ends} live ends)");
            Check(t.Straight == 0 && t.Pinched == 0 && t.BadTail == 0, $"every live end holds the three bars: {t.Straight} not straight, {t.Pinched} pinched, {t.BadTail} tails outside 0.7-1.15, of {t.Ends}");
            Check(t.Thin == 0 && t.MinR >= MarginR, $"the pinch bar holds with margin: tightest bend {t.MinR:0.000} (bar {StubJoins.MinBendR}, margin {MarginR:0.00}), {t.Thin} ends under the margin");
            Check(t.None == 0, $"the lay never gives up: {t.None} live ends left as handed");
            Check(t.StillWithRoom == 0, $"an end lies still only where no whipping tail holds the bars: {t.StillWithRoom} of {t.Still} still ends could whip");
            Check(t.Devices == 0, $"the tied loop is an emergency device: used on {t.Devices} live ends of the swept family (measured 0; a use here is a region the bare cord lost)");

            // the whip alone, on a dead straight cord, over 60 seeds and 20 seconds at each end of the whip bar
            double shortTail = StraightWhipRadius(0.7, 60, false), longTail = StraightWhipRadius(0.95, 60, false);
            Check(shortTail >= CordMotion.WhipBendR && longTail >= CordMotion.WhipBendR,
                  $"the whip never bends a straight cord under {CordMotion.WhipBendR}: tail 0.7 {shortTail:0.000}, tail 0.95 {longTail:0.000} (60 seeds x 20 s)");

            // ---- the check can fail
            Tally raw = Sweep(LiveEndCensus.Family(1, null, thin: true).Where((x, i) => i % 6 == 0), layOff: true);
            double oldShort = StraightWhipRadius(0.7, 60, true);
            Check(raw.Pinched >= 20 && oldShort < StubJoins.MinBendR,
                  $"can fail: the cords as handed to the lay pinch on {raw.Pinched} of {raw.Ends} live ends, and the old sideways whip folds a straight 0.7 tail to {oldShort:0.000} (under {StubJoins.MinBendR})");
        }
    }
}
