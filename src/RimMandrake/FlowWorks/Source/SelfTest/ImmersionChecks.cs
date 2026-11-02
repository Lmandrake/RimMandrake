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
        }
    }
}
