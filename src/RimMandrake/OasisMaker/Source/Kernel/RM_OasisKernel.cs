// Verse-free kernel of the oasis-maker: the shade/rock scoring of a site, the quality it earns, the placement verdict, the machine's
// Dormant/Attuning/Working state machine, and the ring-by-ring terrain growth (ring bands, ladders, time per rung). The placement scorer, the
// place worker and the comp call these with the same expressions; SelfTest/OasisMakerFuzz.cs compiles this file alone. Keep it free of
// Verse/RimWorld/UnityEngine (a `using Verse;` here breaks the self-test build, which is the guard rail).
// Unity's Mathf.RoundToInt rounds half to even (Math.Round); Mathf.Lerp clamps t; Mathf.InverseLerp clamps and returns 0 when a == b.
using System;

namespace RimMandrake.OasisMaker
{
    public enum RM_OasisMakerState : byte
    {
        Dormant,
        Attuning,
        Working,
    }

    public enum RM_OasisPlacement { Allowed, NeedsShade, NeedsRock, NeedsBoth }

    /// <summary>The map as the scorer sees it, one cell at a time.</summary>
    public interface IOasisGrid
    {
        bool InBounds(int x, int z);
        bool Roofed(int x, int z);
        /// <summary>A building at fill 0.8+ or a plant at visual size 1.5+ stands on this cell.</summary>
        bool CastsShade(int x, int z);
        /// <summary>Natural rock edifice or rough-stone terrain.</summary>
        bool IsRock(int x, int z);
    }

    public static class RM_OasisKernel
    {
        // ---------------------------------------------------------------- scoring
        public const int ShadeSearchRadius = 2;
        public const float ShadeThreshold = 0.5f;

        public static float Clamp01(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }

        public static float Lerp(float a, float b, float t) { return a + (b - a) * Clamp01(t); }

        public static float InverseLerp(float a, float b, float value)
        {
            return a != b ? Clamp01((value - a) / (b - a)) : 0f;
        }

        /// <summary>
        /// Shade at a cell, 0..1: a roofed cell is fully shaded; otherwise the best falloff against a shade-casting neighbour within
        /// <see cref="ShadeSearchRadius"/>: 1 - distance / (radius + 1). Out of bounds is 0.
        /// </summary>
        public static float ShadeAt(IOasisGrid g, int x, int z)
        {
            if (!g.InBounds(x, z)) return 0f;
            if (g.Roofed(x, z)) return 1f;
            float best = 0f;
            for (int dz = -ShadeSearchRadius; dz <= ShadeSearchRadius; dz++)
            {
                for (int dx = -ShadeSearchRadius; dx <= ShadeSearchRadius; dx++)
                {
                    if (dx == 0 && dz == 0) continue;
                    int nx = x + dx, nz = z + dz;
                    if (!g.InBounds(nx, nz) || !g.CastsShade(nx, nz)) continue;
                    float dist = (float)Math.Sqrt(dx * dx + dz * dz);
                    float score = Clamp01(1f - dist / (ShadeSearchRadius + 1));
                    if (score > best) best = score;
                }
            }
            return best;
        }

        /// <summary>Counts, over the square of <paramref name="radius"/> around the centre, the shaded cells (shade at or over the threshold) and the rock cells.</summary>
        public static void ScoreAt(IOasisGrid g, int cx, int cz, int radius, out int shade, out int rock)
        {
            shade = 0;
            rock = 0;
            for (int dz = -radius; dz <= radius; dz++)
            {
                for (int dx = -radius; dx <= radius; dx++)
                {
                    int x = cx + dx, z = cz + dz;
                    if (!g.InBounds(x, z)) continue;
                    if (ShadeAt(g, x, z) >= ShadeThreshold) shade++;
                    if (g.IsRock(x, z)) rock++;
                }
            }
        }

        public static bool MeetsFloor(int shade, int rock, int shadeFloor, int rockFloor)
        {
            return shade >= shadeFloor && rock >= rockFloor;
        }

        /// <summary>0..1: how far shade and rock sit above their floors toward their "excellent" ceilings, averaged so one axis cannot buy full quality.</summary>
        public static float Quality01(int shade, int rock, int shadeFloor, int shadeExcellent, int rockFloor, int rockExcellent)
        {
            float shadeQ = InverseLerp(shadeFloor, shadeExcellent, shade);
            float rockQ = InverseLerp(rockFloor, rockExcellent, rock);
            return Clamp01((shadeQ + rockQ) / 2f);
        }

        /// <summary>The ring count a site earns: the poor-placement cap blended to the excellent-placement cap by quality (rounded half to even).</summary>
        public static int RadiusCap(int minCap, int maxCap, float quality)
        {
            return (int)Math.Round(Lerp(minCap, maxCap, quality));
        }

        public static float SpeedMultiplier(float quality)
        {
            return Lerp(0.5f, 1.5f, quality);
        }

        /// <summary>The place worker's verdict: a disabled mechanic never blocks; otherwise the floors decide and the message names what is missing.</summary>
        public static RM_OasisPlacement Verdict(bool masterEnabled, int shade, int rock, int shadeFloor, int rockFloor)
        {
            if (!masterEnabled) return RM_OasisPlacement.Allowed;
            if (MeetsFloor(shade, rock, shadeFloor, rockFloor)) return RM_OasisPlacement.Allowed;
            bool needsShade = shade < shadeFloor;
            bool needsRock = rock < rockFloor;
            if (needsShade && needsRock) return RM_OasisPlacement.NeedsBoth;
            return needsShade ? RM_OasisPlacement.NeedsShade : RM_OasisPlacement.NeedsRock;
        }

