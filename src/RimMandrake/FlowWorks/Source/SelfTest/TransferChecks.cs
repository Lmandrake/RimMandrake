// Build step L1 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md §4, §6 L1): the one transfer service.
//   * RM_LiquidTransfer.Move (PRODUCTION, ../Machinery/RM_LiquidTransfer.cs) with an injected refusal on each leg, at
//     validation (Can) and at mutation (Do), leaves every total unchanged and credits nothing;
//   * one case per production site (pump draw from a channel and from a body, pump pour, converter to a tank and to items,
//     reactor, bath, adapter send and take, tank feed): that site's legs, over fake stores that keep the tank's rules, with
//     each leg refused in turn; then the PRODUCTION site is read and must build exactly those legs inside Move and credit
//     only inside the block of a committed Move (the RiverSwitchFlipChecks pattern);
//   * caller coverage over the whole production source: every tank / world / VE mutation in the L1 site files is inside a
//     transfer leg, every hose credit is inside a committed-Move block, the credit sites are FINAL's 11 plus the tank feed, the pump's six hose-end credits (L6), the dump drain (L7) and the pond return,
//     and no other file mutates a tank except the listed item-and-bottle paths. Can-fail: planted violations are caught.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class TransferChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A store with Building_LiquidTank's rules (one liquid, capacity; emptied clears the liquid), plus injected
        /// refusals.</summary>
        internal sealed class Tank
        {
            public string Liquid;
            public int Units, Cap;
            public bool RefuseAdd, RefuseRemove, RefuseUndo;
            public Tank(string liquid, int units, int cap) { Liquid = units > 0 ? liquid : null; Units = units; Cap = cap; }
            public bool Empty => Liquid == null || Units <= 0;
            public bool CanAccept(string l, int k) => l != null && k > 0 && (Empty || Liquid == l) && Units + k <= Cap;
            public bool CanProvide(int k) => !Empty && k > 0 && Units >= k;
            public bool TryAdd(string l, int k) { if (RefuseAdd || !CanAccept(l, k)) return false; Liquid = l; Units += k; return true; }
            public bool TryRemove(int k) { if (RefuseRemove || !CanProvide(k)) return false; Units -= k; if (Units <= 0) { Units = 0; Liquid = null; } return true; }
            public RM_TransferLeg In(string l, int per = 1) => RM_TransferLeg.Store(k => CanAccept(l, k * per), k => TryAdd(l, k * per), k => !RefuseUndo && TryRemove(k * per));
            public RM_TransferLeg Out(int per = 1)
            {
                string l = Liquid;
                return RM_TransferLeg.Store(k => CanProvide(k * per), k => TryRemove(k * per), k => !RefuseUndo && TryAdd(l, k * per));
            }
            public override string ToString() => (Liquid ?? "-") + ":" + Units;
        }

        /// <summary>The world (a channel cell's levels or a body's stock): checked, then taken or given, never undone.</summary>
        internal sealed class World
        {
            public int Levels;
            public int Room = 99;
            public bool CanSay = true, RefuseDo;
            public int Calls;
            public RM_TransferLeg Take(int perLevel) => RM_TransferLeg.World(k => CanSay && Levels > 0, k => { Calls++; if (RefuseDo || Levels <= 0) return false; Levels--; return true; });
            public RM_TransferLeg Pour(int perLevel) => RM_TransferLeg.World(k => CanSay && Room > 0, k => { Calls++; if (RefuseDo || Room <= 0) return false; Room--; Levels++; return true; });
        }

        private const int Level = 5;   // a test level: Move and the legs are unit-agnostic (production: RM_Volume.UnitsPerLevel)

        public static void Run(Action<string, Action> Case)
        {
            Case("Transfer_Move_refusal_on_either_leg_changes_nothing", MoveCore);
            Case("Transfer_Move_composite_legs_are_all_or_nothing", Composites);
            Case("Transfer_Adapter_boundary_conserves_with_carry", Boundary);
            Case("Transfer_site_pump_draw_channel", () => PumpDraw(true));
            Case("Transfer_site_pump_draw_source", () => PumpDraw(false));
            Case("Transfer_site_pump_draw_pond_to_the_last_decilitre", PondPumpsDry);
            Case("Transfer_site_pump_pour", PumpPour);
            Case("Transfer_site_converter", Converter);
            Case("Transfer_site_reactor", Reactor);
            Case("Transfer_site_bath", Bath);
            Case("Transfer_site_adapter", AdapterSite);
            Case("Transfer_site_tank_settle", TankFeed);
            Case("Transfer_caller_coverage", CallerCoverage);
        }

        // ------------------------------------------------------------------------------------------- the service itself
        private static void MoveCore()
        {
            foreach (string where in new[] { "srcCan", "dstCan", "srcDo", "dstDo" })
            {
                var a = new Tank("water", 20, 100);
                var b = new Tank("water", 0, 100);
                RM_TransferLeg src = where == "srcCan" ? new RM_TransferLeg("store", k => false, a.Out().Do, a.Out().Undo) : a.Out();
                RM_TransferLeg dst = where == "dstCan" ? new RM_TransferLeg("store", k => false, b.In("water").Do, b.In("water").Undo) : b.In("water");
                a.RefuseRemove = where == "srcDo";
                b.RefuseAdd = where == "dstDo";
                int m = RM_LiquidTransfer.Move(5, src, dst, out RM_MoveOutcome o);
                Assert(m == 0 && a.Units == 20 && b.Units == 0 && o.Lost == 0 && o.Refused != RM_MoveRefusal.None,
                    "refusal at " + where + ": moved " + m + ", " + a + " " + b + ", lost " + o.Lost);
            }
            var x = new Tank("water", 20, 100);
            var y = new Tank("water", 0, 100);
            Assert(RM_LiquidTransfer.Move(5, x.Out(), y.In("water"), out RM_MoveOutcome ok) == 5 && x.Units == 15 && y.Units == 5 && ok.Refused == RM_MoveRefusal.None,
                "an accepted move moves exactly the units");
            // the reversible leg goes FIRST: a world source is never touched when the tank refuses at mutation
            var w = new World { Levels = 3 };
            var t = new Tank(null, 0, 100) { RefuseAdd = true };
            Assert(RM_LiquidTransfer.Move(Level, w.Take(Level), t.In("water"), out _) == 0 && w.Levels == 3 && w.Calls == 0,
                "a tank refusing at mutation: the world leg is never called (" + w.Calls + " calls)");
            // ... and a world refusing after the tank was reserved puts the tank back
            var w2 = new World { Levels = 3, RefuseDo = true };
            var t2 = new Tank("water", 10, 100);
            Assert(RM_LiquidTransfer.Move(Level, w2.Take(Level), t2.In("water"), out RM_MoveOutcome o2) == 0 && t2.Units == 10 && w2.Levels == 3 && o2.Refused == RM_MoveRefusal.SourceDo,
                "the world refusing last: the reserved tank units are put back");
            // two irreversible legs are refused before anything happens
            var w3 = new World { Levels = 3 };
            Assert(RM_LiquidTransfer.Move(Level, w3.Take(Level), w3.Pour(Level), out RM_MoveOutcome o3) == 0 && w3.Calls == 0 && o3.Refused == RM_MoveRefusal.BothIrreversible,
                "world to world is refused unrun");
            // a put-back that fails is REPORTED, never silent
            var p = new Tank("water", 20, 100) { RefuseUndo = true };
            var q = new Tank("water", 0, 100) { RefuseAdd = true };
            RM_LiquidTransfer.Move(5, p.Out(), q.In("water"), out RM_MoveOutcome o4);
            Assert(o4.Lost == 5, "a put-back that fails is reported as lost (" + o4.Lost + ")");
            Assert(RM_LiquidTransfer.Move(0, x.Out(), y.In("water"), out RM_MoveOutcome o5) == 0 && o5.Refused == RM_MoveRefusal.Nothing, "zero units: nothing");
        }

        private static void Composites()
        {
            // All: a reactor's two reactants move together or not at all
            var a = new Tank("tar", 10, 100);
            var b = new Tank("acid", 10, 100) { RefuseRemove = true };
            var p = new Tank(null, 0, 100);
            Assert(RM_LiquidTransfer.Move(2, RM_TransferLeg.All(a.Out(1), b.Out(2)), p.In("gas"), out _) == 0 && a.Units == 10 && b.Units == 10 && p.Units == 0,
                "All: B refusing puts A back");
            b.RefuseRemove = false;
            Assert(RM_LiquidTransfer.Move(2, RM_TransferLeg.All(a.Out(1), b.Out(2)), p.In("gas"), out _) == 2 && a.Units == 8 && b.Units == 6 && p.Units == 2,
                "All: both reactants move per batch");
            // Split: a level spread over tanks (L3 uses it), all-or-nothing, undone from the last parts
            var t1 = new Tank("water", 97, 100);
            var t2 = new Tank("water", 98, 100) { RefuseAdd = true };
            int[] parts = { 3, 2 };
            Tank[] ts = { t1, t2 };
            RM_TransferLeg split = RM_TransferLeg.Split(2, i => parts[i], (i, k) => ts[i].CanAccept("water", k), (i, k) => ts[i].TryAdd("water", k), (i, k) => ts[i].TryRemove(k));
            var src = new Tank("water", 50, 100);
            Assert(RM_LiquidTransfer.Move(5, src.Out(), split, out _) == 0 && t1.Units == 97 && t2.Units == 98 && src.Units == 50, "Split: the second part refusing undoes the first");
            t2.RefuseAdd = false;
            Assert(RM_LiquidTransfer.Move(5, src.Out(), split, out _) == 5 && t1.Units == 100 && t2.Units == 100 && src.Units == 45, "Split: 3 + 2 takes the level");
            // the full tanks above would refuse any count, so probe a fresh Split over two empty tanks: only the exact sum passes
            var e1 = new Tank(null, 0, 100); var e2 = new Tank(null, 0, 100);
            Tank[] es = { e1, e2 };
            RM_TransferLeg fresh = RM_TransferLeg.Split(2, i => parts[i], (i, k) => es[i].CanAccept("water", k), (i, k) => es[i].TryAdd("water", k), (i, k) => es[i].TryRemove(k));
            Assert(fresh.Can(5) && !fresh.Can(4), "Split: parts that do not sum to the units are refused at validation (empty tanks, so only the sum can refuse)");
        }

        private static void Boundary()
        {
            // invariant: tank units x per + VE stored + carry, over random sends and takes with short accepts
            var rnd = new Random(11);
            foreach (float per in new[] { 1f, 0.5f, 1.5f, 2.5f, 0.3f })
            {
                float carry = 0f, ve = 37.3f;
                var tank = new Tank("chemfuel", 60, 1000);
                double I0 = tank.Units * per + ve + carry;
                for (int step = 0; step < 400; step++)
                {
                    int k = 1 + rnd.Next(10);
                    float shortFrac = (float)rnd.NextDouble();
                    bool send = rnd.Next(2) == 0;
                    RM_TransferLeg b = send
                        ? RM_TransferLeg.Boundary(u => true, u => { float d = Math.Min(u * per, u * per * shortFrac + (rnd.Next(3) == 0 ? u * per : 0f)); ve += d; return Math.Max(0, RM_LiquidTransfer.SettleSend(d, per, u, ref carry)); })
                        : RM_TransferLeg.Boundary(u => true, u => { float ask = Math.Max(0f, u * per - Math.Max(0f, carry)); float d = Math.Min(ve, ask * shortFrac + (rnd.Next(3) == 0 ? ask : 0f)); d = Math.Min(d, ve); ve -= d; return Math.Max(0, RM_LiquidTransfer.SettleTake(d, per, u, ref carry)); });
                    if (send) RM_LiquidTransfer.Move(Math.Min(k, tank.Units), tank.Out(), b, out _);
                    else RM_LiquidTransfer.Move(k, b, tank.In("chemfuel"), out _);
                }
                double I1 = tank.Units * per + ve + carry;
                Assert(Math.Abs(I1 - I0) < 1e-2, "per " + per + ": units x per + stored + carry " + I0.ToString("0.000") + " -> " + I1.ToString("0.000"));
                Assert(Math.Abs(carry) < per * 400, "carry stays bounded");
            }
            float c = 0f;
            Assert(RM_LiquidTransfer.SettleSend(float.NaN, 1f, 5, ref c) == -1 && RM_LiquidTransfer.SettleTake(3f, float.PositiveInfinity, 5, ref c) == -1
                   && RM_LiquidTransfer.SettleTake(3f, 0f, 5, ref c) == -1 && c == 0f, "non-finite reading or ratio: -1 (fail closed), carry untouched");
            // a short accept of 3.7 at per 1: 3 units go across, 2 come back, 0.7 is carried (never rounded away)
            c = 0f;
            Assert(RM_LiquidTransfer.SettleSend(3.7f, 1f, 5, ref c) == 3 && Math.Abs(c + 0.7f) < 1e-4, "short send: 3 of 5, carry -0.7 (" + c + ")");
            c = 0.7f;
            Assert(RM_LiquidTransfer.SettleTake(4.4f, 1f, 5, ref c) == 5 && Math.Abs(c - 0.1f) < 1e-4, "carry 0.7 + 4.4 drawn pays 5 units, 0.1 carried (" + c + ")");
        }

        // ------------------------------------------------------------------------------------------- one case per site
        /// <summary>Runs <paramref name="scene"/> with each refusal in <paramref name="faults"/> injected in turn, asserting
        /// the ledger snapshot unchanged and no credit; then with no fault, asserting it moved.</summary>
        private static void EachFault(string site, string[] faults, Func<string, (string before, string after, int credited, int moved)> scene)
        {
            foreach (string f in faults)
            {
                var r = scene(f);
                Assert(r.before == r.after && r.credited == 0 && r.moved == 0, site + ": refusal '" + f + "' changed " + r.before + " -> " + r.after + ", credited " + r.credited);
            }
            var ok = scene(null);
            Assert(ok.before != ok.after && ok.moved > 0 && ok.credited == ok.moved, site + ": with no refusal it moves and credits (" + ok.before + " -> " + ok.after + ")");
        }

        private static void PumpDraw(bool channel)
        {
            EachFault(channel ? "pump draw (channel)" : "pump draw (source)", new[] { "worldCan", "worldDo", "tankCan", "tankDo" }, f =>
            {
                var w = new World { Levels = 4, CanSay = f != "worldCan", RefuseDo = f == "worldDo" };
                var t = new Tank("water", f == "tankCan" ? 98 : 10, 100) { RefuseAdd = f == "tankDo" };
                string b = w.Levels + "/" + t;
                int credited = 0;
                int m = RM_LiquidTransfer.Move(Level, w.Take(Level), t.In("water"), out _);
                if (m == Level) credited += m;
                return (b, w.Levels + "/" + t, credited, m);
            });
            string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
            string world = channel
                ? @"RM_TransferLeg\.World\(k => ex\.IsExcavated\(cell\) && ex\.WaterDlAt\(cell\) >= k, k => ex\.TryTakeDl\(cell, k, out _\) == k\)"
                : @"RM_TransferLeg\.World\(k => ex\.Stock\.SupplyDl\(Map, cell, k, ex\) >= k, k => ex\.Stock\.TryDebitDl\(Map, cell, k, ex\)\)";
            // LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (channel) and POND_PUMP_FIX_LAST_DROP_COUNTS (source): both give up to a notch, in dL
            const string amount = "take";
            RiverSwitchFlipChecks.Has(pump, @"RM_TransferLeg world = " + world + @"; if \(RM_LiquidTransfer\.Move\(" + amount + @", world, " + PlanInto("l") + @", out \w+\) == " + amount + @"\) \{ foreach \(\(Building_LiquidTank tank, int units\) p in plan\) Machinery\.RM_LiquidNet\.Credit\(this, p\.tank, l, p\.units, RM_PumpMath\.CycleTicks\); // credit site: pump draw \(" + (channel ? "channel" : "source") + @"\)",
                "pump draw " + (channel ? "(channel)" : "(source)") + ": world leg checked first, the tank leg in Move, credit inside the committed block");
        }

        /// <summary>POND_PUMP_FIX_LAST_DROP_COUNTS (owner by card 2026-10-22, GPT review Q6 → "ponds pump to the last dL"): a natural pond is
        /// pumped to the last decilitre, as a dug channel is. A fake pond (decilitre stock) is drained through Move with the
        /// PRODUCTION take rule (RM_PumpMath.SourceTakeUnits) until the pump finds nothing; exact-level on it ends at 0 dL with
        /// every dL in the tank, off it keeps the sub-notch remainder (the old rule, kept for that setting). Can-fail: the old
        /// whole-notch rule planted in exact mode strands the remainder and the check sees it. Then the production pump must
        /// gate drawability and the take on that rule.</summary>
        private static void PondPumpsDry()
        {
            const int U = RM_PumpMath.TankUnitsPerLevel;
            Func<int, long, bool, int> wholeNotch = (u, s, e) => s >= u ? u : 0;   // the defect: CanSupply + TryDebit(one notch)
            (long left, int moved) Drain(long stockDl, bool exact, Func<int, long, bool, int> rule)
            {
                long pond = stockDl;
                var tank = new Tank(null, 0, int.MaxValue);
                for (int cycle = 0; cycle < 1000; cycle++)
                {
                    int take = rule(U, Math.Min(pond, U), exact);
                    if (take <= 0) break;
                    RM_TransferLeg world = RM_TransferLeg.World(k => pond >= k, k => { if (pond < k) return false; pond -= k; return true; });
                    if (RM_LiquidTransfer.Move(take, world, tank.In("water"), out _) != take) break;
                }
                return (pond, tank.Units);
            }
            foreach (long start in new long[] { 1, 9_999, 10_000, 10_001, 23_456, 4 * 10_000L + 7 })
            {
                var on = Drain(start, true, RM_PumpMath.SourceTakeUnits);
                Assert(on.left == 0 && on.moved == start, "exact-level on: a " + start + " dL pond pumps dry (left " + on.left + ", moved " + on.moved + ")");
                var off = Drain(start, false, RM_PumpMath.SourceTakeUnits);
                Assert(off.left == start % U && off.moved == start - start % U, "exact-level off: whole notches only (left " + off.left + ")");
                if (start % U != 0)
                {
                    var bad = Drain(start, true, wholeNotch);
                    Assert(bad.left != 0, "can-fail: the old whole-notch rule strands " + bad.left + " dL and this check sees it");
                }
            }
            Assert(RM_PumpMath.SourceTakeUnits(U, 0, true) == 0 && RM_PumpMath.SourceTakeUnits(U, -5, true) == 0 && RM_PumpMath.SourceTakeUnits(0, 500, true) == 0,
                "a dry pond, a negative reading or no budget: nothing to take");
            string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
            RiverSwitchFlipChecks.Has(pump, @"return RM_PumpMath\.SourceTakeUnits\(units, ex\.Stock\.SupplyDl\(Map, c, units, ex\), RM_MapComponent_Excavation\.LevelExact\);",
                "the pump's take on a natural body is the selftested rule, on the body's decilitres");
            RiverSwitchFlipChecks.Has(pump, @"if \(ex\.IsSourceCell\(c\) && SourceTake\(ex, c\) > 0\)", "a natural body is drawable while that rule takes anything");
            RiverSwitchFlipChecks.Has(pump, @"int give = s\.channel \? RM_PumpMath\.ChannelTakeUnits\(units, ex\.WaterDlAt\(s\.cell\)\) : SourceTake\(ex, s\.cell\);",
                "the tank take starts from what the pond gives (a part notch at the end)");
            // PUMP_SOURCE_FIX_REJECTS_PARTIAL_DRAW: the take is cut to the store's room, and the SOURCE CHOICE asks for that take, not
            // a whole cycle (the old predicate FillPlan(this, lq, units) refused a nearly-full tank before the partial code ran)
            for (int give = -1; give <= U + 1; give += 1)
            {
                foreach (int room in new[] { -3, 0, 1, 899, 900, 901, U - 1, U, U + 1, 5 * U })
                {
                    foreach (bool part in new[] { true, false })
                    {
                        int t = RM_PumpMath.TankTakeUnits(give, room, part);
                        int want = give <= 0 || room <= 0 ? 0 : (room >= give ? give : (part ? room : 0));
                        Assert(t == want, "TankTakeUnits(" + give + ", " + room + ", " + part + ") = " + t + ", want " + want);
                        Assert(t >= 0 && t <= System.Math.Max(0, give) && t <= System.Math.Max(0, room), "never more than the source gives or the store holds");
                    }
                }
                if (give > U / 2) give += 97;   // sweep densely near 0 and the edges, sparsely in the middle
            }
            Assert(RM_PumpMath.TankTakeUnits(U, 900, true) == 900, "item scenario: a full source, a tank with 900 dL free: 900 dL go (exact-level on)");
            Assert(RM_PumpMath.TankTakeUnits(900, 900, true) == 900, "item scenario: a 900 dL source into exactly 900 dL of room");
            Assert(RM_PumpMath.TankTakeUnits(U, 900, false) == 0, "exact-level off, a natural body: whole notches only, as before");
            RiverSwitchFlipChecks.Has(pump, @"return RM_PumpMath\.TankTakeUnits\(give, Machinery\.RM_LiquidNet\.Room\(this, l\), s\.channel \|\| RM_MapComponent_Excavation\.LevelExact\);",
                "the pump's tank take is the selftested rule on the store's whole room (a channel moves part-levels always)");
            RiverSwitchFlipChecks.Has(pump, @"i => TankTake\(ex, sources\[i\], LiquidFor\(sources\[i\]\.fluid\)\) > 0, cycle,",
                "PumpNext's tank predicate asks for the affordable take, not a whole cycle");
            Assert(!Regex.IsMatch(pump, @"FillPlan\(this, lq?, units\)"), "can-fail: no whole-cycle fill plan is asked for anywhere in the pump's draw");
            RiverSwitchFlipChecks.Has(pump, @"int take = TankTake\(ex, s, l\); List<\(Building_LiquidTank tank, int units\)> plan = take > 0 \? Machinery\.RM_LiquidNet\.FillPlan\(this, l, take\) : null;",
                "the fill plan is for that same take");
            Assert(!Regex.IsMatch(pump, @"TryDebit\(Map, cell, f\.volumePerTile, ex\)"), "the whole-notch pond debit is gone from the pump");
        }

        /// <summary>The production destination leg of a pump draw (L3: the fill plan, split across tanks).</summary>
        internal static string PlanInto(string liquid) =>
            @"RM_TransferLeg\.Split\(plan\.Count, i => plan\[i\]\.units, \(i, k\) => plan\[i\]\.tank\.CanAccept\(" + liquid + @", k\), \(i, k\) => plan\[i\]\.tank\.TryAddLiquid\(" + liquid + @", k\), \(i, k\) => plan\[i\]\.tank\.TryRemoveLiquid\(k\)\)";

        private static void PumpPour()
        {
            EachFault("pump pour", new[] { "worldCan", "worldDo", "tankCan", "tankDo" }, f =>
            {
                var w = new World { Levels = 0, Room = 3, CanSay = f != "worldCan", RefuseDo = f == "worldDo" };
                var t = new Tank("water", f == "tankCan" ? 3 : 40, 100) { RefuseRemove = f == "tankDo" };
                string b = w.Levels + "/" + t;
                int credited = 0;
                int m = RM_LiquidTransfer.Move(Level, t.Out(), w.Pour(Level), out _);
                if (m == Level) credited += m;
                return (b, w.Levels + "/" + t, credited, m);
            });
            string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
            RiverSwitchFlipChecks.Has(pump, @"RM_TransferLeg world = RM_TransferLeg\.World\(k => ex\.IsExcavated\(cell\) && ex\.FillAt\(cell\) < ex\.DepthAt\(cell\), k => ex\.TryPourLevel\(cell, fluid\)\); if \(RM_LiquidTransfer\.Move\(units, RM_TransferLeg\.Store\(k => tank\.CanProvide\(k\), k => tank\.TryRemoveLiquid\(k\), k => tank\.TryAddLiquid\(poured, k\)\), world, out RM_MoveOutcome mv\) != units\) \{ return [^}]*\} Machinery\.RM_LiquidNet\.Credit\(this, tank, poured, units, RM_PumpMath\.CycleTicks\); // credit site: pump pour",
                "pump pour: the tank is removed first and put back if the cell refuses; credit only after the committed move");
            Assert(!Regex.IsMatch(pump, @"if \(!ex\.TryPourLevel\("), "the old pour-first order is gone");
        }

        private static void Converter()
        {
            // 2 in -> 1 out per batch, 3 batches; output to a tank, or to pending items
            EachFault("converter (tank output)", new[] { "inCan", "inDo", "outCan", "outDo" }, f =>
            {
                var i = new Tank("brine", f == "inCan" ? 4 : 30, 100) { RefuseRemove = f == "inDo" };
                var o = new Tank("water", f == "outCan" ? 99 : 0, 100) { RefuseAdd = f == "outDo" };
                string b = i + "/" + o;
                int m = RM_LiquidTransfer.Move(3, i.Out(2), o.In("water", 1), out _);
                return (b, i + "/" + o, m == 3 ? 3 : 0, m);
            });
            // item output: a pending count (saved), never lost; a different pending item blocks the move until placed
            int pending = 0;
            string pendingDef = null;
            RM_TransferLeg Pending(string def, int per) => new RM_TransferLeg("pending", k => pending == 0 || pendingDef == def, k => { pendingDef = def; pending += k * per; return k; }, k => { pending -= k * per; return true; });
            var inp = new Tank("ore slurry", 30, 100);
            Assert(RM_LiquidTransfer.Move(3, inp.Out(2), Pending("Steel", 1), out _) == 3 && pending == 3 && inp.Units == 24, "item output: 3 batches -> 3 pending items");
            Assert(RM_LiquidTransfer.Move(3, inp.Out(2), Pending("Jade", 1), out RM_MoveOutcome po) == 0 && po.DestRefused && pending == 3 && inp.Units == 24,
                "another item kind waits: the input is not consumed while Steel is still pending");
            inp.RefuseRemove = true;
            Assert(RM_LiquidTransfer.Move(3, inp.Out(2), Pending("Steel", 1), out _) == 0 && pending == 3, "input refusing: no item output (the old code made output anyway)");
            string conv = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "CompLiquidConverter.cs"));
            RiverSwitchFlipChecks.Has(conv, @"if \(RM_LiquidTransfer\.Move\(n, RM_TransferLeg\.Split\(inPlan\.Count, i => inPlan\[i\]\.units, \(i, k\) => inPlan\[i\]\.tank\.CanProvide\(k\), \(i, k\) => inPlan\[i\]\.tank\.TryRemoveLiquid\(k\), \(i, k\) => inPlan\[i\]\.tank\.TryAddLiquid\(inputLiquid, k\), step\.InputUnits\), dest, out RM_MoveOutcome mv\) == n\) \{ foreach \(\(Building_LiquidTank tank, int units\) p in inPlan\) RM_LiquidNet\.Credit\(parent, p\.tank, inputLiquid, p\.units, RM_ConversionMath\.RareTick\); // credit site: converter input foreach \(\(Building_LiquidTank tank, int units\) p in outPlan \?\? .*?\) RM_LiquidNet\.Credit\(parent, p\.tank, step\.product, p\.units, RM_ConversionMath\.RareTick\); // credit site: converter output",
                "converter: input and output one Move; both credits inside the committed block");
            RiverSwitchFlipChecks.Has(conv, @"new RM_TransferLeg\(""pending"", k => pendingCount == 0 \|\| pendingThing == step\.productThing,", "item output goes to the saved pending count");
            RiverSwitchFlipChecks.Has(conv, @"Scribe_Values\.Look\(ref pendingCount, ""RM_convPendingCount"", 0\);", "pending items are saved");
            RiverSwitchFlipChecks.Has(conv, @"bool ok = GenPlace\.TryPlaceThing\(t, at, parent\.Map, ThingPlaceMode\.Near\); int placed = ok \|\| t\.Destroyed \? count : count - t\.stackCount; pendingCount -= placed; if \(!ok\) \{ break; \}",
                "placement keeps whatever found no room pending");
            Assert(!conv.Contains("DropItems("), "the dropping path that lost unplaced items is gone");
        }

        private static void Reactor()
        {
            EachFault("reactor", new[] { "aCan", "aDo", "bCan", "bDo", "pCan", "pDo" }, f =>
            {
                var a = new Tank("tar", f == "aCan" ? 1 : 20, 100) { RefuseRemove = f == "aDo" };
                var b = new Tank("acid", f == "bCan" ? 1 : 20, 100) { RefuseRemove = f == "bDo" };
                var p = new Tank("green gas", f == "pCan" ? 100 : 0, 100) { RefuseAdd = f == "pDo" };
                string s = a + "/" + b + "/" + p;
                int m = RM_LiquidTransfer.Move(2, RM_TransferLeg.All(a.Out(2), b.Out(2)), p.In("green gas", 1), out _);
                return (s, a + "/" + b + "/" + p, m == 2 ? 2 : 0, m);
            });
            string re = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "Kits", "RM_LiquidReaction.cs"));
            RiverSwitchFlipChecks.Has(re, @"if \(RM_LiquidTransfer\.Move\(n, RM_TransferLeg\.All\(RM_TransferLeg\.Split\(pa\.Count, [^;]*?pa\[i\]\.tank\.TryRemoveLiquid\(k\), \(i, k\) => pa\[i\]\.tank\.TryAddLiquid\(r\.reactantA, k\), r\.UnitsA\), RM_TransferLeg\.Split\(pb\.Count, [^;]*?pb\[i\]\.tank\.TryRemoveLiquid\(k\), \(i, k\) => pb\[i\]\.tank\.TryAddLiquid\(r\.reactantB, k\), r\.UnitsB\)\), dest, out _\) == n\) \{ foreach [^;]*RM_LiquidNet\.Credit\(parent, p\.tank, r\.reactantA,[^;]*; // credit site: reactor A foreach [^;]*RM_LiquidNet\.Credit\(parent, p\.tank, r\.reactantB,[^;]*; // credit site: reactor B foreach [^;]*RM_LiquidNet\.Credit\(parent, p\.tank, r\.productLiquid,[^;]*; // credit site: reactor product",
                "reactor: A and B together (All), product in one Move; three credits inside the committed block");
            RiverSwitchFlipChecks.Has(re, @"RM_TransferLeg\.Split\(pp\.Count, i => pp\[i\]\.units, \(i, k\) => pp\[i\]\.tank\.CanAccept\(r\.productLiquid, k\), \(i, k\) => pp\[i\]\.tank\.TryAddLiquid\(r\.productLiquid, k\), \(i, k\) => pp\[i\]\.tank\.TryRemoveLiquid\(k\), r\.ProductUnits\)",
                "the product tank is a put-back-able leg (a refusal puts A and B back, never vents them)");
        }

        private static void Bath()
        {
            EachFault("bath", new[] { "tankCan", "tankDo" }, f =>
            {
                var t = new Tank("green slime", f == "tankCan" ? 3 : 20, 100) { RefuseRemove = f == "tankDo" };
                string b = t.ToString();
                int consumed = 0;
                int m = RM_LiquidTransfer.Move(5, t.Out(), RM_TransferLeg.Sink(k => consumed += k), out _);
                return (b, t.ToString(), m == 5 ? 5 : 0, m);
            });
            string bath = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "Kits", "RM_LiquidBath.cs"));
            RiverSwitchFlipChecks.Has(bath, @"if \(RM_LiquidTransfer\.Move\(ext\.UnitsPerCraft, RM_TransferLeg\.Split\(plan\.Count, i => plan\[i\]\.units, \(i, k\) => plan\[i\]\.tank\.CanProvide\(k\), \(i, k\) => plan\[i\]\.tank\.TryRemoveLiquid\(k\), \(i, k\) => plan\[i\]\.tank\.TryAddLiquid\(bathed, k\)\), RM_TransferLeg\.Sink\(null\), out _\) == ext\.UnitsPerCraft\) \{ // [^;]*?RM_LiquidNet\.Credit\(bench, p\.tank, bathed, p\.units,",
                "bath: the craft is a sink; credit inside the committed block");
        }

        private static void AdapterSite()
        {
            EachFault("adapter send", new[] { "tankCan", "tankDo", "veCan", "veZero" }, f =>
            {
                float carry = 0f, ve = 0f;
                var t = new Tank("chemfuel", f == "tankCan" ? 0 : 20, 100) { RefuseRemove = f == "tankDo" };
                string b = t + "/" + ve;
                RM_TransferLeg leg = RM_TransferLeg.Boundary(k => f != "veCan", k => { float d = f == "veZero" ? 0f : k; ve += d; return RM_LiquidTransfer.SettleSend(d, 1f, k, ref carry); });
                int m = RM_LiquidTransfer.Move(5, t.Out(), leg, out _);
                return (b, t + "/" + ve, m, m);
            });
            EachFault("adapter take", new[] { "tankCan", "tankDo", "veCan", "veZero" }, f =>
            {
                float carry = 0f, ve = 50f;
                var t = new Tank("chemfuel", f == "tankCan" ? 100 : 0, 100) { RefuseAdd = f == "tankDo" };
                string b = t + "/" + ve;
                RM_TransferLeg leg = RM_TransferLeg.Boundary(k => f != "veCan", k => { float d = f == "veZero" ? 0f : k; ve -= d; return RM_LiquidTransfer.SettleTake(d, 1f, k, ref carry); });
                int m = RM_LiquidTransfer.Move(5, leg, t.In("chemfuel"), out _);
                return (b, t + "/" + ve, m, m);
            });
            string ad = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "CompLiquidPipeAdapter.cs"));
            RiverSwitchFlipChecks.Has(ad, @"float before = Stored\(amountStored\); float ask = RM_LiquidTransfer\.SendAsk\(k, per, carry\); try \{ if \(ask > 0f\) addResource\.Invoke\(storage, new object\[\] \{ ask \}\); \} catch \(Exception\) \{ broken = true; return 0; \} int u = RM_LiquidTransfer\.SettleSend\(Stored\(amountStored\) - before, per, k, ref carry\);",
                "send: AddResource, then AmountStored read back and settled (a short accept puts units back, the fraction carried)");
            RiverSwitchFlipChecks.Has(ad, @"int u = RM_LiquidTransfer\.SettleTake\(before - Stored\(amountStored\), per, k, ref carry\);", "take: DrawResource read back and settled");
            RiverSwitchFlipChecks.Has(ad, @"if \(RM_LiquidTransfer\.Move\(take, RM_TransferLeg\.Split\(plan\.Count, [^;]*?plan\[i\]\.tank\.TryRemoveLiquid\(k\), \(i, k\) => plan\[i\]\.tank\.TryAddLiquid\(fed, k\)\), ve, out RM_MoveOutcome mv\) > 0\) \{ foreach \(\(Building_LiquidTank tank, int units\) p in RM_LiquidNet\.Committed\(plan, mv\.Moved\)\) RM_LiquidNet\.Credit\(parent, p\.tank, fed, p\.units,",
                "send: the tank leg first, the VE call last, the units SENT credited (the committed parts of the plan)");
            RiverSwitchFlipChecks.Has(ad, @"if \(RM_LiquidTransfer\.Move\(units, ve, RM_TransferLeg\.Split\(plan\.Count, [^;]*?plan\[i\]\.tank\.TryAddLiquid\(Props\.liquid, k\), \(i, k\) => plan\[i\]\.tank\.TryRemoveLiquid\(k\)\), out RM_MoveOutcome mv\) > 0\) \{ foreach \(\(Building_LiquidTank tank, int units\) p in RM_LiquidNet\.Committed\(plan, mv\.Moved\)\) RM_LiquidNet\.Credit\(parent, p\.tank, Props\.liquid, p\.units,",
                "take: the tank reserved first, the VE draw last, the units GOT credited");
            RiverSwitchFlipChecks.Has(ad, @"Scribe_Values\.Look\(ref carry, ""RM_adapterCarry"", 0f\);", "the carried fraction is saved");
            Assert(!Regex.IsMatch(ad, @"Convert\.ToSingle\(amountCanAccept\.GetValue"), "no unchecked reflection read is left");
        }

        private static void TankFeed()
        {
            EachFault("tank feed", new[] { "srcCan", "srcDo", "dstCan", "dstDo" }, f =>
            {
                var s = new Tank("water", f == "srcCan" ? 2 : 80, 100) { RefuseRemove = f == "srcDo" };
                var d = new Tank(f == "dstCan" ? "tar" : "water", f == "dstCan" ? 10 : 0, 100) { RefuseAdd = f == "dstDo" };
                string b = s + "/" + d;
                int m = RM_LiquidTransfer.Move(5, s.Out(), d.In("water"), out _);
                return (b, s + "/" + d, m, m);
            });
            // the production tank-settle site builds exactly these legs inside Move and credits only a committed move
            string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
            RiverSwitchFlipChecks.Has(net, @"RM_LiquidTransfer\.Move\(n, RM_TransferLeg\.Store\(k => src\.CanProvide\(k\), k => src\.TryRemoveLiquid\(k\), k => src\.TryAddLiquid\(liquid, k\)\),\s*RM_TransferLeg\.Store\(k => dst\.CanAccept\(liquid, k\), k => dst\.TryAddLiquid\(liquid, k\), k => dst\.TryRemoveLiquid\(k\)\), out RM_MoveOutcome mv\) > 0\)\s*\{\s*CreditRoute\(map, route, liquid, mv\.Moved,",
                "tank settle: source leg, destination leg, credit only inside the committed Move");
        }

        // ------------------------------------------------------------------------------------------- caller coverage
        /// <summary>The L1 site files: every tank, world and VE mutation in them must be a transfer leg.</summary>
        internal static readonly string[] SiteFiles =
        {
            "LiquidTypes/Building_LiquidPump.cs", "Machinery/CompLiquidConverter.cs", "Machinery/CompLiquidPipeAdapter.cs",
            "Machinery/Kits/RM_LiquidReaction.cs", "Machinery/Kits/RM_LiquidBath.cs", "Machinery/RM_LiquidNet.cs",
            "Sprinklers/RM_Sprinkle.cs",   // SPRINKLER_HEADS_BUILD_PUMP_REQUIRED: the sprinkler draw
            "Thirst/Building_RM_PipeFaucet.cs",   // PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE: a faucet's draw (drink or container)
            "RM_IceMelter.cs",   // ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN: a finished melt bill fills the bench's tanks
        };

        /// <summary>Files that may mutate a tank outside the transfer service, each with its reason (anything new fails).</summary>
        internal static readonly Dictionary<string, string> TankMutationAllowed = new Dictionary<string, string>
        {
            { "LiquidTypes/Building_LiquidTank.cs", "the definitions themselves" },
            { "LiquidTypes/JobDriver_EmptyBottleIntoTank.cs", "a pawn pours a carried container: the item is consumed only on a successful add" },
            { "LiquidTypes/JobDriver_FillBottleFromTank.cs", "a pawn fills a container: the item is made only on a successful remove" },
            { "Thirst/RM_ThirstJobs.cs", "a pawn drinks 1.5 L from a tank: the drink happens only on a successful remove (THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY)" },
            { "Machinery/RM_LiquidWorksRuins.cs", "ruin stock placed at map generation (no source leg exists)" },
            { "Hose/HoseNetProbe.cs", "the dev probe's filltank verb (test setup)" },
            { "RM_NorthstarProofs.cs", "ProofTank: the extension harness's tank staging (test setup, like the probe's filltank)" },
        };

        /// <summary>FINAL's 11 credit sites, the tank settle (L1/L4), the pump's hose-end credits (L6), the dump drain (L7) and the pond return: each tag exactly once, each inside a committed-Move block.</summary>
        internal static readonly string[] CreditTags =
        {
            "credit site: pump draw (channel)", "credit site: pump draw (source)", "credit site: pump pour", "credit site: converter input",
            "credit site: converter output", "credit site: adapter feeds the pipe net", "credit site: adapter draws from the pipe net",
            "credit site: reactor A", "credit site: reactor B", "credit site: reactor product", "credit site: bath", "credit site: tank settle",
            // L6 (rev 2 §3.3): the pump's hose free ends
            "credit site: pump to outflow", "credit site: pump intake (to outflow)", "credit site: pump intake (channel)", "credit site: pump intake (source)",
            "credit site: outflow pour (tank)", "credit site: outflow pour (end)",
            // L7: the Dump tank's slow drain
            "credit site: dump drain",
            // POND_RETURN_LEG_BUILD_WATER_GOES_HOME: a pump pours a level back into a pond in reach
            "credit site: pond return (pump)",
            // SPRINKLER_HEADS_BUILD_PUMP_REQUIRED: a sprinkler head's hourly draw to its spray (a Sink)
            "credit site: sprinkler draw",
            // PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: passive levelling between two bodies through a hose route
            "credit site: levelling",
            // CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED stage 1: a backed-up pump spills its level over a full canal's lip
            "credit site: pump overflow spill",
            // CANAL_OVERFLOW stage 2 (D2 gravity feed): a Dump tank against a full channel spills its surplus over the lip
            "credit site: gravity overflow",
            // PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE: a pipe faucet's draw for a drink or a container (a Sink)
            "credit site: faucet draw",
            // ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN: a melt bill's water into the tanks on the melter's net (a World source)
            "credit site: ice melter",
        };

        // review day 3: the decilitre movers (TryPourDl, TryDebitDl, CreditDl, TryReturnDl) joined the list; a site calling one
        // outside a leg went unseen (".TryDebit(" does not match ".TryDebitDl(")
        private static readonly string[] WorldMutations = { ".TryTakeLevel(", ".TryTakeDl(", ".TryDebit(", ".TryDebitDl(", ".TryPourLevel(", ".TryPourDl(",
            ".TryReturnLevels(", ".TryReturnDl(", ".CreditDl(", "addResource.Invoke(", "drawResource.Invoke(" };
        private static readonly string[] TankMutations = { ".TryAddLiquid(", ".TryRemoveLiquid(" };

        private static void CallerCoverage()
        {
            Dictionary<string, string> files = ProductionSources();
            int sourceFiles = files.Keys.Count(k => !k.StartsWith("//tags:"));   // review 2026-10-22: each file is keyed twice
            Assert(sourceFiles > 50, "read the production source (" + sourceFiles + " files)");
            List<string> bad = Lint(files, out int credits, out Dictionary<string, int> tags);
            Assert(bad.Count == 0, "caller coverage: " + string.Join("; ", bad.Take(8)));
            Assert(credits == CreditTags.Length, "credit calls = " + credits + ", want " + CreditTags.Length + " (FINAL's 11 + the tank settle + the pump's 6 hose-end credits + the dump drain + the pond pour)");
            // can-fail: an unwrapped add, an unwrapped world take, a credit outside a committed block, a new mutating file
            var planted = new Dictionary<string, string>(files);
            planted["Machinery/CompLiquidConverter.cs"] += "\nclass X { void Y() { output.TryAddLiquid(l, 5); ex.TryTakeLevel(c, out _); RM_LiquidNet.Credit(parent, output, l, 5, 250); } }";
            planted["Machinery/NewThing.cs"] = "class Z { void W() { tank.TryRemoveLiquid(5); } }";
            List<string> caught = Lint(planted, out _, out _);
            Assert(caught.Count == 4, "can-fail: 4 planted violations caught, got " + caught.Count + ": " + string.Join("; ", caught));
            // refused-credit can-fail (TRANSFER_LINT_HARDEN_REFUSED_CREDIT_PASSES): a credit under `== 0` (the refusal) and a credit
            // after a refusal branch whose only return is conditional are both caught; the correct early-return shape is not
            var refused = new Dictionary<string, string>(files);
            refused["Machinery/RefusedCredit.cs"] = "class R { void A() { if (RM_LiquidTransfer.Move(n, s, d, out _) == 0) { RM_LiquidNet.Credit(p, t, l, n, 250); } }\n"
                + " void B() { if (RM_LiquidTransfer.Move(n, s, d, out _) != n) { if (x) { return; } } RM_LiquidNet.Credit(p, t, l, n, 250); }\n"
                + " void C() { if (RM_LiquidTransfer.Move(n, s, d, out _) != n) { Log(\"}\"); return; } RM_LiquidNet.Credit(p, t, l, n, 250); }\n"
                + " void D() { if (RM_LiquidTransfer.Move(n, s, d, out _) == none) { RM_LiquidNet.Credit(p, t, l, n, 250); } }\n"
                + " void E() { if (RM_LiquidTransfer.Move(n, s, d, out _) != n) { char c = '}'; if (y) { return; } } RM_LiquidNet.Credit(p, t, l, n, 250); } }";
            List<string> refusedCaught = Lint(refused, out _, out _).Where(x => x.StartsWith("Machinery/RefusedCredit.cs")).ToList();
            string lines = string.Join(",", refusedCaught.Select(x => x.Substring(x.LastIndexOf(' ') + 1)).OrderBy(x => x));
            Assert(lines == "1,2,4,5", "refused-credit can-fail: the == 0 credit (line 1), the conditional-return credit (line 2), the == another-name"
                + " credit (line 4) and the char-literal '}' credit (line 5) caught, the early-return one (line 3) not; got " + string.Join("; ", refusedCaught));
            Assert(!EndsInReturn(" if (x) return; ") && EndsInReturn(" a(); return b ? 1 : 2; ") && !EndsInReturn(" return; a(); "),
                "refused-credit: EndsInReturn reads only the last top-level statement");
        }

        internal static Dictionary<string, string> ProductionSources()
        {
            string root = Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath(Path.Combine("Rivers", "RM_RiverMath.cs"))));
            var d = new Dictionary<string, string>();
            foreach (string p in Directory.GetFiles(root, "*.cs", SearchOption.AllDirectories))
            {
                string rel = Path.GetRelativePath(root, p).Replace('\\', '/');
                if (rel.StartsWith("SelfTest/") || rel.Contains("/bin/") || rel.Contains("/obj/") || rel.StartsWith("bin/") || rel.StartsWith("obj/")) continue;
                d[rel] = StripComments(File.ReadAllText(p), out _);
                d["//tags:" + rel] = File.ReadAllText(p);
            }
            return d;
        }

        internal static List<string> Lint(Dictionary<string, string> files, out int credits, out Dictionary<string, int> tags)
        {
            var bad = new List<string>();
            credits = 0;
            tags = CreditTags.ToDictionary(t => t, t => 0);
            foreach (KeyValuePair<string, string> kv in files)
            {
                if (kv.Key.StartsWith("//tags:"))
                {
                    foreach (string t in CreditTags) tags[t] += Regex.Matches(kv.Value, Regex.Escape(t)).Count;
                    continue;
                }
                string rel = kv.Key, src = kv.Value;
                List<(int a, int b)> legs = Spans(src, @"RM_TransferLeg\.\w+\(|new RM_TransferLeg\(");
                List<(int a, int b)> blocks = CommittedBlocks(src);
                // the crediting functions' own bodies (RM_LiquidNet.Credit calls CreditRoute) are the service, not a site
                List<(int a, int b)> defs = Regex.Matches(src, @"static void (Credit|CreditRoute|CreditTo)\(").Cast<Match>()
                    .Select(m => { int b0 = src.IndexOf('{', m.Index); return (m.Index, Match(src, b0, '{', '}')); }).ToList();
                bool site = SiteFiles.Contains(rel);
                foreach (string m in TankMutations.Concat(site ? WorldMutations : new string[0]))
                    foreach (int at in Occurrences(src, m))
                    {
                        if (rel == "LiquidTypes/Building_LiquidTank.cs") continue;
                        bool inLeg = legs.Any(s => at > s.a && at < s.b);
                        if (site && !inLeg) bad.Add(rel + ": " + m.Trim('.', '(') + " outside a transfer leg at " + Line(src, at));
                        if (!site && TankMutations.Contains(m) && !TankMutationAllowed.ContainsKey(rel)) bad.Add(rel + ": mutates a tank outside the transfer service at " + Line(src, at));
                    }
                foreach (string c in new[] { "RM_LiquidNet.Credit(", "CreditRoute(", "CreditTo(" })
                    foreach (int at in Occurrences(src, c))
                    {
                        if (defs.Any(d => at >= d.a && at <= d.b)) continue;
                        credits++;
                        if (!blocks.Any(s => at > s.a && at < s.b)) bad.Add(rel + ": hose credit outside a committed-Move block at " + Line(src, at));
                    }
            }
            foreach (KeyValuePair<string, int> t in tags)
                if (t.Value != 1 && files.Keys.Any(k => k.StartsWith("//tags:"))) bad.Add("tag '" + t.Key + "' found " + t.Value + "x");
            return bad;
        }

        private static IEnumerable<int> Occurrences(string s, string needle)
        {
            for (int i = s.IndexOf(needle, StringComparison.Ordinal); i >= 0; i = s.IndexOf(needle, i + 1, StringComparison.Ordinal)) yield return i;
        }

        private static int Line(string s, int at) => s.Take(at).Count(ch => ch == '\n') + 1;

        /// <summary>The argument spans of every call matching <paramref name="opener"/> (which ends at its '(').</summary>
        private static List<(int a, int b)> Spans(string src, string opener)
        {
            var spans = new List<(int, int)>();
            foreach (Match m in Regex.Matches(src, opener))
            {
                int open = m.Index + m.Length - 1;
                int close = Match(src, open, '(', ')');
                if (close > open) spans.Add((open, close));
            }
            return spans;
        }

        /// <summary>The { } block right after `if (RM_LiquidTransfer.Move(n, ...) == n)` or `... > 0)`: where a committed move may credit.
        /// TRANSFER_LINT_HARDEN_REFUSED_CREDIT_PASSES (Codex rev_i): the whole condition is read, not a prefix of it. A committed
        /// guard is the Move call and one comparison, `== n` (n = Move's own first argument) or `> 0`, nothing else: `== 0` is the
        /// REFUSAL (Move returns 0 on every refusal), and `== other` or `== n || x` commits nothing. A refusal branch,
        /// `if (Move(n, ...) != n) { ... return ...; }`, makes the
        /// rest of its method committed only when its LAST top-level statement is a return; a return nested in an inner if lets a
        /// refused move fall through to the credit.</summary>
        private static List<(int a, int b)> CommittedBlocks(string src)
        {
            var blocks = new List<(int, int)>();
            foreach (Match m in Regex.Matches(src, @"if\s*\(\s*RM_LiquidTransfer\.Move\("))
            {
                int open = src.IndexOf('(', m.Index);
                int close = Match(src, open, '(', ')');
                int moveOpen = m.Index + m.Length - 1;
                int moveClose = Match(src, moveOpen, '(', ')');
                if (close < 0 || moveClose < 0 || moveClose > close) continue;
                string tail = src.Substring(moveClose + 1, close - moveClose - 1).Trim();
                // `== x` / `!= x` compare against what was asked for: Move's own first argument (review: `== none` with none = 0
                // is the refusal again under another name)
                string asked = Regex.Replace(FirstArg(src, moveOpen, moveClose), @"\s+", "");
                Match eq = Regex.Match(tail, @"^(==|!=)\s*(.+)$");
                bool same = eq.Success && asked.Length > 0 && Regex.Replace(eq.Groups[2].Value, @"\s+", "") == asked;
                bool committed = Regex.IsMatch(tail, @"^>\s*0$") || (same && eq.Groups[1].Value == "==");
                bool refusal = same && eq.Groups[1].Value == "!=";
                if (!committed && !refusal) continue;
                int brace = src.IndexOf('{', close);
                if (brace < 0 || src.Substring(close + 1, brace - close - 1).Trim().Length > 0) continue;
                int end = Match(src, brace, '{', '}');
                if (end <= brace) continue;
                if (committed) { blocks.Add((brace, end)); continue; }
                if (!EndsInReturn(src.Substring(brace + 1, end - brace - 1))) continue;
                // the refusal branch returns, so the rest of its enclosing block is committed: up to the next "}" at a lower depth
                int depth = 0, i = end + 1;
                for (; i < src.Length; i++)
                {
                    if (src[i] == '{') depth++;
                    else if (src[i] == '}') { if (depth == 0) break; depth--; }
                }
                blocks.Add((end, i));
            }
            return blocks;
        }

        /// <summary>The text of a call's first argument: from just after its '(' at <paramref name="open"/> to the first ',' at its own
        /// depth (or its ')'), strings and char literals skipped.</summary>
        private static string FirstArg(string s, int open, int close)
        {
            int depth = 0;
            for (int i = open + 1; i < close; i++)
            {
                char ch = s[i];
                if (ch == '"') { for (i++; i < close && s[i] != '"'; i++) if (s[i] == '\\') i++; continue; }
                if (ch == '\'' && i + 2 < close) { i += s[i + 1] == '\\' ? 3 : 2; continue; }
                if (ch == '(' || ch == '[' || ch == '{') depth++;
                else if (ch == ')' || ch == ']' || ch == '}') depth--;
                else if (ch == ',' && depth == 0) return s.Substring(open + 1, i - open - 1).Trim();
            }
            return s.Substring(open + 1, close - open - 1).Trim();
        }

        /// <summary>True when a block body's last top-level statement is `return ...;` (nested blocks are read as "{}", so a
        /// return inside an inner if or loop does not count, nor does `if (x) return;`).</summary>
        internal static bool EndsInReturn(string body)
        {
            var top = new System.Text.StringBuilder();
            int depth = 0;
            for (int i = 0; i < body.Length; i++)
            {
                char ch = body[i];
                if (ch == '"')
                {
                    int j = i + 1;
                    for (; j < body.Length && body[j] != '"'; j++) if (body[j] == '\\') j++;
                    if (depth == 0) top.Append("\"\"");
                    i = j;
                    continue;
                }
                if (ch == '\'' && i + 2 < body.Length) { i += body[i + 1] == '\\' ? 3 : 2; continue; }   // review: '}' is no brace
                if (ch == '{') { if (depth++ == 0) top.Append('{'); continue; }
                if (ch == '}') { if (--depth == 0) top.Append('}'); continue; }
                if (depth == 0) top.Append(ch);
            }
            return Regex.IsMatch(top.ToString(), @"(^|[;}])\s*return\b[^;{}]*;\s*$");
        }

        private static int Match(string s, int open, char o, char c)
        {
            int depth = 0;
            for (int i = open; i < s.Length; i++)
            {
                char ch = s[i];
                if (ch == '"')
                {
                    for (i++; i < s.Length && s[i] != '"'; i++) if (s[i] == '\\') i++;
                    continue;
                }
                if (ch == '\'' && i + 2 < s.Length)
                {
                    i += s[i + 1] == '\\' ? 3 : 2;
                    continue;
                }
                if (ch == o) depth++;
                else if (ch == c && --depth == 0) return i;
            }
            return -1;
        }

        /// <summary>Production source with // and /* */ comments blanked (lengths kept, so positions and lines stay true).</summary>
        internal static string StripComments(string s, out int stripped)
        {
            var sb = new System.Text.StringBuilder(s);
            stripped = 0;
            for (int i = 0; i < s.Length; i++)
            {
                if (s[i] == '"')
                {
                    if (i > 0 && s[i - 1] == '@') { for (i++; i < s.Length && !(s[i] == '"' && (i + 1 >= s.Length || s[i + 1] != '"')); i++) if (s[i] == '"') i++; continue; }
                    for (i++; i < s.Length && s[i] != '"'; i++) if (s[i] == '\\') i++;
                    continue;
                }
                if (s[i] == '\'' && i + 2 < s.Length) { i += s[i + 1] == '\\' ? 3 : 2; continue; }
                if (s[i] == '/' && i + 1 < s.Length && s[i + 1] == '/')
                {
                    for (; i < s.Length && s[i] != '\n'; i++) { sb[i] = ' '; stripped++; }
                    continue;
                }
                if (s[i] == '/' && i + 1 < s.Length && s[i + 1] == '*')
                {
                    for (; i + 1 < s.Length && !(s[i] == '*' && s[i + 1] == '/'); i++) if (s[i] != '\n') sb[i] = ' ';
                    if (i + 1 < s.Length) { sb[i] = ' '; sb[i + 1] = ' '; i++; }
                }
            }
            return sb.ToString();
        }
    }
}
