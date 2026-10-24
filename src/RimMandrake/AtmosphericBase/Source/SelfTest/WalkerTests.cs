// Selftest for build step 7, the walkers (RM_PatternWalkers.cs: PROCESSION, COIL, TELL, COUNT), kernel only.
// REAL, compiled from production source; layers are read from XML by PatternTests' reflection loader.
// NOT covered: the drawn glow between fixtures (no drawn layer exists; drawnInBlack is checked to change nothing).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.AtmosphericBase;

internal static class WalkerTests
{
    private static void Check(string name, bool ok, string detail = "") => Program.Check(name, ok, detail);

    private const string Pal4 = "<li>(0,0,0,0)</li><li>(26,10,4,0)</li><li>(64,26,8,0)</li><li>(205,98,24,0)</li>";

    private static RM_RoomFacts R(int id, bool th = false) => new RM_RoomFacts { id = id, cells = 20, threshold = th };
    private static KeyValuePair<int, int> D(int a, int b) => new KeyValuePair<int, int>(a, b);

    /// <summary>A chain of `rooms` rooms (room 1 is the threshold), `per` fixtures in each, laid out left to right.</summary>
    private static void Chain(int rooms, int per, out RM_RoomGraph g, out RM_FixtureSet f)
    {
        var rs = new List<RM_RoomFacts>(); var ds = new List<KeyValuePair<int, int>>();
        for (int i = 1; i <= rooms; i++) { rs.Add(R(i, i == 1)); if (i > 1) ds.Add(D(i - 1, i)); }
        g = RM_RoomGraph.Build(rs, ds);
        var e = new List<int>(); var r = new List<int>(); var x = new List<float>(); var z = new List<float>();
        for (int i = 0; i < rooms * per; i++) { e.Add(5000 + (i * 7919) % 9973); r.Add(1 + i / per); x.Add(i * 2f); z.Add((i % 2) * 1f); }
        f = new RM_FixtureSet(e, r, x, z);
    }

    private static RM_SchemeData Layer(string li, string under = "") =>
        PatternTests.One("<layers>" + under + "<li>" + li + "</li></layers>", Pal4);

    private static int[] Snap(RM_SchemeData s, RM_RoomGraph g, RM_FixtureSet f, double t)
    {
        var v = new int[f.Count];
        for (int k = 0; k < f.Count; k++)
        {
            RM_PatternCtx c = RM_PatternCtx.Of(f.ids[k], f.room[k], g, f);
            v[k] = RM_PatternEvaluator.Index(s, ref c, t, false);
        }
        return v;
    }

    private static int Lit(int[] v, int baseline = 0) => v.Count(x => x != baseline);

    private static Func<int, RM_PatternCtx> CtxOf(RM_RoomGraph g, RM_FixtureSet f) =>
        r => { int k = r % f.Count; return RM_PatternCtx.Of(f.ids[k], f.room[k], g, f); };

