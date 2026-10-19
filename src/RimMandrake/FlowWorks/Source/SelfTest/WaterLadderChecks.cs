// POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD = rebuild plan P14 (design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md; engine
// doc design/RimMandrake/flowworks_natural_water_engine_2026-10-17.md §3 Option B2; owner R10, one kind of water). The L1 rows:
//   1. one ladder table in code, used by both lake drawdown and dug-water staging; metres -> def for each rung;
//   2. no SetTempTerrain call stages liquid in FlowWorks; a wet dug square's base terrain has a water-body type;
//   3. a full natural lake's terrain grid is unchanged by formation or by joining a canal;
//   4. the save migration converts temp fills to base writes with litres unchanged (logged before/after).
// Arithmetic is the PRODUCTION Verse-free code (RM_WaterLadder, RM_PondDepthMath, RM_LevelSolve); the wiring is read from
// production source and the shipped Defs. ⛔ What this cannot see: a live map (vanilla's water-body tracker, FreezeManager,
// a flood over a canal): those are the item's L2 rows.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WaterLadderChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string DefsDir()
        {
            string src = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("FluidDef.cs"));
            return Path.Combine(Path.GetDirectoryName(src), "Defs");
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("P14_one_ladder_maps_metres_to_def_for_every_rung", () =>
            {
                var want = new (double m, RM_WaterLadder.Rung rung, string def)[]
                {
                    (0.0, RM_WaterLadder.Rung.Dry, null),
                    (0.10, RM_WaterLadder.Rung.VeryShallow, "RM_WaterVeryShallow"),   // under 25 cm: the damp-film look (R2)
                    (0.50, RM_WaterLadder.Rung.Thin, "RM_WaterThin"),
                    (1.00, RM_WaterLadder.Rung.Shallow, "WaterShallow"),
                    (1.50, RM_WaterLadder.Rung.ChestDeep, "RM_WaterChestDeepStill"),
                    (2.00, RM_WaterLadder.Rung.Deep, "WaterDeep"),
                    (6.00, RM_WaterLadder.Rung.Deep, "WaterDeep"),
                };
                foreach (var w in want)
                {
                    RM_WaterLadder.Rung r = RM_WaterLadder.RungForMetres(w.m);
                    Assert(r == w.rung, w.m + " m is rung " + w.rung + ", got " + r);
                    Assert(RM_WaterLadder.FreshwaterDefName(r) == w.def, w.m + " m shows " + (w.def ?? "nothing") + ", got "
                        + (RM_WaterLadder.FreshwaterDefName(r) ?? "null"));
                }
                // the band edges sit halfway between rungs
                Assert(RM_WaterLadder.RungForMetres(0.24) == RM_WaterLadder.Rung.VeryShallow
                    && RM_WaterLadder.RungForMetres(0.26) == RM_WaterLadder.Rung.Thin, "edge at 25 cm");
                Assert(RM_WaterLadder.RungForMetres(1.74) == RM_WaterLadder.Rung.ChestDeep
                    && RM_WaterLadder.RungForMetres(1.76) == RM_WaterLadder.Rung.Deep, "edge at 1.75 m");
                // the shipped ladder defs exist: the two of ours in Defs, the vanilla two by name (vanilla Data is not read here)
                string stage = File.ReadAllText(Path.Combine(DefsDir(), "Canals", "TerrainDefs", "FlowWorks_PondStageTerrain.xml"));
                Assert(stage.Contains("<defName>RM_WaterThin</defName>") && stage.Contains("<defName>RM_WaterChestDeepStill</defName>"),
                    "RM_WaterThin and RM_WaterChestDeepStill are shipped");
                Assert(stage.Contains("<defName>RM_WaterVeryShallow</defName>"), "RM_WaterVeryShallow is shipped (its PNG is outside the staged selftest tree)");
                Assert(Regex.IsMatch(stage, @"<defName>RM_WaterVeryShallow</defName>[\s\S]*?<texturePath>RimMandrake/FlowWorks/Terrain/RM_WaterVeryShallow</texturePath>"),
                    "the under-25 cm def points at its own texture");
                string dof = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorks_DefOf.cs");
                Assert(dof.Contains("public static TerrainDef RM_WaterThin;") && dof.Contains("public static TerrainDef RM_WaterChestDeepStill;"),
                    "and bound in DefOf (a typo fails the load)");
            });

            Case("P14_lake_drawdown_and_dug_staging_read_the_same_table", () =>
            {
                // the lake: StageForExact's wet stages are the ladder's rungs, for every depth below full
                int U = RM_LevelSolve.U;
                // below the deep band (a deep-bedded square holding 2 m+ keeps its own deep terrain: that is the Original rule)
                for (long dl = 5; dl < 7L * U / 2; dl += 7)
                {
                    RM_PondDepthMath.Stage st = RM_PondDepthMath.StageForExact(dl, 40);
                    Assert(st == RM_WaterLadder.PondStageOf(RM_WaterLadder.RungForDl(dl)), dl + " dl: pond stage " + st);
                    Assert(RM_WaterLadder.RungOfPondStage(st) == RM_WaterLadder.RungForDl(dl)
                        || RM_WaterLadder.RungForDl(dl) == RM_WaterLadder.Rung.VeryShallow, dl + " dl: stage and rung agree");
                }
                string pd = RiverSwitchFlipChecks.Src("RM_PondDepthMath.cs");
                RiverSwitchFlipChecks.Has(pd, @"return RM_WaterLadder\.PondStageOf\(RM_WaterLadder\.RungForDl\(w\)\);", "StageForExact reads the ladder");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"return RM_WaterLadderDefs\.Freshwater\(RM_WaterLadder\.RungOfPondStage\(stage\)\);",
                    "PondStageTerrain writes the ladder's terrain");
                RiverSwitchFlipChecks.Has(ex, @"\? original : RM_WaterLadderDefs\.Freshwater\(RM_WaterLadder\.Rung\.Deep\);", "the deep stage too");
                Assert(!Regex.IsMatch(ex, @"return TerrainDefOf\.WaterShallow;|return RimMandrakeFlowWorks_DefOf\.RM_WaterThin;"),
                    "no second list of stage terrains in PondStageTerrain");
                // the dug square: ApplyFillTerrain -> FluidDef.WetTerrainForBand -> the same RM_WaterLadderDefs table for water
                RiverSwitchFlipChecks.Has(ex, @"want = fluid\.WetTerrainForBand\(RM_ExcavationDepth\.FillTier\(WaterDl\(i\)\)\);", "dug water asks the ladder");
                string fd = RiverSwitchFlipChecks.Src("FluidDef.cs");
                RiverSwitchFlipChecks.Has(fd, @"if \(freshwaterLadder\) \{ TerrainDef t = RM_WaterLadderDefs\.Freshwater\(", "water's wet look is the freshwater ladder");
                string ld = RiverSwitchFlipChecks.Src("RM_WaterLadderDefs.cs");
                RiverSwitchFlipChecks.Has(ld, @"string name = RM_WaterLadder\.FreshwaterDefName\(", "the def resolver reads the one table, no second list");
                XDocument fl = XDocument.Load(Path.Combine(DefsDir(), "Canals", "FluidDefs", "FlowWorks_Fluids.xml"));
                XElement water = fl.Descendants().First(e => (string)e.Element("defName") == "RM_Fluid_Water");
                Assert((string)water.Element("freshwaterLadder") == "true", "RM_Fluid_Water stages the freshwater ladder");
                int ladders = fl.Descendants("freshwaterLadder").Count()
                    + XDocument.Load(Path.Combine(DefsDir(), "Canals", "FluidDefs", "FlowWorks_PitFluids.xml")).Descendants("freshwaterLadder").Count();
                Assert(ladders == 1, "only water uses the freshwater ladder; every other liquid keeps its own (" + ladders + ")");
            });

            Case("P14_no_SetTempTerrain_stages_liquid_and_wet_dug_squares_have_a_water_body_type", () =>
            {
                string src = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("FluidDef.cs"));
                var hits = new List<string>();
                foreach (string f in Directory.GetFiles(src, "*.cs", SearchOption.AllDirectories))
                {
                    if (f.Contains(Path.DirectorySeparatorChar + "SelfTest" + Path.DirectorySeparatorChar)
                        || f.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar))
                    {
                        continue;
                    }
                    string[] lines = File.ReadAllLines(f);
                    for (int n = 0; n < lines.Length; n++)
                    {
                        string l = lines[n].Trim();
                        if (l.StartsWith("//") || l.StartsWith("///") || l.StartsWith("*"))
                        {
                            continue;
                        }
                        if (Regex.IsMatch(l, @"\.SetTempTerrain\("))
                        {
                            hits.Add(Path.GetFileName(f) + ":" + (n + 1));
                        }
                    }
                }
                // The one left is a SPILL over open natural water (a flood in vanilla's sense), never a dug square.
                Assert(hits.Count == 1 && hits[0].StartsWith("Flood_FlowWorks.cs:"), "SetTempTerrain sites: " + string.Join(", ", hits));
                string fl = RiverSwitchFlipChecks.Src("Flood_FlowWorks.cs");
                RiverSwitchFlipChecks.Has(fl, @"if \(fluidDef\.floodTerrain == null \|\| !fluidDef\.floodTerrain\.temporary\) \{ placedLookup\.Add\(c\);",
                    "a spill of a base-layer liquid is hands off");
                RiverSwitchFlipChecks.Has(fl, @"if \(policy == RM_StockMath\.FloodCellPolicy\.ViaEngine\)", "dug squares go through the engine");
                Assert(RM_StockMath.FloodPolicy(true, true) == RM_StockMath.FloodCellPolicy.ViaEngine
                    && RM_StockMath.FloodPolicy(true, false) == RM_StockMath.FloodCellPolicy.HandsOff, "a dug square never gets the temp puddle");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"FluidDef held = FluidAt\(c\) \?\? fluid; bool drained = [^;]*; map\.terrainGrid\.SetTerrain\(c, want\);",
                    "ApplyFillTerrain is a base write");
                // every non-water liquid's tiers are base-layer defs with their own water-body type; water's ladder is freshwater
                var tiers = new HashSet<string>();
                foreach (string ff in new[] { "FlowWorks_Fluids.xml", "FlowWorks_PitFluids.xml" })
                {
                    foreach (XElement fdef in XDocument.Load(Path.Combine(DefsDir(), "Canals", "FluidDefs", ff)).Root.Elements())
                    {
                        if ((string)fdef.Element("freshwaterLadder") == "true")
                        {
                            continue;
                        }
                        foreach (string tag in new[] { "floodTerrain", "fillTerrainVeryShallow", "fillTerrainHalf", "fillTerrainBrim", "fillTerrainSuperdeep" })
                        {
                            string v = (string)fdef.Element(tag);
                            if (!string.IsNullOrEmpty(v)) tiers.Add(v);
                        }
                    }
                }
                Assert(tiers.Count >= 40, "non-water tiers found: " + tiers.Count);
                var terr = new Dictionary<string, XElement>();
                foreach (string tf in Directory.GetFiles(Path.Combine(DefsDir(), "Canals", "TerrainDefs"), "*.xml"))
                {
                    foreach (XElement t in XDocument.Load(tf).Root.Elements("TerrainDef"))
                    {
                        string dn = (string)t.Element("defName");
                        if (dn != null) terr[dn] = t;
                    }
                }
                foreach (string t in tiers)
                {
                    Assert(terr.ContainsKey(t), t + " is shipped");
                    Assert((string)terr[t].Element("temporary") != "true", t + " is a base-layer def (not temporary)");
                    Assert((string)terr[t].Element("waterBodyType") == "Other", t + " carries its own water-body type (Other: no fish)");
                    Assert((string)terr[t].Attribute("ParentName") == "WaterShallow", t + " is in the water family (inherits IsWater)");
                }
                foreach (string w in new[] { "RM_WaterVeryShallow", "RM_WaterThin", "RM_WaterChestDeepStill" })
                {
                    XElement t = XDocument.Load(Path.Combine(DefsDir(), "Canals", "TerrainDefs", "FlowWorks_PondStageTerrain.xml"))
                        .Root.Elements("TerrainDef").First(e => (string)e.Element("defName") == w);
                    Assert((string)t.Attribute("ParentName") == "WaterShallowBase" && t.Element("temporary") == null && t.Element("waterBodyType") == null,
                        w + " inherits vanilla WaterShallowBase's Freshwater body type, on the base layer");
                }
            });

            Case("P14_full_natural_lake_terrain_unchanged_by_formation_or_a_joining_canal", () =>
            {
                // full (at its brim, the state formation and a canal joining at the brim leave it in): every square keeps its
                // own terrain, whatever its floor
                var beds = new List<int> { 1, 2, 3, 4, 6, 9, 20, 40, 120, 250 };
                int[] h = RM_PondDepthMath.Histogram(beds);
                long cap = RM_LevelSolve.PondCapacity(h);
                double surf = RM_LevelSolve.PondSurfaceHeight(h, cap);
                foreach (int b in beds)
                {
                    Assert(RM_PondDepthMath.StageForExact(RM_LevelSolve.PondSquareWater(b, surf), b) == RM_PondDepthMath.Stage.Original,
                        "bed " + b + " at the brim keeps its own terrain (R10)");
                }
                // formation writes no terrain
                string st = RiverSwitchFlipChecks.Src("RM_LiquidStock.cs");
                int a = st.IndexOf("public int FormAllBodies(Map map, RM_MapComponent_Excavation owner)", StringComparison.Ordinal);
                Assert(a >= 0, "FormAllBodies found");
                int e = st.IndexOf(" public ", a + 10, StringComparison.Ordinal);
                string form = e > a ? st.Substring(a, e - a) : st.Substring(a);
                Assert(!form.Contains("SetTerrain") && !form.Contains("StageNaturalCell") && !form.Contains("SetTempTerrain"),
                    "FormAllBodies writes no terrain");
                // a joining canal's base-layer water is never read as natural: the lake's footprint, sources and bed reads
                // stop at a dug square (the guard keeps every answer what it was when dug squares were always dry channels)
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"private bool IsNaturalLiquid\(IntVec3 c\) \{ //[^{]*?if \(c\.InBounds\(map\) && depthGrid\[map\.cellIndices\.CellToIndex\(c\)\] != 0\) \{ return false; \}",
                    "IsNaturalLiquid is false on a dug square");
                RiverSwitchFlipChecks.Has(ex, @"if \(depthGrid\[i\] == 0\) \{ return; //", "ApplyFillTerrain never draws on an undug (lake) square");
            });

            Case("P14_save_migration_temp_fill_to_base_write_litres_logged", () =>
            {
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"private int fillLayerModel = 1;", "a new map starts on the base layer");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Values\.Look\(ref fillLayerModel, ""RM_fillLayerModel"", 0\);", "an old save loads as model 0");
                RiverSwitchFlipChecks.Has(ex, @"depthViewModel = 1; \} MigrateFillLayer\(\);", "migrated once in FinalizeInit");
                Match m = Regex.Match(ex, @"private void MigrateFillLayer\(\) \{.*?fillLayerModel = 1; \}");
                Assert(m.Success, "MigrateFillLayer found");
                string body = m.Value;
                Assert(body.Contains("map.terrainGrid.RemoveTempTerrain(c);") && body.Contains("ApplyFillTerrain(c, FluidAt(c) ?? ActiveFluid);"),
                    "each temp fill comes off and the square is redrawn on the base layer");
                Assert(body.Contains("beforeDl += WaterDl(i);") && body.Contains("afterDl += WaterDl(i);") && body.Contains("Log.Message("),
                    "litres summed before and after and logged");
                Assert(!Regex.IsMatch(body, @"(fillGrid|partGrid|depthGrid|fluidGrid)\[[^\]]*\] ?[-+]?="), "the migration writes no grid: no water moves");
            });
        }
    }
}
