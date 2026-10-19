// Verse-free kernel of the Cauldron vent gas (CAULDRON_MECHANICS_BUILD_1 part 3, owner rulings Q1/N2 2026-10-15/16:
// "Drifting gas clouds plus the native gas system already built into rimworld"; by card, "A brand-new gas type").
//
// WHY A SEPARATE GRID. Verse.GasGrid packs four gases into one uint per cell (BlindSmoke, ToxGas, RotStink, DeadlifeDust,
// one byte each): there is no free byte for a fifth type, and widening it would mean patching every reader of that uint,
// which is exactly the "can break other mods' gases" risk the ruling's guard row is about. So the new type keeps its own
// byte-per-cell grid (RM_VentGasCells below), moved by the SAME rules vanilla gas uses (MinDiffusion 17, half the
// difference per step, the same walls via GasGrid.GasCanMoveTo, roof halves dissipation, vacuum multiplies it), drawn by a
// SectionLayer_Gas subclass, and its burning hands off to the vanilla grid as ToxGas (the toxic smoke). Nothing here
// touches Verse.GasGrid's storage, so no other gas -- vanilla's or another mod's -- can be changed by this code.
//
// RM_VentGas.cs (the MapComponent, the layer, ignition) and RM_GasTap.cs call these with the same expressions;
// SelfTest/CauldronFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
// Every number marked PROVISIONAL is a first-guess tuning value (owner, 2026-10-03: ship it, mark it, tune it live).
using System;

namespace RimMandrake.Cauldron
{
    public static class RM_VentGasKernel
    {
        public const int MaxDensity = 255;
        public const int MinDiffusion = 17;            // vanilla GasGrid.MinDiffusion
        // PROVISIONAL: vanilla tox gas is 3; vent gas lingers a little longer. At half vanilla's sweep rate one 1x vent holds a
        // cloud of only ~13-60 cells (reviewer estimate): if the live bar "a drifting cloud" reads as a blob, lower the
        // dissipation (not below 2: a roofed cell rounds 0.5x of 1 to 0 and would never clear) or raise BaseEmit.
        public const int DissipationAmount = 2;
        public const float VacuumDissipateFactor = 25f; // vanilla GasGrid.VacuumDissipatePerTickFactor
        public const int BaseEmit = 12;                // PROVISIONAL: density added per emission pulse at output 1x
        public const float LeakFactor = 2f;            // PROVISIONAL: a chronic leak breathes twice as much gas
        public const int EmitIntervalTicks = 60;
        public const int IgniteMin = 24;               // PROVISIONAL: a cell this thick or thicker catches
        public const float ToxPerGas = 0.6f;           // PROVISIONAL: vanilla ToxGas density made per unit burned
        public const int BurnScanIntervalTicks = 30;
        public const int MaxIgnitionsPerScan = 40;     // a whole cloud burns over several scans, never in one frame
        public const int HeadingPeriodTicks = 60000;   // the drift heading changes once a day
        public const float MaxDriftChance = 0.75f;
        public const float DriftPerWind = 0.4f;

        // Eight headings, cardinal and diagonal: index -> (dx, dz). The drift pushes gas one cell along it.
        public static readonly int[] HeadingDx = { 0, 1, 1, 1, 0, -1, -1, -1 };
        public static readonly int[] HeadingDz = { 1, 1, 0, -1, -1, -1, 0, 1 };
        // Cardinal directions for diffusion, the same four vanilla shuffles.
        public static readonly int[] CardDx = { 0, 1, 0, -1 };
        public static readonly int[] CardDz = { 1, 0, -1, 0 };

        // Vanilla GasGrid.TryDiffuseIndividualGas, verbatim in behaviour.
        public static bool TryDiffuse(ref int a, ref int b)
        {
            if (a < MinDiffusion) return false;
            int num = Math.Abs(a - b) / 2;
            if (a > b && num >= MinDiffusion)
            {
                a -= num;
                b += num;
                return true;
            }
            return false;
        }

        // Vanilla GasGrid.AdjustedDensity: clamp to 255, the excess is overflow.
        public static int Adjusted(int newDensity, out int overflow)
        {
            if (newDensity > MaxDensity)
            {
                overflow = newDensity - MaxDensity;
                return MaxDensity;
            }
            overflow = 0;
            return newDensity < 0 ? 0 : newDensity;
        }

        // Vanilla's dissipation step for one gas: roof halves it, vacuum multiplies it.
        public static int DissipateStep(bool roofed, float vacuum)
        {
            float f = (roofed ? 0.5f : 1f) + Math.Max(0f, vacuum) * VacuumDissipateFactor;
            return (int)Math.Round(DissipationAmount * f, MidpointRounding.ToEven);
        }

