// JawaBenchCompTimingCore.cs - the pure bookkeeping behind jawa/game_comp_timing (GAMECOMP_STALL_HUNT_SEVEN_SECONDS).
//
// No Verse, no Unity, no Harmony: TpsMathSelfTest compiles this PRODUCTION file directly and drives it offline
// (UnitsCompTiming.cs). The tool owns the patches and the clock; this file owns what a timed call becomes:
//   * per-key rows (calls, total, max, the game tick of the max) - the "which component is expensive" view;
//   * a bounded list of SPIKES (single calls >= a threshold), largest kept when it overflows - the "who caused
//     the one-off 6.76 s stall" view that a total over hundreds of ticks drowns;
//   * load tracking: a game object other than the one armed in is a LOAD, and every spike carries ticks since
//     that load (-1 when no load was seen), so a stall "18 ticks after load" is recognisable as one;
//   * a roll-up of the rows by owner (mod);
//   * the worst STAGE call (one whole GameComponentUtility.GameComponentTick) and the component that took the most of
//     THAT call, so "the stage stalled 6.76 s" and "this component took 6.7 s of it" are one event, not two numbers
//     that merely look alike.
// Durations are opaque integers (Stopwatch ticks in game, anything in the tests); conversion is the caller's.

using System;
using System.Collections.Generic;
using System.Linq;

namespace JawaBench.BridgeTools
{
    internal sealed class JawaBenchCompTimingCore<TKey>
    {
        internal sealed class Row
        {
            public long Calls, Total, Max;
            public int MaxAtTick = -1;
        }

        internal struct Spike
        {
            public TKey Key;
            public long Dur;
            public int Tick;            // game tick of the call
            public int SinceLoad;       // ticks since the last load this run saw, -1 if none was seen
            public int Load;            // 0 = the game armed in; n = the n-th load seen while armed
        }

        internal struct OwnerRow
        {
            public string Owner;
            public long Calls, Total, Max;
            public int Keys;
        }

        public readonly Dictionary<TKey, Row> Rows = new Dictionary<TKey, Row>();
        public readonly List<Spike> Spikes = new List<Spike>();
        public readonly long SpikeThreshold;   // a call >= this is a spike; <= 0 records none
        public readonly int SpikeCap;          // how many spikes are kept (largest win); <= 0 keeps none
        public long SpikesSeen;                // every spike, kept or dropped
        public int Loads;                      // loads seen while armed
        public int TicksObserved;              // distinct game ticks noted through NoteTick, summed over games

        // The worst stage call, its tick, load index, and the largest component call inside it.
        public long StageMax;
        public int StageMaxAtTick = -1, StageMaxLoad = -1, StageMaxSinceLoad = -1;
        public TKey StageMaxTop;
        public long StageMaxTopDur = -1;   // -1: no component call was timed inside the worst stage call
        private bool inStage;
        private TKey curTop;
        private long curTopDur = -1;

        private object game;                   // reference identity only, never dereferenced; set by Arm
        private int loadTick = -1;
        private int lastTick = int.MinValue;

        public JawaBenchCompTimingCore(long spikeThreshold, int spikeCap)
        {
            SpikeThreshold = spikeThreshold;
            SpikeCap = spikeCap;
        }

        /// <summary>Call once when arming, with the game running at that moment (null at the menu or mid-load).
        /// Any OTHER game object later passed to NoteTick is a load.</summary>
        public void Arm(object currentGame)
        {
            game = currentGame; loadTick = -1; lastTick = int.MinValue;
        }

        /// <summary>Start of one game tick (once per tick, before that tick's components run).</summary>
        public void NoteTick(object currentGame, int tick)
        {
            if (!ReferenceEquals(currentGame, game))
            {
                Loads++; loadTick = tick; game = currentGame; lastTick = int.MinValue;
            }
            if (tick != lastTick) { TicksObserved++; lastTick = tick; }
        }

        /// <summary>A stage call begins (after NoteTick). Component calls added until StageEnd belong to it.</summary>
        public void StageBegin() { inStage = true; curTop = default(TKey); curTopDur = -1; }

        /// <summary>The stage call that began with StageBegin ended after <paramref name="dur"/>.</summary>
        public void StageEnd(long dur, int tick)
        {
            if (!inStage) return;
            inStage = false;
            if (dur < 0) dur = 0;
            if (StageMaxAtTick < 0 || dur > StageMax)
            {
                StageMax = dur; StageMaxAtTick = tick; StageMaxLoad = Loads; StageMaxSinceLoad = SinceLoad(tick);
                StageMaxTop = curTop; StageMaxTopDur = curTopDur;
            }
        }

        public int SinceLoad(int tick) => loadTick < 0 ? -1 : tick - loadTick;

        /// <summary>One timed call of <paramref name="key"/> at game tick <paramref name="tick"/>.</summary>
        public void Add(TKey key, long dur, int tick)
        {
            if (dur < 0) dur = 0;
            if (!Rows.TryGetValue(key, out var r)) { r = new Row(); Rows[key] = r; }
            r.Calls++; r.Total += dur;
            if (r.MaxAtTick < 0 || dur > r.Max) { r.Max = dur; r.MaxAtTick = tick; }
            if (inStage && dur > curTopDur) { curTop = key; curTopDur = dur; }
            if (SpikeThreshold <= 0 || dur < SpikeThreshold) return;
            SpikesSeen++;
            if (SpikeCap <= 0) return;
            var s = new Spike { Key = key, Dur = dur, Tick = tick, SinceLoad = SinceLoad(tick), Load = Loads };
            if (Spikes.Count < SpikeCap) { Spikes.Add(s); return; }
            int min = 0;
            for (int i = 1; i < Spikes.Count; i++) if (Spikes[i].Dur < Spikes[min].Dur) min = i;
            if (dur > Spikes[min].Dur) Spikes[min] = s;
        }

        /// <summary>Rows largest total first; ties by max, then key text, so the order is deterministic.</summary>
        public List<KeyValuePair<TKey, Row>> Ranked() =>
            Rows.OrderByDescending(kv => kv.Value.Total).ThenByDescending(kv => kv.Value.Max)
                .ThenBy(kv => kv.Key?.ToString() ?? "", StringComparer.Ordinal).ToList();

        /// <summary>Spikes largest first, then earliest load, then earliest tick.</summary>
        public List<Spike> RankedSpikes() =>
            Spikes.OrderByDescending(s => s.Dur).ThenBy(s => s.Load).ThenBy(s => s.Tick).ToList();

        /// <summary>Rows rolled up by owner (mod), largest total first. A null/empty owner becomes "?".</summary>
        public List<OwnerRow> ByOwner(Func<TKey, string> owner)
        {
            var acc = new Dictionary<string, OwnerRow>(StringComparer.Ordinal);
            foreach (var kv in Rows)
            {
                string o = owner(kv.Key);
                if (string.IsNullOrEmpty(o)) o = "?";
                acc.TryGetValue(o, out var a);
                a.Owner = o; a.Calls += kv.Value.Calls; a.Total += kv.Value.Total; a.Keys++;
                if (kv.Value.Max > a.Max) a.Max = kv.Value.Max;
                acc[o] = a;
            }
            return acc.Values.OrderByDescending(a => a.Total).ThenByDescending(a => a.Max)
                .ThenBy(a => a.Owner, StringComparer.Ordinal).ToList();
        }
    }
}