    private static void Procession()
    {
        Chain(5, 3, out RM_RoomGraph g, out RM_FixtureSet f);
        RM_WalkMap w = RM_WalkMap.For(g, f, RM_Anchor.Threshold);
        // the tour (anchored at the chain's end room, so depth-first order has no backtrack): each fixture once; every hop of a lap stays in its room or crosses one door, except the lap's wrap
        int nonAdj = 0;
        for (int i = 0; i < w.tour.Length; i++)
        {
            int a = w.tour[i], b = w.tour[(i + 1) % w.tour.Length];
            int na = g.Node(f.room[a]), nbn = g.Node(f.room[b]);
            if (na != nbn && !g.adj[na].Contains(nbn)) nonAdj++;
        }
        Check("S7 procession tour: every fixture exactly once", w.tour.Distinct().Count() == f.Count && w.tour.Length == f.Count);
        Check("S7 procession walk on a chain: every hop stays in the room or crosses one door, except the lap's wrap", nonAdj == 1, "non-adjacent hops " + nonAdj);

        foreach (int k in new[] { 1, 2, 3 })
        {
            RM_SchemeData s = Layer("<primitive>Procession</primitive><entries>1~3</entries><heads>" + k + "</heads><dwell>2</dwell><hop>0.6</hop>",
                                    "<li><primitive>Steady</primitive><entries>0</entries></li>");
            bool ok = true; string why = "";
            for (int st = 0; st < 60 && ok; st++)
            {
                int inDwell = Lit(Snap(s, g, f, st * 2.6 + 1.0)), inHop = Lit(Snap(s, g, f, st * 2.6 + 2.3));
                if (inDwell != k || inHop != 0) { ok = false; why = "step " + st + " dwell lit " + inDwell + " hop lit " + inHop; }
            }
            Check("S7 procession heads=" + k + ": exactly " + k + " lamps lit in each dwell, none in the hop (no overlap)", ok, why);
        }
        {
            RM_SchemeData s = Layer("<primitive>Procession</primitive><entries>1~3</entries><dwell>2</dwell><hop>0.6</hop><overlap>true</overlap><anchor>Threshold</anchor>",
                                    "<li><primitive>Steady</primitive><entries>0</entries></li>");
            bool ok = true;
            for (int st = 0; st < 40; st++)
            {
                int[] a = Snap(s, g, f, st * 2.6 + 1.0), b = Snap(s, g, f, st * 2.6 + 2.3), c = Snap(s, g, f, (st + 1) * 2.6 + 0.5);
                // in the hop the next lamp is already lit while the last still is
                bool both = Lit(b) == 2 && Enumerable.Range(0, f.Count).All(i => b[i] == 0 || a[i] != 0 || c[i] != 0);
                if (Lit(a) != 1 || !both) ok = false;
            }
            Check("S7 procession overlap: one lamp in the dwell; in the hop the next is lit before the last goes out", ok);
            var seen = new HashSet<int>(); int jumps = 0;
            int prev = -1;
            for (int st = 0; st <= f.Count; st++)
            {
                int[] a = Snap(s, g, f, st * 2.6 + 1.0);
                int head = Array.FindIndex(a, x => x == 3);
                if (prev >= 0)
                {
                    int na = g.Node(f.room[prev]), nb = g.Node(f.room[head]);
                    if (na != nb && !g.adj[na].Contains(nb)) jumps++;
                }
                prev = head; seen.Add(head);
            }
            Check("S7 procession walk: over a lap consecutive head lamps are graph-adjacent (same room or one door), bar the one wrap", jumps == 1 && seen.Count == f.Count, "jumps " + jumps);
        }
        {
            RM_SchemeData s = Layer("<primitive>Procession</primitive><entries>1~3</entries><heads>3</heads><step>Jump</step><dwell>1</dwell><hop>0.5</hop>");
            bool ok = true; int moved = 0; int[] last = null;
            for (int st = 0; st < 200; st++)
            {
                int[] a = Snap(s, g, f, st * 1.5 + 0.5);
                if (Lit(a, 0) != 3) ok = false;
                if (last != null && !a.SequenceEqual(last)) moved++;
                last = a;
            }
            Check("S7 procession jump heads=3: exactly 3 distinct lamps every step, and they move", ok && moved > 150, "moved " + moved);
        }
        {
            RM_SchemeData s = Layer("<primitive>Procession</primitive><entries>1~3</entries><tail>2</tail><dwell>1</dwell><hop>0.5</hop>",
                                    "<li><primitive>Steady</primitive><entries>0</entries></li>");
            int[] a = Snap(s, g, f, 10 * 1.5 + 0.5);
            var vals = a.Where(x => x != 0).OrderByDescending(x => x).ToArray();
            Check("S7 procession tail=2: head at hi, the two lamps behind it one and two entries lower", vals.SequenceEqual(new[] { 3, 2, 1 }), string.Join(",", vals));
            RM_SchemeData p = Layer("<primitive>Procession</primitive><entries>1~3</entries><pair>true</pair><dwell>1</dwell><hop>0.5</hop>",
                                    "<li><primitive>Steady</primitive><entries>0</entries></li>");
            Check("S7 procession pair: two lamps lit as one head", Lit(Snap(p, g, f, 4 * 1.5 + 0.5)) == 2);
            RM_SchemeData tr = Layer("<primitive>Procession</primitive><entries>1~3</entries><trace>1</trace><dwell>1</dwell><hop>0.5</hop>",
                                     "<li><primitive>Steady</primitive><entries>0</entries></li>");
            var lits = Enumerable.Range(0, f.Count + 2).Select(st => Lit(Snap(tr, g, f, st * 1.5 + 0.5))).ToArray();
            bool grows = true;
            for (int st = 1; st < f.Count; st++) if (lits[st] != lits[st - 1] + 1) grows = false;
            Check("S7 procession trace +1: the lamps a head passed stay up for the lap, then the lap starts dark",
                  grows && lits[0] == 1 && lits[f.Count] == 1, string.Join(",", lits));
            RM_SchemeData dr = Layer("<primitive>Procession</primitive><entries>1~3</entries><tail>2</tail><dwell>1</dwell><hop>0.5</hop><drawnInBlack>true</drawnInBlack>",
                                     "<li><primitive>Steady</primitive><entries>0</entries></li>");
            bool same = true;
            for (int st = 0; st < 50; st++) if (!Snap(dr, g, f, st * 0.37).SequenceEqual(Snap(s, g, f, st * 0.37))) same = false;
            Check("S7 procession drawnInBlack: no drawn layer is built, the flag changes no grid index", same && !RM_PatternKernel.DrawnLayerBuilt);
            PatternTests.NextChangeAgrees("S7 procession tail+overlap", Layer("<primitive>Procession</primitive><entries>1~3</entries><tail>2</tail><overlap>true</overlap><dwell>1.3</dwell><hop>0.4</hop>"),
                                          false, 200, 0.05, 6, CtxOf(g, f));
            PatternTests.NextChangeAgrees("S7 procession jump pair", Layer("<primitive>Procession</primitive><entries>1~3</entries><step>Jump</step><heads>2</heads><pair>true</pair><dwell>0.9</dwell><hop>0.3</hop>"),
                                          false, 200, 0.05, 6, CtxOf(g, f));
        }
        {
            // L8: the true-black ember procession -- a black base with one ember walking at the dim nonzero entry
            RM_SchemeData s = Layer("<primitive>Procession</primitive><entries>1~1</entries><overlap>true</overlap><dwell>2</dwell><hop>0.6</hop>",
                                    "<li><primitive>Steady</primitive><entries>0</entries></li>");
            var rng = new Random(3); int still = 0; bool emberOnly = true;
            for (int i = 0; i < 200; i++)
            {
                double t0 = rng.NextDouble() * 3000;
                int[] a = Snap(s, g, f, t0);
                if (a.Any(x => x > 1)) emberOnly = false;
                bool moved = false;
                for (double t = t0 + 0.1; t <= t0 + 4.0 && !moved; t += 0.1) if (!Snap(s, g, f, t).SequenceEqual(a)) moved = true;
                if (!moved) still++;
            }
            Check("S7 ember procession in true black: only entries 0 and 1 (the dim ember) and something moves in every 4 s window (L8)", still == 0 && emberOnly, "still windows " + still);
        }
        {
            RM_SchemeData s = Layer("<primitive>Procession</primitive><entries>2~2</entries><graph>Rooms</graph><dwell>1</dwell><hop>0.5</hop>",
                                    "<li><primitive>Steady</primitive><entries>0</entries></li>");
            int[] a = Snap(s, g, f, 2 * 1.5 + 0.5);
            var rooms = Enumerable.Range(0, f.Count).Where(i => a[i] != 0).Select(i => f.room[i]).Distinct().ToArray();
            Check("S7 procession graph=Rooms: a head lights its whole room (3 lamps, one room)", Lit(a) == 3 && rooms.Length == 1);
        }
        Check("S7 procession Errors: heads 0, trace with Jump, negative tail are refused",
              PatternTests.HasError(Layer("<primitive>Procession</primitive><heads>0</heads>"), "heads")
              && PatternTests.HasError(Layer("<primitive>Procession</primitive><trace>1</trace><step>Jump</step>"), "trace needs step Walk")
              && PatternTests.HasError(Layer("<primitive>Procession</primitive><tail>-1</tail>"), "tail"));
    }

