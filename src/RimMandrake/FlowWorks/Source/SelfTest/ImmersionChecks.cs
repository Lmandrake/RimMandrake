// IMMERSION_DAMAGE_WIRE_NEVER_APPLIED: the production RM_LiquidImmersionMath rule on the SHIPPED Defs. A pawn in chest-deep or
// deeper liquid takes the liquid's damageOnImmersion; shallower takes damageOnContact; an immersion-only liquid does nothing in
// the shallows. Before the fix LiquidCorrosion applied damageOnContact everywhere and damageOnImmersion had no consumer.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ImmersionChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string ModRoot()
        {
            string d = AppContext.BaseDirectory;
            for (int i = 0; i < 10 && d != null; i++, d = Path.GetDirectoryName(d))
            {
                if (Directory.Exists(Path.Combine(d, "Defs", "LiquidTypes")) && Directory.Exists(Path.Combine(d, "Source", "LiquidTypes")))
                    return d;
            }
            throw new Exception("FlowWorks mod root not found above " + AppContext.BaseDirectory);
        }

        private static List<XElement> Rows(string tag)
        {
            return Directory.GetFiles(Path.Combine(ModRoot(), "Defs"), "*.xml", SearchOption.AllDirectories)
                .SelectMany(f => XDocument.Load(f).Descendants(tag)).ToList();
        }

        // Passability of the vanilla parents our liquid terrains name (Core Terrain_Water.xml, read 2026-11-02): only
        // WaterDeepBase sets Impassable; WaterShallowBase, WaterShallow and MarshBase inherit WaterBase's Standable.
        private static readonly Dictionary<string, bool> VanillaImpassable = new Dictionary<string, bool>
        {
            { "WaterDeepBase", true }, { "WaterShallowBase", false }, { "WaterShallow", false }, { "MarshBase", false },
        };

        private sealed class Liquid
        {
            public string defName, parent;
            public bool impassable, suiteDeep;
            public List<string> tags;
            public float contact, immersion;   // 0 = no live spec
            public RM_LiquidImmersionMath.Exposure exposure;
            public float Amount => exposure == RM_LiquidImmersionMath.Exposure.Immersion ? immersion
                : exposure == RM_LiquidImmersionMath.Exposure.Contact ? contact : 0f;
        }

        private static float SpecAmount(XElement props, string name)
        {
            XElement s = props.Element(name);
            if (s == null || string.IsNullOrEmpty((string)s.Element("damageDef"))) return 0f;
            string a = (string)s.Element("amount");
            return a == null ? 0f : float.Parse(a, CultureInfo.InvariantCulture);
        }

        private static Dictionary<string, Liquid> Shipped()
        {
            var deep = new HashSet<string>();
            foreach (XElement l in Rows("RimMandrake.FlowWorks.LiquidTypes.LiquidDef"))
            {
                XElement s = l.Element("terrainSuite");
                foreach (string m in new[] { (string)s?.Element("deep"), (string)s?.Element("chestDeep") })
                    if (m != null) deep.Add(m);
            }
            var outp = new Dictionary<string, Liquid>();
            foreach (XElement t in Rows("TerrainDef"))
            {
                XElement props = t.Element("modExtensions")?.Elements("li")
                    .FirstOrDefault(li => ((string)li.Attribute("Class") ?? "").EndsWith(".RM_LiquidProperties"));
                if (props == null) continue;
                var q = new Liquid
                {
                    defName = (string)t.Element("defName"),
                    parent = (string)t.Attribute("ParentName"),
                    tags = t.Element("tags")?.Elements("li").Select(e => e.Value).ToList() ?? new List<string>(),
                    contact = SpecAmount(props, "damageOnContact"),
                    immersion = SpecAmount(props, "damageOnImmersion"),
                };
                string own = (string)t.Element("passability");
                if (own != null) q.impassable = own == "Impassable";
                else
                {
                    Assert(q.parent != null && VanillaImpassable.ContainsKey(q.parent), q.defName + ": parent " + q.parent + " has no known passability; add it to VanillaImpassable from the Core def");
                    q.impassable = VanillaImpassable[q.parent];
                }
                q.suiteDeep = deep.Contains(q.defName);
                q.exposure = RM_LiquidImmersionMath.Select(RM_LiquidImmersionMath.IsImmersing(q.impassable, q.suiteDeep, q.tags), q.contact > 0f, q.immersion > 0f);
                outp[q.defName] = q;
            }
            Assert(outp.Count >= 20, "only " + outp.Count + " liquid terrains found: the def reader went blind");
            return outp;
        }


        // A tiny interpreter for the five statements in LiquidCorrosion.DoCorrosionPass that decide the damage, plus the
        // SuiteDeep set builder. Whitespace-normalised; every expression must be one it knows, else the case fails.
        private sealed class Wiring
        {
            private string contactField, immersionField, immFieldPick, conFieldPick;
            private Func<Liquid, bool>[] isImmArgs;
            private Func<Liquid, bool> immersingFn, contactLiveFn, immersionLiveFn;
            private string[] selectArgs;
            private bool suiteHasDeep, suiteHasChest, damageFromSpec;

            private static string Norm(string s) => System.Text.RegularExpressions.Regex.Replace(s, @"\s+", " ");

            private static System.Text.RegularExpressions.Match One(string src, string pattern, string what)
            {
                var ms = System.Text.RegularExpressions.Regex.Matches(src, pattern);
                Assert(ms.Count == 1, "LiquidCorrosion: expected exactly one " + what + ", found " + ms.Count);
                return ms[0];
            }

            private static float Spec(Liquid q, string field)
            {
                if (field == "damageOnContact") return q.contact;
                if (field == "damageOnImmersion") return q.immersion;
                throw new Exception("LiquidCorrosion reads unknown spec field props." + field);
            }

            private Func<Liquid, bool> ImmArg(string a)
            {
                a = a.Trim();
                if (a == "terrain.passability == Traversability.Impassable") return q => q.impassable;
                if (a == "SuiteDeep(terrain)") return q => q.suiteDeep && ((suiteHasDeep && suiteHasChest) || throwSuite());
                if (a == "terrain.tags") return null;   // the tag list: handled as the third argument
                if (a == "true") return q => true;
                if (a == "false") return q => false;
                throw new Exception("LiquidCorrosion IsImmersing argument not understood: '" + a + "'");
            }

            private bool throwSuite() { throw new Exception("SuiteDeep no longer collects both terrainSuite.deep and terrainSuite.chestDeep"); }

            private Func<Liquid, bool> Flag(string a)
            {
                a = a.Trim();
                if (a == "immersing") return q => immersingFn(q);
                if (a == "contactLive") return q => contactLiveFn(q);
                if (a == "immersionLive") return q => immersionLiveFn(q);
                if (a == "true") return q => true;
                if (a == "false") return q => false;
                throw new Exception("LiquidCorrosion Select argument not understood: '" + a + "'");
            }

            public static Wiring Read(string raw)
            {
                string src = Norm(raw);
                var w = new Wiring();
                const string F = @"(damageOn\w+)";
                var c = One(src, @"bool contactLive = props\." + F + @"\?\.damageDef != null && props\." + F + @"\.amount > 0f;", "contactLive");
                Assert(c.Groups[1].Value == c.Groups[2].Value, "contactLive mixes two spec fields");
                w.contactField = c.Groups[1].Value;
                var i = One(src, @"bool immersionLive = props\." + F + @"\?\.damageDef != null && props\." + F + @"\.amount > 0f;", "immersionLive");
                Assert(i.Groups[1].Value == i.Groups[2].Value, "immersionLive mixes two spec fields");
                w.immersionField = i.Groups[1].Value;
                w.contactLiveFn = q => Spec(q, w.contactField) > 0f;
                w.immersionLiveFn = q => Spec(q, w.immersionField) > 0f;

                var m = One(src, @"bool immersing = RM_LiquidImmersionMath\.IsImmersing\(([^;]*)\);", "immersing = IsImmersing(...)");
                string[] ia = m.Groups[1].Value.Split(',');
                Assert(ia.Length == 3 && ia[2].Trim() == "terrain.tags", "IsImmersing args changed: " + m.Groups[1].Value);
                Func<Liquid, bool> a0 = w.ImmArg(ia[0]), a1 = w.ImmArg(ia[1]);
                w.immersingFn = q => RM_LiquidImmersionMath.IsImmersing(a0(q), a1(q), q.tags);

                var s = One(src, @"RM_LiquidImmersionMath\.Exposure exposure = RM_LiquidImmersionMath\.Select\(([^;]*)\);", "exposure = Select(...)");
                w.selectArgs = s.Groups[1].Value.Split(',');
                Assert(w.selectArgs.Length == 3, "Select args changed: " + s.Groups[1].Value);
                foreach (string a in w.selectArgs) w.Flag(a);   // fail early on an unknown argument

                var p = One(src, @"LiquidDamageSpec spec = exposure == RM_LiquidImmersionMath\.Exposure\.(\w+) \? props\." + F
                    + @" : exposure == RM_LiquidImmersionMath\.Exposure\.(\w+) \? props\." + F + @" : null;", "spec pick");
                Assert(p.Groups[1].Value == "Immersion" && p.Groups[3].Value == "Contact", "spec pick tests " + p.Groups[1].Value + "/" + p.Groups[3].Value);
                w.immFieldPick = p.Groups[2].Value;
                w.conFieldPick = p.Groups[4].Value;

                w.damageFromSpec = One(src, @"if \(spec != null\) \{ DamageInfo dinfo = new DamageInfo\(spec\.damageDef, spec\.amount, 0f, -1f, null\); pawn\.TakeDamage\(dinfo\); \}", "spec -> TakeDamage").Success;
                One(src, @"TerrainDef terrain = pawn\.Position\.GetTerrain\(map\); RM_LiquidProperties props = terrain\?\.GetModExtension<RM_LiquidProperties>\(\);", "terrain/props read at the pawn");
                w.suiteHasDeep = System.Text.RegularExpressions.Regex.IsMatch(src, @"if \(l\.terrainSuite\?\.deep != null\) set\.Add\(l\.terrainSuite\.deep\);");
                w.suiteHasChest = System.Text.RegularExpressions.Regex.IsMatch(src, @"if \(l\.terrainSuite\?\.chestDeep != null\) set\.Add\(l\.terrainSuite\.chestDeep\);");
                One(src, @"return suiteDeep\.Contains\(terrain\);", "SuiteDeep membership");

                // Order inside the pass: flags, immersing, exposure, spec, damage.
                int[] at = { src.IndexOf("bool contactLive"), src.IndexOf("bool immersing"), src.IndexOf("exposure = RM_LiquidImmersionMath.Select"),
                    src.IndexOf("LiquidDamageSpec spec ="), src.IndexOf("pawn.TakeDamage(dinfo)") };
                int pass = src.IndexOf("private void DoCorrosionPass()");
                Assert(pass >= 0 && at[0] > pass && at.Zip(at.Skip(1), (x, y) => x < y).All(b => b), "DoCorrosionPass statements out of order");
                return w;
            }

            public float Damage(Liquid q)
            {
                Func<Liquid, bool> s0 = Flag(selectArgs[0]), s1 = Flag(selectArgs[1]), s2 = Flag(selectArgs[2]);
                var e = RM_LiquidImmersionMath.Select(s0(q), s1(q), s2(q));
                if (!damageFromSpec) return 0f;
                return e == RM_LiquidImmersionMath.Exposure.Immersion ? Spec(q, immFieldPick)
                    : e == RM_LiquidImmersionMath.Exposure.Contact ? Spec(q, conFieldPick) : 0f;
            }
        }

        private static void Expect(Dictionary<string, Liquid> all, string defName, RM_LiquidImmersionMath.Exposure e, float amount)
        {
            Assert(all.TryGetValue(defName, out Liquid q), defName + " not among the shipped liquid terrains");
            Assert(q.exposure == e && Math.Abs(q.Amount - amount) < 1e-4f, defName + ": " + q.exposure + " " + q.Amount + ", expected " + e + " " + amount);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("ImmersionDamage_select_truth_table", () =>
            {
                foreach (bool imm in new[] { false, true })
                    foreach (bool c in new[] { false, true })
                        foreach (bool i in new[] { false, true })
                        {
                            var want = imm && i ? RM_LiquidImmersionMath.Exposure.Immersion
                                : c ? RM_LiquidImmersionMath.Exposure.Contact : RM_LiquidImmersionMath.Exposure.None;
                            Assert(RM_LiquidImmersionMath.Select(imm, c, i) == want, "Select(" + imm + "," + c + "," + i + ")");
                        }
                Assert(!RM_LiquidImmersionMath.IsImmersing(false, false, null), "nothing deep reads immersing");
                Assert(!RM_LiquidImmersionMath.IsImmersing(false, false, new[] { "Water", "WaterFreshShallow" }), "shallow tag reads immersing");
                Assert(RM_LiquidImmersionMath.IsImmersing(true, false, null), "impassable is not immersing");
                Assert(RM_LiquidImmersionMath.IsImmersing(false, true, null), "suite deep is not immersing");
                Assert(RM_LiquidImmersionMath.IsImmersing(false, false, new[] { "Water", "WaterFreshDeep" }), "WaterFreshDeep is not immersing");
            });

            Case("ImmersionDamage_shipped_acid_pool_and_slime", () =>
            {
                var all = Shipped();
                Expect(all, "RM_AcidDeep", RM_LiquidImmersionMath.Exposure.Immersion, 3f);         // the GPT finding's scenario
                Expect(all, "RM_AcidShallow", RM_LiquidImmersionMath.Exposure.Contact, 1f);
                Expect(all, "RM_ReactionLiquorDeep", RM_LiquidImmersionMath.Exposure.Immersion, 5f);
                Expect(all, "RM_SlimeGreenShallow", RM_LiquidImmersionMath.Exposure.None, 0f);     // immersion-only liquid
                Expect(all, "RM_SlimeGreenDeep", RM_LiquidImmersionMath.Exposure.Immersion, 2f);   // Standable deep, by suite
                Expect(all, "RM_SlimeRedDeep", RM_LiquidImmersionMath.Exposure.Immersion, 2f);
                Expect(all, "RM_WaterFrigidShallow", RM_LiquidImmersionMath.Exposure.Contact, 1f); // slush cost 60, still shallow
            });

            Case("ImmersionDamage_shipped_canal_ladders", () =>
            {
                var all = Shipped();
                foreach (var (ladder, c, i) in new[] { ("AcidWater", 1f, 3f), ("ReactionLiquor", 2f, 5f) })
                {
                    Expect(all, "RM_Fill_" + ladder + "_Trace", RM_LiquidImmersionMath.Exposure.Contact, c);
                    Expect(all, "RM_Fill_" + ladder + "_Half", RM_LiquidImmersionMath.Exposure.Contact, c);
                    Expect(all, "RM_Fill_" + ladder + "_Brim", RM_LiquidImmersionMath.Exposure.Immersion, i);
                    Expect(all, "RM_Fill_" + ladder + "_Superdeep", RM_LiquidImmersionMath.Exposure.Immersion, i);
                }
            });

            Case("ImmersionDamage_shipped_every_liquid_by_parent", () =>
            {
                int deepSeen = 0, shallowSeen = 0;
                foreach (Liquid q in Shipped().Values)
                {
                    bool deepParent = q.parent == "WaterDeepBase";
                    bool deepTag = q.tags.Contains(RM_LiquidImmersionMath.DeepTag);
                    if (deepParent && q.immersion > 0f)
                    {
                        deepSeen++;
                        Assert(q.exposure == RM_LiquidImmersionMath.Exposure.Immersion, q.defName + " is deep, authors immersion, takes " + q.exposure);
                    }
                    if (!deepParent && !deepTag)
                    {
                        shallowSeen++;
                        Assert(q.exposure != RM_LiquidImmersionMath.Exposure.Immersion, q.defName + " is shallow and takes immersion damage");
                    }
                }
                Assert(deepSeen >= 6 && shallowSeen >= 10, "sweep saw " + deepSeen + " deep and " + shallowSeen + " shallow: reader blind");
            });

            Case("ImmersionDamage_corrosion_pass_consumes_immersion", () =>
            {
                string src = File.ReadAllText(Path.Combine(ModRoot(), "Source", "LiquidTypes", "LiquidCorrosion.cs"));
                Assert(src.Contains("props.damageOnImmersion") && src.Contains("RM_LiquidImmersionMath.Select("), "LiquidCorrosion no longer selects damageOnImmersion by depth");
            });

            // The in-game consumer, EXECUTED on the shipped defs: DoCorrosionPass's own wiring statements are read out of
            // LiquidCorrosion.cs and interpreted (each argument and field name is resolved, unknown text fails), then run on
            // every shipped liquid terrain. A mutant that hands Immersion the contact spec, drops SuiteDeep, swaps a Select
            // argument, or feeds a live-flag from the wrong field changes what RM_AcidDeep / RM_SlimeGreenDeep take, and goes red.
            Case("ImmersionDamage_corrosion_pass_wiring_runs_on_shipped_defs", () =>
            {
                var w = Wiring.Read(File.ReadAllText(Path.Combine(ModRoot(), "Source", "LiquidTypes", "LiquidCorrosion.cs")));
                var all = Shipped();
                foreach (var (name, amount) in new[] { ("RM_AcidDeep", 3f), ("RM_AcidShallow", 1f), ("RM_SlimeGreenDeep", 2f),
                    ("RM_SlimeGreenShallow", 0f), ("RM_ReactionLiquorDeep", 5f), ("RM_Fill_AcidWater_Brim", 3f), ("RM_Fill_AcidWater_Half", 1f) })
                {
                    Assert(all.TryGetValue(name, out Liquid q), name + " not shipped");
                    float got = w.Damage(q);
                    Assert(Math.Abs(got - amount) < 1e-4f, "LiquidCorrosion wiring gives " + name + " " + got + " damage per pass, expected " + amount);
                }
                foreach (Liquid q in all.Values)
                    Assert(Math.Abs(w.Damage(q) - q.Amount) < 1e-4f, q.defName + ": LiquidCorrosion wiring gives " + w.Damage(q) + ", the immersion rule gives " + q.Amount);
            });
        }
    }
}
