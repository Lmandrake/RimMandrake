namespace RimMandrake.Ninefold
{
    // Shared small/med/large deltas for the event hooks (Patch_*.cs).
    // design/Jawa/divine_satiation_engine.md §8b: "common everyday acts/events
    // are a WEAK influence that accumulates... rare/high-impact acts/events
    // are a LARGE, sudden modification -- the size of the swing tracks the
    // rarity and weight of the act, not just its category."
    //
    // 🔴 UNTUNED -- a first-pass ordering only, same status as
    // GameComponent_Ninefold.MoodAmplitude. §10 explicitly defers real
    // tuning to a throwaway-save test rig; these are just SMALL < MEDIUM <
    // LARGE placeholders so the five hooks (Patch_*.cs) have something
    // concrete to call.
    public static class EventMagnitude
    {
        public const float Small = 3f;
        public const float Medium = 8f;
        public const float Large = 15f;
    }
}
