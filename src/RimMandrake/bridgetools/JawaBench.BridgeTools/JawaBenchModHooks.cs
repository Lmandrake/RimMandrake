// JawaBenchModHooks.cs - the Verse half of the mods' test hooks: jawa/mod_hooks (TEST profile only), and the registry that each
// scene run arms and clears (JawaBenchSceneTick.Refuse sets JawaBenchSceneTickCore.Watch before the first run).
// Item RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION. Page: design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md.
// The rules are JawaBenchModHooksCore.cs; the mod side is src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs. No Harmony patch.
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using MH = JawaBench.BridgeTools.JawaBenchModHooksCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchModHooks
    {
        /// <summary>Found once, on first use: assemblies do not change after the game has loaded.</summary>
        internal static readonly MH.Registry Registry = new MH.Registry(() => AppDomain.CurrentDomain.GetAssemblies());

        /// <summary>list | admit | digest | prove | reset. Main thread only.</summary>
        public static Dictionary<string, object> Act(string action, string mod, string scope, string purpose, string step)
        {
            var r = Registry;
            switch ((action ?? "").Trim().ToLowerInvariant())
            {
                case "list":
                    return new Dictionary<string, object>
                    {
                        { "success", true }, { "mods", r.Rows() }, { "armed", r.Armed }, { "said", r.Said }, { "late", r.Late }, { "staleAtArm", r.StaleAtArm },
                    };
                case "admit":
                {
                    var no = r.Admit(purpose);
                    return new Dictionary<string, object> { { "success", true }, { "purpose", purpose }, { "admitted", no.Count == 0 }, { "refusals", no } };
                }
                case "digest":
                {
                    var rows = new List<object>();
                    foreach (var m in r.Mods)
                    {
                        if (!string.IsNullOrEmpty(mod) && !string.Equals(m.Name, mod.Trim(), StringComparison.OrdinalIgnoreCase)) continue;
                        if (m.Digest == null) { rows.Add(new Dictionary<string, object> { { "mod", m.Name }, { "digest", null }, { "why", "no digest hook" } }); continue; }
                        object d; string why = null;
                        try { d = m.Digest.Invoke(null, new object[] { scope ?? "" }); }
                        catch (Exception e) { d = null; var x = e.InnerException ?? e; why = "the hook threw " + x.GetType().Name + ": " + x.Message; }
                        rows.Add(new Dictionary<string, object> { { "mod", m.Name }, { "digest", d }, { "proven", m.Proven }, { "why", why } });
                    }
                    return new Dictionary<string, object> { { "success", true }, { "digests", rows } };
                }
                case "prove": return r.Prove(mod, step, scope);
                case "reset": return r.Reset(mod, scope);
            }
            return new Dictionary<string, object>
            {
                { "success", false }, { "refused", "BAD_ARGS" }, { "message", "action is list, admit, digest, prove or reset, not '" + action + "'" }, { "repair", "correct it" },
            };
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/mod_hooks",
            Description =
                "The test hooks that our mods compile in (src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs), found by reflection " +
                "(design/specs/2026-11-23-bridge-v2-mod-hooks/boundary.md). action=list: each RimMandrake assembly, its build (PROOF | RELEASE | " +
                "none), its trace point, its reset and digest hooks, the digest's proof and each problem by name. action=admit purpose=acceptance: " +
                "refuses each hook of a PROOF build. action=digest: each mod's digest now. action=prove step=clean, then dirty the mod's state on " +
                "purpose, then step=dirty: the digest is accepted only when the two differ. action=reset: calls the mod's reset hook and compares " +
                "its digest with the clean read (verified | differs | unproven). A scene run arms every trace point at its start and clears it at " +
                "its end: each RMTrace.Emit is a `mod` record of the run's trace. TEST profile only.",
            ResultDescription =
                "list: success, mods[] (mod, build, trace, reset, digest, digestProven, digestProof, problems[]), armed, said, late, staleAtArm. " +
                "admit: admitted, refusals[]. digest: digests[] (mod, digest, proven, why). prove and reset: the mod's row, clean, dirty, and for reset " +
                "cleared, digestAfter, reset. A refusal: success false, refused (name), message, repair.")]
        public static async Task<object> ModHooks(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "list, admit, digest, prove or reset.")] string action = "list",
            [ToolParameter(Description = "digest, prove, reset: the mod's assembly name, as action=list says it (digest: empty = every mod).")] string mod = "",
            [ToolParameter(Description = "digest, prove, reset: the scope given to the mod's hook; empty = all of its state.")] string scope = "",
            [ToolParameter(Description = "admit: acceptance or explore.")] string purpose = "explore",
            [ToolParameter(Description = "prove: clean or dirty.")] string step = "")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                return JawaBenchModHooks.Act(action, mod, scope, purpose, step);
            }, cancellationToken);
        }
    }
}
