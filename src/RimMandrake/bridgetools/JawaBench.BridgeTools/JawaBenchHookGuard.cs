// JawaBenchHookGuard.cs - the entry/exit discipline every TPS recorder Harmony hook goes through
// (TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS; GPT metrics review 2.3, bridge review 5.2/5.4).
//
// ⛔ NO Verse, NO UnityEngine, NO HarmonyLib: compiled into the companion AND into the offline harness
// (bridgetools/TpsMathSelfTest/UnitsHookGuard.cs), which replays foreign-thread, nested, orphan-finalizer,
// left-open and fault sequences through THIS file.
//
// THE PATTERN (each hook pair in JawaBenchTpsSampler / JawaBenchTpsProfiler):
//   prefix(out Scope __state)   : __state = default FIRST; then TryEnter(onMainThread) - the thread check and the
//                                 nesting check happen BEFORE any recorder state is read or written; then the body,
//                                 inside try/catch -> Fault (which disables that recorder, visibly).
//   postfix(bool __runOriginal) : only to COUNT a skipped original (a postfix is never proof the original ran).
//   finalizer(Scope __state, Exception __exception) : void, so the game's exception propagates unchanged; it
//                                 closes ONLY a scope its own prefix opened (Valid), counts an orphan (prefix never
//                                 ran: late install, or an earlier prefix threw), and is itself inside try/catch.
// All per-invocation values (start time, tick id, ticks before, GC count) live in the Scope struct the prefix hands
// its own finalizer - never in a static, so a nested or concurrent call cannot overwrite an outer measurement.
//
// Nesting: a guard either supports it (depth stack, inner scopes left open are closed by their outer and counted)
// or REJECTS it (the nested call records nothing and leaves the outer scope untouched), chosen per recorder.
// Depth is main-thread-only state: a foreign thread is rejected before it can touch it.

using System;
using System.Globalization;
using System.Threading;

namespace JawaBench.BridgeTools
{
    internal sealed class JawaBenchHookGuard
    {
        /// <summary>The per-invocation state a prefix hands its own finalizer (Harmony __state).</summary>
        internal struct Scope
        {
            internal bool Valid;        // this invocation entered; its finalizer must exit
            internal bool Rejected;     // deliberately not entered (foreign thread, nested, disabled): finalizer silent
            internal int Depth;         // depth this scope opened at (1 = outermost)
            internal long T0;           // free per-invocation slots for the hook's own values
            internal long T1;
            internal int I0;
            internal int I1;
        }

        internal readonly string Name;
        internal readonly bool AllowNesting;
        private int _depth;
        internal long Entered, ForeignRejected, NestedRejected, OrphanExits, Unbalanced, OriginalSkipped, OriginalThrew;
        internal long Faults;
        internal volatile bool Disabled;
        internal string LastFault;

        internal JawaBenchHookGuard(string name, bool allowNesting)
        {
            Name = name;
            AllowNesting = allowNesting;
        }

        internal int Depth => _depth;

        /// <summary>Order is the contract: disabled, then THREAD, then nesting - nothing else is touched first.</summary>
        internal bool TryEnter(bool onMainThread, out Scope s)
        {
            s = default(Scope);
            if (Disabled) { s.Rejected = true; return false; }
            if (!onMainThread) { Interlocked.Increment(ref ForeignRejected); s.Rejected = true; return false; }
            if (_depth > 0 && !AllowNesting) { NestedRejected++; s.Rejected = true; return false; }
            _depth++;
            Entered++;
            s.Valid = true;
            s.Depth = _depth;
            return true;
        }

        /// <summary>Close exactly the scope this invocation opened. Returns true when it closed something.</summary>
        internal bool Exit(Scope s)
        {
            if (!s.Valid)
            {
                if (!s.Rejected) OrphanExits++;
                return false;
            }
            if (_depth < s.Depth) return false;                 // already closed by an outer exit
            if (_depth > s.Depth) Unbalanced++;                 // inner scope(s) left open: closed with ours
            _depth = s.Depth - 1;
            return true;
        }

        internal void NoteOriginal(bool ran) { if (!ran) Interlocked.Increment(ref OriginalSkipped); }
        internal void NoteThrew() { Interlocked.Increment(ref OriginalThrew); }

        /// <summary>Our own body failed: disable this recorder and say where. Never rethrows.</summary>
        internal void Fault(string where, Exception e)
        {
            Interlocked.Increment(ref Faults);
            try { LastFault = where + ": " + (e == null ? "?" : e.GetType().Name + ": " + e.Message); } catch { }
            Disabled = true;
        }

        /// <summary>ok | degraded (something was not measured: a rejection, an orphan, a skipped original) |
        /// disabled (a fault). A writer/recorder fault is coverage failure, never silence.</summary>
        internal string Coverage
        {
            get
            {
                if (Disabled || Faults > 0) return "disabled";
                if (ForeignRejected + NestedRejected + OrphanExits + Unbalanced + OriginalSkipped + OriginalThrew > 0) return "degraded";
                return "ok";
            }
        }

        internal string CoverageFields()
        {
            string I(long v) => v.ToString(CultureInfo.InvariantCulture);
            return "\"hook\":" + JawaBenchTpsMath.Json(Name) + ",\"coverage\":\"" + Coverage + "\",\"entered\":" + I(Entered) +
                   ",\"foreignRejected\":" + I(Interlocked.Read(ref ForeignRejected)) + ",\"nestedRejected\":" + I(NestedRejected) +
                   ",\"orphanExits\":" + I(OrphanExits) + ",\"unbalanced\":" + I(Unbalanced) +
                   ",\"originalSkipped\":" + I(Interlocked.Read(ref OriginalSkipped)) + ",\"originalThrew\":" + I(Interlocked.Read(ref OriginalThrew)) +
                   ",\"faults\":" + I(Interlocked.Read(ref Faults)) + ",\"lastFault\":" + JawaBenchTpsMath.Json(LastFault);
        }

        internal void ResetForTest()
        {
            _depth = 0; Entered = ForeignRejected = NestedRejected = OrphanExits = Unbalanced = OriginalSkipped = OriginalThrew = Faults = 0;
            Disabled = false; LastFault = null;
        }
    }
}