    private static void Coil()
    {
        Chain(6, 5, out RM_RoomGraph g, out RM_FixtureSet f);
        RM_SchemeData s = Layer("<primitive>Coil</primitive><entries>1~3</entries><coils>3</coils><hop>0.3</hop><length>4</length><turnChance>0.3</turnChance>");
        var seq = new List<string>();
        for (int st = 0; st < 400; st++) seq.Add(string.Join(",", Snap(s, g, f, st * 0.3 + 0.1)));
        var windows = new HashSet<string>(); bool repeat = false;
        for (int st = 0; st + 8 <= seq.Count; st++) if (!windows.Add(string.Join("|", seq.GetRange(st, 8)))) repeat = true;
        Check("S7 coil: no 8-step window of the whole figure repeats in 400 steps (never exactly repeats)", !repeat);
        RM_WalkMap w = RM_WalkMap.For(g, f, RM_Anchor.Core);
        RM_Layer l = s.layers[0];
        int crossings = 0; bool flare = true;
        for (int st = 0; st < 3000; st++)
        {
            int[][] tr = RM_CoilPrimitive.Trails(l, f, w, st);
            for (int k = 0; k < f.Count; k++)
            {
                int under = tr.Count(c => c.Contains(k));
                if (under < 2) continue;
                crossings++;
                RM_PatternCtx c2 = RM_PatternCtx.Of(f.ids[k], f.room[k], g, f);
                if (RM_PatternEvaluator.Index(s, ref c2, st * 0.3 + 0.1, false) != 3) flare = false;
            }
        }
        Check("S7 coil: a lamp under two coils flares to max (hi)", crossings > 0 && flare, "crossings " + crossings);
        PatternTests.NextChangeAgrees("S7 coil", s, false, 120, 0.05, 2, CtxOf(g, f));
        foreach (int T in new[] { 200, 1000 })
        {
            Chain(T / 10, 10, out RM_RoomGraph gt, out RM_FixtureSet ft);
            RM_SchemeData sc = Layer("<primitive>Coil</primitive><entries>1~3</entries><coils>3</coils><hop>0.3</hop><length>4</length>");
            int[] prev = Snap(sc, gt, ft, 0.1);
            int worst = 0;
            var sw = System.Diagnostics.Stopwatch.StartNew();
            for (int st = 1; st < 100; st++)
            {
                int[] a = Snap(sc, gt, ft, st * 0.3 + 0.1);
                int ch = 0; for (int i = 0; i < a.Length; i++) if (a[i] != prev[i]) ch++;
                worst = Math.Max(worst, ch); prev = a;
            }
            sw.Stop();
            Check("S7 coil T=" + T + ": at most coils x length x 2 = 24 changes per step, 100 full passes under 2 s (" + sw.ElapsedMilliseconds + " ms)",
                  worst <= 24 && sw.ElapsedMilliseconds < 2000, "worst " + worst);
        }
    }

