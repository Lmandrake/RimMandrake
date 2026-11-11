// PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT (plan P5) and DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT (plan P6) of
// FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG. Owner R5 (2026-10-17, by card): a dig cap settable 2 to 20 m (DEEP_DIG_BUILD_DROIDS_
// TAKE_THE_SHOVEL, owner card 2026-10-21: colonists 2 m shipped, machine labour 20 m); the
// 0.5 m dig step stays; lakes keep their own floors; the dig cost curve stays 3,200 x the notch being cut; lowering the cap
// never shallows a dug cell; the dig job, work-giver and designator read the depth GRID. Arithmetic is the PRODUCTION
// Verse-free code (RM_DigDepthMath, RM_PocketGridMath, RM_PitTrapMath, RM_CliffMaskMath, the exact kernel on plain arrays);
// the Verse-bound wiring is read from production source.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DeepDigChecks
    {
        private const int U = RM_LevelSolve.U;

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>The 4/7/7/4 square (feasibility §5): ring 12 squares at 4 m (8 notches), core 4 at 7 m (14), placed at
        /// (x0..x0+3, z0..z0+3) on a w-wide grid. Returns (ring, core) cell indices.</summary>
        private static (List<int> ring, List<int> core) Square(int w, int x0, int z0)
        {
            var ring = new List<int>();
            var core = new List<int>();
            for (int z = 0; z < 4; z++)
                for (int x = 0; x < 4; x++)
                {
                    int c = (z0 + z) * w + x0 + x;
                    if (x >= 1 && x <= 2 && z >= 1 && z <= 2) core.Add(c); else ring.Add(c);
                }
            return (ring, core);
        }

        /// <summary>Dig a square by dig-to orders the way the work-giver and the job do: one cut per pass while the square owes
        /// work (RM_DigDepthMath.DigToOwesWork), each cut priced by WorkToCut of the notch being cut. Returns cuts and work.</summary>
        private static (int cuts, long work) DigTo(byte[] depth, IEnumerable<int> cells, int target, int cap, bool curve = true)
        {
            int cuts = 0;
            long work = 0;
            foreach (int c in cells)
            {
                while (RM_DigDepthMath.DigToOwesWork(depth[c], target, cap))
                {
                    work += RM_DigDepthMath.WorkToCut(depth[c] + 1, curve);
                    depth[c]++;
                    cuts++;
                }
            }
            return (cuts, work);
        }

        private static ArrayWorld World(int w, int h, bool exact)
        {
            var world = new ArrayWorld(w, h);
            world.k.levelBySurfaceEnabled = true;
            world.k.levelSetEnabled = true;
            world.k.creepWaterEnabled = true;
            world.k.creepEnabled = true;
            world.k.viscosityEnabled = true;
            world.k.levelExactEnabled = exact;
            return world;
        }

        private static long TotalDl(ArrayWorld w)
        {
            long t = 0;
            for (int i = 0; i < w.w * w.h; i++) if (w.k.depth[i] > 0) t += w.k.WaterOf(i);
            return t;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("DeepDig_cap_setting_2_8_20_and_never_shallows", () =>
            {
                // the setting: 2 m .. 20 m in half-metre steps; colonists 2 m shipped (DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL)
                Assert(RM_DigDepthMath.ClampCap(4f) == 4 && RM_DigDepthMath.ClampCap(16f) == 16 && RM_DigDepthMath.ClampCap(40f) == 40,
                    "cap 2 m / 8 m / 20 m read back as 4 / 16 / 40 notches");
                Assert(RM_Volume.FormatFloorMetres(RM_DigDepthMath.ClampCap(4f)) == "2 m" && RM_Volume.FormatFloorMetres(RM_DigDepthMath.ClampCap(16f)) == "8 m"
                    && RM_Volume.FormatFloorMetres(RM_DigDepthMath.ClampCap(40f)) == "20 m", "and say 2 m / 8 m / 20 m");
                Assert(RM_DigDepthMath.ClampCap(1f) == 4 && RM_DigDepthMath.ClampCap(99f) == 40 && RM_DigDepthMath.ClampCap(15.6f) == 16
                    && RM_DigDepthMath.ClampCap(float.NaN) == 4, "held to 2..20 m and snapped to the half-metre");
                Assert(RM_DigDepthMath.DefaultMaxDigDepth == 4 && RM_DigDepthMath.DefaultMachineDigDepth == 40 && RM_DigDepthMath.PitDepth == RM_PitTrapMath.Superdeep
                    && RM_DigDepthMath.MaxDigCeiling == 40, "colonists 2 m, machines 20 m by default; the pit (2 m) is its own constant");
                // each cap stops the dig exactly there, at every setting
                foreach (int cap in new[] { 4, 16, 40 })
                {
                    var d = new byte[1];
                    var (cuts, _) = DigTo(d, new[] { 0 }, 99, cap);
                    Assert(d[0] == cap && cuts == cap && !RM_DigDepthMath.MayDeepen(cap, cap) && RM_DigDepthMath.MayDeepen(cap - 1, cap),
                        "cap " + cap + ": dug to " + d[0] + " in " + cuts + " cuts");
                }
                // lowering the cap never shallows: a 7 m square under a 2 m cap stays 7 m (repair clamps to the 20 m ceiling)
                var depth = new byte[] { 14, 40, 4 };
                var fill = new byte[] { 14, 3, 0 };
                var fluid = new byte[] { 1, 1, 0 };
                var rep = RM_ExcavationSanityMath.Repair(depth, fill, fluid, 1, RM_DigDepthMath.RepairCeiling);
                Assert(depth[0] == 14 && depth[1] == 40 && fill[0] == 14 && rep.Total == 0, "the load repair keeps 7 m and 20 m squares");
                Assert(!RM_DigDepthMath.MayDeepen(14, 4) && !RM_DigDepthMath.DigToOwesWork(14, 16, 4), "a lowered cap only stops further digging");
                // can-fail: the old clamp (the dig cap 4) WOULD have shallowed it
                var old = new byte[] { 14 }; var of = new byte[] { 14 }; var ok = new byte[] { 1 };
                RM_ExcavationSanityMath.Repair(old, of, ok, 1, 4);
                Assert(old[0] == 4, "sanity: a clamp at the cap would shallow (that is the bug the ceiling prevents)");
                // the wiring: setting, default, slider range, repair clamp, Deepen gate; MaxDepth is gone
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                RiverSwitchFlipChecks.Has(set, @"public static float maxDigDepth = 4f;", "the colonist cap setting, 2 m shipped");
                Assert(RM_DigDepthMath.DefaultMaxDigDepth == 4, "the literal is the default constant");
                RiverSwitchFlipChecks.Has(set, @"Scribe_Values\.Look\(ref maxDigDepth, ""maxDigDepth"", 4f\);", "saved");
                RiverSwitchFlipChecks.Has(set, @"maxDigDepth = list\.Slider\(maxDigDepth, RM_DigDepthMath\.MinMaxDigDepth, RM_DigDepthMath\.MaxDigCeiling\);", "slider 2..20 m");
                RiverSwitchFlipChecks.Has(set, @"list\.Label\(""Deepest colonist dig: "" \+ RM_Volume\.FormatFloorMetres\(MaxDigDepth\)", "settings text in metres");
                RiverSwitchFlipChecks.Has(set, @"\.Declare\(""digToDepthEnabled"", ""maxDigDepth"", ""digCostRisesWithDepth"", ""machineDigEnabled""\)", "greys with Dig deeper");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"RM_ExcavationSanityMath\.Repair\(depthGrid, fillGrid, fluidGrid, fluidPalette\.Count, RM_ExcavationDepth\.MaxDigCeiling\);", "repair clamps to the ceiling");
                RiverSwitchFlipChecks.Has(ex, @"if \(!RM_DigDepthMath\.MayDeepen\(d, cap\)\) \{ return d; \}", "Deepen stops at the digger's cap and writes nothing");
                RiverSwitchFlipChecks.Has(ex, @"Scribe_Collections\.Look\(ref digTargets, ""RM_digTargets"", LookMode\.Value, LookMode\.Value", "dig-to orders are saved");
                string src = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_Volume.cs"));
                foreach (string f in Directory.GetFiles(src, "*.cs", SearchOption.AllDirectories))
                {
                    if (f.Contains(Path.DirectorySeparatorChar + "SelfTest" + Path.DirectorySeparatorChar)) continue;
                    string t = File.ReadAllText(f);
                    Assert(!Regex.IsMatch(t, @"RM_ExcavationDepth\.MaxDepth\b|RM_PocketGrid\.MaxDepth\b|RM_PitDrawMath\.MaxDepth\b"),
                        "a reader of the deleted one-number cap survives in " + f);
                }
            });

            Case("DeepDig_no_dig_code_reads_terrain_for_depth", () =>
            {
                // terrain says only "2 m or deeper": every square past 2 m is RM_Channel_Superdeep
                foreach (string rel in new[] { "WorkGiver_DigCanal.cs", "Designator_DigCanal.cs", "JobDriver_DigCanal.cs" })
                {
                    string s = RiverSwitchFlipChecks.Src(rel);
                    var uses = Regex.Matches(s, @"DepthOfDryTerrain\(");
                    var grid = Regex.Matches(s, @"(\w+) != null \? (\(byte\))?\1\.ExcavatedDepthAt\(c\) : RM_ExcavationDepth\.DepthOfDryTerrain\(");
                    Assert(grid.Count >= 1 && uses.Count == grid.Count, rel + ": the depth is the grid's (terrain only when no engine): "
                        + uses.Count + " terrain reads, " + grid.Count + " grid-first");
                }
                string wg = RiverSwitchFlipChecks.Src("WorkGiver_DigCanal.cs");
                RiverSwitchFlipChecks.Has(wg, @"\|\| !RM_DigDepthMath\.MayDeepen\(depth, RM_DigLabor\.OrderCap\) \|\| \(target > 0 && depth >= target\)", "work-giver: order cap and target");
                string ds = RiverSwitchFlipChecks.Src("Designator_DigCanal.cs");
                RiverSwitchFlipChecks.Has(ds, @"public class Designator_DigCanalTo : Designator_DigCanal", "the dig-to-N designator exists");
                RiverSwitchFlipChecks.Has(ds, @"public override string Label => ""Dig to "" \+ RM_Volume\.FormatFloorMetres\(Target\);", "labelled in metres");
                Assert(!ds.Contains("SUPERDEEP") && !ds.Contains("shallow, mid, deep"), "the designator text names metres, not four depths");
                string jd = RiverSwitchFlipChecks.Src("JobDriver_DigCanal.cs");
                RiverSwitchFlipChecks.Has(jd, @"cutLanded = after > before;", "a landed cut is noted");
                RiverSwitchFlipChecks.Has(jd, @"if \(ex\.DigToOwesWork\(c\) && RimMandrakeFlowWorksSettings\.digToDepthEnabled\)", "and the order re-designates until its target");
                string patch = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_Volume.cs")), "..", "Patches", "FlowWorks_OrdersPatch.xml"));
                Assert(patch.Contains("<li>RimMandrake.FlowWorks.Designator_DigCanalTo</li>"), "the dig-to designator is on the Orders tab");
            });

            Case("DeepDig_colonists_2m_machines_deeper", () =>
            {
                // DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL (owner card 2026-10-21, "Colonists 2 m, machines deeper")
                int col = RM_DigDepthMath.DefaultMaxDigDepth, mach = RM_DigDepthMath.DefaultMachineDigDepth;
                Assert(RM_DigDepthMath.CapFor(false, col, true, mach) == 4 && RM_DigDepthMath.CapFor(true, col, true, mach) == 40,
                    "shipped: a colonist 2 m, a machine 20 m");
                Assert(!RM_DigDepthMath.MayDeepen(4, RM_DigDepthMath.CapFor(false, col, true, mach))
                    && RM_DigDepthMath.MayDeepen(4, RM_DigDepthMath.CapFor(true, col, true, mach)), "can-fail: at 2 m the colonist stops, the machine cuts on");
                Assert(RM_DigDepthMath.CapFor(true, col, false, mach) == 4, "machine digging off: machines stop where colonists stop");
                Assert(RM_DigDepthMath.CapFor(true, 16, true, 8) == 16 && RM_DigDepthMath.CapFor(false, 16, true, 40) == 16,
                    "a machine is never held shallower than a colonist; the machine cap never lifts a colonist");
                Assert(RM_DigDepthMath.DesignationCap(col, true, mach) == 40 && RM_DigDepthMath.DesignationCap(col, false, mach) == 4,
                    "an order is held to the deepest anyone may dig");
                // a 2 m square ordered to 4 m: still owes work (for a machine) — the order is not stale
                Assert(RM_DigDepthMath.DigToOwesWork(4, 8, RM_DigDepthMath.DesignationCap(col, true, mach))
                    && !RM_DigDepthMath.DigToOwesWork(4, 8, RM_DigDepthMath.DesignationCap(col, false, mach)), "today's designation cap: machines off stop new orders at 2 m");
                // night fixer 2026-10-22: a STANDING order never vanishes when machine digging is switched off; it waits
                Assert(RM_DigDepthMath.OrderCap(col, mach) == 40 && RM_DigDepthMath.DigToOwesWork(4, 8, RM_DigDepthMath.OrderCap(col, mach))
                    && RM_DigDepthMath.MayDeepen(4, RM_DigDepthMath.OrderCap(col, mach)), "the order cap ignores the machine switch: the 2 m order to 4 m still stands");
                Assert(RM_DigDepthMath.OrderCap(16, 8) == 16 && !RM_DigDepthMath.MayDeepen(40, RM_DigDepthMath.OrderCap(col, mach)),
                    "the order cap is never under the colonist cap and still stops at the ceiling");
                // colonist then machine on one square: 4 cuts, then 4 more
                var d = new byte[1];
                var (c1, _) = DigTo(d, new[] { 0 }, 8, RM_DigDepthMath.CapFor(false, col, true, mach));
                Assert(d[0] == 4 && c1 == 4, "the colonist stops at 2 m: " + d[0]);
                var (c2, _) = DigTo(d, new[] { 0 }, 8, RM_DigDepthMath.CapFor(true, col, true, mach));
                Assert(d[0] == 8 && c2 == 4, "the machine takes it to 4 m: " + d[0]);
                // the wiring: who is machine labour, the per-digger cut, the kept designation, the settings
                string lab = RiverSwitchFlipChecks.Src("RM_DigLabor.cs");
                RiverSwitchFlipChecks.Has(lab, @"public class RM_MachineDigger : DefModExtension", "the opt-in extension");
                RiverSwitchFlipChecks.Has(lab, @"if \(race\.IsMechanoid\) \{ return true; \}", "mechanoids are machine labour");
                RiverSwitchFlipChecks.Has(lab, @"pawn\.def\.HasModExtension<RM_MachineDigger>\(\) \|\| \(race\.FleshType != null && race\.FleshType\.HasModExtension<RM_MachineDigger>\(\)\)", "race or flesh type opts in");
                Assert(!Regex.IsMatch(lab, @"RSW_|Droidworks|Mech_Tunneler"), "FlowWorks names no franchise or vanilla def");
                string wg = RiverSwitchFlipChecks.Src("WorkGiver_DigCanal.cs");
                RiverSwitchFlipChecks.Has(wg, @"int myCap = RM_DigLabor\.CapFor\(pawn\); if \(!RM_DigDepthMath\.MayDeepen\(depth, myCap\) \|\| \(depth == RM_ExcavationDepth\.Surface && eng != null && eng\.FirstCutDepthAt\(c, myCap\) < 0\)\) \{ JobFailReason\.Is\(", "a capped digger refuses with a reason");
                int del = wg.IndexOf("des.Delete();"), mine = wg.IndexOf("int myCap");
                Assert(del > 0 && mine > del && wg.IndexOf("des.Delete();", mine) < 0, "the per-digger refusal keeps the designation (only the stale test deletes)");
                string jd = RiverSwitchFlipChecks.Src("JobDriver_DigCanal.cs");
                RiverSwitchFlipChecks.Has(jd, @"int after = excavation\.DeepenWithin\(c, RM_DigLabor\.CapFor\(pawn\)\);", "the cut is held to the digger's cap");
                RiverSwitchFlipChecks.Has(jd, @"cutRefusedButOwed = after == before && RM_DigDepthMath\.MayDeepen\(before, RM_DigLabor\.OrderCap\);", "a refused cut is noted");
                RiverSwitchFlipChecks.Has(jd, @"if \(cutRefusedButOwed && Map != null && job\.targetA\.IsValid\)", "and its order put back");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                Assert(!Regex.IsMatch(ex, @"public byte Deepen\(IntVec3 c, int"), "no Deepen overload: bridge tools reflect GetMethod(\"Deepen\")");
                RiverSwitchFlipChecks.Has(ex, @"public byte Deepen\(IntVec3 c\) \{ return DeepenWithin\(c, RM_DigLabor\.DesignationCap\); \}", "debug/bridge Deepen uses the designation cap");
                RiverSwitchFlipChecks.Has(ex, @"RM_DigDepthMath\.DigToOwesWork\(ExcavatedDepthAt\(c\), DigTargetAt\(c\), RM_DigLabor\.OrderCap\)", "orders owe work to the order cap (machines off: they wait)");
                string al = RiverSwitchFlipChecks.Src("RM_DeepDigAlert.cs");
                RiverSwitchFlipChecks.Has(al, @"if \(eng == null \|\| \(!machinesOff && HasMachineDigger\(m\)\)\)", "the waiting alert covers machine digging switched off");
                Assert(al.Contains("is switched off in the Flow Works settings"), "and says so");
                string lab2 = RiverSwitchFlipChecks.Src("RM_DigLabor.cs");
                Assert(lab2.Contains("is off in this mod's settings. The order waits."), "the right-click reason names the switch");
                string ds = RiverSwitchFlipChecks.Src("Designator_DigCanal.cs");
                Assert(Regex.Matches(ds, @"RM_DigLabor\.DesignationCap").Count >= 3, "the designator offers depths to the designation cap");
                Assert(!ds.Contains("8 m as shipped"), "no '8 m as shipped' text survives");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                RiverSwitchFlipChecks.Has(set, @"public static bool machineDigEnabled = true;", "machine digging shipped on");
                RiverSwitchFlipChecks.Has(set, @"public static float maxMachineDigDepth = 40f;", "machine cap 20 m shipped");
                RiverSwitchFlipChecks.Has(set, @"Scribe_Values\.Look\(ref machineDigEnabled, ""machineDigEnabled"", true\); Scribe_Values\.Look\(ref maxMachineDigDepth, ""maxMachineDigDepth"", 40f\);", "both saved");
                RiverSwitchFlipChecks.Has(set, @"\.Declare\(""machineDigEnabled"", ""maxMachineDigDepth""\)", "the machine cap greys with its switch");
                RiverSwitchFlipChecks.Has(set, @"""Deepest machine dig: "" \+ RM_Volume\.FormatFloorMetres\(MachineDigDepth\)", "the label shows the effective machine cap");
                Assert(!set.Contains("shipped 8 m"), "no 'shipped 8 m' settings text survives");
                string proj = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_Volume.cs")), "RimMandrake_FlowWorks.csproj"));
                Assert(proj.Contains(@"<Compile Include=""RM_DigLabor.cs"" />"), "RM_DigLabor.cs is compiled");
            });

            Case("DeepDig_cost_curve_numbers_measured", () =>
            {
                for (int n = 1; n <= RM_DigDepthMath.MaxDigCeiling; n++)
                    Assert(RM_DigDepthMath.WorkToCut(n) == 3200 * n, "notch " + n + " costs 3,200 x " + n);
                Assert(RM_DigDepthMath.WorkToDig(0, 4) == 32000 && RM_DigDepthMath.WorkToDig(0, 8) == 115200 && RM_DigDepthMath.WorkToDig(0, 14) == 336000
                    && RM_DigDepthMath.WorkToDig(0, 16) == 435200 && RM_DigDepthMath.WorkToDig(0, 40) == 2624000, "feasibility §3.2 table");
                // the 4/7/7/4 square: 2,726,400 work; digger-days at vanilla's 1.7 work a tick (MiningSpeed 100%)
                long sq = 12 * RM_DigDepthMath.WorkToDig(0, 8) + 4 * RM_DigDepthMath.WorkToDig(0, 14);
                Assert(sq == 2726400, "the square's work: " + sq);
                double days = RM_DigDepthMath.DiggerDays(sq);
                Assert(Math.Abs(days - 26.73) < 0.01, "the square is 26.73 digger-days (feasibility's 45 assumed 1 work a tick): " + days);
                Assert(Math.Abs(RM_DigDepthMath.DiggerDays(336000) - 3.29) < 0.01, "one 7 m square is 3.29 digger-days");
                // the other option (setting off): flat 12,800 a notch past 2 m
                Assert(RM_DigDepthMath.WorkToCut(5, false) == 12800 && RM_DigDepthMath.WorkToCut(40, false) == 12800 && RM_DigDepthMath.WorkToCut(3, false) == 9600,
                    "flat past 2 m, unchanged above it");
                long flat = 12 * RM_DigDepthMath.WorkToDig(0, 8, false) + 4 * RM_DigDepthMath.WorkToDig(0, 14, false);
                Assert(flat == 1638400 && Math.Abs(RM_DigDepthMath.DiggerDays(flat) - 16.06) < 0.01, "flat square 1,638,400 = 16.06 digger-days: " + flat);
                // the job prices by the grid through this curve; the fill-in stays half the cut being undone
                string dep = RiverSwitchFlipChecks.Src("RM_ExcavationDepth.cs");
                RiverSwitchFlipChecks.Has(dep, @"return RM_DigDepthMath\.WorkToCut\(fromDepth \+ 1, RimMandrakeFlowWorksSettings\.digCostRisesWithDepth\);", "WorkToDeepen is the curve");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                RiverSwitchFlipChecks.Has(set, @"public static bool digCostRisesWithDepth = true;", "the curve is shipped on");
                RiverSwitchFlipChecks.Has(set, @"list\.CheckboxLabeled\(""Each half-metre deeper costs more"", ref digCostRisesWithDepth,", "and is a setting");
            });

            Case("DeepDig_square_4774_digs_and_holds_152000_L_level", () =>
            {
                const int W = 8, H = 8;
                var (ring, core) = Square(W, 2, 2);
                var depth = new byte[W * H];
                // two drags of "Dig to": the ring to 4 m, the core to 7 m — 16 designations, 152 cuts, dug by machine labour
                // (the 20 m default; colonists stop at 2 m since DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL)
                var r1 = DigTo(depth, ring, 8, RM_DigDepthMath.DefaultMachineDigDepth);
                var r2 = DigTo(depth, core, 14, RM_DigDepthMath.DefaultMachineDigDepth);
                Assert(ring.Count + core.Count == 16 && r1.cuts + r2.cuts == 152, "16 orders, 152 cuts: " + (r1.cuts + r2.cuts));
                Assert(ring.All(c => depth[c] == 8) && core.All(c => depth[c] == 14), "4 4 4 4 / 4 7 7 4 / 4 7 7 4 / 4 4 4 4");
                // a 2 m cap could not: every square stops at 2 m
                var t0 = new byte[W * H];
                DigTo(t0, core, 14, 4);
                Assert(core.All(c => t0[c] == 4), "under a 2 m cap the core stops at 2 m");
                // stock capacity: 152 notches x 1,000 L
                long notches = ring.Sum(c => (long)depth[c]) + core.Sum(c => (long)depth[c]);
                Assert(notches == 152 && notches * RM_Volume.LitresPerLevel == 152000, "the square holds 152,000 L: " + notches * RM_Volume.LitresPerLevel);
                Assert(RM_Volume.Readout(14, 8, 14L * U) == "Hole 7 m (ledge 4 m) · Water 7.00 m (14,000 L)", "a brim-full core square reads " + RM_Volume.Readout(14, 8, 14L * U));
                // the exact kernel: brim-full is one body at one surface, every decilitre kept
                var w = World(W, H, true);
                Array.Copy(depth, w.k.depth, depth.Length);
                var all = ring.Concat(core).ToList();
                foreach (int c in all) { w.k.fill[c] = depth[c]; w.cellFluid[c] = ArrayWorld.Water; }
                long before = TotalDl(w);
                for (int p = 0; p < 30; p++) w.Pulse(all);
                Assert(before == 152L * U && TotalDl(w) == before && w.k.worstImbalance == 0, "152,000 L kept to the decilitre");
                double gap = LevelExactChecks.WorstGap(w, out int bodies);
                Assert(bodies == 1 && gap < 0.01, "brim-full: one body, gap " + gap + " m over " + bodies);
                // 56,000 L poured into the core settles over all 16 squares: the core fills to the 4 m ledge (24 notches), the
                // other 32 stand 1 m deep over the whole square (surface 3 m down): ring 1 m, core 4 m
                var v = World(W, H, true);
                Array.Copy(depth, v.k.depth, depth.Length);
                foreach (int c in core) { v.k.fill[c] = 14; v.cellFluid[c] = ArrayWorld.Water; }
                for (int p = 0; p < 400; p++) v.Pulse(all);
                Assert(TotalDl(v) == 56L * U, "56,000 L kept: " + TotalDl(v));
                Assert(ring.All(c => v.k.WaterOf(c) == 2L * U) && core.All(c => v.k.WaterOf(c) == 8L * U),
                    "ring 1 m, core 4 m: ring " + string.Join(",", ring.Select(c => v.k.WaterOf(c))) + " core " + string.Join(",", core.Select(c => v.k.WaterOf(c))));
                gap = LevelExactChecks.WorstGap(v, out bodies);
                Assert(bodies == 1 && gap < 0.01, "one body, one surface (the P3 diagnostic under 1 cm): " + gap + " over " + bodies);
                // below the ledge the core keeps its own surface (16,000 L: 1 m in each core square, the ring dry)
                var s = World(W, H, true);
                Array.Copy(depth, s.k.depth, depth.Length);
                foreach (int c in core) { s.k.fill[c] = 4; s.cellFluid[c] = ArrayWorld.Water; }
                for (int p = 0; p < 100; p++) s.Pulse(all);
                Assert(ring.All(c => s.k.WaterOf(c) == 0) && core.All(c => s.k.WaterOf(c) == 4L * U), "under the ledge the ring stays dry");
            });

            Case("DeepDig_legacy_notch_kernel_survives_past_2m", () =>
            {
                // exact level OFF (a setting): the notch kernel bucketed surfaces over -4..0 and indexed out of range past 2 m
                const int W = 8, H = 8;
                var (ring, core) = Square(W, 2, 2);
                var all = ring.Concat(core).ToList();
                foreach (bool bySurface in new[] { true, false })
                {
                    var w = World(W, H, false);
                    w.k.levelBySurfaceEnabled = bySurface;
                    foreach (int c in ring) w.k.depth[c] = 8;
                    foreach (int c in core) { w.k.depth[c] = 14; }
                    foreach (int c in ring.Take(6)) { w.k.fill[c] = 8; w.cellFluid[c] = ArrayWorld.Water; }
                    int sum0 = all.Sum(c => w.k.fill[c]);
                    for (int p = 0; p < 300; p++) w.Pulse(all);
                    int sum1 = all.Sum(c => w.k.fill[c]);
                    Assert(sum0 == 48 && sum1 == 48, "notch kernel (bySurface " + bySurface + ") conserves 48 notches: " + sum1);
                    Assert(core.Sum(c => w.k.fill[c]) >= 24, "water ran down into the 7 m core (bySurface " + bySurface + "): "
                        + string.Join(",", core.Select(c => w.k.fill[c])));
                }
            });

            Case("DeepDig_pits_past_2m_trap_by_band_ladders_and_ramps_by_delta", () =>
            {
                const int W = 8, H = 8;
                var (ring, core) = Square(W, 2, 2);
                var depth = new byte[W * H];
                foreach (int c in ring) depth[c] = 8;
                foreach (int c in core) depth[c] = 14;
                // bands sized by who climbs: K 1..6, every K has a grid
                Assert(RM_PitTrapMath.MaxClimbLimit == RM_PitTrapMath.ClimbBandEdges.Length + 1 + 2 && RM_PitTrapMath.ClimbBands == 7,
                    "largest climb limit = top size band + climber + leaper = 6");
                Assert(RM_PitTrapMath.ClimbLimit(50f, 5, 3f) == 6, "no creature climbs past the largest band");
                int coreCell = core[0], ringCell = ring[0];
                for (int k = 1; k < RM_PitTrapMath.ClimbBands; k++)
                {
                    var l = RM_PocketGridMath.Label(depth, W, H, k);
                    Assert(l.IsPocketCell(coreCell) && l.IsPocketCell(ringCell), "K " + k + ": nothing that walks leaves a 4 m sheer wall");
                    bool joined = l.SameComponent(coreCell, ringCell);
                    Assert(joined == (k >= 6), "K " + k + ": core and ledge joined only for a 3 m climber (step 6): " + joined);
                }
                // a huge K 4 (thrumbo) is now held by a 3 m sheer step (the old "K at the dig cap climbs all" was false)
                var three = new byte[W * H];
                for (int z = 2; z < 6; z++) for (int x = 2; x < 6; x++) three[z * W + x] = 6;
                Assert(RM_PocketGridMath.Label(three, W, H, 4).IsPocketCell(3 * W + 3) && !RM_PocketGridMath.Label(three, W, H, 6).IsPocketCell(3 * W + 3),
                    "a 3 m sheer pit holds K 4, frees K 6");
                // ladders join ANY shallower neighbour (a ring ladder to the surface, a core ladder to the ledge); ramps 1..3 notches
                Assert(RM_CliffMaskMath.LadderJoins(8, 0) && RM_CliffMaskMath.LadderJoins(14, 8) && !RM_CliffMaskMath.LadderJoins(14, 14),
                    "a ladder spans 4 m to the surface and 3 m to the ledge; none on a flat floor");
                Assert(RM_CliffMaskMath.RampJoins(11, 8, 3) && !RM_CliffMaskMath.RampJoins(14, 8, 3) && !RM_CliffMaskMath.RampJoins(8, 0, 3),
                    "a ramp spans at most 1.5 m: no ramp fits inside the square (feasibility §5)");
                Assert(RM_PitTrapMath.StepAllowed(14, 8, 2, false, true) && !RM_PitTrapMath.StepAllowed(14, 8, 2) && RM_PitTrapMath.StepAllowed(14, 13, 1)
                    && RM_PitTrapMath.StepAllowed(11, 8, 1, true), "steps by delta, a ladder or a ramp joins whatever the depth");
                // a ramp joins two squares of the pocket labelling for every band: a staircase 0 -> 3 -> 6 -> 8 frees a person
                var stairs = (byte[])depth.Clone();
                int s1 = 1 * W + 2, s2 = 1 * W + 3, s3 = 1 * W + 4;   // north of the ring
                stairs[s1] = 3; stairs[s2] = 6;
                Func<int, int, bool> ramps = (a, b) => (a == s1 && b == 0 * W + 2) || (a == 0 * W + 2 && b == s1) || (a == s2 && b == s1) || (a == s1 && b == s2)
                    || (a == 2 * W + 3 && b == s2) || (a == s2 && b == 2 * W + 3);
                Assert(RM_CliffMaskMath.RampJoins(3, 0, 3) && RM_CliffMaskMath.RampJoins(6, 3, 3) && RM_CliffMaskMath.RampJoins(8, 6, 3), "each flight is 1..1.5 m");
                var ls = RM_PocketGridMath.Label(stairs, W, H, 2, ramps);
                Assert(!ls.IsPocketCell(ringCell) && ls.IsPocketCell(coreCell), "ramps free the ledge to the surface; the core still needs a ladder");
                _ = s3;
                // the pit (collapse) rules with D > 4: still one pit; the descent is the crossing of 2 m; the OFF branch holds
                Assert(RM_PitTrapMath.IsPitDescent(0, 8) && !RM_PitTrapMath.IsPitDescent(8, 14) && !RM_PitTrapMath.StepBlocked(true, 8)
                    && RM_PitTrapMath.StepBlocked(true, 3), "a 7 m core under a 4 m ledge is one pit; a held pawn walks its floor at any depth");
                Assert(RM_PitTrapMath.DryStepBaseCost(8, 14, 70) == 0 && RM_PitTrapMath.DryStepBaseCost(14, 8, 70) == 70, "down is a fall, up is a climb");
                Assert(Math.Abs(RM_RelativeRulesMath.FallScaleNotches(14) - 3.5f) < 1e-6 && RM_RelativeRulesMath.FallScaleNotches(2) == 0.5f,
                    "a 7 m fall is 3.5 times the 2 m fall, never softened by the dig cap (P7 V3)");
                string trap = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_SuperdeepTrap.cs"));
                RiverSwitchFlipChecks.Has(trap, @"float scale = FallScaleFor\(d\);", "the fall scales by metres fallen, not the cap");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"if \(d >= RM_ExcavationDepth\.Superdeep && before < RM_ExcavationDepth\.Superdeep\) \{ superdeepCellCount\+\+;", "a pit is counted once, at the 2 m crossing");
                RiverSwitchFlipChecks.Has(ex, @"if \(d >= RM_ExcavationDepth\.Superdeep && newD < RM_ExcavationDepth\.Superdeep\) \{ superdeepCellCount--;", "and uncounted only when filled back above 2 m");
                string pg = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PocketGrid.cs"));
                RiverSwitchFlipChecks.Has(pg, @"public static int BandCount => RM_PitTrapMath\.ClimbBands;", "the pocket grid is sized by who climbs");
                string cm = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_CliffMask.cs"));
                RiverSwitchFlipChecks.Has(cm, @"band = new NativeArray<CellConnection>\[RM_PitTrapMath\.ClimbBands\]", "and so are the cliff masks");
                // SINK_CAP_WIDEN_PAWNS_SINK_TO_FOUR: the pawn keeps sinking to 4 m (D 8, the owner's pawn_height_ladder_legible
                // card) and saturates there; wall faces still saturate at 2 m (his look first, P9); never index out
                Assert(RM_PitDrawMath.SinkFor(8, 0.3f) > RM_PitDrawMath.SinkFor(4, 0.3f) && RM_PitDrawMath.SinkFor(6, 0.3f) > RM_PitDrawMath.SinkFor(4, 0.3f),
                    "a pawn on 3 m and 4 m floors sinks deeper than on a 2 m floor");
                Assert(RM_PitDrawMath.SinkFor(14, 0.3f) == RM_PitDrawMath.SinkFor(8, 0.3f) && RM_WallFaceMath.NorthFaceHeight(14) == RM_WallFaceMath.NorthMax,
                    "a 7 m drop draws as a 4 m drop (the sink cap); wall faces saturate");
            });
        }
    }
}
