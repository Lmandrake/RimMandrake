using System;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.Aftermath
{
    // design/CHRONICLE_EVENT_SPINE.md, "Subscription": a plain static C#
    // event, not a Def-registered hook -- the idiom this suite already ships
    // (RimMandrake.Property's PropertyEvents), needing no load-order Def
    // resolution and binding cleanly by reflection when this mod is absent.
    //
    // NOTHING here knows any consumer. The engine raises; whoever is loaded
    // listens. This is the whole point of CHRONICLE_NINEFOLD_DECOUPLE_1: the
    // recorder used to call GameComponent_Ninefold.ApplyDelta directly, which
    // cost this mod a hard modDependency and a compile-time assembly
    // reference on mandrake.rm.ninefold.
    //
    // 🔴 Type name, method names and the ChronicleEvent field names are a
    // REFLECTION CONTRACT (soft-hook law 3): consumers bind by string and a
    // rename breaks them with no compile error on either side. The gated
    // Aftermath -> RimChronicle rename row must move the consumers' name
    // strings in the same change; RimMandrake.Ninefold.ChronicleSubscriber
    // already probes the post-rename name first for that reason.
    public static class ChronicleEvents
    {
        // The spine event. A consumer that DOES hold a compile-time
        // reference to this assembly (none in v1 -- see the soft-hook law)
        // would use this directly; everyone else goes through Subscribe.
        public static event Action<ChronicleEvent> EventClosed;

        public static void Raise(ChronicleEvent e)
        {
            if (e == null) return;
            Action<ChronicleEvent> handlers = EventClosed;
            if (handlers == null) return;

            // Per-handler isolation, deliberately not a bare Invoke: the
            // spine has several independent consumers and one that throws
            // must not silently cancel the ones after it in the invocation
            // list (which is exactly what a single Invoke would do).
            foreach (Delegate d in handlers.GetInvocationList())
            {
                try
                {
                    ((Action<ChronicleEvent>)d)(e);
                }
                catch (Exception ex)
                {
                    Log.Error("[RimMandrake.Aftermath] chronicle consumer " +
                        (d.Method?.DeclaringType?.FullName ?? "?") + "." +
                        (d.Method?.Name ?? "?") + " threw on '" + e.Kind + "': " + ex);
                }
            }
        }

        // --- Reflection-friendly subscription --------------------------------
        //
        // A consumer with no assembly reference to this mod cannot name
        // Action<ChronicleEvent>, so it cannot build a delegate for the event
        // above without relying on relaxed delegate binding. Action<object>
        // is nameable by BOTH sides (it lives in mscorlib), so this pair is
        // the front door every soft consumer actually uses:
        //
        //   var t = AccessTools.TypeByName("RimMandrake.Aftermath.ChronicleEvents");
        //   t?.GetMethod("Subscribe")?.Invoke(null, new object[] { (Action<object>)Handler });
        //
        // The wrapper delegates are kept so Unsubscribe can find them again
        // (a lambda handed to `-=` would never match).
        private static readonly Dictionary<Action<object>, Action<ChronicleEvent>> Wrappers =
            new Dictionary<Action<object>, Action<ChronicleEvent>>();

        public static void Subscribe(Action<object> handler)
        {
            if (handler == null || Wrappers.ContainsKey(handler)) return;
            Action<ChronicleEvent> wrapper = e => handler(e);
            Wrappers[handler] = wrapper;
            EventClosed += wrapper;
        }

        public static void Unsubscribe(Action<object> handler)
        {
            if (handler == null) return;
            if (!Wrappers.TryGetValue(handler, out Action<ChronicleEvent> wrapper)) return;
            EventClosed -= wrapper;
            Wrappers.Remove(handler);
        }
    }
}