    private static void CoilTwoMaps()
    {
        Chain(6, 5, out RM_RoomGraph g, out RM_FixtureSet f);
        Chain(3, 4, out RM_RoomGraph g2, out RM_FixtureSet f2);
        const string coil = "<primitive>Coil</primitive><entries>1~3</entries><coils>3</coils><hop>0.3</hop><length>4</length><turnChance>0.3</turnChance>";
        RM_Layer shared = Layer(coil).layers[0], solo = Layer(coil).layers[0];
        RM_WalkMap w = RM_WalkMap.For(g, f, RM_Anchor.Core), w2 = RM_WalkMap.For(g2, f2, RM_Anchor.Core);
        int before = RM_CoilPrimitive.Restarts;
        bool same = true;
        for (int st = 0; st < 120; st++)
        {
            int[] a = RM_CoilPrimitive.Trails(solo, f, w, st).SelectMany(x => x).ToArray();
            RM_CoilPrimitive.Trails(shared, f2, w2, st / 3);     // the other map, on the same layer, at an earlier step
            int[] b = RM_CoilPrimitive.Trails(shared, f, w, st).SelectMany(x => x).ToArray();
            if (!a.SequenceEqual(b)) same = false;
        }
        int restarts = RM_CoilPrimitive.Restarts - before;
        Check("S7 coil: two maps sharing one layer, alternating, neither restarts the other and the figure is undisturbed",
              same && restarts == 3, "restarts " + restarts + " (want 3: solo, shared on each map)");
    }

