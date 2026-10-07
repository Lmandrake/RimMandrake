// Abyss pure kernel, part 1: the arithmetic of the Dark, the lamps (Dark shrink + krizzak dimming), the fold-lane geometry,
// the cryptid's signs, summ sunburn, etchfall and the biome score. Every rule used to be an inline expression in a map component or
// comp, tangled with Verse/Unity calls; they live here so an offline fuzz (Source/AbyssFuzz) can drive the SAME code the game runs.
// NO `using Verse;` / `using UnityEngine;` may ever land in this file: the fuzz project compiles it on plain net8.0 and the build
// breaks - the guard rail working. Part 2 (timers and state machines): RM_AbyssStateKernel.cs.
//
// Behaviour is preserved except where a comment marks a fix. Mathf.SmoothStep / InverseLerp / RoundToInt / FloorToInt are re-stated
// with their Unity definitions (SmoothStep clamps then t*t*(3-2t); RoundToInt is Math.Round, round-half-even).
using System;
using System.Collections.Generic;

namespace RimMandrake.Abyss
{
    public static class RM_DarkKernel
    {
        public const string DarkWeather = "RM_AbyssDark";
        public const string UnveilWeather = "RM_AbyssUnveiling";
        public const string StormWeather = "RM_AbyssWitchfire";

        /// <summary>Effective-temperature band over which the Dark thins: opaque at/below ClearStart, fully clear at/above ClearFull.</summary>
        public const float ClearStart = 8f;
        public const float ClearFull = 14f;
        public const float PocketAmplitude = 10f;

        public const float MurkStep = 0.05f;
        public const float MurkOffBelow = 0.03f;
        public const float LampFloor = 0.3f;
        public const float LampSlack = 0.15f;

        public static float Clamp01(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }

        public static float InverseLerp(float a, float b, float v)
        {
            return a != b ? Clamp01((v - a) / (b - a)) : 0f;
        }

        /// <summary>Mathf.SmoothStep(0, 1, t).</summary>
        public static float SmoothStep01(float t)
        {
            t = Clamp01(t);
            return -2f * t * t * t + 3f * t * t;
        }

        public static float DarknessForTemperature(float t)
        {
            return 1f - SmoothStep01(InverseLerp(ClearStart, ClearFull, t));
        }

        // The weather strings decide whether there is any Dark at all.
        public static bool DarkPresent(string weather) { return weather == DarkWeather || weather == StormWeather; }

        public static bool IsUnveiling(string weather) { return weather == UnveilWeather; }

        /// <summary>Etchfall and the grain sound scale with this: x2 in the Unveiling, x1 in the Dark and the storm, 0 otherwise.</summary>
        public static float GrainMultiplier(string weather)
        {
            if (weather == UnveilWeather) return 2f;
            return (weather == DarkWeather || weather == StormWeather) ? 1f : 0f;
        }

        /// <summary>Outdoor cells get a drifting noise offset (noise in 0..1) that opens and closes clear pockets.</summary>
        public static float PocketOffset(float noise01) { return (noise01 - 0.5f) * 2f * PocketAmplitude; }

        /// <summary>
        /// Darkness at a cell: 0 with no Dark or off the map; else the temperature curve (with the outdoor pocket noise) times
        /// what is left after a fold-lamp lane and a phantom pocket have each cleared their share.
        /// </summary>
        public static float DarknessAt(string weather, bool inBounds, float cellTemperature, bool roofed, float noise01, float laneClear, float phantomClear)
        {
            if (!DarkPresent(weather) || !inBounds) return 0f;
            float t = cellTemperature;
            if (!roofed) t += PocketOffset(noise01);
            return DarknessForTemperature(t) * (1f - laneClear) * (1f - phantomClear);
        }

        // ── murk (the blindness hediff) ──────────────────────────────

        public static float MurkTarget(bool active, float darkness, float strength) { return active ? darkness * strength : 0f; }

        public struct MurkResult
        {
            public bool has, added, removed, set;
            public float severity;
        }

        /// <summary>One pawn's MurkPass: remove under the floor, otherwise add if missing and move the severity once it is a step away.</summary>
        public static MurkResult MurkStepFor(bool has, float severity, float target, float severityOnAdd)
        {
            var r = new MurkResult { has = has, severity = severity };
            if (target < MurkOffBelow)
            {
                if (has) { r.has = false; r.removed = true; }
                return r;
            }
            if (!has) { r.has = true; r.added = true; r.severity = severityOnAdd; }
            if (Math.Abs(r.severity - target) >= MurkStep) { r.severity = target; r.set = true; }
            return r;
        }

        // ── lamps: the Dark shrinks a building lamp, a krizzak feeds on it ──

        public struct Lamp
        {
            public float radius;                  // CompGlower.GlowRadius right now
            public float baseline;                // the def's own glowRadius
            public bool shrunkKnown;              // the Dark's remembered-baseline entry exists
            public float shrunkBaseline;
            public bool kPresent;                 // the krizzak dimming entry exists (IsDimmed)
            public float kOriginal;
            public int kLastFed;
        }

