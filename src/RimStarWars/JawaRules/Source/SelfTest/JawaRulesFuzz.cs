// Approach B for JawaRules: seeded fuzz over the Verse-free kernel the mod calls (../Kernel/RSW_JawaRulesKernel.cs):
//   hood   the swim-hood postfix and the always-on fallback hood against a fake render engine (flag masking, headgear visibility, other gates):
//          a Jawa's real hood stays drawn while swimming, nothing else changes, and the fallback draws exactly when the real hood will not
//   rules  the small rule gates (no-sow, relations tracker, pet names, pawn-kind redress, world-label values) on evolving pawn populations
// A failing action sequence is shrunk (delta debugging) and printed as `family seed N: message | actions`.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace RimMandrake.StarWars.JawaRules.SelfTest
{
    internal static class JawaRulesFuzz
    {
        public static long Cases, Steps, SwimKept, SwimAsked, Fallbacks, RealDraws, Gaps, FailOpen, Named, Redressed, Sown;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            for (int chunk = Math.Max(1, cur.Count / 2); chunk >= 1; chunk /= 2)
            {
                bool progress = true;
                while (progress)
                {
                    progress = false;
                    for (int i = 0; i + chunk <= cur.Count; i++)
                    {
                        var trial = new List<T>(cur);
                        trial.RemoveRange(i, chunk);
                        if (fails(trial)) { cur = trial; progress = true; break; }
                    }
                }
            }
            return cur;
        }

        private struct Act
        {
            public int kind, a, b, c; public bool f;
            public override string ToString() { return "k" + kind + "(" + a + "," + b + "," + c + (f ? ",T" : "") + ")"; }
        }

        private static Act[] Gen(Random r, int len, int[] kindWeights)
        {
            int total = kindWeights.Sum();
            var a = new Act[len];
            for (int i = 0; i < len; i++)
            {
                int k = r.Next(total), kind = 0;
                while (k >= kindWeights[kind]) { k -= kindWeights[kind]; kind++; }
                a[i] = new Act { kind = kind, a = r.Next(1 << 16), b = r.Next(1 << 16), c = r.Next(1 << 16), f = r.Next(2) == 0 };
            }
            return a;
        }

        private static List<string> Family(string name, int n, int seed0, int[] weights, int minLen, int spread, Func<IList<Act>, int, bool, string> run)
        {
            var fails = new List<string>();
            for (int i = 0; i < n; i++)
            {
                int seed = seed0 + i; var r = new Random(seed);
                var acts = Gen(r, minLen + r.Next(spread), weights); Cases++;
                if (run(acts, seed, true) == null) continue;
                var small = Shrink(acts.ToList(), t => run(t, seed, false) != null);
                fails.Add($"{name} seed {seed}: {run(small, seed, false)} | {string.Join(" ", small)}");
                if (fails.Count >= 3) break;
            }
            return fails;
        }

        // ════════════════════════ hood ════════════════════════
        // kinds: 0 draw, 1 settings, 2 wardrobe change, 3 bed/map change
        private static string RunHood(IList<Act> acts, int seed, bool count)
        {
            bool swimSetting = true, wearsHood = true, hoodResolved = true, tracker = true, bedHides = false, hatsOnlyOnMap = false, onMap = true; int stepNo = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 1: swimSetting = (a.a & 7) != 0; break;
                        case 2: wearsHood = (a.a & 3) != 0; hoodResolved = (a.b & 7) != 0; tracker = (a.c & 7) != 0; break;
                        case 3: bedHides = (a.a & 3) == 0; hatsOnlyOnMap = (a.b & 3) == 0; onMap = (a.c & 3) != 0; break;
                        default:
                            {
                                bool swimming = (a.a & 1) != 0, portrait = (a.a & 6) == 0 && (a.a & 8) != 0;
                                int rawFlags = (a.b & 0xFF) | ((a.c & 1) != 0 ? 0x60 : 0);          // what the renderer would pass when not swimming
                                bool otherGates = (a.c & 6) != 0, fallbackBase = (a.c & 24) != 0, kept = (a.a & 48) != 0, reentry = (a.a & 192) == 192;
                                // the engine's own swim masking happens BEFORE the worker is asked
                                int flags = swimming ? rawFlags & ~0xE0 : rawFlags;
                                Func<int, bool> visible = f => (f & 0x60) == 0x60 && !bedHides && !(hatsOnlyOnMap && !onMap);
                                Func<int, bool> vanilla = f => otherGates && visible(f);
                                bool applies = RSW_HoodKernel.SwimForceApplies(swimSetting, swimming, portrait);
                                Check(applies == (swimSetting && swimming && !portrait), "SwimForceApplies");
                                Check(RSW_HoodKernel.EffectiveFlags(flags, applies) == (applies ? (flags | 0x60) : flags), "EffectiveFlags");
                                Check((RSW_HoodKernel.EffectiveFlags(flags, true) & ~0x60) == (flags & ~0x60), "EffectiveFlags changed an unrelated flag");
                                int asks = 0;
                                bool vanillaResult = vanilla(flags);
                                // the real hood node
                                bool final = RSW_HoodKernel.Postfix(vanillaResult, reentry, applies, kept, flags, f => { asks++; return vanilla(f); });
                                // kernel level, whatever the engine can produce: a "yes" from vanilla is never re-asked
                                int asks3 = 0;
                                bool r3 = RSW_HoodKernel.Postfix(true, false, applies, kept, flags, f => { asks3++; return false; });
                                Check(r3 && asks3 == 0, "the postfix re-asked after vanilla said yes");
                                // an unrelated apparel node (kept = false) never changes
                                bool other = RSW_HoodKernel.Postfix(vanillaResult, reentry, applies, false, flags, f => { asks++; return vanilla(f); });
                                Check(other == vanillaResult, "a non-kept apparel changed");
                                Check(asks <= 1, $"the worker was asked {asks} times");
                                if (vanillaResult || reentry || !applies || !kept) { Check(final == vanillaResult && asks == 0, "the postfix acted when it should have stayed out"); }
                                else
                                {
                                    Check(asks == 1, "the kept hood was not re-asked");
                                    Check(final == vanilla(flags | 0x60), "the re-ask did not use the restored flags");
                                    if (count) SwimAsked++;
                                    if (final && count) SwimKept++;
                                }
                                // the feature: a worn kept hood stays up while swimming whenever every other gate lets it
                                if (swimSetting && swimming && !portrait && kept && !reentry && otherGates && !bedHides && !(hatsOnlyOnMap && !onMap))
                                    Check(final, "a swimming Jawa lost its hood although nothing else forbids it");
                                if (!applies && !reentry) Check(final == vanillaResult, "the rule acted outside swimming / with the setting off / on a portrait");
                                // the fallback hood
                                bool realDrawing = RSW_HoodKernel.RealHoodIsDrawing(hoodResolved, visible, flags, applies, tracker, () => wearsHood);
                                bool want = hoodResolved && visible(RSW_HoodKernel.EffectiveFlags(flags, applies)) && tracker && wearsHood;
                                Check(realDrawing == want, $"RealHoodIsDrawing {realDrawing} vs {want}");
                                bool fb = RSW_HoodKernel.FallbackDraws(fallbackBase, () => realDrawing);
                                Check(fb == (fallbackBase && !realDrawing), "FallbackDraws");
                                if (count && fb) Fallbacks++;
                                // never both, and never neither when the real hood's other gates pass
                                if (kept && !reentry && wearsHood && hoodResolved && tracker && fallbackBase)
                                {
                                    bool realFinal = final;
                                    if (otherGates) Check(realFinal != fb, $"hood/fallback: real {realFinal}, fallback {fb} (both or neither)");
                                    else if (realDrawing && !fb) { if (count) Gaps++; }   // the real hood's own gate refuses what the fallback cannot see
                                }
                                if (count && final && kept) RealDraws++;
                                // fail open
                                bool open = RSW_HoodKernel.FallbackDraws(fallbackBase, () => throw new InvalidOperationException("boom"));
                                Check(open == fallbackBase, "the fallback did not fail open");
                                if (count && fallbackBase) FailOpen++;
                                if (!wearsHood || !hoodResolved || !tracker) Check(fb == fallbackBase, "the fallback hid with no real hood to stand in for");
                                break;
                            }
                    }
                }
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        // ════════════════════════ rules ════════════════════════
        // kinds: 0 new pet, 1 tame / rename, 2 sow query, 3 redress, 4 settings, 5 pawn without tracker, 6 world labels
        private sealed class Pet { public bool animal, player, hasName, numerical; public string name; }

        private static string RunRules(IList<Act> acts, int seed, bool count)
        {
            bool en = true; var pets = new List<Pet>(); var used = new HashSet<string>(); int stepNo = 0, nameSeq = 0;
            try
            {
                foreach (Act a in acts)
                {
                    stepNo++; if (count) Steps++;
                    switch (a.kind)
                    {
                        case 4: en = (a.a & 7) != 0; break;
                        case 0: pets.Add(new Pet { animal = (a.a & 3) != 0, player = (a.b & 1) != 0, hasName = (a.b & 6) != 0, numerical = (a.b & 24) == 0 }); if (pets.Count > 8) pets.RemoveAt(0); break;
                        case 1:
                            {
                                if (pets.Count == 0) break;
                                var p = pets[a.a % pets.Count];
                                if ((a.b & 1) != 0) p.player = true;
                                else if ((a.b & 2) != 0) { p.hasName = true; p.numerical = false; p.name = "playerchosen" + (nameSeq++); used.Add(p.name); }
                                bool needs = RSW_RulesKernel.NeedsPetName(en, true, p.animal, true, p.player, p.hasName, p.numerical);
                                string before = p.name;
                                Check(needs == (en && p.animal && p.player && (!p.hasName || p.numerical)), "NeedsPetName");
                                if (needs)
                                {
                                    p.name = "pet" + (nameSeq++); p.hasName = true; p.numerical = false; used.Add(p.name); if (count) Named++;
                                    Check(!RSW_RulesKernel.NeedsPetName(en, true, p.animal, true, p.player, p.hasName, p.numerical), "a named pet still needs a name (renames forever)");
                                }
                                else if (p.hasName && !p.numerical && before != null) Check(p.name == before, "a chosen name was replaced");
                                if (!p.animal || !p.player) Check(!needs, "a wild animal or a non-animal was named");
                                Check(!RSW_RulesKernel.NeedsPetName(en, true, p.animal, false, true, p.hasName, p.numerical), "an animal with no faction at all was named");
                                break;
                            }
                        case 2:
                            {
                                bool vanilla = (a.a & 1) != 0, jawa = (a.a & 2) != 0; int asked = 0;
                                bool res = RSW_RulesKernel.SowResult(en, vanilla, () => { asked++; return jawa; });
                                Check(res == (en && vanilla && jawa ? false : vanilla), "SowResult");
                                Check(asked == (en && vanilla ? 1 : 0), "the xenotype was read when it should not be (or not when it should)");
                                if (res != vanilla) { Check(en && vanilla && jawa, "a non-Jawa lost the right to sow"); if (count) Sown++; }
                                Check(!(vanilla == false && res), "the rule granted sowing");
                                break;
                            }
                        case 3:
                            {
                                bool kindDiffers = (a.a & 1) != 0, hasReq = (a.a & 6) != 0, hasPawn = (a.a & 24) != 0, biotech = (a.b & 1) != 0, genes = (a.b & 6) != 0, factionX = (a.b & 24) != 0, wanted = (a.c & 3) != 0, xDiffers = (a.c & 12) != 0;
                                bool fk = RSW_RulesKernel.ForceKind(en, hasPawn, hasReq, kindDiffers);
                                Check(fk == (en && hasPawn && hasReq && kindDiffers), "ForceKind");
                                if (fk) { if (count) Redressed++; Check(!RSW_RulesKernel.ForceKind(en, hasPawn, hasReq, false), "a corrected pawn is corrected again"); }
                                bool fx = RSW_RulesKernel.ForceXenotype(biotech, genes, factionX, wanted, xDiffers);
                                Check(fx == (biotech && genes && factionX && wanted && xDiffers), "ForceXenotype");
                                break;
                            }
                        case 5:
                            Check(RSW_RulesKernel.NeedsRelationsTracker(en, (a.a & 1) != 0, (a.a & 2) != 0, (a.a & 4) != 0) == (en && (a.a & 1) != 0 && (a.a & 2) != 0 && (a.a & 4) == 0), "NeedsRelationsTracker");
                            break;
                        case 6:
                            {
                                float vanilla = 0.3f, wanted = 0.6f;
                                Check(RSW_RulesKernel.Current(en, wanted, vanilla) == (en ? wanted : vanilla), "Current world-label value");
                                break;
                            }
                    }
                    var names = pets.Where(p => p.hasName && !p.numerical && p.name != null).Select(p => p.name).ToList();
                    Check(names.Distinct().Count() == names.Count, "two pets share a name");
                }
                // IsJawa: exact by name
                Check(RSW_RulesKernel.IsJawa(true, true, "RSW_MandrakeJawa", "RSW_MandrakeJawa") && !RSW_RulesKernel.IsJawa(true, true, "RSW_RimMandrakeJawa", "RSW_MandrakeJawa") && !RSW_RulesKernel.IsJawa(false, true, "RSW_MandrakeJawa", "RSW_MandrakeJawa") && !RSW_RulesKernel.IsJawa(true, false, null, "RSW_MandrakeJawa") && !RSW_RulesKernel.IsJawa(true, true, "rsw_mandrakejawa", "RSW_MandrakeJawa"), "IsJawa is an exact, case-sensitive xenotype name match");
            }
            catch (Exception e) { return $"step {stepNo}: {e.Message}"; }
            return null;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("hood", () => Family("hood", N(5000), S(1), new[] { 80, 6, 8, 6 }, 20, 120, RunHood)),
                ("rules", () => Family("rules", N(5000), S(1), new[] { 12, 25, 25, 20, 6, 6, 6 }, 20, 120, RunRules)),
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
            Console.WriteLine($"reached: swim re-asks {SwimAsked} (hood kept {SwimKept}), real-hood draws {RealDraws}, fallback draws {Fallbacks}, fail-open checks {FailOpen}, measured gaps {Gaps}, pets named {Named}, pawns re-kinded {Redressed}, Jawa sowing refused {Sown}");
            if (!oneSeed.HasValue && scale >= 1)
            {
                bool all = only == null;
                if ((all || only == "hood") && (SwimAsked == 0 || SwimKept == 0 || Fallbacks == 0 || RealDraws == 0)) { Console.WriteLine("FAIL hood fuzz never re-asked / kept a hood / drew a fallback (blind)"); ok = false; }
                if ((all || only == "rules") && (Named == 0 || Redressed == 0 || Sown == 0)) { Console.WriteLine("FAIL rules fuzz never named a pet / re-kinded a pawn / refused a sow (blind)"); ok = false; }
            }
            Console.WriteLine($"jawarules fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
