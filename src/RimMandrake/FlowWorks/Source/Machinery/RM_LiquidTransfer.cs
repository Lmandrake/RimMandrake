// Verse-free (the FlowWorks SelfTest compiles this file): the ONE transfer service every liquid move goes through
// (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md §4 "One transfer service", build step L1).
//
//   Move(units, source, destination):
//     1. validate both legs (Can: read-only, nothing changes on a refusal here);
//     2. the REVERSIBLE leg goes first (a tank: removed from, or reserved by adding to);
//     3. the other leg (often the world: TryTakeLevel / TryDebit / TryPourLevel, which cannot be undone) goes last, so its
//        refusal is the only failure after a change, and that change is on our side;
//     4. on a refusal (or a partial accept at a boundary) the first leg is put back;
//     5. the caller credits hoses and counters only when Move returned the units moved (a committed move).
//
// A leg is a set of closures written AT the call site, so the mutation each site makes is visible where it happens and
// TransferChecks.cs can read it from the production source (caller coverage). Units are whatever both legs agree on: tank
// units for a pump or a feed, BATCHES for a converter or a reactor (each leg multiplies by its own per-batch amount).
using System;

namespace RimMandrake.FlowWorks.Machinery
{
    /// <summary>One side of a transfer. <see cref="Can"/> is read-only; <see cref="Do"/> mutates and returns the units it
    /// actually did (0 = refused, nothing changed); <see cref="Undo"/> reverses units of a Do (null = irreversible: the world).
    /// A reversible leg is all-or-nothing on Do (it returns k or 0); only an irreversible boundary leg may accept part.</summary>
    public sealed class RM_TransferLeg
    {
        public readonly string Kind;
        public readonly Func<int, bool> Can;
        public readonly Func<int, int> Do;
        public readonly Func<int, bool> Undo;

        public bool Reversible => Undo != null;

        public RM_TransferLeg(string kind, Func<int, bool> can, Func<int, int> @do, Func<int, bool> undo)
        {
            Kind = kind;
            Can = can ?? (k => true);
            Do = @do;
            Undo = undo;
        }

        /// <summary>A tank (or any store we own): all-or-nothing, put back by <paramref name="undo"/>.</summary>
        public static RM_TransferLeg Store(Func<int, bool> can, Func<int, bool> @do, Func<int, bool> undo) =>
            new RM_TransferLeg("store", can, k => @do(k) ? k : 0, undo);

        /// <summary>The world (a channel level, a body's stock, a pour into a cell): checked by <paramref name="can"/> before
        /// anything changes, never undone, so Move runs it after the reversible leg.</summary>
        public static RM_TransferLeg World(Func<int, bool> can, Func<int, bool> @do) =>
            new RM_TransferLeg("world", can, k => @do(k) ? k : 0, null);

        /// <summary>The world as a SOURCE whose take can be put back (rev 2 §3.3 world-to-world pump move: a channel level is poured
        /// back, a body's debit credited back). Move runs it first, and the destination cell (checked by its own Can) last.</summary>
        public static RM_TransferLeg World(Func<int, bool> can, Func<int, bool> @do, Func<int, bool> undo) =>
            new RM_TransferLeg("world", can, k => @do(k) ? k : 0, undo);

        /// <summary>Where consumed liquid goes and never comes back (a finished bath craft, a vent): always accepts.</summary>
        public static RM_TransferLeg Sink(Action<int> take) =>
            new RM_TransferLeg("sink", k => true, k => { take?.Invoke(k); return k; }, null);

        /// <summary>A foreign store that may accept PART (the VE pipe-net boundary, read back after the call): returns the units
        /// it settled; Move puts the rest back on the reversible side.</summary>
        public static RM_TransferLeg Boundary(Func<int, bool> can, Func<int, int> @do) =>
            new RM_TransferLeg("boundary", can, @do, null);

        /// <summary>Every leg moves k together (a reactor's two reactants). A refusal of any undoes the ones already done.</summary>
        public static RM_TransferLeg All(params RM_TransferLeg[] legs)
        {
            return new RM_TransferLeg("all",
                k =>
                {
                    foreach (RM_TransferLeg l in legs) if (!l.Can(k)) return false;
                    return true;
                },
                k =>
                {
                    for (int i = 0; i < legs.Length; i++)
                    {
                        if (legs[i].Do(k) == k) continue;
                        for (int j = i - 1; j >= 0; j--) legs[j].Undo(k);
                        return 0;
                    }
                    return k;
                },
                k =>
                {
                    bool ok = true;
                    foreach (RM_TransferLeg l in legs) ok &= l.Undo(k);
                    return ok;
                });
        }

        /// <summary>k units split over <paramref name="parts"/> stores (a fill or draw plan, §3.2 split levels): part i takes
        /// <paramref name="partUnits"/>(i) tank units, and the parts sum to k x <paramref name="per"/> (per = tank units per Move
        /// unit: 1 for a pump level's units, a recipe's per-batch amount for a converter or reactor). All-or-nothing; Undo(m)
        /// takes m x per back from the LAST parts.</summary>
        public static RM_TransferLeg Split(int parts, Func<int, int> partUnits, Func<int, int, bool> can, Func<int, int, bool> @do,
                                           Func<int, int, bool> undo, int per = 1)
        {
            return new RM_TransferLeg("split",
                k =>
                {
                    int sum = 0;
                    for (int i = 0; i < parts; i++)
                    {
                        int u = partUnits(i);
                        if (u <= 0 || !can(i, u)) return false;
                        sum += u;
                    }
                    return parts > 0 && sum == k * per;
                },
                k =>
                {
                    for (int i = 0; i < parts; i++)
                    {
                        if (@do(i, partUnits(i))) continue;
                        for (int j = i - 1; j >= 0; j--) undo(j, partUnits(j));
                        return 0;
                    }
                    return k;
                },
                mb =>
                {
                    bool ok = true;
                    int m = mb * per;
                    for (int i = parts - 1; i >= 0 && m > 0; i--)
                    {
                        int u = Math.Min(m, partUnits(i));
                        ok &= undo(i, u);
                        m -= u;
                    }
                    return ok && m == 0;
                });
        }
    }

