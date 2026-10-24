// Selftest for build step 10, the phrase modifiers (Kernel/RM_PatternModifiers.cs: ECHO, APPROACH, SCAR, HUSH) and the
// Sweep pause/accelerate warp (RM_PatternFronts.cs), kernel only. REAL, compiled from production source.
// NOT covered: the compositor's wiring of SCAR/HUSH to live fixtures (needs Verse; the rules it calls are tested here).
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.AtmosphericBase;

internal static class ModifierTests
{
    private static void Check(string name, bool ok, string detail = "") => Program.Check(name, ok, detail);

    private const string Pal4 = "<li>(0,0,0,0)</li><li>(26,10,4,0)</li><li>(64,26,8,0)</li><li>(205,98,24,0)</li>";

    private static void Chain(int rooms, int per, out RM_RoomGraph g, out RM_FixtureSet f)
    {
        var rs = new List<RM_RoomFacts>(); var ds = new List<KeyValuePair<int, int>>();
        for (int i = 1; i <= rooms; i++)
        {
            rs.Add(new RM_RoomFacts { id = i, cells = 20, threshold = i == 1 });
            if (i > 1) ds.Add(new KeyValuePair<int, int>(i - 1, i));
        }
        g = RM_RoomGraph.Build(rs, ds);
        var e = new List<int>(); var r = new List<int>(); var x = new List<float>(); var z = new List<float>();
        for (int i = 0; i < rooms * per; i++) { e.Add(6000 + (i * 7919) % 9973); r.Add(1 + i / per); x.Add(i * 2f); z.Add((i % 2) * 1f); }
        f = new RM_FixtureSet(e, r, x, z);
    }

    private static RM_SchemeData Layer(string li, string under = "") =>
        PatternTests.One("<layers>" + under + "<li>" + li + "</li></layers>", Pal4);

    private static int At(RM_SchemeData s, RM_RoomGraph g, RM_FixtureSet f, int k, double t)
    {
        RM_PatternCtx c = RM_PatternCtx.Of(f.ids[k], f.room[k], g, f);
        return RM_PatternEvaluator.Index(s, ref c, t, false);
    }

    private static Func<int, RM_PatternCtx> CtxOf(RM_RoomGraph g, RM_FixtureSet f) =>
        r => { int k = r % f.Count; return RM_PatternCtx.Of(f.ids[k], f.room[k], g, f); };

    internal static void Run()
    {
        Echo();
        Approach();
        Scar();
        Hush();
        SweepWarp();
    }

    private static void Echo()
    {
        Chain(5, 2, out RM_RoomGraph g, out RM_FixtureSet f);
        const string breath = "<primitive>Breath</primitive><scope>Field</scope><period>30</period><phaseSpread>0</phaseSpread><anchor>Threshold</anchor>";
        RM_SchemeData plain = Layer(breath);
        RM_SchemeData echo = Layer(breath + "<echo>6</echo>");
        RM_SchemeData inv = Layer(breath + "<echo>6</echo><echoInvert>true</echoInvert>");
        RM_Layer l = echo.layers[0];
        // delays: rooms an even number of doors out call (0); odd rooms answer after echo x (1 +- 20%) x ((d+1)/2)
        bool bounds = true; var delays = new HashSet<double>(); string why = "";
        for (int k = 0; k < f.Count; k++)
        {
            RM_PatternCtx c = RM_PatternCtx.Of(f.ids[k], f.room[k], g, f);
            double d = RM_Modifiers.EchoDelay(l, ref c);
            int hops = g.Distance(RM_Anchor.Threshold, c.node);
            if (hops % 2 == 0) { if (d != 0) { bounds = false; why = "room " + f.room[k] + " d=" + d; } continue; }
            double nominal = 6.0 * ((hops + 1) / 2);
            if (d < nominal * 0.8 - 1e-9 || d > nominal * 1.2 + 1e-9) { bounds = false; why = "room " + f.room[k] + " d=" + d; }
            delays.Add(Math.Round(d, 6));
        }
        Check("M1 echo delay: calling rooms 0, answering rooms within echo x (1 +- 20%) x ((d+1)/2), and the jitter is real",
              bounds && delays.Count >= 2, why + " distinct " + delays.Count);
        // the answer replays the caller: an answering fixture now shows what the plain layer showed `delay` ago
        bool replay = true, inverted = true, caller = true;
        for (int k = 0; k < f.Count; k++)
        {
            RM_PatternCtx c = RM_PatternCtx.Of(f.ids[k], f.room[k], g, f);
            double d = RM_Modifiers.EchoDelay(l, ref c);
            for (double t = 100; t < 160; t += 0.7)
            {
                int was = At(plain, g, f, k, t - d), now = At(echo, g, f, k, t), iv = At(inv, g, f, k, t);
                if (d == 0) { if (now != At(plain, g, f, k, t) || iv != now) caller = false; continue; }
                if (now != was) replay = false;
                if (iv != 0 + 3 - was) inverted = false;
            }
        }
        Check("M1 echo: the calling wing is the plain layer, unchanged (and echoInvert leaves it alone)", caller);
        Check("M1 echo: an answering room shows exactly what the caller showed one delay earlier", replay);
        Check("M1 echoInvert: the answer is the caller inverted (lo + hi - x)", inverted);
        PatternTests.NextChangeAgrees("M1 echo NextChange", echo, false, 300, 0.05, 40, CtxOf(g, f));
        PatternTests.NextChangeAgrees("M1 echoInvert NextChange", inv, false, 300, 0.05, 40, CtxOf(g, f));
        Check("M1 echo Errors: negative echo, and echoInvert without echo, are refused",
              PatternTests.HasError(Layer(breath + "<echo>-1</echo>"), "echo must be")
              && PatternTests.HasError(Layer(breath + "<echoInvert>true</echoInvert>"), "echoInvert needs"));
    }

