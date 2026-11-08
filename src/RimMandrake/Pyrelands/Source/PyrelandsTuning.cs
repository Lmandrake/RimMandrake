namespace RimMandrake.Pyrelands
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
    public static class PyrelandsTuning
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
        public static readonly string[] PyrelandsBiomeDefNames =
        {
            "ZBiome_Grasslands", "RM_Pyrelands",
        };

        // ---------------------------------------------------------------
        // The burn-line watch (MapComponent_BurnLine).
        // ---------------------------------------------------------------
        /// <summary>How often the burn is re-measured. 60 ticks = one second of
        /// game time at 1x; the same cadence CompHeatPusher uses.</summary>
        public const int BurnWatchIntervalTicks = 60;

        /// <summary>Sheet §5: "The burn exists somewhere on the biome, always;
        /// only its address changes." Two quiet days is the grace period before
        /// this component lights the next address itself. [INVENTED]</summary>
        public const int StandingBurnQuietTicks = 120000;

        /// <summary>How many cells are sampled looking for somewhere lawful to
        /// re-seed the standing burn before giving up until the next attempt.</summary>
        public const int StandingBurnSeedTries = 40;

        /// <summary>Minimum distance from any player-faction building before the
        /// standing burn may re-seed. The burn is the biome's, not an attack: it
        /// starts out in the grass. [INVENTED]</summary>
        public const float StandingBurnMinDistFromColony = 32f;

        /// <summary>Re-seed attempts are spaced out so a map where nothing is
        /// flammable does not sample 40 cells every second. [INVENTED]</summary>
        public const int StandingBurnRetryTicks = 2500;

        /// <summary>Fire.MinFireSize — a smoulder, not a blaze.</summary>
        public const float SmoulderFireSize = 0.1f;

        // ---------------------------------------------------------------
        // Burn intelligence: arson debt (sheet §8, "an unplanned burn is an act
        // of war"). Debt accrues once per watch interval per burning cell whose
        // Fire.instigator belongs to the player.
        // ---------------------------------------------------------------
        public const float ArsonDebtPerPlayerFirePerCheck = 1f;
        public const float ArsonDebtDecayPerCheck = 0.5f;
        public const float ArsonDebtCap = 1500f;

        /// <summary>Arson debt at which the Tribes will answer. At the accrual
        /// rate above this is roughly "a twenty-cell burn you lit, left running
        /// for half an in-game hour" (20 checks x 60 ticks = 1,200 ticks). [INVENTED]</summary>
        public const float ArsonDebtRaidThreshold = 400f;

        /// <summary>Goodwill the Tribes lose over an unplanned burn. Enough to
        /// push a merely-neutral tribe over the hostility line in one event.
        /// [INVENTED]</summary>
        public const int FireRaidGoodwillHit = -75;

        /// <summary>Arson-justice is "short, furious" (sheet §8) — not a full
        /// threat-point raid. [INVENTED]</summary>
        public const float FireRaidPointsFactor = 0.6f;
        public const float FireRaidPointsMin = 250f;

        // ---------------------------------------------------------------
        // Flame harvest (sheet §8): the Tribes walk a live burn-line.
        // ---------------------------------------------------------------
        /// <summary>How much fire has to be standing before a harvest party is
        /// worth the walk. [INVENTED]</summary>
        public const int FlameHarvestMinFires = 10;

        /// <summary>Points handed to the peaceful pawn-group maker. Vanilla
        /// visitor groups sit in this band. [INVENTED]</summary>
        public const float FlameHarvestPoints = 180f;

        // ---------------------------------------------------------------
        // Fire-hawk (§7c). Spread-only: every one of these is downstream of an
        // existing fire being found first.
        // ---------------------------------------------------------------
        public const float FireHawkScanRadius = 18f;
        public const int FireHawkSpreadDistance = 6;
        public const int FireHawkCooldownTicks = 15000;   // ~6 in-game hours
        public const int FireHawkTakeEmberTicks = 90;

        // ---------------------------------------------------------------
        // Furnace-beast (§8b, §8c).
        // ---------------------------------------------------------------
        /// <summary>Aura radius — "pawns within a few cells" (§8b). [INVENTED]</summary>
        public const float FurnaceAuraRadius = 4.9f;

        /// <summary>PYRELANDS_ULLAI_GIANT_BUILD_1: the classic adult body size the radius and bed numbers were tuned
        /// at. A bigger race scales them: warmth radius by sqrt(size ratio) (heat spreads over an area), bed-down
        /// smoulder cells by the ratio itself. The classic beast reads 1.</summary>
        public const float FurnaceClassicBodySize = 3.2f;

        public static float FurnaceSizeRatio(Verse.Pawn beast)
        {
            return RM_FurnaceKernel.SizeRatio(beast?.RaceProps?.baseBodySize, FurnaceClassicBodySize);
        }

        /// <summary>Felt-temperature offset at the beast itself, degrees C, before the Mod Settings strength dial.
        /// Falls to 0 at the aura radius. Replaces the old RM_FurnaceWarmth comfort-range hediff (-14 cold / -6 heat
        /// tolerance) with one local heat source: it relieves cold and worsens heat through vanilla's own systems.
        /// [INVENTED, tuned in live play]</summary>
        public const float FurnaceWarmthMaxC = 14f;

        /// <summary>A rest has to have been a real rest before the ground is hot
        /// enough to take. 1 in-game hour. [INVENTED]</summary>
        public const int FurnaceMinRestTicks = 2500;

        /// <summary>Chance that a completed bed-down smoulders its ground. NO
        /// tamed exemption — owner ruling, verbatim: "Fires all the time! I love
        /// it." [INVENTED number, ruled behaviour]</summary>
        public const float FurnaceBedIgnitionChance = 0.18f;

        /// <summary>"Smolder, not blaze: 1-2 cells" (§8c).</summary>
        public const int FurnaceBedIgnitionMinCells = 1;
        public const int FurnaceBedIgnitionMaxCells = 2;

        /// <summary>Owner card 2026-11-08 01:01 "it ignites grass it sleeps in": asleep on a flammable plant, the beast
        /// sets it alight. Never at once: the first half hour of sleep is safe, then a mean of 1.5 h more, so about two
        /// hours of sleep on average (63% by 2 h, 81% by 3 h, ~99% by a night of 8 h). Never on a bare floor. [INVENTED, ruled behaviour]</summary>
        public const int FurnaceSleepIgnitionGraceTicks = 1250;
        public const int FurnaceSleepIgnitionMtbTicks = 3750;
        public const int FurnaceSleepIgnitionCheckTicks = 250;

        /// <summary>The sleeping-in-grass fire is a fire, not the bed-down smoulder: a 0.1 start in grass usually dies
        /// before it spreads, so the fire-front's size. [INVENTED]</summary>
        public const float FurnaceSleepIgnitionFireSize = 0.35f;

        // ---------------------------------------------------------------
        // PYRELANDS_FIRE_CADENCE_1 — the biome's fire clock (PyrelandsFireFront).
        // Owner, 2026-09-14: "the fires should come every few days, not a rare
        // event." The range below IS that sentence; do not widen it into
        // "occasionally" without a ruling.
        // ---------------------------------------------------------------
        // The burn approaching home. A front walks about 60 cells a day (measured 2026-11-07, 250x250 map, day 1 of a
        // real colony), and a player watching their base got no word of it until vanilla's Fire! alert, with flames
        // already on the home area and the food stacked outside lost. 30 cells is about half a day. [INVENTED, played once]
        public const int BurnApproachWarnCells = 30;
        /// <summary>At or inside this many cells the warning says the burn has reached home's edge, not how far off it is.</summary>
        public const int BurnApproachAtEdgeCells = 3;
        public const int BurnApproachCheckTicks = 600;
        public const int BurnApproachCooldownTicks = 90000;
        public const int BurnApproachHomeResampleTicks = 2500;

        public const float FireFrontMinDays = 2f;
        public const float FireFrontMaxDays = 4f;

        /// <summary>Cells lit on one bearing. A single smoulder in grass usually
        /// dies before it becomes anything; a line walks. [INVENTED]</summary>
        public const int FireFrontWidthCells = 9;

        /// <summary>Bigger than the reseed's smoulder — this one is meant to
        /// take hold — but still well under a blaze. [INVENTED]</summary>
        public const float FireFrontFireSize = 0.35f;

        /// <summary>Ember-grass cells sampled looking for a lawful origin before
        /// falling back to any lawful cell on the map.</summary>
        public const int FireFrontEmberGrassTries = 30;
        public const int FireFrontSeedTries = 40;

        // ---------------------------------------------------------------
        // PYRE_OPENING_FRONT — every fresh Pyrelands map starts with one small smouldering front (owner, by card,
        // 2026-10-22: "GPT review Q7 → Pyrelands fresh map starts with a smouldering front"), so the walk bar "a fresh map
        // shows an active line of fire, with a scorched trail" is true at arrival instead of 2-4 days in.
        // ---------------------------------------------------------------

        /// <summary>Cells on the opening front's line: about half a scheduled front. [INVENTED]</summary>
        public const int OpeningFrontWidthCells = 5;

        /// <summary>The scheduled front's fire size: the reseed's 0.1 smoulder usually dies before it walks, and the bar
        /// wants a line that walks and leaves a trail. [INVENTED]</summary>
        public const float OpeningFrontFireSize = 0.35f;

        /// <summary>How long after map generation the opening front may still be lit (it retries each watch interval
        /// when no lawful cell takes); past it the map is no longer fresh and the opening front is dropped. One hour.</summary>
        public const int OpeningFrontWindowTicks = 2500;

        // Yesterday's fire (PyrelandsYesterdayFire, 2026-11-07): on map s the 5-cell opening line lit in thick grass and read
        // as a camp fire, with no trail behind it. The map is now generated with a half-disc scar on one edge and the opening
        // front lights along its leading arc. Conductor brief: radius ~35-50, front at least ~70 cells from the map centre
        // and the landing spot, away from corners and rock, the arc lit enough to read as a line but not every cell.

        /// <summary>The scar's nominal radius, rolled per map; its ragged edge reaches up to YesterdayFireRagged further.</summary>
        public const float YesterdayFireMinRadius = 35f;
        public const float YesterdayFireMaxRadius = 50f;

        /// <summary>Below this the scar is not built (a small map has no room 70 cells from its centre): the opening front
        /// falls back to its plain line. [INVENTED]</summary>
        public const float YesterdayFireFloorRadius = 20f;

        /// <summary>The front's farthest ragged reach stays this far from the map centre and from the landing spot.</summary>
        public const float YesterdayFireFrontClearance = 70f;

        /// <summary>How far, as a share of the radius, the noise pushes the edge in or out at a bearing. [INVENTED]</summary>
        public const float YesterdayFireRagged = 0.22f;

        /// <summary>Perlin frequency of the edge's raggedness along the arc: about one bulge per 12 cells of a 45-cell arc
        /// (2 pi 45 x 0.08 = 23 per turn) before the finer octaves. [INVENTED]</summary>
        public const double YesterdayFireEdgeFrequency = 0.08;

        /// <summary>The burn's age where it started (the map edge) and at its front: about the last day. A new game's scar is
        /// stamped at tick 0 throughout (RM_BurnKernel.ScarStampTick). [INVENTED]</summary>
        public const int YesterdayFireOldestAgeTicks = 45000;
        public const int YesterdayFireYoungestAgeTicks = 1250;

        /// <summary>The arc is the leading edge: bearings within 60 degrees of the inward normal (cos 60 = 0.5); the flanks
        /// running back to the map edge stay quiet char.</summary>
        public const float YesterdayFireArcMinCos = 0.5f;

        /// <summary>One fire per second arc cell at least, and at most this many fires: a 45-cell scar's arc holds about 50-60
        /// grass cells, so about 25-30 fires, three scheduled fronts' worth. [INVENTED]</summary>
        public const int YesterdayFireArcStride = 2;
        public const int YesterdayFireArcFireCap = 32;

        /// <summary>The scar's age you can see: where it started, YesterdayFireSproutChance of its cells have re-sprouted young
        /// grass (ember-grass and quickgrass at the biome's own wild ratio, growth between the two bounds), falling straight to
        /// none at YesterdayFireSproutEndDepth, so the char right behind the front is bare. Conductor brief: "a scar ~0.75 day
        /// old held about 15% of its cells re-sprouted (small grass, growth ~0.05-0.2)" in ordinary play.</summary>
        public const float YesterdayFireSproutChance = 0.15f;
        public const float YesterdayFireSproutEndDepth = 0.6f;
        public const float YesterdayFireSproutGrowthMin = 0.05f;
        public const float YesterdayFireSproutGrowthMax = 0.2f;

        /// <summary>Scorch-fruit pods laid on the young part of the scar (depth from the edge at least YesterdayFireYoungDepth);
        /// the burn's landing rule (FruitLandingLegal) and the map cap (scorchFruitMapCap) still apply. "A few". [INVENTED]</summary>
        public const int YesterdayFirePods = 4;
        public const float YesterdayFireYoungDepth = 0.7f;

        /// <summary>Site search: candidate centres per map edge, along the middle of it (away from the corners), cells sampled
        /// in each half-disc, and the share that must be burnable ground (not rock, roof or water). [INVENTED]</summary>
        public const int YesterdayFireSitesPerEdge = 3;
        public const float YesterdayFireSiteMinAlong = 0.3f;
        public const float YesterdayFireSiteMaxAlong = 0.7f;
        public const int YesterdayFireSiteSamples = 64;
        public const float YesterdayFireSiteMinBurnable = 0.6f;

        /// <summary>Ground this close to water did not burn: the green ring (GenStep_PyrelandsGreenRing's ringReach, 7.5), which
        /// map t showed green around its ponds, stays green inside a scar too.</summary>
        public const float YesterdayFireWetReach = 7.5f;

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
        public const float FireRiteFraction = 0.33f;

        /// <summary>"A small group" — the owner's words. [INVENTED]</summary>
        public const int FireRiteGroupMin = 3;
        public const int FireRiteGroupMax = 5;

        /// <summary>How long the party works the burn before leaving with what it
        /// took. Scorch-fruit "opens only in the burn and spoils within a day"
        /// (the_pyrelands.md §5), so this is comfortably inside the window and
        /// long enough for the front to have walked off its origin. [INVENTED]</summary>
        public const float FireRiteHarvestHours = 8f;

        /// <summary>If the party cannot reach the origin at all, the rite still
        /// happens — they light it where they got to. Half an in-game day of
        /// walking is more than a map crossing. [INVENTED]</summary>
        public const int FireRiteTravelTimeoutTicks = 30000;

        /// <summary>How far from the rite's origin a harvester will range looking
        /// for pods. The front walks, so this is deliberately wider than the
        /// ignition line. [INVENTED]</summary>
        public const float FireRiteHarvestRadius = 45f;

        /// <summary>How near the origin they mill about between pods.</summary>
        public const float FireRiteWanderRadius = 12f;

        /// <summary>Scorch-fruit one harvester will carry off before it stops
        /// picking. The plant yields 5 a pod, so this is roughly five pods
        /// each. [INVENTED]</summary>
        public const int FireRiteCarryPerPawn = 25;

        /// <summary>Spread of the party around its map-edge entry cell.</summary>
        public const int FireRiteSpawnSpread = 8;

        // ---------------------------------------------------------------
        // FURNACEBEAST_THERMAL_CYCLE_1 — the capacitor
        // (CompFurnaceThermalCharge, JobGiver_RUT_FurnaceThermalCycle).
        // ---------------------------------------------------------------
        /// <summary>Charge is re-evaluated ~every 6 in-game minutes. Rare-tick
        /// cadence: this is a weeks-long cycle, not a combat stat.</summary>
        public const int FurnaceChargeIntervalTicks = 250;

        /// <summary>How far above outdoors a furnace-beast can heat an enclosed room: the oven's ceiling (owner card
        /// 2026-11-08 01:01, "heat with no cap", a pen at 50 C ambient settles 15-30 C over it). 75 C gives an unprotected
        /// colonist extreme heatstroke in ~7 h, death in ~11 h: a hazard to read, not a trap. The beast is immune.</summary>
        public const float FurnaceRoomAboveOutdoorC = 25f;

        /// <summary>The ceiling never falls under this, so a barn in a cold biome still warms to comfortable (the old def cap).</summary>
        public const float FurnaceRoomFloorC = 24f;

        /// <summary>Above this ambient temperature the beast charges. Chosen at
        /// the Deep Desert's daytime floor, so basking genuinely works out there
        /// and an ordinary temperate map never charges one at all. [INVENTED]</summary>
        public const float FurnaceChargeAmbientC = 35f;

        /// <summary>Degrees above the threshold at which charging is at full
        /// rate. Beyond it the rate is capped — a 1000 degC reading must not fill
        /// the capacitor in one check. [INVENTED]</summary>
        public const float FurnaceChargeAmbientSpanC = 45f;

        /// <summary>At full rate, ~1 in-game day from empty to full
        /// (1 / 0.004 = 250 checks, at 240 checks/day): on a map the player
        /// watches, about a day of standing in the heat is the readable
        /// version. [INVENTED]</summary>
        public const float FurnaceChargePerCheckAtFullHeat = 0.004f;

        /// <summary>Below this the beast bleeds. The near-terminator leg.</summary>
        public const float FurnaceBleedAmbientC = 5f;
        public const float FurnaceBleedAmbientSpanC = 35f;

        /// <summary>Slower than charging: "bleeding its banked warmth into the
        /// cold air for weeks". [INVENTED]</summary>
        public const float FurnaceBleedPerCheckAtFullCold = 0.0015f;

        /// <summary>Standing in the burn is the fast lane — ~2 in-game hours from
        /// empty to full. This is what makes walking into a fire rational.
        /// [INVENTED]</summary>
        public const float FurnaceChargePerCheckNearFire = 0.05f;
        public const float FurnaceChargeFireRadius = 6f;

        /// <summary>Radiant push at full charge, per check. Deliberately under
        /// the beast's own flat CompHeatPusher (heatPerSecond 18): this is the
        /// part that runs down, not the main heater. [INVENTED]</summary>
        public const float FurnaceRadiantHeatPerCheckAtFullCharge = 6f;

        /// <summary>Below this charge the beast seeks the burn; above the second
        /// number it steps off it. The gap between them is hysteresis — without
        /// it a beast at the threshold oscillates on and off the fire every
        /// check. [INVENTED]</summary>
        public const float FurnaceChargeSeekBelow = 0.75f;
        public const float FurnaceChargeAvoidAbove = 0.95f;

        /// <summary>Map-scale only. Further than this the job-giver returns no
        /// job rather than faking one.</summary>
        public const float FurnaceBurnSeekRadius = 60f;
        public const float FurnaceBurnCloseEnough = 8f;
        public const int FurnaceBurnBackOffCells = 14;

        /// <summary>How far a hungry beast will walk for a thornvine patch.
        /// [INVENTED]</summary>
        public const float FurnaceThornvineScanRadius = 30f;

        // ---------------------------------------------------------------
        // PYRELANDS_DEDICATED_GRAZER_1 — burrow-on-fire
        // (RM_JobGiver_BurrowOnFire, RM_JobDriver_Burrow). Generic and
        // opt-in via RM_BurrowOnFireExtension, so any race can adopt the
        // "detect the fire, go to ground, re-emerge" behaviour without new
        // C#; RM_Ashwallow is the first consumer.
        // ---------------------------------------------------------------
        /// <summary>How close a free-standing fire has to be before an
        /// extension-carrying race goes to ground. Comfortably wider than a
        /// fire front's own width (FireFrontWidthCells, 9 cells) so the
        /// animal burrows ahead of the line reaching it rather than at the
        /// last possible cell. [INVENTED] 6, was 15 (map t, 2026-11-07): at 15 a herd dove with the front a quarter-day off
        /// and sat out of sight for hours; MapComponent_BurnLine now also pulls a grazing or sleeping burrower down.</summary>
        public const float BurrowDetectionRadius = 6f;

        /// <summary>PyrelandsWetRoots: degrees a plant on WATERED ash-field ground is spared when its heat growth factor is read.
        /// At the biome's 53.6 C median a vanilla crop's 42-58 C falloff zeroes the growing day; 15 C brings a 45-62 C day
        /// to 30-47 C, so a watered crop grows nearly all day and a dry one hardly at all. [INVENTED, 2026-11-07]</summary>
        public const float WetRootsCoolingC = 15f;

        /// <summary>PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE: least gap between two dive nudges of one pawn
        /// (MapComponent_BurnLine re-asks an idling burrower's think tree while a fire is near). Normally one nudge
        /// suffices because it starts the dive; the gap only bounds a pawn whose tree answers something other than the
        /// dive, so its wander is not restarted every watch interval. [INVENTED]</summary>
        public const int BurrowNudgeMinGapTicks = 250;

        /// <summary>Safety cap: never stays burrowed longer than this even
        /// if the fire-near check somehow never clears (a stuck Fire, a
        /// modded interaction) — comfortably longer than any one front
        /// takes to pass. 60000 ticks = 1 in-game day. Followed by
        /// BurrowTimeoutCooldownTicks above ground, or the job giver would
        /// send it straight back down. [INVENTED]</summary>
        public const int BurrowMaxTicks = 60000;

        /// <summary>FIRE_SCAN_DIAGNOSE_BIG_BURN_COST: a burrowed pawn re-asks "is a fire still near" once per this many ticks
        /// (staggered per pawn, RM_FireEcoKernel.BurrowEmergeCheckDue), not every tick; it surfaces at most this late.</summary>
        public const int BurrowEmergeCheckIntervalTicks = 30;

        /// <summary>After a timed-out burrow, the animal stays up this long
        /// before it may burrow again, even with the fire still near.
        /// 7500 ticks = 3 in-game hours. [INVENTED]</summary>
        public const int BurrowTimeoutCooldownTicks = 7500;

        /// <summary>ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE: after a heat-category hit the dome holds at least this long with
        /// no fire near (a flamethrower or incendiary shot leaves no free fire to wait out); every further hit restarts it.
        /// 600 ticks = 10 s. [INVENTED]</summary>
        public const int BurrowHeatHoldTicks = 600;
    }
}
