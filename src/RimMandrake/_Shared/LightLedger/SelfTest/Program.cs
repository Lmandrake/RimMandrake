// Light ledger kernel selftest: the composition rules, the neutral-value removal, and a seeded fuzz that
// replays the two filed collisions (SUN_SPHERE_GRAZE_PERSIST_1, TWILIGHT_WELL_LIGHT_STATE_1) as orderings:
// whatever order effects write in, the radius depends only on the SET of modifiers, never on who wrote last.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.Shared.SelfTest
{
    internal static class Program
    {
        private static int fails;

        private static void Check(bool ok, string what)
        {
            if (!ok) { fails++; Console.WriteLine("FAIL " + what); }
        }

        private static bool Near(float a, float b) { return Math.Abs(a - b) < 1e-4f; }

        private static int Main()
        {
            var m = new Dictionary<string, float>();
            Check(Near(LightLedgerKernel.Compute(6f, m), 6f), "empty ledger reads the def radius");
            LightLedgerKernel.Set(m, "base", 4f);
            Check(Near(LightLedgerKernel.Compute(6f, m), 4f), "an owner's base replaces the def radius");
            LightLedgerKernel.Set(m, "mul:a", 0.5f);
            LightLedgerKernel.Set(m, "mul:b", 1.5f);
            Check(Near(LightLedgerKernel.Compute(6f, m), 3f), "multipliers compose: 4 x 0.5 x 1.5");
            LightLedgerKernel.Set(m, "sub:graze", 1f);
            Check(Near(LightLedgerKernel.Compute(6f, m), 2f), "subtraction after scaling");
            Check(Near(LightLedgerKernel.Scaled(6f, m), 3f), "Scaled ignores subtractions");
            LightLedgerKernel.Set(m, "cap:dark", 0.1f);
            Check(Near(LightLedgerKernel.Compute(6f, m), 0.1f), "a cap holds the light down");
            LightLedgerKernel.Set(m, "cap:dark", -1f);
            Check(!m.ContainsKey("cap:dark"), "negative cap lets go");
            LightLedgerKernel.Set(m, "mul:a", 1f);
            Check(!m.ContainsKey("mul:a"), "mul 1 lets go");
            LightLedgerKernel.Set(m, "sub:graze", 0f);
            Check(!m.ContainsKey("sub:graze"), "sub 0 lets go");
            LightLedgerKernel.Set(m, "sub:huge", 100f);
            Check(Near(LightLedgerKernel.Compute(6f, m), 0f), "never below zero");
            m["tag:deepfire"] = 1f;
            m.Remove("sub:huge");
            Check(Near(LightLedgerKernel.Compute(6f, m), 6f), "a tag is not a modifier (4 x 1.5 = 6)");
            Check(!LightLedgerKernel.NeedsWrite(2f, 2.005f) && LightLedgerKernel.NeedsWrite(2f, 2.02f), "write tolerance");

            // The sun-sphere bug as an ordering: culture re-sets the base every 60 ticks; graze must survive it.
            var s = new Dictionary<string, float>();
            LightLedgerKernel.Set(s, "base", 6f);
            LightLedgerKernel.Set(s, "sub:tb.graze", 2.5f);
            LightLedgerKernel.Set(s, "base", 6f);                   // the culture step
            Check(Near(LightLedgerKernel.Compute(6f, s), 3.5f), "SUN_SPHERE_GRAZE_PERSIST_1: graze survives a culture step");
            // The well bug: lid-dark cap must survive a waning step.
            var w = new Dictionary<string, float>();
            LightLedgerKernel.Set(w, "cap:tb.liddark", 0.1f);
            LightLedgerKernel.Set(w, "base", 5f);                   // the waning step
            Check(Near(LightLedgerKernel.Compute(7f, w), 0.1f), "TWILIGHT_WELL_LIGHT_STATE_1: lid-dark survives a waning step");

            // Fuzz: random writes in random order; the result equals a recompute from the final set only.
            var rng = new Random(20261008);
            string[] keys = { "base", "mul:a", "mul:b", "sub:c", "cap:d", "mul:e", "tag:x" };
            for (int c = 0; c < 2000; c++)
            {
                var ops = new List<KeyValuePair<string, float>>();
                int n = rng.Next(1, 12);
                for (int i = 0; i < n; i++)
                {
                    string k = keys[rng.Next(keys.Length)];
                    float v = k.StartsWith("cap:") && rng.Next(4) == 0 ? -1f
                        : k.StartsWith("mul:") && rng.Next(4) == 0 ? 1f
                        : (float)Math.Round(rng.NextDouble() * 8, 2);
                    ops.Add(new KeyValuePair<string, float>(k, v));
                }
                var a = new Dictionary<string, float>();
                foreach (var op in ops) LightLedgerKernel.Set(a, op.Key, op.Value);
                // last write per key wins; the final set, applied in a shuffled order, gives the same radius
                var last = new Dictionary<string, float>();
                foreach (var op in ops) last[op.Key] = op.Value;
                var b = new Dictionary<string, float>();
                foreach (var kv in last.OrderBy(_ => rng.Next())) LightLedgerKernel.Set(b, kv.Key, kv.Value);
                float ra = LightLedgerKernel.Compute(3f, a), rb = LightLedgerKernel.Compute(3f, b);
                if (!Near(ra, rb)) { Check(false, "fuzz case " + c + ": order changed the radius " + ra + " vs " + rb); break; }
                if (ra < 0f) { Check(false, "fuzz case " + c + ": negative radius"); break; }
            }

            Console.WriteLine(fails == 0 ? "lightledger kernel: all checks passed" : "lightledger kernel: " + fails + " FAILED");
            return fails == 0 ? 0 : 1;
        }
    }
}
