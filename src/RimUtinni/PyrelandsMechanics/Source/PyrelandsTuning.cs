namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1 — every number this kit invents, in one place.
    ///
    /// 🔴 EVERY constant here is INVENTED unless its comment cites a ruling or a
    /// measured vanilla anchor. The briefs
    /// (design/Jawa/worldbuilding/creatures/RUT_ruled_commissions_wave2.md §§7-8,
    /// design/Jawa/worldbuilding/biomes/the_pyrelands.md) flag the same numbers
    /// [INVENTED] and hand the choice to the build seat, which is this file. They
    /// are deliberately gathered here rather than scattered through the comps so a
    /// live-fire tuning pass edits one file.
    ///
    /// Tick arithmetic used throughout: 2500 ticks = 1 in-game hour,
    /// 60000 ticks = 1 in-game day.
    /// </summary>
    internal static class PyrelandsTuning
    {
        // ---------------------------------------------------------------
        // Which maps carry the standing burn.
        // ---------------------------------------------------------------
        // Both biome defNames are READ, not guessed: ZBiome_Grasslands is the
        // campaign's Pyrelands (the_pyrelands.md's own header: "Defines
        // ZBiome_Grasslands (More Vanilla Biomes donor)"), and RM_FE_Pyrelands is
        // the standalone RM-tier biome shipped by mandrake.rm.pyrelands
        // (src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml). A map on any
        // other biome is invisible to the burn-line component.
        internal static readonly string[] PyrelandsBiomeDefNames =
        {
            "ZBiome_Grasslands", "RM_FE_Pyrelands",
        };

        // ---------------------------------------------------------------
        // The burn-line watch (MapComponent_BurnLine).
        // ---------------------------------------------------------------
        /// <summary>How often the burn is re-measured. 60 ticks = one second of
        /// game time at 1x; the same cadence CompHeatPusher uses.</summary>
        internal const int BurnWatchIntervalTicks = 60;

        /// <summary>Sheet §5: "The burn exists somewhere on the biome, always;
        /// only its address changes." Two quiet days is the grace period before
        /// this component lights the next address itself. [INVENTED]</summary>
        internal const int StandingBurnQuietTicks = 120000;

        /// <summary>How many cells are sampled looking for somewhere lawful to
        /// re-seed the standing burn before giving up until the next attempt.</summary>
        internal const int StandingBurnSeedTries = 40;

        /// <summary>Minimum distance from any player-faction building before the
        /// standing burn may re-seed. The burn is the biome's, not an attack: it
        /// starts out in the grass. [INVENTED]</summary>
        internal const float StandingBurnMinDistFromColony = 32f;

        /// <summary>Re-seed attempts are spaced out so a map where nothing is
        /// flammable does not sample 40 cells every second. [INVENTED]</summary>
        internal const int StandingBurnRetryTicks = 2500;

        /// <summary>Fire.MinFireSize — a smoulder, not a blaze.</summary>
        internal const float SmoulderFireSize = 0.1f;

        // ---------------------------------------------------------------
        // Burn intelligence: arson debt (sheet §8, "an unplanned burn is an act
        // of war"). Debt accrues once per watch interval per burning cell whose
        // Fire.instigator belongs to the player.
        // ---------------------------------------------------------------
        internal const float ArsonDebtPerPlayerFirePerCheck = 1f;
        internal const float ArsonDebtDecayPerCheck = 0.5f;
        internal const float ArsonDebtCap = 1500f;

        /// <summary>Arson debt at which the Tribes will answer. At the accrual
        /// rate above this is roughly "a twenty-cell burn you lit, left running
        /// for four minutes of game time". [INVENTED]</summary>
        internal const float ArsonDebtRaidThreshold = 400f;

        /// <summary>Goodwill the Tribes lose over an unplanned burn. Enough to
        /// push a merely-neutral tribe over the hostility line in one event.
        /// [INVENTED]</summary>
        internal const int FireRaidGoodwillHit = -75;

        /// <summary>Arson-justice is "short, furious" (sheet §8) — not a full
        /// threat-point raid. [INVENTED]</summary>
        internal const float FireRaidPointsFactor = 0.6f;
        internal const float FireRaidPointsMin = 250f;

        // ---------------------------------------------------------------
        // Flame harvest (sheet §8): the Tribes walk a live burn-line.
        // ---------------------------------------------------------------
        /// <summary>How much fire has to be standing before a harvest party is
        /// worth the walk. [INVENTED]</summary>
        internal const int FlameHarvestMinFires = 10;

        /// <summary>Points handed to the peaceful pawn-group maker. Vanilla
        /// visitor groups sit in this band. [INVENTED]</summary>
        internal const float FlameHarvestPoints = 180f;

        // ---------------------------------------------------------------
        // Fire-hawk (§7c). Spread-only: every one of these is downstream of an
        // existing fire being found first.
        // ---------------------------------------------------------------
        internal const float FireHawkScanRadius = 18f;
        internal const int FireHawkSpreadDistance = 6;
        internal const int FireHawkCooldownTicks = 15000;   // ~6 in-game hours
        internal const int FireHawkTakeEmberTicks = 90;

        // ---------------------------------------------------------------
        // Furnace-beast (§8b, §8c).
        // ---------------------------------------------------------------
        /// <summary>Aura radius — "pawns within a few cells" (§8b). [INVENTED]</summary>
        internal const float FurnaceAuraRadius = 4.9f;
        internal const int FurnaceAuraIntervalTicks = 60;

        /// <summary>The warmth hediff is re-stamped every aura interval and is
        /// written to expire shortly after, so walking away from the herd loses
        /// it within a few seconds rather than lingering.</summary>
        internal const int FurnaceAuraHediffTicks = 180;

        /// <summary>A rest has to have been a real rest before the ground is hot
        /// enough to take. 1 in-game hour. [INVENTED]</summary>
        internal const int FurnaceMinRestTicks = 2500;

        /// <summary>Chance that a completed bed-down smoulders its ground. NO
        /// tamed exemption — owner ruling, verbatim: "Fires all the time! I love
        /// it." [INVENTED number, ruled behaviour]</summary>
        internal const float FurnaceBedIgnitionChance = 0.18f;

        /// <summary>"Smolder, not blaze: 1-2 cells" (§8c).</summary>
        internal const int FurnaceBedIgnitionMinCells = 1;
        internal const int FurnaceBedIgnitionMaxCells = 2;
    }
}