    private static void Approach()
    {
        Chain(5, 2, out RM_RoomGraph g, out RM_FixtureSet f);
        const string under = "<li><primitive>Steady</primitive><entries>1</entries></li>";
        const string sweep = "<primitive>Sweep</primitive><period>4</period><lit>0.5</lit><anchor>Threshold</anchor><entries>2~3</entries>"
                             + "<reach>3</reach><speed>0.5</speed><pause>8</pause><approachEvery>60</approachEvery>";
        RM_SchemeData slow = Layer(sweep, under);
        RM_SchemeData fast = Layer(sweep + "<withdraw>Fast</withdraw>", under);
        RM_Layer ls = slow.layers[1], lf = fast.layers[1];
        // envelope: advance 3 hops at 0.5 hops/s = 6 s, hold 8 s, withdraw Slow 18 s / Fast 2 s, then nothing till 60
        bool env = Math.Abs(RM_Modifiers.Front(ls, 3) - 1.5) < 1e-9 && Math.Abs(RM_Modifiers.Front(ls, 6) - 3) < 1e-9
                   && Math.Abs(RM_Modifiers.Front(ls, 13.9) - 3) < 1e-9 && Math.Abs(RM_Modifiers.Front(ls, 23) - 1.5) < 1e-9
                   && RM_Modifiers.Front(ls, 40) == 0 && Math.Abs(RM_Modifiers.Front(ls, 63) - 1.5) < 1e-9;
        Check("M2 approach envelope: advance reach/speed, hold pause, Slow withdraw 3x the advance, rest, repeat every approachEvery", env);
        Check("M2 approach: Slow withdraws three times the advance, Fast a third of it (18 s vs 2 s)",
              Math.Abs(RM_Modifiers.WithdrawSeconds(ls) - 18) < 1e-9 && Math.Abs(RM_Modifiers.WithdrawSeconds(lf) - 2) < 1e-9
              && RM_Modifiers.Front(lf, 15) < RM_Modifiers.Front(ls, 15));
        // outside the front the layer is Pass (the Steady 1 below shows); inside, the sweep shows (2~3)
        bool outsidePass = true, insideShows = true, farNever = true; int seenInside = 0;
        for (int k = 0; k < f.Count; k++)
        {
            RM_PatternCtx c = RM_PatternCtx.Of(f.ids[k], f.room[k], g, f);
            int hops = g.Distance(RM_Anchor.Threshold, c.node);
            for (double t = 0.3; t < 120; t += 0.5)
            {
                int v = At(slow, g, f, k, t);
                bool inside = RM_Modifiers.Inside(ls, ref c, t);
                if (hops >= 3 && inside) farNever = false;
                if (!inside && v != 1) outsidePass = false;
                if (inside) { seenInside++; if (v < 2) insideShows = false; }
            }
        }
        Check("M2 approach: outside the front the layer is Pass (the layer below shows)", outsidePass);
        Check("M2 approach: inside the front the layer shows", insideShows && seenInside > 0, "inside samples " + seenInside);
        Check("M2 approach: a room reach or more doors out is never reached", farNever);
        // a room 1 door out is inside later than the anchor room and leaves earlier
        RM_PatternCtx c0 = RM_PatternCtx.Of(f.ids[0], f.room[0], g, f), c1 = RM_PatternCtx.Of(f.ids[2], f.room[2], g, f);
        Check("M2 approach: the front reaches the anchor room before the room one door out, and leaves it after",
              RM_Modifiers.Inside(ls, ref c0, 1) && !RM_Modifiers.Inside(ls, ref c1, 1)
              && RM_Modifiers.Inside(ls, ref c0, 25) && !RM_Modifiers.Inside(ls, ref c1, 25));
        PatternTests.NextChangeAgrees("M2 approach Slow NextChange", slow, false, 300, 0.05, 70, CtxOf(g, f));
        PatternTests.NextChangeAgrees("M2 approach Fast NextChange", fast, false, 300, 0.05, 70, CtxOf(g, f));
        Check("M2 approach Errors: reach on Breath, a cycle longer than approachEvery, and speed 0 are refused",
              PatternTests.HasError(Layer("<primitive>Breath</primitive><reach>2</reach>"), "front primitive only")
              && PatternTests.HasError(Layer(sweep.Replace("<approachEvery>60</approachEvery>", "<approachEvery>20</approachEvery>")), "longer than approachEvery")
              && PatternTests.HasError(Layer(sweep.Replace("<speed>0.5</speed>", "<speed>0</speed>")), "speed > 0"));
    }

