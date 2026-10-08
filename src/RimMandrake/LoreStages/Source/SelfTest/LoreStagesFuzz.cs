// Approach B for LoreStages: seeded fuzz that drives the PRODUCTION applier (LoreStageApplier.ResetAndApply) on REAL engine defs
// (BiomeDef, HediffDef, ThingDef from Assembly-CSharp.dll, same fixtures as Program.cs) against an independent restatement of the rules:
//   choose   the kernel's rung pick against a sort oracle (highest rung at or below the stage, first listed wins a tie, text-less skipped)
//   ladder   random tables over a small def/field space (collisions between ladders happen on purpose), random stage sequences (up, down,
//            zero, toggle off, reapply, a table removed): every field must equal the oracle after every apply, the memoized descriptions
//            must show the new text, the return value must count the staged fields, and each problem is warned about at most once
//   config   RM_LoreStageTableDef.ConfigErrors against per-rule counts; ladder key fallback; stage clamp; master toggle
// A failing case is printed as `family seed N: step K: message`; --fuzz-seed N replays it.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.LoreStages.SelfTest
{
    internal static class LoreStagesFuzz
    {
        public static long Cases, Steps, StagedFields, Collisions, StageDowns, ToggleOffs, WarnsSeen, TablesDropped;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        // ════════════════════════ choose ════════════════════════
        private static List<string> Choose(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 7919 + 3);
                try
                {
                    int count = r.Next(0, 9);
                    var st = Enumerable.Range(0, count).Select(i => r.Next(8) == 0 ? -r.Next(1, 3) : r.Next(0, 9)).ToList();
                    var tx = Enumerable.Range(0, count).Select(i => r.Next(6) != 0).ToList();
                    for (int stage = -1; stage <= 10; stage++)
                    {
                        int got = RM_LoreStageKernel.ChooseRung(st, tx, stage);
                        // oracle: the candidates, best = max stage, first index wins
                        var cand = Enumerable.Range(0, count).Where(i => tx[i] && st[i] <= stage).ToList();
                        if (cand.Count == 0) { Check(got == -1, "stage " + stage + " picked " + got + " but no rung applies"); continue; }
                        int top = cand.Max(i => st[i]);
                        int want = cand.First(i => st[i] == top);
                        Check(got == want, "stage " + stage + " picked rung " + got + " (stage " + (got >= 0 ? st[got] : -99) + "), oracle says rung " + want + " rungs [" + string.Join(",", st.Select((x, i) => x + (tx[i] ? "" : "!"))) + "]");
                        if (stage > -1) Check(RM_LoreStageKernel.ChooseRung(st, tx, stage - 1) <= -1 || st[RM_LoreStageKernel.ChooseRung(st, tx, stage - 1)] <= st[got], "the shown rung fell as the stage rose");
                    }
                }
                catch (Exception e) { fails.Add("choose seed " + s + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ ladder ════════════════════════
        private sealed class World
        {
            public BiomeDef biomeA, biomeB; public HediffDef hedA, hedB; public ThingDef item;
            public Dictionary<string, string> pristine = new Dictionary<string, string>();   // "def|field" -> shipped text
            public Def Resolve(string type, string name)
            {
                if (type == "BiomeDef" && name == "FZ_BiomeA") return biomeA;
                if (type == "BiomeDef" && name == "FZ_BiomeB") return biomeB;
                if (type == "HediffDef" && name == "FZ_HediffA") return hedA;
                if (type == "HediffDef" && name == "FZ_HediffB") return hedB;
                if (type == "ThingDef" && name == "FZ_Item") return item;
                return null;
            }
            public string Read(string name, string field)
            {
                Def d = Resolve(name.StartsWith("FZ_Biome") ? "BiomeDef" : name.StartsWith("FZ_Hed") ? "HediffDef" : "ThingDef", name);
                return (string)d.GetType().GetField(field).GetValue(d);
            }
        }

        // the address menu: (defType, defName, field, valid?)
        private static readonly (string type, string name, string field)[] Valid =
        {
            ("BiomeDef", "FZ_BiomeA", "description"), ("BiomeDef", "FZ_BiomeA", "settleWarning"), ("BiomeDef", "FZ_BiomeB", "description"),
            ("HediffDef", "FZ_HediffA", "description"), ("HediffDef", "FZ_HediffB", "description"), ("ThingDef", "FZ_Item", "description"),
            ("BiomeDef", "FZ_BiomeB", "label"),
        };
        private static readonly (string type, string name, string field)[] Invalid =
        {
            ("BiomeDef", "FZ_NoSuchBiome", "description"), ("ThingDef", "FZ_BiomeA", "description"), ("BiomeDef", "FZ_BiomeA", "noSuchField"),
            ("BiomeDef", "FZ_BiomeA", "workerClass"), ("HediffDef", "FZ_HediffA", "defName_"),
        };

        private static World MakeWorld(Random r)
        {
            LoreStageApplier.ForgetBaselinesForTesting();
            var w = new World
            {
                biomeA = new BiomeDef { defName = "FZ_BiomeA", description = "SHIPPED biomeA.description", settleWarning = "SHIPPED biomeA.settleWarning", label = "SHIPPED biomeA.label" },
                biomeB = new BiomeDef { defName = "FZ_BiomeB", description = "SHIPPED biomeB.description", settleWarning = "SHIPPED biomeB.settleWarning", label = "SHIPPED biomeB.label" },
                hedA = new HediffDef { defName = "FZ_HediffA", description = "SHIPPED hediffA.description" },
                hedB = new HediffDef { defName = "FZ_HediffB", description = "SHIPPED hediffB.description" },
            };
            var item = (ThingDef)System.Runtime.Serialization.FormatterServices.GetUninitializedObject(typeof(ThingDef));
            item.defName = "FZ_Item"; item.description = "SHIPPED item.description";
            w.item = item;
            // Def equality (the applier's HashSet<Def>) is by defNameHash, which only ResolveDefNameHash sets: without it every def of a type
            // is "equal" and two distinct hediffs collapse into one. The loaded game always has it set; a harness def must too.
            foreach (Def d in new Def[] { w.biomeA, w.biomeB, w.hedA, w.hedB, item }) d.ResolveDefNameHash();
            foreach (var a in Valid) w.pristine[a.name + "|" + a.field] = w.Read(a.name, a.field);
            return w;
        }

        private static RM_LoreStageTableDef MakeTable(Random r, int idx, string[] ladders)
        {
            var t = new RM_LoreStageTableDef { defName = "FZ_Table" + idx, ladderId = r.Next(6) == 0 ? null : ladders[r.Next(ladders.Length)], maxStage = r.Next(3) == 0 ? 0 : r.Next(2, 7), targets = new List<LoreStageTarget>() };
            int nt = r.Next(1, 5);
            for (int i = 0; i < nt; i++)
            {
                if (r.Next(25) == 0) { t.targets.Add(null); continue; }
                var addr = r.Next(5) == 0 ? Invalid[r.Next(Invalid.Length)] : Valid[r.Next(Valid.Length)];
                var tg = new LoreStageTarget { defType = addr.type, defName = addr.name, field = addr.field, stages = new List<LoreStageText>() };
                if (r.Next(30) == 0) tg.defName = null;           // incomplete target
                int nr = r.Next(0, 5);
                for (int k = 0; k < nr; k++)
                {
                    if (r.Next(30) == 0) { tg.stages.Add(null); continue; }
                    tg.stages.Add(new LoreStageText { stage = r.Next(12) == 0 ? -1 : r.Next(0, 8), text = r.Next(10) == 0 ? null : "T" + idx + "." + i + "." + k + "@" });
                }
                if (r.Next(40) == 0) tg.stages = null;
                t.targets.Add(tg);
            }
            return t;
        }

        // independent restatement of the whole apply
        private static Dictionary<string, string> Expected(World w, List<RM_LoreStageTableDef> tables, Func<string, int> stageOf, out int applied, HashSet<string> expectedWarnKinds)
        {
            var exp = new Dictionary<string, string>(w.pristine);
            applied = 0;
            foreach (var t in tables)
            {
                if (t == null || t.targets == null) continue;
                int stage = stageOf(string.IsNullOrEmpty(t.ladderId) ? t.defName : t.ladderId);
                foreach (var tg in t.targets)
                {
                    if (tg == null) continue;
                    if (string.IsNullOrEmpty(tg.defType) || string.IsNullOrEmpty(tg.defName) || string.IsNullOrEmpty(tg.field)) { expectedWarnKinds.Add(t.defName + ":incomplete-target"); continue; }
                    Def d = w.Resolve(tg.defType, tg.defName);
                    if (d == null) { expectedWarnKinds.Add(t.defName + ":missing:" + tg.defType + ":" + tg.defName); continue; }
                    var fi = d.GetType().GetField(tg.field, System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
                    if (fi == null || fi.FieldType != typeof(string)) { expectedWarnKinds.Add(t.defName + ":field:" + tg.defType + ":" + tg.field); continue; }
                    string text = null; int top = int.MinValue;
                    if (tg.stages != null)
                        foreach (var rung in tg.stages)
                        {
                            if (rung == null || rung.text == null) continue;
                            if (rung.stage <= stage && rung.stage > top) { top = rung.stage; text = rung.text; }
                        }
                    if (text != null) { exp[tg.defName + "|" + tg.field] = text; applied++; }
                }
            }
            return exp;
        }

        private static List<string> Ladder(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++;
                var r = new Random(s * 131 + 29);
                int step = 0;
                try
                {
                    var w = MakeWorld(r);
                    string[] ladders = { "LA", "LB", "LC" };
                    var tables = new List<RM_LoreStageTableDef>();
                    int nt = r.Next(1, 5);
                    for (int i = 0; i < nt; i++) tables.Add(MakeTable(r, i, ladders));
                    var stages = new Dictionary<string, int>();
                    bool enabled = true;
                    var warnings = new List<string>();
                    var warnKinds = new HashSet<string>();
                    int lastSumStage = 0;
                    int actions = 4 + r.Next(14);
                    for (int a = 0; a < actions; a++)
                    {
                        step = a;
                        Steps++;
                        int kind = r.Next(10);
                        if (kind < 4) { string l = ladders[r.Next(ladders.Length)]; int ns = r.Next(0, 9); if (ns < (stages.TryGetValue(l, out int old) ? old : 0)) StageDowns++; stages[l] = ns; }
                        else if (kind == 4) { string l = ladders[r.Next(ladders.Length)]; stages[l] = 0; StageDowns++; }
                        else if (kind == 5) { enabled = !enabled; if (!enabled) ToggleOffs++; }
                        else if (kind == 6 && tables.Count > 1) { tables.RemoveAt(r.Next(tables.Count)); TablesDropped++; }
                        else if (kind == 7) { tables.Add(MakeTable(r, 10 + a, ladders)); }
                        // kinds 8,9: just reapply
                        Func<string, int> stageOf = id => RM_LoreStageKernel.EffectiveStage(enabled, stages.TryGetValue(id, out int v) ? v : 0);
                        lastSumStage = stages.Values.Sum();
                        // prime the memoized descriptions so a skipped cache clear shows up
                        string pi = w.item.DescriptionDetailed, pa = w.hedA.Description, pb = w.hedB.Description;
                        _ = pi + pa + pb;
                        int applied = LoreStageApplier.ResetAndApply(tables, stageOf, w.Resolve, m => warnings.Add(m));
                        var expWarn = new HashSet<string>();
                        var exp = Expected(w, tables, stageOf, out int expApplied, expWarn);
                        foreach (var kv in exp)
                        {
                            string[] key = kv.Key.Split('|');
                            Check(w.Read(key[0], key[1]) == kv.Value, key[0] + "." + key[1] + " reads <" + w.Read(key[0], key[1]) + "> but the oracle says <" + kv.Value + ">");
                        }
                        Check(applied == expApplied, "ResetAndApply returned " + applied + ", expected " + expApplied + " staged fields");
                        Check(w.item.DescriptionDetailed == w.item.description, "the item's memoized DescriptionDetailed is stale");
                        Check(w.hedA.Description == w.hedA.description, "hediffA memoized Description <" + w.hedA.Description + "> but its field reads <" + w.hedA.description + ">");
                        Check(w.hedB.Description == w.hedB.description, "hediffB memoized Description <" + w.hedB.Description + "> but its field reads <" + w.hedB.description + ">");
                        // warnings: at most once each, over the whole case
                        Check(warnings.Distinct().Count() == warnings.Count, "a problem was warned about twice");
                        WarnsSeen = Math.Max(WarnsSeen, warnings.Count);
                        StagedFields += applied;
                        // two tables staging the same field with an applicable rung each is the collision the last-table-wins rule covers
                        var hits = new Dictionary<string, int>();
                        foreach (var t in tables) if (t?.targets != null) foreach (var tg in t.targets) if (tg?.stages != null && !string.IsNullOrEmpty(tg.defName) && w.Resolve(tg.defType ?? "", tg.defName) != null)
                                    hits[tg.defName + "|" + tg.field] = hits.TryGetValue(tg.defName + "|" + tg.field, out int c) ? c + 1 : 1;
                        if (hits.Values.Any(c => c > 1)) Collisions++;
                    }
                    // finally: every ladder back to 0 with the toggle off must read the stage-0 view; a field no table addresses is shipped text
                    Func<string, int> zero = id => 0;
                    LoreStageApplier.ResetAndApply(tables, zero, w.Resolve, m => { });
                    var exp0 = Expected(w, tables, zero, out int _, new HashSet<string>());
                    foreach (var kv in exp0) { string[] key = kv.Key.Split('|'); Check(w.Read(key[0], key[1]) == kv.Value, "after returning every ladder to 0, " + key[0] + "." + key[1] + " reads <" + w.Read(key[0], key[1]) + "> not <" + kv.Value + ">"); }
                    _ = lastSumStage;
                }
                catch (Exception e) { fails.Add("ladder seed " + s + ": step " + step + ": " + e.Message); }
            }
            return fails;
        }

        // ════════════════════════ config ════════════════════════
        private static List<string> Config(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = seed0; s < seed0 + n && fails.Count < 4; s++)
            {
                Cases++; Steps++;
                var r = new Random(s * 977 + 5);
                try
                {
                    var t = new RM_LoreStageTableDef { defName = "FZ_Cfg", ladderId = r.Next(3) == 0 ? "" : "ID" + r.Next(5), maxStage = r.Next(3) == 0 ? 0 : r.Next(1, 7), targets = new List<LoreStageTarget>() };
                    Check(t.LadderId == (string.IsNullOrEmpty(t.ladderId) ? "FZ_Cfg" : t.ladderId), "LadderId fallback broke");
                    int nr = r.Next(1, 8);
                    var tg = new LoreStageTarget { defType = "BiomeDef", defName = "FZ_BiomeA", field = "description", stages = new List<LoreStageText>() };
                    int dup = 0, neg = 0, above = 0, notext = 0, nulls = 0; var seen = new HashSet<int>();
                    for (int k = 0; k < nr; k++)
                    {
                        if (r.Next(10) == 0) { tg.stages.Add(null); nulls++; continue; }
                        var rung = new LoreStageText { stage = r.Next(8) == 0 ? -r.Next(1, 3) : r.Next(0, 9), text = r.Next(7) == 0 ? null : "x" };
                        tg.stages.Add(rung);
                        if (!seen.Add(rung.stage)) dup++;
                        if (rung.stage < 0) neg++;
                        if (t.maxStage > 0 && rung.stage > t.maxStage) above++;
                        if (rung.text == null) notext++;
                    }
                    t.targets.Add(tg);
                    var errs = t.ConfigErrors().ToList();
                    int Count(string frag) { return errs.Count(e => e.Contains(frag)); }
                    Check(Count("duplicate stage") == dup, "duplicate-stage reports " + Count("duplicate stage") + ", oracle " + dup + " :: " + string.Join(" | ", errs));
                    Check(Count("negative stage") == neg, "negative-stage reports " + Count("negative stage") + ", oracle " + neg);
                    Check(Count("above maxStage") == above, "above-maxStage reports " + Count("above maxStage") + ", oracle " + above + " (maxStage " + t.maxStage + ")");
                    Check(Count("has no text") == notext, "no-text reports " + Count("has no text") + ", oracle " + notext);
                    Check(Count("null stage entry") == nulls, "null-entry reports " + Count("null stage entry") + ", oracle " + nulls);
                    // clamp + toggle
                    int stage = r.Next(-3, 12), max = r.Next(0, 6);
                    int c = RM_LoreStageKernel.ClampStage(stage, max);
                    Check(c >= 0 && (max <= 0 || c <= max), "clamped stage " + c + " outside 0.." + max);
                    Check(stage < 0 ? c == 0 : (max > 0 && stage > max ? c == max : c == stage), "clamp(" + stage + "," + max + ") = " + c);
                    Check(RM_LoreStageKernel.ClampStage(c, max) == c, "clamp is not idempotent");
                    Check(RM_LoreStageKernel.EffectiveStage(false, stage) == 0 && RM_LoreStageKernel.EffectiveStage(true, stage) == stage, "master toggle");
                }
                catch (Exception e) { fails.Add("config seed " + s + ": " + e.Message); }
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
                ("choose", () => Choose(N(6000), S(1))),
                ("ladder", () => Ladder(N(5000), S(1))),
                ("config", () => Config(N(5000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            if (only == null || only == "ladder")
            {
                Console.WriteLine($"reached: staged fields {StagedFields}, ladder collisions {Collisions}, stage downs {StageDowns}, toggle offs {ToggleOffs}, tables dropped {TablesDropped}, most warnings in a case {WarnsSeen}");
                if (!oneSeed.HasValue && scale >= 1 && (StagedFields == 0 || Collisions == 0 || StageDowns == 0 || ToggleOffs == 0 || TablesDropped == 0 || WarnsSeen == 0)) { Console.WriteLine("FAIL the ladder fuzz never reached staging, a collision, a stage down, a toggle, a dropped table and a warning (blind)"); ok = false; }
            }
            Console.WriteLine($"lorestages fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
