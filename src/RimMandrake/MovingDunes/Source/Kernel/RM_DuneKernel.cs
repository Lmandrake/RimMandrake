// Verse-free kernel of the Moving Dunes engine (MapComponent_DuneField.cs): the Werner-style slab transport on the sand grid, the
// windward influx (source/sink), the wind schedule, storm factors and plant-choke sizing. The sand grid is reached through
// IDuneField so the same code runs on the real SandGrid (MapDuneField) and on an array in SelfTest/MovingDunesFuzz.cs, which
// compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.MovingDunes
{
    public interface IDuneField
    {
        int Width { get; }
        int Height { get; }
        float MaxDepth { get; }
        float TotalDepth { get; }
        float GetDepth(int x, int z);
        /// <summary>Writes a depth; the field may clamp it to [0, MaxDepth] or refuse it (a cell that cannot hold sand).</summary>
        void SetDepth(int x, int z, float depth);
        bool Roofed(int x, int z);
        /// <summary>An edifice that cannot coexist with sand (a wall): sand banks against it.</summary>
        bool BlocksSand(int x, int z);
        /// <summary>Ground that can hold sand at all: false for water and space (the terrain's holdSnowOrSand).
        /// Sand hopping onto it banks on the last cell before it, like a wall (MOVINGDUNES_WATER_BANKS_SAND_1).</summary>
        bool CanHoldSand(int x, int z);
    }

    public sealed class TransportParams
    {
        public float SlabSize = 0.05f, ErodeMinDepth = 0.1f;
        public int ShadowRange = 4, HopMin = 2, HopMax = 6;
    }

    /// <summary>What one batch did, so the caller (and the fuzz) can account for every grain.</summary>
    public sealed class Batch
    {
        /// <summary>Nominal depth that left the map over the leeward edge.</summary>
        public float Lost;
        /// <summary>Depth a landing could not take because it was at MaxDepth. The only way a moved slab still leaves the map's sand
        /// apart from the leeward edge: water no longer eats it (it banks on the shore).</summary>
        public float CapOverflow;
        /// <summary>Sum over moves of (depth actually deposited - slab + cap overflow): only the boundary nudge, so exactly 0 with it off.</summary>
        public float DepositError;
        /// <summary>Sum over moves of (depth actually removed - slab): positive when the source was nudged down further.</summary>
        public float ErodeError;
        /// <summary>Net change of cells eroded and put straight back (the boundary nudge can leave them a hair off).</summary>
        public float InPlaceDelta;
        public int Moves, OffMap, InPlace, Attempts;
        /// <summary>Moves whose hop met water (a cell that cannot hold sand) and banked on the shore cell before it.</summary>
        public int WaterBanked;
    }

    public static class RM_DuneKernel
    {
        public const int BatchIntervalTicks = 250;
        public const int TicksPerDay = 60000;
        public const int BatchesPerDay = TicksPerDay / BatchIntervalTicks;
        public static readonly float[] CategoryBoundaries = { 0.03f, 0.25f, 0.5f, 0.75f };
        public const float BoundaryHysteresis = 0.012f;
        public const float ShadowDepthMargin = 0.15f;
        public const float LowCellMargin = 0.02f;
        public const int InfluxBandWidth = 6;

        // 8 compass directions, index 0 = north, clockwise.
        public static readonly int[] WindDx = { 0, 1, 1, 1, 0, -1, -1, -1 };
        public static readonly int[] WindDz = { 1, 1, 0, -1, -1, -1, 0, 1 };

        public static float Clamp(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

        public static bool InBounds(IDuneField f, int x, int z) { return x >= 0 && z >= 0 && x < f.Width && z < f.Height; }

        // ── scale ──
        public static int AttemptsPerBatch(float attemptsPerCellPerDay, int numCells)
        {
            return Math.Max(1, (int)Math.Round(attemptsPerCellPerDay * numCells / 240f));
        }
        public static int TransportAttempts(int attemptsPerBatch, float stormFactor)
        {
            return (int)Math.Round(attemptsPerBatch * Math.Max(0.01f, stormFactor));
        }
        public static int ChokeSamples(int attemptsPerBatch, float sampleFraction, float stormFactor)
        {
            return (int)Math.Round(attemptsPerBatch * sampleFraction * Math.Max(0.01f, stormFactor));
        }
        /// <summary>Damage per visit, sized so a fully buried plant dies in chokeDays.</summary>
        public static int ChokeDamage(float maxHitPoints, float chokeDays, float visitsPerDay)
        {
            return Math.Max(1, (int)Math.Round(maxHitPoints / (chokeDays * visitsPerDay)));
        }
        public static float VisitsPerDay(int samples, int numCells) { return (float)samples * BatchesPerDay / numCells; }

        // ── storm ──
        public static void StormFactors(float sandRate, bool hasExt, float extTransport, float extInflux, bool extForce, float matTransport, float matInflux, out float transport, out float influx)
        {
            transport = 1f; influx = 1f;
            bool storming = sandRate > 0.001f || (hasExt && extForce);
            if (!storming) return;
            transport = hasExt && extTransport >= 0f ? extTransport : matTransport;
            influx = hasExt && extInflux >= 0f ? extInflux : matInflux;
        }

        // ── wind ──
        public static bool WindLockApplies(bool settingOn, bool hasExt, bool locks) { return settingOn && hasExt && locks; }
        public static int ShiftWind(int windDir, bool big, bool negative)
        {
            int step = big ? 2 : 1;
            if (negative) step = -step;
            return (windDir + step + 8) & 7;
        }
        public static int NextWindShiftTick(int now, float rollHalfToOneAndHalf, float meanDays)
        {
            float days = rollHalfToOneAndHalf * Math.Max(0.05f, meanDays);
            return now + (int)Math.Round(days * TicksPerDay);
        }

        // ── the grid write that keeps clear of the movement-category boundaries ──
        public static void SetDepthHysteretic(IDuneField f, int x, int z, float target, float hysteresis)
        {
            target = Clamp(target, 0f, f.MaxDepth);
            if (target > 0f)
            {
                for (int i = 0; i < CategoryBoundaries.Length; i++)
                {
                    float b = CategoryBoundaries[i];
                    if (Math.Abs(target - b) < hysteresis)
                    {
                        target = target >= b ? b + hysteresis : b - hysteresis;
                        break;
                    }
                }
                target = Clamp(target, 0f, f.MaxDepth);
            }
            f.SetDepth(x, z, target);
        }

        // ── transport ──
        public static bool IsWindShadowed(IDuneField f, int x, int z, int wx, int wz, float here, int shadowRange)
        {
            for (int s = 1; s <= shadowRange; s++)
            {
                int ux = x - wx * s, uz = z - wz * s;
                if (!InBounds(f, ux, uz)) return false;   // open desert upwind
                if (f.BlocksSand(ux, uz)) return true;
                if (f.GetDepth(ux, uz) > here + ShadowDepthMargin) return true;
            }
            return false;
        }

        /// <summary>One batch of slab attempts. rangeExcl(lo,hi) is Rand.Range (hi exclusive), rangeIncl is Rand.RangeInclusive.
        /// onDeposit(x,z,before,after) lets the caller lay filth and bury items where a slab landed.</summary>
        public static Batch RunTransport(IDuneField f, int wx, int wz, int attempts, TransportParams p, float hysteresis,
                                         Func<int, int, int> rangeExcl, Func<int, int, int> rangeIncl, Action<int, int, float, float> onDeposit)
        {
            var b = new Batch { Attempts = attempts };
            float q = p.SlabSize;
            for (int i = 0; i < attempts; i++)
            {
                int cx = rangeExcl(0, f.Width), cz = rangeExcl(0, f.Height);
                float here = f.GetDepth(cx, cz);
                if (here < p.ErodeMinDepth) continue;
                if (f.Roofed(cx, cz)) continue;   // roofed cells are out of the wind entirely
                if (IsWindShadowed(f, cx, cz, wx, wz, here, p.ShadowRange)) continue;

                float slab = Math.Min(q, here);
                int hop = rangeIncl(p.HopMin, p.HopMax);
                int lx = 0, lz = 0; bool haveLanding = false;
                int px = cx, pz = cz;
                bool offMap = false, atWater = false;
                for (int s = 1; s <= hop; s++)
                {
                    int nx = cx + wx * s, nz = cz + wz * s;
                    if (!InBounds(f, nx, nz)) { offMap = true; break; }
                    if (f.Roofed(nx, nz)) { lx = px; lz = pz; haveLanding = true; break; }   // banks at the lip of a roof
                    if (f.BlocksSand(nx, nz)) { lx = px; lz = pz; haveLanding = true; break; }   // the snowdrift behind a fence
                    if (!f.CanHoldSand(nx, nz)) { lx = px; lz = pz; haveLanding = true; atWater = true; break; }   // the shore banks it (owner: water banks the sand)
                    if (f.GetDepth(nx, nz) < here - LowCellMargin) { lx = nx; lz = nz; haveLanding = true; break; }   // deposition prefers low
                    px = nx; pz = nz;
                }

                SetDepthHysteretic(f, cx, cz, here - slab, hysteresis);
                float removed = here - f.GetDepth(cx, cz);
                if (offMap)
                {
                    b.Lost += slab; b.OffMap++; b.Moves++;
                    b.ErodeError += removed - slab;
                    continue;
                }
                if (!haveLanding) { lx = px; lz = pz; }
                if (lx == cx && lz == cz)
                {
                    // Erode-and-replace-in-place is a no-op that still costs a mesh dirty; put the slab back.
                    SetDepthHysteretic(f, cx, cz, here, hysteresis);
                    b.InPlaceDelta += f.GetDepth(cx, cz) - here;
                    b.InPlace++;
                    continue;
                }
                b.Moves++;
                if (atWater) b.WaterBanked++;
                b.ErodeError += removed - slab;
                float before = f.GetDepth(lx, lz);
                float overflow = Math.Max(0f, before + slab - f.MaxDepth);
                SetDepthHysteretic(f, lx, lz, before + slab, hysteresis);
                float after = f.GetDepth(lx, lz);
                b.CapOverflow += overflow;
                b.DepositError += (after - before) - slab + overflow;
                if (onDeposit != null) onDeposit(lx, lz, before, after);
            }
            return b;
        }

        // ── influx (the source half of source/sink) ──
        public static float InfluxDebtDelta(float lostDepth, float lossRatio, float perDay, float weather, float driftMult)
        {
            return lostDepth * lossRatio * weather + perDay / BatchesPerDay * weather * driftMult;
        }

        public static void RandomWindwardCell(int w, int h, int wx, int wz, Func<int, int, int> rangeExcl, out int x, out int z)
        {
            int band = Math.Min(InfluxBandWidth, Math.Min(w, h) / 2);
            if (band < 1) band = 1;
            x = wx > 0 ? rangeExcl(0, band) : wx < 0 ? rangeExcl(w - band, w) : rangeExcl(0, w);
            z = wz > 0 ? rangeExcl(0, band) : wz < 0 ? rangeExcl(h - band, h) : rangeExcl(0, h);
            x = x < 0 ? 0 : (x > w - 1 ? w - 1 : x);
            z = z < 0 ? 0 : (z > h - 1 ? h - 1 : z);
        }

        /// <summary>Spends the influx debt as slabs on the windward band, bounded per batch; returns how many were placed. The mass cap binds.</summary>
        public static int RunInflux(IDuneField f, ref float debt, float lostDepth, float stormFactor, float driftMult, TransportParams p, float lossRatio, float perDay,
                                    float maxTotalMassFraction, int attemptsPerBatch, int wx, int wz, float hysteresis, Func<int, int, int> rangeExcl)
        {
            int cells = f.Width * f.Height;
            float cap = maxTotalMassFraction * cells * f.MaxDepth;
            if (f.TotalDepth >= cap) { debt = 0f; return 0; }

            float weather = Math.Max(0f, stormFactor);
            debt += InfluxDebtDelta(lostDepth, lossRatio, perDay, weather, driftMult);
            if (debt <= 0f) return 0;

            float q = p.SlabSize;
            int placed = 0;
            int budget = (int)Math.Ceiling(debt / q);
            int maxPlacements = Math.Max(16, attemptsPerBatch * 4);
            int tries = 0, maxTries = maxPlacements * 4;
            while (placed < budget && placed < maxPlacements && tries < maxTries && f.TotalDepth < cap)
            {
                tries++;
                int x, z;
                RandomWindwardCell(f.Width, f.Height, wx, wz, rangeExcl, out x, out z);
                if (!InBounds(f, x, z) || f.Roofed(x, z)) continue;
                float before = f.GetDepth(x, z);
                if (before >= f.MaxDepth - 0.001f) continue;
                SetDepthHysteretic(f, x, z, before + q, hysteresis);
                if (f.GetDepth(x, z) <= before) continue;   // the cell refused the sand: do not spend the debt
                placed++;
                debt -= q;
            }
            if (debt < 0f) debt = 0f;
            return placed;
        }
    }
}