    private static void Tell()
    {
        bool ok = true; string why = "";
        for (int T = 0; T <= 25; T++)
        {
            if (T == 0) { if (RM_TellPrimitive.CapFor(new RM_Layer(), 0) != 0) ok = false; continue; }
            Chain(1, T, out RM_RoomGraph g, out RM_FixtureSet f);
            RM_SchemeData s = Layer("<primitive>Tell</primitive><entries>3</entries><interval>10</interval><beat>1</beat>",
                                    "<li><primitive>Steady</primitive><entries>1</entries></li>");
            int want = T >= 8 ? 1 : 0, most = 0;
            for (double t = 0; t < 400; t += 0.25) most = Math.Max(most, Snap(s, g, f, t).Count(x => x == 3));
            if (most != want) { ok = false; why += " T=" + T + " most=" + most; }
        }
        Check("S7 tell integer cap for 0-25 fixtures: exactly 1 stray lamp at once when T >= 8, never one below 8", ok, why);
        Chain(2, 10, out RM_RoomGraph g2, out RM_FixtureSet f2);
        RM_SchemeData s3 = Layer("<primitive>Tell</primitive><entries>3</entries><interval>10</interval><beat>1</beat><cap>3</cap>",
                                 "<li><primitive>Steady</primitive><entries>1</entries></li>");
        int most3 = 0; for (double t = 0; t < 400; t += 0.25) most3 = Math.Max(most3, Snap(s3, g2, f2, t).Count(x => x == 3));
        Check("S7 tell cap 3: three stray lamps at once at most, and they do appear", most3 == 3);
        Check("S7 tell Errors: cap 4 and a beat longer than the interval are refused",
              PatternTests.HasError(Layer("<primitive>Tell</primitive><cap>4</cap>"), "cap")
              && PatternTests.HasError(Layer("<primitive>Tell</primitive><interval>1</interval><beat>2</beat>"), "beat"));
        PatternTests.NextChangeAgrees("S7 tell", Layer("<primitive>Tell</primitive><entries>3</entries><interval>6</interval><beat>1</beat><cap>2</cap>"),
                                      false, 200, 0.05, 14, CtxOf(g2, f2));
    }

