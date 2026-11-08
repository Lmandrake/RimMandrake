using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the fire-ecology hooks and the biome (FireEcologyHook.cs, WildPlantAllowlist.cs, RM_PyrelandsMod.cs): the
    // biome placement score, the terrain-family predicates, the ash-dusting / scorch-fruit gates, ash on the sand grid (the
    // weather's ash rate, the outdoor wear, the cover's opacity, the grass dust), the once-per-fire roll set, the cross-biome list parser and the wild-plant allowlist. The mod calls these with the
    // same expressions; the offline fuzz drives them.

    /// <summary>A map's drift-field noise cut points (RM_FireEcoKernel.DriftCuts): pool, fringe (1), bank (2), core (3).</summary>
    public struct RM_DriftCuts
    {
        public float Pool, Fringe, Bank, Core;
    }

    public static class RM_FireEcoKernel
    {
        /// <summary>BiomeWorker_Pyrelands.GetScore: -100 when generation is off or the tile is water, 0 outside the climate band (rainfall is
        /// half-open, like vanilla's workers), else a base score rising with warmth and rainfall.</summary>
        public static float BiomeScore(bool generationEnabled, bool hasTile, bool waterCovered, float temperature, float rainfall,
            float elevation, bool mountainousOrImpassable, float tMin, float tMax, float rMin, float rMax, float eMin, float eMax,
            float baseScore, float degreeWeight, float rainfallDivisor)
        {
            if (!generationEnabled)
            {
                return -100f;
            }
            if (!hasTile || waterCovered)
            {
                return -100f;
            }
            if (temperature < tMin || temperature > tMax)
            {
                return 0f;
            }
            if (rainfall < rMin || rainfall >= rMax)
            {
                return 0f;
            }
            if (elevation < eMin || elevation > eMax)
            {
                return 0f;
            }
            if (mountainousOrImpassable)
            {
                return 0f;
            }
            float divisor = rainfallDivisor > 0.0001f ? rainfallDivisor : 1f;
            return baseScore + (temperature - tMin) * degreeWeight + (rainfall - rMin) / divisor;
        }

        /// <summary>Vanilla BiomeWorker_AridShrubland's score, the rival the Pyrelands has to out-bid on its band.</summary>
        public static float AridShrublandScore(float temperature, float rainfall)
        {
            return 22.5f + (temperature - 20f) * 2.2f + (rainfall - 600f) / 100f;
        }

        public static bool IsPyrelandsGround(string terrainDefName)
        {
            return terrainDefName != null && terrainDefName.StartsWith("RM_FE_", StringComparison.Ordinal);
        }

        /// <summary>The fire-tick gate's ground (PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED): ANY Pyrelands ground (an `RM_FE_` terrain, deep
        /// ash included, since deep ash is ~85% of the biome), plus vanilla Soil/Sand/Gravel/SoilRich. The
        /// ground alone opts in nothing: the hook ANDs it with the map's biome gate (ScorchableHere, FireEcologyOnMap). Widened from `RM_FE_Ground_*` alone, which would silence ash dusting, scorch-fruit and the burn
        /// stamp on every deep-ash cell.</summary>
        public static bool IsScorchableGround(string n)
        {
            if (n == null)
            {
                return false;
            }
            return IsPyrelandsGround(n) || n == "Sand" || n == "Gravel" || n == "Soil" || n == "SoilRich";
        }

        public const string DeepAshDefName = "RM_FE_Ash_Deep";

        /// <summary>The burn stamp's gate: master on, the bonus on, a spawned ground fire (not a burning pawn) on scorchable ground.
        /// Independent of the ash-dusting and scorch-fruit toggles.</summary>
        public static bool BurnStampMay(bool pyrelandsEnabled, bool bonusOn, bool spawned, bool attachedToPawn, bool scorchable)
        {
            return pyrelandsEnabled && bonusOn && spawned && !attachedToPawn && scorchable;
        }

        /// <summary>Fresh-burn bonus: base x max(0, 1 - age/duration), on its own clock; rain never takes it away (owner, d_blackrain_stop_wipe:
        /// black rain's watered lift stacks on top). burnTick &lt; 0 = never burned; a stamp from the future (another game) counts as never.</summary>
        public static float BurnBonus(int burnTick, int now, float bonus, int durationTicks)
        {
            if (burnTick < 0 || now < burnTick || durationTicks <= 0 || bonus <= 0f)
            {
                return 0f;
            }
            float f = 1f - (float)(now - burnTick) / durationTicks;
            if (f <= 0f)
            {
                return 0f;
            }
            return bonus * (f > 1f ? 1f : f);
        }

        /// <summary>Deep-ash fertility (design §3): watered or dry, plus the burn bonus, clamped to [0, cap].</summary>
        public static float AshFertility(float dry, float watered, bool isWatered, bool waterOn, float bonus, float cap)
        {
            float v = (waterOn && isWatered ? watered : dry) + (bonus > 0f ? bonus : 0f);
            if (v > cap)
            {
                v = cap;
            }
            return v < 0f ? 0f : v;
        }

        /// <summary>Days of bonus left on the clock alone (the inspect line), 0 when none.</summary>
        public static float BonusDaysLeft(int burnTick, int now, int durationTicks)
        {
            if (burnTick < 0 || now < burnTick || durationTicks <= 0)
            {
                return 0f;
            }
            int left = durationTicks - (now - burnTick);
            return left <= 0 ? 0f : left / 60000f;
        }

        /// <summary>A watered-until stamp: the later of the old stamp and now + ticks.</summary>
        public static int ExtendWatered(int oldUntil, int now, int ticks)
        {
            int until = now + ticks;
            return until > oldUntil ? until : oldUntil;
        }

        /// <summary>PyrelandsWetRoots: the temperature a plant's roots feel on watered ash, coolingC below its cell's.</summary>
        public static float WetRootTemperature(float cellTemp, float coolingC)
        {
            return cellTemp - (coolingC > 0f ? coolingC : 0f);
        }

        /// <summary>PyrelandsWetRoots: vanilla's growth season (PlantUtility.GrowthSeasonNow: minGrowth &lt; T &lt; maxGrowth) for a plant
        /// on watered ash. Only the hot side moves: at or past maxGrowth the cooled root temperature is tested instead, so wet roots can
        /// open a season the heat shut and never shut one, and a cold cell never counts as warmer (map w 2026-11-08, 58.8 C: rice read
        /// "0% (out of temperature growth range)" under our own "grows as if 27F cooler" line).</summary>
        public static bool WetRootGrowthSeason(float cellTemp, float minGrowth, float maxGrowth, float coolingC)
        {
            if (cellTemp < maxGrowth)
            {
                return cellTemp > minGrowth;
            }
            float roots = WetRootTemperature(cellTemp, coolingC);
            return roots > minGrowth && roots < maxGrowth;
        }

        /// <summary>ASH_FIELD_FIX_FORGETS_THE_WATER (6): a Black Rain waters an unroofed cell until its stamp, and only while the setting
        /// still gives it hours. Setting blackRainWaterHours to 0 switches the water off at once, not when the old stamp runs out.</summary>
        public static bool BlackRainWaters(int wateredUntil, int now, float waterHours, bool roofed)
        {
            return waterHours > 0f && wateredUntil > now && !roofed;
        }

        /// <summary>ASH_FIELD_FIX_FORGETS_THE_WATER (7): a watered-until stamp ran out inside the last `window` ticks (wet turned dry),
        /// so the fertility overlay must be redrawn; the dry-to-wet edge alone left a stale green overlay.</summary>
        public static bool WateredExpiredWithin(int wateredUntil, int now, int window)
        {
            return wateredUntil > 0 && wateredUntil <= now && wateredUntil > now - window;
        }

        /// <summary>Ambient ash (design §5a): the biome's old Clear weight split between AshDrift (share) and plain Clear.</summary>
        public static void SplitClear(float clearWeight, bool ambientOn, float share, out float ashDrift, out float clear)
        {
            if (share < 0f) share = 0f;
            if (share > 1f) share = 1f;
            ashDrift = ambientOn ? clearWeight * share : 0f;
            clear = clearWeight - ashDrift;
        }

        /// <summary>RM_PyrelandsSettings.MechanicsOn: this mod's own master switch AND, when the Baroque Biomes shell is loaded, its
        /// "Pyrelands" roster toggle (biome_mod_unification_spec.md §5 arm 2). No shell (the standalone mod) = the master alone.</summary>
        public static bool MechanicsOn(bool modMaster, bool shellPresent, bool shellOn)
        {
            return modMaster && (!shellPresent || shellOn);
        }

        /// <summary>RM_JobGiver_BurrowOnFire: a burrow may start unless the last one TIMED OUT less than cooldownTicks ago.
        /// lastTimeoutTick &lt; 0 = never timed out; now &lt; lastTimeoutTick (a record from another game) = expired.</summary>
        public static bool BurrowMayStart(int now, int lastTimeoutTick, int cooldownTicks)
        {
            return lastTimeoutTick < 0 || now < lastTimeoutTick || now - lastTimeoutTick >= cooldownTicks;
        }

        /// <summary>ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE: a heat-category hit (DamageDef.armorCategory Heat) sends an
        /// opted-in burrower into its dome at once, fire near or not. Refused when the mod or the burrow/dome switches are
        /// off, the pawn is dead or downed (it cannot curl up), or it is in a mental state (an enraged animal fights; the
        /// state's own think node owns its jobs).</summary>
        public static bool DomeOnHeatHit(bool heatDamage, bool optedIn, bool mechanicsOn, bool burrowOn, bool domeOn,
            bool alive, bool downed, bool mentalState)
        {
            return heatDamage && optedIn && mechanicsOn && burrowOn && domeOn && alive && !downed && !mentalState;
        }

        /// <summary>The dome's heat hold after a hit at `now`: never shortened by a later, shorter hold.</summary>
        public static int BurrowHeatHoldUntil(int now, int currentHoldUntil, int holdTicks)
        {
            int until = now + Math.Max(0, holdTicks);
            return currentHoldUntil > until ? currentHoldUntil : until;
        }

        /// <summary>BURROWER_FLEES_LARGE_FIRE: vanilla's JobGiver_AnimalFlee sits in AnimalConstant and is asked every 30 ticks
        /// for a wild animal. With 60+ fires near and one inside 10 cells it hands out a Flee that interrupts any job, the
        /// dome included (map w, pass 18: a domed ashwallow surfaced 2.2 cells from a creeping front and ran; earlier, one
        /// fled instead of diving and was killed). What a burrower's flee giver answers instead:
        /// 0 = vanilla's answer stands, 1 = nothing (stay domed, or keep grazing until the front is in dive range), 2 = dive.</summary>
        public static int BurrowerFleeAnswer(bool burrower, bool burrowed, bool fleeFromFire, bool wouldDive)
        {
            if (!burrower)
            {
                return 0;
            }
            if (burrowed)
            {
                return 1;
            }
            if (!fleeFromFire)
            {
                return 0;
            }
            return wouldDive ? 2 : 1;
        }

        /// <summary>RM_JobDriver_Burrow surfaces only when no free fire is within its radius AND the last heat hit's hold
        /// has run out; heatHoldUntil &lt; 0 = never hit.</summary>
        public static bool BurrowMayEmerge(int now, int heatHoldUntil, bool fireNear)
        {
            return !fireNear && (heatHoldUntil < 0 || now >= heatHoldUntil);
        }

        /// <summary>FIRE_SCAN_DIAGNOSE_BIG_BURN_COST: a burrowed pawn's "is a fire still near" scan walks every Fire on the map, and
        /// the burrow wait toil asked it EVERY tick, so 20 burrowers under a thousand-fire burn paid 20,000 distance tests a tick.
        /// It is now asked once per `interval` ticks, staggered by the pawn's id so burrowers do not all scan on the same tick.
        /// interval &lt;= 1 = every tick.</summary>
        public static bool BurrowEmergeCheckDue(int now, int pawnId, int interval)
        {
            if (interval <= 1)
            {
                return true;
            }
            long phase = ((long)now + (pawnId & 0x7fffffff)) % interval;
            return phase == 0;
        }

        /// <summary>FIRE_SCAN_DIAGNOSE_BIG_BURN_COST: which "fire near" scan is cheaper — walking the map's fire list (one distance
        /// test per fire) or the radial cells within the radius (one thing-list read per cell). Cells win only when the burn holds
        /// more fires than the disc holds cells.</summary>
        public static bool FireScanByCells(int fireCount, int radialCellCount)
        {
            return radialCellCount > 0 && fireCount > radialCellCount;
        }

        /// <summary>PYRE_BURROWERS_DIAGNOSE_FLEE_BEFORE_DIVE: the burn-line's dive nudge. The burrow giver sits at Animal_PreWander and
        /// is only asked at a job boundary, so on a cold first burn a grazer mid-GotoWander dived 120-380 ticks late (once never).
        /// While anything burns, a burrower whose own giver WOULD dive now, idling in a wander/wait job, not already burrowed, and
        /// not nudged inside minGapTicks, gets its think tree re-asked at once (CheckForJobOverride: the tree, not this, still
        /// decides, so a higher node such as AnimalFlee keeps its priority). lastNudgeTick &lt; 0 = never; now &lt; it = another game.</summary>
        public static bool BurrowNudgeDue(bool anyBurn, bool wouldDive, bool burrowedOrDiving, bool idleJob, int now, int lastNudgeTick, int minGapTicks)
        {
            if (!anyBurn || !wouldDive || burrowedOrDiving || !idleJob)
            {
                return false;
            }
            return lastNudgeTick < 0 || now < lastNudgeTick || now - lastNudgeTick >= minGapTicks;
        }

        /// <summary>The fire-tick postfix, before any roll: master on, one of the two outcomes on, a spawned ground fire (not a burning pawn)
        /// on scorchable ground.</summary>
        public static bool FireTickMayRoll(bool pyrelandsEnabled, bool ashOn, bool fruitOn, bool spawned, bool attachedToPawn, bool scorchable)
        {
            if (!pyrelandsEnabled || (!ashOn && !fruitOn) || !spawned || attachedToPawn)
            {
                return false;
            }
            return scorchable;
        }

        /// <summary>FIRE_ECOLOGY_DIAGNOSE_FOREST_FIRES_FRUIT: fire ecology (ash dusting, the burn stamp, scorch-fruit) runs on a map only
        /// when its biome is the Pyrelands or the cross-biome opt-in names it (CrossBiomeApplies). Without this a temperate-forest
        /// fire on vanilla Soil dusted ash, stamped burns and grew scorch-fruit, because the vanilla soils are scorchable ground.</summary>
        public static bool FireEcologyOnMap(bool nativeBiome, bool crossBiomeApplies)
        {
            return nativeBiome || crossBiomeApplies;
        }

        /// <summary>The fire-tick hook's `scorchable` input: scorchable ground (IsScorchableGround) on a map fire ecology runs on.</summary>
        public static bool ScorchableHere(bool ecologyOnMap, string terrainDefName)
        {
            return ecologyOnMap && IsScorchableGround(terrainDefName);
        }

        /// <summary>Per-interval ash chance: the per-tick chance times the batch size, so a watched and an unwatched fire roll alike.</summary>
        public static float DustChance(float perTick, int delta)
        {
            return perTick * delta;
        }

        // ── The drift field (PyrelandsDriftField): one static low-frequency noise per map gives every cell a target ash
        // level 0..3 (AshDepthPerLevel of sand depth each). Conductor ruling 2026-11-07 on map s: "make the drifts fewer, of varied size and clustered (pooled
        // against walls and along the burn edge), rather than redrawing the grain again." A hashed third of a scar's cells at
        // thickness 1 read as polka dots: every drift alone, all one size, evenly spread. The cuts are quantiles of the map's
        // own noise, so the shares below hold whatever the noise's spread turns out to be.

        /// <summary>Above this share of the field a lee or burn-edge cell pools a drift; below it the bonus is dropped, so a long
        /// wall or a scar's rim holds pools and gaps instead of an outline.</summary>
        public const float DriftPoolQuantile = 0.5f;
        /// <summary>The top fifth of the field holds a drift at all: with the lee and edge pools that is ~20-25% of a scar.</summary>
        public const float DriftFringeQuantile = 0.8f;
        /// <summary>Banks (thickness 2) and cores (3) sit inside the fringes, on the field's highest ground.</summary>
        public const float DriftBankQuantile = 0.91f;
        public const float DriftCoreQuantile = 0.965f;
        /// <summary>The deepest a scar or drift-field target goes, in drift levels (AshDepthPerLevel each).</summary>
        public const int DriftTargetMax = 3;
        /// <summary>A fire must have burned this long before its cell counts the burn edge: early in a cell's fire the grass ahead
        /// of the front has not caught yet, and every interior cell would read as rim.</summary>
        public const int ScarEdgeSettleTicks = 600;

        /// <summary>Quantile cut points of a map's drift-field noise; sorts the samples in place.</summary>
        public static RM_DriftCuts DriftCuts(float[] samples)
        {
            var cuts = new RM_DriftCuts();
            if (samples == null || samples.Length == 0)
            {
                cuts.Pool = cuts.Fringe = cuts.Bank = cuts.Core = float.MaxValue;
                return cuts;
            }
            Array.Sort(samples);
            cuts.Pool = Quantile(samples, DriftPoolQuantile);
            cuts.Fringe = Quantile(samples, DriftFringeQuantile);
            cuts.Bank = Quantile(samples, DriftBankQuantile);
            cuts.Core = Quantile(samples, DriftCoreQuantile);
            return cuts;
        }

        private static float Quantile(float[] sorted, float q)
        {
            int i = (int)(q * (sorted.Length - 1));
            if (i < 0) i = 0;
            if (i >= sorted.Length) i = sorted.Length - 1;
            return sorted[i];
        }

        /// <summary>A cell's target ash thickness 0..3: the field's height, plus one in the lee of an edifice and one at a burn edge
        /// where the field is at least middling.</summary>
        public static int DriftTarget(float noise, RM_DriftCuts cuts, bool lee, bool burnEdge)
        {
            int t = noise >= cuts.Core ? 3 : noise >= cuts.Bank ? 2 : noise >= cuts.Fringe ? 1 : 0;
            if (noise >= cuts.Pool)
            {
                if (lee) t++;
                if (burnEdge) t++;
            }
            return t > DriftTargetMax ? DriftTargetMax : t;
        }

        /// <summary>A burning cell's ash after one dusting: one drift level deeper, never past the cell's drift-field target, never
        /// thinned (a long burn can never re-roll its way past the target, and a deeper fall already lying stays).</summary>
        public static float ScarAshStep(float depth, int target)
        {
            float want = target * AshDepthPerLevel;
            if (depth >= want - AshDepthEpsilon) return depth;
            float next = depth + AshDepthPerLevel;
            return next > want ? want : next;
        }

        /// <summary>A scar laid at once (yesterday's fire, a ruin): the cell's target depth, never thinning a deeper drift.</summary>
        public static float ScarAshLaid(float depth, int target)
        {
            float want = target * AshDepthPerLevel;
            return depth > want ? depth : want;
        }

        public static bool UnderFruitCap(int existing, int cap)
        {
            return existing < cap;
        }

        // ── Ash on vanilla sand (PyrelandsAshSand.cs). Owner, by card, 2026-11-08: "Rebuild ash on vanilla sand?" -> "Yes, rebuild
        // on sand". Ash is the Odyssey sand depth grid (0..1) on a map fire ecology runs on: ash fall lays it through the weather's
        // own sandRate (vanilla SteadyEnvironmentEffects.AddFallenSandAt, snow's code path), a fire lays it on its cell, black rain
        // carries it off, and colonists clear it with vanilla's clear-snow-and-sand job.

        /// <summary>One drift level in sand depth (a drift level is thickness 1..4): the drift field's targets convert at this.</summary>
        public const float AshDepthPerLevel = 0.25f;
        public const float AshDepthEpsilon = 0.001f;
        /// <summary>Ash shallower than this is none: vanilla's own None buildup category (WeatherBuildupUtility, below 0.03).</summary>
        public const float AshVisibleDepth = 0.03f;
        /// <summary>Vanilla's sand wear per steady-effects visit on an open-sky cell with no sand falling (SteadyEnvironmentEffects,
        /// SandDissipateRate 1/180). A cell is visited every ~1,667 ticks (0.0006 of the map a tick), 36 times a day: 0.2 a day.</summary>
        public const float VanillaSandWear = 1f / 180f;
        /// <summary>Dry ash on an ash map wears at this share of vanilla's sand: 0.1 depth a day, so a full cover lasts ~10 days and a
        /// scar's 0.25-0.75 lasts 2.5-7.5 (the retired filth expired 6-9 days after its last thickening).</summary>
        public const float AshDryWearShare = 0.5f;
        /// <summary>Rain carries off this much ash a visit at rainRate 1: one drift level, as vanilla's rainWashes thinned the filth one
        /// level on a Rand.Chance(rainRate) roll. Black rain (rainRate 1.1) clears a full cover in ~2.5 hours.</summary>
        public const float AshRainWashPerVisit = 0.25f;
        /// <summary>Cross-biome ambient ash at 100% coverage, as a share of the ash weathers' own sandRate.</summary>
        public const float AmbientAshShare = 0.1f;
        /// <summary>Cross-biome ambient ash falls only while the map's mean depth is below this (then dry wear takes over).</summary>
        public const float AmbientMeanDepthCap = 0.1f;

        /// <summary>The sand rate an ash weather adds on this map: its own sandRate times the rate setting on an ash map with ash fall
        /// on; nothing otherwise (the weather still blows, it lays nothing; and never sand on a map that does not draw ash).</summary>
        public static float AshWeatherSandRate(float ashWeatherRate, bool ashMap, bool accumulationOn, float rateMultiplier)
        {
            if (!ashMap || !accumulationOn || !(ashWeatherRate > 0f) || !(rateMultiplier > 0f)) return 0f;
            return ashWeatherRate * rateMultiplier;
        }

        /// <summary>The steady ambient ash rate of an opted-in foreign biome's map: the coverage slider's share of a tenth of ash fall's
        /// rate, falling only while the map's mean depth is under AmbientMeanDepthCap; 0 for the Pyrelands itself or off.</summary>
        public static float AmbientAshSandRate(bool crossBiomeApplies, bool nativeBiome, bool accumulationOn, float coverage,
            float ashFallRate, float rateMultiplier, float meanDepth)
        {
            if (nativeBiome || !crossBiomeApplies || !accumulationOn || !(coverage > 0f) || meanDepth >= AmbientMeanDepthCap) return 0f;
            return coverage * AmbientAshShare * ashFallRate * rateMultiplier;
        }

        /// <summary>What one steady-effects visit takes off an open-sky cell with no sand falling: vanilla's wear on any map that does
        /// not hold ash; on an ash map half that dry, plus the rain's wash (black rain is the one rain the Pyrelands has).</summary>
        public static float OutdoorSandWear(bool ashMap, float rainRate)
        {
            if (!ashMap) return VanillaSandWear;
            return VanillaSandWear * AshDryWearShare + AshRainWashPerVisit * (rainRate > 0f ? rainRate : 0f);
        }

        /// <summary>The ground cover's opacity over a cell of this ash depth: none below the visible depth, a gritty 0.4 at a dusting
        /// (the rough shader opens holes below 1), 0.9 at one old drift level (0.25, the old cover's x1), solid from 0.5.</summary>
        public static float AshCoverOpacity(float depth)
        {
            if (!(depth >= AshVisibleDepth)) return 0f;
            if (depth >= 0.5f) return 1f;
            if (depth >= AshDepthPerLevel) return 0.9f + 0.1f * (depth - AshDepthPerLevel) / (0.5f - AshDepthPerLevel);
            return 0.4f + 0.5f * (depth - AshVisibleDepth) / (AshDepthPerLevel - AshVisibleDepth);
        }

        /// <summary>Grass dust over a plant: 0 none, 1 the light overlay, 2 the full one.</summary>
        public static int AshDustLevel(float depth)
        {
            if (!(depth >= AshDustLightDepth)) return 0;
            return depth >= AshDustFullDepth ? 2 : 1;
        }

        /// <summary>A grass cell dusts light from here (~1.5 hours of ash fall) and full from AshDustFullDepth (~8 hours).</summary>
        public const float AshDustLightDepth = 0.08f;
        public const float AshDustFullDepth = 0.4f;

        /// <summary>True exactly once per id; the set is cleared wholesale when it passes a bound no live map reaches.</summary>
        public static bool MarkOnce(HashSet<int> rolled, int id, int bound)
        {
            if (rolled.Count > bound)
            {
                rolled.Clear();
            }
            return rolled.Add(id);
        }

        /// <summary>The late ruin sweep's subject (PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE): an unowned, destroyable, artificial
        /// building - a ruin wall, ancient junk, a utility building - never natural rock, a geyser (not destroyable) or anything a
        /// faction owns.</summary>
        public static bool IsScorchableRuin(bool artificial, bool hasFaction, bool destroyable, bool naturalRock)
        {
            return artificial && !hasFaction && destroyable && !naturalRock;
        }

        /// <summary>Does the ruin sweep lay deep ash on this cell? Not on water, and not where it already is deep ash (the visible scorch
        /// is then the loose-ash filth alone). The retired heavy/light rungs collapsed to this one step.</summary>
        public static bool RuinScorchLays(bool water, string currentTerrain)
        {
            return !water && currentTerrain != DeepAshDefName;
        }

        /// <summary>The scorch-fruit spot scan order over a fire's 3x3: its OWN cell first (the cell that just burned out; the fruit
        /// is Flammability 0, so the dying fire there cannot hurt it), then the eight neighbours.</summary>
        public static readonly int[] FruitSpotDx = { 0, -1, -1, -1, 0, 0, 1, 1, 1 };
        public static readonly int[] FruitSpotDz = { 0, -1, 0, 1, -1, 1, -1, 0, 1 };

        /// <summary>SCORCH_FRUIT_FIX_LANDS_ON_FIREBREAK: a pod lands only on bare, standable PYRELANDS GROUND (IsScorchableGround: deep
        /// ash or the scorchable soils), never on a floor or other unburnable ground beside the fire.</summary>
        public static bool FruitLandingLegal(bool inBounds, bool standable, bool hasPlant, bool scorchableGround)
        {
            return inBounds && standable && !hasPlant && scorchableGround;
        }

        /// <summary>SCORCH_FRUIT_FIX_LANDS_ON_FIREBREAK: what a save keeps of the roll set - only the ids of fires still burning, so a
        /// fire alive across a save/load does not roll twice and the saved list stays as small as the live burn.</summary>
        public static List<int> RolledStillBurning(HashSet<int> rolled, IEnumerable<int> liveFireIds)
        {
            var keep = new List<int>();
            if (rolled == null || liveFireIds == null) return keep;
            foreach (int id in liveFireIds)
            {
                if (rolled.Contains(id)) keep.Add(id);
            }
            return keep;
        }

        /// <summary>Index into FruitSpotDx/Dz of the first cell `legal(dx, dz)` accepts, or -1 when none does.</summary>
        public static int FirstFruitSpot(Func<int, int, bool> legal)
        {
            for (int i = 0; i < FruitSpotDx.Length; i++)
            {
                if (legal(FruitSpotDx[i], FruitSpotDz[i]))
                {
                    return i;
                }
            }
            return -1;
        }

        /// <summary>A fire's ONE scorch-fruit roll, deferred until it can land (SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES): returns the
        /// spot index when this fire takes its roll now, -1 when it does not — already rolled, or no legal spot yet because the grass
        /// it is burning still stands, so it waits for the ashes instead of spending the roll on a full 3x3. Taking the roll marks
        /// the fire; the chance and the map cap are the caller's.</summary>
        public static int TakeFruitRoll(HashSet<int> rolled, int fireId, int bound, Func<int, int, bool> legal)
        {
            if (rolled.Contains(fireId))
            {
                return -1;
            }
            return TakeFruitRollAt(rolled, fireId, bound, FirstFruitSpot(legal));
        }

        /// <summary>TakeFruitRoll with the spot already found (FIRE_SCAN_DIAGNOSE_BIG_BURN_COST: the fire-tick hook scans its 3x3 with
        /// a static method, no closure, and only for a fire not yet in `rolled`). spot &lt; 0 = no legal spot: the fire waits.</summary>
        public static int TakeFruitRollAt(HashSet<int> rolled, int fireId, int bound, int spot)
        {
            if (spot < 0 || rolled.Contains(fireId))
            {
                return -1;
            }
            MarkOnce(rolled, fireId, bound);
            return spot;
        }

        /// <summary>The once-per-fire roll set of ONE owner (the hook passes the Map). PYRE_SCORCHFRUIT_DIAGNOSE_FIRE_BEARS_NOTHING: a
        /// static set outlived a reload, the reloaded save re-issued the same thingIDNumbers to the next fires, and those fires found
        /// their ids already "rolled" and never fruited (0 fruit in a burned 24x24 cohort, 2/2 live, after earlier pieces of the same
        /// session had burned). A reload builds new Map objects, so a set keyed on the owner starts empty; a dead owner's set is
        /// collected with it.</summary>
        public static HashSet<int> RollSetFor(System.Runtime.CompilerServices.ConditionalWeakTable<object, HashSet<int>> tables, object owner)
        {
            return tables.GetValue(owner, _ => new HashSet<int>());
        }

        /// <summary>"a, b; c" -> ["a","b","c"]: comma / semicolon separated, trimmed, blanks dropped.</summary>
        public static List<string> ParseList(string text)
        {
            var result = new List<string>();
            if (string.IsNullOrEmpty(text))
            {
                return result;
            }
            string[] parts = text.Split(',', ';');
            for (int i = 0; i < parts.Length; i++)
            {
                string trimmed = parts[i].Trim();
                if (trimmed.Length > 0)
                {
                    result.Add(trimmed);
                }
            }
            return result;
        }

        /// <summary>Cross-biome opt-in (ash drift and fire ecology): never the native biome, "everywhere" covers all, else the named list.</summary>
        public static bool CrossBiomeApplies(bool enabled, bool hasBiome, bool isNative, bool everywhere, bool listed)
        {
            if (!enabled || !hasBiome || isNative)
            {
                return false;
            }
            return everywhere || listed;
        }

        /// <summary>The wild-plant allowlist on one cell's candidate list, in place: anything off the allowlist goes. On a foreign open cell
        /// (a mixed-biome patch on a Pyrelands map, not a cave cell) the native grasses that can grow there are supplied, because vanilla
        /// fills that list from the secondary biome alone and an empty list leaves the cell bare (ALLOWLIST_DIAGNOSE_BARE_MIXED_PATCHES).
        /// A native cell is never supplied: vanilla already offered what its wild order allows.</summary>
        public static void ApplyWildAllowlist<T>(List<T> candidates, IList<T> native, Func<T, bool> allowed, Func<T, bool> canGrow, bool foreignOpenCell)
        {
            for (int i = candidates.Count - 1; i >= 0; i--)
            {
                if (!allowed(candidates[i]))
                {
                    candidates.RemoveAt(i);
                }
            }
            if (!foreignOpenCell)
            {
                return;
            }
            for (int i = 0; i < native.Count; i++)
            {
                if (!candidates.Contains(native[i]) && canGrow(native[i]))
                {
                    candidates.Add(native[i]);
                }
            }
        }
    }
}
