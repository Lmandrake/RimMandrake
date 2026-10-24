// Selftest for TIDE as a TERRITORY SHAPE and the canon-pairing table (Kernel/RM_TerritoryShapes.cs), kernel only.
// REAL, compiled from production source. NOT covered: the compositor's lookup of a claim's signature (needs Verse and
// loaded defs; the plan and allocation it calls are tested here).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.AtmosphericBase;

internal static class TerritoryTests
{
    private static void Check(string name, bool ok, string detail = "") => Program.Check(name, ok, detail);

    private sealed class Canvas
    {
        public RM_RoomGraph g;
        public List<int> ids = new List<int>(), nodes = new List<int>(), rooms = new List<int>();
        public List<float> x = new List<float>(), z = new List<float>();
        public int Count => ids.Count;
    }

    /// <summary>Rooms 1..n in a line, room 1 opens outside; `per` fixtures each.</summary>
    private static Canvas Chain(int n, int per)
    {
        var rs = new List<RM_RoomFacts>(); var ds = new List<KeyValuePair<int, int>>();
        for (int i = 1; i <= n; i++) { rs.Add(new RM_RoomFacts { id = i, cells = 20, threshold = i == 1 }); if (i > 1) ds.Add(new KeyValuePair<int, int>(i - 1, i)); }
        return Fill(RM_RoomGraph.Build(rs, ds), per, r => (r * 6f, 0f));
    }

    /// <summary>A ring of n rooms, room 5 the threshold, room 3 holds power.</summary>
    private static Canvas Ring(int n, int per)
    {
        var rs = new List<RM_RoomFacts>(); var ds = new List<KeyValuePair<int, int>>();
        for (int i = 1; i <= n; i++) { rs.Add(new RM_RoomFacts { id = i, cells = 20 + i, threshold = i == 5, power = i == 3 }); ds.Add(new KeyValuePair<int, int>(i, i % n + 1)); }
        return Fill(RM_RoomGraph.Build(rs, ds), per, r => ((float)(10 * Math.Cos(r)), (float)(10 * Math.Sin(r))));
    }

    /// <summary>A hub (room 1, many doors, big) with three arms of three rooms; the end of arm one opens outside.</summary>
    private static Canvas Branch(int per)
    {
        var rs = new List<RM_RoomFacts> { new RM_RoomFacts { id = 1, cells = 80 } };
        var ds = new List<KeyValuePair<int, int>>();
        int id = 2;
        for (int arm = 0; arm < 3; arm++)
        {
            int prev = 1;
            for (int k = 0; k < 3; k++) { rs.Add(new RM_RoomFacts { id = id, cells = 16, threshold = arm == 0 && k == 2 }); ds.Add(new KeyValuePair<int, int>(prev, id)); prev = id; id++; }
        }
        return Fill(RM_RoomGraph.Build(rs, ds), per, r => (r * 3f, (r % 3) * 4f));
    }

    private static Canvas Fill(RM_RoomGraph g, int per, Func<int, (float, float)> at)
    {
        var c = new Canvas { g = g };
        int k = 0;
        for (int node = 0; node < g.Count; node++)
            for (int j = 0; j < per; j++, k++)
            {
                c.ids.Add(7000 + (k * 7919) % 9973);
                c.nodes.Add(node); c.rooms.Add(g.roomIds[node]);
                (float px, float pz) = at(g.roomIds[node]);
                c.x.Add(px + j * 0.7f); c.z.Add(pz + (j % 2) * 0.9f);
            }
        return c;
    }

    private static RM_TerritoryTuning Tune(float share = 0.6f, float ragged = 0f) =>
        new RM_TerritoryTuning { periodSeconds = 240f, leadShare = share, ragged = ragged };

