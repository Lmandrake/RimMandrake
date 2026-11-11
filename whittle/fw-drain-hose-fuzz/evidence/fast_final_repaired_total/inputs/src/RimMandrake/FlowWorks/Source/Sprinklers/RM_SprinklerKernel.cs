// Verse-free (the SelfTest compiles this file): the sprinkler's arithmetic and decisions
// (SPRINKLER_HEADS_BUILD_PUMP_REQUIRED; design/RimMandrake/sprinklers_design_2026-10-16.md §1, §3 bold #1, §7 rulings).
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Sprinklers
{
    /// <summary>What a head did on its last pulse. Order matters only for reading; every state but Spraying draws nothing.</summary>
    public enum RM_SprinklerState
    {
        Idle,        // never pulsed yet
        Disabled,    // sprinklersEnabled off (native) / adapter off (VFE)
        SwitchedOff, // its flick switch
        NoPressure,  // OQ-S2: no working pump on the head's network
        NoLiquid,    // the net holds no liquid at all
        Clogged,     // §1.8: Thick or Heavy liquid
        Dry,         // the net cannot pay the whole pulse (all-or-nothing, §1.1)
        NoCells,     // nothing to water (walls all round, or the valve found nothing worth watering)
        Budget,      // VFE thirst valve: daily budget or reserve floor reached
        Spraying,
    }

    /// <summary>One cell the thirst valve weighs (§3 bold #1). Index is the caller's, Dist the distance from the head.</summary>
    public struct RM_ValveCell
    {
        public int Index;
        public float Dist;
        public bool HasPlant, Sealed, AlreadyWet, Lit, Exempt;

        public RM_ValveCell(int index, float dist, bool hasPlant, bool @sealed, bool alreadyWet, bool lit, bool exempt)
        {
            Index = index; Dist = dist; HasPlant = hasPlant; Sealed = @sealed; AlreadyWet = alreadyWet; Lit = lit; Exempt = exempt;
        }
    }

    public static class RM_SprinklerKernel
    {
        /// <summary>§1.3 PROPOSED: one pulse a game hour, 250 ticks of grace past the next pulse.</summary>
        public const int PulseTicks = 2500;
        public const int GraceTicks = 250;

        /// <summary>OQ-S1 RULED: 0.5 L per cell per hour (the settings default).</summary>
        public const float RuledLitresPerCellHour = 0.5f;

        /// <summary>§2 PROPOSED: the native head's radius (29 cells incl. its own).</summary>
        public const float NativeRadius = 2.9f;

        /// <summary>The tank units one pulse costs: cells x litres x units-per-litre, rounded up (never free).</summary>
        public static int UnitsFor(int cells, float litresPerCellHour, int unitsPerLitre)
        {
            if (cells <= 0 || litresPerCellHour <= 0f || unitsPerLitre <= 0) return 0;
            return (int)Math.Ceiling(Math.Round(cells * (double)litresPerCellHour * unitsPerLitre, 3));
        }

        /// <summary>§1.1/§1.2: a paid pulse keeps its cells wet until the next pulse is due plus the grace.</summary>
        public static int WetUntil(int now) => now + PulseTicks + GraceTicks;

        public static bool IsWet(int wetUntil, int now) => now < wetUntil;

        /// <summary>§1.8: Thin and Water spray; Thick and Heavy clog the head.</summary>
        public static bool Sprays(bool thickOrHeavy) => !thickOrHeavy;

        /// <summary>The whole pre-draw decision (§1.1, §1.8, §1.9). <paramref name="available"/> is the net's units of the
        /// chosen liquid; the pulse is all-or-nothing, so anything below <paramref name="need"/> is Dry.</summary>
        public static RM_SprinklerState Decide(bool enabled, bool switchOn, bool pressure, bool hasLiquid, bool thickOrHeavy,
                                               int cells, int need, int available)
        {
            if (!enabled) return RM_SprinklerState.Disabled;
            if (!switchOn) return RM_SprinklerState.SwitchedOff;
            if (!pressure) return RM_SprinklerState.NoPressure;
            if (!hasLiquid) return RM_SprinklerState.NoLiquid;
            if (!Sprays(thickOrHeavy)) return RM_SprinklerState.Clogged;
            if (cells <= 0 || need <= 0) return RM_SprinklerState.NoCells;
            if (available < need) return RM_SprinklerState.Dry;
            return RM_SprinklerState.Spraying;
        }

        /// <summary>The liquid the head sprays (§2 "no liquid picker"): the one its net holds most of, ties by key (ordinal).
        /// Null when the net holds nothing.</summary>
        public static string PickLiquid(IEnumerable<KeyValuePair<string, int>> held)
        {
            var sums = new Dictionary<string, int>();
            foreach (KeyValuePair<string, int> kv in held)
            {
                if (kv.Key == null || kv.Value <= 0) continue;
                sums.TryGetValue(kv.Key, out int s);
                sums[kv.Key] = s + kv.Value;
            }
            string best = null;
            int bestUnits = 0;
            foreach (KeyValuePair<string, int> kv in sums)
            {
                if (kv.Value > bestUnits || (kv.Value == bestUnits && best != null && string.CompareOrdinal(kv.Key, best) < 0))
                {
                    best = kv.Key;
                    bestUnits = kv.Value;
                }
            }
            return best;
        }

        /// <summary>The native head (dumb, §1.5/§1.6): every covered cell is charged except SEALED ones (basins, pots: H1).</summary>
        public static List<int> NativeCharge(IList<RM_ValveCell> cells)
        {
            var kept = new List<int>();
            foreach (RM_ValveCell c in cells) if (!c.Sealed) kept.Add(c.Index);
            return kept;
        }

        /// <summary>Does water change growth on this cell (§3 bold #1)? A plant, not sealed, not already wet by another source,
        /// lit, not exempt.</summary>
        public static bool ValveWants(RM_ValveCell c) => c.HasPlant && !c.Sealed && !c.AlreadyWet && c.Lit && !c.Exempt;

        /// <summary>The thirst valve (§3 bold #1, OQ-S4): only cells where water changes growth, nearest first, trimmed from the
        /// farthest so the pulse fits the day's budget left (<paramref name="budgetLeftUnits"/>, &lt; 0 = no budget) and keeps the
        /// net above the reserve floor (<paramref name="netUnits"/> - pulse &gt;= <paramref name="reserveUnits"/>). Ties by index.</summary>
        public static List<int> Valve(IList<RM_ValveCell> cells, float litresPerCellHour, int unitsPerLitre, int budgetLeftUnits,
                                      int netUnits, int reserveUnits, out bool trimmed)
        {
            var want = new List<RM_ValveCell>();
            foreach (RM_ValveCell c in cells) if (ValveWants(c)) want.Add(c);
            want.Sort((a, b) => a.Dist != b.Dist ? a.Dist.CompareTo(b.Dist) : a.Index.CompareTo(b.Index));
            int cap = want.Count;
            if (budgetLeftUnits >= 0) cap = Math.Min(cap, MaxCellsFor(budgetLeftUnits, litresPerCellHour, unitsPerLitre));
            if (reserveUnits > 0) cap = Math.Min(cap, MaxCellsFor(Math.Max(0, netUnits - reserveUnits), litresPerCellHour, unitsPerLitre));
            trimmed = cap < want.Count;
            var kept = new List<int>(cap);
            for (int i = 0; i < cap; i++) kept.Add(want[i].Index);
            return kept;
        }

        /// <summary>The most cells <paramref name="units"/> pays for in one pulse.</summary>
        public static int MaxCellsFor(int units, float litresPerCellHour, int unitsPerLitre)
        {
            if (units <= 0 || litresPerCellHour <= 0f || unitsPerLitre <= 0) return 0;
            int n = (int)Math.Floor(units / (litresPerCellHour * (double)unitsPerLitre) + 1e-9);
            while (n > 0 && UnitsFor(n, litresPerCellHour, unitsPerLitre) > units) n--;
            return n;
        }

        /// <summary>Units of the daily budget left (litres/day x units-per-litre - spent today); &lt; 0 = no budget set.</summary>
        public static int BudgetLeft(int budgetLitresPerDay, int spentTodayUnits, int unitsPerLitre)
        {
            if (budgetLitresPerDay <= 0) return -1;
            return Math.Max(0, budgetLitresPerDay * unitsPerLitre - spentTodayUnits);
        }

        /// <summary>The units the valve saved this pulse against watering every covered unsealed cell.</summary>
        public static int Saved(int coveredUnsealed, int charged, float litresPerCellHour, int unitsPerLitre)
            => Math.Max(0, UnitsFor(coveredUnsealed, litresPerCellHour, unitsPerLitre) - UnitsFor(charged, litresPerCellHour, unitsPerLitre));
    }

    /// <summary>The per-cell wet record (§4 RM_MapComponent_Sprinklers' grid, Verse-free so the selftest drives it): a cell is
    /// sprinkled while now &lt; wetUntil; a fruiting crop spends it (EC3) until the next paid pulse re-wets it.</summary>
    public sealed class RM_SprinkledGrid
    {
        public readonly int[] wetUntil;
        public readonly int[] owner;
        public readonly ushort[] liquid;
        public readonly List<string> palette = new List<string> { null };

        public RM_SprinkledGrid(int cells)
        {
            wetUntil = new int[cells];
            owner = new int[cells];
            liquid = new ushort[cells];
        }

        public ushort KeyIndex(string key)
        {
            int i = palette.IndexOf(key);
            if (i < 0)
            {
                if (palette.Count >= ushort.MaxValue) return 0;
                palette.Add(key);
                i = palette.Count - 1;
            }
            return (ushort)i;
        }

        public void Wet(int cell, string key, int until, int headId)
        {
            if (cell < 0 || cell >= wetUntil.Length) return;
            wetUntil[cell] = until;
            owner[cell] = headId;
            liquid[cell] = KeyIndex(key);
        }

        /// <summary>The liquid key wetting the cell now, or null.</summary>
        public string WetBy(int cell, int now)
        {
            if (cell < 0 || cell >= wetUntil.Length || !RM_SprinklerKernel.IsWet(wetUntil[cell], now)) return null;
            return palette[liquid[cell]];
        }

        /// <summary>Wet now by a head other than <paramref name="headId"/>.</summary>
        public bool WetByOther(int cell, int headId, int now) => WetBy(cell, now) != null && owner[cell] != headId;

        /// <summary>EC3: a fruiting crop used the water; the cell is dry until the next paid pulse. True if it was wet.</summary>
        public bool Spend(int cell, int now)
        {
            if (WetBy(cell, now) == null) return false;
            wetUntil[cell] = 0;
            return true;
        }

        public int LiveCells(int now)
        {
            int n = 0;
            for (int i = 0; i < wetUntil.Length; i++) if (RM_SprinklerKernel.IsWet(wetUntil[i], now)) n++;
            return n;
        }
    }
}
