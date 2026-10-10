// JawaBenchTpsExplained.cs - how much of an observation interval was spent in IDENTIFIED work (long events,
// saves, frames spent waiting on an asynchronous long event), BRIDGE_TPS_REVIEW2_FIXES_1 MUST 15.
//
// ⛔ NO Verse, NO UnityEngine, NO HarmonyLib: compiled into the companion AND the offline harness. The
// sampler's hooks call in with Stopwatch seconds; TmuPrefix takes the explained seconds for its interval.

using System;

namespace JawaBench.BridgeTools
{
    /// <summary>
    /// Identified work is measured as INTERVALS and their UNION is taken against each observation interval
    /// (MUST 15): long-event scopes, SaveGame scopes (direct saves outside any long event included; a save
    /// nested in a long event counted once) and whole frames spent waiting on an asynchronous long event.
    /// Take(now) returns the covered seconds in (previous Take, now] - an open scope is split at the
    /// observation, never credited twice. Scopes are closed by Harmony FINALIZERS, so an exception in the
    /// original cannot leave one open; a scope still open at a game boundary is dropped by Reset().
    /// </summary>
    internal sealed class JawaBenchTpsExplained
    {
        private const int MaxIntervals = 64;
        private readonly double[] _s = new double[MaxIntervals], _e = new double[MaxIntervals];
        private int _n, _depth;
        private double _openStart, _lastTake, _prevRootPre;
        private bool _prevWaiting, _primed;

        private void Add(double s, double e)
        {
            if (e <= s) return;
            if (_n > 0 && s <= _e[_n - 1]) { if (e > _e[_n - 1]) _e[_n - 1] = e; return; }
            if (_n == MaxIntervals)
            {
                // bounded: merge the two oldest (over-covers the gap between them; only on pathological churn)
                _e[0] = _e[1];
                Array.Copy(_s, 2, _s, 1, _n - 2); Array.Copy(_e, 2, _e, 1, _n - 2);
                _n--;
            }
            _s[_n] = s; _e[_n] = e; _n++;
        }

        private void BeginScope(double now) { if (_depth++ == 0) _openStart = now; }

        private void EndScope(double now)
        {
            if (_depth == 0) return;
            if (--_depth == 0) Add(_openStart, now);
        }

        /// <summary>Start of Root.Update (every frame): a frame that was waiting on an async event is explained whole.</summary>
        internal void RootPre(double now)
        {
            if (_prevWaiting && _primed) Add(_prevRootPre, now);
            _prevRootPre = now;
            _primed = true;
        }

        /// <summary>End of Root.Update: is this frame waiting on an asynchronous long event?</summary>
        internal void RootPost(bool waiting) { _prevWaiting = waiting; }

        internal void LongEventBegin(double now) => BeginScope(now);
        internal void LongEventEnd(double now) => EndScope(now);
        internal void SaveBegin(double now) => BeginScope(now);
        internal void SaveEnd(double now) => EndScope(now);

        /// <summary>Covered seconds in (previous Take, now]; consumed.</summary>
        internal double Take(double now)
        {
            double from = _lastTake, sum = 0;
            int keep = 0;
            for (int i = 0; i < _n; i++)
            {
                double s = Math.Max(_s[i], from), e = Math.Min(_e[i], now);
                if (e > s) sum += e - s;
                if (_e[i] > now) { _s[keep] = Math.Max(_s[i], now); _e[keep] = _e[i]; keep++; }
            }
            _n = keep;
            if (_depth > 0)
            {
                double s = Math.Max(_openStart, from);
                if (now > s) sum += now - s;
            }
            if (now > _lastTake) _lastTake = now;
            return sum;
        }

        /// <summary>Game boundary: forget open scopes and unconsumed intervals.</summary>
        internal void Reset() { _n = 0; _depth = 0; _prevWaiting = false; }
    }
}
