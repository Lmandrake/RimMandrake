// SPRINKLER_HEADS_BUILD_PUMP_REQUIRED (design/RimMandrake/sprinklers_design_2026-10-16.md §6 step 1, OQ-S1..S7 ruled 2026-10-16).
// Offline halves: the production kernel (Sprinklers/RM_SprinklerKernel.cs, compiled in) and the shipped XML (head def, styles,
// mote, the VFE FindMod patch) plus the call sites that carry the rulings. Each case has a can-fail.
// NOT proven here (live, owed; FlowWorks.md walk rows): a head on a pump net drawing cells x 0.5 L per hour, drying when
// starved, clogging on tar, the liquid key of a slime, No pressure without a pump, the VFE boost skipped in our biomes.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Sprinklers;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SprinklerChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string ModRoot => Path.GetDirectoryName(Path.GetDirectoryName(ContainerMatFixture.Root()));
        private static string Src(string rel) => File.ReadAllText(Path.Combine(ModRoot, "Source", rel));

        private const int UPL = 10;   // RM_Volume.UnitsPerLitre (decilitres)

        public static void Run(Action<string, Action> Case)
        {
            Case("Sprinkler_ruled_cost", () =>
            {
                Assert(RM_SprinklerKernel.UnitsFor(29, 0.5f, UPL) == 145, "OQ-S1: 29 cells x 0.5 L = 14.5 L = 145 units");
                Assert(RM_SprinklerKernel.UnitsFor(1, 0.05f, UPL) == 1, "rounds up, never free");
                Assert(RM_SprinklerKernel.UnitsFor(0, 0.5f, UPL) == 0 && RM_SprinklerKernel.UnitsFor(29, 0f, UPL) == 0, "nothing costs nothing");
                Assert(Math.Abs(RM_SprinklerKernel.UnitsFor(29, 0.5f, UPL) * 24 / 10f - 348f) < 0.01f, "~350 L a day for a native head");
                Assert(RM_SprinklerKernel.UnitsFor(29, 0.5f, UPL) != 290, "can-fail: not a litre per cell");
            });
            Case("Sprinkler_pulse_all_or_nothing", () =>
            {
                Assert(RM_SprinklerKernel.Decide(true, true, true, true, false, 29, 145, 145) == RM_SprinklerState.Spraying, "exactly enough sprays");
                Assert(RM_SprinklerKernel.Decide(true, true, true, true, false, 29, 145, 144) == RM_SprinklerState.Dry, "one unit short is Dry, not a part spray");
                Assert(RM_SprinklerKernel.Decide(true, true, true, false, false, 29, 145, 0) == RM_SprinklerState.NoLiquid, "empty net");
            });
            Case("Sprinkler_needs_a_pump", () =>
            {
                Assert(RM_SprinklerKernel.Decide(true, true, false, true, false, 29, 145, 99999) == RM_SprinklerState.NoPressure, "OQ-S2: no pump, no spray however full");
                Assert(RM_SprinklerKernel.Decide(true, true, true, true, false, 29, 145, 99999) == RM_SprinklerState.Spraying, "can-fail: a pump flips it");
                Assert(RM_SprinklerKernel.Decide(false, true, true, true, false, 29, 145, 99999) == RM_SprinklerState.Disabled, "setting off");
                Assert(RM_SprinklerKernel.Decide(true, false, true, true, false, 29, 145, 99999) == RM_SprinklerState.SwitchedOff, "flick off");
            });
            Case("Sprinkler_thick_liquid_clogs", () =>
            {
                Assert(RM_SprinklerKernel.Decide(true, true, true, true, true, 29, 145, 99999) == RM_SprinklerState.Clogged, "tar clogs");
                Assert(RM_SprinklerKernel.Sprays(false) && !RM_SprinklerKernel.Sprays(true), "thin sprays, thick not");
            });
            Case("Sprinkler_expiry_one_pulse_plus_grace", () =>
            {
                int until = RM_SprinklerKernel.WetUntil(1000);
                Assert(until == 1000 + 2500 + 250, "wet until next pulse + grace");
                Assert(RM_SprinklerKernel.IsWet(until, 1000 + 2749) && !RM_SprinklerKernel.IsWet(until, 1000 + 2750), "dry within 2,750 ticks");
            });
            Case("Sprinkler_spend_dries_until_next_pulse", () =>
            {
                var g = new RM_SprinkledGrid(10);
                g.Wet(3, "RM_Fluid_Water", RM_SprinklerKernel.WetUntil(0), 7);
                Assert(g.WetBy(3, 100) == "RM_Fluid_Water", "wet with its liquid key");
                Assert(g.Spend(3, 100) && g.WetBy(3, 101) == null, "EC3: spent is dry");
                Assert(!g.Spend(3, 102), "can-fail: a dry cell spends nothing");
                g.Wet(3, "RM_Fluid_Water", RM_SprinklerKernel.WetUntil(2500), 7);
                Assert(g.WetBy(3, 2600) != null, "the next paid pulse re-wets it");
                Assert(!g.WetByOther(3, 7, 2600) && g.WetByOther(3, 8, 2600), "owner tracked per head");
            });
            Case("Sprinkler_liquid_key_per_cell", () =>
            {
                var g = new RM_SprinkledGrid(4);
                g.Wet(0, "RM_Fluid_Water", 100, 1);
                g.Wet(1, "RM_Fluid_GreenSlime", 100, 2);
                Assert(g.WetBy(0, 0) == "RM_Fluid_Water" && g.WetBy(1, 0) == "RM_Fluid_GreenSlime", "each cell keeps its liquid");
                Assert(g.LiveCells(0) == 2 && g.LiveCells(100) == 0, "live count and expiry");
            });
            Case("Sprinkler_picks_most_held_liquid", () =>
            {
                var held = new[] { KV("B", 50), KV("A", 30), KV("A", 30) };
                Assert(RM_SprinklerKernel.PickLiquid(held) == "A", "sums across tanks");
                Assert(RM_SprinklerKernel.PickLiquid(new[] { KV("B", 10), KV("A", 10) }) == "A", "ties by name");
                Assert(RM_SprinklerKernel.PickLiquid(new KeyValuePair<string, int>[0]) == null, "nothing held");
            });
            Case("Sprinkler_sealed_cells_never_charged", () =>
            {
                var cells = new List<RM_ValveCell>
                {
                    new RM_ValveCell(0, 0f, false, false, false, false, false),
                    new RM_ValveCell(1, 1f, true, true, false, true, false),
                    new RM_ValveCell(2, 1f, true, false, false, true, false),
                };
                List<int> n = RM_SprinklerKernel.NativeCharge(cells);
                Assert(n.SequenceEqual(new[] { 0, 2 }), "native: every cell but the sealed one (dark and bare cells too)");
                List<int> v = RM_SprinklerKernel.Valve(cells, 0.5f, UPL, -1, 0, 0, out _);
                Assert(v.SequenceEqual(new[] { 2 }), "valve: only the lit, unsealed plant");
            });
            Case("Sprinkler_valve_budget_and_reserve", () =>
            {
                var cells = new List<RM_ValveCell>();
                for (int i = 0; i < 10; i++) cells.Add(new RM_ValveCell(i, 10 - i, true, false, i == 9, true, i == 8));
                List<int> all = RM_SprinklerKernel.Valve(cells, 0.5f, UPL, -1, 0, 0, out bool t0);
                Assert(all.Count == 8 && !t0, "skips already-wet and exempt cells");
                List<int> b = RM_SprinklerKernel.Valve(cells, 0.5f, UPL, 15, 0, 0, out bool t1);
                Assert(b.Count == 3 && t1 && b[0] == 7, "15 units pays 3 cells, nearest first (got " + string.Join(",", b) + ")");
                List<int> r = RM_SprinklerKernel.Valve(cells, 0.5f, UPL, -1, 1020, 1000, out bool t2);
                Assert(r.Count == 4 && t2, "reserve floor: 20 units above the floor pays 4 cells");
                Assert(RM_SprinklerKernel.Valve(cells, 0.5f, UPL, 0, 0, 0, out _).Count == 0, "budget spent: nothing");
                Assert(RM_SprinklerKernel.BudgetLeft(0, 50, UPL) == -1 && RM_SprinklerKernel.BudgetLeft(10, 50, UPL) == 50, "budget arithmetic");
                Assert(RM_SprinklerKernel.Saved(10, 4, 0.5f, UPL) == 30, "saved litres");
            });
            Case("Sprinkler_conserves_litres", () =>
            {
                string s = Src("Sprinklers/RM_Sprinkle.cs");
                Assert(s.Contains("RM_LiquidTransfer.Move(r.need, source, sink, out RM_MoveOutcome _) == r.need)"), "the draw is one conserving Move, all-or-nothing");
                Assert(s.Contains("RM_LiquidNet.DrawPlan(head, liquid, r.need)"), "drawn by the net's draw plan");
                Assert(s.Contains("p.Working"), "OQ-S2: a WORKING pump");
                Assert(Src("Machinery/RM_LiquidNet.cs").Contains("GetComp<Sprinklers.CompRM_SprinklerBase>()"), "a head is a machine on the net");
            });
            Case("Sprinkler_walls_and_effects_wired", () =>
            {
                string s = Src("Sprinklers/RM_Sprinkle.cs");
                Assert(s.Contains("GenSight.LineOfSight(o, c, map, true)"), "OQ-S7: line of sight from the head");
                Assert(s.Contains("damageOnContact") && s.Contains("liquid.hot") && s.Contains("liquid.flammable") && s.Contains("RM_LiquidSpill.Spill"), "OQ-S5 effects");
            });
            Case("Sprinkler_shipped_defs", () =>
            {
                XDocument d = XDocument.Load(Path.Combine(ModRoot, "Defs", "Sprinklers", "RM_Sprinklers.xml"));
                XElement head = d.Descendants("ThingDef").FirstOrDefault(e => (string)e.Element("defName") == "RM_SprinklerHead");
                Assert(head != null, "RM_SprinklerHead ships");
                Assert(head.Descendants("li").Any(l => l.Value == "RimMandrake.FlowWorks.Sprinklers.PlaceWorker_RM_OnPipe"), "on-pipe placeworker");
                Assert(!head.Descendants("li").Any(l => ((string)l.Attribute("Class") ?? "").Contains("CompProperties_Power")), "OQ-S2: no electrical power");
                Assert((string)head.Element("costList")?.Element("Steel") == "5", "5 steel");
                foreach (string look in new[] { "Scrapper", "Industrial", "Modern", "Futuristic" })
                {
                    XElement st = d.Descendants("ThingStyleDef").FirstOrDefault(e => (string)e.Element("defName") == "RM_SprinklerHead_" + look);
                    Assert(st != null, "style " + look);
                    string tex = (string)st.Element("graphicData")?.Element("texPath");
                    Assert(tex == "RimMandrake/FlowWorks/Sprinkler/" + look + "/RM_SprinklerHead", "art path for " + look + ": " + tex);
                }
                Assert(d.Descendants("ThingDef").Any(e => (string)e.Element("defName") == "RM_Mote_SprinklerSpray"), "spray mote");
            });
            Case("Sprinkler_vfe_patch_findmod", () =>
            {
                XDocument p = XDocument.Load(Path.Combine(ModRoot, "Patches", "Compat", "RM_VFEFarming_Sprinkler.xml"));
                XElement op = p.Root.Element("Operation");
                Assert((string)op.Attribute("Class") == "PatchOperationFindMod", "FindMod, never a top-level MayRequire");
                Assert(op.Element("mods").Elements("li").Any(l => l.Value == "Vanilla Furniture Expanded - Farming"), "the VFE mod name");
                Assert(op.ToString().Contains("VFE_Sprinkler") && op.ToString().Contains("CompProperties_RM_SmartSprinkler"), "adds our comp to VFE_Sprinkler");
                string c = Src("Sprinklers/CompRM_SmartSprinkler.cs");
                Assert(c.Contains("\"VFEF.VFEF_SprinklersManager\"") && c.Contains("\"BoostPlantAt\", new[] { typeof(IntVec3) }"), "OQ-S3: prefix target by name");
                Assert(c.Contains("InOurBiomes(__instance?.map)") && c.Contains("return true;"), "OQ-S3: skipped only in our biomes");
                Assert(!c.Contains("using VFEF"), "can-fail: no compile reference to VFEF");
            });

            Case("Sprinkler_review_fixes_B1_P1_in_source", () =>
            {
                string m = Src("Sprinklers/RM_MapComponent_Sprinklers.cs");
                Assert(m.Contains("Scribe.mode == LoadSaveMode.LoadingVars && cells != null"), "B1: the wet grid is rebuilt in LoadingVars, where the lists are filled");
                Assert(!m.Contains("LoadSaveMode.PostLoadInit"), "can-fail: PostLoadInit sees fresh null locals, so the rebuild never ran");
                Assert(m.Contains("cachedMap") && m.Contains("cachedComp.map == map"), "P1: Of() keeps a one-slot map-component cache");
            });
        }

        private static KeyValuePair<string, int> KV(string k, int v) => new KeyValuePair<string, int>(k, v);
    }
}
