// Verse-free kernel of the Rite of Tipping contract (QuestPart_RM_TippingContract in RM_RiteOfTipping.cs): the delivery
// state machine (pad present / missed / fail / complete), the one-shot evidence ask and finance grant, the schedule, and
// the reburial discovery roll. The quest part calls these with the same expressions; SelfTest/WastelandFuzz.cs
// compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.Wasteland
{
    public enum FinanceStep { None = 0, Hint = 1, Grant = 2 }

    public struct TippingState
    {
        public int deliveriesDone;
        public int missed;
        public bool evidenceAsked;
        public bool financeGranted;
        public bool financeHinted;
        public bool active;       // QuestPartState.Enabled
    }

    public struct TippingResult
    {
        public bool delivered;
        public bool failed;
        public bool completed;
        public bool askEvidence;
        public FinanceStep finance;
        public int convoyGoodwill;   // total goodwill change with the convoy this step
    }

    public static class RM_TippingKernel
    {
        public const int MissedGoodwill = -5;

        // Silver the convoy pays per delivery.
        public static int SilverPerDelivery(int casksPerDelivery, int silverPerCask) { return casksPerDelivery * silverPerCask; }

        // Delivery fires when the clock reaches the scheduled tick; the next is the interval later.
        public static bool DeliveryDue(int now, int nextDeliveryTick) { return now >= nextDeliveryTick; }
        public static int NextDelivery(int now, float intervalDays, int ticksPerDay) { return now + (int)Math.Round(intervalDays * ticksPerDay); }

        // The contract voids itself when the map or convoy is gone or the convoy turned hostile.
        public static bool ContractVoid(bool hasMap, bool hasConvoy, bool convoyHostile) { return !hasMap || !hasConvoy || convoyHostile; }

        public static FinanceStep FinanceOffer(bool granted, bool hasFinanceFaction, bool financeUsable, bool bayStanding, bool hinted)
        {
            if (granted || !hasFinanceFaction || !financeUsable) return FinanceStep.None;
            if (!bayStanding) return hinted ? FinanceStep.None : FinanceStep.Hint;
            return FinanceStep.Grant;
        }

        // One convoy load. Mutates the state exactly as the quest part does.
        public static TippingResult Deliver(ref TippingState s, bool padPresent, bool hasEvidenceFaction, bool evidenceUsable,
                                            bool hasFinanceFaction, bool financeUsable, bool bayStanding,
                                            int goodwillPerDelivery, int deliveriesTotal, int missedAllowed)
        {
            var r = new TippingResult();
            if (!s.active) return r;                      // a finished contract delivers nothing
            if (!padPresent)
            {
                s.missed++;
                r.convoyGoodwill = MissedGoodwill;
                if (s.missed > missedAllowed) { r.failed = true; s.active = false; }
                return r;
            }
            r.convoyGoodwill = goodwillPerDelivery;
            s.deliveriesDone++;
            r.delivered = true;
            if (!s.evidenceAsked && hasEvidenceFaction && evidenceUsable) { s.evidenceAsked = true; r.askEvidence = true; }
            r.finance = FinanceOffer(s.financeGranted, hasFinanceFaction, financeUsable, bayStanding, s.financeHinted);
            if (r.finance == FinanceStep.Grant) s.financeGranted = true;
            else if (r.finance == FinanceStep.Hint) s.financeHinted = true;
            if (s.deliveriesDone >= deliveriesTotal) { r.completed = true; s.active = false; }
            return r;
        }

        // Rand.Chance(c): false at <= 0, true at >= 1, else value < c.
        public static bool Chance(float c, float value) { return c > 0f && (c >= 1f || value < c); }

        // Illegal reburial: each usable faction (evidence, finance) independently discovers it.
        public static bool Discovers(bool hasFaction, bool usable, float chance, Func<float> roll) { return hasFaction && usable && Chance(chance, roll()); }
    }
}
