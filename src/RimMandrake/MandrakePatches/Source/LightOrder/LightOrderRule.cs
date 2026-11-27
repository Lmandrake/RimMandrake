namespace RimMandrake.Patches
{
    // RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS (owner, 2026-11-25: "this should be a generic capability all
    // colonists have for anything flammable, at the RimMandrake level"). The one decision of the right-click "Set fire to ..."
    // order, kept free of Verse so Scenario/LightOrder can run it offline. LightOrder.cs reads each fact from the game and
    // hands it over; the thresholds stay vanilla's own (Thing.FlammableNow, FireUtility.ChanceToStartFireIn).
    //
    // Who may light: every player-controlled colonist (slaves included, drafted or not) who is standing and can use hands.
    // Being incapable of violence or of firefighting does not stop it: the target is never a living pawn, and the owner asked
    // for a capability ALL colonists have (a pyromaniac, the likeliest to want it, is incapable of firefighting).
    public enum LightVerdict
    {
        None,       // no menu line at all
        Disabled,   // a greyed line with the reason
        Offer,      // the order
    }

    public struct LightFacts
    {
        public bool OrderOn;            // Mod Settings: the order is on (default on)
        public bool PlantsOn;           // Mod Settings: plants are offered too (default off)
        public bool PawnControllable;   // Pawn.IsColonistPlayerControlled
        public bool PawnDowned;
        public bool PawnHasHands;       // capable of Manipulation
        public bool TargetIsPawn;       // a living pawn (a corpse is a Thing, not this)
        public bool TargetIsPlant;
        public bool TargetIsFire;       // the Fire thing itself
        public bool FlammableNow;       // Thing.FlammableNow: Flammability >= 0.01 and no fire bulwark on its square
        public bool Burning;            // FireUtility.IsBurning
        public bool CellTakesFire;      // one of its squares has FireUtility.ChanceToStartFireIn > 0 (no fire foam, no fire)
        public bool Reachable;          // the colonist can reach touch range
        public bool OtherModCellLine;   // FlowWorks offers its own "Toss a flame here" on the clicked square
    }

    public static class LightOrderRule
    {
        public static LightVerdict Decide(LightFacts f, out string reason)
        {
            reason = Hidden(f);
            if (reason != null)
                return LightVerdict.None;
            if (!f.PawnHasHands)
                reason = "cannot use hands";
            else if (!f.CellTakesFire)
                reason = "nothing there will catch";
            else if (!f.Reachable)
                reason = "no path";
            return reason == null ? LightVerdict.Offer : LightVerdict.Disabled;
        }

        // Why there is no line at all, or null. A line on every steel wall, rock or living pawn would be noise (vanilla shows
        // none for a thing that cannot be acted on); a plant line would sit on nearly every outdoor click and turn one
        // misclick into a wildfire, so plants wait behind their own switch.
        private static string Hidden(LightFacts f)
        {
            if (!f.OrderOn) return "switched off in Mod Settings";
            if (!f.PawnControllable) return "not a player-controlled colonist";
            if (f.PawnDowned) return "downed";
            if (f.TargetIsPawn) return "a living pawn";
            if (f.TargetIsFire) return "a fire";
            if (f.TargetIsPlant && !f.PlantsOn) return "a plant (plants are off in Mod Settings)";
            if (!f.FlammableNow) return "not flammable";
            if (f.Burning) return "already burning";
            if (f.OtherModCellLine) return "FlowWorks' toss line covers this square";
            return null;
        }

        // The menu line: null for None.
        public static string Label(string thingLabel, LightVerdict v, string reason)
        {
            switch (v)
            {
                case LightVerdict.Offer: return "Set fire to " + thingLabel;
                case LightVerdict.Disabled: return "Cannot set fire to " + thingLabel + ": " + reason;
                default: return null;
            }
        }
    }
}
