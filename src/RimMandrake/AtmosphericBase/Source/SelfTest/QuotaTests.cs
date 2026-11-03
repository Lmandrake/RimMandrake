// ATMOSPHERIC_BASE_HARDEN_SMALL_LAMP_COUNTS -- Q1 integer quotas swept 0..25, Q2 the hitch, Q3 the cost at
// 11 / 200 / 1000 fixtures, Q4 the travelling ember. Spec: design/RimMandrake/atmospheric_base_mod_definition.md §2.6a.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using RimMandrake.AtmosphericBase;

internal static class QuotaTests
{
    private static void Check(string name, bool ok, string detail = "") => Program.Check(name, ok, detail);

    internal static void Run()
    {
        Q1Sweep();
        Q2Hitch();
        Q3Measure();
        Q4Ember();
    }

    private static List<int> Ids(int n)
    {
        var l = new List<int>(n);
        for (int i = 0; i < n; i++) l.Add(1000 + 7 * i);
        return l;
    }

    // ---- Q1: tremor and flasher quotas for every group size 0..25
    private static void Q1Sweep()
    {
        float[] shares = { float.NaN, -1f, 0f, 0.001f, 0.01f, 0.04f, 0.05f, 0.099f, 0.1f, 0.25f, 0.5f, 1f, 3f };
        string bad = "";
        for (int n = 0; n <= 25; n++)
            foreach (float f in shares)
            {
                int c = RM_Quota.TremorCap(n, f);
                int pm = Math.Min(RM_Quota.TremorCeilingPerMille, RM_Quota.PerMille(f));
                if (c < 0 || c * 10 > n) bad += " over:" + n + "@" + f + "=" + c;                       // never above a tenth
                if (n >= RM_Quota.TremorMinFixtures && pm > 0 && c < 1) bad += " zero:" + n + "@" + f;   // never silently zero
                if (n < RM_Quota.TremorMinFixtures && c != 0) bad += " small:" + n + "@" + f + "=" + c;  // stated: off below ten
                if (pm == 0 && c != 0) bad += " noshare:" + n + "@" + f;
                if (c > ((long)n * pm + 999) / 1000) bad += " abovewant:" + n + "@" + f;
            }
        Check("Q1 tremor cap, n = 0..25 x 13 shares: never above floor(n/10), at least one from 10 fixtures when the share > 0, 0 below 10", bad == "", bad);
        Check("Q1 tremor cap: the review's cases -- 4% of 11 is 1 (not 0.44 floored to 0), 4% of 9 is 0 (one would be 11%), 4% of 300 is 12",
              RM_Quota.TremorCap(11, 0.04f) == 1 && RM_Quota.TremorCap(9, 0.04f) == 0 && RM_Quota.TremorCap(300, 0.04f) == 12
              && RM_Quota.TremorCap(25, 0.04f) == 1 && RM_Quota.TremorCap(25, 0.10f) == 2 && RM_TremorKernel.InstantCap(11, 0.04f) == 1);

        // the cap holds on the real Assign, with every fixture wanting to flicker
        var tu = new RM_TremorTuning { cap = 3, slotSeconds = 4f, flickerSeconds = 1f, oneIn = 1, maxFraction = 0.10f };
        string abad = "";
        for (int n = 0; n <= 25; n++)
        {
            List<int> ids = Ids(n);
            var src = new List<RM_TremorSource>
            {
                new RM_TremorSource { paletteCount = 3, salt = 11, members = ids },
                new RM_TremorSource { paletteCount = 3, salt = 12, members = ids },
            };
            int most = 0;
            for (double t = 0; t < 40; t += 0.05)
            {
                int k = RM_TremorKernel.Assign(src, t, n, tu).Count;
                if (k > most) most = k;
            }
            int cap = RM_Quota.TremorCap(n, 0.10f);
            if (most > cap || most * 10 > n) abad += " n" + n + ":" + most + ">" + cap;
            if (n >= 10 && most < 1) abad += " n" + n + ":never";
        }
        Check("Q1 tremor Assign, n = 0..25, every fixture eager: the most flickering at once never exceeds the cap or a tenth, and is not zero from 10", abad == "", abad);

        string fbad = "";
        for (int n = 0; n <= 25; n++)
            for (int req = -1; req <= 6; req++)
            {
                List<int> ids = Ids(n);
                int k = RM_SchemeKernel.PickFlashers(ids, req).Count;
                if (k != RM_Quota.FlasherCap(n, req)) fbad += " mismatch:" + n + "/" + req;
                if (n >= 1 && k >= n) fbad += " whole:" + n + "/" + req;                              // never the whole group
                if (n >= RM_Quota.FlasherMinFixtures && req >= 1 && k < 1) fbad += " zero:" + n + "/" + req; // never silently zero
                if (k > Math.Max(1, n / 10)) fbad += " overtenth:" + n + "/" + req + "=" + k;
                if (k > Math.Max(0, req)) fbad += " overask:" + n + "/" + req;
            }
        Check("Q1 flashers, n = 0..25 x asked -1..6: at least one when asked and n >= 2, never the whole group, never above max(1, floor(n/10)) or the ask", fbad == "", fbad);
        Check("Q1 flashers: one lamp never flashes (max(1,10%) would have made it 100%); 11 lamps asking 2 get 1; 25 asking 2 get 2",
              RM_SchemeKernel.PickFlashers(Ids(1), 1).Count == 0 && RM_SchemeKernel.PickFlashers(Ids(11), 2).Count == 1
              && RM_SchemeKernel.PickFlashers(Ids(25), 2).Count == 2 && RM_SchemeKernel.PickFlashers(Ids(2), 5).Count == 1);
    }

