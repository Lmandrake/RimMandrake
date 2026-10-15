// FlowWorks pre-release GPT consult fixes, builder A (liquid network, tanks, hoses, bottles), 2026-10-15.
// Triage: Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md. Each case runs the PRODUCTION rule and would have gone red
// on the code the finding was made against.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GptFixesAChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            // final review row 33: apparel corroded to 0 HP is destroyed (vanilla wear-out), never orphaned by a bare Remove.
            Case("GptA_corrosion_destroys_worn_out_apparel", () =>
            {
                string src = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "LiquidCorrosion.cs"));
                Assert(!src.Contains("pawn.apparel.Remove(piece)"), "a corroded-away piece is not merely removed (orphaned Thing)");
                RiverSwitchFlipChecks.Has(src, @"if \(piece\.HitPoints <= 0\)\s*\{[^}]*piece\.Destroy\(\);", "a piece at 0 HP is destroyed");
                RiverSwitchFlipChecks.Has(src, @"if \(!piece\.def\.useHitPoints\)", "an item without hit points is never worn away");
                Assert(!src.Contains("has never ticked inside a running game") && !RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "LiquidIgnition.cs")).Contains("this has never shipped"),
                    "corrosion/ignition comments no longer say they never shipped");
            });

            // LIQUID_ROTATION_FIX_STARVED_STRANGER C1-F4: B sits on another store with less than one batch; A must keep drawing.
            Case("GptA_rotation_starved_stranger_on_another_store_never_stalls", () =>
            {
                var rot = new RM_ConsumerRotation();
                int aDrew = 0;
                for (int c = 0; c < 20; c++)
                {
                    int now = c * 250;
                    object ka = RM_ConsumerRotation.Key("water", 100), kb = RM_ConsumerRotation.Key("water", 200);
                    if (rot.MayDraw(ka, 1, now)) { aDrew++; rot.Served(ka, 1, now); } else rot.Starved(ka, 1, now);
                    rot.Starved(kb, 2, now + 50);   // B: its own store never holds a batch
                }
                Assert(aDrew == 20, "A on store 100 draws every cycle while B starves on store 200 (" + aDrew + "/20)");
                Assert(!Equals(RM_ConsumerRotation.Key("water", 1), RM_ConsumerRotation.Key("water", 2)) && Equals(RM_ConsumerRotation.Key("water", 1), RM_ConsumerRotation.Key("water", 1)),
                    "keys differ per store, equal within one");
            });

            // C1-F4 on ONE store: B's batch is more than the store ever holds; A yields once, B still goes without, A resumes.
            Case("GptA_rotation_unservable_neighbour_forfeits_after_one_yield", () =>
            {
                foreach (bool bFirst in new[] { false, true })
                {
                    var rot = new RM_ConsumerRotation();
                    object k = RM_ConsumerRotation.Key("water", 7);
                    int pool = 0, aDrew = 0;
                    for (int c = 0; c < 30; c++)
                    {
                        pool += 3;   // A needs 3 a batch, B needs 50: B can never run
                        for (int step = 0; step < 2; step++)
                        {
                            bool isA = (step == 0) != bFirst;
                            int now = c * 250 + step * 100;
                            if (isA)
                            {
                                if (pool >= 3 && rot.MayDraw(k, 1, now)) { pool -= 3; aDrew++; rot.Served(k, 1, now); }
                                else rot.Starved(k, 1, now);
                            }
                            else if (pool >= 50 && rot.MayDraw(k, 2, now)) { pool -= 50; rot.Served(k, 2, now); }
                            else rot.Starved(k, 2, now);
                        }
                    }
                    Assert(aDrew >= 18, "B " + (bFirst ? "ticking first" : "ticking second") + " with an unservable batch must not stall A: A drew " + aDrew + "/30");
                }
            });

            // C1-F16: a machine with two runnable inputs takes them in turn.
            Case("GptA_converter_multi_input_rotates", () =>
            {
                var b = new List<int> { 2, 3 };
                Assert(RM_ConversionMath.NextRunnable(b, -1) == 0, "nothing ran yet: the first runnable");
                Assert(RM_ConversionMath.NextRunnable(b, 0) == 1, "input 0 ran last: input 1 runs");
                Assert(RM_ConversionMath.NextRunnable(b, 1) == 0, "input 1 ran last: wraps to input 0");
                Assert(RM_ConversionMath.NextRunnable(new List<int> { 0, 3 }, 1) == 1, "the only runnable input runs every cycle");
                Assert(RM_ConversionMath.NextRunnable(new List<int> { 0, 0 }, 0) == -1 && RM_ConversionMath.NextRunnable(new List<int>(), -1) == -1, "nothing runnable: -1");
                string conv = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "CompLiquidConverter.cs"));
                RiverSwitchFlipChecks.Has(conv, @"int pick = RM_ConversionMath\.NextRunnable\(batches, cand\.FindIndex\(c => c\.input == lastInput\)\);", "converter picks after the last input");
                RiverSwitchFlipChecks.Has(conv, @"lastInput = inputLiquid;", "converter records the input that ran");
                RiverSwitchFlipChecks.Has(conv, @"Scribe_Defs\.Look\(ref lastInput, ""RM_convLastInput""\);", "the last input is saved");
            });

            // BOTTLE_STOCK_MEND_FREE_REFILLS C2-F2/C2-F3: fill and wash from terrain pay the pond body; C2-F9: no free repair.
            Case("GptA_bottle_fill_and_wash_pay_the_body_and_keep_wear", () =>
            {
                Assert(Math.Abs(RM_ContainerMaterialMath.BodyStockFor(5, 1f, 5) - 1f) < 1e-6f, "a level's worth of units costs one level of stock");
                Assert(Math.Abs(RM_ContainerMaterialMath.BodyStockFor(1, 2f, 5) - 0.4f) < 1e-6f, "a viscous liquid (2 per tile) costs its share");
                Assert(RM_ContainerMaterialMath.BodyStockFor(0, 1f, 5) == 0f && RM_ContainerMaterialMath.BodyStockFor(3, 0f, 5) == 0f, "nothing for nothing");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(30, 60, 60) == 30, "a half-worn bottle stays half-worn");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(30, 60, 100) == 50, "the worn fraction carries to a bigger max");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(1, 100, 10) == 1, "never rounds a live container to 0");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(5, 0, 40) == 40, "a source with no hit points gives full");
                Assert(RM_ContainerMaterialMath.CarriedHitPoints(80, 60, 60) == 60, "never above the max");
                string util = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "RM_LiquidBottleUtility.cs"));
                RiverSwitchFlipChecks.Has(util, @"made\.HitPoints = RM_ContainerMaterialMath\.CarriedHitPoints\(from\.HitPoints, from\.MaxHitPoints, made\.MaxHitPoints\);", "MakeContainer carries the wear");
                RiverSwitchFlipChecks.Has(util, @"return ex\.Stock\.TryDebit\(map, c, stock, ex\);", "terrain debit spends the body");
                RiverSwitchFlipChecks.Has(util, @"if \(ex\?\.Stock != null && !ex\.Stock\.CanSupply\(map, c, ex\)\)", "the search skips a spent body");
                string fill = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "JobDriver_FillBottle.cs"));
                RiverSwitchFlipChecks.Has(fill, @"if \(!RM_LiquidBottleUtility\.TryDebitTerrain\(Map, job\.targetB\.Cell, RM_ContainerMaterials\.UnitsIn\(carried, liquid, size\)\)\) \{ return; \} Thing filled", "fill debits before it makes the bottle");
                string wash = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "JobDriver_WashBottle.cs"));
                RiverSwitchFlipChecks.Has(wash, @"if \(!RM_LiquidBottleUtility\.TryDebitTerrain\(Map, job\.targetB\.Cell, liquid\.UnitsFor\(size\)\)\) \{ return; \} Thing empty", "wash debits before it cleans");
            });

            // TANK_SETTLE_FIX_DOUBLE_DIPPED C1-F5: a Store tank in two components is settled once per cycle, not once per component.
            Case("GptA_settle_tank_in_two_components_shares_one_budget", () =>
            {
                // component 1: Empty tank E (id 1, 50 water) and Store S (id 2, empty). component 2: S and Fill tank F (id 3, empty).
                int sUnits = 0, fUnits = 0;
                List<(int src, int dst, int units)> Run(bool shared, Dictionary<int, int> sent, Dictionary<int, int> recv)
                {
                    var c1 = new List<RM_SettleTank> { new RM_SettleTank(1, 50, 100, "water", RM_TankMode.Empty), new RM_SettleTank(2, sUnits, 100, "water", RM_TankMode.Store) };
                    var p1 = shared ? RM_LiquidNetKernel.SettlePlan(c1, 10, 0, sent, recv) : RM_LiquidNetKernel.SettlePlan(c1, 10, 0);
                    foreach (var m in p1) { if (c1[m.dst].Id == 2) sUnits += m.units; if (shared) { sent[c1[m.src].Id] = (sent.TryGetValue(c1[m.src].Id, out int a) ? a : 0) + m.units; recv[c1[m.dst].Id] = (recv.TryGetValue(c1[m.dst].Id, out int b) ? b : 0) + m.units; } }
                    var c2 = new List<RM_SettleTank> { new RM_SettleTank(2, sUnits, 100, "water", RM_TankMode.Store), new RM_SettleTank(3, fUnits, 100, null, RM_TankMode.Fill) };
                    var p2 = shared ? RM_LiquidNetKernel.SettlePlan(c2, 10, 0, sent, recv) : RM_LiquidNetKernel.SettlePlan(c2, 10, 0);
                    foreach (var m in p2) if (c2[m.dst].Id == 3) { fUnits += m.units; sUnits -= m.units; }
                    return p2;
                }
                Run(false, null, null);
                Assert(fUnits == 10, "can-fail: today's per-component plan sends on the 10 units S received this settle (F got " + fUnits + ")");
                sUnits = 0; fUnits = 0;
                Run(true, new Dictionary<int, int>(), new Dictionary<int, int>());
                Assert(fUnits == 0 && sUnits == 10, "with the shared budget S sends nothing it received this settle (F " + fUnits + ", S " + sUnits + ")");
                // a sender's budget is shared too: S starts with 40, sends 10 to F in component 2 after sending 10 elsewhere
                var sent2 = new Dictionary<int, int> { { 2, 10 } };
                var plan = RM_LiquidNetKernel.SettlePlan(new List<RM_SettleTank> { new RM_SettleTank(2, 40, 100, "water", RM_TankMode.Store), new RM_SettleTank(3, 0, 100, null, RM_TankMode.Fill) }, 10, 0, sent2, new Dictionary<int, int>());
                Assert(plan.Count == 0, "a tank that already sent its 10 this settle sends no more (" + plan.Count + " moves)");
                string net = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"sentById\[src\.thingIDNumber\] = .*\+ mv\.Moved; recvById\[dst\.thingIDNumber\] = .*\+ mv\.Moved;", "SettleTick records committed moves per tank");
            });

            // PIPE_ADAPTER_FIX_DEBT_NEVER_PAID C1-F8: a partial accept's debt (negative carry) is charged on the next send.
            Case("GptA_adapter_send_debt_is_paid", () =>
            {
                float carry = 0f, per = 1f, ve = 0f;
                int tank = 100;
                // send 1: 3 units offered, the net takes 2.5 (a short accept): 2 units leave the tank, 0.5 is owed
                int u1 = RM_LiquidTransfer.SettleSend(2.5f, per, 3, ref carry);
                tank -= u1; ve += 2.5f;
                Assert(u1 == 2 && Math.Abs(carry + 0.5f) < 1e-4f, "short accept: 2 units, carry -0.5 (" + u1 + ", " + carry + ")");
                // send 2: 3 units; the adapter offers 2.5 (the debt paid first), the net takes it all: 3 units leave the tank
                float ask = RM_LiquidTransfer.SendAsk(3, per, carry);
                Assert(Math.Abs(ask - 2.5f) < 1e-4f, "the offer is the units less the debt (" + ask + ")");
                int u2 = RM_LiquidTransfer.SettleSend(ask, per, 3, ref carry);
                tank -= u2; ve += ask;
                Assert(u2 == 3 && Math.Abs(carry) < 1e-4f, "the debt is paid: 3 units, carry 0 (" + u2 + ", " + carry + ")");
                Assert(Math.Abs(tank * per + ve + carry - 100f) < 1e-3f, "tank x per + net + carry is conserved (" + (tank * per + ve + carry) + ")");
                // over many short sends nothing is created
                carry = 0f; tank = 1000; ve = 0f;
                var rnd = new Random(3);
                for (int i = 0; i < 500; i++)
                {
                    float a = RM_LiquidTransfer.SendAsk(4, 1.3f, carry);
                    float took = (float)Math.Round(a * rnd.NextDouble(), 3);
                    int u = RM_LiquidTransfer.SettleSend(took, 1.3f, 4, ref carry);
                    tank -= u; ve += took;
                }
                Assert(Math.Abs(tank * 1.3f + ve + carry - 1300f) < 0.05f, "500 random short accepts conserve resource (" + (tank * 1.3f + ve + carry) + ")");
                Assert(carry > -1.3f - 1e-3f, "the debt never grows past one unit (" + carry + ")");
            });

            // TANK_CONTENTS_SALVAGE_ON_DECONSTRUCT C2-F5/C1-F1: a destroyed tank spills, a drill returns, a converter drops pending items.
            Case("GptA_destroyed_tank_drill_converter_keep_their_contents", () =>
            {
                string tank = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("LiquidTypes", "Building_LiquidTank.cs"));
                RiverSwitchFlipChecks.Has(tank, @"public override void Destroy\(DestroyMode mode = DestroyMode\.Vanish\) \{ if \(Spawned && !Empty && mode != DestroyMode\.Vanish && mode != DestroyMode\.WillReplace\)", "the tank overrides Destroy");
                RiverSwitchFlipChecks.Has(tank, @"base\.Destroy\(mode\); Machinery\.RM_LiquidSpill\.Spill\(map, at, liquid, units\);", "its stock spills where it stood");
                string drill = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Drilling", "Building_LiquidDrill.cs"));
                RiverSwitchFlipChecks.Has(drill, @"GetComponent<RM_MapComponent_SubsurfaceLiquid>\(\)\?\.ReturnUnits\(pendingUnits\);", "the drill returns pending units to the deposit");
                string conv = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "CompLiquidConverter.cs"));
                RiverSwitchFlipChecks.Has(conv, @"public override void PostDestroy\(DestroyMode mode, Map previousMap\)", "the converter settles pending items on destroy");
                RiverSwitchFlipChecks.Has(conv, @"GenPlace\.TryPlaceThing\(t, at, previousMap, ThingPlaceMode\.Near\);", "they are placed on the map it stood on");
            });

            // HOSE_OFF_MEND_SLEEPWALKING_RETRACT C7a-F4: with hoses off, no reroute / trail deletion / auto-retract.
            Case("GptA_hoses_off_never_retract_on_obstacles", () =>
            {
                string mc = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                RiverSwitchFlipChecks.Has(mc, @"if \(RM_HoseSettings\.enabled && \(now \+ r\.parent\.thingIDNumber\) % 250 == 0 && r\.layKey != null", "the obstacle check runs only with hoses on");
                int at = mc.IndexOf("r.Retract(why); Retracts++;", StringComparison.Ordinal), gate = mc.IndexOf("if (RM_HoseSettings.enabled && (now + r.parent.thingIDNumber) % 250 == 0", StringComparison.Ordinal);
                Assert(gate > 0 && at > gate, "the automatic retract sits inside the gated block");
            });

            // HOSE_ORDERS_MEND_WAITING_FOREVER C7b-F2..F8.
            Case("GptA_hose_orders_fresh_order_on_dropped_end_runs", () =>
            {
                Assert(HoseOrderRules.MayResume(HoseCarryState.Dropped, HosePendingOrder.Move, false, false, true), "C7b-F2: a new order on a dropped end runs with auto-resume off");
                Assert(!HoseOrderRules.MayResume(HoseCarryState.Dropped, HosePendingOrder.Move, false, false, false), "an interrupted order still waits (the setting's point)");
                Assert(!HoseOrderRules.MayResume(HoseCarryState.Dropped, HosePendingOrder.None, false, false, true), "no order, nothing to run");
                string reel = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "CompHoseReel.cs"));
                Assert(System.Text.RegularExpressions.Regex.Matches(reel, @"pendingFresh = true;").Count == 3, "Deploy, Move and Retract orders are fresh");
                RiverSwitchFlipChecks.Has(reel, @"carrier = null; pendingFresh = false;", "a dropped carry turns the order into a resume");
                RiverSwitchFlipChecks.Has(reel, @"wound = 0f; pendingFresh = false;", "an interrupted wind turns the order into a resume");
                RiverSwitchFlipChecks.Has(reel, @"Scribe_Values\.Look\(ref pendingFresh, ""rmHosePendingFresh""\);", "freshness is saved");
                string wg = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "Jobs", "WorkGiver_HoseOrders.cs"));
                RiverSwitchFlipChecks.Has(wg, @"HoseOrderRules\.MayResume\(r\.carry, r\.pending, forced, HoseJobTuning\.autoResumeDroppedHose, r\.pendingFresh\)", "the work giver reads freshness");
                RiverSwitchFlipChecks.Has(wg, @"if \(!pawn\.CanReach\(dest, destMode, d\)\)", "C7b-F4: destination checked with the driver's end mode");
                string fm = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "Jobs", "FloatMenuOptionProvider_Hose.cs"));
                RiverSwitchFlipChecks.Has(fm, @"string endBlocked = Blocked\(p, r, clickedThing, false\) \?\? EndBlocked\(p, r\);", "C7b-F3: moving an end needs a path to the end, not the reel");
                Assert(System.Text.RegularExpressions.Regex.Matches(fm, @"!HoseJobs\.GiveForced\(").Count == 2, "C7b-F5: both forced submissions restore the order when refused");
                string drv = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "Jobs", "JobDriver_CarryHoseEnd.cs"));
                RiverSwitchFlipChecks.Has(drv, @"\|\| HosePorts\.FindAt\(r\.parent\.Map, Dest, r\.parent, out RimMandrake\.Shared\.Slack\.Cell _, out HosePortKind _\) != null\);", "C7b-F8: a port coupling takes the coupling time");
            });

            // HOSE_SPILL_MEND_POND_GETS_NOTHING C1-F10/F11/F12.
            Case("GptA_hose_drain_and_spill_go_back_to_the_pond", () =>
            {
                string sp = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Machinery", "RM_LiquidSpill.cs"));
                RiverSwitchFlipChecks.Has(sp, @": kind == RM_OutletKind\.Body && ex\.TryReturnLevels\(c, liquid\.canalFluid, 1\);", "C1-F10: held liquid drains whole levels back into a pond");
                RiverSwitchFlipChecks.Has(sp, @"units -= ReturnToPond\(map, cell, liquid, units\); if \(units <= 0\) \{ return; \} SpilledUnits \+= units;", "C1-F11: a spill over its pond returns to the pond before it counts as filth");
                RiverSwitchFlipChecks.Has(sp, @"if \(onEnd != null && onEnd\.def\.passability == Traversability\.Impassable\) \{ return RM_OutletKind\.Blocked; \} if \(ex != null && fluid != null\)", "C1-F12: an end under a wall is blocked before any neighbour is tried");
            });

            // HOSE_IMPORT_MEND_ONE_SHOT_MISS C8a-F1: the GSS import is marked done only after it read.
            Case("GptA_hose_import_marked_done_after_success", () =>
            {
                string lg = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Hose", "RM_HoseLegacy.cs"));
                int mark = lg.IndexOf("RM_HoseSettings.hoseSettingsImported = true;", StringComparison.Ordinal);
                int read = lg.IndexOf("File.ReadAllText(hoseFile)", StringComparison.Ordinal);
                int katch = lg.IndexOf("catch (Exception ex)", Math.Max(0, read), StringComparison.Ordinal);
                Assert(read > 0 && mark > read && mark < katch, "the done flag is set after the read, inside the try");
                Assert(lg.IndexOf("RM_HoseSettings.hoseSettingsImported = true;", mark + 1, StringComparison.Ordinal) < 0, "and nowhere else");
                RiverSwitchFlipChecks.Has(lg, @"catch \(Exception ex\) \{ Log\.Warning\(.*?\); return false; \}", "a failed import changes nothing and retries");
            });

            // HOSE_LAY_POLISH_CENTRE_VS_MOUTH C8a-F4: the install pre-check measures from the mouth the route starts at.
            Case("GptA_hose_install_range_from_the_mouth", () =>
            {
                var w = new CordWorld(120, 40);
                var reel = new HoseReelRect(50, 20, 2, 2);
                var target = new Cell(40, 21);   // west, the mouth side: 9.5 from the mouth, 10.5 from the centre
                double fromMouth = V2.Dist(reel.Mouth, target.Centre), fromCentre = V2.Dist(reel.Centre, target.Centre);
                Assert(fromMouth < 10.0 && fromCentre > 10.2, "fixture: mouth " + fromMouth.ToString("0.00") + ", centre " + fromCentre.ToString("0.00"));
                string why = HoseMath.CheckInstall(w, reel, target, 10.2);
                Assert(why == null, "a target the route reaches within the hose is accepted (got " + (why ?? "null") + ")");
                Assert(HoseMath.CheckInstall(w, reel, new Cell(30, 21), 10.2) == "too far", "a target past the hose's reach from the mouth is still too far");
            });

            // DBH_WATER_MEND_ACID_ON_TAP C9-F4/C9-F6: only plain waters carry dbh_water; full DBH gets the integration too.
            Case("GptA_dbh_water_only_on_plain_water_and_full_dbh_gated", () =>
            {
                string mod = System.IO.Path.GetDirectoryName(System.IO.Path.GetDirectoryName(ContainerMatFixture.Root()));
                var keep = new HashSet<string> { "RM_WaterFrigid", "RM_WaterBrackish", "RM_WaterBrine", "RM_WaterMineral" };
                int checkedFiles = 0;
                foreach (string f in System.IO.Directory.GetFiles(System.IO.Path.Combine(mod, "Defs", "LiquidTypes", "TerrainDefs"), "*.xml"))
                {
                    string name = System.IO.Path.GetFileNameWithoutExtension(f);
                    bool has = System.IO.File.ReadAllText(f).Contains("dbh_water");
                    Assert(has == keep.Contains(name), name + (has ? " carries dbh_water (a hazardous liquid as a wash/drink source)" : " lost dbh_water"));
                    checkedFiles++;
                }
                Assert(checkedFiles >= 19, "instrument: read " + checkedFiles + " liquid terrain files");
                foreach (string pf in new[] { "RM_DBH_WaterTerrainTag.xml", "RM_DBH_FreshWaterDrinkables.xml" })
                    Assert(System.IO.File.ReadAllText(System.IO.Path.Combine(mod, "Patches", "LiquidTypes", pf)).Contains("<li>Dubs Bad Hygiene</li>"), pf + " fires for full DBH too");
                string bottles = System.IO.File.ReadAllText(System.IO.Path.Combine(mod, "Defs", "ManyWaters", "ThingDefs", "RM_ColoredWaterBottles.xml"));
                Assert(!bottles.Contains("MayRequire=\"Dubwise.DubsBadHygiene.Lite\"") && bottles.Contains("MayRequireAnyOf=\"Dubwise.DubsBadHygiene.Lite,Dubwise.DubsBadHygiene\""), "coloured bottles load with either DBH");
                string gen = System.IO.File.ReadAllText(System.IO.Path.Combine(mod, "Tools", "generate_liquid_suite.py"));
                Assert(gen.Contains("DBH_WATER_PREFIXES = {\"RM_WaterFrigid\", \"RM_WaterBrackish\", \"RM_WaterBrine\", \"RM_WaterMineral\"}"), "the generator keeps the same list, so a regeneration does not put the tag back");
            });
        }
    }
}
