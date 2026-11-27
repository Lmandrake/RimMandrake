// Approach B for WreckedMachines: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RM_WreckedMachinesKernel.cs):
//   ladder    the capability ratios for any saved or hand-edited setting: ordered wrecked <= kludged <= refurbished, inside the slider ranges,
//             always below the original's 1.0, in-range input untouched
//   place     where an upper grade may be built (a lower grade of ITS OWN line underneath, reinstalls free, wrecks free) against a random cell
//   emanator  the soothe stage per grade and the strongest-in-range pick, never above the top stage, inert when wrecked
//   salvage   the one salvage rule's arithmetic: stacks keep every unit inside the limit; a retried process cycle pays nothing until its first
//             stack lands and then pays each remaining stack once; cremation pays only for a corpse with the toggle on
//   scale     power output (producers only, never above the original), emanator mood, material counts and research cost under their sliders
//   process   which processes a Kludged and a Refurbished level run: the row's part, everything on the level's def as loaded (a
//             neighbour's patch stays, whether or not the donor has that process too), nothing else, the same when applied again
// A failing case prints `family seed N: message`; --fuzz-seed N replays it. PROVISIONAL: ratios 0.001 / 0.2 / 0.75 are owner-ruled defaults;
// slider ranges (wrecked 0..0.05, kludged 0.05..0.6, refurbished 0.3..0.95) are the shipped UI.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.Shared;
using RimMandrake.WreckedMachines;

namespace RimMandrake.WreckedMachines.SelfTest
{
    internal static class WreckedFuzz
    {
        public static long Cases, Steps, Allowed, Refused, Inverted, Producers;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private static float F(Random r, float lo, float hi) { return lo + (float)r.NextDouble() * (hi - lo); }

