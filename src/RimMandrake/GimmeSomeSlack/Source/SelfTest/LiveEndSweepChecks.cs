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

        /// <summary>How near a box's, plate's or strip's middle may stand to a cut end's run, off the run's line: between the abstract sweep's worst
        /// unlaid pose (0.749) and the grid's nearest (0.835). See the check that reads it.</summary>
        public const double BoxSepMin = 0.80;

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

        /// <summary>A conduit through a doorway that ends one, two or three cells past it, cut at both ends: the end's own line runs back through
        /// the door (CordShapeChecks' door room, nearer the door than it goes).</summary>
        private static IEnumerable<(string name, CordWorld w, BuildOptions opt, Func<Cell, bool> live)> PastADoor()
        {
            foreach (int d in new[] { 1, 2, 3 })
                foreach (ulong seed in new ulong[] { 1, 2, 3, 4 })
                {
                    var w = new CordWorld(50, 30);
                    for (int z = 4; z <= 26; z++) if (z != 15) w.SetBlocked(new Cell(20, z), BlockKind.Wall);
                    w.SetDoor(new Cell(20, 15));
                    for (int x = 12; x <= 20 + d; x++) w.SetConduit(new Cell(x, 15));
                    yield return ($"door room, end {d} past the door, seed {seed}", w, new BuildOptions { Seed = seed }, _ => true);
                }
            // the live proof's cut scene (validation.py M8): a battery's run through a door and across a room, a branch to a lamp, a spur into
            // the east wall; one cell of the run destroyed two cells before the door. West of the cut is live, east of it dead
            foreach (ulong seed in new ulong[] { 1, 2, 3, 4 })
                foreach (int gap in new[] { 7, 8, 5, 12 })
                {
                    var w = new CordWorld(40, 20);
                    for (int x = 10; x <= 18; x++) { w.SetBlocked(new Cell(x, 0), BlockKind.Wall); w.SetBlocked(new Cell(x, 6), BlockKind.Wall); }
                    for (int z = 0; z <= 6; z++) { if (z != 3) w.SetBlocked(new Cell(10, z), BlockKind.Wall); w.SetBlocked(new Cell(18, z), BlockKind.Wall); }
                    w.SetDoor(new Cell(10, 3));
                    for (int x = 3; x <= 17; x++) if (x != gap) w.SetConduit(new Cell(x, 3));
                    w.SetConduit(new Cell(13, 4)); w.SetConduit(new Cell(13, 5));
                    w.SetConduit(new Cell(17, 2)); w.SetConduit(new Cell(18, 2));
                    w.SetBlocked(new Cell(2, 3), BlockKind.Device); w.SetBlocked(new Cell(2, 4), BlockKind.Device);
                    w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = 2, Z0 = 3, W = 1, H = 2, Hookups = new List<Cell> { new Cell(3, 3) } });
                    w.SetBlocked(new Cell(12, 5), BlockKind.Device);
                    w.Machines.Add(new MachineInfo { Id = "lamp", Kind = MachineKind.Lamp, X0 = 12, Z0 = 5, Hookups = new List<Cell> { new Cell(13, 5) } });
                    yield return ($"cut scene, cell {gap} of the run destroyed, seed {seed}", w, new BuildOptions { Seed = seed }, c => c.X < gap && c.Z == 3);
                }
        }

        internal sealed class Tally
        {
            public int Worlds, Ends, Straight, Pinched, BadTail, None, Still, StillWithRoom, Devices, Thin, Kept, Joined, WholePigtail, Near, MachineOnRun, CutEnds, Unlisted;
            public double Nearest = double.MaxValue, BoxSep = double.MaxValue, MachineSep = double.MaxValue;
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
                // every cut end on the floor, live or dead, is in the pieces' list of ends (the registry the sparks, the glow, the shock and the
                // probe read): in-game visit 1 found a dead end drawn and missing from it (M8_break_two_ends_live_dead)
                foreach (CordNode nd in b.Graph.Nodes.Values.Where(n => n.Type == NodeType.Terminal && !n.Seam))
                {
                    if (!ps.Any(p => p.EndA != null && (p.EndA == nd.OracleName + ":" + nd.Cell.X + "," + nd.Cell.Z || p.EndB == nd.OracleName + ":" + nd.Cell.X + "," + nd.Cell.Z))) continue;
                    t.CutEnds++;
                    if (!ps.Any(p => p.Ends.Any(e => e.NetCell.Equals(nd.Cell)))) { t.Unlisted++; t.Bad.Add($"{x.name}: the cut end at {nd.Cell} ({(x.live(nd.Cell) ? "live" : "dead")}) is drawn but not in any piece's list of ends"); }
                }
                foreach (LiveEndCensus.End e in LiveEndCensus.Read(x.name, b.Graph, ps, x.live, null, new ulong[] { 0, 1, 5 }))
                {
                    t.Ends++;
                    string at = $"{x.name} {e.Cord} ({e.Len:0.00} of cord, {e.LayKind})";
                    if (e.NotStraight) { t.Straight++; t.Bad.Add($"{at}: not straight out of the conduit end (off {e.Off:0.00}, arrive {e.Arrive:0}, turn {e.Turn:0})"); }
                    if (e.Pinched) { t.Pinched++; t.Bad.Add($"{at}: pinched, radius {e.MinR:0.000}"); }
                    if (e.BadTail) { t.BadTail++; t.Bad.Add($"{at}: tail {e.Tail:0.00} outside 0.7-1.15"); }
                    // how near a fitting comes to a cut end, and whether its body lies on the end's own run
                    double farDist = Math.Sqrt(e.FarAlong * e.FarAlong + e.FarSide * e.FarSide);
                    if (e.FarType != "Terminal" && e.FarType != "?" && farDist > 1e-6)
                    {
                        t.Nearest = Math.Min(t.Nearest, farDist);
                        if (farDist < 2.0) t.Near++;
                    }
                    // how far a fitting's body stands from the end's own run, for fittings off the run's line (one ON the line is the straight shot):
                    // a box, plate or strip by its node's point; a machine by its footprint, when its plug is within a cell and a half of the end
                    if (e.FarBodyToRun >= 0 && Math.Abs(e.FarSide) > 0.05)
                    {
                        if (!e.FarMachine) t.BoxSep = Math.Min(t.BoxSep, e.FarBodyToRun);
                        else if (e.FarToEnd < 1.5) t.MachineSep = Math.Min(t.MachineSep, e.FarBodyToRun);
                    }
                    if (e.FarMachine && e.FarOnRun) { t.MachineOnRun++; t.Bad.Add($"{at}: its machine's footprint lies on its own straight run"); }
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

            // ---- what the game can place beside a cut end (RIMMANDRAKE_LAY_SLACK_CLOSE_FITTINGS_TWENTY_ONE_UNLAID)
            Tally p = Sweep(LiveEndCensus.Placements(true));
            Console.WriteLine($"  live end placements: {p.Worlds} worlds, {p.Ends} live ends, {p.Near} with their fitting under 2 cells off (nearest {p.Nearest:0.00}): {p.Kept} kept as handed, {p.Joined} joined, "
                              + $"{p.WholePigtail} short pigtails whipping whole, {p.Still} lying still, {p.Devices} tied loops, {p.None} unlaid; {p.Straight} not straight, {p.Pinched} pinched, {p.BadTail} tails off length; tightest bend {p.MinR:0.000}");
            foreach (string x in p.Bad.Take(8)) Console.WriteLine("  live end placements refused: " + x);
            Check(p.Ends >= 600 && p.Near >= 300, $"the placements put fittings beside cut ends ({p.Worlds} worlds, {p.Ends} live ends, {p.Near} with the fitting under 2 cells off, nearest {p.Nearest:0.00})");
            Check(p.Straight == 0 && p.Pinched == 0 && p.BadTail == 0 && p.None == 0 && p.Thin == 0,
                  $"every fitting the game can place beside a cut end is laid to: {p.None} unlaid, {p.Straight} not straight, {p.Pinched} pinched, {p.BadTail} tails off length, {p.Thin} under the margin, of {p.Ends} (tightest bend {p.MinR:0.000})");
            Check(p.StillWithRoom == 0, $"placements: an end lies still only where no whipping tail holds the bars: {p.StillWithRoom} of {p.Still} still ends could whip");
            // the three families the first report named as not built, each read on its own so none can go missing from the placements unseen
            foreach ((string tag, string what) in new[] { (" heap ", "a heap of cable as the far fitting"), (" water ", "a run that goes under water at the far cell"),
                                                         ("+ahead ", "a wall right ahead of the end besides its fitting") })
            {
                Tally f = Sweep(LiveEndCensus.Placements(true).Where(x => x.name.Contains(tag)));
                foreach (string x in f.Bad.Take(4)) Console.WriteLine("  live end placements refused: " + x);
                Console.WriteLine($"  live end placements, {what}: {f.Worlds} worlds, {f.Ends} live ends, {f.Joined} joined, {f.Kept} kept, {f.Still} lying still, {f.None} unlaid");
                Check(f.Ends >= 10 && f.Straight == 0 && f.Pinched == 0 && f.BadTail == 0 && f.None == 0 && f.Thin == 0,
                      $"placements, {what}: {f.Ends} live ends in {f.Worlds} worlds, {f.None} unlaid, {f.Straight} not straight, {f.Pinched} pinched, {f.BadTail} tails off length, {f.Thin} under the margin");
            }
            // THE PROOF that the unlaid poses of the abstract sweep are not the game's (selftest_gss_live_end_sweep.py: over 13,248 fitting poses, the
            // fitting's body modelled, the lay fails only where that body crowds the end's own straight run: a box, plate or strip whose middle is
            // within 0.749 cell of the run; a machine whose footprint lies on the run or within 0.219 of it with its plug right there). On the grid:
            //   a box, plate or strip off the run's line stands hypot(1 - 0.29, 0.44) = 0.835 from the run at the nearest (a plate beside the cell
            //   behind the end). BoxSepMin sits between the model's 0.749 and that;
            //   a machine's footprint never lies on the run: the run is wholly inside the end's own cell, which holds conduit.
            // And every machine the grid can stand beside or ahead of an end (the placements above, each side, size and offset) is laid to. The day
            // a mod or a rule puts a fitting's body nearer, this goes red, and that pose must be laid or ruled on
            double boxSep = Math.Min(p.BoxSep, t.BoxSep), machineSep = Math.Min(p.MachineSep, t.MachineSep);
            int onRun = p.MachineOnRun + t.MachineOnRun;
            Check(boxSep >= BoxSepMin && onRun == 0,
                  $"no fitting's body crowds a cut end's run: the nearest box, plate or strip off the run's line stands {boxSep:0.000} from it (limit {BoxSepMin}); {onRun} machine footprints lie on a run "
                  + $"(the nearest machine with its plug within 1.5 cells stands {machineSep:0.000} off, laid to like every placement); {p.Ends + t.Ends} live ends");

            // ---- challenge cases beside the families: the oracle's scenes in every look and random worlds. Nothing the builder lays anywhere is unlaid
            // (and the random worlds a 300-sequence census caught: sequence 257, a cut end in the cell past a doorway, once left unlaid; sequences 81 and
            // 284, a 0.8-cell cord from a water or device stub right behind the end, once kept whipping on a tail of exactly 0.70)
            Tally c = Sweep(LiveEndCensus.Worlds(0, 40, Program.OracleScenes, families: false).Select(x => (x.name, x.w, x.opt, x.live))
                            .Concat(GssFuzz.CordWorlds(284).Where(x => x.seed == 81 || x.seed == 257 || x.seed == 284).Select(x => ($"fuzz seed {x.seed} step {x.step}", x.w, x.opt, x.live)))
                            .Concat(PastADoor())
                            // (and the cut end one cell in front of its box with needless loops off, second draw: 8 of 126,730 in the whole
                            // census were left unlaid when the slack's keep-off round its own box was first applied to the live end's join too)
                            .Concat(LiveEndCensus.Family(2).Where(x => x.name.Contains(" len1 turn0 after0 ") && x.name.EndsWith(" noprune s1", StringComparison.Ordinal))));
            Console.WriteLine($"  live end challenge cases: {c.Worlds} worlds (oracle scenes x looks, 40 random sequences), {c.Ends} live ends: {c.None} unlaid, {c.Straight} not straight, {c.Pinched} pinched, {c.BadTail} tails off length, {c.Devices} tied loops, {c.Still} lying still");
            foreach (string x in c.Bad.Take(6)) Console.WriteLine("  live end challenge refused: " + x);
            int listed = t.CutEnds + p.CutEnds + c.CutEnds, unlisted = t.Unlisted + p.Unlisted + c.Unlisted;
            Check(listed >= 3000 && unlisted == 0, $"every cut end on the floor, live or dead, is in the list of ends: {unlisted} of {listed} drawn and not listed (families, placements, challenge cases)");
            Check(c.Ends >= 40 && c.None == 0 && c.Straight == 0 && c.Pinched == 0 && c.BadTail == 0 && c.Thin == 0,
                  $"challenge cases: every live end of the oracle scenes and the random worlds is laid and holds the bars: {c.None} unlaid, {c.Straight} not straight, {c.Pinched} pinched, {c.BadTail} tails off length, {c.Thin} under the margin, of {c.Ends}");

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