    private static readonly List<RM_PairingRule> Canon = new List<RM_PairingRule>
    {
        new RM_PairingRule { a = "Ishko", b = "TaBaa", anchorA = RM_Anchor.Core, anchorB = RM_Anchor.Threshold, label = "meet at the threshold" },
        new RM_PairingRule { a = "Shkaar", b = "Ishko", anchorA = RM_Anchor.Open, anchorB = RM_Anchor.Core, aHunts = true, label = "Sh'kaar hunts Ishko" },
    };

    private static bool[] At(Canvas c, long step, RM_TerritoryPlan p, RM_TerritoryTuning t, int salt = 12345) =>
        RM_TerritoryShapes.Allocate(c.ids, c.x, c.z, c.nodes, c.g, step, salt, t, p);

    /// <summary>Max over fixtures of the number of hand-overs during one turn (step 0..240 inclusive).</summary>
    private static int MaxFlips(Canvas c, RM_TerritoryPlan p, RM_TerritoryTuning t, int salt)
    {
        var flips = new int[c.Count];
        bool[] prev = At(c, 0, p, t, salt);
        for (long s = 1; s <= RM_TerritoryKernel.StepsPerTurn; s++)
        {
            bool[] cur = At(c, s, p, t, salt);
            for (int i = 0; i < c.Count; i++) if (cur[i] != prev[i]) flips[i]++;
            prev = cur;
        }
        return flips.Max();
    }

