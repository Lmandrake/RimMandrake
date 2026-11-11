// FlowWorks code-review fixes, batch 01 (2026-10-11). Offline checks on the SHIPPED XML and the production source (not
// copies): natural tar burns and is not a fishing water, the dig and fill-in designations never share a cell, and a
// dig-find debug force / map budget is spent only as documented. Each has a can-fail.
// NOT proven here: a live fire on a tar pool, the fishing designator refusing it, a pawn's job choice.
using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ReviewFixBatch01Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Body(string src, string signature)
        {
            int at = src.IndexOf(signature, StringComparison.Ordinal);
            Assert(at >= 0, "can-fail: " + signature + " not found");
            int open = src.IndexOf('{', at);
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(open, i - open + 1);
            }
            throw new Exception("unbalanced body: " + signature);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("NaturalTar_burns_and_is_not_a_fishing_water", () =>
            {
                XDocument d = XDocument.Load(Path.Combine(ContainerMatFixture.Root(), "TerrainDefs", "RM_Tar.xml"));
                foreach (string dn in new[] { "RM_TarShallow", "RM_TarDeep" })
                {
                    XElement t = d.Descendants("TerrainDef").FirstOrDefault(e => (string)e.Element("defName") == dn);
                    Assert(t != null, dn + " shipped");
                    Assert((string)t.Element("extinguishesFire") == "false",
                        dn + ": extinguishesFire false (WaterBase's true puts out any fire on a tar source cell)");
                    Assert((string)t.Element("waterBodyType") == "None",
                        dn + ": waterBodyType None (the inherited Freshwater made tar a fishable freshwater body)");
                }
            });
            Case("DigCanal_and_FillInCanal_designations_never_share_a_cell", () =>
            {
                string dig = Body(RiverSwitchFlipChecks.Src("Designator_DigCanal.cs"), "public override void DesignateSingleCell");
                string fill = Body(RiverSwitchFlipChecks.Src("Designator_FillInCanal.cs"), "public override void DesignateSingleCell");
                Assert(dig.Contains("TryRemoveDesignation(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal)"), "digging clears a fill-in order");
                Assert(fill.Contains("TryRemoveDesignation(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal)"), "filling in clears a dig order");
                Assert(dig.IndexOf("TryRemoveDesignation", StringComparison.Ordinal) < dig.IndexOf("AddDesignation", StringComparison.Ordinal),
                    "the old order is cleared before the new one is added");
            });
            Case("DigFind_force_spent_on_every_cut_and_budget_debited_only_on_a_drop", () =>
            {
                string cut = Body(RiverSwitchFlipChecks.Src("RM_DigDiscovery.cs"), "public void OnCut(");
                int roll = cut.IndexOf("RM_DigDiscoveryMath.RollsAt(", StringComparison.Ordinal);
                int spentAfterEnsure = cut.IndexOf("ForceNextRoll = false;", cut.IndexOf("Ensure(map);", StringComparison.Ordinal), StringComparison.Ordinal);
                Assert(roll > 0 && spentAfterEnsure > 0 && spentAfterEnsure < roll,
                    "an armed force is spent before the already-rolled early return");
                int place = cut.IndexOf("GenPlace.TryPlaceThing(", StringComparison.Ordinal);
                int debit = cut.IndexOf("budgetLeft -= cost;", StringComparison.Ordinal);
                Assert(place > 0 && debit > place, "the map budget is debited only after the find was placed");
                Assert(cut.Split(new[] { "budgetLeft -= cost;" }, StringSplitOptions.None).Length == 2, "debited once");
            });
        }
    }
}