        public static float LampFactor(bool on, float darkness, float strength)
        {
            return on ? 1f - (1f - LampFloor) * Clamp01(darkness * strength) : 1f;
        }

        /// <summary>RM_MapComponent_Dark.LampPass for one lamp (main loop, then the restore loop). Returns true when the radius changed.</summary>
        public static bool DarkLampPass(ref Lamp l, bool glows, bool on, float darkness, float strength)
        {
            bool changed = false;
            if (glows && !l.kPresent)                               // a krizzak has this one: do not fight it
            {
                float f = LampFactor(on, darkness, strength);
                float target = l.baseline * f;
                if (Math.Abs(l.radius - target) >= LampSlack)
                {
                    if (f < 0.999f) { l.shrunkKnown = true; l.shrunkBaseline = l.baseline; }
                    else if (target >= l.baseline - 0.01f) l.shrunkKnown = false;   // back to full size: nothing left to restore (the entry used to linger for the life of the lamp)
                    l.radius = target;
                    changed = true;
                }
            }
            // restore a lamp we shrank that is no longer in the Dark (or whose Dark is off)
            if (l.shrunkKnown && !on && l.radius < l.shrunkBaseline - 0.01f && !l.kPresent)
            {
                l.radius = l.shrunkBaseline;
                l.shrunkKnown = false;
                changed = true;
            }
            return changed;
        }

        public const int KrizzakRecoverAfterTicks = 600;

        public static bool KrizzakAtFloor(in Lamp l, float minFraction)
        {
            return l.kPresent && l.radius <= l.kOriginal * minFraction + 0.01f;
        }

        /// <summary>RM_MapComponent_KrizzakDimming.Feed. Returns true when the radius shrank.</summary>
        public static bool KrizzakFeed(ref Lamp l, int now, float fraction, float minFraction)
        {
            if (!l.kPresent) { l.kPresent = true; l.kOriginal = l.radius; }
            l.kLastFed = now;
            float next = Math.Max(l.kOriginal * minFraction, l.radius - l.kOriginal * fraction);
            if (next < l.radius) { l.radius = next; return true; }
            return false;
        }

        /// <summary>RM_MapComponent_KrizzakDimming.MapComponentTick for one dimmed lamp (every 250 ticks).</summary>
        public static void KrizzakRecover(ref Lamp l, int now)
        {
            if (!l.kPresent) return;
            if (now - l.kLastFed < KrizzakRecoverAfterTicks) return;
            float next = Math.Min(l.kOriginal, l.radius + l.kOriginal * 0.1f);
            l.radius = next;
            if (next >= l.kOriginal - 0.01f) l.kPresent = false;
        }

        // ── etchfall ─────────────────────────────────────────────────

        public const int EtchCellsPerPass = 24;

        public static int EtchTries(float strength, float grainMultiplier)
        {
            return (int)Math.Ceiling(EtchCellsPerPass * strength * grainMultiplier);
        }

        // ── summ sunburn ─────────────────────────────────────────────

        /// <summary>
        /// One CompTickRare of the summ's sun rule. In sun it gains `burn` (capped at the hediff's max, starting at `burn`); out of
        /// it the hediff cools by `cool` and goes at or under 0.001. newSeverity is the RAW value: Hediff.Severity clamps to the def.
        /// </summary>
        public static void SunStep(bool has, float severity, bool inSun, float burn, float cool, float maxSeverity, out bool nowHas, out float newSeverity)
        {
            nowHas = has; newSeverity = severity;
            if (inSun)
            {
                if (!has) { nowHas = true; newSeverity = burn; }
                else newSeverity = Math.Min(maxSeverity, severity + burn);
            }
            else if (has)
            {
                newSeverity = severity - cool;
                if (newSeverity <= 0.001f) nowHas = false;
            }
        }

        // ── the fold-lamp lane ───────────────────────────────────────

        public const int LaneLength = 14;
        public const int LaneFadeFrom = 10;

        public static int LaneHalfWidth(int d)
        {
            if (d <= 2) return 1;
            if (d <= 9) return 2;
            return 1;
        }

        public static float LaneValue(int d)
        {
            return d <= LaneFadeFrom ? 1f : 1f - (d - LaneFadeFrom) / (float)(LaneLength - LaneFadeFrom + 1);
        }

        /// <summary>
        /// Lay one lamp's lane: the origin at 1, then a lane (3 wide at the throat, 5 in the middle, 3 at the far end) LaneLength long,
        /// fading over its last cells, stopped in each column by the first blocked cell (off the map or a wall).
        /// (fx,fz) is the facing step, (sx,sz) the clockwise side step.
        /// </summary>
        public static void LayLane(int ox, int oz, int fx, int fz, int sx, int sz, Func<int, int, bool> blocked, Action<int, int, float> mark)
        {
            mark(ox, oz, 1f);
            for (int lateral = -2; lateral <= 2; lateral++)
            {
                for (int d = 1; d <= LaneLength; d++)
                {
                    if (Math.Abs(lateral) > LaneHalfWidth(d)) continue;
                    int cx = ox + fx * d + sx * lateral, cz = oz + fz * d + sz * lateral;
                    if (blocked(cx, cz)) break;
                    mark(cx, cz, LaneValue(d));
                }
            }
        }