    internal static void Run()
    {
        // ---------------- the plan: canon pairings first (either order), the leader's shape elsewhere
        RM_TerritoryShape tideCore = RM_TerritoryShape.Tide(RM_Anchor.Core);
        RM_TerritoryPlan p1 = RM_TerritoryShapes.Plan("Ishko", tideCore, "TaBaa", Canon);
        Check("pairing: Ishko leading Ta'Baa is a paired tide Core/Threshold", p1.kind == RM_PlanKind.PairedTide && p1.leadAnchor == RM_Anchor.Core
              && p1.otherAnchor == RM_Anchor.Threshold && p1.hunter == -1, p1.ToString());
        RM_TerritoryPlan p2 = RM_TerritoryShapes.Plan("TaBaa", RM_TerritoryShape.Tide(RM_Anchor.Threshold), "Ishko", Canon);
        Check("pairing: the same rule read in the other rank order swaps the anchors", p2.kind == RM_PlanKind.PairedTide
              && p2.leadAnchor == RM_Anchor.Threshold && p2.otherAnchor == RM_Anchor.Core, p2.ToString());
        RM_TerritoryPlan h0 = RM_TerritoryShapes.Plan("Shkaar", RM_TerritoryShape.Tide(RM_Anchor.Open), "Ishko", Canon);
        RM_TerritoryPlan h1 = RM_TerritoryShapes.Plan("Ishko", tideCore, "Shkaar", Canon);
        Check("pairing: Sh'kaar hunts Ishko whichever of them is louder", h0.hunter == 0 && h1.hunter == 1
              && h0.leadAnchor == RM_Anchor.Open && h1.otherAnchor == RM_Anchor.Open, h0 + " | " + h1);
        RM_TerritoryPlan e1 = RM_TerritoryShapes.Plan("Ozzik", RM_TerritoryShape.Tide(RM_Anchor.Grandest), "TaBaa", Canon);
        RM_TerritoryPlan e2 = RM_TerritoryShapes.Plan("Mob", RM_TerritoryShape.Wedge, "Ishko", Canon);
        RM_TerritoryPlan e3 = RM_TerritoryShapes.Plan(null, RM_TerritoryShape.Wedge, null, Canon);
        Check("elsewhere: an unpaired tide leader floods from its own anchor; a wedge leader keeps the wedge; no signature = wedge",
              e1.kind == RM_PlanKind.LeaderTide && e1.leadAnchor == RM_Anchor.Grandest && e2.kind == RM_PlanKind.Wedge && e3.kind == RM_PlanKind.Wedge,
              e1 + " | " + e2 + " | " + e3);
        RM_TerritoryPlan c1 = RM_TerritoryShapes.Plan("Ohm", new RM_TerritoryShape { kind = RM_ShapeKind.Circuit }, "Oomo", Canon);
        Check("CIRCUIT runs as TIDE(Power) until a conduit graph exists", c1.kind == RM_PlanKind.LeaderTide && c1.leadAnchor == RM_Anchor.Power, c1.ToString());
        var rev = new List<RM_PairingRule>(Canon); rev.Reverse();
        Check("the plan does not depend on the order the rules were loaded in",
              RM_TerritoryShapes.Plan("Ishko", tideCore, "Shkaar", rev).ToString() == h1.ToString()
              && RM_TerritoryShapes.Plan("Ishko", tideCore, "TaBaa", rev).ToString() == p1.ToString());

        // ---------------- the canon pair meets at the threshold, on every canvas
        var canvases = new[] { ("chain", Chain(7, 3)), ("ring", Ring(8, 3)), ("branch", Branch(3)) };
        foreach ((string name, Canvas c) in canvases)
        {
            int thr = c.g.AnchorNodes(RM_Anchor.Threshold)[0];
            bool taBaaKeepsDoor = true, cut = true;
            foreach (RM_TerritoryPlan p in new[] { p1, p2 })
                for (long s = 0; s < RM_TerritoryKernel.StepsPerTurn; s += 3)
                {
                    bool[] got = At(c, s, p, Tune());
                    bool ishkoLeads = p.leadAnchor == RM_Anchor.Core;
                    // ishko's side: d_core - d_thr; Ta'Baa holds the larger values
                    var key = Enumerable.Range(0, c.Count).Select(i => c.g.Distance(RM_Anchor.Core, c.nodes[i]) - c.g.Distance(RM_Anchor.Threshold, c.nodes[i])).ToArray();
                    int maxIshko = int.MinValue, minTa = int.MaxValue;
                    for (int i = 0; i < c.Count; i++)
                    {
                        bool ishko = got[i] == ishkoLeads;
                        if (ishko) maxIshko = Math.Max(maxIshko, key[i]); else minTa = Math.Min(minTa, key[i]);
                        if (c.nodes[i] == thr && ishko) taBaaKeepsDoor = false;
                    }
                    if (maxIshko > minTa) cut = false;   // one front: every Ishko fixture lies core-side of every Ta'Baa fixture
                }
            Check("pairing (" + name + "): Ta'Baa holds the threshold room at every step, whichever leads", taBaaKeepsDoor);
            Check("pairing (" + name + "): one front between the two anchors (Ishko core-side of every Ta'Baa fixture)", cut);
            Check("pairing (" + name + "): the boundary moves (the share takes more than two values over a turn)",
                  Enumerable.Range(0, RM_TerritoryKernel.StepsPerTurn).Select(s => At(c, s, p1, Tune()).Count(b => b)).Distinct().Count() > 2);
        }

        // ---------------- laws on every canvas and plan: both sides keep a fixture, the quieter a fifth, <= 2 flips a turn
        RM_TerritoryPlan lt = RM_TerritoryShapes.Plan("Ozzik", RM_TerritoryShape.Tide(RM_Anchor.Core), "Oomo", Canon);
        foreach ((string name, Canvas c) in canvases)
            foreach ((string pn, RM_TerritoryPlan p) in new[] { ("paired", p1), ("hunt-lead", h0), ("hunt-second", h1), ("leader-tide", lt) })
            {
                bool both = true, fifth = true; int n = c.Count, lo = (int)Math.Round(0.2 * n) - 1;
                foreach (float share in new[] { 0.5f, 0.65f, 0.8f })
                    for (long s = 0; s < RM_TerritoryKernel.StepsPerTurn; s++)
                    {
                        int k = At(c, s, p, Tune(share)).Count(b => b);
                        if (k < 1 || k > n - 1) both = false;
                        if (k < lo || n - k < lo) fifth = false;
                    }
                int fl = new[] { 1, 77, 991, -5 }.Max(salt => new[] { 0f, 0.25f }.Max(rg => MaxFlips(c, p, Tune(0.6f, rg), salt)));
                Check("laws (" + name + ", " + pn + "): both claimants always hold a fixture and the smaller side about a fifth", both && fifth);
                Check("laws (" + name + ", " + pn + "): no fixture changes hands more than twice in a turn", fl <= 2, "max flips " + fl);
            }

        // ---------------- the hunt: the hunter surges to the cap, stands, falls -- whichever of the two is louder
        {
            Canvas c = Ring(8, 3); int n = c.Count;
            foreach ((string pn, RM_TerritoryPlan p) in new[] { ("Sh'kaar louder", h0), ("Sh'kaar quieter", h1) })
            {
                var hk = Enumerable.Range(0, RM_TerritoryKernel.StepsPerTurn).Select(s => { int k = At(c, s, p, Tune(0.55f)).Count(b => b); return p.hunter == 0 ? k : n - k; }).ToArray();
                int peak = hk.Max(), cap = RM_TerritoryShapes.TideCount(n, RM_TerritoryKernel.MaxLeadShare);
                int run = 0, best = 0;
                for (int i = 0; i < 2 * hk.Length; i++) { if (hk[i % hk.Length] == peak) { run++; best = Math.Max(best, run); } else run = 0; }
                Check("hunt (" + pn + "): the hunter's share reaches the 0.8 cap", peak == cap, "peak " + peak + "/" + n + " cap " + cap);
                Check("hunt (" + pn + "): it stands at the peak for about a quarter turn", best >= (int)(RM_TerritoryShapes.HuntStand * RM_TerritoryKernel.StepsPerTurn) - 2
                      && best < RM_TerritoryKernel.StepsPerTurn / 2, "stand " + best + " steps");
                Check("hunt (" + pn + "): and falls back below its rank share", hk.Min() < (int)Math.Round(n * (p.hunter == 0 ? 0.55 : 0.45)), "min " + hk.Min());
            }
            int open = c.g.AnchorNodes(RM_Anchor.Open)[0];
            bool openHeld = Enumerable.Range(0, RM_TerritoryKernel.StepsPerTurn).All(s =>
            { bool[] got = At(c, s, h1, Tune(0.55f)); return Enumerable.Range(0, n).Where(i => c.nodes[i] == open).All(i => !got[i]); });
            Check("hunt: the hunter's front starts from its own anchor (Sh'kaar always holds the Open room)", openHeld);
        }

        // ---------------- leader tide floods room by room from its anchor
        {
            Canvas c = Branch(3); bool prefix = true;
            for (long s = 0; s < RM_TerritoryKernel.StepsPerTurn; s += 2)
            {
                bool[] got = At(c, s, lt, Tune(0.6f));
                int far = Enumerable.Range(0, c.Count).Where(i => got[i]).Max(i => c.g.Distance(RM_Anchor.Core, c.nodes[i]));
                for (int i = 0; i < c.Count; i++) if (!got[i] && c.g.Distance(RM_Anchor.Core, c.nodes[i]) < far) prefix = false;
            }
            Check("leader tide: the leader holds every room nearer its anchor than its farthest fixture (it floods, never rotates)", prefix);
            var p = Enumerable.Range(0, c.Count).Reverse().ToArray();
            Canvas d = new Canvas { g = c.g };
            foreach (int i in p) { d.ids.Add(c.ids[i]); d.nodes.Add(c.nodes[i]); d.x.Add(c.x[i]); d.z.Add(c.z[i]); d.rooms.Add(c.rooms[i]); }
            bool same = true;
            for (long s = 0; s < 60; s += 7)
            {
                bool[] a = At(c, s, lt, Tune(0.6f, 0.2f)), b = At(d, s, lt, Tune(0.6f, 0.2f));
                for (int j = 0; j < p.Length; j++) if (b[j] != a[p[j]]) same = false;
            }
            Check("leader tide: input order never changes who holds a fixture", same);
        }

        // ---------------- degenerate canvases fall back to the wedge exactly
        {
            Canvas one = Chain(1, 8), c = Chain(5, 3);
            var sameRoom = new Canvas { g = c.g };
            for (int i = 0; i < 9; i++) { sameRoom.ids.Add(500 + i); sameRoom.nodes.Add(2); sameRoom.x.Add(i); sameRoom.z.Add(i % 3); sameRoom.rooms.Add(3); }
            bool eq = true;
            foreach (Canvas k in new[] { one, sameRoom })
                for (long s = 0; s < 240; s += 11)
                {
                    bool[] a = At(k, s, p1, Tune()), w = RM_TerritoryKernel.Allocate(k.ids, k.x, k.z, s, 12345, Tune());
                    if (!a.SequenceEqual(w)) eq = false;
                }
            bool[] nullG = RM_TerritoryShapes.Allocate(c.ids, c.x, c.z, c.nodes, null, 9, 12345, Tune(), p1);
            Check("degenerate: one room, every fixture in one room, or no graph runs the wedge exactly", eq
                  && nullG.SequenceEqual(RM_TerritoryKernel.Allocate(c.ids, c.x, c.z, 9, 12345, Tune()))
                  && !RM_TerritoryShapes.RunsAsTide(p1, sameRoom.nodes, c.g) && RM_TerritoryShapes.RunsAsTide(p1, c.nodes, c.g));
            bool wedgePlan = true;
            for (long s = 0; s < 240; s += 13)
                if (!At(c, s, e2, Tune()).SequenceEqual(RM_TerritoryKernel.Allocate(c.ids, c.x, c.z, s, 12345, Tune()))) wedgePlan = false;
            Check("a wedge plan is the old wedge allocation, bit for bit (no signature = the shipped behaviour)", wedgePlan);
        }

        // ---------------- the share clock
        {
            bool mono = true, bounded = true;
            foreach (int hunter in new[] { -1, 0, 1 })
                foreach (int salt in new[] { 0, 3, 4242 })
                {
                    var sh = Enumerable.Range(0, 240).Select(s => RM_TerritoryShapes.Share(s, salt, 0.6f, hunter)).ToArray();
                    if (sh.Any(v => v < RM_TerritoryShapes.MinTideShare - 1e-9 || v > RM_TerritoryKernel.MaxLeadShare + 1e-9)) bounded = false;
                    int turns = 0;
                    for (int i = 0; i < 240; i++)
                    {
                        double a = sh[(i + 239) % 240], b = sh[i], c2 = sh[(i + 1) % 240];
                        if ((b > a + 1e-12 && b > c2 + 1e-12) || (b < a - 1e-12 && b < c2 - 1e-12)) turns++;
                    }
                    if (turns > 2) mono = false;
                }
            Check("share clock: within [0.2, 0.8] and one rise, one fall a turn (so at most two hand-overs per fixture)", mono && bounded);
            Check("share clock: steps a whole turn apart are identical", RM_TerritoryShapes.Share(17, 9, 0.6f, 0) == RM_TerritoryShapes.Share(17 + 240, 9, 0.6f, 0)
                  && RM_TerritoryShapes.Share(-3, 9, 0.6f, -1) == RM_TerritoryShapes.Share(237, 9, 0.6f, -1));
            Check("TideCount keeps both sides with two or more fixtures", RM_TerritoryShapes.TideCount(2, 0.8) == 1 && RM_TerritoryShapes.TideCount(2, 0.2) == 1
                  && RM_TerritoryShapes.TideCount(10, 0.8) == 8 && RM_TerritoryShapes.TideCount(1, 0.5) == 1 && RM_TerritoryShapes.TideCount(0, 0.5) == 0);
        }
    }
}
