namespace RimMandrake.Ninefold
{
    // The nine gods of The Salvation, canon order per
    // design/Jawa/divine_satiation_engine.md "Matrix status: NINE OF NINE
    // SHIPPED (2026-08-30)". Names are LOCKED (2026-08-08) - do not rename.
    //
    // 🔴 NINEFOLD_ENUM_ORDER_SAVE_TRAP_1: THIS ENUM'S DECLARATION ORDER IS A
    // SAVE-FORMAT CONTRACT, not just a naming one. GameComponent_Ninefold
    // saves satiation/mood as a plain List<float> indexed by (int)god - the
    // ORDINAL, not the name. Inserting a 10th god mid-list, or swapping two
    // entries, keeps Count the same (FromLists()'s only guard) but silently
    // reassigns every god's saved satiation/mood to the WRONG god on load,
    // with no warning. A new god MUST be appended at the end; an existing
    // god must NEVER be reordered. GodExtensions.CheckOrdinalContract()
    // enforces the current shipped order at runtime and logs loudly (not an
    // exception - a corrupted enum still needs to load *something*) if this
    // is ever violated; update it in the SAME commit as any deliberate
    // reorder (which should not happen - append only).
    public enum God
    {
        Ishko,     // the Unmaskable - hiding, ambush, the prepared dark
        Ohm,       // the All-Current - the living machine
        Oomo,      // the Unspilled - water, thirst, rationing
        MobUnloo,  // the Ever-Owed - debt, trade, the sacred exchange
        Rekko,     // of the Second Hand - salvage, repair
        TaBaa,     // the Unrooted - flight, the refusal to root
        Zizzik,    // the Spark-Maker - malfunction, betrayal, bad luck
        Shkaar,    // the All-Searing - evil sun, exposure (EVIL god)
        Ozzik,     // the Shamed - ambition, pride, grief (THE TRAP)
    }

    public static class GodExtensions
    {
        public const int Count = 9;

        public static God[] All = new[]
        {
            God.Ishko, God.Ohm, God.Oomo, God.MobUnloo, God.Rekko,
            God.TaBaa, God.Zizzik, God.Shkaar, God.Ozzik,
        };

        // NINEFOLD_ENUM_ORDER_SAVE_TRAP_1: the frozen ordinal each god had at
        // ship (2026-08-30), keyed by name so a rename (already forbidden
        // separately) does not mask a reorder here. Call once at startup
        // (GameComponent_Ninefold's constructor) - cheap, and catches a
        // silent reorder before any save is touched rather than after.
        public static void CheckOrdinalContract()
        {
            var frozen = new System.Collections.Generic.Dictionary<God, int>
            {
                { God.Ishko, 0 }, { God.Ohm, 1 }, { God.Oomo, 2 },
                { God.MobUnloo, 3 }, { God.Rekko, 4 }, { God.TaBaa, 5 },
                { God.Zizzik, 6 }, { God.Shkaar, 7 }, { God.Ozzik, 8 },
            };
            foreach (var kv in frozen)
            {
                if ((int)kv.Key != kv.Value)
                {
                    Verse.Log.Error("[Ninefold] NINEFOLD_ENUM_ORDER_SAVE_TRAP_1: God." +
                        kv.Key + " has ordinal " + (int)kv.Key + ", expected " + kv.Value +
                        " - the God enum was reordered. Every save's satiation/mood List<float> " +
                        "is indexed by this ordinal and will now load into the WRONG god. " +
                        "Do not ship this without a save-migration plan.");
                }
            }
        }
    }
}
