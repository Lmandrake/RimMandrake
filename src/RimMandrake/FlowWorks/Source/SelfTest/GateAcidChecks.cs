// VEXXITH_USES_1, owner: "Acid-proof material for canal doors that can withstand acid shutoff/open flows." The production
// RM_CanalLiquidIndex and gate rule on the SHIPPED Defs: a gate standing in a canal fill burns, on every acid ladder, unless
// plasteel holds it off; water and the other canal fluids leave it alone. The vexxith half of the rule is in
// Cauldron/selftest_vexxith_uses.py, because the immunity lives in the Cauldron mod.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GateAcidChecks
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
                if (Directory.Exists(Path.Combine(d, "Defs", "Canals")) && Directory.Exists(Path.Combine(d, "Source", "MapControls")))
                    return d;
            }
            throw new Exception("FlowWorks mod root not found above " + AppContext.BaseDirectory);
        }

        private static List<XElement> Rows(string tag)
        {
            return Directory.GetFiles(Path.Combine(ModRoot(), "Defs"), "*.xml", SearchOption.AllDirectories)
                .SelectMany(f => XDocument.Load(f).Descendants(tag)).ToList();
        }

        private static readonly string[] FillFields = { "floodTerrain", "fillTerrainVeryShallow", "fillTerrainHalf", "fillTerrainBrim", "fillTerrainSuperdeep" };

        private static bool ShippedAcid(XElement l)
        {
            bool burns = l.Descendants("damageDef").Any(d => d.Value == "AcidBurn");
            bool corrodes = (string)l.Element("corrodesApparel") == "true";
            string ph = (string)l.Element("pH");
            float pH = ph == null ? 7f : float.Parse(ph, System.Globalization.CultureInfo.InvariantCulture);
            return RM_ContainerMaterialMath.IsAcid(pH, corrodes, burns);
        }

        private static RM_CanalLiquidIndex ShippedIndex()
        {
            var index = new RM_CanalLiquidIndex();
            foreach (XElement l in Rows("RimMandrake.FlowWorks.LiquidTypes.LiquidDef"))
            {
                XElement s = l.Element("terrainSuite");
                index.AddLiquid((string)l.Element("defName"), ShippedAcid(l), (string)l.Element("canalFluid"),
                    (string)s?.Element("shallow"), (string)s?.Element("deep"), (string)s?.Element("chestDeep"));
            }
            foreach (XElement f in Rows("RimMandrake.FlowWorks.FluidDef"))
            {
                index.AddFluid((string)f.Element("defName"), FillFields.Select(n => (string)f.Element(n)).ToArray());
            }
            return index;
        }

        private static bool Burns(RM_CanalLiquidIndex ix, string terrain, string fluid, RM_ContainerMaterial stuff)
        {
            return RM_ContainerMaterialMath.GateBurnsInAcid(stuff, true, ix.CellIsAcid(terrain, fluid));
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("GateAcid_canal_fill_burns_steel_not_plasteel", () =>
            {
                RM_CanalLiquidIndex ix = ShippedIndex();
                foreach (string ladder in new[] { "SlimeRed", "AcidWater", "ReactionLiquor" })
                {
                    foreach (string tier in new[] { "Trace", "Half", "Brim", "Superdeep" })
                    {
                        string t = "RM_Fill_" + ladder + "_" + tier;
                        Assert(Burns(ix, t, null, RM_ContainerMaterial.Metal), t + " does not burn a steel gate");
                        Assert(!Burns(ix, t, null, RM_ContainerMaterial.Plasteel), t + " burns a plasteel gate");
                    }
                }
                Assert(Burns(ix, "RM_AcidShallow", null, RM_ContainerMaterial.Metal), "a natural acid pool stopped burning");
                Assert(Burns(ix, "Soil", "RM_Fluid_AcidWater", RM_ContainerMaterial.Metal), "a recorded acid fluid on an unknown terrain did not burn");
            });
            Case("GateAcid_controls_leave_the_gate_alone", () =>
            {
                RM_CanalLiquidIndex ix = ShippedIndex();
                int seen = 0;
                foreach (XElement f in Rows("RimMandrake.FlowWorks.FluidDef"))
                {
                    string name = (string)f.Element("defName");
                    bool acidLadder = name == "RM_Fluid_SlimeRed" || name == "RM_Fluid_AcidWater" || name == "RM_Fluid_ReactionLiquor";
                    foreach (string t in FillFields.Select(n => (string)f.Element(n)).Where(t => t != null))
                    {
                        seen++;
                        Assert(Burns(ix, t, name, RM_ContainerMaterial.Metal) == acidLadder, name + " on " + t + ": gate burn should be " + acidLadder);
                    }
                }
                Assert(seen >= 40, "control saw only " + seen + " fill terrains: the parser is blind");
                Assert(!Burns(ix, "WaterShallow", "RM_Fluid_Water", RM_ContainerMaterial.Metal), "water burns a gate");
                Assert(!Burns(ix, "Soil", null, RM_ContainerMaterial.Metal), "dry ground burns a gate");
                Assert(ix.LiquidOfTerrain("RM_Fill_AcidWater_Half") == "RM_Liquid_AcidWater", "the acid ladder is not acid water's");
            });
            Case("GateAcid_every_acid_pool_feeds_a_canal_as_acid", () =>
            {
                // FormBody stamps RM_Fluid_Water on a liquid with no canalFluid: a canal off an acid pool would run fresh water.
                int acids = 0;
                foreach (XElement l in Rows("RimMandrake.FlowWorks.LiquidTypes.LiquidDef").Where(x => ShippedAcid(x) && x.Element("terrainSuite") != null))
                {
                    acids++;
                    Assert(l.Element("canalFluid") != null, (string)l.Element("defName") + " is an acid pool with no canal fluid");
                }
                Assert(acids >= 3, "only " + acids + " acid liquids seen: the parser is blind");
            });
            Case("GateAcid_canal_acid_burns_a_wader", () =>
            {
                XElement half = Rows("TerrainDef").First(t => (string)t.Element("defName") == "RM_Fill_AcidWater_Half");
                Assert(half.Descendants("damageDef").Any(d => d.Value == "AcidBurn"), "LiquidCorrosion reads RM_LiquidProperties on the terrain: canal acid would not burn a pawn");
                Assert((string)half.Element("dangerous") == "true", "canal acid is not marked dangerous");
            });
        }
    }
}
