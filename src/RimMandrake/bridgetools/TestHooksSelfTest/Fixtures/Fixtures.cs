// Fixtures.cs - the fixture mods of selftest_test_hooks.py, one source for seven builds (Fixture.props, the FIX_* defines). Each
// build is its own assembly; A and B hold the SAME type names, so that two mods' hooks are seen not to collide.
using System.Collections.Generic;
#if !FIX_NONE
using RimMandrake.Shared.TestHooks;
#endif

namespace RimMandrake.HookFixture
{
    public static class State
    {
        public static readonly List<int> Pending = new List<int>();
        public static int Counter;

        /// <summary>Dirties the state on purpose: the harness calls it between the clean and the dirty digest read.</summary>
        public static void Poke() { Counter++; Pending.Add(Counter); }

#if !FIX_NONE
        /// <summary>A branch of the mod, with its trace points.</summary>
        public static void Work()
        {
            RMTrace.Emit("worked");
            RMTrace.Emit("worked", "counter", (long)Counter);
            RMTrace.Emit("worked", "ratio", 0.5);
            RMTrace.Emit("worked", "who", "fixture");
            RMTrace.Emit("worked", "ok", true);
        }
#endif
    }

#if FIX_GOOD
    public static class Hooks
    {
        [RMReset]
        public static string Reset(string scope)
        {
            int n = State.Pending.Count;
            State.Pending.Clear();
            State.Counter = 0;
            return "pending " + n;
        }

        [RMDigest]
        public static string Digest(string scope)
        {
            return State.Counter + ":" + State.Pending.Count;
        }
    }
#endif

#if FIX_CONST
    public static class Hooks
    {
        [RMReset]
        public static string Reset(string scope) { State.Pending.Clear(); State.Counter = 0; return "cleared"; }

        /// <summary>The wrong code of the item (GPT's case): a digest that answers a constant.</summary>
        [RMDigest]
        public static string Digest(string scope) { return "same"; }
    }
#endif

#if FIX_WRONG
    public class Hooks
    {
        [RMReset]
        public string Reset(string scope) { return ""; }                       // not static

        [RMDigest]
        public static string Digest(int scope) { return ""; }                  // takes an int
    }

    public static class MoreHooks
    {
        [RMReset]
        public static void ResetVoid(string scope) { }                         // returns void
    }
#endif

#if FIX_LEAK
    public static class Leak
    {
        /// <summary>The fault of this build: the mod names a type of the companion.</summary>
        public static string Name() { return JawaBench.BridgeTools.FakeCompanionType.Name; }
    }
#endif
}
