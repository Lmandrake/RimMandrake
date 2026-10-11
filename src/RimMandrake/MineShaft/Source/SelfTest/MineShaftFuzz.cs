// Approach B for the Mine Shaft: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_MineShaftKernel.cs):
//   source  IsEligibleSource against its truth table, all 32 inputs
//   ban     a banned product is never offered; null product / null list never ban
//   work    WorkTicks floored at 60, monotone in hit points and in the multiplier, finite for adversarial input (NaN, +/-inf, int.Min)
//   yield   chunks (stack limit <= 1) always exactly 1; otherwise 1..MaxYieldPerBill, monotone in the multiplier
//   order   CompareSources is a total order (reflexive zero, antisymmetric, transitive) and ranks ore before stone, scattering first
//   vein    OfferedOnMap truth table
// A failing case is printed as `family seed N: message`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;

namespace RimMandrake.MineShaft.SelfTest
{
    internal static class MineShaftFuzz
    {
        public static long Cases;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        private static List<string> Loop(string name, int n, int seed, Action<int> one)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                Cases++;
                try { one(seed + i); } catch (Exception e) { fails.Add($"{name} seed {seed + i}: {e.Message}"); if (fails.Count >= 3) break; }
            }
            return fails;
        }

        private static float AdversarialFloat(Random r)
        {
            switch (r.Next(8))
            {
                case 0: return float.NaN;
                case 1: return float.PositiveInfinity;
                case 2: return float.NegativeInfinity;
                case 3: return -(float)r.NextDouble() * 100f;
                case 4: return 0f;
                default: return (float)(r.NextDouble() * 10.0);
            }
        }

        private static List<string> Source(int n, int seed)
        {
            return Loop("source", 1, 1, _ =>
            {
                for (int m = 0; m < 32; m++)
                {
                    bool mineable = (m & 1) != 0, prod = (m & 2) != 0, res = (m & 4) != 0, nat = (m & 8) != 0, stone = (m & 16) != 0;
                    bool want = mineable && prod && (res || (stone && nat));
                    Check(RM_MineShaftKernel.IsEligibleSource(mineable, prod, res, nat, stone) == want, "eligibility mask " + m);
                }
            });
        }

        private static List<string> Ban(int n, int seed)
        {
            return Loop("ban", n, seed, s =>
            {
                var r = new Random(s);
                var banned = new HashSet<string>();
                for (int i = 0; i < r.Next(0, 6); i++) banned.Add("P" + r.Next(10));
                string p = "P" + r.Next(10);
                Check(RM_MineShaftKernel.IsBanned(p, banned) == banned.Contains(p), "ban disagrees with set for " + p);
                Check(!RM_MineShaftKernel.IsBanned(null, banned), "null product banned");
                Check(!RM_MineShaftKernel.IsBanned(p, null), "null list banned");
            });
        }

        private static List<string> Work(int n, int seed)
        {
            return Loop("work", n, seed, s =>
            {
                var r = new Random(s);
                int hp = r.Next(4) == 0 ? (r.Next(2) == 0 ? int.MinValue : int.MaxValue) : r.Next(-100, 20000);
                float m = AdversarialFloat(r);
                float t = RM_MineShaftKernel.WorkTicks(hp, m);
                Check(!float.IsNaN(t) && !float.IsInfinity(t), "non-finite work " + t + " hp " + hp + " m " + m);
                Check(t >= RM_MineShaftKernel.MinWorkTicks, "work below floor " + t);
                float cm = RM_MineShaftKernel.ClampMultiplier(m);
                Check(cm >= RM_MineShaftKernel.MinMultiplier && cm <= RM_MineShaftKernel.MaxMultiplier, "clamp out of range " + cm);
                int hp2 = hp == int.MaxValue ? hp : hp + r.Next(0, 500);
                Check(RM_MineShaftKernel.WorkTicks(hp2, m) >= t, "work not monotone in hp");
                float m2 = cm + (float)r.NextDouble();
                Check(RM_MineShaftKernel.WorkTicks(hp, m2) >= RM_MineShaftKernel.WorkTicks(hp, cm), "work not monotone in multiplier");
            });
        }

        private static List<string> Yield(int n, int seed)
        {
            return Loop("yield", n, seed, s =>
            {
                var r = new Random(s);
                int stack = r.Next(-2, 200);
                int y = r.Next(4) == 0 ? (r.Next(2) == 0 ? int.MinValue : int.MaxValue) : r.Next(-5, 100);
                float m = AdversarialFloat(r);
                int got = RM_MineShaftKernel.Yield(stack, y, m);
                if (stack <= 1) Check(got == 1, "chunk yield " + got);
                Check(got >= 1 && got <= RM_MineShaftKernel.MaxYieldPerBill, "yield out of range " + got);
                float cm = RM_MineShaftKernel.ClampMultiplier(m);
                Check(RM_MineShaftKernel.Yield(stack, y, cm + 0.5f) >= RM_MineShaftKernel.Yield(stack, y, cm), "yield not monotone");
            });
        }

        private struct Src { public bool Res; public float Com; public int Hp; public string Name; }

        private static Src RandSrc(Random r)
        {
            return new Src { Res = r.Next(2) == 0, Com = r.Next(3) == 0 ? 0f : (float)r.Next(0, 4) / 2f, Hp = r.Next(0, 4) * 500, Name = "R" + r.Next(6) };
        }

        private static int Cmp(Src a, Src b) { return RM_MineShaftKernel.CompareSources(a.Res, a.Com, a.Hp, a.Name, b.Res, b.Com, b.Hp, b.Name); }

        private static List<string> Order(int n, int seed)
        {
            return Loop("order", n, seed, s =>
            {
                var r = new Random(s);
                Src a = RandSrc(r), b = RandSrc(r), c = RandSrc(r);
                Check(Cmp(a, a) == 0, "not reflexive");
                Check(Math.Sign(Cmp(a, b)) == -Math.Sign(Cmp(b, a)), "not antisymmetric");
                if (Cmp(a, b) <= 0 && Cmp(b, c) <= 0) Check(Cmp(a, c) <= 0, "not transitive");
                if (a.Res && !b.Res) Check(Cmp(a, b) < 0, "stone ranked before ore");
                if (a.Res == b.Res && a.Com > 0f && b.Com == 0f) Check(Cmp(a, b) < 0, "event-only rock ranked before a scattering one");
            });
        }

        private static List<string> Vein(int n, int seed)
        {
            return Loop("vein", 1, 1, _ =>
            {
                for (int m = 0; m < 8; m++)
                {
                    bool on = (m & 1) != 0, rock = (m & 2) != 0, deep = (m & 4) != 0;
                    Check(RM_MineShaftKernel.OfferedOnMap(on, rock, deep) == (!on || rock || deep), "vein mask " + m);
                }
                Check(RM_MineShaftKernel.IsShaftRecipe(RM_MineShaftKernel.RecipeDefName("MineableGold")), "own recipe not recognised");
                Check(!RM_MineShaftKernel.IsShaftRecipe("MinesAutomated_RecipeDef_MineableGold") && !RM_MineShaftKernel.IsShaftRecipe(null), "foreign recipe recognised");
            });
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            int N(int baseN) { return oneSeed.HasValue ? 1 : (int)Math.Round(baseN * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var families = new List<(string, Func<int, int, List<string>>, int, int)>
            {
                ("source", Source, 1, 1), ("ban", Ban, 4000, 1000), ("work", Work, 20000, 2000),
                ("yield", Yield, 20000, 3000), ("order", Order, 20000, 4000), ("vein", Vein, 1, 1),
            };
            var all = new List<string>();
            int ran = 0;
            foreach (var (name, fn, n, seed) in families)
            {
                if (only != null && only != name) continue;
                int count = N(n);
                if (count <= 0) continue;
                ran++;
                List<string> f = fn(count, S(seed));
                Console.WriteLine($"{name}: {(f.Count == 0 ? "PASS" : "FAIL")} ({count} case(s))");
                all.AddRange(f);
            }
            foreach (string f in all) Console.WriteLine("  " + f);
            Console.WriteLine($"MineShaft fuzz: {ran} famil(ies), {Cases} case(s), {all.Count} failure(s)");
            return all.Count == 0 && ran > 0;
        }
    }
}