        /// <summary>The per-cell clearance grid with its touched list: Mark keeps the maximum, Reset zeroes only what was touched.</summary>
        public sealed class ClearGrid
        {
            public readonly float[] clear;
            public readonly List<int> touched = new List<int>();
            public ClearGrid(int cells) { clear = new float[cells]; }

            public void Mark(int idx, float v)
            {
                if (clear[idx] <= 0f) touched.Add(idx);
                if (v > clear[idx]) clear[idx] = v;
            }

            public void Reset()
            {
                for (int i = 0; i < touched.Count; i++) clear[touched[i]] = 0f;
                touched.Clear();
            }
        }

        // ── the cryptid's signs ──────────────────────────────────────

        public const float CircleRadius = 2.9f;
        public const int CircleNeed = 3;

        /// <summary>Cells within CircleRadius of a cairn (the engine's radial cells, centre included).</summary>
        public static List<int[]> RadialOffsets(float radius)
        {
            var list = new List<int[]>();
            int r = (int)Math.Ceiling(radius);
            for (int dx = -r; dx <= r; dx++)
                for (int dz = -r; dz <= r; dz++)
                    if (dx * dx + dz * dz <= radius * radius) list.Add(new[] { dx, dz });
            return list;
        }

        /// <summary>Cells (x * width... packed as x + z * width) with at least CircleNeed cairns in range, on a width x height map.</summary>
        public static HashSet<int> CircleCells(IList<int[]> cairns, int width, int height)
        {
            var counts = new Dictionary<int, int>();
            var result = new HashSet<int>();
            List<int[]> offs = RadialOffsets(CircleRadius);
            foreach (int[] c in cairns)
            {
                foreach (int[] o in offs)
                {
                    int x = c[0] + o[0], z = c[1] + o[1];
                    if (x < 0 || z < 0 || x >= width || z >= height) continue;
                    int key = x + z * width;
                    counts.TryGetValue(key, out int n);
                    counts[key] = n + 1;
                    if (n + 1 >= CircleNeed) result.Add(key);
                }
            }
            return result;
        }

        /// <summary>The value an exchange is worth: the stack's market value (at least 5) times a 0.8..1.3 roll.</summary>
        public static float ExchangeValue(float marketValue, int stackCount, float roll01)
        {
            return Math.Max(5f, marketValue * stackCount) * (0.8f + 0.5f * roll01);
        }

        /// <summary>
        /// Goods left in return, in the order given (component, tholin, steel): each gets 40% of the value still unspent, steel (isFull)
        /// all of it, at most one full stack each. counts[i] is the stack size left of goods i; the return is the value left unspent.
        /// The count is computed in double and saturated: a float beyond int range used to floor to int.MinValue and pay nothing.
        /// </summary>
        public static float ExchangeGoods(float value, IList<float> baseValue, IList<int> stackLimit, IList<bool> isFull, int[] counts)
        {
            for (int i = 0; i < baseValue.Count; i++)
            {
                counts[i] = 0;
                if (value < baseValue[i]) continue;
                float quota = value * (isFull[i] ? 1f : 0.4f) / baseValue[i];
                int n = (int)Math.Min(stackLimit[i], Math.Floor((double)quota));
                if (n <= 0) continue;
                counts[i] = n;
                value -= n * baseValue[i];
            }
            return value;
        }

        /// <summary>One phantom pocket's clearance at distance d: 1 at the centre falling smoothly to 0 at its radius.</summary>
        public static float PhantomClearance(float d, float radius)
        {
            return d < radius ? 1f - SmoothStep01(d / radius) : 0f;
        }

        // ── the biome worker ─────────────────────────────────────────

        public struct BiomeRanges
        {
            public float tempMin, tempMax, rainMin, rainMax, elevMin, elevMax, baseScore, degreeWeight, rainfallDivisor, spawnChance;
        }

        public static float BiomeScore(bool tileNull, bool waterCovered, bool hillyEnough, float rarity, float temperature, float rainfall, float elevation,
            in BiomeRanges r, Func<float, bool> seededChance)
        {
            if (tileNull || waterCovered) return -100f;
            if (rarity <= 0.001f) return -100f;
            if (temperature < r.tempMin || temperature > r.tempMax) return 0f;
            if (rainfall < r.rainMin || rainfall >= r.rainMax) return 0f;
            if (elevation < r.elevMin || elevation > r.elevMax) return 0f;
            if (!hillyEnough) return 0f;
            float gate = r.spawnChance * rarity;
            if (gate < 1f && !seededChance(gate)) return 0f;
            float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
            return r.baseScore + (r.tempMax - temperature) * r.degreeWeight + (rainfall - r.rainMin) / divisor;
        }
    }
}