        // ---------------------------------------------------------------- state machine
        public const int RareTickInterval = 250;

        /// <summary>
        /// One rare tick of the machine's state. Dormant -> Attuning when the site is valid; Attuning -> Dormant when it stops being valid,
        /// else counts up and becomes Working after the attuning days (quality is locked ONCE, on the first such transition);
        /// Working -> Dormant when the site stops being valid. <paramref name="grow"/> is true when the machine is Working, valid and
        /// has rings left to make. Nothing at all happens while the mechanic is off or the building is not spawned.
        /// </summary>
        public static void Step(ref RM_OasisMakerState state, ref int ticksInState, bool masterEnabled, bool spawned, Func<bool> validNow,
            int attuningDays, int ticksPerDay, ref bool qualityLocked, Action lockQuality, int currentRing, int lockedRadiusCap, out bool grow)
        {
            grow = false;
            if (!masterEnabled || !spawned) return;
            switch (state)
            {
                case RM_OasisMakerState.Dormant:
                    if (validNow())
                    {
                        state = RM_OasisMakerState.Attuning;
                        ticksInState = 0;
                    }
                    break;
                case RM_OasisMakerState.Attuning:
                    if (!validNow())
                    {
                        state = RM_OasisMakerState.Dormant;
                        ticksInState = 0;
                        break;
                    }
                    ticksInState += RareTickInterval;
                    if (ticksInState >= attuningDays * ticksPerDay)
                    {
                        if (!qualityLocked)
                        {
                            lockQuality();
                            qualityLocked = true;
                        }
                        state = RM_OasisMakerState.Working;
                        ticksInState = 0;
                    }
                    break;
                case RM_OasisMakerState.Working:
                    if (!validNow())
                    {
                        state = RM_OasisMakerState.Dormant;
                        ticksInState = 0;
                        break;
                    }
                    if (currentRing >= lockedRadiusCap) return;
                    grow = true;
                    break;
            }
        }

        // ---------------------------------------------------------------- growth
        /// <summary>Terrain ladders by defName. SoftSand is folded onto Sand's rung.</summary>
        public static readonly string[] MarginLadder = { "Sand", "Gravel", "Soil", "SoilRich" };
        public static readonly string[] PoolLadder = { "Sand", "Gravel", "Soil", "Mud", "Marsh", "WaterShallow" };

        public static string[] LadderForRing(int ring) { return ring == 0 ? PoolLadder : MarginLadder; }

        public static int RungsForRing(int ring) { return LadderForRing(ring).Length - 1; }

        /// <summary>Ring 0 is the pool zone (Chebyshev distance 0..1 from the centre cell); ring r &gt;= 1 is the one-cell band at distance r + 1.</summary>
        public static void RingBand(int ring, out int lo, out int hi)
        {
            lo = ring == 0 ? 0 : ring + 1;
            hi = ring == 0 ? 1 : ring + 1;
        }

        public static int Chebyshev(int dx, int dz) { return Math.Max(Math.Abs(dx), Math.Abs(dz)); }

        public static bool InRing(int ring, int dx, int dz)
        {
            int lo, hi;
            RingBand(ring, out lo, out hi);
            int c = Chebyshev(dx, dz);
            return c >= lo && c <= hi;
        }

        public static long RingDurationTicks(int ring, float baseRingDays, float growthFactor, int ticksPerDay)
        {
            double days = baseRingDays * Math.Pow(growthFactor, ring);
            return (long)(days * ticksPerDay);
        }

        public static long PerRungTicks(int ring, float baseRingDays, float growthFactor, int ticksPerDay)
        {
            return Math.Max(1L, RingDurationTicks(ring, baseRingDays, growthFactor, ticksPerDay) / RungsForRing(ring));
        }

        /// <summary>The terrain a cell becomes after one rung, or null when it is not on this ring's ladder or already at its end.</summary>
        public static string NextTerrain(int ring, string currentDefName)
        {
            string[] ladder = LadderForRing(ring);
            string name = currentDefName == "SoftSand" ? "Sand" : currentDefName;
            for (int i = 0; i < ladder.Length; i++)
            {
                if (ladder[i] == name) return i >= ladder.Length - 1 ? null : ladder[i + 1];
            }
            return null;
        }

        /// <summary>
        /// Adds a rare tick's worth of progress (scaled by the locked speed) and climbs as many whole rungs as it pays for, ring by ring,
        /// calling <paramref name="climbRung"/>(ring) once per rung. A finished ring starts the next with no carry-over. Returns the rungs climbed.
        /// </summary>
        public static int AdvanceGrowth(ref int rungProgressTicks, ref int currentRing, ref int ringRungsClimbed, int deltaTicks, float speedMultiplier,
            int lockedRadiusCap, float baseRingDays, float growthFactor, int ticksPerDay, Action<int> climbRung)
        {
            int climbed = 0;
            rungProgressTicks += (int)(deltaTicks * speedMultiplier);
            while (currentRing < lockedRadiusCap && rungProgressTicks >= PerRungTicks(currentRing, baseRingDays, growthFactor, ticksPerDay))
            {
                rungProgressTicks -= (int)PerRungTicks(currentRing, baseRingDays, growthFactor, ticksPerDay);
                climbRung(currentRing);
                climbed++;
                ringRungsClimbed++;
                if (ringRungsClimbed >= RungsForRing(currentRing))
                {
                    currentRing++;
                    ringRungsClimbed = 0;
                    rungProgressTicks = 0;
                }
            }
            return climbed;
        }
    }
}
