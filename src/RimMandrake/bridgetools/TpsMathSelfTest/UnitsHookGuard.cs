// Production Harmony hook discipline (TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS): every TPS recorder hook
// (sampler, profiler, long event) enters and leaves through the PRODUCTION JawaBenchHookGuard, so these
// sequences are what the live hooks do: foreign thread, nesting, a finalizer whose prefix never ran (late
// install / skipped prefix), an inner scope left open by an exception, a fault in our own body.
using System;
using G = JawaBench.BridgeTools.JawaBenchHookGuard;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static void T_GuardForeignThreadRejectedBeforeState()
        {
            var g = new G("tmu", allowNesting: false);
            bool ok = g.TryEnter(onMainThread: false, out var s);
            Check(!ok && s.Rejected && !s.Valid, "a foreign-thread call must be rejected with a rejected (not valid) scope");
            Check(g.Depth == 0 && g.Entered == 0 && g.ForeignRejected == 1, "rejection must touch no recorder state but its counter: depth " + g.Depth + " entered " + g.Entered + " foreign " + g.ForeignRejected);
            g.Exit(s);
            Check(g.Depth == 0 && g.OrphanExits == 0, "the rejected scope's finalizer is silent: depth " + g.Depth + " orphans " + g.OrphanExits);
        }

        private static void T_GuardNestedRejectedKeepsOuterState()
        {
            var g = new G("tick", allowNesting: false);
            Check(g.TryEnter(true, out var outer), "outer enters");
            outer.T0 = 100; outer.I0 = 7;
            bool inner = g.TryEnter(true, out var s2);
            Check(!inner && s2.Rejected && g.NestedRejected == 1 && g.Depth == 1, "a nested call is rejected without touching the outer scope: depth " + g.Depth);
            g.Exit(s2);
            Check(g.Depth == 1, "the rejected inner finalizer must not close the outer scope: depth " + g.Depth);
            Check(outer.T0 == 100 && outer.I0 == 7, "outer per-invocation state survives the nested call");
            g.Exit(outer);
            Check(g.Depth == 0 && g.Unbalanced == 0, "outer exit balances: depth " + g.Depth);
        }

        private static void T_GuardNestingAllowedIsBalanced()
        {
            var g = new G("save", allowNesting: true);
            g.TryEnter(true, out var a);
            g.TryEnter(true, out var b);
            Check(g.Depth == 2 && a.Depth == 1 && b.Depth == 2, "nesting allowed: depths " + a.Depth + "," + b.Depth);
            g.Exit(b); g.Exit(a);
            Check(g.Depth == 0 && g.Unbalanced == 0, "nested exits balance");
        }

        private static void T_GuardOrphanFinalizerIsCountedNotApplied()
        {
            var g = new G("le", allowNesting: false);
            g.Exit(default(G.Scope));        // late install / another prefix threw before ours ran
            Check(g.Depth == 0 && g.OrphanExits == 1, "a finalizer with no prefix changes nothing and is counted: depth " + g.Depth + " orphans " + g.OrphanExits);
            Check(g.TryEnter(true, out var s) && g.Depth == 1, "after an orphan the next pair still works");
            g.Exit(s);
            Check(g.Depth == 0, "pair balanced after orphan");
        }

        private static void T_GuardInnerLeftOpenClosedByOuter()
        {
            var g = new G("x", allowNesting: true);
            g.TryEnter(true, out var outer);
            g.TryEnter(true, out var inner);    // its finalizer never runs (would not happen with finalizers; defence)
            g.Exit(outer);
            Check(g.Depth == 0 && g.Unbalanced == 1, "an outer exit closes an inner scope left open, counted: depth " + g.Depth + " unbalanced " + g.Unbalanced);
            g.Exit(inner);
            Check(g.Depth == 0, "a late inner exit can never drive depth negative: " + g.Depth);
        }

        private static void T_GuardFaultDisablesAndIsVisible()
        {
            var g = new G("root", allowNesting: false);
            g.TryEnter(true, out var s);
            g.Fault("root-prefix", new InvalidOperationException("boom"));
            Check(g.Disabled && g.Faults == 1 && g.LastFault.Contains("root-prefix") && g.LastFault.Contains("boom"), "a fault disables and names itself: " + g.LastFault);
            g.Exit(s);
            Check(g.Depth == 0, "a scope opened before the fault still closes");
            Check(!g.TryEnter(true, out var s2) && s2.Rejected && g.ForeignRejected == 0, "disabled: entry refused without counting as foreign");
            Check(g.Coverage == "disabled", "coverage says disabled, never ok: " + g.Coverage);
            string f = g.CoverageFields();
            Check(f.Contains("\"coverage\":\"disabled\"") && f.Contains("\"faults\":1"), "coverage fields carry the fault: " + f);
        }

        private static void T_GuardOriginalSkippedAndThrewCounted()
        {
            var g = new G("tmu", allowNesting: false);
            Check(g.Coverage == "ok", "fresh guard reads ok");
            g.NoteOriginal(false);
            g.NoteThrew();
            Check(g.OriginalSkipped == 1 && g.OriginalThrew == 1, "skipped/threw originals are counted");
            g.TryEnter(false, out _);
            Check(g.Coverage == "degraded", "a rejection or skipped original makes coverage degraded: " + g.Coverage);
            g.ResetForTest();
            Check(g.Coverage == "ok" && g.Depth == 0 && g.Faults == 0, "reset");
        }
    }
}