        // Density one vent adds per EmitIntervalTicks. 0 when the setting is off, the vent is capped by a gas-tap scaffold, it
        // is faltering (the hush before a bloom: the forest goes silent), or silenced (output at or below the puff floor
        // RM_VentKernel.PuffsAt uses).
        public static int EmitAmount(bool enabled, bool capped, bool faltering, float output, bool leaking, float factor)
        {
            if (!enabled || capped || faltering || output <= 0.05f || factor <= 0f) return 0;
            double v = BaseEmit * output * (leaking ? LeakFactor : 1f) * factor;
            return (int)Math.Round(v, MidpointRounding.AwayFromZero);
        }

        // Chance per diffusion visit that a cell also pushes a share downwind. Calm air: no drift.
        public static float DriftChance(float windSpeed)
        {
            float c = windSpeed * DriftPerWind;
            return c < 0f ? 0f : c > MaxDriftChance ? MaxDriftChance : c;
        }

        // The share a drifting cell pushes downwind: a quarter, and only from a cell thick enough to diffuse at all.
        public static int DriftAmount(int a)
        {
            return a < MinDiffusion ? 0 : a / 4;
        }

        // The map's drift heading for this day: stable for HeadingPeriodTicks, then a new one (seeded per map).
        public static int Heading(int ticksGame, int mapSeed)
        {
            long day = (ticksGame < 0 ? 0 : ticksGame) / HeadingPeriodTicks;
            unchecked
            {
                uint h = (uint)(day * 2654435761L) ^ (uint)mapSeed;
                h ^= h >> 15; h *= 0x2C1B3C6Du; h ^= h >> 12;
                return (int)(h % 8u);
            }
        }

        public static bool Ignites(bool enabled, int density) { return enabled && density >= IgniteMin; }

        // Vanilla ToxGas made when `burned` units of vent gas burn: the toxic smoke.
        public static int ToxFromBurn(int burned, bool toxicSmoke)
        {
            if (!toxicSmoke || burned <= 0) return 0;
            return (int)Math.Round(burned * ToxPerGas, MidpointRounding.AwayFromZero);
        }

        // A burning cell's fire size: a thin wisp flickers, a thick cell roars. 0.2 .. 1.0.
        public static float FireSize(int burned)
        {
            float f = 0.2f + 0.8f * (burned / (float)MaxDensity);
            return f < 0.2f ? 0.2f : f > 1f ? 1f : f;
        }

        // ── gas tap ────────────────────────────────────────────────────────
        public const float TapUnitsPerDayAtOne = 12f;  // PROVISIONAL: condensate units a tapped 1x vent banks per day
        public const float TapBankCap = 60f;           // PROVISIONAL: what the scaffold holds when no tank takes it
        public const int RareTicksPerDay = 60000 / 250;
        public const float PryDamage = 8f;             // PROVISIONAL: a prying vexxiss's damage to a scaffold per pry
        public const int PryIntervalTicks = 120;

        // The bank after one rare tick: grows with the vent's output (a leak twice as fast), never past the cap.
        public static float TapAccrue(float bank, bool enabled, float output, bool leaking)
        {
            if (bank < 0f) bank = 0f;
            if (!enabled || output <= 0f) return Math.Min(bank, TapBankCap);
            float add = TapUnitsPerDayAtOne * output * (leaking ? LeakFactor : 1f) / RareTicksPerDay;
            float b = bank + add;
            return b > TapBankCap ? TapBankCap : b;
        }

        // Whole units ready to leave the bank for a tank.
        public static int TapReady(float bank) { return bank < 1f ? 0 : (int)Math.Floor(bank); }
    }

    // One byte of vent gas per cell, index = z * width + x (CellIndicesUtility.CellToIndex). The MapComponent owns one and
    // feeds it vanilla's wall test through `canMoveTo`; the fuzz drives the same class over a random small grid.
    public sealed class RM_VentGasCells
    {
        public readonly int Width, Height;
        public byte[] Density;
        public int NonZero;   // cells holding any gas (the grid skips its sweeps while this is 0)

        public RM_VentGasCells(int width, int height)
        {
            Width = width;
            Height = height;
            Density = new byte[width * height];
        }

        public int Count => Density.Length;

        public int Neighbour(int i, int dx, int dz)
        {
            int x = i % Width + dx, z = i / Width + dz;
            if (x < 0 || z < 0 || x >= Width || z >= Height) return -1;
            return z * Width + x;
        }

        private void Set(int i, int v)
        {
            byte old = Density[i];
            byte nv = (byte)(v < 0 ? 0 : v > RM_VentGasKernel.MaxDensity ? RM_VentGasKernel.MaxDensity : v);
            if (old == 0 && nv != 0) NonZero++;
            else if (old != 0 && nv == 0) NonZero--;
            Density[i] = nv;
        }

