// RIMMANDRAKE_MEND_SLACK_STYLED_RUNS_FRESH_BUILD_DIVERGES (in-game visit 2, 2026-11-19): on the full-list review map the walk's
// "live cords == fresh build" read FAILED on station 5 (Modern colour runs) and station 31 (an Industrial run), and passed on a
// plain map. The walk's fresh build took bare settings; production keys every edge by its run's look (pile art + plug boot).
// This sweeps the range of looks a map can hold and requires the live recipe and the fresh recipe (both through the SHIPPED
// Core BuildOptions.UseLooks) to agree, and the bare-settings recipe to diverge exactly where the look rule says it must.
//
// Range: the default look (the settings' style) x the look stored by run A x the look stored by run B, each run a conduit
// line from a battery to a lamp (run A with a 3-cell spur, so a junction end too): 4 x 5 x 5 = 100 cases (5 = unstyled or one
// of the 4 looks). Each case is built live-style: one builder that first laid the map under the previous looks (a restyle
// re-keys a cached edge), then (a) a complete build and (b) the AsyncLay worker path drained, both against a fresh builder.
// Left out: Modern colours (a colour picks a material, never a key or a pile: ConduitStyles.PieceVariant), tap clamps (the
// StraightPlugIds input, guarded by selftest_gss_weakclose_guards.py and selftest_gss_fresh_build_inputs.py), and terrain
// (DeterminismChecks replays 64 recorded boards for that).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class StyledFreshChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "styled fresh: " + msg);

        private static readonly HashSet<Cell> RunA = new HashSet<Cell>(), RunB = new HashSet<Cell>();

        private static CordWorld World()
        {
            var w = new CordWorld(32, 14);
            RunA.Clear(); RunB.Clear();
            for (int x = 3; x <= 12; x++) RunA.Add(new Cell(x, 4));
            for (int z = 5; z <= 7; z++) RunA.Add(new Cell(8, z));
            for (int x = 17; x <= 27; x++) RunB.Add(new Cell(x, 9));
            foreach (Cell c in RunA.Concat(RunB)) w.SetConduit(c);
            void M(string id, MachineKind k, int x, int z, Cell hook) =>
                w.Machines.Add(new MachineInfo { Id = id, Kind = k, X0 = x, Z0 = z, W = 1, H = 1, Hookups = new List<Cell> { hook } });
            M("tA", MachineKind.Battery, 3, 3, new Cell(3, 4));
            M("cA", MachineKind.Consumer, 12, 1, new Cell(12, 4));
            M("tB", MachineKind.Battery, 17, 8, new Cell(17, 9));
            M("cB", MachineKind.Consumer, 27, 11, new Cell(27, 9));
            return w;
        }

        /// <summary>The settings' default look as GimmeSomeSlackSettings.BuildOptions sets it (strips only for the Modern look).</summary>
        private static BuildOptions Defaults(string look) =>
            new BuildOptions { Pile = look == "Modern" ? PileArt.Strips : PileArt.Junctions, PlugBoot = CordBuilder.PlugBootU(look) };

        private static Func<Cell, string> Looks(string a, string b) => c => RunA.Contains(c) ? a : RunB.Contains(c) ? b : null;

        private static bool Same(string look, string def) =>
            look == null || ((look == "Modern") == (def == "Modern") && CordBuilder.PlugBootU(look) == CordBuilder.PlugBootU(def));

        public static void Run()
        {
            string[] runLooks = new string[] { null }.Concat(AerialStyles.Looks).ToArray();
            CordWorld w = World();
            Func<Cell, bool> live = c => w.IsConduit(c);
            int cases = 0, badComplete = 0, badAsync = 0, worstComplete = 0, worstAsync = 0, oldDiverged = 0, oldPredicted = 0, oldMismatch = 0;
            int worstDrain = 0, drainTimeouts = 0;
            string firstBad = null, firstMismatch = null;
            foreach (string def in AerialStyles.Looks)
                for (int ia = 0; ia < runLooks.Length; ia++)
                    for (int ib = 0; ib < runLooks.Length; ib++)
                    {
                        string la = runLooks[ia], lb = runLooks[ib];
                        // the look each run held before (a restyle re-keys the cached edges)
                        string pa = runLooks[(ia + 1) % runLooks.Length], pb = runLooks[(ib + 2) % runLooks.Length];
                        cases++;
                        List<LaidPiece> fresh = new CordBuilder().Build(w, Defaults(def).UseLooks(Looks(la, lb)), live);

                        var b = new CordBuilder();
                        b.Build(w, Defaults(def).UseLooks(Looks(pa, pb)), live);
                        var rc = DeterminismChecks.Compare(b.Build(w, Defaults(def).UseLooks(Looks(la, lb)), live), fresh);
                        int nc = rc.diff + rc.missing;
                        worstComplete = Math.Max(worstComplete, nc);
                        if (nc > 0 || rc.same == 0) { badComplete++; firstBad ??= $"complete {def}/{la ?? "-"}/{lb ?? "-"}: {string.Join("; ", rc.diffKeys.Take(2))}"; }

                        // the game's frame path: the lay on a worker, later Builds take what landed
                        var ba = new CordBuilder();
                        ba.Build(w, Defaults(def).UseLooks(Looks(pa, pb)), live);
                        List<LaidPiece> outA = null;
                        int drains = 0;
                        var sw = System.Diagnostics.Stopwatch.StartNew();
                        while (true)
                        {
                            BuildOptions o = Defaults(def).UseLooks(Looks(la, lb));
                            o.AsyncLay = true;
                            outA = ba.Build(w, o, live);
                            drains++;
                            if (ba.LastPending == 0 && !ba.LastGraphPending) break;
                            if (sw.Elapsed.TotalSeconds > 30) { drainTimeouts++; break; }   // a worker that never lands: reported, not waited on
                            System.Threading.Thread.Sleep(1);
                        }
                        worstDrain = Math.Max(worstDrain, drains);
                        var ra = DeterminismChecks.Compare(outA, fresh);
                        int na = ra.diff + ra.missing;
                        worstAsync = Math.Max(worstAsync, na);
                        if (na > 0 || ra.same == 0) { badAsync++; firstBad ??= $"async {def}/{la ?? "-"}/{lb ?? "-"}: {string.Join("; ", ra.diffKeys.Take(2))}"; }

                        // challenge: the visit-2 walk's recipe (bare settings, no run looks) against production's build
                        var ro = DeterminismChecks.Compare(new CordBuilder().Build(w, Defaults(def), live), fresh);
                        bool diverged = ro.diff + ro.missing > 0;
                        bool predicted = !Same(la, def) || !Same(lb, def);
                        if (diverged) oldDiverged++;
                        if (predicted) oldPredicted++;
                        if (diverged != predicted) { oldMismatch++; firstMismatch ??= $"{def}/{la ?? "-"}/{lb ?? "-"}: diverged {diverged}, rule says {predicted}"; }
                    }
            Check(cases == 100, $"read {cases} cases (4 default looks x 5 run-A looks x 5 run-B looks), want 100");
            Check(badComplete == 0, $"live recipe, complete build after a restyle == fresh build with the run looks in {cases - badComplete}/{cases} cases (worst {worstComplete} pieces off, limit 0){(firstBad == null ? "" : "; first: " + firstBad)}");
            Check(badAsync == 0 && drainTimeouts == 0, $"live recipe, AsyncLay worker drained == fresh build in {cases - badAsync}/{cases} cases (worst {worstAsync} pieces off, limit 0; most Builds to drain {worstDrain}, timeouts {drainTimeouts})");
            Check(oldMismatch == 0 && oldPredicted > 0 && oldPredicted < cases, $"can fail: the bare-settings fresh build (visit 2's walk) diverges in {oldDiverged}/{cases} cases, exactly the {oldPredicted} where a run's look keys a pile or plug boot other than the default's ({oldMismatch} off the rule){(firstMismatch == null ? "" : "; first: " + firstMismatch)}");
            Console.WriteLine($"styled fresh: {cases} cases; live == fresh complete {cases - badComplete}, async {cases - badAsync}; bare-settings recipe diverged {oldDiverged} (rule {oldPredicted})");
        }
    }
}
