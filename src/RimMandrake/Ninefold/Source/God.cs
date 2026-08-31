namespace RimMandrake.Ninefold
{
    // The nine gods of The Salvation, canon order per
    // design/Jawa/divine_satiation_engine.md "Matrix status: NINE OF NINE
    // SHIPPED (2026-08-30)". Names are LOCKED (2026-08-08) - do not rename.
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
    }
}