    public enum RM_MoveRefusal { None, Nothing, SourceCan, DestCan, SourceDo, DestDo, BothIrreversible, Partial }

    public struct RM_MoveOutcome
    {
        public int Moved;
        public RM_MoveRefusal Refused;
        /// <summary>Units a put-back could not return (the caller reports it; 0 in every correct build).</summary>
        public int Lost;
        public bool DestRefused => Refused == RM_MoveRefusal.DestCan || Refused == RM_MoveRefusal.DestDo;
    }

    public static class RM_LiquidTransfer
    {
        /// <summary>State read (probes, selftests): committed moves and put-backs this session.</summary>
        public static int Moves, PutBacks;

        /// <summary>Move <paramref name="units"/> from <paramref name="source"/> to <paramref name="dest"/> (§4). Returns the units
        /// moved; 0 leaves both sides exactly as they were. The caller credits hoses only when this returns &gt; 0, by the
        /// units returned.</summary>
        public static int Move(int units, RM_TransferLeg source, RM_TransferLeg dest, out RM_MoveOutcome o)
        {
            o = default;
            if (units <= 0 || source == null || dest == null) { o.Refused = RM_MoveRefusal.Nothing; return 0; }
            if (!source.Can(units)) { o.Refused = RM_MoveRefusal.SourceCan; return 0; }
            if (!dest.Can(units)) { o.Refused = RM_MoveRefusal.DestCan; return 0; }
            if (!source.Reversible && !dest.Reversible) { o.Refused = RM_MoveRefusal.BothIrreversible; return 0; }
            bool sourceFirst = source.Reversible;
            RM_TransferLeg first = sourceFirst ? source : dest, second = sourceFirst ? dest : source;
            RM_MoveRefusal firstRefused = sourceFirst ? RM_MoveRefusal.SourceDo : RM_MoveRefusal.DestDo;
            RM_MoveRefusal secondRefused = sourceFirst ? RM_MoveRefusal.DestDo : RM_MoveRefusal.SourceDo;
            int a = first.Do(units);
            if (a != units)
            {
                // a reversible leg is all-or-nothing by contract; one that did part is put back whole
                if (a > 0) PutBack(first, a, ref o);
                o.Refused = firstRefused;
                return 0;
            }
            int b = second.Do(units);
            if (b < 0) b = 0;
            if (b > units) b = units;
            if (b < units) PutBack(first, units - b, ref o);
            o.Moved = b;
            o.Refused = b == 0 ? secondRefused : b < units ? RM_MoveRefusal.Partial : RM_MoveRefusal.None;
            if (b > 0) Moves++;
            return b;
        }

        private static void PutBack(RM_TransferLeg leg, int units, ref RM_MoveOutcome o)
        {
            PutBacks++;
            if (!leg.Undo(units)) o.Lost += units;
        }

        // ---------------------------------------------------------------- the VE pipe-net boundary (§3.10 G5)
        // Invariant over every adapter call: tankUnits x perUnit + veStored + carry is unchanged. carry is the saved fractional
        // remainder (resource taken from the VE net not yet whole tank units, or, negative, resource the net accepted beyond the
        // units debited for it); it is never rounded away.

        /// <summary>Send: the VE storage's read-back gain <paramref name="delta"/> for <paramref name="units"/> units offered.
        /// Returns the units it absorbed (the rest go back into the tank); the remainder goes into <paramref name="carry"/>.
        /// PIPE_ADAPTER_FIX_DEBT_NEVER_PAID (C1-F8): a negative carry is resource the net already got beyond the units debited
        /// for it (an earlier partial accept); it counts toward these units, so the debt is charged to the tank, never forgiven
        /// (the adapter offers <see cref="SendAsk"/>, the units' resource less that debt).
        /// -1 = a non-finite reading or ratio (the adapter fails closed and moves nothing more).</summary>
        public static int SettleSend(float delta, float perUnit, int units, ref float carry)
        {
            if (!Finite(delta) || !Finite(perUnit) || perUnit <= 0f || !Finite(carry)) return -1;
            int u = (int)Math.Floor((delta + Math.Max(0f, -carry)) / perUnit + 1e-4);
            u = Math.Max(0, Math.Min(units, u));
            carry -= delta - u * perUnit;
            return u;
        }

        /// <summary>Send: the resource offered to the VE net for <paramref name="units"/> units, less any debt a negative
        /// <paramref name="carry"/> holds (never below 0).</summary>
        public static float SendAsk(int units, float perUnit, float carry) => Math.Max(0f, units * perUnit - Math.Max(0f, -carry));

        /// <summary>Take: the VE storage's read-back loss <paramref name="delta"/> after asking for <paramref name="units"/> units.
        /// Returns the whole units it pays for (carry included, at most <paramref name="units"/>); the remainder stays in carry.</summary>
        public static int SettleTake(float delta, float perUnit, int units, ref float carry)
        {
            if (!Finite(delta) || !Finite(perUnit) || perUnit <= 0f || !Finite(carry)) return -1;
            float total = carry + delta;
            int u = (int)Math.Floor(total / perUnit + 1e-4);
            u = Math.Max(0, Math.Min(units, u));
            carry = total - u * perUnit;
            return u;
        }

        private static bool Finite(float f) => !float.IsNaN(f) && !float.IsInfinity(f);
    }
}
