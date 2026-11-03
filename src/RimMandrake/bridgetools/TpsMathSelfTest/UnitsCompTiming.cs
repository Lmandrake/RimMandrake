// jawa/game_comp_timing bookkeeping (GAMECOMP_STALL_HUNT_SEVEN_SECONDS): the PRODUCTION JawaBenchCompTimingCore
// driven with the shapes the item names - a one-off 6.76 s call among cheap ones, a stall 18 ticks after a load,
// many spikes overflowing the kept list, and the roll-up by owning mod.
using System.Collections.Generic;
using C = JawaBench.BridgeTools.JawaBenchCompTimingCore<string>;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void T_CompTimingOneOffSpikeIsNamedNotDrowned()
        {
            var c = new C(spikeThreshold: 250, spikeCap: 8);   // units: ms here
            var g = new object(); c.Arm(g);
            for (int t = 7000; t < 7600; t++)
            {
                c.NoteTick(g, t);
                c.Add("Busy", 2, t);
                c.Add("Stall", t == 7501 ? 6760 : 0, t);
            }
            Check(c.TicksObserved == 600 && c.Loads == 0, "600 ticks, no load: " + c.TicksObserved + "/" + c.Loads);
            Check(c.SpikesSeen == 1 && c.Spikes.Count == 1, "exactly one spike: " + c.SpikesSeen);
            var s = c.RankedSpikes()[0];
            Check(s.Key == "Stall" && s.Dur == 6760 && s.Tick == 7501 && s.SinceLoad == -1 && s.Load == 0,
                "spike names the component, duration and tick, no load seen: " + s.Key + " " + s.Dur + " " + s.Tick + " " + s.SinceLoad);
            var r = c.Rows["Stall"];
            Check(r.Max == 6760 && r.MaxAtTick == 7501 && r.Calls == 600, "row max and its tick: " + r.Max + "@" + r.MaxAtTick);
            Check(c.Ranked()[0].Key == "Stall", "the stall's total outranks the steady 2/tick component");
        }

        private static void T_CompTimingStallAfterLoadCarriesSinceLoad()
        {
            var c = new C(100, 4);
            var g1 = new object(); c.Arm(g1);
            for (int t = 100; t < 110; t++) { c.NoteTick(g1, t); c.Add("A", 1, t); }
            var g2 = new object();                               // the save is reloaded while armed
            for (int t = 5803; t < 5830; t++) { c.NoteTick(g2, t); c.Add("A", t == 5821 ? 2880 : 1, t); }
            Check(c.Loads == 1, "one load seen: " + c.Loads);
            Check(c.TicksObserved == 37, "ticks summed across both games: " + c.TicksObserved);
            var s = c.RankedSpikes()[0];
            Check(s.SinceLoad == 18 && s.Load == 1 && s.Tick == 5821, "the post-load stall reads 18 ticks after load 1: " + s.SinceLoad + " load " + s.Load);
        }

        private static void T_CompTimingArmedAtMenuFirstGameIsALoad()
        {
            var c = new C(10, 4);
            c.Arm(null);                                         // armed at the menu / mid-load
            var g = new object();
            c.NoteTick(g, 0); c.NoteTick(g, 0); c.NoteTick(g, 1);
            c.Add("X", 50, 1);
            Check(c.Loads == 1 && c.TicksObserved == 2, "first game after a menu arm is load 1; repeated tick counted once: " + c.Loads + "/" + c.TicksObserved);
            Check(c.Spikes[0].SinceLoad == 1, "since load from the first tick seen: " + c.Spikes[0].SinceLoad);
        }

        private static void T_CompTimingSpikeCapKeepsLargest()
        {
            var c = new C(10, 3);
            c.Arm(new object());
            long[] durs = { 11, 50, 12, 90, 13, 70, 10, 9 };
            for (int i = 0; i < durs.Length; i++) c.Add("K" + i, durs[i], i);
            Check(c.SpikesSeen == 7, "threshold is inclusive (10 counts, 9 does not): " + c.SpikesSeen);
            var kept = c.RankedSpikes();
            Check(kept.Count == 3 && kept[0].Dur == 90 && kept[1].Dur == 70 && kept[2].Dur == 50,
                "the three largest are kept, largest first: " + string.Join(",", kept.ConvertAll(k => k.Dur.ToString())));
            var none = new C(0, 3); none.Add("A", 1000, 0);
            Check(none.SpikesSeen == 0 && none.Spikes.Count == 0, "threshold 0 records no spikes");
            var nokeep = new C(5, 0); nokeep.Add("A", 1000, 0);
            Check(nokeep.SpikesSeen == 1 && nokeep.Spikes.Count == 0, "cap 0 counts but keeps none");
        }

        private static void T_CompTimingRollsUpByOwner()
        {
            var c = new C(0, 0);
            c.Add("ModA.One", 30, 0); c.Add("ModA.Two", 25, 0); c.Add("ModB.Big", 40, 0); c.Add("Loose", 5, 0);
            c.Add("ModA.One", -7, 1);                            // a negative clock delta clamps to 0
            var owners = new Dictionary<string, string> { ["ModA.One"] = "mod.a", ["ModA.Two"] = "mod.a", ["ModB.Big"] = "mod.b" };
            var by = c.ByOwner(k => owners.TryGetValue(k, out var o) ? o : null);
            Check(by.Count == 3, "three owners incl. ?: " + by.Count);
            Check(by[0].Owner == "mod.a" && by[0].Total == 55 && by[0].Keys == 2 && by[0].Calls == 3 && by[0].Max == 30,
                "mod.a sums its two components: " + by[0].Owner + " " + by[0].Total + " keys " + by[0].Keys + " calls " + by[0].Calls);
            Check(by[1].Owner == "mod.b" && by[2].Owner == "?" && by[2].Total == 5, "unknown owner reads ?: " + by[2].Owner);
            Check(c.Rows["ModA.One"].Total == 30 && c.Rows["ModA.One"].Max == 30, "clamped delta adds nothing");
        }

        private static void T_CompTimingStageMaxNamesItsOwnComponent()
        {
            var c = new C(100, 8);
            var g = new object(); c.Arm(g);
            // tick 7400: a 5000 component spike inside a 5010 stage call; tick 7501: a 6760 stage call whose biggest
            // component is only 40 (the rest ran outside any timed override). The worst stage must NOT be credited to
            // the unrelated tick-7400 spike.
            c.NoteTick(g, 7400); c.StageBegin(); c.Add("Early", 5000, 7400); c.Add("Small", 3, 7400); c.StageEnd(5010, 7400);
            c.NoteTick(g, 7501); c.StageBegin(); c.Add("Small", 40, 7501); c.Add("Tiny", 1, 7501); c.StageEnd(6760, 7501);
            c.NoteTick(g, 7502); c.StageBegin(); c.StageEnd(2, 7502);
            Check(c.StageMaxSinceLoad == -1, "no load seen: stage max since-load is -1: " + c.StageMaxSinceLoad);
            Check(c.StageMax == 6760 && c.StageMaxAtTick == 7501 && c.StageMaxLoad == 0, "worst stage call kept: " + c.StageMax + "@" + c.StageMaxAtTick);
            Check(c.StageMaxTop == "Small" && c.StageMaxTopDur == 40, "its top component is the one inside it: " + c.StageMaxTop + " " + c.StageMaxTopDur);
            c.Add("Outside", 9000, 7503);                        // a call outside any stage changes no stage attribution
            Check(c.StageMaxTop == "Small", "a call outside a stage is not attributed");
            c.StageEnd(99999, 7504);                             // an end without a begin is ignored
            Check(c.StageMax == 6760, "unpaired StageEnd ignored: " + c.StageMax);
            var g2 = new object();
            c.NoteTick(g2, 5803); c.StageBegin(); c.StageEnd(1, 5803);
            c.NoteTick(g2, 5821); c.StageBegin(); c.Add("PostLoad", 7000, 5821); c.StageEnd(7100, 5821);
            Check(c.StageMax == 7100 && c.StageMaxLoad == 1 && c.StageMaxSinceLoad == 18 && c.StageMaxTop == "PostLoad",
                "post-load worst stage: load 1, 18 ticks after it, its own component: " + c.StageMaxLoad + " " + c.StageMaxSinceLoad + " " + c.StageMaxTop);
            var e = new C(0, 0); e.Arm(g);
            e.NoteTick(g, 1); e.StageBegin(); e.StageEnd(50, 1);
            Check(e.StageMaxTopDur == -1 && e.StageMaxTop == null, "a stage with no timed component reads -1/null");
        }
    }
}
