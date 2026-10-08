// Approach B for Wreckage: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_WreckageKernel.cs):
//   tier    the loot-tier ladder and the weathering fold: landing rung = clamp(rung + shift), shift 0 is identity, up/down are monotone, a
//           tier never survives a move to a different rung under its old name, "nothing inside" and Scrap never keep a rare roll
//   loot    deconstruct yield fraction, skill-scaled rare chance (monotone in skill, bounded, 0.25x..2x), stack generosity, hazard dose
//   fields  the disabled-field list: set/get round trips with sloppy whitespace and neighbouring keys, FieldActive truth table
//   place   the field placement loop against random placement oracles: never more than the target, stops after three missed anchors, always
//           reaches the target when everything fits, clusters never overshoot
// A failing case prints `family seed N: message`; --fuzz-seed N replays it. PROVISIONAL: tier ladder, skill factor 0.25..2, rare 0.05.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.Wreckage;

namespace RimMandrake.Wreckage.SelfTest
{
    internal static class WreckageFuzz
    {
        public static long Cases, Steps, Shifts, Rungs, Fills, Stops, Clusters;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float F(Random r, float lo, float hi) { return lo + (float)r.NextDouble() * (hi - lo); }
        private static readonly string[] Tiers = { "Scrap", "Hull", "Tank", "Carapace", "Sealed" };
        private static int SpecRank(string t) { return t == "Scrap" ? 0 : t == "Sealed" ? 2 : 1; }