    private static void Scar()
    {
        Check("M3 scar linger: capped at 30 s unless the scheme keeps (Rekko)",
              RM_Scar.Linger(50, false) == 30 && RM_Scar.Linger(50, true) == 50 && RM_Scar.Linger(12, false) == 12 && RM_Scar.Linger(0, true) == 0);
        Check("M3 scar: the previous owner shows only on the new owner's lowest entry, and only within the linger",
              RM_Scar.ShowsPrevious(0, 0, 5, 12, false) && !RM_Scar.ShowsPrevious(2, 0, 5, 12, false)
              && !RM_Scar.ShowsPrevious(0, 0, 12.5, 12, false) && !RM_Scar.ShowsPrevious(0, 0, 40, 50, false)
              && RM_Scar.ShowsPrevious(0, 0, 40, 50, true) && !RM_Scar.ShowsPrevious(0, 0, -1, 12, false));
        RM_SchemeData ok = PatternTests.One("<scarLinger>20</scarLinger>", Pal4);
        Check("M3 scar Errors: a linger over 30 s without scarKeeps is refused, with it accepted, 20 s accepted",
              PatternTests.HasError(PatternTests.One("<scarLinger>45</scarLinger>", Pal4), "scarKeeps")
              && !PatternTests.HasError(PatternTests.One("<scarLinger>45</scarLinger><scarKeeps>true</scarKeeps>", Pal4), "scar")
              && !PatternTests.HasError(ok, "scar") && ok.scarLinger == 20);
    }

    private static void Hush()
    {
        // weight: rises over settle, holds, falls over settle, then over
        bool rise = true, fall = true; double prev = -1;
        for (double s = 0; s <= 4; s += 0.1) { double w = RM_Hush.Weight(s, 4, 20); if (w < prev - 1e-12) rise = false; prev = w; }
        prev = 2;
        for (double s = 24; s <= 28.5; s += 0.1) { double w = RM_Hush.Weight(s, 4, 20); if (w > prev + 1e-12) fall = false; prev = w; }
        Check("M4 hush weight: rises monotone over settle, holds 1, falls monotone over settle, then 0 and over",
              rise && fall && RM_Hush.Weight(10, 4, 20) == 1 && RM_Hush.Weight(29, 4, 20) == 0 && RM_Hush.Over(28, 4, 20) && !RM_Hush.Over(27.9, 4, 20)
              && RM_Hush.Weight(-1, 4, 20) == 0);
        // narrowing is monotone toward the held entry and never overshoots
        bool mono = true;
        foreach (int start in new[] { 0, 3 })
        {
            int last = start;
            for (double w = 0; w <= 1.0001; w += 0.05)
            {
                int v = RM_Hush.Apply(start, 1, w, false, false);
                if (Math.Abs(v - 1) > Math.Abs(last - 1) || (start > 1 ? v < 1 : v > 1)) mono = false;
                last = v;
            }
            if (last != 1) mono = false;
        }
        Check("M4 hush: an index narrows monotone to the held mid entry, never past it", mono);
        RM_SchemeData p4 = PatternTests.One("", Pal4);
        RM_SchemeData blackMid = PatternTests.One("", "<li>(0,0,0,0)</li><li>(0,0,0,0)</li><li>(40,16,6,0)</li><li>(205,98,24,0)</li>");
        Check("M4 hush mid: the palette's middle entry, or the lowest lit one when the middle is black (the ember)",
              RM_Hush.Mid(p4) == 1 && RM_Hush.Mid(blackMid) == 2);
        Check("M4 hush in a dark room: only the keeper holds the ember, the rest settle to black (L8)",
              RM_Hush.Apply(3, 1, 1, true, true) == 1 && RM_Hush.Apply(3, 1, 1, true, false) == 0 && RM_Hush.Apply(3, 1, 0, true, false) == 3);
    }

