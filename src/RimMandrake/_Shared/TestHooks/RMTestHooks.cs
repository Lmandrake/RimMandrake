// RMTestHooks.cs - test hooks that a mod compiles in as its own internal copy: trace points, a reset hook and a digest hook
// (BRIDGE v2.0, decision 8 of design/specs/2026-11-23-bridge-v2/05_build_design.md; item
// RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION). Page: design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md.
//
// The JawaBench companion finds these by TYPE NAME through reflection (JawaBenchModHooksCore.cs). The mod names no type of the
// companion, and the companion names no type of the mod. This file names no Verse, Unity or Harmony type, so it compiles into a
// net472 mod and into the offline harness alike. It is compiled into the RELEASE build too: in play the cost of one Emit is one
// field read and one branch.
//
// Use, in a mod's csproj:
//     <Compile Include="..\..\_Shared\TestHooks\RMTestHooks.cs" Link="Shared\RMTestHooks.cs" />
// In the mod:
//     RMTrace.Emit("refused_no_cell");                       // a branch the mod took, for a scene to read
//     RMTrace.Emit("planned", "cells", plan.Count);
//     [RMReset]  public static string Reset(string scope)  { cache.Clear(); return "cache " + n; }   // what it cleared
//     [RMDigest] public static string Digest(string scope) { return cache.Count + ":" + pending.Count; }
// Both hooks are public static, take one string (the scope, "" = all) and answer a string. A Digest answers a digest of the
// same state that Reset clears; the companion accepts a Digest only after it was seen to differ between a clean state and a
// state dirtied on purpose.
using System;
using System.Globalization;

namespace RimMandrake.Shared.TestHooks
{
    /// <summary>Which build this copy was compiled into. A hook of a PROOF build is never evidence for an acceptance run.</summary>
    internal static class RMTestHooksBuild
    {
#if RM_PROOFS
        public const string Kind = "PROOF";
#else
        public const string Kind = "RELEASE";
#endif
        /// <summary>The version of this file's contract with the companion.</summary>
        public const int Contract = 1;
    }

    /// <summary>Trace points. `Sink` is null in play; the companion sets it at the arm of a scene run and clears it at the end.</summary>
    internal static class RMTrace
    {
        /// <summary>(name, key, value). Set and cleared by the companion only.</summary>
        public static Action<string, string, string> Sink;

        public static void Emit(string name)
        {
            var s = Sink;
            if (s != null) s(name, null, null);
        }

        public static void Emit(string name, string key, string value)
        {
            var s = Sink;
            if (s != null) s(name, key, value);
        }

        public static void Emit(string name, string key, long value)
        {
            var s = Sink;
            if (s != null) s(name, key, value.ToString(CultureInfo.InvariantCulture));
        }

        public static void Emit(string name, string key, double value)
        {
            var s = Sink;
            if (s != null) s(name, key, value.ToString("R", CultureInfo.InvariantCulture));
        }

        public static void Emit(string name, string key, bool value)
        {
            var s = Sink;
            if (s != null) s(name, key, value ? "true" : "false");
        }
    }

    /// <summary>Marks `public static string Reset(string scope)`: clears the mod's per-scene state and answers what it cleared.</summary>
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = false, Inherited = false)]
    internal sealed class RMResetAttribute : Attribute { }

    /// <summary>Marks `public static string Digest(string scope)`: a digest of the state that the Reset hook clears.</summary>
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = false, Inherited = false)]
    internal sealed class RMDigestAttribute : Attribute { }
}