    // a small moving scheme: a three-entry Lamplight-like palette whose mass steps fast enough to show transitions
    private static RM_SchemeData Mover(int flashers)
    {
        return PatternTests.One("<massPeriodSeconds>6</massPeriodSeconds><flasherCount>" + flashers
                                + "</flasherCount><flasherPeriodSeconds>0.5</flasherPeriodSeconds>");
    }

    private static readonly RM_TremorTuning Tremor = new RM_TremorTuning { cap = 3, slotSeconds = 30f, flickerSeconds = 0.8f, oneIn = 4, maxFraction = 0.04f };

    /// <summary>The kernel half of one compositor evaluation: tremor, flashers, the pattern, changed-only writes.
    /// Returns the writes (each one dirties the glow grid at that fixture).</summary>
    private static int EvalOnce(RM_SchemeData s, List<int> ids, HashSet<int> flash, List<RM_TremorSource> trem, RM_ChangeTracker tr, double t)
    {
        Dictionary<int, KeyValuePair<int, int>> at = RM_TremorKernel.Assign(trem, t, ids.Count, Tremor);
        int w = 0;
        for (int i = 0; i < ids.Count; i++)
        {
            int id = ids[i];
            long v = at.TryGetValue(id, out KeyValuePair<int, int> kv)
                ? RM_ChangeTracker.Pack(1 + kv.Key, kv.Value)
                : RM_ChangeTracker.Pack(0, RM_SchemeKernel.PaletteIndex(s, id, i / 8, t, flash.Contains(id)));
            if (tr.Want(id, v)) w++;
        }
        return w;
    }

    private static List<RM_TremorSource> Sources(List<int> ids) => new List<RM_TremorSource>
    {
        new RM_TremorSource { paletteCount = 3, salt = 101, members = ids },
        new RM_TremorSource { paletteCount = 4, salt = 102, members = ids },
        new RM_TremorSource { paletteCount = 3, salt = 103, members = ids },
    };

    private static long State(RM_SchemeData s, List<int> ids, HashSet<int> flash, List<RM_TremorSource> trem, double t, int i)
    {
        Dictionary<int, KeyValuePair<int, int>> at = RM_TremorKernel.Assign(trem, t, ids.Count, Tremor);
        int id = ids[i];
        return at.TryGetValue(id, out KeyValuePair<int, int> kv) ? RM_ChangeTracker.Pack(1 + kv.Key, kv.Value)
                                                                 : RM_ChangeTracker.Pack(0, RM_SchemeKernel.PaletteIndex(s, id, i / 8, t, flash.Contains(id)));
    }

