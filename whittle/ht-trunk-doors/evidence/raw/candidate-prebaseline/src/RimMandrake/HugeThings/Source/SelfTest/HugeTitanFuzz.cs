// Seeded fuzz of the giant-plant/titan seam and the Mod Settings gate tree (Kernel/RM_HugeTitanKernel.cs), against independent
// oracles written here from the rulings, never from the kernel:
//   smash      which giants one titan step smashes: exactly the owners with a solid cell within Reach of the footprint, each once,
//              ascending, permutation-invariant; nothing when the tier is below the smash tier, the feature is off, or the tier
//              setting is out of range. Default ladder: T1 and T2 never smash, T3 does.
//   smashstep  a titan walking past giants for many steps: every giant in reach takes exactly one forwarded blow per step through
//              the production DamageDedup, even when the trunk-forwarding route fires for the same source in the same tick.
//   gates      master AND detail for every behaviour; either master off is vanilla for its half; smashing needs both masters
//              and the wake; a giant is off the wake's crush table only while giant plants are on.
//   determinism every family replays a seed identically.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.HugeThings.SelfTest
{
    internal static class HugeTitanFuzz
    {
        public static long Cases, Checks, Smashed, Spared;

        private static void Check(bool ok, string msg)
        {
            Checks++;
            if (!ok) throw new Exception(msg);
        }

        private static bool OracleSmashes(int tier, int minTier, bool enabled)
            => enabled && tier >= 1 && tier <= 3 && minTier >= 1 && minTier <= 3 && tier >= minTier;

        internal static string CaseSmash(int seed)
        {
            var r = new Random(seed);
            int tier = r.Next(0, 4);
            int minTier = r.Next(10) == 0 ? (r.Next(2) == 0 ? 0 : 4) : r.Next(1, 4);
            bool enabled = r.Next(5) != 0;
            int w = r.Next(1, 5), h = r.Next(1, 5);
            int x0 = r.Next(-20, 20), z0 = r.Next(-20, 20);
            int x1 = x0 + w - 1, z1 = z0 + h - 1;
            var solid = new List<SolidCell>();
            int n = r.Next(0, 40);
            for (int i = 0; i < n; i++)
                solid.Add(new SolidCell(x0 + r.Next(-4, w + 4), z0 + r.Next(-4, h + 4), r.Next(0, 7) * 13 + 2));

            List<int> got = GiantSmash.Owners(tier, minTier, enabled, x0, z0, x1, z1, solid);
            var want = new SortedSet<int>();
            if (OracleSmashes(tier, minTier, enabled))
            {
                foreach (SolidCell s in solid)
                {
                    int dx = s.X < x0 ? x0 - s.X : (s.X > x1 ? s.X - x1 : 0);
                    int dz = s.Z < z0 ? z0 - s.Z : (s.Z > z1 ? s.Z - z1 : 0);
                    if (Math.Max(dx, dz) <= 1) want.Add(s.Owner);
                }
            }
            Check(got.SequenceEqual(want), $"tier {tier} min {minTier} on {enabled}: smashed [{string.Join(",", got)}], want [{string.Join(",", want)}]");
            Check(got.Distinct().Count() == got.Count, "a giant smashed twice in one step");
            if (got.Count > 0) Smashed++; else if (solid.Count > 0) Spared++;

            // permutation invariance: the map's thing order never changes who is hit or in which order
            var shuffled = solid.OrderBy(_ => r.Next()).ToList();
            Check(GiantSmash.Owners(tier, minTier, enabled, x0, z0, x1, z1, shuffled).SequenceEqual(got), "order of solid cells changed the result");

            // the shipped default: only T3 smashes; T1 and T2 path around
            Check(GiantSmash.Smashes(tier, GiantSmash.DefaultMinTier, true) == (tier == 3), "default smash tier is not exactly T3");
            Check(!GiantSmash.Smashes(0, 1, true), "an untiered pawn smashes");

            // damage: the heavy blow scaled, never negative, monotone in the multiplier
            float heavy = 1f + (float)r.NextDouble() * 100f, m1 = (float)r.NextDouble() * 3f, m2 = m1 + (float)r.NextDouble();
            Check(Math.Abs(GiantSmash.Damage(heavy, m1) - heavy * m1) < 1e-3f, "smash damage is not heavy x multiplier");
            Check(GiantSmash.Damage(heavy, m2) >= GiantSmash.Damage(heavy, m1), "smash damage not monotone in the multiplier");
            Check(GiantSmash.Damage(heavy, -1f) == 0f, "negative multiplier deals negative damage");
            return string.Join(",", got);
        }

        internal static string CaseSmashStep(int seed)
        {
            var r = new Random(seed);
            int tier = r.Next(1, 4), minTier = r.Next(1, 4);
            int size = r.Next(1, 5);
            var dedup = new DamageDedup();
            var solid = new List<SolidCell>();
            int giants = r.Next(1, 5);
            for (int g = 0; g < giants; g++)
            {
                int gx = r.Next(2, 30), gz = r.Next(-3, size + 3), owner = 100 + g;
                int cells = r.Next(1, 8);
                for (int c = 0; c < cells; c++) solid.Add(new SolidCell(gx + r.Next(-2, 3), gz + r.Next(-2, 3), owner));
            }
            long titan = r.Next(1, 1000);
            var hits = new Dictionary<int, int>();
            int steps = 32, tick = 1000;
            for (int step = 0; step < steps; step++)
            {
                tick += 1 + r.Next(30);   // a pawn enters at most one cell per tick, and ticks only rise
                List<int> owners = GiantSmash.Owners(tier, minTier, true, step, 0, step + size - 1, size - 1, solid);
                foreach (int o in owners)
                {
                    bool first = dedup.ShouldForward(tick, titan, o);
                    Check(first, "a giant's first smash in a step was dropped");
                    hits[o] = (hits.TryGetValue(o, out int k) ? k : 0) + 1;
                    // the trunk-forwarding route for the same blow (same source, same tick) must not hit again
                    Check(!dedup.ShouldForward(tick, titan, o), "the trunk route hit a giant a second time in one step");
                }
                if (tier < minTier) Check(owners.Count == 0, "a titan below the smash tier smashed");
            }
            foreach (var kv in hits) Check(kv.Value <= steps, "more blows than steps");
            // PLANT_INTERACTION_GUARDS_1 (A3.7): pellets / burst rounds from one launcher in one tick are separate projectiles and each
            // lands; the same source as an AREA event lands once.
            {
                var d2 = new DamageDedup();
                int t0 = 5000 + r.Next(1000), pellets = r.Next(2, 9), owner = 7 + r.Next(50);
                long launcher = r.Next(1, 100000);
                int landed = 0;
                for (int i = 0; i < pellets; i++) if (d2.ShouldForward(t0, launcher, owner, false)) landed++;
                Check(landed == pellets, $"{pellets} same-tick pellets from one launcher landed {landed}");
                int area = 0;
                for (int i = 0; i < pellets; i++) if (d2.ShouldForward(t0, launcher, owner, true)) area++;
                Check(area == 1, $"one area event over {pellets} trunk cells landed {area} times");
            }
            // PLANT_INTERACTION_GUARDS_1 (C3.3): the hitbox follows the graphic actually drawn (female / alternate), never smaller than the body.
            {
                float bx = 0.5f + (float)r.NextDouble() * 8f, by = 0.5f + (float)r.NextDouble() * 8f;
                float ax = 0.5f + (float)r.NextDouble() * 12f, ay = 0.5f + (float)r.NextDouble() * 12f;
                bool has = r.Next(2) == 0;
                HitboxDraw.Pick(bx, by, has, ax, ay, out float hx, out float hy);
                Check(hx >= bx && hy >= by, "hitbox narrower than the body graphic");
                if (has) Check(hx == Math.Max(bx, ax) && hy == Math.Max(by, ay), "a bigger drawn (female/alternate) graphic did not widen the hitbox");
                else Check(hx == bx && hy == by, "no active graphic changed the hitbox");
                HitboxDraw.Pick(1f, 1f, true, 3f, 2f, out float fx, out float fy);
                Check(fx == 3f && fy == 2f, "female graphic 3x2 over a 1x1 body did not set the hitbox");
            }
            return string.Join(";", hits.OrderBy(kv => kv.Key).Select(kv => kv.Key + ":" + kv.Value));
        }

        internal static string CaseGates(int seed)
        {
            var r = new Random(seed);
            bool gp = r.Next(2) == 0, ga = r.Next(2) == 0, wake = r.Next(2) == 0, f = r.Next(2) == 0, smash = r.Next(2) == 0, giant = r.Next(2) == 0;
            Check(HugeGates.Plant(gp, f) == (gp && f), "plant gate");
            Check(HugeGates.Animal(ga, f) == (ga && f), "animal gate");
            Check(HugeGates.Wake(ga, wake, f) == (ga && wake && f), "wake sub-gate");
            Check(HugeGates.Smash(gp, ga, wake, smash) == (gp && ga && wake && smash), "smash gate");
            if (!gp) Check(!HugeGates.Plant(gp, true) && !HugeGates.Smash(gp, true, true, true), "giant plants off still lets a plant behaviour run");
            if (!ga) Check(!HugeGates.Animal(ga, true) && !HugeGates.Wake(ga, true, true) && !HugeGates.Smash(true, ga, true, true),
                           "giant animals off still lets an animal behaviour run");
            Check(HugeGates.Plant(true, true) && HugeGates.Animal(true, true) && HugeGates.Wake(true, true, true) && HugeGates.Smash(true, true, true, true),
                  "the shipped defaults (everything on) do not run every behaviour");
            bool g = HugeGates.IsGiantForWake(gp, giant);
            Check(g == (gp && giant), "giant-for-wake");
            Check(GiantSmash.WakeMayCrush(g) == !(gp && giant), "the crush table may touch a giant while giant plants are on, or skips an ordinary plant");
            return (gp ? "1" : "0") + (ga ? "1" : "0") + (wake ? "1" : "0") + (f ? "1" : "0") + (smash ? "1" : "0");
        }

        private static bool Family(string name, int n, int? one, Func<int, string> run)
        {
            int fails = 0, ran = 0;
            for (int i = 0; i < n; i++)
            {
                int seed = one ?? (i * 6151 + name.Length * 92821);
                Cases++;
                ran++;
                try
                {
                    run(seed);
                }
                catch (Exception e)
                {
                    if (fails++ < 5) Console.WriteLine("FAIL " + name + " seed " + seed + ": " + e.Message);
                }
                if (one.HasValue) break;
            }
            // HUGETHINGS_TEST_HONESTY_1 (C3.8): print what actually ran; a family that ran nothing fails.
            Console.WriteLine((fails == 0 && ran > 0 ? "PASS " : "FAIL ") + name + ": " + ran + " cases, " + fails + " failed");
            return fails == 0 && ran > 0;
        }

        public static readonly string[] Families = { "smash", "smashstep", "gates", "titandeterminism" };

        public static bool Run(double scale, int? one, string only)
        {
            int N(int baseN) => Math.Max(scale > 0 ? 1 : 0, (int)(baseN * scale));
            bool ok = true;
            if (only == null || only == "smash") ok &= Family("smash", N(6000), one, CaseSmash);
            if (only == null || only == "smashstep") ok &= Family("smashstep", N(2000), one, CaseSmashStep);
            if (only == null || only == "gates") ok &= Family("gates", N(1000), one, CaseGates);
            if (only == null || only == "titandeterminism")
                ok &= Family("titandeterminism", N(300), one, s =>
                {
                    Check(CaseSmash(s) == CaseSmash(s) && CaseSmashStep(s) == CaseSmashStep(s) && CaseGates(s) == CaseGates(s), "a seed replayed differently");
                    return "";
                });
            if (only == null && !one.HasValue && scale >= 1 && (Smashed == 0 || Spared == 0))
            {
                Console.WriteLine("FAIL smash fuzz never reached both a smash and a spare (blind): smashed " + Smashed + ", spared " + Spared);
                ok = false;
            }
            Console.WriteLine("huge-titan seam fuzz: " + Cases + " cases, " + Checks + " checks");
            return ok;
        }
    }
}
