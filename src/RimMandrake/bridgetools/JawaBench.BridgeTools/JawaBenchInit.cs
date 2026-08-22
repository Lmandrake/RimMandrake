// JawaBenchInit.cs - the one line that says the companion is here.
//
// WHY THIS FILE EXISTS  (JAWABENCH_HAS_NO_INIT_LINE_1)
// ===================================================
// Measured 2026-08-22 against the 08:40 Player.log: ZERO lines matching
// "JawaBench". Every Log call in the assembly sat inside a catch, so the
// companion was silent when it worked AND silent when it was absent - and those
// are the two states a deploy most needs to tell apart. RimBridge itself
// announces ("[RimBridge] Applied 56 optional Harmony patch classes."); its
// companion did not.
//
// ⭐ WHAT IT BUYS. Proving "112 -> 115 tools after a deploy" used to require
// bringing the bridge up and asking it - a game, a load, and CHECK holding the
// bridge - to answer a question one log line answers for free before anyone
// connects. A companion that silently failed to load is also the single most
// likely failure after a deploy.
//
// 🔑 WHY A MODULE INITIALIZER AND NOT A STATIC CONSTRUCTOR. A static ctor on the
// tools class fires on the first tool INVOCATION, which is far too late: by then
// something has already connected and asked, which is exactly the expensive route
// this replaces. A module initializer runs when the ASSEMBLY IS LOADED, which is
// the event we actually want to witness.
// ⚠️ net472 has no ModuleInitializerAttribute in its reference assemblies, so it
// is declared below. Roslyn honours a user-defined one as long as the full name
// matches exactly; the csproj already sets LangVersion=latest, which is what
// makes C# 9's module initializers available at all.
//
// ⛔ EVERYTHING HERE IS INSIDE A try/catch THAT SWALLOWS. A companion that throws
// while announcing itself would be a worse failure than the silence it replaces.

using System;
using System.Linq;
using System.Reflection;
using RimBridgeServer.Sdk;
using Verse;

namespace System.Runtime.CompilerServices
{
    /// <summary>
    /// Present only because net472's reference assemblies do not ship it. Roslyn
    /// matches this attribute BY FULL NAME, so it must stay in this namespace with
    /// this exact name. ⛔ Do not "tidy" it into the JawaBench namespace.
    /// </summary>
    [AttributeUsage(AttributeTargets.Method, Inherited = false)]
    internal sealed class ModuleInitializerAttribute : Attribute
    {
    }
}

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchInit
    {
        [System.Runtime.CompilerServices.ModuleInitializer]
        internal static void Announce()
        {
            try
            {
                Assembly self = typeof(JawaBenchInit).Assembly;

                // The tool COUNT is derived by the same rule RimBridgeServer uses to
                // find them - a [Tool] attribute on a public static method - so the
                // number in the log is the number the bridge will register, not a
                // constant somebody has to remember to bump.
                // ⚠️ GetTypes() throws ReflectionTypeLoadException if ANY type in the
                // assembly fails to load, and that exception carries the types that DID
                // load. Catching it here rather than letting the outer catch swallow the
                // whole line matters: a partial load is precisely the case where somebody
                // most needs to see a line at all, even one that says the count is unknown.
                int tools;
                try
                {
                    tools = CountTools(self.GetTypes());
                }
                catch (ReflectionTypeLoadException rtle)
                {
                    tools = CountTools(rtle.Types.Where(t => t != null).ToArray());
                    Log.Warning("[JawaBench] some types failed to load; the tool count below " +
                                "counts only the ones that did.");
                }

                // build.py reads provenance out of AssemblyInformationalVersion, which
                // the SDK stamps as "<version>+<40-hex-sha>". Reporting the same 12
                // characters means a log line and a deploy plan can be compared by eye.
                string build = "unknown";
                var attr = self.GetCustomAttribute<AssemblyInformationalVersionAttribute>();
                if (attr != null && !string.IsNullOrEmpty(attr.InformationalVersion))
                {
                    string v = attr.InformationalVersion;
                    int plus = v.IndexOf('+');
                    build = (plus >= 0 && v.Length > plus + 1) ? v.Substring(plus + 1) : v;
                    if (build.Length > 12) build = build.Substring(0, 12);
                }

                Log.Message("[JawaBench] ready: " + tools + " tools, build " + build);
            }
            catch (Exception e)
            {
                try { Log.Warning("[JawaBench] init line failed (harmless): " + e.Message); }
                catch { }
            }
        }

        private static int CountTools(Type[] types)
        {
            return types
                .SelectMany(t => t.GetMethods(BindingFlags.Public | BindingFlags.Static |
                                              BindingFlags.NonPublic | BindingFlags.Instance))
                .Count(m => m.GetCustomAttributes(typeof(ToolAttribute), inherit: false).Length > 0);
        }
    }
}