    // ---- Q2: after a long frame, one recompute; no burst of replayed transitions
    private static void Q2Hitch()
    {
        Check("Q2 hitch threshold: a 30 s gap is a hitch, an ordinary 0.1 s evaluation step is not, the first evaluation never is",
              RM_Hitch.IsHitch(100, 130) && !RM_Hitch.IsHitch(100, 100.1) && !RM_Hitch.IsHitch(-1, 50) && RM_Hitch.MaxDelaySeconds >= 0.4);
        RM_SchemeData s = Mover(2);
        List<int> ids = Ids(200);
        HashSet<int> flash = RM_SchemeKernel.PickFlashers(ids, s.flasherCount);
        List<RM_TremorSource> trem = Sources(ids);
        var tr = new RM_ChangeTracker();
        for (double t = 90; t <= 100.0001; t += 0.1) EvalOnce(s, ids, flash, trem, tr, t);
        // what a replay would have written: every transition inside the gap, at the 0.1 s evaluation step
        int replay = 0;
        var shadow = new Dictionary<int, long>();
        for (int i = 0; i < ids.Count; i++) shadow[ids[i]] = State(s, ids, flash, trem, 100, i);
        for (double t = 100.1; t <= 130.0001; t += 0.1)
            for (int i = 0; i < ids.Count; i++)
            {
                long v = State(s, ids, flash, trem, t, i);
                if (shadow[ids[i]] != v) { replay++; shadow[ids[i]] = v; }
            }
        int differ = 0;
        for (int i = 0; i < ids.Count; i++) if (State(s, ids, flash, trem, 100, i) != State(s, ids, flash, trem, 130, i)) differ++;
        int w = EvalOnce(s, ids, flash, trem, tr, 130);
        Check("Q2 hitch: the 30 s gap is ONE recompute -- writes == fixtures whose state differs between the two instants, <= one per fixture, a tenth or less of what replaying the gap would write",
              w == differ && w <= ids.Count && replay >= 10 * Math.Max(1, w), "writes=" + w + " differ=" + differ + " replay=" + replay);
        // an overdue flicker is dropped: what shows at 130 is exactly what Assign(130) says, nothing from inside the gap
        Dictionary<int, KeyValuePair<int, int>> now = RM_TremorKernel.Assign(trem, 130, ids.Count, Tremor);
        int stale = 0;
        for (int i = 0; i < ids.Count; i++)
        {
            tr.Shows(ids[i], out long v);
            bool tremShown = (v >> 8) != 0;
            if (tremShown != now.ContainsKey(ids[i])) stale++;
        }
        Check("Q2 hitch: no flicker from inside the gap survives it (the shown tremor set is exactly the current one)", stale == 0, "stale=" + stale);
        int again = EvalOnce(s, ids, flash, trem, tr, 130);
        Check("Q2 hitch: re-evaluating the same instant writes nothing (no deferred catch-up)", again == 0, "again=" + again);
    }