    private static void Count()
    {
        Chain(5, 3, out RM_RoomGraph g, out RM_FixtureSet f);
        RM_SchemeData sp = Layer("<primitive>Count</primitive><entries>3</entries><n>3</n><restEntry>1</restEntry>");
        int[] a = Snap(sp, g, f, 5);
        var markedRooms = Enumerable.Range(0, f.Count).Where(i => a[i] == 3).Select(i => f.room[i]).ToArray();
        Check("S7 count spread n=3: three marked lamps in three different rooms, the rest at restEntry",
              markedRooms.Length == 3 && markedRooms.Distinct().Count() == 3 && a.Count(x => x == 1) == f.Count - 3);
        RM_SchemeData pr = Layer("<primitive>Count</primitive><entries>3</entries><n>1</n><perRoom>true</perRoom>");
        int[] b = Snap(pr, g, f, 5);
        Check("S7 count perRoom n=1: one marked lamp in every room", Enumerable.Range(0, f.Count).Where(i => b[i] == 3).Select(i => f.room[i]).Distinct().Count() == 5
              && b.Count(x => x == 3) == 5);
        RM_SchemeData na = Layer("<primitive>Count</primitive><entries>3</entries><n>3</n><pick>NearestAnchor</pick><anchor>Threshold</anchor>");
        int[] c = Snap(na, g, f, 5);
        Check("S7 count nearestAnchor n=3: the threshold room's three lamps", Enumerable.Range(0, f.Count).Where(i => c[i] == 3).All(i => f.room[i] == 1)
              && c.Count(x => x == 3) == 3);
        bool steady = true;
        for (int k = 0; k < f.Count; k++)
        {
            RM_PatternCtx cx = RM_PatternCtx.Of(f.ids[k], f.room[k], g, f);
            if (!double.IsPositiveInfinity(RM_PatternEvaluator.NextChange(sp, ref cx, 12.5, false))) steady = false;
        }
        for (double t = 0; t < 600; t += 7.3) if (!Snap(sp, g, f, t).SequenceEqual(a)) steady = false;
        Check("S7 count at steady state: zero changes, NextChange Never for every lamp", steady);
        // membership: one more lamp moves at most one mark
        var e = f.ids.ToList(); var r = f.room.ToList(); var x = f.x.ToList(); var z = f.z.ToList();
        e.Add(99991); r.Add(3); x.Add(13f); z.Add(0f);
        var f2 = new RM_FixtureSet(e, r, x, z);
        int[] a2 = Snap(sp, g, f2, 5);
        var before = new HashSet<int>(Enumerable.Range(0, f.Count).Where(i => a[i] == 3).Select(i => f.ids[i]));
        var after = new HashSet<int>(Enumerable.Range(0, f2.Count).Where(i => a2[i] == 3).Select(i => f2.ids[i]));
        Check("S7 count: a lamp added moves at most one mark", after.Count == 3 && before.Except(after).Count() <= 1);
        RM_SchemeData ac = Layer("<primitive>Count</primitive><entries>3</entries><n>0</n><accumulate>true</accumulate><beat>8</beat><restEntry>0</restEntry>");
        var counts = Enumerable.Range(0, 10).Select(k => Snap(ac, g, f, k * 8 + 1).Count(v => v == 3)).ToArray();
        Check("S7 count accumulate beat 8 s: per room 0,1,2,3 marked then clear (5 rooms: 0,5,10,15,0,...)",
              counts.SequenceEqual(new[] { 0, 5, 10, 15, 0, 5, 10, 15, 0, 5 }), string.Join(",", counts));
        RM_SchemeData tb = Layer("<primitive>Count</primitive><entries>3</entries><n>1</n><perRoom>true</perRoom><tremble>true</tremble><restEntry>0</restEntry>");
        int k0 = Array.FindIndex(b, v => v == 3);
        RM_PatternCtx ck = RM_PatternCtx.Of(f.ids[k0], f.room[k0], g, f);
        int changes = 0, prev = RM_PatternEvaluator.Index(tb, ref ck, 0, false); var vals = new HashSet<int> { prev };
        for (double t = 0.01; t < 30; t += 0.01) { int v = RM_PatternEvaluator.Index(tb, ref ck, t, false); if (v != prev) changes++; prev = v; vals.Add(v); }
        Check("S7 count tremble: a marked lamp alternates two adjacent entries every 0.8-1.5 s", vals.SetEquals(new[] { 2, 3 }) && changes >= 19 && changes <= 38, "changes in 30 s " + changes);
        PatternTests.NextChangeAgrees("S7 count tremble+accumulate", Layer("<primitive>Count</primitive><entries>3</entries><n>0</n><accumulate>true</accumulate><tremble>true</tremble><beat>3</beat>"),
                                      false, 200, 0.02, 8, CtxOf(g, f));
        Check("S7 count Errors: markEntry outside the palette is refused", PatternTests.HasError(Layer("<primitive>Count</primitive><markEntry>4</markEntry>"), "markEntry"));
        int builds = RM_WalkMap.Builds;
        Snap(sp, g, f, 1); Snap(pr, g, f, 2);
        Check("S7 walk map: built once per (graph, fixtures, anchor), not per evaluation", RM_WalkMap.Builds == builds);
    }

    internal static void Run()
    {
        Procession();
        Coil();
        CoilTwoMaps();
        Tell();
        Count();
    }
}