    private static void SweepWarp()
    {
        Chain(5, 2, out RM_RoomGraph g, out RM_FixtureSet f);
        const string sw = "<primitive>Sweep</primitive><period>10</period><lit>0.3</lit><field>Axis</field>";
        RM_SchemeData plain = Layer(sw), zero = Layer(sw + "<pauseChance>0</pauseChance><accelerate>0</accelerate>");
        RM_SchemeData pausing = Layer(sw + "<pauseChance>1</pauseChance><pause>5</pause>");
        RM_SchemeData some = Layer(sw + "<pauseChance>0.5</pauseChance><pause>4</pause>");
        RM_SchemeData acc = Layer(sw + "<accelerate>0.8</accelerate>"), dec = Layer(sw + "<accelerate>-0.8</accelerate>");
        bool same = true;
        for (int k = 0; k < f.Count; k++) for (double t = 0; t < 60; t += 0.37) if (At(plain, g, f, k, t) != At(zero, g, f, k, t)) same = false;
        Check("S7 sweep unwarped: pauseChance 0 and accelerate 0 are exactly the plain sweep", same);
        bool inverse = true, monotone = true; string why = "";
        foreach (RM_SchemeData s in new[] { pausing, some, acc, dec })
        {
            RM_Layer l = s.layers[0]; double prev = -1;
            for (double t = 0; t < 200; t += 0.13)
            {
                double p = RM_SweepPrimitive.Passes(l, t);
                if (p < prev - 1e-9) monotone = false;
                prev = p;
                double back = RM_SweepPrimitive.TimeOf(l, p);
                if (back > t + 1e-6 || RM_SweepPrimitive.Passes(l, back) < p - 1e-6) { inverse = false; why = "t=" + t + " p=" + p + " back=" + back; }
            }
        }
        Check("S7 sweep warp: Passes never runs backward, and TimeOf is its earliest-time inverse", monotone && inverse, why);
        // pauseChance 1: every pass stops for `pause` s at 0.15-0.85 of it; the cycle is period + pause, so passes never drift
        RM_Layer lp = pausing.layers[0];
        bool stopsEvery = true;
        for (int k = 0; k < 20; k++)
        {
            double start = k * 15.0, held = 0;
            for (double t = start; t < start + 15; t += 0.05)
                if (RM_SweepPrimitive.Passes(lp, t + 0.05) - RM_SweepPrimitive.Passes(lp, t) < 1e-12) held += 0.05;
            if (held < 4.8 || held > 5.2 || Math.Abs(RM_SweepPrimitive.Passes(lp, start) - k) > 1e-9) stopsEvery = false;
        }
        Check("S7 sweep pause: pauseChance 1 holds every pass 5 s and a pass still starts every period + pause", stopsEvery);
        RM_Layer la = acc.layers[0], ld = dec.layers[0];
        Check("S7 sweep accelerate: +0.8 starts slow and ends fast, -0.8 the reverse; both a whole pass per period",
              RM_SweepPrimitive.Passes(la, 2.5) < 0.25 && RM_SweepPrimitive.Passes(ld, 2.5) > 0.25
              && Math.Abs(RM_SweepPrimitive.Passes(la, 10) - 1) < 1e-9 && Math.Abs(RM_SweepPrimitive.Passes(ld, 10) - 1) < 1e-9);
        PatternTests.NextChangeAgrees("S7 sweep pause NextChange", some, false, 300, 0.02, 30, CtxOf(g, f));
        PatternTests.NextChangeAgrees("S7 sweep accelerate NextChange", acc, false, 300, 0.02, 30, CtxOf(g, f));
        PatternTests.NextChangeAgrees("S7 sweep decelerate NextChange", dec, false, 300, 0.02, 30, CtxOf(g, f));
        Check("S7 sweep warp Errors: pauseChance 2, accelerate 1.5, and a pausing sweep with pause 0 are refused",
              PatternTests.HasError(Layer(sw + "<pauseChance>2</pauseChance>"), "pauseChance")
              && PatternTests.HasError(Layer(sw + "<accelerate>1.5</accelerate>"), "accelerate")
              && PatternTests.HasError(Layer(sw + "<pauseChance>0.5</pauseChance><pause>0</pause>"), "pause"));
    }
}