    // ---- Q3: the kernel's cost and the regrid count at 11 / 200 / 1000 fixtures
    private static void Q3Measure()
    {
        AppDomain.MonitoringIsEnabled = true;
        foreach (int n in new[] { 11, 200, 1000 })
        {
            RM_SchemeData s = Mover(2);
            List<int> ids = Ids(n);
            HashSet<int> flash = RM_SchemeKernel.PickFlashers(ids, s.flasherCount);
            List<RM_TremorSource> trem = Sources(ids);
            var tr = new RM_ChangeTracker();
            int initial = EvalOnce(s, ids, flash, trem, tr, 0);
            const int evals = 600;   // 60 s of real time at 60 fps, one evaluation every 6 frames
            var sw = new Stopwatch();
            double maxMs = 0, sumMs = 0;
            long writes = 0; int burst = 0, burstAt = 0;
            long a0 = AppDomain.CurrentDomain.MonitoringTotalAllocatedMemorySize;
            for (int k = 1; k <= evals; k++)
            {
                double t = k * 0.1;
                sw.Restart();
                int w = EvalOnce(s, ids, flash, trem, tr, t);
                sw.Stop();
                double ms = sw.Elapsed.TotalMilliseconds;
                sumMs += ms; if (ms > maxMs) maxMs = ms;
                writes += w; if (w > burst) { burst = w; burstAt = k; }
            }
            long alloc = AppDomain.CurrentDomain.MonitoringTotalAllocatedMemorySize - a0;
            sw.Restart();
            int hitch = EvalOnce(s, ids, flash, trem, tr, evals * 0.1 + 30);
            sw.Stop();
            Console.WriteLine(string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "MEASURE n={0} evals={1} initial_writes={2} mean_eval_ms={3:F4} max_eval_ms={4:F4} writes_per_eval={5:F2} regrid_dirties_per_s={6:F1} max_burst={7} (eval {8}) alloc_bytes_per_eval={9} flashers={10} tremor_cap={11} hitch_writes={12} hitch_ms={13:F4}",
                n, evals, initial, sumMs / evals, maxMs, writes / (double)evals, writes / 60.0, burst, burstAt, alloc / evals, flash.Count,
                RM_Quota.TremorCap(n, Tremor.maxFraction), hitch, sw.Elapsed.TotalMilliseconds));
            Check("Q3 n=" + n + ": no evaluation and no hitch writes more than one per fixture", burst <= n && hitch <= n && initial == n);
        }
    }

    // ---- Q4: the dark room's ember travels; one lamp blinks; an empty room holds nothing black
    private static void Q4Ember()
    {
        var ids = new List<int> { 50, 51, 52, 53, 54 };
        var rooms = new List<int> { 7, 7, 7, 7, 7 };
        var owned = new List<bool> { true, true, true, true, true };
        var trem = new List<bool> { false, false, false, false, false };
        var xs = new List<float> { 4, 0, 3, 1, 2 };   // sweep order by x: 51, 53, 54, 52, 50
        var zs = new List<float> { 0, 0, 0, 0, 0 };
        var order = new List<int> { 51, 53, 54, 52, 50 };
        var hushed = new HashSet<int> { 7 };
        var seen = new HashSet<int>();
        int prev = -1; bool neighbours = true, movesEveryStep = true, stillWindow = false;
        double lastChange = 0;
        for (double t = 0; t < 60; t += 0.25)
        {
            int k = RM_Hush.PickKeepers(ids, rooms, owned, trem, hushed, t, xs, zs)[7];
            seen.Add(k);
            if (prev >= 0 && k != prev)
            {
                if (Math.Abs(order.IndexOf(k) - order.IndexOf(prev)) != 1) neighbours = false;
                lastChange = t;
            }
            if (t - lastChange > RM_Ember.StepSeconds + 1e-9) stillWindow = true;
            if (prev >= 0 && RM_Ember.Step(t) != RM_Ember.Step(t - 0.25) && k == prev) movesEveryStep = false;
            prev = k;
        }
        Check("Q4 ember: in a 5-lamp dark room the ember visits every lamp, moves every step, never sits still longer than a step, and each move is to a neighbour in sweep order",
              seen.Count == 5 && movesEveryStep && !stillWindow && neighbours,
              "seen=" + seen.Count + " every=" + movesEveryStep + " still=" + stillWindow + " nb=" + neighbours);
        Check("Q4 ember: the travelling keeper still never picks a tremor lamp or an unowned one",
              !RM_Hush.PickKeepers(ids, rooms, new List<bool> { true, false, true, true, true }, new List<bool> { false, false, true, false, false }, hushed, 100, xs, zs)
                   .ContainsValue(51)
              && RM_Hush.PickKeepers(ids, rooms, owned, trem, new HashSet<int>(), 0, xs, zs).Count == 0);
        // one lamp: alternates ember / black every step, so the room still changes
        var one = new List<int> { 9 };
        bool alternates = RM_Ember.Keeper(one, 0) == 9 && RM_Ember.Keeper(one, RM_Ember.StepSeconds) == -1 && RM_Ember.Keeper(one, 2 * RM_Ember.StepSeconds) == 9;
        Check("Q4 ember: a one-lamp dark room blinks ember / black each step (going out is the change)", alternates);
        // empty room: every lamp a tremor flicker (or unowned) -> no keeper, and none of its lamps reaches the dark
        var allTrem = new List<bool> { true, true, true, true, true };
        Check("Q4 ember: an EMPTY dark room (no holdable lamp) has no keeper, and so no lamp of it is driven black by the hush",
              !RM_Hush.PickKeepers(ids, rooms, owned, allTrem, hushed, 3, xs, zs).ContainsKey(7) && RM_Ember.Keeper(new List<int>(), 5) == -1);
        // the ember the keeper holds is lit: Apply on the keeper returns the held (lowest lit) entry, the rest black
        RM_SchemeData dark = PatternTests.One("", "<li>(0,0,0,0)</li><li>(0,0,0,0)</li><li>(40,16,6,0)</li><li>(205,98,24,0)</li>");
        int held = RM_Hush.Mid(dark);
        Check("Q4 ember: the keeper shows a lit entry in a dark hush and the others go black",
              held == 2 && RM_Hush.Apply(3, held, 1, true, true) == 2 && RM_Hush.Apply(3, held, 1, true, false) == 0);
        Check("Q4 ember: the bounce walk is 0,1,2,3,2,1,0,1 for four stops", RM_Ember.Bounce(0, 4) == 0 && RM_Ember.Bounce(3, 4) == 3
              && RM_Ember.Bounce(4, 4) == 2 && RM_Ember.Bounce(6, 4) == 0 && RM_Ember.Bounce(7, 4) == 1 && RM_Ember.Bounce(-1, 4) == 1);
    }
}
