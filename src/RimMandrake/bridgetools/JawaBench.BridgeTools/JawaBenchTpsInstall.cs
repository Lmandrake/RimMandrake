// JawaBenchTpsInstall.cs - transactional patch installation for the TPS record (BRIDGE_TPS_REVIEW2_FIXES_1,
// MUST 16). ⛔ NO Verse/Unity/Harmony: compiled into the offline harness too; the caller passes the resolve,
// patch and rollback actions (Harmony.Patch / Harmony.UnpatchAll(our id)).

using System;
using System.Collections.Generic;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchTpsInstall
    {
        internal sealed class Target
        {
            internal readonly string Name;
            internal readonly bool Required;
            internal readonly Func<object> Resolve;
            internal Target(string name, bool required, Func<object> resolve) { Name = name; Required = required; Resolve = resolve; }
        }

        /// <summary>
        /// Resolve EVERY target first; a missing required target installs nothing ("failed"). Then patch them;
        /// any exception rolls back every patch this installer made ("failed"), so a half-installed recorder
        /// never runs. A missing optional target gives "partial", named in <paramref name="detail"/>; only
        /// all targets patched is "complete".
        /// </summary>
        internal static string Run(IList<Target> targets, Action<string, object> patch, Action rollback, out string detail)
        {
            var resolved = new List<KeyValuePair<Target, object>>();
            var notes = new List<string>();
            bool missingOptional = false;
            foreach (var t in targets)
            {
                object m = null;
                try { m = t.Resolve(); } catch (Exception e) { notes.Add(t.Name + ": resolve threw " + e.GetType().Name); }
                if (m == null)
                {
                    notes.Add(t.Name + ": missing");
                    if (t.Required) { detail = string.Join("; ", notes); return "failed"; }
                    missingOptional = true;
                    continue;
                }
                resolved.Add(new KeyValuePair<Target, object>(t, m));
            }
            foreach (var kv in resolved)
            {
                try { patch(kv.Key.Name, kv.Value); }
                catch (Exception e)
                {
                    notes.Add(kv.Key.Name + ": patch threw " + e.GetType().Name + ": " + e.Message + " (all rolled back)");
                    try { rollback(); } catch (Exception re) { notes.Add("rollback threw " + re.GetType().Name); }
                    detail = string.Join("; ", notes);
                    return "failed";
                }
                notes.Add(kv.Key.Name + ": ok");
            }
            detail = string.Join("; ", notes);
            return missingOptional ? "partial" : "complete";
        }
    }
}
