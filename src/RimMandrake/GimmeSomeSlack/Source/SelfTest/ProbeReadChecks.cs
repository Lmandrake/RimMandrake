// RIMMANDRAKE_SETTLE_SLACK_CUT_CENSUS_DEAD_END_POLL_LATE (in-game visit 2, 2026-11-19: M8_break_two_ends_live_dead FAIL in 7 of
// 9 runs; the first census after a one-cell cut listed the live end only, the next poll with no tick between listed both).
// A probe read of the laid set is the published pieces, settled first when the component owes a build (Core/ProbeRead.cs).
// The generator: what the game varies for this bar is the cut (where on the run, which side the battery is, how long the run
// is) and, above all, how far the frame's build had got when the read arrived: a graph job running, a graph landed and not
// yet adopted, the adopting build's lays held with 0, 1 or all but one landed, a dirty event marked stale and no build yet,
// or nothing owed. Each case reads the way the probe does and must list every end a from-scratch complete build of the cut
// world lists, with the same live/dead kind. Left out: walls, doors, looks and other machines around the run (the read
// decision does not look at them; the end bars' own sweeps, LiveEndSweepChecks and CordEndKindChecks, cover the ends' shape
// there), and real frame timing (the states above are the timings' outcomes, each held exactly on the worker hooks).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class ProbeReadChecks
    {
        private const int Z = 10;

        /// <summary>A straight run of conduit cells x0..x0+len-1 on row Z, a battery at one end and a lamp at the other; cut = the
        /// x of the one removed cell (or -1).</summary>
        private static CordWorld Run(int x0, int len, bool batteryWest, int cut)
        {
            var w = new CordWorld(x0 + len + 8, 21);
            for (int x = x0; x < x0 + len; x++) if (x != cut) w.SetConduit(new Cell(x, Z));
            int bx = batteryWest ? x0 : x0 + len - 1, lx = batteryWest ? x0 + len - 1 : x0;
            w.Machines.Add(new MachineInfo { Id = "bat", Kind = MachineKind.Battery, X0 = bx, Z0 = Z + 1, Hookups = new List<Cell> { new Cell(bx, Z) } });
            w.Machines.Add(new MachineInfo { Id = "lamp", Kind = MachineKind.Lamp, X0 = lx, Z0 = Z - 1, Hookups = new List<Cell> { new Cell(lx, Z) } });
            return w;
        }

        /// <summary>Every end of the set: its net cell and its fray kind (live, dead, or none drawn), sorted.</summary>
        private static List<string> Ends(IEnumerable<LaidPiece> ps)
        {
            var rows = new List<string>();
            foreach (LaidPiece p in ps)
                foreach (CordEnd e in p.Ends)
                {
                    bool live = p.Decals.Any(d => d.Kind == DecalKind.FrayLive && V2.Dist(d.Pos, e.Tip) < 0.75);
                    bool dead = p.Decals.Any(d => d.Kind == DecalKind.FrayDead && V2.Dist(d.Pos, e.Tip) < 0.75);
                    rows.Add(e.NetCell.X + "," + e.NetCell.Z + (live ? " live" : dead ? " dead" : " bare"));
                }
            rows.Sort(StringComparer.Ordinal);
            return rows;
        }

        private static void WaitFor(Func<bool> done, string what)
        {
            var t = Stopwatch.StartNew();
            while (!done()) { if (t.Elapsed.TotalSeconds > 60) { Program.Check(false, $"probe read: worker wait '{what}' timed out after 60 s"); return; } System.Threading.Thread.Sleep(1); }
        }

        private enum State { GraphRunning, GraphLanded, LaysNone, LaysOne, LaysAllButOne, StaleNoBuild, Settled }

        internal static void Run() => Run(ProbeRead.OwesBuild);

        /// <summary>owes: the read's decision (the shipped ProbeRead.OwesBuild; the red-first run passes the old behaviour, never).</summary>
        internal static void Run(Func<bool, int, bool, bool> owes)
        {
            int cases = 0, owed = 0, rawStale = 0, bad = 0, bothCutEnds = 0, needless = 0, skipped = 0;
            var firstBad = new List<string>();
            var perState = new Dictionary<State, int[]>();      // cases, raw read differed, settled read differed
            foreach (int len in new[] { 4, 5, 7, 9, 12, 16 })
                foreach (bool west in new[] { true, false })
                    for (int cut = 3 + 1; cut < 3 + len - 1; cut++)
                        foreach (State st in Enum.GetValues(typeof(State)))
                        {
                            Func<Cell, bool> livePre = c => true;
                            // after the cut only the battery's side carries power
                            int cx = cut;
                            Func<Cell, bool> liveCut = c => west ? c.X < cx : c.X > cx;
                            List<string> want = Ends(new CordBuilder().Build(Run(3, len, west, cut), new BuildOptions(), liveCut));
                            if (want.Count < 2) { skipped++; continue; }
                            bool cutEnds = want.Any(r => r.StartsWith((cut - 1) + "," + Z + " ")) && want.Any(r => r.StartsWith((cut + 1) + "," + Z + " "));

                            var graphGo = new System.Threading.SemaphoreSlim(0);
                            var layGo = new System.Threading.SemaphoreSlim(0);
                            var b = new CordBuilder { GraphJobHook = () => graphGo.Wait(), WorkerLayHook = k => layGo.Wait(), CoalescePieces = 1 };
                            List<LaidPiece> published = b.Build(Run(3, len, west, -1), new BuildOptions(), livePre);   // the colony before the cut
                            bool stale = false;
                            var async = new BuildOptions { AsyncLay = true };
                            if (st == State.StaleNoBuild) stale = true;                 // the destroy's dirty event, no frame since
                            else if (st != State.Settled)
                            {
                                published = b.Build(Run(3, len, west, cut), async, liveCut);   // starts the graph job, shows the old set
                                if (st != State.GraphRunning)
                                {
                                    graphGo.Release(1000);
                                    WaitFor(() => b.LayReady, "graph landed");
                                    if (st != State.GraphLanded)
                                    {
                                        published = b.Build(Run(3, len, west, cut), async, liveCut);   // adopts the graph, queues the lays
                                        int queued = b.LastPending;
                                        int land = st == State.LaysNone ? 0 : st == State.LaysOne ? 1 : Math.Max(0, queued - 1);
                                        if (land > 0)
                                        {
                                            layGo.Release(land);
                                            WaitFor(() => b.LayReadyCoalesced(Stopwatch.GetTimestamp()) || !b.LayRunning, "lays landed");
                                            System.Threading.Thread.Sleep(5);
                                            published = b.Build(Run(3, len, west, cut), async, liveCut);
                                        }
                                    }
                                }
                            }
                            else published = b.Build(Run(3, len, west, cut), new BuildOptions(), liveCut);   // the frame finished it
                            bool o = owes(true, b.LastPending, stale);
                            List<LaidPiece> read = o ? b.Build(Run(3, len, west, cut), new BuildOptions(), liveCut) : published;
                            graphGo.Release(100000);
                            layGo.Release(100000);
                            WaitFor(() => !b.LayRunning, "workers drained");

                            List<string> raw = Ends(published), got = Ends(read);
                            bool rawDiff = !raw.SequenceEqual(want), diff = !got.SequenceEqual(want);
                            if (!perState.TryGetValue(st, out int[] ps)) perState[st] = ps = new int[3];
                            ps[0]++; if (rawDiff) ps[1]++; if (diff) ps[2]++;
                            cases++;
                            if (o) owed++;
                            if (rawDiff) rawStale++;
                            if (cutEnds) bothCutEnds++;
                            if (st == State.Settled && o) needless++;
                            if (diff)
                            {
                                bad++;
                                if (firstBad.Count < 4)
                                    firstBad.Add($"len {len} {(west ? "battery west" : "battery east")} cut x={cut} {st}: read [{string.Join("; ", got)}] want [{string.Join("; ", want)}]");
                            }
                        }
            string states = string.Join(", ", perState.OrderBy(kv => kv.Key).Select(kv => $"{kv.Key} {kv.Value[0]} (raw stale {kv.Value[1]}, read wrong {kv.Value[2]})"));
            Console.WriteLine($"probe read: {cases} cases ({skipped} cuts with fewer than 2 ends skipped), {bothCutEnds} with both cut ends listed by the complete build; " +
                              $"owed {owed}; raw published set wrong in {rawStale}; settled read wrong in {bad} (limit 0); needless builds {needless} (limit 0)");
            Console.WriteLine("probe read: by state: " + states);
            Program.Check(rawStale > 0, "probe read: blind, no case's published set differed from the cut world's ends (the generator cannot see the race)");
            Program.Check(bothCutEnds > 0, "probe read: blind, no complete build listed both cut ends");
            Program.Check(bad == 0, $"probe read: {bad} of {cases} reads listed ends other than the complete build's (M8: the first census after a cut must list the live and the dead end): " + string.Join(" | ", firstBad));
            Program.Check(needless == 0, $"probe read: {needless} reads built though nothing was owed (a probe build would hide an unannounced change from D2)");
            // the command split: the laid-set reads settle; the frame measures, the print comparison and the builds of their own do not
            foreach (string c in new[] { "census", "fresh", "rect:1,2,3,4", "ends:5,5,3", "endkind:1,2", "joins:1,2,3,4", "under:1,2,3,4", "bends", "kinks", "styles", "slack", "artfit", "strandsnear:1,2,3", "worlddump:1,2,3,4", "shapeaudit", "shapetable", "doorstrays" })
                Program.Check(ProbeRead.ReadsLaidSet(c), $"probe read: '{c}' reads the laid set and must settle first");
            foreach (string c in new[] { "motion", "strands:1,2,3,4", "poll", "rebuild", "sameframe:1,2,3,4", "slicereset", "set:enabled=true", "setmany:defaults", "colonists", "pawn:1=draft", "select:1,2", "statics", "", null })
                Program.Check(!ProbeRead.ReadsLaidSet(c), $"probe read: '{c}' must not build before it answers");
            Program.Check(!ProbeRead.OwesBuild(false, 5, true), "probe read: a disabled mod owes no build");
        }
    }
}
