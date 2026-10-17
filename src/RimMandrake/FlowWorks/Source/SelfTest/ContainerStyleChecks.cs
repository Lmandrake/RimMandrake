// LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS (owner 2026-10-16: "They too should have the four styles of art."; sheet approved
// 100%; by card: material colour on the TRIM only, body keeps its painted style, liquid shows in the masked window).
// Offline halves: the Verse-free RM_ContainerStyleMath rules, the SHIPPED XML (style defs, ItemBases, the Dubs Bad Hygiene
// coloured bottles, the generated filled defs) and the call sites. Each property has a can-fail.
// NOT proven here: the bill's Style button opening and the crafted product wearing the pick, a filled/drunk/washed
// container keeping its look, two looks never merging on a stockpile cell, the window/trim tints reading in game. Those are
// the live rows of validation.py's container_styles chain and the review map station containers_styles.
using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.FlowWorks.LiquidTypes;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ContainerStyleChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string LiquidDefs => ContainerMatFixture.Root();
        private static string ModRoot => Path.GetDirectoryName(Path.GetDirectoryName(LiquidDefs));

        private static readonly (string size, string drawSize)[] Sizes = { ("Bottle", "0.75"), ("Bucket", "1.0"), ("Barrel", "1.4") };

        private static XElement Named(XDocument d, string name) =>
            d.Descendants("ThingDef").FirstOrDefault(e => (string)e.Attribute("Name") == name);

        public static void Run(Action<string, Action> Case)
        {
            Case("ContainerStyle_looks_and_names", () =>
            {
                Assert(RM_ContainerStyleMath.Looks.SequenceEqual(HoseStyles.Looks), "the same four looks, same order, as hoses/pipes/tanks");
                Assert(RM_ContainerStyleMath.StyleDefName("Bucket", "Modern") == "RM_Bucket_Modern", "style def naming");
                Assert(RM_ContainerStyleMath.TexPath("Barrel", "Futuristic") == "Things/Item/Resource/FlowWorks/Futuristic/RM_Barrel", "texture path");
                Assert(RM_ContainerStyleMath.LookOfStyleDefName("RM_Bottle_Scrapper") == "Scrapper", "look read back from a style def");
                Assert(RM_ContainerStyleMath.LookOfStyleDefName("RM_LiquidTank_Modern") == null, "can-fail: a tank's style is not a container look");
                Assert(RM_ContainerStyleMath.LookOfStyleDefName("RM_Bottle_Gold") == null, "can-fail: unknown look");
                Assert(RM_ContainerStyleMath.LookOfStyleDefName(null) == null && RM_ContainerStyleMath.LookOfStyleDefName("RM_") == null, "can-fail: nothing");
            });
            Case("ContainerStyle_tech_default", () =>
            {
                Assert(RM_ContainerStyleMath.LookForTech("Neolithic") == "Scrapper" && RM_ContainerStyleMath.LookForTech("Medieval") == "Scrapper", "tribes scavenge");
                Assert(RM_ContainerStyleMath.LookForTech("Industrial") == "Industrial", "industrial: plain water bottle");
                Assert(RM_ContainerStyleMath.LookForTech("Spacer") == "Modern", "spacer: soda bottle");
                Assert(RM_ContainerStyleMath.LookForTech("Ultra") == "Futuristic" && RM_ContainerStyleMath.LookForTech("Archotech") == "Futuristic", "ultra: canteen");
                Assert(RM_ContainerStyleMath.LookForTech("Undefined") == "Industrial" && RM_ContainerStyleMath.LookForTech(null) == "Industrial", "unknown: fallback");
            });
            Case("ContainerStyle_stacks_keep_looks_apart", () =>
            {
                Assert(RM_ContainerStyleMath.MayStack("Modern", "Modern"), "same look stacks");
                Assert(!RM_ContainerStyleMath.MayStack("Modern", "Scrapper"), "can-fail: two looks never merge");
                Assert(RM_ContainerStyleMath.MayStack("Modern", null), "an unstyled incoming stack takes the stack's look");
                Assert(!RM_ContainerStyleMath.MayStack(null, "Modern"), "a styled stack is never swallowed by an unstyled one");
                Assert(RM_ContainerStyleMath.MayStack(null, null), "two unstyled stack");
            });
            Case("ContainerStyle_window_colours", () =>
            {
                float[] e = RM_ContainerStyleMath.EmptyWindow, d = RM_ContainerStyleMath.DirtyWindow;
                Assert(e.Length == 3 && d.Length == 3, "rgb");
                Assert(e.All(c => c >= 0.8f && c <= 1f), "empty reads as pale clear glass");
                Assert(d.All(c => c < 0.6f) && d[0] > d[2], "dirty reads as grime brown (darker, warm)");
            });
            Case("ContainerStyle_shipped_style_defs", () =>
            {
                XDocument st = XDocument.Load(Path.Combine(LiquidDefs, "ThingDefs", "RM_LiquidContainerStyles.xml"));
                var defs = st.Descendants("ThingStyleDef").ToList();
                Assert(defs.Count == 12, "twelve container styles, found " + defs.Count);
                XDocument b = XDocument.Load(Path.Combine(LiquidDefs, "ThingDefs", "RM_LiquidBottles_Base.xml"));
                foreach (var (size, draw) in Sizes)
                {
                    string baseDraw = (string)Named(b, "RM_" + size + "ItemBase")?.Element("graphicData")?.Element("drawSize");
                    Assert(baseDraw == draw, size + " ItemBase drawSize " + baseDraw);
                    foreach (string look in RM_ContainerStyleMath.Looks)
                    {
                        string dn = RM_ContainerStyleMath.StyleDefName(size, look);
                        XElement s = defs.FirstOrDefault(e => (string)e.Element("defName") == dn);
                        Assert(s != null, dn + " present");
                        XElement g = s.Element("graphicData");
                        Assert((string)g.Element("texPath") == RM_ContainerStyleMath.TexPath(size, look), dn + ": owned art path");
                        Assert((string)g.Element("shaderType") == "CutoutComplex", dn + ": masked (window + trim)");
                        Assert((string)g.Element("graphicClass") == "Graphic_Single", dn + ": single graphic");
                        Assert((string)g.Element("drawSize") == draw, dn + ": a style never resizes the container");
                    }
                }
                foreach (string f in Directory.GetFiles(Path.Combine(ModRoot, "Defs"), "*.xml", SearchOption.AllDirectories))
                {
                    XDocument x = XDocument.Load(f);
                    Assert(!x.Descendants("StyleCategoryDef").Descendants().Any(e => ((string)e).StartsWith("RM_Bottle_") || ((string)e).StartsWith("RM_Bucket_") || ((string)e).StartsWith("RM_Barrel_")),
                        "no ideoligion style category hands out a container look (" + Path.GetFileName(f) + ")");
                }
            });
            Case("ContainerStyle_item_bases_wired", () =>
            {
                XDocument b = XDocument.Load(Path.Combine(LiquidDefs, "ThingDefs", "RM_LiquidBottles_Base.xml"));
                foreach (var (size, _) in Sizes)
                {
                    XElement d = Named(b, "RM_" + size + "ItemBase");
                    Assert(d != null, size + " ItemBase");
                    Assert((string)d.Element("thingClass") == "RimMandrake.FlowWorks.LiquidTypes.RM_LiquidContainer", size + ": trim colour class");
                    XElement g = d.Element("graphicData");
                    Assert((string)g.Element("texPath") == RM_ContainerStyleMath.TexPath(size, "Industrial") && (string)g.Element("shaderType") == "CutoutComplex",
                        size + ": an unstyled container draws the masked Industrial look");
                    var comps = d.Element("comps").Elements("li").ToList();
                    Assert(comps.Any(li => (string)li.Attribute("Class") == "CompProperties_Styleable"), size + ": CompStyleable stores the look");
                    Assert(comps.Any(li => (string)li.Element("compClass") == "RimMandrake.FlowWorks.LiquidTypes.RM_CompContainerStyle"), size + ": style lifecycle comp");
                    Assert(comps.Any(li => (string)li.Element("compClass") == "RimMandrake.FlowWorks.LiquidTypes.RM_CompContainerMaterial"), size + ": window colour comp kept");
                }
                // the generated filled defs inherit all of it and override none of it
                XDocument gen = XDocument.Load(Path.Combine(LiquidDefs, "ThingDefs", "RM_LiquidBottles.xml"));
                var filled = gen.Descendants("ThingDef").ToList();
                Assert(filled.Count >= 27, "generated filled containers present (" + filled.Count + ")");
                foreach (XElement f in filled)
                {
                    string p = (string)f.Attribute("ParentName");
                    Assert(p == "RM_BottleItemBase" || p == "RM_BucketItemBase" || p == "RM_BarrelItemBase", (string)f.Element("defName") + " parent " + p);
                    Assert(f.Element("thingClass") == null && f.Element("graphicData") == null, (string)f.Element("defName") + ": overrides neither class nor graphic");
                }
            });
            Case("ContainerStyle_dbh_bottles_masked", () =>
            {
                // THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY (OQ-4, owner by card 2026-10-16): the five DBH-only RM_WaterBottle_<Colour>
                // defs are gone; the coloured waters are registry rows whose generated RM_Bottle_<Colour>Water inherit the
                // masked Industrial bottle (RM_BottleItemBase) and get their window colour from the LiquidDef, like every bottle.
                Assert(!File.Exists(Path.Combine(ModRoot, "Patches", "RM_ColoredWaterBottles_Patch.xml")), "the DBH-only coloured-bottle patch is deleted");
                XDocument gen = XDocument.Load(Path.Combine(LiquidDefs, "ThingDefs", "RM_LiquidBottles.xml"));
                XDocument reg = XDocument.Load(Path.Combine(LiquidDefs, "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                foreach (string c in new[] { "Rust", "Verdigris", "Amber", "Violet", "Chalk" })
                {
                    XElement t = gen.Descendants("ThingDef").FirstOrDefault(e => (string)e.Element("defName") == "RM_Bottle_" + c + "Water");
                    Assert(t != null, "RM_Bottle_" + c + "Water generated");
                    Assert((string)t.Attribute("ParentName") == "RM_BottleItemBase" && t.Element("graphicData") == null, c + ": the masked Industrial bottle, no own graphic");
                    XElement row = reg.Root.Elements().FirstOrDefault(e => (string)e.Element("defName") == "RM_Liquid_" + c + "Water");
                    Assert(row != null && row.Element("color") != null && (string)row.Element("thirstQuality") == "Potable", c + ": a Potable row with its own window colour");
                }
                Assert(!gen.ToString().Contains("RM_WaterBottle_"), "can-fail: no old DBH-only defName survives");
            });
            Case("ContainerStyle_call_sites", () =>
            {
                string util = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "RM_LiquidBottleUtility.cs"));
                RiverSwitchFlipChecks.Has(util, @"RM_ContainerStyles\.CarryStyle\(from, made\); return made;", "MakeContainer carries the look through every chain step");
                string mat = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "RM_ContainerMaterials.cs"));
                RiverSwitchFlipChecks.Has(mat, @"return ext\.liquid\.color;", "filled: the liquid's colour in the window");
                RiverSwitchFlipChecks.Has(mat, @"ext\.dirty \? RM_ContainerStyleMath\.DirtyWindow : RM_ContainerStyleMath\.EmptyWindow", "empty/dirty window colours");
                string sty = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "RM_ContainerStyles.cs"));
                RiverSwitchFlipChecks.Has(sty, @"override Color DrawColorTwo \{ get \{ if \(Stuff != null\) \{ return def\.GetColorForStuff\(Stuff\);", "trim = the material");
                RiverSwitchFlipChecks.Has(sty, @"\[HarmonyPatch\(typeof\(Dialog_BillConfig\), nameof\(Dialog_BillConfig\.DoWindowContents\)\)\]", "the bill dialog carries the Style button");
                RiverSwitchFlipChecks.Has(sty, @"bill\.style = sd; bill\.globalStyle = false;", "a pick writes the bill's own style (vanilla Toils_Recipe applies it)");
                RiverSwitchFlipChecks.Has(sty, @"override void PostSplitOff\(Thing piece\) \{ base\.PostSplitOff\(piece\); if \(piece != null && piece != parent && parent\.StyleDef != null\) \{ piece\.StyleDef = parent\.StyleDef;", "a split keeps the look");
                RiverSwitchFlipChecks.Has(sty, @"override bool AllowStackWith\(Thing other\) => RM_ContainerStyleMath\.MayStack\(", "stacks keep looks apart");
                RiverSwitchFlipChecks.Has(sty, @"override void PostSpawnSetup\(bool respawningAfterLoad\) \{ base\.PostSpawnSetup\(respawningAfterLoad\); if \(parent\.StyleDef == null\)", "an unstyled container gets its faction's look on spawn");
                RiverSwitchFlipChecks.Has(sty, @"override void PostPostGeneratedForTrader\(.*?RM_ContainerStyles\.ApplyDefault\(parent, forFaction\);", "trader stock wears the trader's look");
                string csproj = File.ReadAllText(RiverSwitchFlipChecks.SrcPath("RimMandrake_FlowWorks.csproj"));
                Assert(csproj.Contains(@"LiquidTypes\RM_ContainerStyles.cs") && csproj.Contains(@"LiquidTypes\RM_ContainerStyleMath.cs"), "both files compiled into the mod");
            });
        }
    }
}
