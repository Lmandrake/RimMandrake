// JawaBenchDefExtensionTools.cs - jawa/def_mod_extension: list, add or remove a DefModExtension on a named def at runtime,
// recorded in the deviation record so the scene session puts the def back when it is released (the same record as a
// settings write; JawaBenchDeviations). Built for RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES: a Python scene
// must give a weapon or projectile ThingDef its own tuning extension to read which def a mod's hook reads. Generic: any
// def type, any DefModExtension subclass with a parameterless constructor, scalar fields only.
//
// API read from 1.6 source (rimsage): Verse.Def.modExtensions is a public List<DefModExtension> (may be null);
// Def.GetModExtension<T>() returns the FIRST entry of type T, so add inserts at index 0 and the scene's extension wins over
// any of the same type that XML gave the def. The tool never mutates a list in place: each add or remove writes a NEW list,
// so the record's before value is the untouched original reference and the put-back restores it exactly.
#if JAWA_GM_TOOLS
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using D = JawaBench.BridgeTools.JawaBenchDeviationCore;
using S = JawaBench.BridgeTools.JawaBenchSafetyCore;

namespace JawaBench.BridgeTools
{
    /// <summary>A def's extension list as the deviation record sees it: its ToString names each extension and its scalar
    /// fields, so the overlay stamp and the record's rows say what the def carries.</summary>
    internal sealed class JawaBenchExtensionList : List<DefModExtension>
    {
        internal JawaBenchExtensionList(IEnumerable<DefModExtension> items) : base(items ?? Enumerable.Empty<DefModExtension>()) { }

        public override string ToString() => "[" + string.Join("; ", this.Select(JawaBenchTerrainTools.DescribeExtension)) + "]";
    }

    public sealed partial class JawaBenchTerrainTools
    {
        internal static string DescribeExtension(DefModExtension e)
        {
            if (e == null) return "null";
            var parts = e.GetType().GetFields(BindingFlags.Public | BindingFlags.Instance)
                .Where(f => IsScalarField(f.FieldType))
                .Select(f => f.Name + "=" + Convert.ToString(f.GetValue(e), CultureInfo.InvariantCulture));
            return e.GetType().FullName + "{" + string.Join(",", parts) + "}";
        }

        private static bool IsScalarField(Type t) =>
            t == typeof(bool) || t == typeof(int) || t == typeof(float) || t == typeof(double) || t == typeof(string) || t.IsEnum;

        private static object ExtensionRow(DefModExtension e)
        {
            var fields = new Dictionary<string, object>();
            foreach (var f in e.GetType().GetFields(BindingFlags.Public | BindingFlags.Instance).Where(f => IsScalarField(f.FieldType)))
                fields[f.Name] = Convert.ToString(f.GetValue(e), CultureInfo.InvariantCulture);
            return new { type = e.GetType().FullName, fields };
        }

        private static Type ResolveDefType(string defType)
        {
            string n = defType.Trim();
            foreach (var cand in new[] { n, "Verse." + n, "RimWorld." + n })
            {
                Type t = GenTypes.GetTypeInAnyAssembly(cand);
                if (t != null && typeof(Def).IsAssignableFrom(t)) return t;
            }
            return null;
        }

