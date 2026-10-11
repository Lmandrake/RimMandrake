// Verse-free (the FlowWorks SelfTest compiles this file): P3 (hose port step 5; GPT review G1.16) -- a liquid-bath craft
// either PAYS for its liquid or does not complete. The completion hook used to look the source up again and silently skip
// the debit when the tank had been drained or disconnected mid-craft, so the product was made for nothing.
namespace RimMandrake.FlowWorks.Machinery.Kits
{
    public enum RM_BathPay { NoNeed, Ground, Tank, Unpaid }

    public static class RM_LiquidBathMath
    {
        /// <summary>What one craft of a bath bill owes right now. NoNeed: the setting is off or the recipe draws nothing;
        /// Ground: the bench stands by the liquid's own ground (never drawn down); Tank: a tank on the net holds a full
        /// craft's units; Unpaid: neither -- the craft must not complete (its job fails while this holds).</summary>
        public static RM_BathPay Pay(bool settingOn, int unitsPerCraft, bool groundSource, int bestTankUnits)
        {
            if (!settingOn || unitsPerCraft <= 0) return RM_BathPay.NoNeed;
            if (groundSource) return RM_BathPay.Ground;
            return bestTankUnits >= unitsPerCraft ? RM_BathPay.Tank : RM_BathPay.Unpaid;
        }

        /// <summary>The job doing the bill keeps working only while the craft can be paid for.</summary>
        public static bool MayKeepWorking(RM_BathPay pay) => pay != RM_BathPay.Unpaid;
    }
}
