// GSS_PLAN_FIX_SECOND_PER_FULL_BUILD + GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG round 3 (live round 4, 2026-10-26).
// (1) A planned build of the live scene (E=248) held one frame ~1 s on Mono (offline .NET 8: ~225 ms, 97% of it the per-strand
//     settle in CordLayer.Sprawl). A budgeted Build lays edges until its budget is spent and leaves the rest to the next Build;
//     the run of Builds must end bit-identical to one unbudgeted Build, and no slice may hold a frame.
// (2) A far dig left the live probe's farSkips unmoved: the skip was counted only when our section layer regenerated, which
//     vanilla does for on-screen sections only. RebuildGate counts it when the dirty event is classified.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SliceGateChecks
    {
        /// <summary>The slice bound: the game's frame budget (8 ms) plus one worst edge and the node/reach tail, well under
        /// the 20 ms the live re-measure requires.</summary>
        private const double BudgetMs = 8.0, SliceBoundMs = 20.0;

        internal static void Run()
        {
            Slices();
            Gate();
        }

        private static (int slices, double worst, List<LaidPiece> last, int minEdgePieces) Converge(CordBuilder b, CordWorld w, BuildOptions opt, Func<Cell, bool> live)
        {
            int slices = 0, minPieces = int.MaxValue;
            double worst = 0;
            List<LaidPiece> outp = null;
            var sw = new Stopwatch();
            do
            {
                sw.Restart();
                outp = b.Build(w, opt, live);
                worst = Math.Max(worst, sw.Elapsed.TotalMilliseconds);
                slices++;
                minPieces = Math.Min(minPieces, outp.Count(p => p.EndA != null));
            } while (b.LastPending > 0 && slices < 2000);
            return (slices, worst, outp, minPieces);
        }

        private static void Slices()
        {
            Func<Cell, bool> dead = c => false;
            ulong want = GssFuzz.Digest(new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), dead));
            int edges = new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), dead).Count(p => p.EndA != null);

            // a cold planned build (the first build on a loaded map, a lattice placed at once)
            var opt = new BuildOptions { LayBudgetMs = BudgetMs };
            var b = new CordBuilder();
            var (slices, worst, last, _) = Converge(b, RebuildPerDigChecks.LiveScene(), opt, dead);
            Program.Check(worst <= SliceBoundMs, $"slice: a planned build of the live scene (E={edges}) held one Build {worst:0.0} ms (bound {SliceBoundMs} ms, budget {BudgetMs} ms)");
            Program.Check(slices > 1, $"slice: the cold build finished in {slices} Build (the budget never deferred an edge: instrument blind)");
            Program.Check(b.LastPending == 0 && GssFuzz.Digest(last) == want, "slice: the budgeted Builds did not end bit-identical to one unbudgeted Build");
            Console.WriteLine($"slice: cold E={edges} planned over {slices} Builds, worst {worst:0.0} ms (budget {BudgetMs} ms)");

            // every key changes at once (the slack setting moved): until the re-lay completes each edge keeps its previous cord
            var opt2 = new BuildOptions { LayBudgetMs = BudgetMs };
            opt2.Lay.SlackScale *= 0.8;
            var full2 = new BuildOptions();
            full2.Lay.SlackScale = opt2.Lay.SlackScale;
            var (slices2, worst2, last2, minEdges2) = Converge(b, RebuildPerDigChecks.LiveScene(), opt2, dead);
            ulong wantLit = GssFuzz.Digest(new CordBuilder().Build(RebuildPerDigChecks.LiveScene(), full2, dead));
            Program.Check(worst2 <= SliceBoundMs && slices2 > 1, $"slice: an all-keys-changed re-lay held one Build {worst2:0.0} ms over {slices2} Builds");
            Program.Check(GssFuzz.Digest(last2) == wantLit, "slice: the all-keys-changed re-lay did not end bit-identical to one unbudgeted Build");
            Program.Check(minEdges2 == edges, $"slice: a mid-re-lay Build showed {minEdges2} of {edges} cords (a deferred edge must keep its previous piece)");

            // an all-reused Build is never sliced, and an unbudgeted Build never defers
            b.Build(RebuildPerDigChecks.LiveScene(), opt2, dead);
            Program.Check(b.LastPending == 0 && b.LastPlanned == 0, $"slice: an all-reused budgeted Build planned {b.LastPlanned}, pending {b.LastPending}");
            var u = new CordBuilder();
            u.Build(RebuildPerDigChecks.LiveScene(), new BuildOptions(), dead);
            Program.Check(u.LastPending == 0 && u.LastPlanned == edges, $"slice: an unbudgeted Build planned {u.LastPlanned} of {edges}, pending {u.LastPending}");
        }

        private static string Names(ulong f) => "0x" + f.ToString("X");

        /// <summary>The gate on the live lattice and the live far dig 135,120 (flag bits are arbitrary here: only "inside the
        /// benign set or not" matters). The dig is off screen, so no layer regenerate follows it.</summary>
        private static void Gate()
        {
            const ulong terrain = 1, roofs = 2, buildings = 4, fog = 8, power = 16, ours = 32, benign = terrain | roofs | buildings | fog;
            var b = new CordBuilder();
            b.Build(RebuildPerDigChecks.Lattice(), new BuildOptions(), c => true);
            CordReach reach = b.Reach;
            Func<Cell, bool> nothing = c => false;
            var far = new Cell(135, 120);

            var g = new RebuildGate();
            Program.Check(g.RegenerateNeedsBuild(), "gate: a fresh gate (before any build) skipped the first build");
            g.Published(0);
            bool skip = g.Note(false, terrain, benign, reach, far, nothing, Names);
            Program.Check(skip && g.FarSkips == 1 && g.RelevantEvents == 0, $"gate: an off-screen far dig was not counted as a far skip (skip {skip}, farSkips {g.FarSkips}, relevant {g.RelevantEvents})");
            Program.Check(g.LastFarSkip(Names) == "0x1@135,120", $"gate: lastFarSkip '{g.LastFarSkip(Names)}'");
            Program.Check(!g.RegenerateNeedsBuild() && g.RegenSkips == 1, "gate: a regenerate after only a far dig rebuilt");
            g.Note(false, terrain | roofs, benign, reach, far, nothing, Names);
            Program.Check(g.FarSkips == 2, "gate: a second far dig (terrain + roof) was not counted");

            // our own reprint is benign but not a far skip; a powered far cell, a power-grid event and an in-reach dig are relevant
            g.Note(true, ours, benign, reach, new Cell(171, 166), nothing, Names);
            Program.Check(g.FarSkips == 2 && g.RelevantEvents == 0, "gate: our own section dirtying counted as a far skip or relevant");
            Program.Check(!g.Note(false, buildings, benign, reach, far, c => true, Names), "gate: a conduit built at a far cell was benign");
            g.Published(0);
            Program.Check(!g.Note(false, terrain | power, benign, reach, far, nothing, Names), "gate: a far power-grid event was benign");
            g.Published(0);
            Program.Check(!g.Note(false, terrain, benign, reach, new Cell(171, 166), nothing, Names) && g.RegenerateNeedsBuild(),
                          "gate: a dig under a conduit did not force a rebuild");
            Program.Check(g.LastRelevant == "0x1@171,166 inReach", $"gate: lastRelevant '{g.LastRelevant}'");
            Program.Check(!g.Note(false, terrain, benign, null, far, nothing, Names), "gate: with no reach (before the first build) a far dig was benign");

            // a build that left edges pending keeps the cords stale: the next regenerate must rebuild
            g.Published(3);
            g.Note(false, terrain, benign, reach, far, nothing, Names);
            Program.Check(g.RegenerateNeedsBuild(), "gate: a regenerate while a sliced build was pending skipped the rebuild");
            Console.WriteLine($"gate: farSkips {g.FarSkips}, regenSkips {g.RegenSkips}, relevant {g.RelevantEvents}");
        }
    }
}