        private static List<string> Salvage(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    int total = r.Next(-3, 2000), limit = r.Next(-1, 80);
                    List<int> stacks = RM_SalvageRuleKernel.Stacks(total, limit);
                    Check(stacks.Sum() == Math.Max(0, total), $"stacks of {total} sum to {stacks.Sum()}");
                    Check(stacks.All(s => s > 0 && s <= Math.Max(1, limit)), $"illegal stack in {total} at limit {limit}");

                    // A cycle: the process fails to place N times (full hopper, retried next tick), then places the first stack.
                    int planned = r.Next(0, 6), retries = r.Next(0, 5), paidByUs = 0, paidByProcess = 0;
                    bool planHeld = true;
                    for (int t = 0; t <= retries && planHeld; t++)
                    {
                        Steps++;
                        int placed = t == retries && planned > 0 ? 1 : 0;
                        paidByProcess += placed;
                        paidByUs += RM_SalvageRuleKernel.ExtrasOwed(planned, placed);
                        if (RM_SalvageRuleKernel.CycleOver(planned, placed)) planHeld = false;
                        else Check(paidByUs == 0, $"paid {paidByUs} on a retry");
                    }
                    Check(!planHeld, $"plan of {planned} outlived its cycle");
                    Check(paidByProcess + paidByUs == planned, $"plan of {planned} paid {paidByProcess}+{paidByUs}");

                    bool on = r.Next(2) == 0, corpse = r.Next(2) == 0;
                    Check(RM_SalvageRuleKernel.CremationPays(on, corpse) == (on && corpse), $"cremation on={on} corpse={corpse}");
                }
                catch (Exception e) { fails.Add($"salvage seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Ladder(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int i = 0; i < 40; i++)
                    {
                        Steps++;
                        // anywhere a config can land, including hand-edited nonsense
                        float w = i % 4 == 0 ? F(r, 0f, 0.05f) : F(r, -1f, 3f), k = i % 4 == 0 ? F(r, 0.05f, 0.6f) : F(r, -1f, 3f), rf = i % 4 == 0 ? F(r, 0.3f, 0.95f) : F(r, -1f, 3f);
                        var l = RM_WreckedMachinesKernel.Normalize(w, k, rf);
                        Check(l.wrecked >= 0f && l.wrecked <= l.kludged && l.kludged <= l.refurbished, $"ladder not ordered: {l.wrecked} {l.kludged} {l.refurbished} from {w} {k} {rf}");
                        Check(l.refurbished < 1f && l.refurbished <= 0.95f, $"refurbished {l.refurbished} reaches the original");
                        Check(l.kludged <= 0.6f && l.wrecked <= 0.05f, "a ratio left its slider range");
                        Check(RM_WreckedMachinesKernel.RatioFor(3, l) == 1f, "the original is not exactly 1");
                        for (int g = 0; g < 3; g++) Check(RM_WreckedMachinesKernel.RatioFor(g, l) <= RM_WreckedMachinesKernel.RatioFor(g + 1, l), $"grade {g} is above grade {g + 1}");
                        Check(RM_WreckedMachinesKernel.RatioFor(2, l) < RM_WreckedMachinesKernel.RatioFor(3, l), "refurbished reaches the original");
                        Check(RM_WreckedMachinesKernel.RatioFor(0, l) == l.wrecked && RM_WreckedMachinesKernel.RatioFor(1, l) == l.kludged && RM_WreckedMachinesKernel.RatioFor(2, l) == l.refurbished, "RatioFor mixes grades");
                        bool inRange = w >= 0 && w <= 0.05f && k >= 0.05f && k <= 0.6f && rf >= 0.3f && rf <= 0.95f && k <= rf && w <= k;
                        if (inRange) Check(l.wrecked == w && l.kludged == k && l.refurbished == rf, "an in-range, ordered config was altered");
                        else if (k > rf && k <= 0.6f && rf >= 0.3f && rf <= 0.95f) Inverted++;
                    }
                    var d = RM_WreckedMachinesKernel.Normalize(0.001f, 0.2f, 0.75f);
                    Check(d.wrecked == 0.001f && d.kludged == 0.2f && d.refurbished == 0.75f, "the shipped defaults are altered by Normalize");
                }
                catch (Exception e) { fails.Add($"ladder seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Place(int cases, int seed0)
        {
            var fails = new List<string>();
            string[] lines = { "smelter", "cell", "emanator" };
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int i = 0; i < 30; i++)
                    {
                        Steps++;
                        bool require = r.Next(5) != 0, reinstall = r.Next(6) == 0, hasExt = r.Next(8) != 0; int grade = r.Next(4); string line = lines[r.Next(3)];
                        int n = r.Next(0, 5); var ol = new List<string>(); var og = new List<int>();
                        for (int j = 0; j < n; j++) { ol.Add(lines[r.Next(3)]); og.Add(r.Next(4)); }
                        bool got = RM_WreckedMachinesKernel.AllowsPlacing(require, reinstall, hasExt, grade, line, ol, og);
                        bool lower = false; for (int j = 0; j < n; j++) if (ol[j] == line && og[j] < grade) lower = true;
                        bool want = !require || reinstall || !hasExt || grade == 0 || lower;
                        Check(got == want, $"AllowsPlacing(req {require}, reinstall {reinstall}, ext {hasExt}, grade {grade}, line {line}, cell {string.Join(",", ol.Select((x, q) => x + ":" + og[q]))}) = {got}, spec {want}");
                        if (got) Allowed++; else Refused++;
                        if (require && !reinstall && hasExt && grade > 0 && got) Check(lower, "an upper grade went on open ground / over another line / over an equal or higher grade");
                        if (require && !reinstall && hasExt && grade > 0 && n == 0) Check(!got, "an upper grade was allowed on an empty cell");
                        // a lower grade of ANOTHER line never counts
                        if (require && !reinstall && hasExt && grade > 0) Check(!RM_WreckedMachinesKernel.AllowsPlacing(true, false, true, grade, line, new[] { "other" }, new[] { 0 }), "a lower grade of another line allowed the build");
                        if (require && !reinstall && hasExt && grade > 0) Check(!RM_WreckedMachinesKernel.AllowsPlacing(true, false, true, grade, line, new[] { line }, new[] { grade }), "the same grade underneath allowed the build");
                        if (require && !reinstall && hasExt && grade > 0) Check(!RM_WreckedMachinesKernel.AllowsPlacing(true, false, true, grade, line, new[] { line }, new[] { 3 }), "a higher grade underneath allowed the build");
                    }
                }
                catch (Exception e) { fails.Add($"place seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Emanator(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    for (int sc = 1; sc <= 4; sc++)
                    {
                        Steps++;
                        Check(RM_WreckedMachinesKernel.EmanatorStage(0, sc) == -1, "a wrecked emanator soothes");
                        for (int g = 1; g <= 3; g++)
                        {
                            int st = RM_WreckedMachinesKernel.EmanatorStage(g, sc);
                            Check(st >= 0 && st <= sc - 1, $"stage {st} outside 0..{sc - 1} for grade {g}");
                            Check(st == Math.Min(g - 1, sc - 1), "stage is not min(grade - 1, top)");
                            if (g > 1) Check(st >= RM_WreckedMachinesKernel.EmanatorStage(g - 1, sc), "a higher grade soothes less");
                        }
                    }
                    // strongest in range wins: a list of nearby grades, the best stage is the max of the stages
                    int n = r.Next(0, 6); var gs = new List<int>(); for (int i = 0; i < n; i++) gs.Add(r.Next(4));
                    int best = -1; foreach (int g in gs) best = Math.Max(best, RM_WreckedMachinesKernel.EmanatorStage(g, 2));
                    Check(best == (gs.Any(g => g > 0) ? Math.Min(gs.Max() - 1, 1) : -1), "strongest nearby emanator is not the highest grade's stage");
                    Check(RM_WreckedMachinesKernel.EmanatorStage(3, 2) == 1, "the original soothes beyond the top stage");
                }
                catch (Exception e) { fails.Add($"emanator seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        private static List<string> Scale(int cases, int seed0)
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
                        float orig = i == 0 ? 0f : i % 3 == 0 ? F(r, 0f, 500f) : -F(r, 1f, 6000f);   // producers are negative draws
                        var l = RM_WreckedMachinesKernel.Normalize(F(r, 0f, 0.05f), F(r, 0.05f, 0.6f), F(r, 0.3f, 0.95f));
                        float? prev = null;
                        for (int g = 0; g < 4; g++)
                        {
                            float? o = RM_WreckedMachinesKernel.ScaledPowerOutput(orig, RM_WreckedMachinesKernel.RatioFor(g, l));
                            if (orig >= 0f) { Check(o == null, "a consumer's draw was rewritten"); continue; }
                            Producers++;
                            Check(o != null, "a producer was left unscaled");
                            Check(o.Value <= 0f && o.Value >= orig - 1e-3f, $"salvaged output {o} outside [original {orig}, 0]: a bodge out-produces the original");
                            Check(Math.Abs(o.Value - orig * RM_WreckedMachinesKernel.RatioFor(g, l)) <= 1e-3f + Math.Abs(orig) * 1e-5f, $"salvaged output {o} is not original {orig} x ratio {RM_WreckedMachinesKernel.RatioFor(g, l)}");
                            if (g < 3) Check(Math.Abs(o.Value) <= Math.Abs(orig) * 0.951f + 1e-3f, "a salvaged grade matches or nears the original");
                            if (prev != null) Check(Math.Abs(o.Value) >= Math.Abs(prev.Value) - 1e-3f, "a higher grade produces less");
                            prev = o;
                        }
                        float vm = F(r, 0.5f, 20f);
                        Check(RM_WreckedMachinesKernel.EmanatorMood(vm, l.kludged) < RM_WreckedMachinesKernel.EmanatorMood(vm, l.refurbished) + 1e-6f, "kludged emanator out-soothes refurbished");
                        Check(RM_WreckedMachinesKernel.EmanatorMood(vm, l.refurbished) < vm, "a refurbished emanator matches or beats the vanilla one");
                        int bc = r.Next(1, 200); float fac = F(r, 0.25f, 4f);
                        int sc2 = RM_WreckedMachinesKernel.ScaledCount(bc, fac);
                        Check(sc2 >= 1, "a material count fell below one");
                        Check(Math.Abs(sc2 - bc * (double)fac) <= 0.5 + 1e-4 || bc * fac < 1, $"count {bc} x {fac} = {bc * fac} became {sc2}");
                        Check(RM_WreckedMachinesKernel.ScaledCount(bc, 1f) == bc, "factor 1 changed a count");
                        Check(RM_WreckedMachinesKernel.ScaledResearch(2000f, 1f) == 2000f && RM_WreckedMachinesKernel.ScaledResearch(2000f, 0.25f) == 500f && RM_WreckedMachinesKernel.ScaledResearch(0.5f, 0.25f) == 1f, "research cost arithmetic");
                    }
                }
                catch (Exception e) { fails.Add($"scale seed {seed}: {e.Message}"); }
            }
            return fails;
        }

        // The situations the game can make for a level's process list, and what is read on each:
        //   the donor's list as loaded: 0 to 9 processes (0 = a donor with no list at all), some of them added by a neighbour mod;
        //   the row: names its part (1 to 3 of the donor's own processes, one of them possibly from a mod that is not loaded, so it
        //     resolves to nothing), or takes the donor's first N (N from 1 to past the end), or neither;
        //   the Kludged def as loaded: what the stamp wrote (the row's part of the donor's own list; nothing when the donor's
        //     processes are made in code at startup), then 0 to 3 processes that neighbours patched on. Each neighbour process is
        //     on the donor too, or on our def only (the Armoury's durasteel is on both);
        //   the Refurbished def as loaded: the donor's own list or nothing, then 0 to 3 neighbour processes, on the donor too or not;
        //   nulls and repeats in a loaded list; the lists applied a second time (settings applied again).
        // Left out: a process def removed after startup, and a mod that edits a list after our startup code (neither is seen).
        public static long NeighbourOnBoth, MadeInCode, RowNamed, RowCounted;
        private static List<string> Process(int cases, int seed0)
        {
            var fails = new List<string>();
            for (int c = 0; c < cases; c++)
            {
                int seed = seed0 + c; var r = new Random(seed); Cases++;
                try
                {
                    int own = r.Next(0, 7);                                   // the donor's own processes: d0..d(own-1)
                    var donorOwn = Enumerable.Range(0, own).Select(i => "d" + i).ToList();
                    bool inCode = own > 0 && r.Next(4) == 0;                   // the donor's XML holds no list; the factory mod's code fills it
                    int nn = r.Next(0, 4);                                    // neighbour processes n0..n(nn-1)
                    var onDonor = new List<string>(); var onKludged = new List<string>(); var onRefurbished = new List<string>();
                    for (int i = 0; i < nn; i++)
                    {
                        int where = r.Next(1, 8);                             // bit 1 the donor, 2 our Kludged, 4 our Refurbished
                        if ((where & 1) != 0) onDonor.Add("n" + i);
                        if ((where & 2) != 0) onKludged.Add("n" + i);
                        if ((where & 4) != 0) onRefurbished.Add("n" + i);
                    }
                    List<string> donor = donorOwn.Concat(onDonor).ToList();

                    int mode = own == 0 ? 2 : r.Next(3);                      // 0 the row names, 1 the row counts, 2 neither
                    if (inCode && mode == 0) mode = 1;                        // onboard.py refuses a name the donor's XML does not have
                    var named = new List<string>(); int count = 0;
                    List<string> stamped;
                    if (mode == 0)
                    {
                        named = donorOwn.OrderBy(_ => r.Next()).Take(r.Next(1, 4)).ToList();
                        stamped = named.ToList();
                        if (r.Next(5) == 0) named[r.Next(named.Count)] = null; // a named process of a mod that is not loaded
                        RowNamed++;
                    }
                    else if (mode == 1)
                    {
                        count = r.Next(1, own + 3);
                        stamped = inCode ? new List<string>() : donorOwn.Take(count).ToList();
                        RowCounted++;
                    }
                    else stamped = own > 0 && r.Next(2) == 0 ? donorOwn.Take(r.Next(1, own + 1)).ToList() : new List<string>();
                    if (inCode) MadeInCode++;

                    List<string> kLoaded = stamped.Concat(onKludged).ToList();
                    List<string> rLoaded = (inCode || r.Next(3) == 0 ? new List<string>() : donorOwn.ToList()).Concat(onRefurbished).ToList();
                    if (r.Next(6) == 0 && kLoaded.Count > 0) kLoaded.Insert(r.Next(kLoaded.Count + 1), kLoaded[r.Next(kLoaded.Count)]);
                    if (r.Next(6) == 0) kLoaded.Insert(r.Next(kLoaded.Count + 1), null);
                    if (r.Next(6) == 0) rLoaded.Insert(r.Next(rLoaded.Count + 1), null);

                    List<string> rowPart = mode == 0 ? named.Where(p => p != null).ToList() : mode == 1 ? donor.Take(count).ToList() : new List<string>();
                    string what = $"donor [{string.Join(",", donor)}] row {(mode == 0 ? "names [" + string.Join(",", named.Select(p => p ?? "null")) + "]" : mode == 1 ? "counts " + count : "says nothing")} Kludged as loaded [{string.Join(",", kLoaded.Select(p => p ?? "null"))}]";

                    List<string> k = RM_WreckedMachinesKernel.KludgedProcesses(donor, named, count, kLoaded);
                    Steps++;
                    foreach (string p in kLoaded.Where(p => p != null))
                        Check(k.Contains(p), $"the Kludged level lost {p}, which is on its def as loaded: {what} -> [{string.Join(",", k)}]");
                    foreach (string p in rowPart)
                        Check(k.Contains(p), $"the Kludged level lacks {p} of the row's part: {what} -> [{string.Join(",", k)}]");
                    bool fallback = rowPart.Count == 0 && !kLoaded.Any(p => p != null);
                    foreach (string p in k)
                        Check(p != null && (rowPart.Contains(p) || kLoaded.Contains(p) || (fallback && donor.Count > 0 && p == donor[0])),
                            $"the Kludged level runs {p ?? "null"}, which neither the row nor its def gives it: {what} -> [{string.Join(",", k)}]");
                    Check(k.Distinct().Count() == k.Count, $"a process twice on the Kludged level: {what} -> [{string.Join(",", k)}]");
                    Check(donor.Count == 0 || k.Count > 0, $"a Kludged level with no process though the donor has some: {what}");
                    Check(RM_WreckedMachinesKernel.KludgedProcesses(donor, named, count, k).SequenceEqual(k),
                        $"applied a second time, the Kludged list changes: {what} -> [{string.Join(",", k)}]");
                    if (onKludged.Any(p => onDonor.Contains(p))) NeighbourOnBoth++;

                    List<string> rf = RM_WreckedMachinesKernel.RefurbishedProcesses(donor, rLoaded);
                    Steps++;
                    foreach (string p in donor.Concat(rLoaded.Where(p => p != null)))
                        Check(rf.Contains(p), $"the Refurbished level lacks {p}: donor [{string.Join(",", donor)}] as loaded [{string.Join(",", rLoaded.Select(q => q ?? "null"))}] -> [{string.Join(",", rf)}]");
                    foreach (string p in rf)
                        Check(p != null && (donor.Contains(p) || rLoaded.Contains(p)), $"the Refurbished level runs {p ?? "null"} from nowhere");
                    Check(rf.Distinct().Count() == rf.Count, $"a process twice on the Refurbished level: [{string.Join(",", rf)}]");
                    Check(rf.Take(donor.Count).SequenceEqual(donor), $"the Refurbished level does not start with the donor's list in the donor's order: [{string.Join(",", rf)}]");
                    Check(RM_WreckedMachinesKernel.RefurbishedProcesses(donor, rf).SequenceEqual(rf), "applied a second time, the Refurbished list changes");
                }
                catch (Exception e) { fails.Add($"process seed {seed}: {e.Message}"); }
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
                ("ladder", () => Ladder(N(3000), S(1))),
                ("place", () => Place(N(4000), S(1))),
                ("emanator", () => Emanator(N(2000), S(1))),
                ("scale", () => Scale(N(3000), S(1))),
                ("salvage", () => Salvage(N(3000), S(1))),
                ("process", () => Process(N(6000), S(1))),
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
                Console.WriteLine($"reached: placements allowed {Allowed}, refused {Refused}, producers scaled {Producers}, inverted slider pairs repaired {Inverted}");
                if (Allowed == 0 || Refused == 0 || Producers == 0 || Inverted == 0) { Console.WriteLine("FAIL wrecked-machines fuzz never reached a path (blind)"); ok = false; }
                Console.WriteLine($"reached: process lists with a neighbour's process on the donor and on our Kludged def {NeighbourOnBoth}, a donor list made in code {MadeInCode}, a row that names {RowNamed}, a row that counts {RowCounted}");
                if (NeighbourOnBoth == 0 || MadeInCode == 0 || RowNamed == 0 || RowCounted == 0) { Console.WriteLine("FAIL the process-list fuzz never reached a situation (blind)"); ok = false; }
            }
            Console.WriteLine($"wreckedmachines fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
