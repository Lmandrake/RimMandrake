// RIGID_PIPE_BUILD_WIRE_STYLE_PICKER + FLOWWORKS_TABS_RECONCILE_PIPES_WITH_PIPES (owner rulings 2026-10-11 #1, #4, #6, #8,
// design/RimMandrake/gss_flowworks_rulings_2026-10-11.md). Offline halves of the rigid pipe's looks and the build-menu
// placement: the Verse-free PipeStyles rules, and the SHIPPED XML (not a copy) the game loads. Each property has a can-fail.
// NOT proven here: the build-button menu opening, a picked look surviving blueprint -> frame -> building -> save, the atlas
// joining up on a map. Those are live rows in validation.py (pipe_looks chain).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PipeStyleChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Defs => Path.GetDirectoryName(ContainerMatFixture.Root());
        private static string ModRoot => Path.GetDirectoryName(Defs);

        private static XDocument Load(params string[] rel) => XDocument.Load(Path.Combine(new[] { Defs }.Concat(rel).ToArray()));

        private static XElement Thing(XDocument d, string defName) =>
            d.Descendants("ThingDef").FirstOrDefault(e => (string)e.Element("defName") == defName);

        public static void Run(Action<string, Action> Case)
        {
            Case("PipeStyles_looks_are_the_wires_looks", () =>
            {
                Assert(PipeStyles.Looks.SequenceEqual(HoseStyles.Looks), "pipe looks == hose/wire looks, same menu order");
                Assert(PipeStyles.Looks.SequenceEqual(new[] { "Scrapper", "Industrial", "Modern", "Futuristic" }), "the four looks");
                Assert(PipeStyles.StyledDefs.SequenceEqual(new[] { "RM_UniversalPipe" }), "only the rigid pipe registers");
                Assert(PipeStyles.StyleDefName("RM_UniversalPipe", "Modern") == "RM_UniversalPipe_Modern", "style def naming");
            });
            Case("PipeStyles_resolve_rule", () =>
            {
                Assert(PipeStyles.Resolve("Modern", "Scrapper", false, null) == "Modern", "last pick wins");
                Assert(PipeStyles.Resolve(null, "Industrial", false, null) == "Industrial", "no pick: default");
                Assert(PipeStyles.Resolve("Modern", "Scrapper", true, "Futuristic") == "Futuristic", "copy builds the copied look");
                Assert(PipeStyles.Resolve("Modern", "Scrapper", true, null) == "Scrapper", "unstyled copy builds the default");
                Assert(PipeStyles.Resolve("Gold", "Scrapper", false, null) == "Scrapper", "can-fail: an unknown pick is not a look");
                Assert(PipeStyles.DefaultLook("Gold") == "Scrapper" && PipeStyles.DefaultLook("Modern") == "Modern", "default-look setting");
                Assert(PipeStyles.AtlasPath("Industrial") == "RimMandrake/FlowWorks/Pipe/Industrial/UniversalPipe_Atlas", "atlas path");
            });
            Case("TankStyles_four_looks_per_tank", () =>
            {
                // TANK_TALL_BUILD_TWICE_THE_DRINK (owner 2026-10-14): the four tanks take the GSS looks. The style defs ship in
                // Defs/LiquidTypes/ThingDefs/RM_LiquidTankStyles.xml once installed; until then the staged copy in art_source is read.
                Assert(PipeStyles.TankDefs.SequenceEqual(new[] { "RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank", "RM_UniversalCargoTankXTall" }), "the four tanks");
                Assert(!PipeStyles.StyledDefs.Contains("RM_LiquidTank"), "tanks register only through the guarded list, never unconditionally");
                Assert(PipeStyles.TankTexPath("RM_LiquidTankTall", "Modern") == "RimMandrake/FlowWorks/Tank/Modern/RM_LiquidTankTall", "tank tex path");
                Assert(PipeStyles.TankTexPath("RM_LiquidTank", "Gold") == "RimMandrake/FlowWorks/Tank/Scrapper/RM_LiquidTank", "can-fail: unknown look reads Scrapper");
                string shipped = Path.Combine(Defs, "LiquidTypes", "ThingDefs", "RM_LiquidTankStyles.xml");
                string staged = Path.Combine(ModRoot, "art_source", "TankTall", "v3", "RM_LiquidTankStyles.xml");
                XDocument st = XDocument.Load(File.Exists(shipped) ? shipped : staged);
                XDocument a = Load("LiquidTypes", "ThingDefs", "RM_LiquidTank.xml"), b = Load("Machinery", "RM_LiquidLogistics.xml");
                foreach (string tank in PipeStyles.TankDefs)
                {
                    XElement td = Thing(a, tank) ?? Thing(b, tank);
                    Assert(td != null, tank + " shipped");
                    Assert(td.Element("comps")?.Elements("li").Any(li => (string)li.Attribute("Class") == "CompProperties_Styleable") == true, tank + ": CompStyleable stores the look");
                    XElement tg = td.Element("graphicData");
                    foreach (string look in PipeStyles.Looks)
                    {
                        string dn = PipeStyles.StyleDefName(tank, look);
                        XElement s = st.Descendants("ThingStyleDef").FirstOrDefault(e => (string)e.Element("defName") == dn);
                        Assert(s != null, dn + " present");
                        XElement g = s.Element("graphicData");
                        Assert((string)g.Element("texPath") == PipeStyles.TankTexPath(tank, look), dn + ": owned art path");
                        Assert((string)g.Element("drawSize") == (string)tg.Element("drawSize") && (string)g.Element("drawOffset") == (string)tg.Element("drawOffset"),
                            dn + ": a style never moves the drawing (drawSize/drawOffset = the tank's)");
                    }
                }
            });
            Case("TankStyles_choose_style_gizmo", () =>
            {
                // TANK_LOOKS_WIRE_FOUR_STYLE_SWITCH (owner 2026-10-16: "I don't see the switch."): every tank carries the built
                // tank's Choose style gizmo, and the gizmo restyles through the shared picker (never a def swap).
                XDocument a = Load("LiquidTypes", "ThingDefs", "RM_LiquidTank.xml"), b = Load("Machinery", "RM_LiquidLogistics.xml");
                foreach (string tank in PipeStyles.TankDefs)
                {
                    XElement td = Thing(a, tank) ?? Thing(b, tank);
                    Assert(td != null, tank + " shipped");
                    Assert(td.Element("comps")?.Elements("li").Any(li => (string)li.Attribute("Class") == "RimMandrake.FlowWorks.Machinery.CompProperties_TankLook") == true,
                        tank + ": the Choose style gizmo (CompProperties_TankLook)");
                }
                // can-fail: a liquid-tank-class building outside TankDefs would be built with no look at all
                int tankClass = 0;
                foreach (XDocument d in new[] { a, b })
                    foreach (XElement td in d.Descendants("ThingDef").Where(e => ((string)e.Element("thingClass") ?? "").EndsWith(".Building_LiquidTank")))
                    {
                        tankClass++;
                        Assert(PipeStyles.TankDefs.Contains((string)td.Element("defName")), (string)td.Element("defName") + ": a liquid tank missing from PipeStyles.TankDefs");
                    }
                Assert(tankClass >= PipeStyles.TankDefs.Length, "sanity probe: the thingClass scan sees the shipped tanks (" + tankClass + ")");
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "PipeLook.cs"));
                Assert(src.Contains("class CompTankLook") && src.Contains("PipeLook.StyleFor(tank?.def, look)") && src.Contains("tank.SetStyleDef(sd)"),
                    "CompTankLook restyles in place through the shared picker");
                Assert(src.Contains("tank.OccupiedRect()"), "the whole footprint is redrawn (a 2x2 can straddle a mesh section)");
            });
            Case("PipeStyles_restyle_clears_cached_graphic", () =>
            {
                // can-fail: ThingStyleHelper.SetStyleDef never clears Thing.styleGraphicInt, so a restyle that does not call
                // Notify_ColorChanged stores the look and redraws the old one (owner 2026-10-16: the pipe's button "doesn't seem to do anything")
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "PipeLook.cs"));
                Assert(src.Contains("pipe.SetStyleDef(sd);") && src.Contains("pipe.Notify_ColorChanged();"), "the pipe's SetLook clears the cached style graphic");
                Assert(src.Contains("tank.SetStyleDef(sd);") && src.Contains("tank.Notify_ColorChanged();"), "the tank's SetLook clears the cached style graphic");
                string reel = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "CompHoseReel.cs"));
                Assert(reel.Contains("parent.SetStyleDef(sd);") && reel.Contains("parent.Notify_ColorChanged();"), "the reel's SetLook clears the cached style graphic");
            });
            Case("PipeStyles_shipped_style_defs", () =>
            {
                XDocument d = Load("Machinery", "RM_UniversalPipeStyles.xml");
                foreach (string look in PipeStyles.Looks)
                {
                    string dn = PipeStyles.StyleDefName(PipeStyles.PipeDef, look);
                    XElement s = d.Descendants("ThingStyleDef").FirstOrDefault(e => (string)e.Element("defName") == dn);
                    Assert(s != null, dn + " shipped");
                    XElement g = s.Element("graphicData");
                    Assert(g != null && (string)g.Element("linkType") == "Basic", dn + ": a Basic-linked atlas so a run joins up");
                    Assert(g.Element("linkFlags")?.Elements("li").Any(li => li.Value == "Custom3") == true, dn + ": the def's link flag");
                    Assert((string)g.Element("texPath") == PipeStyles.AtlasPath(look), dn + ": the look's owned atlas, got " + (string)g.Element("texPath"));
                    Assert((string)s.Element("uiIconPath") == PipeStyles.IconPath(look), dn + ": the look's owned menu icon");
                    Assert(g.Element("color") == null, dn + ": owned art is not tinted");
                    // the PNGs themselves: validation.py pipe_looks.owned_art_installed (this selftest runs from a staging dir with no Textures)
                }
                Assert(d.Descendants("StyleCategoryDef").Count() == 0, "no StyleCategoryDef (no ideoligion hands these out)");
            });
            Case("PipeStyles_pipe_is_styleable", () =>
            {
                XElement p = Thing(Load("Machinery", "RM_LiquidLogistics.xml"), "RM_UniversalPipe");
                Assert(p != null, "RM_UniversalPipe shipped");
                var comps = p.Element("comps")?.Elements("li").Select(li => (string)li.Attribute("Class")).ToList();
                Assert(comps != null && comps.Contains("CompProperties_Styleable"), "the engine's style field (CompProperties_Styleable)");
                Assert(comps.Contains("RimMandrake.FlowWorks.Machinery.CompProperties_PipeLook"), "the Choose style gizmo");
                Assert(p.Element("modExtensions")?.Elements("li").Any(li => (string)li.Attribute("Class") == "RimMandrake.FlowWorks.Machinery.RM_UniversalPipeExtension") == true,
                    "still the net's pipe (RM_UniversalPipeExtension)");
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "PipeLook.cs"));
                Assert(src.Contains("Core.Register(PipeStyles.StyledDefs, PipeStyles.StyleDefName)"), "PipeLook registers through the shared StylePickerCore");
                Assert(src.Contains("new StylePickerCore("), "the shared picker, not a copy");
            });
            Case("BuildMenu_pipes_and_tanks_in_the_pipe_networks_tab", () =>
            {
                XDocument tab = Load("Machinery", "RM_PipeNetworksTab.xml");
                Assert(tab.Descendants("DesignationCategoryDef").Any(e => (string)e.Element("defName") == "VCHE_PipeNetworks"), "the VE pipe tab is shipped");
                (string file, string def)[] want =
                {
                    (Path.Combine("Machinery", "RM_LiquidLogistics.xml"), "RM_UniversalPipe"),
                    (Path.Combine("Machinery", "RM_LiquidLogistics.xml"), "RM_UniversalCargoTank"),
                    (Path.Combine("LiquidTypes", "ThingDefs", "RM_LiquidTank.xml"), "RM_LiquidTank"),
                    (Path.Combine("Hose", "RM_HoseReel.xml"), "RM_HoseReel"),
                };
                foreach ((string file, string def) in want)
                {
                    XElement t = Thing(XDocument.Load(Path.Combine(Defs, file)), def);
                    Assert(t != null, def + " shipped");
                    Assert((string)t.Element("designationCategory") == "VCHE_PipeNetworks", def + " in the pipe networks tab, got " + (string)t.Element("designationCategory"));
                }
                XDocument ad = XDocument.Load(Path.Combine(ModRoot, "Patches", "Machinery", "RM_PipeNetAdapters.xml"));
                // every adapter the file ships (chemfuel; the propane one left with Alpha Biomes, eb6b1ec0c8) sits in the tab
                var adapters = ad.Descendants("defName").Where(e => e.Value.StartsWith("RM_PipeAdapter_")).Select(e => e.Parent).ToList();
                Assert(adapters.Any(a => (string)a.Element("defName") == "RM_PipeAdapter_Chemfuel"), "the chemfuel pipe adapter shipped");
                foreach (XElement a in adapters)
                    Assert((string)a.Element("designationCategory") == "VCHE_PipeNetworks",
                        (string)a.Element("defName") + " in the pipe networks tab, got " + (string)a.Element("designationCategory"));
                // can-fail: machines stay with production (pumps, stills are machines, not pipes or storage)
                XElement pump = Thing(Load("LiquidTypes", "ThingDefs", "RM_LiquidPump.xml"), "RM_LiquidPump");
                Assert((string)pump.Element("designationCategory") == "Production", "the pump is a machine: Production");
            });
            Case("PumpStyles_four_looks_scrapper_keeps_todays_pump", () =>
            {
                // owner card 2026-10-22: pumps E (Industrial), F (Modern), G (Futuristic) installed, each look picks its picture;
                // Scrapper keeps today's pump
                XElement pump = Thing(Load("LiquidTypes", "ThingDefs", "RM_LiquidPump.xml"), PipeStyles.PumpDef);
                Assert(pump != null, "the pump shipped");
                var comps = pump.Element("comps").Elements("li").Select(li => (string)li.Attribute("Class")).ToList();
                Assert(comps.Contains("CompProperties_Styleable") && comps.Contains("RimMandrake.FlowWorks.Machinery.CompProperties_TankLook"),
                    "the pump stores a look and has the Choose style gizmo");
                XElement pg = pump.Element("graphicData");
                Assert((string)pg.Element("texPath") == PipeStyles.PumpTexPath(PipeStyles.Scrapper), "the unstyled pump is the Scrapper picture (today's)");
                XDocument st = Load("LiquidTypes", "ThingDefs", "RM_LiquidPumpStyles.xml");
                var tex = new List<string>();
                foreach (string look in PipeStyles.Looks)
                {
                    string dn = PipeStyles.StyleDefName(PipeStyles.PumpDef, look);
                    XElement s = st.Descendants("ThingStyleDef").FirstOrDefault(e => (string)e.Element("defName") == dn);
                    Assert(s != null, dn + " present");
                    XElement g = s.Element("graphicData");
                    Assert((string)g.Element("texPath") == PipeStyles.PumpTexPath(look), dn + ": art path " + (string)g.Element("texPath"));
                    Assert((string)g.Element("drawSize") == (string)pg.Element("drawSize"), dn + ": a style never resizes the pump");
                    tex.Add((string)g.Element("texPath"));
                }
                Assert(tex.Distinct().Count() == 4, "can-fail: four looks, four pictures");
                string src = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "PipeLook.cs"));
                Assert(src.Contains("PipeStyles.StyleDefName(PipeStyles.PumpDef, PipeStyles.Scrapper)") && src.Contains("Core.Register(new[] { PipeStyles.PumpDef }"),
                    "PipeLook registers the pump with the shared picker once its styles load");
            });
            Case("Pitch_never_solidifies_in_bulk", () =>
            {
                // ruling #6 (owner, typed 2026-10-11): "Pitch stays pitch." No liquid def carries a solid/freeze state, and no
                // production C# turns a stored liquid solid (tanks, bottles, buckets, hoses, pipes).
                string reg = File.ReadAllText(Path.Combine(Defs, "LiquidTypes", "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                foreach (string w in new[] { "<solidif", "<freez", "<congeal", "<setsInto" })
                    Assert(reg.IndexOf(w, StringComparison.OrdinalIgnoreCase) < 0, "registry has no " + w);
                foreach (string rel in new[] { Path.Combine("LiquidTypes", "Building_LiquidTank.cs"), Path.Combine("LiquidTypes", "LiquidDef.cs"),
                                               Path.Combine("LiquidTypes", "RM_LiquidBottleUtility.cs") })
                {
                    string s = RiverSwitchFlipChecks.Src(rel);
                    Assert(s.IndexOf("solidif", StringComparison.OrdinalIgnoreCase) < 0 && s.IndexOf("freez", StringComparison.OrdinalIgnoreCase) < 0,
                        rel + ": no solidification of stored liquid");
                }
            });
        }
    }
}
