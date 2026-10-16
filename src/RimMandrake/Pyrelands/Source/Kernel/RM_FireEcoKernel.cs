using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the fire-ecology hooks and the biome (FireEcologyHook.cs, WildPlantAllowlist.cs, RM_PyrelandsMod.cs): the
    // biome placement score, the terrain-family predicates, the ash-dusting / scorch-fruit gates, the ash-fall rate and
    // attempt count, the once-per-fire roll set, the cross-biome list parser and the wild-plant allowlist. The mod calls these with the
    // same expressions; the offline fuzz drives them.

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
        /// ash included, since deep ash is ~85% of the biome) except the firebreak, plus vanilla Soil/Sand/Gravel/SoilRich. The
        /// ground alone opts in nothing: the hook ANDs it with the map's biome gate (ScorchableHere, FireEcologyOnMap). Widened from `RM_FE_Ground_*` alone, which would silence ash dusting, scorch-fruit and the burn
        /// stamp on every deep-ash cell.</summary>
        public static bool IsScorchableGround(string n)
        {
            if (n == null || n == FirebreakDefName)
            {
                return false;
            }
            return IsPyrelandsGround(n) || n == "Sand" || n == "Gravel" || n == "Soil" || n == "SoilRich";
        }

        public const string FirebreakDefName = "RM_FE_FirebreakLine";
        public const string DeepAshDefName = "RM_FE_Ash_Deep";

        /// <summary>The retired ladder rungs, kept one cycle as hidden legacy aliases and re-laid to deep ash on load.</summary>
        public static readonly string[] LegacyAshDefNames = { "RM_FE_Ash_Trace", "RM_FE_Ash_Light", "RM_FE_Ash_Heavy" };

        public static bool IsLegacyAsh(string n)
        {
            return n != null && Array.IndexOf(LegacyAshDefNames, n) >= 0;
        }

        /// <summary>The burn stamp's gate: master on, the bonus on, a spawned ground fire (not a burning pawn) on scorchable ground.
        /// Independent of the ash-dusting and scorch-fruit toggles.</summary>
        public static bool BurnStampMay(bool pyrelandsEnabled, bool bonusOn, bool spawned, bool attachedToPawn, bool scorchable)
        {
            return pyrelandsEnabled && bonusOn && spawned && !attachedToPawn && scorchable;
        }

        /// <summary>Fresh-burn bonus (design §4): base x max(0, 1 - age/duration - rainSince/rainBudget), capped at base. burnTick &lt; 0 =
        /// never burned; a stamp from the future (another game) counts as never. rainFade off = time only.</summary>
        public static float BurnBonus(int burnTick, int now, float bonus, int durationTicks, float rainSince, float rainBudget, bool rainFade)
        {
            if (burnTick < 0 || now < burnTick || durationTicks <= 0 || bonus <= 0f)
            {
                return 0f;
            }
            float f = 1f - (float)(now - burnTick) / durationTicks;
            if (rainFade && rainBudget > 0f && rainSince > 0f)
            {
                f -= rainSince / rainBudget;
            }
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

        /// <summary>RM_JobDriver_Burrow surfaces only when no free fire is within its radius AND the last heat hit's hold
        /// has run out; heatHoldUntil &lt; 0 = never hit.</summary>
        public static bool BurrowMayEmerge(int now, int heatHoldUntil, bool fireNear)
        {
            return !fireNear && (heatHoldUntil < 0 || now >= heatHoldUntil);
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

        public static bool UnderFruitCap(int existing, int cap)
        {
            return existing < cap;
        }

        /// <summary>The ash-fall rate this map gets this batch, or -1 when it gets none: ash fall full, cinderfall reduced, an opted-in
        /// foreign biome the coverage slider, anything else nothing.</summary>
        public static float AshRate(bool ashFall, bool cinderfall, float cinderFactor, bool nativeBiome, bool crossBiomeApplies,
            float crossCoverage, float rateMultiplier)
        {
            float rate;
            if (ashFall)
            {
                rate = 1f;
            }
            else if (cinderfall)
            {
                rate = cinderFactor;
            }
            else if (!nativeBiome && crossBiomeApplies)
            {
                rate = crossCoverage;
            }
            else
            {
                return -1f;
            }
            return rate * rateMultiplier;
        }

        /// <summary>Deposit attempts this batch: map area per attempt scaled by the rate; a rate of zero deposits nothing, any positive
        /// rate deposits at least one.</summary>
        public static int AshAttempts(int area, float cellsPerAttempt, float rate)
        {
            if (rate <= 0f)
            {
                return 0;
            }
            int attempts = (int)((float)area / cellsPerAttempt * rate);
            return attempts < 1 ? 1 : attempts;
        }

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
        /// ash or the scorchable soils), never on a firebreak, a floor or other unburnable ground beside the fire.</summary>
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
            int spot = FirstFruitSpot(legal);
            if (spot < 0)
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
    }
}
