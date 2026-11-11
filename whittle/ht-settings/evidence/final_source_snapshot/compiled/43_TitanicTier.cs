namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// The three ruled tiers (TITANIC_CREATURES_MOD_1 card #2 / tier table).
    /// Backed by int so ordinary &lt;/&gt;/&gt;=/&lt;= comparisons order them
    /// correctly (None &lt; T1 &lt; T2 &lt; T3) - used throughout the crush
    /// table and wake processor to mean "at least this tier".
    /// </summary>
    public enum TitanicTier
    {
        None = 0,
        T1 = 1,
        T2 = 2,
        T3 = 3,
    }
}
