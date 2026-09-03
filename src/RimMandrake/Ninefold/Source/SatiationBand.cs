namespace RimMandrake.Ninefold
{
    // design/Jawa/divine_satiation_engine.md §1: "Bands: Exalted +60/+100 -
    // Content +20/+59 - Neutral -19/+19 - Slighted -20/-59 - Wrathful -60/-100."
    public enum SatiationBand
    {
        Wrathful,
        Slighted,
        Neutral,
        Content,
        Exalted,
    }

    public static class SatiationBandUtility
    {
        public static SatiationBand BandFor(float satiation)
        {
            // Each boundary value belongs to the band it is the NAMED ENDPOINT
            // of. The positive side's `>=` correctly assigns 60 and 20 to the
            // HIGHER band; the negative side needs a STRICT `>` for the same
            // effect, since -20 and -60 are the start of the LOWER (more
            // negative) band, not the end of the higher one. Reachable at
            // exactly these boundaries: Rekko takes exactly -15 per building
            // deconstruct, so four deconstructs lands exactly -60.
            if (satiation >= 60f) return SatiationBand.Exalted;
            if (satiation >= 20f) return SatiationBand.Content;
            if (satiation > -20f) return SatiationBand.Neutral;
            if (satiation > -60f) return SatiationBand.Slighted;
            return SatiationBand.Wrathful;
        }
    }
}
