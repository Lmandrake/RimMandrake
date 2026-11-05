// HOSE_REPLAY_WIRE_MONO_TIMING_LANE: the two runtime calls that differ between the .NET 8 replay and its net472 twin run under
// the game's own Mono (Mono/). On .NET 8 they are direct calls. On net472 the reference assemblies lack
// GC.GetAllocatedBytesForCurrentThread, so it is bound by reflection from whatever corlib loaded; a runtime without it
// reports -1 (AllocMeasured false), as does one whose counter cannot see a probe allocation (Boehm Mono's); the report then
// says bytes are UNMEASURED and the alloc gate skips, rather than printing a confident zero.
using System;
using System.Reflection;

namespace RimMandrake.FlowWorks.Replay
{
    internal static class Compat
    {
#if NET5_0_OR_GREATER
        public static readonly bool AllocMeasured = true;
        public static long AllocatedBytes() => GC.GetAllocatedBytesForCurrentThread();
        public static string Runtime => System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription;
#else
        private static readonly Func<long> alloc = Bind();
        public static readonly bool AllocMeasured = alloc != null;
        public static long AllocatedBytes() => alloc != null ? alloc() : -1;

        private static Func<long> Bind()
        {
            MethodInfo m = typeof(GC).GetMethod("GetAllocatedBytesForCurrentThread", BindingFlags.Public | BindingFlags.Static, null, Type.EmptyTypes, null);
            if (m == null) return null;
            var f = (Func<long>)Delegate.CreateDelegate(typeof(Func<long>), m);
            // sanity probe: the game's Boehm-GC Mono has the method but answers 0 for every allocation (measured
            // 2026-11-05: bytes 0 beside nonzero gen-0 collections), so a counter that cannot see a 64 KB array is blind
            long b0 = f();
            probe = new byte[65536];
            return f() - b0 >= 65536 ? f : null;
        }

        private static byte[] probe;

        public static string Runtime
        {
            get
            {
                Type mono = Type.GetType("Mono.Runtime");
                MethodInfo name = mono?.GetMethod("GetDisplayName", BindingFlags.NonPublic | BindingFlags.Static);
                return mono == null ? ".NET Framework " + Environment.Version : "Mono " + (name?.Invoke(null, null) ?? Environment.Version.ToString());
            }
        }
#endif
    }
}
