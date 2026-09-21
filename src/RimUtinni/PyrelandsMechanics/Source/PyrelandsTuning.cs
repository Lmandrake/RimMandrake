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
        // ZBiome_Grasslands (More Vanilla Biomes donor)"), and RM_Pyrelands is
        // the standalone RM-tier biome shipped by mandrake.rm.pyrelands
        // (src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml). A map on any
        // other biome is invisible to the burn-line component.
        internal static readonly string[] PyrelandsBiomeDefNames =
        {
            "ZBiome_Grasslands", "RM_Pyrelands",
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

        // The warmth hediff's own disappearsAfterTicks (180 — re-stamped every aura
        // interval, so walking away from the herd loses it within a few seconds
        // rather than lingering) is hardcoded directly on RUT_FurnaceWarmth's
        // HediffCompProperties_Disappears in Defs/HediffDefs/RUT_PyrelandsHediffs.xml.
        // A C# copy of that number here was never read by anything — removed rather
        // than left as a second, driftable source of the same fact.

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

        // ---------------------------------------------------------------
        // PYRELANDS_FIRE_CADENCE_1 — the biome's fire clock (PyrelandsFireFront).
        // Owner, 2026-09-14: "the fires should come every few days, not a rare
        // event." The range below IS that sentence; do not widen it into
        // "occasionally" without a ruling.
        // ---------------------------------------------------------------
        internal const float FireFrontMinDays = 2f;
        internal const float FireFrontMaxDays = 4f;

        /// <summary>Cells lit on one bearing. A single smoulder in grass usually
        /// dies before it becomes anything; a line walks. [INVENTED]</summary>
        internal const int FireFrontWidthCells = 9;

        /// <summary>Bigger than the reseed's smoulder — this one is meant to
        /// take hold — but still well under a blaze. [INVENTED]</summary>
        internal const float FireFrontFireSize = 0.35f;

        /// <summary>Ember-grass cells sampled looking for a lawful origin before
        /// falling back to any lawful cell on the map.</summary>
        internal const int FireFrontEmberGrassTries = 30;
        internal const int FireFrontSeedTries = 40;

        // ---------------------------------------------------------------
        // DEEP_TRIBES_FIRE_RITE_1 — the Deep Tribes come to light it.
        //
        // OWNER, 2026-09-16, verbatim: "What about the biome sometimes spawning a
        // small group of Deep Tribes to ignite the fire event, then harvesting the
        // scorch fruit? That's canon in these parts."
        //
        // CANON: _freeze_rulings_2026-09-07.md R14 — "They are FIRE HARVESTERS —
        // and they are the Deep Tribes. They come into the Pyrelands periodically,
        // to perform their sacred Fire rites and reap its bounty, then return to
        // their true homes in the deep desert." "The Pyre burns with or without
        // them. It does not need them." That last sentence is why the rite is a
        // FRACTION of the clock and never the whole of it.
        // ---------------------------------------------------------------
        /// <summary>Share of fire-clock firings that arrive as a rite instead of
        /// as the biome's own front. One in three keeps the burn the biome's by
        /// default, which is the ruling. [INVENTED]</summary>
        internal const float FireRiteFraction = 0.33f;

        /// <summary>"A small group" — the owner's words. [INVENTED]</summary>
        internal const int FireRiteGroupMin = 3;
        internal const int FireRiteGroupMax = 5;

        /// <summary>How long the party works the burn before leaving with what it
        /// took. Scorch-fruit "opens only in the burn and spoils within a day"
        /// (the_pyrelands.md §5), so this is comfortably inside the window and
        /// long enough for the front to have walked off its origin. [INVENTED]</summary>
        internal const float FireRiteHarvestHours = 8f;

        /// <summary>If the party cannot reach the origin at all, the rite still
        /// happens — they light it where they got to. Half an in-game day of
        /// walking is more than a map crossing. [INVENTED]</summary>
        internal const int FireRiteTravelTimeoutTicks = 30000;

        /// <summary>How far from the rite's origin a harvester will range looking
        /// for pods. The front walks, so this is deliberately wider than the
        /// ignition line. [INVENTED]</summary>
        internal const float FireRiteHarvestRadius = 45f;

        /// <summary>How near the origin they mill about between pods.</summary>
        internal const float FireRiteWanderRadius = 12f;

        /// <summary>Scorch-fruit one harvester will carry off before it stops
        /// picking. The plant yields 5 a pod, so this is roughly five pods
        /// each. [INVENTED]</summary>
        internal const int FireRiteCarryPerPawn = 25;

        /// <summary>Spread of the party around its map-edge entry cell.</summary>
        internal const int FireRiteSpawnSpread = 8;

        // ---------------------------------------------------------------
        // FURNACEBEAST_THERMAL_CYCLE_1 — the capacitor
        // (CompFurnaceThermalCharge, JobGiver_RUT_FurnaceThermalCycle).
        // ---------------------------------------------------------------
        /// <summary>Charge is re-evaluated ~every 4 in-game minutes. Rare-tick
        /// cadence: this is a weeks-long cycle, not a combat stat.</summary>
        internal const int FurnaceChargeIntervalTicks = 250;

        /// <summary>Above this ambient temperature the beast charges. Chosen at
        /// the Deep Desert's daytime floor, so basking genuinely works out there
        /// and an ordinary temperate map never charges one at all. [INVENTED]</summary>
        internal const float FurnaceChargeAmbientC = 35f;

        /// <summary>Degrees above the threshold at which charging is at full
        /// rate. Beyond it the rate is capped — a 1000 degC reading must not fill
        /// the capacitor in one check. [INVENTED]</summary>
        internal const float FurnaceChargeAmbientSpanC = 45f;

        /// <summary>At full rate, ~1.4 in-game days from empty to full
        /// (0.004 x 240 checks/day). "Basking for weeks" in the description is
        /// the WORLD leg; on a map the player watches, a day and a half of
        /// standing in the heat is the readable version. [INVENTED]</summary>
        internal const float FurnaceChargePerCheckAtFullHeat = 0.004f;

        /// <summary>Below this the beast bleeds. The near-terminator leg.</summary>
        internal const float FurnaceBleedAmbientC = 5f;
        internal const float FurnaceBleedAmbientSpanC = 35f;

        /// <summary>Slower than charging: "bleeding its banked warmth into the
        /// cold air for weeks". [INVENTED]</summary>
        internal const float FurnaceBleedPerCheckAtFullCold = 0.0015f;

        /// <summary>Standing in the burn is the fast lane — ~2 in-game hours from
        /// empty to full. This is what makes walking into a fire rational.
        /// [INVENTED]</summary>
        internal const float FurnaceChargePerCheckNearFire = 0.05f;
        internal const float FurnaceChargeFireRadius = 6f;

        /// <summary>Radiant push at full charge, per check. Deliberately under
        /// the beast's own flat CompHeatPusher (heatPerSecond 18): this is the
        /// part that runs down, not the main heater. [INVENTED]</summary>
        internal const float FurnaceRadiantHeatPerCheckAtFullCharge = 6f;

        /// <summary>Below this charge the beast seeks the burn; above the second
        /// number it steps off it. The gap between them is hysteresis — without
        /// it a beast at the threshold oscillates on and off the fire every
        /// check. [INVENTED]</summary>
        internal const float FurnaceChargeSeekBelow = 0.75f;
        internal const float FurnaceChargeAvoidAbove = 0.95f;

        /// <summary>Map-scale only. Further than this and going to the burn is
        /// the WORLD migration's job (FURNACEBEAST_WORLD_MIGRATION_1), not this
        /// job-giver's — so it returns no job rather than faking one.</summary>
        internal const float FurnaceBurnSeekRadius = 60f;
        internal const float FurnaceBurnCloseEnough = 8f;
        internal const int FurnaceBurnBackOffCells = 14;

        /// <summary>How far a hungry beast will walk for a thornvine patch.
        /// [INVENTED]</summary>
        internal const float FurnaceThornvineScanRadius = 30f;
    }
}