        // Adds up to 255; returns the overflow the caller may flood outward.
        public int Add(int i, int amount)
        {
            if (amount <= 0 || i < 0 || i >= Density.Length) return 0;
            int v = RM_VentGasKernel.Adjusted((int)Math.Min((long)Density[i] + amount, int.MaxValue), out int overflow);   // no int wrap
            Set(i, v);
            return overflow;
        }

        // Vanilla TryDiffuseGases for one gas: the four neighbours in `order` (indices into CardDx/CardDz), each equalised
        // by half the difference when that is at least MinDiffusion. `dirty` is told every cell that changed.
        public bool DiffuseFrom(int i, int[] order, Func<int, bool> canMoveTo, Action<int> dirty)
        {
            int a = Density[i];
            if (a < RM_VentGasKernel.MinDiffusion) return false;
            bool any = false;
            for (int k = 0; k < order.Length; k++)
            {
                int d = order[k];
                int j = Neighbour(i, RM_VentGasKernel.CardDx[d], RM_VentGasKernel.CardDz[d]);
                if (j < 0 || !canMoveTo(j)) continue;
                int b = Density[j];
                if (RM_VentGasKernel.TryDiffuse(ref a, ref b))
                {
                    Set(j, b);
                    dirty?.Invoke(j);
                    any = true;
                    if (a < RM_VentGasKernel.MinDiffusion) break;
                }
            }
            if (any)
            {
                Set(i, a);
                dirty?.Invoke(i);
            }
            return any;
        }

        // The wind: a quarter of a thick cell moves one cell along the heading (never into a wall, never past 255).
        public bool Drift(int i, int heading, Func<int, bool> canMoveTo, Action<int> dirty)
        {
            int a = Density[i];
            int amt = RM_VentGasKernel.DriftAmount(a);
            if (amt <= 0) return false;
            int h = ((heading % 8) + 8) % 8;
            int j = Neighbour(i, RM_VentGasKernel.HeadingDx[h], RM_VentGasKernel.HeadingDz[h]);
            if (j < 0 || !canMoveTo(j)) return false;
            int hdx = RM_VentGasKernel.HeadingDx[h], hdz = RM_VentGasKernel.HeadingDz[h];
            if (hdx != 0 && hdz != 0)
            {
                // A diagonal squeezes past no wall corner: both cardinal side cells must be open (vanilla-like).
                int sx = Neighbour(i, hdx, 0), sz = Neighbour(i, 0, hdz);
                if (sx < 0 || sz < 0 || !canMoveTo(sx) || !canMoveTo(sz)) return false;
            }
            int room = RM_VentGasKernel.MaxDensity - Density[j];
            if (amt > room) amt = room;
            if (amt <= 0) return false;
            Set(j, Density[j] + amt);
            Set(i, a - amt);
            dirty?.Invoke(i);
            dirty?.Invoke(j);
            return true;
        }

        // One dissipation visit. True when the cell emptied (its mesh needs a redraw).
        public bool Dissipate(int i, int step)
        {
            int a = Density[i];
            if (a == 0 || step <= 0) return false;
            int v = Math.Max(a - step, 0);
            Set(i, v);
            return v == 0;
        }

        // The cell burns: all its gas is consumed. Returns how much burned.
        public int Burn(int i)
        {
            int a = Density[i];
            if (a > 0) Set(i, 0);
            return a;
        }

        public void Clear()
        {
            Array.Clear(Density, 0, Density.Length);
            NonZero = 0;
        }

        // After a load: recount from the bytes.
        public void Recount()
        {
            int n = 0;
            for (int i = 0; i < Density.Length; i++) if (Density[i] != 0) n++;
            NonZero = n;
        }

        public long Total()
        {
            long t = 0;
            for (int i = 0; i < Density.Length; i++) t += Density[i];
            return t;
        }

        // The cloud's density-weighted centroid over the window x0..x1, z0..z1 (inclusive, clamped to the grid): the one
        // read of the cloud's MOVEMENT (validation.py drift.gas_cloud_moves_along_heading). Returns the total gas in the
        // window; with none, cx = cz = -1 and cells = 0.
        public long CentroidIn(int x0, int z0, int x1, int z1, out double cx, out double cz, out int cells)
        {
            if (x0 < 0) x0 = 0;
            if (z0 < 0) z0 = 0;
            if (x1 >= Width) x1 = Width - 1;
            if (z1 >= Height) z1 = Height - 1;
            long total = 0, sx = 0, sz = 0;
            cells = 0;
            for (int z = z0; z <= z1; z++)
            {
                int row = z * Width;
                for (int x = x0; x <= x1; x++)
                {
                    int d = Density[row + x];
                    if (d == 0) continue;
                    cells++;
                    total += d;
                    sx += (long)d * x;
                    sz += (long)d * z;
                }
            }
            if (total == 0) { cx = -1; cz = -1; return 0; }
            cx = sx / (double)total;
            cz = sz / (double)total;
            return total;
        }
    }
}
