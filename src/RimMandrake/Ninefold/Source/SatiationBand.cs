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
            // Fixed 2026-09-02 TWICE, second time correctly (opus re-review pass
            // caught the first fix was itself wrong): the spec's bands are
            // Neutral -19/+19, Slighted -20/-59, Wrathful -60/-100 - so -20
            // belongs to SLIGHTED and -60 belongs to WRATHFUL, the LOWER band
            // in each case. The positive side's `>=` correctly assigns its
            // boundary (60, 20) to the HIGHER band; by the same convention the
            // negative boundaries must be excluded from the higher (less
            // negative) band, which needs a STRICT `>`, not `>=`. The earlier
            // pass used `>= -20f`/`>= -60f`, which put exactly -20 in Neutral
            // and exactly -60 in Slighted - reachable today: Rekko takes
            // exactly -15 per building deconstruct, so four deconstructs lands
            // exactly -60.
            if (satiation >= 60f) return SatiationBand.Exalted;
            if (satiation >= 20f) return SatiationBand.Content;
            if (satiation > -20f) return SatiationBand.Neutral;
            if (satiation > -60f) return SatiationBand.Slighted;
            return SatiationBand.Wrathful;
        }
    }
}
