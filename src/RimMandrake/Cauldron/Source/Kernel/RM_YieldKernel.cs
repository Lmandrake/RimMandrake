// Verse-free kernel of the Cauldron's metal yield and its readouts (CAULDRON_TREE_METAL_YIELD_1, CAULDRON_GPT_ENRICHMENT_1 part 4,
// CAULDRON_ENRICHMENT_VISUALS_1 V3): the growth-scaled metal count, the assay grade and the fleck band, plus the vent bloom's
// metal-load dose and who it applies to, the vent-ring condensate gardens, and the dewfall bead budget. RM_CompMetalYield.cs,
// RM_VentBloomExposure.cs, RM_CondensateGardens.cs, RM_CauldronDewfallVisuals.cs call these with the same expressions;
// SelfTest/CauldronFuzz.cs compiles this file alone (no Verse/RimWorld/UnityEngine).
using System;

namespace RimMandrake.Cauldron
{
    public enum RM_AssayBand { None = 0, Light = 1, Heavy = 2 }

    public static class RM_YieldKernel
    {
        public const int BeadIntervalTicks = 250;
        public const float BeadsPerInterval = 6f;
        public const int BeadCap = 400;
        public const int BloomIntervalTicks = 3451;
        public const float BaseSeverityPerInterval = 0.012f;

        // Mathf.InverseLerp
        public static float InverseLerp(float a, float b, float v)
        {
            if (a == b) return 0f;
            float t = (v - a) / (b - a);
            return t < 0f ? 0f : t > 1f ? 1f : t;
        }

        // Mathf.Lerp
        public static float Lerp(float a, float b, float t)
        {
            t = t < 0f ? 0f : t > 1f ? 1f : t;
            return a + (b - a) * t;
        }

        // ---- metal yield ------------------------------------------------------------------------------
        // The expected metal count (no rounding) for a trunk at `growth`. Unripe trunks (below harvestMinGrowth) yield nothing.
        public static float Expected(float growth, float harvestMinGrowth, float countAtMin, float countAtFull, float factor)
        {
            if (growth < harvestMinGrowth) return 0f;
            float t = InverseLerp(harvestMinGrowth, 1f, growth);
            return Lerp(countAtMin, countAtFull, t) * factor;
        }

        // What the harvest scales to before random rounding: off = 0; the lerp is taken without the ripeness gate (the harvest only
        // happens once the plant is harvestable).
        public static float AtHarvest(bool enabled, bool hasMetal, float growth, float harvestMinGrowth, float countAtMin, float countAtFull, float factor)
        {
            if (!enabled || !hasMetal) return 0f;
            float t = InverseLerp(harvestMinGrowth, 1f, growth);
            return Lerp(countAtMin, countAtFull, t) * factor;
        }

        // Expected metal as a fraction of the full-growth lode (0 while unripe, or with a zero full lode).
        public static float GradeFraction(float expected, float countAtFull, float factor)
        {
            float full = countAtFull * factor;
            return full > 0f ? expected / full : 0f;
        }

        // 0 trace, 1 fair, 2 rich, 3 lode
        public static int GradeTier(float frac)
        {
            return frac >= 0.95f ? 3 : frac >= 2f / 3f ? 2 : frac >= 1f / 3f ? 1 : 0;
        }

        // Which overlay a tree gets: heavy at heavyFrom, light at lightFrom, each falling back to the other if its art is missing.
        public static RM_AssayBand FleckBand(float frac, float lightFrom, float heavyFrom, bool hasLight, bool hasHeavy)
        {
            if (frac >= heavyFrom) return hasHeavy ? RM_AssayBand.Heavy : hasLight ? RM_AssayBand.Light : RM_AssayBand.None;
            if (frac >= lightFrom) return hasLight ? RM_AssayBand.Light : hasHeavy ? RM_AssayBand.Heavy : RM_AssayBand.None;
            return RM_AssayBand.None;
        }

        public static bool FlecksOn(bool flecksEnabled, bool gradeEnabled, bool yieldEnabled) { return flecksEnabled && gradeEnabled && yieldEnabled; }

        // ---- the bloom's metal load -------------------------------------------------------------------
        // Only once the weather transition has finished, on the vanilla toxic cadence, with the toggle on.
        public static bool BloomTicks(int ticksGame, bool enabled, bool curIsBloom, bool lerpIsOne)
        {
            return ticksGame % BloomIntervalTicks == 0 && enabled && curIsBloom && lerpIsOne;
        }

        public static float Dose(float factor, float toxicResistance, float toxicEnvironmentResistance, float exposureWeight)
        {
            float amount = BaseSeverityPerInterval * factor;
            amount *= Math.Max(1f - toxicResistance, 0f);
            amount *= Math.Max(1f - toxicEnvironmentResistance, 0f);
            amount *= exposureWeight;
            return amount;
        }

        // Dead, unspawned, immune to game-condition effects, not flesh, under a roof, or a native animal: no dose.
        public static bool Eligible(bool exists, bool dead, bool spawned, bool immune, bool flesh, bool roofed, bool animal, bool nativeAnimal)
        {
            if (!exists || dead || !spawned) return false;
            if (immune) return false;
            if (!flesh) return false;
            if (roofed) return false;
            if (animal && nativeAnimal) return false;
            return true;
        }

        // ---- dewfall ----------------------------------------------------------------------------------
        // How many bead cells to try this interval: none at density <= 0 or at the cap.
        public static int BeadCap_(float density) { return (int)Math.Round(BeadCap * density); }

        public static bool BeadsSpawn(float density, int existing, int cap) { return density > 0f && existing < cap; }

        // GenMath.RoundRandom(x): floor(x) plus one with probability frac(x). roll01 in [0,1).
        public static int RoundRandom(float x, float roll01)
        {
            int f = (int)Math.Floor(x);
            return roll01 < x - f ? f + 1 : f;
        }

        // The weather flipped between ticks: remesh once each way (only when the saturation art is live).
        public static bool DewFlip(bool initialised, bool lastDew, bool dew) { return initialised && dew != lastDew; }
        public static bool RemeshOnFlip(bool flipped, bool saturationEnabled, bool artActive) { return flipped && saturationEnabled && artActive; }

        public static bool CanBead(bool roofed, bool fogged, bool standable, bool hasTerrain, bool water, bool home, bool hasRoom, bool roomOutdoors)
        {
            if (roofed || fogged || !standable) return false;
            if (!hasTerrain || water) return false;
            if (home) return false;
            return !hasRoom || roomOutdoors;
        }

        // ---- condensate gardens -----------------------------------------------------------------------
        // A shore cell is a land cell next to one of the named terrains; the water itself is not its own shore.
        public static bool IsShore(bool onNamedTerrain, bool anyNeighbourNamed) { return !onNamedTerrain && anyNeighbourNamed; }

        public static bool PlantAllowed(bool hasPlant, bool inZone, bool canEverPlant) { return !hasPlant && !inZone && canEverPlant; }
    }
}
