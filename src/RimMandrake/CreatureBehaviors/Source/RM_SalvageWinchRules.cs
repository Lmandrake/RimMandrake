// SHIP_TOW_LINE_1: Verse-free, also compiled by SelfTestFuzz.
namespace RimMandrake.CreatureBehaviors
{
    /// <summary>The rules for what a winch may hook, with no Verse lookups beyond the values passed in.</summary>
    public static class RM_SalvageWinchRules
    {
        /// <summary>Reason a thing cannot be hooked, or null when it can. Mass is the whole stack.</summary>
        public static string RefusalFor(bool isCorpse, bool isPawn, bool downedAnimal, bool isItem, float totalMass, float maxMass, float distance, float range)
        {
            if (isPawn && !downedAnimal) return "only a downed beast can be hooked";
            if (!isPawn && !isCorpse && !isItem) return "nothing there to hook";
            if (distance > range) return "out of range";
            if (totalMass > maxMass) return "too heavy for the line";
            return null;
        }
    }
}