        [Tool(
            "jawa/def_mod_extension",
            Description =
                "*** CHANGES A LIVE DEF *** List, add or remove a DefModExtension on one def (Def.modExtensions). action='list' " +
                "(default) reads every extension and its scalar fields. action='add' builds a new instance of typeName " +
                "(Type.FullName, a DefModExtension subclass with a parameterless constructor), sets the scalar fields given in " +
                "'fields' (a JSON object, values coerced to each field's type: bool/int/float/double/string/enum), and puts it " +
                "FIRST in the list, so GetModExtension<T> returns it over any XML one. action='remove' takes out every extension " +
                "of exactly typeName. add and remove go into the deviation record: releasing the scene session (or " +
                "jawa/mod_settings_field action=revert) puts the def's original list back. REFUSES under the CAMPAIGN profile " +
                "and on a canonical save, an unknown def or type, a field that is not a public scalar instance field, and a " +
                "driverless write while a session is open.",
            ResultDescription = "success, action, defType, defName, extensionsBefore[] and extensionsAfter[] (type, fields), removed (remove).")]
        public static async Task<object> DefModExtension(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Def type name, e.g. ThingDef, DamageDef (Verse./RimWorld. tried). Required.")]
            string defType = null,
            [ToolParameter(Description = "The def's defName. Required.")]
            string defName = null,
            [ToolParameter(Description = "'list' (default), 'add' or 'remove'.")]
            string action = "list",
            [ToolParameter(Description = "add/remove: the extension's Type.FullName, e.g. RimMandrake.ExplosiveKnockback.RM_KnockbackExtension.")]
            string typeName = null,
            [ToolParameter(Description = "add: a JSON object of field -> value, e.g. {\"force\": 2.5, \"maxThrowCells\": 8}. Omitted = the type's defaults.")]
            string fields = null,
            [ToolParameter(Description = "Session driver for add or remove while a session is open.")]
            string driver = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string a = (action ?? "list").Trim().ToLowerInvariant();
                if (a != "list" && a != "add" && a != "remove") return Fail("action is 'list', 'add' or 'remove', not '" + action + "'.");
                if (string.IsNullOrWhiteSpace(defType) || string.IsNullOrWhiteSpace(defName)) return Fail("Give 'defType' and 'defName'.");
                Type dt = ResolveDefType(defType);
                if (dt == null) return Fail("No loaded Def type '" + defType + "'.");
                Def def = GenDefDatabase.GetDefSilentFail(dt, defName.Trim(), false);
                if (def == null) return Fail("No " + dt.Name + " '" + defName + "'.");
                var before = (def.modExtensions ?? new List<DefModExtension>()).Select(ExtensionRow).ToList();
                if (a == "list")
                    return (object)new { success = true, action = a, defType = dt.Name, defName = def.defName, extensionsBefore = before, ticksGame = TicksGameSafe() };

                string driverRefusal = JawaBenchHands.SettingsDriver(driver);
                if (driverRefusal != null) return Fail(driverRefusal);
                if (JawaBenchCompanionSafety.Effective(out string why, out _) != S.Test)
                    return Fail("REFUSED: def_mod_extension " + a + " is off under the CAMPAIGN profile (" + why + "); list stays available.");
                string canonical = JawaBenchDeviations.CanonicalRefusal();
                if (canonical != null) return Fail(canonical);
                if (string.IsNullOrWhiteSpace(typeName)) return Fail("Give 'typeName', the extension's Type.FullName.");
                Type et = GenTypes.GetTypeInAnyAssembly(typeName.Trim());
                if (et == null || !typeof(DefModExtension).IsAssignableFrom(et) || et.IsAbstract)
                    return Fail("'" + typeName + "' is not a loaded concrete DefModExtension type.");

                var list = new JawaBenchExtensionList(def.modExtensions);
                int removed = 0;
                if (a == "add")
                {
                    DefModExtension ext;
                    try { ext = (DefModExtension)Activator.CreateInstance(et); }
                    catch (Exception e) { return Fail("Could not construct " + et.FullName + ": " + e.Message); }
                    if (!string.IsNullOrWhiteSpace(fields))
                    {
                        object parsed;
                        try { parsed = C.ParseJson(fields); }
                        catch (Exception e) { return Fail("'fields' is not JSON: " + e.Message); }
                        if (!(parsed is Dictionary<string, object> map)) return Fail("'fields' must be a JSON object.");
                        foreach (var kv in map)
                        {
                            FieldInfo fi = et.GetField(kv.Key, BindingFlags.Public | BindingFlags.Instance);
                            if (fi == null || !IsScalarField(fi.FieldType))
                                return Fail("'" + kv.Key + "' is not a public scalar instance field of " + et.FullName + ".");
                            try
                            {
                                string raw = kv.Value is bool b ? (b ? "true" : "false") : Convert.ToString(kv.Value, CultureInfo.InvariantCulture);
                                fi.SetValue(ext, CoerceSettingsValue(raw, fi.FieldType));
                            }
                            catch (Exception e) { return Fail("Could not set " + kv.Key + "=" + kv.Value + ": " + e.Message); }
                        }
                    }
                    list.Insert(0, ext);
                }
                else
                {
                    removed = list.RemoveAll(e => e != null && e.GetType() == et);
                    if (removed == 0) return Fail(def.defName + " carries no " + et.FullName + ".", new { extensionsBefore = before });
                }

                var entry = new D.Entry("overlay", "PUT BACK", "process", dt.Name + "." + def.defName + ".modExtensions", null, list,
                    () => def.modExtensions, v => def.modExtensions = (List<DefModExtension>)v);
                string error = JawaBenchDeviations.ApplySettings(driver, null, entry);
                if (error != null) return Fail(error);
                return (object)new
                {
                    success = true, action = a, defType = dt.Name, defName = def.defName, removed,
                    extensionsBefore = before,
                    extensionsAfter = (def.modExtensions ?? new List<DefModExtension>()).Select(ExtensionRow).ToList(),
                    ticksGame = TicksGameSafe(),
                };
            }, cancellationToken);
        }
    }
}
#endif
