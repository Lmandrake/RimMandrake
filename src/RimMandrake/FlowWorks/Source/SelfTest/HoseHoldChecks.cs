// Liquid networks build step L8 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md rev 2 §3.7, §6 L8; owner Q2
// ruled REAL, "and you have to have colonists "clean it up" if it's in a cleanable area"): a hose holds a little liquid while it
// carries and empties it out of its open end when it stops. On the PRODUCTION ledger (RM_LiquidNetKernel.cs RM_HoseHold) and
// transfer service, then the production fill, flush and drain read from source. Gates: conservation across fill, liquid change
// and stop; save keys. The live bar "filth in the home area gets a Clean job" is owed to a bridge session.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class HoseHoldChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("HoseHold_capacity_is_cells_times_units_per_cell", () =>
            {
                Assert(RM_HoseHold.Capacity(30, 0.2f) == 6 && RM_HoseHold.Capacity(31, 0.2f) == 7 && RM_HoseHold.Capacity(0, 0.2f) == 0 && RM_HoseHold.Capacity(30, 0f) == 0,
                    "a 30-cell hose holds 6, a 31-cell one 7 (rounded up); none when off");
            });

            Case("HoseHold_conserves_across_fill_change_of_liquid_and_stop", () =>
            {
                // two tanks of two liquids, one hose between them: random moves (each fills the hose out of its own tank), random
                // stops (the hose empties into the world); per liquid, tanks + held + spilled never changes
                var rnd = new Random(8);
                for (int trial = 0; trial < 200; trial++)
                {
                    var tanks = new Dictionary<string, int> { { "water", 200 }, { "tar", 200 } };
                    var spilled = new Dictionary<string, int> { { "water", 0 }, { "tar", 0 } };
                    var consumed = new Dictionary<string, int> { { "water", 0 }, { "tar", 0 } };
                    object heldLiquid = null;
                    int held = 0, cap = 1 + rnd.Next(12);
                    for (int step = 0; step < 40; step++)
                    {
                        if (rnd.Next(5) == 0)
                        {
                            RM_HoseHold.Drain(ref heldLiquid, ref held, (l, u) => spilled[(string)l] += u);
                            continue;
                        }
                        string liq = rnd.Next(2) == 0 ? "water" : "tar";
                        int moved = rnd.Next(1, 6);
                        if (tanks[liq] < moved) continue;
                        tanks[liq] -= moved;   // the committed move itself (tank to a machine, say)
                        consumed[liq] += moved;
                        int t0 = tanks[liq];
                        int got = RM_HoseHold.Fill(ref heldLiquid, ref held, cap, liq,
                            n => { int k = Math.Min(n, tanks[liq]); tanks[liq] -= k; return k; },
                            (l, u) => spilled[(string)l] += u);
                        Assert(got == t0 - tanks[liq], "trial " + trial + ": the fill took exactly what the tank gave");
                    }
                    foreach (string l in new[] { "water", "tar" })
                    {
                        int inHose = Equals(heldLiquid, l) ? held : 0;
                        Assert(tanks[l] + inHose + spilled[l] + consumed[l] == 200,
                            "trial " + trial + " " + l + ": tanks " + tanks[l] + " + hose " + inHose + " + spilled " + spilled[l] + " + used " + consumed[l] + " != 200");
                    }
                    Assert(held <= cap && (held == 0) == (heldLiquid == null), "trial " + trial + ": held within capacity, one liquid");
                }
            });

            Case("HoseHold_change_of_liquid_flushes_first", () =>
            {
                object hl = "tar";
                int held = 6, flushed = 0, taken = 0;
                object flushedLiquid = null;
                RM_HoseHold.Fill(ref hl, ref held, 6, "water", n => { taken += n; return n; }, (l, u) => { flushedLiquid = l; flushed += u; });
                Assert(Equals(flushedLiquid, "tar") && flushed == 6 && Equals(hl, "water") && held == 6 && taken == 6,
                    "tar held, water crosses: the 6 tar leave first, then 6 water fill it (" + flushed + "/" + held + ")");
                object h2 = "water";
                int k2 = 4, f2 = 0;
                RM_HoseHold.Fill(ref h2, ref k2, 6, "water", n => n, (l, u) => f2 += u);
                Assert(f2 == 0 && k2 == 6, "the same liquid: no flush, topped up");
                Assert(RM_HoseHold.ShouldDrain(5, true, true, false) && RM_HoseHold.ShouldDrain(5, true, false, true) && RM_HoseHold.ShouldDrain(5, false, true, true)
                       && !RM_HoseHold.ShouldDrain(5, true, true, true) && !RM_HoseHold.ShouldDrain(0, false, false, false),
                    "a hose drains when holding is off, it is not live, or its lease ran out; never when it carries or holds nothing");
            });

            Case("HoseHold_production_fill_flush_drain_and_save", () =>
            {
                string reel = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "CompHoseReel.cs"));
                RiverSwitchFlipChecks.Has(reel, @"Scribe_Defs\.Look\(ref heldLiquid, ""rmHoseHeldLiquid""\); Scribe_Values\.Look\(ref heldUnits, ""rmHoseHeldUnits"", 0\);", "saved as rmHoseHeldLiquid / rmHoseHeldUnits");
                RiverSwitchFlipChecks.Has(reel, @"if \(Scribe\.mode == LoadSaveMode\.PostLoadInit && heldLiquid == null && heldUnits > 0\) \{[^}]*Log\.Warning\([^}]*heldUnits = 0;", "an unknown held liquid is cleared with one warning");
                RiverSwitchFlipChecks.Has(reel, @"public int HeldCap => RM_HoseSettings\.hoseHoldsLiquid && lay != null \? Machinery\.RM_HoseHold\.Capacity\(lay\.FlatLen, RM_HoseSettings\.HoseUnitsPerCell\) : 0;", "capacity from the laid length");
                RiverSwitchFlipChecks.Has(reel, @"base\.PostDeSpawn\(map, mode\); // [^\n]*?Machinery\.RM_LiquidSpill\.DrainHeld\(this, map, parent\.Position\);", "a packed-up or destroyed reel empties where it stood");
                string net = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidNet.cs"));
                RiverSwitchFlipChecks.Has(net, @"CreditRoute\(origin\.Map, route, liquid, units, cadence, FillFrom\(tank, liquid\)\);", "a tank-leg credit fills its hoses out of that tank");
                RiverSwitchFlipChecks.Has(net, @"RM_LiquidTransfer\.Move\(k, RM_TransferLeg\.Store\(j => tank\.CanProvide\(j\), j => tank\.TryRemoveLiquid\(j\), j => tank\.TryAddLiquid\(liquid, j\)\), RM_TransferLeg\.Sink\(null\), out _\)",
                    "the fill leaves the tank through the transfer service");
                RiverSwitchFlipChecks.Has(net, @"if \(RM_HoseSettings\.hoseHoldsLiquid && fillFrom != null\)", "no fill with holding off");
                RiverSwitchFlipChecks.Has(net, @"RM_HoseHold\.Fill\(ref hl, ref held, r\.HeldCap, liquid, take, \(old, u\) => \{[^}]*RM_LiquidSpill\.DrainHeld\(r, map, RM_LiquidSpill\.DrainCell\(r, map\)\);", "a change of liquid flushes the old one out of the far end");
                string sp = RiverSwitchFlipChecks.Src(Path.Combine("Machinery", "RM_LiquidSpill.cs"));
                RiverSwitchFlipChecks.Has(sp, @"RM_TransferLeg world = RM_TransferLeg\.Sink\(k => PlaceHeld\(map, ex, cell, liquid, k\)\);", "a drain goes to the world, never a tank");
                RiverSwitchFlipChecks.Has(sp, @"units -= PlaceInWater\(map, ex, cell, liquid, units\); if \(units > 0\) \{ Spill\(map, cell, liquid, units\); \}[\s\S]*bool ok = kind == RM_OutletKind\.Channel \? ex\.TryPourDl\(c, fluid, room\) : BodyTake\(ex, c, fluid, room\);",
                    "whole levels into a channel (or back into a pond) that takes them, the rest spilled");
                string hoses = RiverSwitchFlipChecks.Src(Path.Combine("Hose", "RM_MapComponent_Hoses.cs"));
                RiverSwitchFlipChecks.Has(hoses, @"RimMandrake\.FlowWorks\.Machinery\.RM_HoseHold\.ShouldDrain\(r\.heldUnits, RM_HoseSettings\.hoseHoldsLiquid, RimMandrake\.FlowWorks\.Machinery\.RM_HoseLinks\.Eligible\(r\), RimMandrake\.FlowWorks\.Machinery\.RM_LiquidNetKernel\.Flowing\(r\.flowUntil, now\)\)\)",
                    "every pump cycle a stopped hose empties");
                string pump = RiverSwitchFlipChecks.Src(Path.Combine("LiquidTypes", "Building_LiquidPump.cs"));
                RiverSwitchFlipChecks.Has(pump, @"RM_TransferLeg into = fillHoses \? RM_TransferLeg\.Sink\(k => RM_LiquidNet\.FillRoutes\(this, new object\[\] \{ s\.port, port \}, l, k\)\)", "world to world: the first levels fill the hoses");
            });
        }
    }
}
