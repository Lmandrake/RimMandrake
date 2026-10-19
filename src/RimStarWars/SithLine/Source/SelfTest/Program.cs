// SithLine kernel selftest: exhaustive grids plus seeded random cases over RSW_SithLineKernel, each checked against the
// owner's rulings written out here (card 2026-10-09: inquisitors in raids and defenders only, never traders; a Sith
// adept never joins). Every number comes from the production kernel.
using System;
using System.Collections.Generic;
using K = RimMandrake.StarWars.SithLine.RSW_SithLineKernel;

namespace RimMandrake.StarWars.SithLine.SelfTest
{
    internal static class Program
    {
        private static int cases;
        private static readonly List<string> fails = new List<string>();

        private static void Check(bool ok, string msg) { cases++; if (!ok && fails.Count < 20) fails.Add(msg); }

        private static int Main()
        {
            var r = new Random(1);
            var kinds = (K.GroupKind[])Enum.GetValues(typeof(K.GroupKind));
            for (int i = 0; i < 200000; i++)
            {
                K.GroupKind kind = kinds[r.Next(kinds.Length)];
                bool emp = r.Next(4) != 0, rOn = r.Next(4) != 0, dOn = r.Next(4) != 0;
                float pts = r.Next(10) == 0 ? float.NaN : (float)(r.NextDouble() * 5000);
                float roll = r.Next(50) == 0 ? float.NaN : (float)r.NextDouble();
                float rc = r.Next(10) == 0 ? float.NaN : (float)(r.NextDouble() * 1.4 - 0.2);
                float dc = r.Next(10) == 0 ? float.NaN : (float)(r.NextDouble() * 1.4 - 0.2);
                float mp = (float)(r.NextDouble() * 4000);
                bool got = K.AddInquisitor(kind, emp, pts, roll, rOn, rc, mp, dOn, dc);
                bool want = emp && !float.IsNaN(roll) && (
                    (kind == K.GroupKind.Combat && rOn && !float.IsNaN(pts) && pts >= mp && roll < K.ClampChance(rc)) ||
                    (kind == K.GroupKind.Settlement && dOn && roll < K.ClampChance(dc)));
                Check(got == want, $"AddInquisitor({kind}, emp {emp}, pts {pts}, roll {roll}, raids {rOn} {rc} {mp}, def {dOn} {dc}) = {got}, want {want}");
                if (kind == K.GroupKind.Trader || kind == K.GroupKind.Other) Check(!got, $"an inquisitor joined a {kind} group");
                if (!emp) Check(!got, "an inquisitor joined a non-Empire group");
            }
            // chance clamp: [0,1], monotone, NaN fails closed
            float prev = -1f;
            for (float c = -2f; c <= 3f; c += 0.01f)
            {
                float v = K.ClampChance(c);
                Check(v >= 0f && v <= 1f, $"ClampChance({c}) = {v} outside [0,1]");
                Check(v >= prev, $"ClampChance fell at {c}");
                prev = v;
            }
            Check(K.ClampChance(float.NaN) == 0f, "ClampChance(NaN) is not 0");
            Check(!K.AddInquisitor(K.GroupKind.Combat, true, 99999f, 0f, true, 0f, 0f, true, 1f), "a 0% raid chance still added one");
            Check(K.AddInquisitor(K.GroupKind.Settlement, true, 0f, 0.999f, false, 0f, 0f, true, 1f), "a 100% defender chance did not add one");
            // the shipped defaults are inside their own ranges
            Check(K.ClampChance(K.DefaultRaidChance) == K.DefaultRaidChance && K.ClampChance(K.DefaultDefenderChance) == K.DefaultDefenderChance, "a default chance is outside [0,1]");
            // never recruitable: the full truth table
            foreach (bool on in new[] { false, true })
                foreach (bool sith in new[] { false, true })
                    foreach (bool player in new[] { false, true })
                    {
                        Check(K.RefuseJoin(on, sith, player) == (on && sith && player), $"RefuseJoin({on},{sith},{player})");
                        foreach (bool van in new[] { false, true })
                            Check(K.Recruitable(van, on, sith) == (van && !(on && sith)), $"Recruitable({van},{on},{sith})");
                    }
            // lair: wake window 6-10 h, monotone in the roll, clamped; wake only while in trance; loot silver clamped
            int prevW = int.MinValue;
            for (float roll = -0.5f; roll <= 1.5f; roll += 0.01f)
            {
                int w = K.WakeTick(1000, roll);
                Check(w >= 1000 + 6 * K.TicksPerHour && w <= 1000 + 10 * K.TicksPerHour, $"WakeTick roll {roll} = {w - 1000} ticks, outside 6-10 h");
                Check(w >= prevW, $"WakeTick fell at roll {roll}");
                prevW = w;
            }
            Check(K.WakeTick(0, float.NaN) == 6 * K.TicksPerHour, "WakeTick(NaN) is not the 6 h floor");
            for (int i = 0; i < 20000; i++)
            {
                bool dr = r.Next(2) == 0, hurt = r.Next(3) == 0, intr = r.Next(3) == 0;
                int now = r.Next(0, 50000), wake = r.Next(0, 50000);
                bool got = K.ShouldWake(dr, hurt, intr, now, wake);
                Check(got == (dr && (hurt || intr || now >= wake)), $"ShouldWake({dr},{hurt},{intr},{now},{wake}) = {got}");
            }
            int prevS = 0;
            for (float pts = -100f; pts <= 20000f; pts += 7f)
            {
                int sv = K.LootSilver(pts);
                Check(sv >= 200 && sv <= 4000, $"LootSilver({pts}) = {sv} outside [200,4000]");
                Check(sv >= prevS, $"LootSilver fell at {pts}");
                prevS = sv;
            }
            Check(K.LootSilver(float.NaN) == 200, "LootSilver(NaN) is not the floor");
            foreach (string f in fails) Console.WriteLine("FAIL " + f);
            Console.WriteLine($"sithline kernel: {cases} checks, {fails.Count} failures -> {(fails.Count == 0 ? "OK" : "FAILED")}");
            return fails.Count == 0 && cases > 1000 ? 0 : 1;
        }
    }
}