        private static List<string> Tier(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    foreach (string t in Tiers)
                        for (int shift = -3; shift <= 3; shift++)
                        {
                            Steps++; Shifts++;
                            string got = RM_WreckageKernel.ShiftTier(t, shift);
                            int want = Math.Max(0, Math.Min(2, SpecRank(t) + shift));
                            Check(Tiers.Contains(got), $"ShiftTier({t},{shift}) = {got}, not a tier");
                            Check(SpecRank(got) == want, $"ShiftTier({t},{shift}) = {got} sits on rung {SpecRank(got)}, expected rung {want}");
                            if (SpecRank(got) != SpecRank(t)) Rungs++;
                            if (shift == 0) Check(got == t, "shift 0 changed the tier");
                            if (want == SpecRank(t)) Check(got == t, $"ShiftTier({t},{shift}) stayed on its rung but renamed itself {got}");
                            // monotone in shift
                            if (shift > -3) Check(SpecRank(RM_WreckageKernel.ShiftTier(t, shift - 1)) <= SpecRank(got), "tier rung fell as the shift rose");
                            // a tier that moved up or down a rung never keeps the name of the rung it left
                            if (SpecRank(got) != SpecRank(t)) Check(got != t, "moved rung but kept its name");
                        }
                    // the fold
                    for (int i = 0; i < 20; i++)
                    {
                        string t = Tiers[r.Next(5)]; float rare = r.Next(3) == 0 ? 0f : F(r, 0.01f, 0.4f); bool noL = r.Next(5) == 0, wNo = r.Next(4) == 0; int shift = r.Next(-3, 4);
                        LootFold f = RM_WreckageKernel.Fold(t, rare, noL, wNo, shift);
                        Steps++;
                        Check(f.noLoot == (noL || wNo), "noLoot lost");
                        if (wNo) Check(f.rareChance == 0f, "a nothing-inside wreck kept its rare roll");
                        if (f.tier == "Scrap" && shift != 0) Check(f.rareChance == 0f, "a wreck shifted onto Scrap kept its rare roll");
                        if (shift == 0 && !wNo) Check(f.tier == t && f.rareChance == rare, "an unshifted, loot-bearing wreck changed");
                        Check(f.tier == (shift == 0 ? t : RM_WreckageKernel.ShiftTier(t, shift)), "fold tier is not ShiftTier");
                        Check(f.rareChance <= rare, "fold raised the rare chance");
                    }
                    // the combined shift of two moves is the clamp of the sum only when no rail was hit between: from the middle rung it must be
                    for (int a = -2; a <= 2; a++)
                        for (int b = -2; b <= 2; b++)
                        {
                            int rung = SpecRank(RM_WreckageKernel.ShiftTier(RM_WreckageKernel.ShiftTier("Hull", a), b));
                            int direct = SpecRank(RM_WreckageKernel.ShiftTier("Hull", a + b));
                            if (Math.Abs(a) <= 1 && Math.Abs(b) <= 1 && Math.Sign(a) * Math.Sign(b) >= 0) Check(rung == direct, $"two same-direction shifts {a},{b} disagree with their sum");
                        }
                }
                catch (Exception e) { fails.Add($"tier seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Loot(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int i = 0; i < 30; i++)
                    {
                        Steps++;
                        float fam = r.Next(4) == 0 ? 1f : F(r, 0f, 1f), fac = F(r, 0.05f, 1.5f);
                        float y = RM_WreckageKernel.YieldFraction(fam, fac);
                        Check(y >= 0f && y <= 1f, $"yield fraction {y} outside 0..1");
                        Check(Math.Abs(y - Math.Min(1.0, fam * fac)) < 1e-6, "yield fraction is not min(1, family x factor)");
                        float b = F(r, 0f, 1f); bool skill = r.Next(3) != 0, has = r.Next(5) != 0;
                        float prev = -1f;
                        for (int lvl = 0; lvl <= 20; lvl++)
                        {
                            float rc = RM_WreckageKernel.RareChance(b, skill, has, lvl);
                            Check(rc >= 0f && rc <= 1f, "rare chance outside 0..1");
                            Check(rc >= prev - 1e-6f, "rare chance fell as skill rose");
                            prev = rc;
                            if (!(skill && has)) Check(Math.Abs(rc - Math.Min(1f, b)) < 1e-6f, "an unscaled rare chance is not the base");
                            else Check(Math.Abs(rc - Math.Min(1.0, b * (0.25 + 1.75 * lvl / 20.0))) < 1e-5, $"rare chance at skill {lvl} is {rc}, spec {Math.Min(1.0, b * (0.25 + 1.75 * lvl / 20.0))} (0.25x at 0 rising linearly to 2x at 20)");
                        }
                        if (skill && has && b > 0f)
                        {
                            Check(Math.Abs(RM_WreckageKernel.RareChance(b, true, true, 0) - b * 0.25f) < 1e-5f, "skill 0 is not 0.25x");
                            Check(Math.Abs(RM_WreckageKernel.RareChance(b, true, true, 20) - Math.Min(1f, b * 2f)) < 1e-5f, "skill 20 is not 2x");
                            Check(RM_WreckageKernel.RareChance(b, true, true, 99) == RM_WreckageKernel.RareChance(b, true, true, 20), "skill beyond 20 changed the chance");
                            Check(RM_WreckageKernel.RareChance(b, true, true, -4) == RM_WreckageKernel.RareChance(b, true, true, 0), "negative skill changed the chance");
                        }
                        int stack = 1 + r.Next(200), lim = new[] { 1, 1, 10, 75, 100 }[r.Next(5)]; float gen = r.Next(4) == 0 ? 1f : F(r, 0.25f, 3f);
                        int s2 = RM_WreckageKernel.ScaleStack(stack, lim, gen);
                        if (lim <= 1) Check(s2 == stack, "an unstackable item's count was changed");
                        else if (Math.Abs(gen - 1f) < 1e-6f) Check(s2 == stack, "generosity 1 changed a stack");
                        else { Check(s2 >= 1 && s2 <= lim, $"stack {stack} x {gen} -> {s2} outside 1..{lim}"); double ex = stack * (double)gen; if (ex >= 1 && ex <= lim) Check(Math.Abs(s2 - ex) <= 0.5 + 1e-4, $"stack {stack} x {gen} = {ex} rounded to {s2}, not to the nearest"); }
                        float sev = F(r, 0f, 1f), res = F(r, -0.5f, 1.5f);
                        float d1 = RM_WreckageKernel.HazardDose(sev, true, res), d0 = RM_WreckageKernel.HazardDose(sev, false, res);
                        Check(d0 == sev, "a non-toxic dose was scaled by resistance");
                        Check(d1 >= 0f && d1 <= sev + (res < 0 ? -res * sev : 0f) + 1e-5f, "toxic dose out of range");
                        Check(RM_WreckageKernel.HazardDose(sev, true, 1f) == 0f, "full toxic resistance still took a dose");
                        Check(res <= 1f || d1 == 0f, "over-resistance made a negative or positive dose");
                    }
                }
                catch (Exception e) { fails.Add($"loot seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Fields(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    string[] names = { "scald", "rot", "grey", "blue", "warscar", "flood", "a b", "x" };
                    var model = new HashSet<string>();
                    string csv = r.Next(3) == 0 ? null : r.Next(2) == 0 ? "" : " scald , rot ,, ";
                    if (csv != null) foreach (string k in csv.Split(',').Select(k => k.Trim()).Where(k => k.Length > 0)) model.Add(k);
                    for (int i = 0; i < 25; i++)
                    {
                        Steps++;
                        string key = names[r.Next(names.Length)]; bool on = r.Next(2) == 0;
                        csv = RM_WreckageKernel.SetFieldEnabled(csv, key, on);
                        if (on) model.Remove(key); else model.Add(key);
                        foreach (string n in names) Check(RM_WreckageKernel.FieldDisabled(csv, n) == model.Contains(n), $"after set({key},{on}) the list '{csv}' says {n} disabled={RM_WreckageKernel.FieldDisabled(csv, n)}, model {model.Contains(n)}");
                        Check(csv.Split(',').Count(k => k.Trim() == key) == (on ? 0 : 1), "a key appears twice or not at all");
                        Check(!csv.Contains(" ,") && !csv.Contains(",,") && !csv.StartsWith(","), "the list is not normalised");
                        // a key that is only a substring of another is not disabled by it
                        Check(!RM_WreckageKernel.FieldDisabled("scalded", "scald"), "'scalded' disabled 'scald'");
                    }
                    foreach (bool wf in new[] { false, true })
                        foreach (bool gate in new[] { false, true })
                            foreach (string k in new string[] { null, "", "rot", "scald" })
                            {
                                Steps++;
                                bool got = RM_WreckageKernel.FieldActive(wf, k, " scald", gate);
                                Check(got == (wf && !string.IsNullOrEmpty(k) && k != "scald" && gate), $"FieldActive({wf},{k},{gate}) = {got}");
                            }
                    Check(RM_WreckageKernel.FixedCount(5, 0f, 1f) == 0 && RM_WreckageKernel.FixedCount(5, -2f, 1f) == 0, "density 0 or below still places wrecks");
                    Check(RM_WreckageKernel.FixedCount(4, 1f, 1f) == 4 && RM_WreckageKernel.FixedCount(4, 2f, 0.5f) == 4, "fixed count arithmetic");
                    Check(RM_WreckageKernel.Per10k(3f, 0f) == 0f && RM_WreckageKernel.Per10k(3f, -1f) == 0f, "per-10k density at 0 is not 0");
                    Check(RM_WreckageKernel.ScaledCount(3.4f, 1f) == 3 && RM_WreckageKernel.ScaledCount(3.6f, 1f) == 4, "scaled count rounding");
                    Check(RM_WreckageKernel.ClusterChance(-1f, 0.3f) == 0.3f && RM_WreckageKernel.ClusterChance(0f, 0.3f) == 0f && RM_WreckageKernel.ClusterChance(0.2f, 0.3f) == 0.2f, "cluster chance fallback");
                    Check(RM_WreckageKernel.UseOwnClusterSize(2) && !RM_WreckageKernel.UseOwnClusterSize(1) && !RM_WreckageKernel.UseOwnClusterSize(0), "own cluster size rule");
                    Check(!RM_WreckageKernel.MapAllowed(false, 0, true) && RM_WreckageKernel.MapAllowed(true, 0, false) && !RM_WreckageKernel.MapAllowed(true, 2, false) && RM_WreckageKernel.MapAllowed(true, 2, true), "MapAllowed table");
                }
                catch (Exception e) { fails.Add($"fields seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Place(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++; Steps++;
                try
                {
                    int total = r.Next(0, 40); double pAnchor = r.NextDouble(), pCluster = r.NextDouble(), pMember = r.NextDouble(); int maxSize = r.Next(2, 7);
                    int anchorCalls = 0, anchorOk = 0, members = 0, memberOk = 0, rolls = 0;
                    int placed = RM_WreckageKernel.PlaceField(total,
                        () => { if (++anchorCalls > 5000) throw new Exception("the placement loop did not terminate"); bool ok = r.NextDouble() < pAnchor; if (ok) anchorOk++; return ok; },
                        () => { rolls++; return r.NextDouble() < pCluster; },
                        () => 2 + r.Next(maxSize - 1),
                        () => { members++; bool ok = r.NextDouble() < pMember; if (ok) memberOk++; return ok; });
                    Check(placed >= 0 && placed <= total, $"placed {placed} of {total}");
                    Check(placed == anchorOk + memberOk, "placed is not anchors + cluster members that succeeded");
                    int misses = anchorCalls - anchorOk;
                    Check(misses <= 3, $"{misses} missed anchors, the loop must stop at 3");
                    if (placed < total) { Check(misses == 3, $"stopped short ({placed}/{total}) with only {misses} misses"); Stops++; }
                    else Fills++;
                    if (total == 0) Check(anchorCalls == 0, "tried to place for a zero target");
                    Clusters += memberOk;
                    // everything fits: always reaches the target; nothing fits: exactly three attempts
                    int calls = 0;
                    Check(RM_WreckageKernel.PlaceField(total, () => { calls++; return true; }, () => true, () => 6, () => true) == total, "everything fits but the target was missed");
                    Check(calls <= total, "more anchors than the target");
                    calls = 0;
                    Check(RM_WreckageKernel.PlaceField(Math.Max(1, total), () => { if (++calls > 5000) throw new Exception("the placement loop did not terminate"); return false; }, () => true, () => 6, () => true) == 0 && calls == 3, "nothing fits: not exactly three attempts");
                    // a cluster never overshoots the last slot
                    Check(RM_WreckageKernel.PlaceField(1, () => true, () => true, () => 9, () => true) == 1, "a cluster overshot a target of 1");
                    Check(RM_WreckageKernel.PlaceField(1, () => true, () => { throw new Exception("rolled a cluster with no slot left"); }, () => 9, () => true) == 1, "x");
                    Check(RM_WreckageKernel.PlaceField(5, () => true, () => true, () => 1, () => { throw new Exception("size 1 cluster asked for a member"); }) == 5, "size-1 cluster");
                }
                catch (Exception e) { fails.Add($"place seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("tier", () => Tier(N(1500), S(1))),
                ("loot", () => Loot(N(2500), S(1))),
                ("fields", () => Fields(N(2500), S(1))),
                ("place", () => Place(N(6000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails.Take(8)) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if (only == null && !oneSeed.HasValue && scale >= 1)
            {
                Console.WriteLine($"reached: shifts {Shifts} (rung changes {Rungs}), fields filled {Fills}, stopped short {Stops}, cluster members {Clusters}");
                if (Rungs == 0 || Fills == 0 || Stops == 0 || Clusters == 0) { Console.WriteLine("FAIL wreckage fuzz never reached a path (blind)"); ok = false; }
            }
            Console.WriteLine($"wreckage fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
