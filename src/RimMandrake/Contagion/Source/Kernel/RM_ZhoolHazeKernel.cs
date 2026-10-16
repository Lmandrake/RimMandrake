// Verse-free kernel of the zhool's haze (CompZhoolHaze): which plants the haze may turn, what each turns into, the
// per-sample conversion chance and the message throttle. The comp calls these with the same expressions;
// SelfTest/ContagionFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.Contagion
{
    // What a hazed plant becomes, by its shape: a tree turns into a tree, ground cover into ground cover, anything
    // else into a shrub. The defs behind each are data on the comp (CompProperties_ZhoolHaze), never named here.
    public enum HazeShape { None = 0, Tree = 1, GroundCover = 2, Shrub = 3 }

    public static class RM_ZhoolHazeKernel
    {
        public const float MinRate = 0.1f, MaxRate = 5f;
        public const float MinDensity = 0.25f, MaxDensity = 3f;

        // Ground cover is either drawn at the floor layer (the project's ground-cover ruling, 2026-10-14) or a
        // multi-mesh carpet (vanilla grass draws 9 meshes per cell; bushes and trees draw 1).
        public static HazeShape Classify(bool isTree, bool floorLayer, int maxMeshCount)
        {
            if (isTree) return HazeShape.Tree;
            if (floorLayer || maxMeshCount > 1) return HazeShape.GroundCover;
            return HazeShape.Shrub;
        }

        // A plant the haze may turn. Never: with conversion off; off our own biomes (biome mechanics are promised inside
        // our biomes only); a plant already of the Contagion's own flesh (immune); a stump; a plant carrying comps of
        // its own (anima, gauranlen, polux and the like are special-purpose trees, never wild flora); a player's
        // sown crop unless the crop switch is on.
        public static bool Eligible(bool conversionEnabled, bool ourBiome, bool immune, bool isStump, bool hasComps,
                                    bool sown, bool convertCrops)
        {
            if (!conversionEnabled || !ourBiome || immune || isStump || hasComps) return false;
            if (sown && !convertCrops) return false;
            return true;
        }

        public static float ClampRate(float rate)
        {
            if (float.IsNaN(rate)) return 1f;
            return Math.Max(MinRate, Math.Min(MaxRate, rate));
        }

        public static float ClampDensity(float density)
        {
            if (float.IsNaN(density)) return 1f;
            return Math.Max(MinDensity, Math.Min(MaxDensity, density));
        }

        // The chance that one sampled eligible plant turns this scan.
        public static float Chance(float baseChance, float rate)
        {
            float c = Math.Max(0f, baseChance) * ClampRate(rate);
            return Math.Min(1f, c);
        }

        // Haze puffs per emission: a fractional density rolls the remainder (roll in [0,1)).
        public static int Puffs(float basePuffs, float density, float roll)
        {
            float want = Math.Max(0f, basePuffs) * ClampDensity(density);
            int whole = (int)Math.Floor(want);
            return whole + (roll < want - whole ? 1 : 0);
        }

        // The readable sign: at most one message per cooldown, game-wide. lastTick > now means a new game (or a loaded
        // earlier save) started since the last message, so the throttle resets.
        public static bool MessageDue(int now, int lastTick, int cooldownTicks)
        {
            if (lastTick < 0 || lastTick > now) return true;
            return now - lastTick >= Math.Max(0, cooldownTicks);
        }
    }
}
