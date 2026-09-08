using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.DroidRepairJobs
{
    /// <summary>
    /// DROID_REPAIR_FOR_PROFIT_EVENTS_1 (packet C5). Grades the work at pickup
    /// time and pays for it.
    ///
    /// The grade is read off the droid itself: Droidworks' own
    /// Recipe_InstallDroidPart grants one of an Inferior / Standard / Superior
    /// hediff per fitted part, keyed to that part item's CompQuality, and
    /// replaces any earlier tier in the same slot. So "which quality of part did
    /// the Jawa fit" is already recorded on the pawn - this part only reads it.
    ///
    /// Best tier present wins. Fitting one excellent part is not a cheat: the
    /// recipe consumed a real excellent part out of the player's own stores,
    /// which is exactly the trade the packet asks the player to make.
    /// </summary>
    public class QuestPart_DroidRepairJobOutcome : QuestPart
    {
        public string inSignal;

        public List<Pawn> droids = new List<Pawn>();

        public Faction customer;

        public MapParent mapParent;

        public HediffDef faultHediff;

        public List<HediffDef> inferiorHediffs = new List<HediffDef>();

        public List<HediffDef> standardHediffs = new List<HediffDef>();

        public List<HediffDef> superiorHediffs = new List<HediffDef>();

        public int payFine;

        public int payHonest;

        public int payShoddy;

        public string outSignalFine;

        public string outSignalHonest;

        public string outSignalShoddy;

        public string outSignalNeglected;

        private const int TierNeglected = 0;
        private const int TierShoddy = 1;
        private const int TierHonest = 2;
        private const int TierFine = 3;

        public override IEnumerable<GlobalTargetInfo> QuestLookTargets
        {
            get
            {
                foreach (GlobalTargetInfo t in base.QuestLookTargets)
                {
                    yield return t;
                }
                for (int i = 0; i < droids.Count; i++)
                {
                    if (droids[i] != null) yield return droids[i];
                }
            }
        }

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (signal.tag != inSignal) return;

            Pawn droid = droids.FirstOrDefault(p => p != null && !p.Dead && p.health != null);
            int tier = TierNeglected;

            if (droid != null)
            {
                HediffSet set = droid.health.hediffSet;
                if (HasAnyOf(set, superiorHediffs)) tier = TierFine;
                else if (HasAnyOf(set, standardHediffs)) tier = TierHonest;
                else if (HasAnyOf(set, inferiorHediffs)) tier = TierShoddy;

                // Any part at all gets it walking again; the fault is the thing
                // the customer brought it in for.
                if (tier != TierNeglected && faultHediff != null)
                {
                    Hediff fault = set.GetFirstHediffOfDef(faultHediff);
                    if (fault != null) droid.health.RemoveHediff(fault);
                }
            }

            int pay;
            string outSignal;
            switch (tier)
            {
                case TierFine:
                    pay = payFine;
                    outSignal = outSignalFine;
                    break;
                case TierHonest:
                    pay = payHonest;
                    outSignal = outSignalHonest;
                    break;
                case TierShoddy:
                    pay = payShoddy;
                    outSignal = outSignalShoddy;
                    break;
                default:
                    pay = 0;
                    outSignal = outSignalNeglected;
                    break;
            }

            if (pay > 0) PaySilver(pay);
            if (!outSignal.NullOrEmpty())
            {
                Find.SignalManager.SendSignal(new Signal(outSignal));
            }
        }

        private static bool HasAnyOf(HediffSet set, List<HediffDef> defs)
        {
            if (set == null || defs == null) return false;
            for (int i = 0; i < defs.Count; i++)
            {
                if (defs[i] != null && set.HasHediff(defs[i])) return true;
            }
            return false;
        }

        private void PaySilver(int amount)
        {
            Map map = mapParent?.Map;
            if (map == null || amount <= 0) return;

            List<Thing> stacks = new List<Thing>();
            int left = amount;
            int limit = Mathf.Max(1, ThingDefOf.Silver.stackLimit);
            while (left > 0)
            {
                Thing silver = ThingMaker.MakeThing(ThingDefOf.Silver);
                silver.stackCount = Mathf.Min(left, limit);
                left -= silver.stackCount;
                stacks.Add(silver);
            }

            IntVec3 spot = DropCellFinder.TradeDropSpot(map);
            DropPodUtility.DropThingsNear(spot, map, stacks, 110, canInstaDropDuringInit: false,
                                          leaveSlag: false, canRoofPunch: false, forbid: false,
                                          allowFogged: false, faction: customer);
        }

        public override void Notify_FactionRemoved(Faction f)
        {
            if (customer == f) customer = null;
        }

        public override void ReplacePawnReferences(Pawn replace, Pawn with)
        {
            droids.Replace(replace, with);
        }

        public override bool QuestPartReserves(Pawn p)
        {
            return droids.Contains(p);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Collections.Look(ref droids, "droids", LookMode.Reference);
            Scribe_References.Look(ref customer, "customer");
            Scribe_References.Look(ref mapParent, "mapParent");
            Scribe_Defs.Look(ref faultHediff, "faultHediff");
            Scribe_Collections.Look(ref inferiorHediffs, "inferiorHediffs", LookMode.Def);
            Scribe_Collections.Look(ref standardHediffs, "standardHediffs", LookMode.Def);
            Scribe_Collections.Look(ref superiorHediffs, "superiorHediffs", LookMode.Def);
            Scribe_Values.Look(ref payFine, "payFine", 0);
            Scribe_Values.Look(ref payHonest, "payHonest", 0);
            Scribe_Values.Look(ref payShoddy, "payShoddy", 0);
            Scribe_Values.Look(ref outSignalFine, "outSignalFine");
            Scribe_Values.Look(ref outSignalHonest, "outSignalHonest");
            Scribe_Values.Look(ref outSignalShoddy, "outSignalShoddy");
            Scribe_Values.Look(ref outSignalNeglected, "outSignalNeglected");

            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (droids == null) droids = new List<Pawn>();
                if (inferiorHediffs == null) inferiorHediffs = new List<HediffDef>();
                if (standardHediffs == null) standardHediffs = new List<HediffDef>();
                if (superiorHediffs == null) superiorHediffs = new List<HediffDef>();
                droids.RemoveAll((Pawn x) => x == null);
            }
        }
    }
}
