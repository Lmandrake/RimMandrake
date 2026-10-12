// Owner rulings #18 and #19 (2026-10-11, cards) and the bottle-loop fix from the code review. Offline checks on the
// production verdicts (RM_PitTrapMath.FlowDoorStandsOn, RM_WakeMath, RM_TankBottleRules, RM_LiquidNetKernel.SettlePlan),
// the shipped XML and the production source (not copies). Each case has a can-fail.
// NOT proven here: placing a door on a wet cell in game, a frame surviving a live flood, a pawn's wake on screen, a
// colonist's job choice. Those are the live checks owed after deploy.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class RulingsWetDoorWakeBottleChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string Between(string src, string start, string end)
        {
            int a = src.IndexOf(start, StringComparison.Ordinal);
            Assert(a >= 0, "can-fail: '" + start + "' not found");
            int b = src.IndexOf(end, a + start.Length, StringComparison.Ordinal);
            Assert(b >= 0, "can-fail: '" + end + "' not found after '" + start + "'");
            return src.Substring(a, b - a);
        }

        private static readonly RM_TankMode[] Modes = { RM_TankMode.Store, RM_TankMode.Fill, RM_TankMode.Empty, RM_TankMode.Dump };

        public static void Run(Action<string, Action> Case)
        {
            Case("Ruling18_flow_door_stands_on_a_wet_dug_cell_only", () =>
            {
                Assert(RM_PitTrapMath.FlowDoorStandsOn(false, true, 2, 1), "a flow door on a dug cell holding liquid stands");
                Assert(RM_PitTrapMath.FlowDoorStandsOn(false, true, 4, 4), "also a brim-full superdeep cut");
                Assert(!RM_PitTrapMath.FlowDoorStandsOn(false, true, 0, 0), "can-fail: a natural lake (never dug) stays refused");
                Assert(!RM_PitTrapMath.FlowDoorStandsOn(false, true, 0, 3), "can-fail: undug cell refused even if fill were reported");
                Assert(!RM_PitTrapMath.FlowDoorStandsOn(false, false, 2, 1), "can-fail: any other building keeps vanilla's refusal");
                Assert(RM_PitTrapMath.FlowDoorStandsOn(true, false, 0, 0), "vanilla's yes is never turned into a no");
            });

            Case("Ruling18_patch_reads_the_dug_grid_and_the_frame_seals_nothing", () =>
            {
                string doors = Src("Superdeep", "RM_FlowDoors.cs");
                string patch = Between(doors, "[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanBuildOnTerrain))]", "public static class RM_FlowDoorRules");
                Assert(patch.Contains("if (__result ||"), "early-out on every call vanilla already allows");
                Assert(patch.Contains("IsFlowDoorDef(td)"), "only the flow-door defs are let through");
                Assert(patch.Contains("eng.ExcavatedDepthAt(cell)") && !patch.Contains("eng.DepthAt("),
                    "can-fail: the DUG depth, never DepthAt (which reads a natural lake as superdeep)");
                Assert(patch.Contains("RM_PitTrapMath.FlowDoorStandsOn("), "the selftested verdict decides");
                string through = Between(doors, "public static bool LetsLiquidThrough(", "public static bool CanOpen(");
                Assert(through.Contains("edifice is Frame") && through.Contains("IsFlowDoorDef(frame.def.entityDefToBuild"),
                    "a flow door's frame lets liquid through");
                string seals = Between(doors, "public static bool SealsLiquid(", "public static bool CanOpen(");
                Assert(seals.Contains("as Building_RM_FlowDoor"), "the kernel's seal reads only a finished door (a frame never seals)");
                string flood = Src("Flood_FlowWorks.cs");
                Assert(flood.Contains("!RM_FlowDoorRules.LetsLiquidThrough(edifice)"), "the legacy flood walk uses the same verdict");
                XDocument d = XDocument.Load(Path.Combine(ContainerMatFixture.Root(), "..", "Canals", "ThingDefs", "FlowWorks_Doors.xml"));
                foreach (string dn in new[] { "RM_Sluice", "RM_SecurityGrateDoor" })
                {
                    XElement t = d.Descendants("ThingDef").FirstOrDefault(e => (string)e.Element("defName") == dn);
                    Assert(t != null, dn + " shipped");
                    Assert((string)t.Element("thingClass") == "RimMandrake.FlowWorks.Building_RM_FlowDoor", dn + ": the patch keys on this thingClass");
                    Assert((string)t.Element("terrainAffordanceNeeded") == "Light", dn + ": dry placement unchanged (Light)");
                }
            });

            Case("Ruling19_every_liquid_has_a_wake_water_clear_tar_barely", () =>
            {
                Assert(Math.Abs(RM_WakeMath.Speed(1f) - 0.55f) < 1e-6, "water's V: 0.55 cells/s");
                Assert(RM_WakeMath.Speed(0.1f) < RM_WakeMath.Speed(0.4f) && RM_WakeMath.Speed(0.4f) < RM_WakeMath.Speed(1f), "speed rises with wake");
                Assert(RM_WakeMath.Size(1f, 0.1f) < RM_WakeMath.Size(1f, 1f), "a thick liquid's stir is smaller");
                Assert(RM_WakeMath.Speed(float.NaN) == 0f && RM_WakeMath.Speed(5f) == RM_WakeMath.Speed(1f), "clamped 0..1");
                Assert(Math.Abs(RM_WakeMath.Size(9f, 1f) - 0.7f) < 1e-6, "body size clamped at 2");
                string draw = Src("RM_LiquidSurface.cs");
                Assert(draw.Contains("RM_WakeMath.Size(p.BodySize, look.wake)") && draw.Contains("RM_WakeMath.Speed(look.wake)"), "the draw uses the verdicts");
                var wakes = new Dictionary<string, float>();
                foreach (string f in new[] { Path.Combine(ContainerMatFixture.Root(), "LiquidDefs", "RM_LiquidDefRegistry.xml"),
                                             Path.Combine(ContainerMatFixture.Root(), "..", "..", "Patches", "LiquidTypes", "RM_FluidSurfaceLooks.xml") })
                {
                    XDocument x = XDocument.Load(f);
                    foreach (XElement look in x.Descendants("surfaceLook"))
                    {
                        string owner = (string)look.Parent?.Element("defName") ?? "patch";
                        string w = (string)look.Element("wake");
                        Assert(w != null, "can-fail: a surfaceLook with no wake: " + owner);
                        wakes[owner + "#" + wakes.Count] = float.Parse(w, System.Globalization.CultureInfo.InvariantCulture);
                    }
                }
                Assert(wakes.Count >= 20, "sanity: found the shipped looks (" + wakes.Count + ")");
                Assert(wakes.Values.All(v => v > 0f && v <= 1f), "can-fail: every shipped wake in (0, 1]: " + string.Join(",", wakes.Where(kv => !(kv.Value > 0f && kv.Value <= 1f)).Select(kv => kv.Key)));
                Func<string, float> Row = dn => wakes.First(kv => kv.Key.StartsWith(dn + "#", StringComparison.Ordinal)).Value;
                Assert(Row("RM_Liquid_FreshWater") >= 0.9f, "water ripples clearly");
                Assert(Row("RM_Liquid_Tar") <= 0.15f, "tar barely moves");
                Assert(Row("RM_Liquid_Tar") < Row("RM_Liquid_SlimeRed") && Row("RM_Liquid_SlimeRed") < Row("RM_Liquid_FreshWater"), "slime in between");
            });

            Case("BottleLoop_no_tank_takes_bottles_unasked_and_gives_them_back", () =>
            {
                foreach (RM_TankMode m in Modes)
                {
                    Assert(!(RM_TankBottleRules.PoursInto(m, false) && RM_TankBottleRules.FillsFrom(m)), "can-fail: " + m + " both takes bottles unasked and refills them");
                }
                Assert(RM_TankBottleRules.FillsFrom(RM_TankMode.Store), "a player can fill bottles from an ordinary Store tank");
                Assert(RM_TankBottleRules.PoursInto(RM_TankMode.Store, true), "a player's order pours into a Store tank");
                Assert(!RM_TankBottleRules.PoursInto(RM_TankMode.Store, false), "unasked, never into a Store tank");
                Assert(RM_TankBottleRules.PoursInto(RM_TankMode.Fill, false), "a Fill tank takes bottles unasked");
                Assert(!RM_TankBottleRules.PoursInto(RM_TankMode.Empty, true) && !RM_TankBottleRules.PoursInto(RM_TankMode.Dump, true),
                    "Empty and Dump never take bottles (the task's accept set is Store/Fill)");
                Assert(RM_TankBottleRules.FillsFrom(RM_TankMode.Empty) && RM_TankBottleRules.FillsFrom(RM_TankMode.Dump) && !RM_TankBottleRules.FillsFrom(RM_TankMode.Fill),
                    "fills from Store/Empty/Dump, never Fill");

                // The loop across tanks: liquid edges are unasked bottle trips (a -> bottle -> b) plus the production settle's
                // tank-to-tank moves, derived by running SettlePlan on every ordered pair of modes. No cycle may exist.
                HashSet<(RM_TankMode, RM_TankMode)> Edges(Func<RM_TankMode, bool> pours, Func<RM_TankMode, bool> fills)
                {
                    var e = new HashSet<(RM_TankMode, RM_TankMode)>();
                    foreach (RM_TankMode a in Modes)
                    {
                        foreach (RM_TankMode b in Modes)
                        {
                            if (fills(a) && pours(b)) e.Add((a, b));
                            var pair = new List<RM_SettleTank> { new RM_SettleTank(1, 100, 300, "w", a), new RM_SettleTank(2, 0, 300, null, b) };
                            if (RM_LiquidNetKernel.SettlePlan(pair, RM_LiquidNetKernel.TankUnitsPerCycle, 0).Any(p => p.src == 0 && p.dst == 1)) e.Add((a, b));
                        }
                    }
                    return e;
                }
                bool Loops(HashSet<(RM_TankMode, RM_TankMode)> e, RM_TankMode m)
                {
                    var seen = new HashSet<RM_TankMode>();
                    var todo = new Stack<RM_TankMode>(new[] { m });
                    while (todo.Count > 0)
                    {
                        RM_TankMode from = todo.Pop();
                        foreach (var x in e.Where(x => x.Item1 == from))
                        {
                            if (x.Item2 == m) return true;
                            if (seen.Add(x.Item2)) todo.Push(x.Item2);
                        }
                    }
                    return false;
                }
                var edges = Edges(m => RM_TankBottleRules.PoursInto(m, false), RM_TankBottleRules.FillsFrom);
                Assert(edges.Contains((RM_TankMode.Store, RM_TankMode.Fill)), "sanity: the settle's Store -> Fill move is seen");
                foreach (RM_TankMode m in Modes)
                {
                    Assert(!Loops(edges, m), "can-fail: liquid leaving a " + m + " tank comes back to one (a loop)");
                }
                // can-fail witness: the OLD rule (every tank that could hold it took bottles unasked; every non-empty tank refilled
                // them) loops a single Store tank, and this same test sees it.
                Assert(Loops(Edges(m => true, m => true), RM_TankMode.Store), "witness: the old rule's Store-tank loop is detected");
            });

            Case("BottleLoop_search_and_jobs_read_the_tank_job", () =>
            {
                string u = Src("LiquidTypes", "RM_LiquidTankUtility.cs");
                Assert(Between(u, "public static bool TryFindTankToFill(", "public static bool TryFindTankToDrain(").Contains("candidate.TakesBottles(playerOrdered) && candidate.CanAccept("),
                    "the pour search asks the tank's job first");
                Assert(Between(u, "public static bool TryFindTankToDrain(", "private delegate bool TankPredicate").Contains("!candidate.GivesToBottles"),
                    "the fill search skips tanks that do not give to bottles");
                string wg = Src("LiquidTypes", "WorkGiver_EmptyBottleIntoTank.cs");
                Assert(wg.Split(new[] { "TryFindTankToFill(pawn, ext.liquid, units, forced, out tank)" }, StringSplitOptions.None).Length == 3,
                    "both work-giver calls pass forced (a player's order) through");
                Assert(Src("LiquidTypes", "JobDriver_EmptyBottleIntoTank.cs").Contains("!Tank.TakesBottles(job.playerForced)"), "the pour job ends if the tank's job changes");
                Assert(Src("LiquidTypes", "JobDriver_FillBottleFromTank.cs").Contains("!Tank.GivesToBottles"), "the fill job ends if the tank's job changes");
                string tank = Src("LiquidTypes", "Building_LiquidTank.cs");
                Assert(tank.Contains("RM_TankBottleRules.PoursInto(EffectiveMode, playerOrdered)") && tank.Contains("RM_TankBottleRules.FillsFrom(EffectiveMode)"),
                    "the tank reads its EFFECTIVE job (Store when tank jobs are off or the tank is not ours)");
            });
        }
    }
}
