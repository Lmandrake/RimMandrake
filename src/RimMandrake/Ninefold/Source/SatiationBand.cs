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
            if (satiation >= 60f) return SatiationBand.Exalted;
            if (satiation >= 20f) return SatiationBand.Content;
            if (satiation >= -19f) return SatiationBand.Neutral;
            if (satiation >= -59f) return SatiationBand.Slighted;
            return SatiationBand.Wrathful;
        }
    }
}
