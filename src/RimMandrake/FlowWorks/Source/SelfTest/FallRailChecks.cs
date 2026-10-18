// FALL_GUARDRAILS_BUILD_REAL_OBJECT (owner 2026-10-18: "build guardrails as a real object with real need (and support existing
// fences acting this way too)"). Arithmetic is the PRODUCTION Verse-free kernel (RM_FallRailMath over RM_RelativeRulesMath and
// RM_PitTrapMath); the Verse-bound doors, the def and the setting are read from production source.
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class FallRailChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A w×h depth grid (notches); out of bounds answers -1.</summary>
        private sealed class Grid
        {
            public readonly int w, h;
            public readonly int[] d;
            public Grid(int w, int h) { this.w = w; this.h = h; d = new int[w * h]; }
            public void Fill(int x0, int z0, int x1, int z1, int depth)
            {
                for (int z = z0; z <= z1; z++)
                    for (int x = x0; x <= x1; x++)
                        d[z * w + x] = depth;
            }
            public int At(int x, int z) => x < 0 || z < 0 || x >= w || z >= h ? -1 : d[z * w + x];
        }

        public static void Run(Action<string, Action> Case)
        {
            const int Person = 2;   // RM_PocketGrid.PersonBand

            Case("FallRail_threshold_is_the_doors_own_fall", () =>
            {
                for (int k = 0; k <= 8; k++)
                    for (int f = 0; f <= 16; f++)
                        for (int t = 0; t <= 16; t++)
                            Assert(RM_RelativeRulesMath.StepIsAFall(f, t, RM_FallRailMath.FallNotchesFor(k)) == RM_PitTrapMath.ArrivalDropsTooFar(f, t, k),
                                "StepIsAFall(K+1) == ArrivalDropsTooFar(K) at k=" + k + " " + f + "->" + t);
                Assert(RM_FallRailMath.FallNotchesFor(Person) == 3, "a person falls past 1 m: 1.5 m is the first sheer drop");
            });
            Case("FallRail_edge_set_down_a_sheer_drop_only", () =>
            {
                int fall = RM_FallRailMath.FallNotchesFor(Person);
                Assert(RM_FallRailMath.GuardsEdge(true, 0, 14, fall), "a railed surface lip over a 7 m drop is guarded");
                Assert(RM_FallRailMath.GuardsEdge(true, 8, 14, fall), "a railed 4 m ledge over a 7 m core is guarded (3 m drop)");
                Assert(!RM_FallRailMath.GuardsEdge(false, 0, 14, fall), "an unrailed lip still falls");
                Assert(!RM_FallRailMath.GuardsEdge(true, 0, 2, fall), "a 1 m step a person climbs is not a fall: never refused");
                Assert(!RM_FallRailMath.GuardsEdge(true, 14, 0, fall), "climbing UP past a rail is never refused");
                Assert(!RM_FallRailMath.GuardsEdge(true, 4, 4, fall), "walking along the lip is never refused");
                Assert(RM_FallRailMath.GuardsEdge(true, 0, 2, RM_FallRailMath.FallNotchesFor(1)), "a rat (K = 1) falls 1 m: guarded for it");
            });
            Case("FallRail_jump_in_is_deliberate", () =>
            {
                Assert(RM_FallRailMath.FallBlocked(true, false), "a shove over a guarded edge is stopped");
                Assert(!RM_FallRailMath.FallBlocked(true, true), "the jump-in order still works");
                Assert(!RM_FallRailMath.FallBlocked(false, false), "no guarded edge: the fall stands");
            });
            Case("FallRail_vanilla_fences_count", () =>
            {
                Assert(RM_FallRailMath.IsRailThing(true, true, true, false), "our guardrail is a rail");
                Assert(RM_FallRailMath.IsRailThing(true, true, false, true), "a vanilla (isFence) fence is a rail");
                Assert(!RM_FallRailMath.IsRailThing(true, true, false, false), "a wall or chair is not");
                Assert(!RM_FallRailMath.IsRailThing(true, false, true, true), "a frame is not built yet");
                Assert(!RM_FallRailMath.IsRailThing(false, true, true, true), "setting off: nothing is a rail (old behaviour)");
            });
            Case("FallRail_placement_beside_a_sheer_drop", () =>
            {
                var g = new Grid(12, 6);
                g.Fill(3, 1, 4, 4, 14);            // a 7 m pit
                g.Fill(8, 1, 8, 1, 2);             // a 1 m dip
                int fall = RM_FallRailMath.FallNotchesFor(Person);
                Assert(RM_FallRailMath.HasDropBeside(g.At, 2, 2, fall), "the lip beside the pit takes a rail");
                Assert(RM_FallRailMath.HasDropBeside(g.At, 5, 0, fall), "a corner (diagonal) neighbour counts: the 8-way edge set");
                Assert(!RM_FallRailMath.HasDropBeside(g.At, 0, 0, fall), "open ground far from it does not");
                Assert(!RM_FallRailMath.HasDropBeside(g.At, 3, 2, fall), "the pit floor does not (no lower neighbour)");
                Assert(!RM_FallRailMath.HasDropBeside(g.At, 7, 1, fall), "beside a 1 m dip a person climbs: no rail");
                Assert(!RM_FallRailMath.HasDropBeside(g.At, -1, 0, fall), "out of bounds: refused");
            });
            Case("FallRail_line_is_8_adjacent_and_inclusive", () =>
            {
                foreach (var (x0, z0, x1, z1) in new[] { (0, 0, 3, 0), (0, 0, 3, 3), (5, 5, 2, 4), (1, 1, 1, 1), (0, 0, -2, 3) })
                {
                    var l = RM_FallRailMath.Line(x0, z0, x1, z1);
                    Assert(l[0] == (x0, z0) && l[l.Count - 1] == (x1, z1), "ends included " + x0 + "," + z0 + "->" + x1 + "," + z1);
                    Assert(l.Count == Math.Max(Math.Abs(x1 - x0), Math.Abs(z1 - z0)) + 1, "one cell per step");
                    for (int i = 0; i + 1 < l.Count; i++)
                        Assert(Math.Abs(l[i + 1].x - l[i].x) <= 1 && Math.Abs(l[i + 1].z - l[i].z) <= 1, "8-adjacent steps");
                }
            });
            Case("FallRail_throw_stops_at_the_rail", () =>
            {
                // a throw east from x=0 over a rail at x=1 (lip) into a 7 m pit at x=2..3
                var g = new Grid(6, 1);
                g.Fill(2, 0, 3, 0, 14);
                bool[] rail = { false, true, false, false, false, false };
                int fall = RM_FallRailMath.FallNotchesFor(Person);
                Func<int, bool> guarded = i => RM_FallRailMath.GuardsEdge(rail[i], g.At(i, 0), g.At(i + 1, 0), fall);
                Assert(RM_FallRailMath.ThrowStopIndex(4, guarded, i => true) == 1, "stops on the rail's cell");
                Assert(RM_FallRailMath.ThrowStopIndex(4, guarded, i => i != 1) == 0, "a rail cell nobody stands on (a fence): one cell back");
                rail[1] = false;
                Assert(RM_FallRailMath.ThrowStopIndex(4, guarded, i => true) == -1, "unrailed: the throw lands in the pit");
                rail[0] = true;
                Assert(RM_FallRailMath.ThrowStopIndex(4, guarded, i => true) == -1, "a rail away from the lip guards nothing");
            });
            Case("FallRail_doors_def_and_setting_wired", () =>
            {
                string rails = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_FallRails.cs"));
                Assert(rails.Contains("d.building.isFence") && rails.Contains("RimMandrakeFlowWorks_DefOf.RM_PitGuardrail"), "IsRail = our rail OR isFence");
                Assert(rails.Contains("RM_FallRailMath.GuardsEdge(true, fromD, toD, RM_FallRailMath.FallNotchesFor(RM_PocketGrid.ClimbLimitOf(p)))"), "the edge rule at the pawn's own climb");
                Assert(rails.Contains("eng.SuperdeepTrap.IsJumper(p)"), "a jumper is never stopped");
                string trap = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_SuperdeepTrap.cs"));
                Assert(trap.Contains("RM_FallRails.RefusesWalkedStep(pawn, eng, __instance.nextCell)"), "the per-move floor refuses the walked step");
                Assert(trap.Split(new[] { "RM_FallRails.StopsArrival(map, eng, p, prev, pos)" }, StringSplitOptions.None).Length == 3, "both detector doors (Tick, ResolveArrivalNow)");
                string path = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitPathing.cs"));
                Assert(path.Contains("stunDurationTicksRange != IntRange.Zero") && path.Contains("RM_FallRails.ThrowStop(p.Map, eng, p, from, p.Position)"), "a throw stops; a jump does not");
                string cover = RiverSwitchFlipChecks.Src(Path.Combine("Pits", "Building_PitCover.cs"));
                Assert(!cover.Contains("RM_FallRails"), "a cover giving way is unaffected");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                Assert(set.Contains("public static bool pitGuardrailEnabled = true;") && set.Contains("Scribe_Values.Look(ref pitGuardrailEnabled, \"pitGuardrailEnabled\", true);")
                    && set.Contains("ref pitGuardrailEnabled,"), "setting declared, saved, shown");
                // The repo's Defs (run from the repo root): the build staging copies Source only, so its Defs can be stale.
                string rel = Path.Combine("Defs", "Canals", "ThingDefs", "FlowWorks_ThingDefs.xml");
                string repoDefs = Path.Combine(Directory.GetCurrentDirectory(), "src", "RimMandrake", "FlowWorks", rel);
                string defs = File.ReadAllText(File.Exists(repoDefs) ? repoDefs
                    : Path.Combine(Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RimMandrakeFlowWorksMod.cs"))), rel));
                Assert(defs.Contains("<defName>RM_PitGuardrail</defName>") && defs.Contains("RimMandrake.FlowWorks.PlaceWorker_PitGuardrail")
                    && defs.Contains("<li>Metallic</li>") && !defs.Contains("<isFence>true</isFence>"), "the guardrail def: stuff-made, placeworker, not a pen fence");
            });
        }
    }
}
