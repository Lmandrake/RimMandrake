// POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P1-P4):
// offline checks that the shipped RM_PowerCord def (the XML the game loads) is caught by the production crossing table
// (RM_LineCrossingMath) and dig-break selector (RM_LineDigBreakMath), both compiled in, and that the leaf cut reaches the
// power net (RM_PowerCordMath compiled in; Building_RM_PowerCord.cs and RM_Drawbridges.cs read as text). L1 of the item's
// verify. Each case has a can-fail. NOT proven here: a lamp on the far bank going dark in a running game (L2, live rows owed).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PowerCordChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string Body(string src, string signature)
        {
            int a = src.IndexOf(signature, StringComparison.Ordinal);
            Assert(a >= 0, "missing: " + signature);
            int open = src.IndexOf('{', a);
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(a, i - a + 1);
            }
            throw new Exception("unbalanced: " + signature);
        }

        private static string ModRoot() => Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")));

        private static XElement CordDef()
        {
            XDocument d = XDocument.Load(Path.Combine(ModRoot(), "Defs", "Machinery", "RM_PowerCord.xml"));
            return d.Root.Elements("ThingDef").Single(e => (string)e.Element("defName") == "RM_PowerCord");
        }

        /// <summary>The kind the game reads off a def's RM_LineKindExtension (the first one, as GetModExtension does).</summary>
        private static LineKind TagOf(XElement def)
        {
            var ext = def.Element("modExtensions").Elements("li").Where(e => (string)e.Attribute("Class") == "RimMandrake.FlowWorks.Machinery.RM_LineKindExtension").ToList();
            Assert(ext.Count == 1, "exactly one line tag");
            return (LineKind)Enum.Parse(typeof(LineKind), ext[0].Element("kind").Value);
        }

        private static LineKind ConduitTag()
        {
            XDocument patch = XDocument.Load(Path.Combine(ModRoot(), "Patches", "Machinery", "RM_LineKinds.xml"));
            var op = patch.Root.Elements("Operation").Single(e => (string)e.Attribute("Class") == "PatchOperationAddModExtension");
            Assert((string)op.Element("xpath") == "Defs/ThingDef[defName=\"PowerConduit\"]", "the conduit tag sits on PowerConduit");
            return (LineKind)Enum.Parse(typeof(LineKind), op.Descendants("kind").Single().Value);
        }

        private class Cell
        {
            public int X;
            public bool Comp = true;      // CompProperties_Power.transmitsPower
            public bool IsCord;
            public bool LeafRaised;
            public bool Transmits => IsCord ? RM_PowerCordMath.TransmitsNow(Comp, LeafRaised) : Comp;
        }

        /// <summary>The engine's net rule, re-typed: PowerNetMaker.ContiguousPowerBuildings floods cardinal neighbours whose
        /// TransmitsPowerNow is not false. One row of cells; returns the net id of each transmitting cell (-1 = no net).</summary>
        private static int[] Nets(List<Cell> row)
        {
            var id = new int[row.Count];
            int next = 0;
            for (int i = 0; i < row.Count; i++)
            {
                id[i] = row[i].Transmits ? (i > 0 && row[i - 1].Transmits ? id[i - 1] : next++) : -1;
            }
            return id;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PowerCord_def_is_a_FlexCord_power_transmitter_of_its_own", () =>
            {
                XElement d = CordDef();
                Assert(TagOf(d) == LineKind.FlexCord, "can-fail: the cord is tagged FlexCord");
                Assert((string)d.Attribute("ParentName") == "BuildingBase", "never a child of PowerConduit (it would inherit the RigidConduit tag first)");
                Assert(d.Element("thingClass").Value == "RimMandrake.FlowWorks.Machinery.Building_RM_PowerCord", "the leaf-aware building class");
                var power = d.Element("comps").Elements("li").Single(e => (string)e.Attribute("Class") == "CompProperties_Power");
                Assert(power.Element("compClass").Value == "CompPowerTransmitter" && power.Element("transmitsPower").Value == "true", "carries power like a conduit");
                Assert(d.Element("building").Element("isPowerConduit").Value == "true" && d.Element("graphicData").Element("linkType").Value == "Transmitter",
                    "a conduit to the engine and to Gimme Some Slack's cord drawer (ConduitVisuals picks isPowerConduit + Transmitter)");
                Assert(d.Element("graphicData").Element("texPath").Value.StartsWith("Things/Building/Linked/PowerConduit"), "the art stand-in is a vanilla texture that exists; no uninstalled path");
                Assert(d.Element("designationCategory").Value == "Power", "on the Power build tab");
                string cs = Src("Machinery", "Building_RM_PowerCord.cs");
                Assert(cs.Contains("public class Building_RM_PowerCord : Building"), "the class exists");
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                Assert(csproj.Contains("Machinery\\Building_RM_PowerCord.cs") && csproj.Contains("Machinery\\RM_PowerCordMath.cs"), "can-fail: both files are in the mod build");
            });

            Case("PowerCord_placeable_on_rope_timber_steel_decks_and_leaf_refused_dug_and_cover", () =>
            {
                LineKind cord = TagOf(CordDef());
                // timber and steel decks read Deck, rope RopeDeck, a lowered leaf DrawbridgeLeaf (RM_LineCrossing.DeckOn)
                string live = Src("Machinery", "RM_LineCrossing.cs");
                Assert(Body(live, "private static DeckOnSquare DeckOn(Map map, IntVec3 c)").Contains("s.Tier == SuspensionTier.Rope ? DeckOnSquare.RopeDeck : DeckOnSquare.Deck"),
                    "timber/steel/heavy decks are Deck, rope is RopeDeck");
                foreach (DeckOnSquare deck in new[] { DeckOnSquare.Deck, DeckOnSquare.RopeDeck, DeckOnSquare.DrawbridgeLeaf })
                {
                    foreach (bool dugUnder in new[] { false, true })
                    {
                        LineSurface s = RM_LineCrossingMath.Classify(dugUnder, deck);
                        Assert(RM_LineCrossingMath.MayBuild(cord, s), "can-fail: the cord lies on " + deck + (dugUnder ? " over a pit" : ""));
                    }
                }
                Assert(!RM_LineCrossingMath.MayBuild(cord, RM_LineCrossingMath.Classify(true, DeckOnSquare.None)), "can-fail: refused on a dug square");
                Assert(!RM_LineCrossingMath.MayBuild(cord, RM_LineCrossingMath.Classify(true, DeckOnSquare.Cover))
                    && !RM_LineCrossingMath.MayBuild(cord, RM_LineCrossingMath.Classify(false, DeckOnSquare.Cover)), "can-fail: refused on a pit cover");
                Assert(RM_LineCrossingMath.MayBuild(cord, RM_LineCrossingMath.Classify(false, DeckOnSquare.None)), "on solid ground");
                Assert(RM_LineCrossingMath.RefusalReason(cord, LineSurface.Excavated).StartsWith("A power cord"), "the refusal names the cord");
                // the rope exception: rope lends no Light, the terrain gate grants it to flexible kinds only
                Assert(CordDef().Element("terrainAffordanceNeeded").Value == "Light" && Body(live, "public static bool FlexOnDeck(").Contains("RM_LineCrossingMath.IsFlexible(kind.Value)"),
                    "rope admitted through FlexOnDeck, not a general Light affordance");
            });

            Case("PowerCord_restyled_conduit_still_refused_on_decks", () =>
            {
                LineKind conduit = ConduitTag();
                Assert(conduit == LineKind.RigidConduit, "conduit stays rigid");
                foreach (LineSurface s in new[] { LineSurface.Deck, LineSurface.RopeDeck, LineSurface.DrawbridgeLeaf, LineSurface.Cover, LineSurface.Excavated })
                {
                    Assert(!RM_LineCrossingMath.MayBuild(conduit, s), "can-fail: conduit refused on " + s);
                }
                string gssStyles = File.ReadAllText(Path.Combine(ModRoot(), "..", "GimmeSomeSlack", "Defs", "Aerial", "RM_ConduitStyles.xml"));
                Assert(gssStyles.Contains("ThingStyleDef") && !gssStyles.Contains("LineKind"), "a GSS look carries no line kind, so a restyle cannot make conduit a cord");
            });

            Case("PowerCord_dig_break_catches_the_cord_def", () =>
            {
                LineKind cord = TagOf(CordDef());
                var sq = new List<string> { "RM_PowerCord" };
                List<string> hit = RM_LineDigBreakMath.ToBreak(true, 0, 1, sq, t => cord, t => false);
                Assert(hit.Count == 1, "can-fail: a committed dig under the cord breaks it");
                Assert(RM_LineDigBreakMath.ToBreak(true, 1, 1, sq, t => cord, t => false).Count == 0, "no commit, no break");
                string brk = Src("Machinery", "RM_LineDigBreak.cs");
                Assert(Body(brk, "private static LineKind? KindOfBuilt(Thing t)").Contains("RM_LineCrossing.KindOf(t.def)"), "the dig reads the same def tag");
            });

            Case("PowerCord_leaf_raise_disconnects_lower_rejoins_the_power_net", () =>
            {
                // generator | conduit | cord on the leaf | conduit | lamp: the lamp's net is the generator's only while the leaf is down
                var row = new List<Cell> { new Cell { X = 0 }, new Cell { X = 1 }, new Cell { X = 2, IsCord = true }, new Cell { X = 3 }, new Cell { X = 4 } };
                int[] down = Nets(row);
                Assert(down[0] == down[4], "lowered: one net, the lamp is powered");
                row[2].LeafRaised = true;
                int[] up = Nets(row);
                Assert(up[2] == -1 && up[0] != up[4], "can-fail: raised, the cord transmits nothing and the net splits");
                row[2].LeafRaised = false;
                int[] again = Nets(row);
                Assert(again[0] == again[4], "lowered again: it rejoins");
                Assert(!RM_PowerCordMath.TransmitsNow(false, false), "a cord whose comp does not transmit stays dark");
                Assert(RM_PowerCordMath.CutLine(true) != null && RM_PowerCordMath.CutLine(false) == null, "the inspect line says why");
                // production wiring: the override reads the leaf, and a toggle re-registers every cord on the changed squares
                string cs = Src("Machinery", "Building_RM_PowerCord.cs");
                Assert(cs.Contains("public override bool TransmitsPowerNow => RM_PowerCordMath.TransmitsNow(base.TransmitsPowerNow, CutByLeaf);")
                    && cs.Contains("RM_Drawbridges.LineCutAt(Map, new[] { Position })"), "can-fail: the engine's net rule reads the leaf through the override");
                Assert(Body(cs, "public static int Notify_LeafToggled(Map map, List<IntVec3> changed)").Contains("map.powerNetManager.Notfiy_TransmitterTransmitsPowerNowChanged(cord.PowerComp)"),
                    "a toggle rebuilds the net at once (the power-switch path)");
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                Assert(Body(db, "public static void NotifyToggled(Map map, List<IntVec3> changed)").Contains("Building_RM_PowerCord.Notify_LeafToggled(map, changed)"),
                    "can-fail: every leaf toggle reaches the cords");
            });

            Case("PowerCord_deck_collapse_destroys_it_fallen_live_wire_not_yet", () =>
            {
                // P4: a collapsing deck destroys the cords on it (ClearDeckTop kills every building on the square). The fallen live
                // wire (RM_FallenWireShock) is PIPE_POLES phase 3 and is NOT built: this case pins today's behaviour only.
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                string clear = Body(comp, "public static void ClearDeckTop(Map map, IntVec3 c)");
                Assert(clear.Contains("if (t is Building || t.def.IsBlueprint || t.def.IsFrame)") && clear.Contains("DestroyMode.KillFinalize"), "can-fail: the cord is destroyed with the deck");
                Assert(Body(comp, "public void CollapseSpan(Building_SuspensionDeck from, string how)").Contains("ClearDeckTop(map, d.Position)"), "on every square of the span");
            });
        }
    }
}
