// JawaBenchModSettingsFieldsBatchTools.cs - jawa/mod_settings_fields, the many-fields form of jawa/mod_settings_field
// (speed_20261112 step 2a, design/RimMandrake/live_test_speed_assessment_2026-11-12.md).
//
// WHY: a bridge call costs about 66 ms of round trip whatever it does (measured 2026-11-12: 10,530 single-field calls
// were 4.9% of a night). The commonest pattern is validation_core.probe_of's mailbox: get serial, set request, poll
// serial, get result = four calls per probe. With this tool a probe is two: (reads serial + sets request) and
// (reads serial + result). GSS proof_all made 1,600 such reads.
//
// ORDER IS THE CONTRACT: every field in `fields` is read FIRST, then the one optional set is applied. A probe's "serial
// before the request" must be read before the request is written, in the same main-thread pass, so no frame can service
// the request in between. A read that fails stops the set (the old four-call probe refused to post on an unreadable
// serial; this keeps that refusal).
//
// Same type resolution (ResolveLiveType: the copy the game's own code runs), same static-then-instance lookup and the
// same value coercion as jawa/mod_settings_field; that tool is unchanged.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        /// <summary>The public field `name` (static first, then instance) on settingsType and the object to read it on
        /// (null for static). Returns an error string, or null when found. `instance` is looked up once per call.</summary>
        private static string ResolveSettingsField(Type settingsType, string name, ref object instance, ref bool instanceLooked,
            out FieldInfo fi, out object target, out string kind)
        {
            target = null;
            kind = "static";
            fi = settingsType.GetField(name, BindingFlags.Public | BindingFlags.Static);
            if (fi != null)
            {
                return null;
            }
            fi = settingsType.GetField(name, BindingFlags.Public | BindingFlags.Instance);
            if (fi == null)
            {
                return "no public field '" + name + "' (static or instance)";
            }
            kind = "instance";
            if (!instanceLooked)
            {
                instance = FindModSettingsInstance(settingsType);
                instanceLooked = true;
            }
            if (instance == null)
            {
                return "'" + name + "' is an INSTANCE field but no loaded Mod's GetSettings<T>() could be located";
            }
            target = instance;
            return null;
        }

        [Tool(
            "jawa/mod_settings_fields",
            Description = "Read MANY public fields (static or instance) of one ModSettings-derived class, and optionally " +
                "write ONE, in a single call and a single main-thread pass - the batched form of mod_settings_field " +
                "(same type resolution, lookup and coercion). The reads happen FIRST, then the set, so a mailbox probe can " +
                "read its serial and post its request atomically. A field that cannot be read is listed in 'missing', makes " +
                "success false and stops the set (NOT applied); the other values are still returned.",
            ResultDescription = "success, typeName, values {field: string value}, kinds {field: static|instance}, " +
                "missing {field: why}, set {field, fieldKind, valueBefore, valueAfter} when a set was asked, typeIdentity, ticksGame.")]
        public static async Task<object> ModSettingsFields(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Type.FullName of the settings class, exact (as mod_settings_field).")]
            string typeName,
            [ToolParameter(Description = "Field names to read, separated by ',' (whitespace ignored). May be empty when only setting.",
                DefaultValue = "")]
            string fields = "",
            [ToolParameter(Description = "Optional: one field to write AFTER the reads.", DefaultValue = null)]
            string setField = null,
            [ToolParameter(Description = "The value for setField as a string, coerced to the field's type (as mod_settings_field).",
                DefaultValue = null)]
            string setValue = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                Type settingsType = ResolveLiveType(typeName, out string resolvedVia, out int copies);
                var typeIdentity = new { resolvedVia, copiesInAppDomain = copies, assembly = settingsType?.Assembly.GetName().Name };
                if (settingsType == null)
                {
                    return Fail("No loaded type '" + typeName + "' found - mod not active, or the name is wrong (pass Type.FullName exactly).");
                }
                List<string> names = (fields ?? "").Split(',').Select(s => s.Trim()).Where(s => s.Length > 0).ToList();
                bool wantSet = !string.IsNullOrWhiteSpace(setField);
                if (names.Count == 0 && !wantSet)
                {
                    return Fail("Give 'fields' (comma-separated) and/or 'setField'.");
                }
                if (wantSet && setValue == null)
                {
                    return Fail("Give 'setValue' with 'setField'.");
                }

                object instance = null;
                bool instanceLooked = false;
                var values = new Dictionary<string, string>();
                var kinds = new Dictionary<string, string>();
                var missing = new Dictionary<string, string>();
                foreach (string name in names)
                {
                    string err = ResolveSettingsField(settingsType, name, ref instance, ref instanceLooked, out FieldInfo fi, out object target, out string kind);
                    if (err != null)
                    {
                        missing[name] = err;
                        continue;
                    }
                    values[fi.Name] = SafeFieldToString(fi.GetValue(target));
                    kinds[fi.Name] = kind;
                }

                object setResult = null;
                string setError = null;
                if (wantSet && missing.Count > 0)
                {
                    // the reads gate the set: a probe whose serial could not be read must not post its request
                    setError = "set " + setField + " NOT applied: a read failed first";
                }
                else if (wantSet)
                {
                    string err = ResolveSettingsField(settingsType, setField.Trim(), ref instance, ref instanceLooked, out FieldInfo fi, out object target, out string kind);
                    if (err != null)
                    {
                        setError = err;
                    }
                    else
                    {
                        try
                        {
                            object coerced = CoerceSettingsValue(setValue, fi.FieldType);
                            string before = SafeFieldToString(fi.GetValue(target));
                            fi.SetValue(target, coerced);
                            setResult = new { field = fi.Name, fieldKind = kind, valueBefore = before, valueAfter = SafeFieldToString(fi.GetValue(target)) };
                        }
                        catch (Exception e)
                        {
                            setError = "set " + setField + " failed: " + e.GetType().Name + ": " + e.Message;
                        }
                    }
                }

                bool ok = missing.Count == 0 && setError == null;
                return (object)new
                {
                    success = ok,
                    error = ok ? null : (setError ?? ("could not read: " + string.Join(", ", missing.Keys.ToArray()))),
                    typeName,
                    values,
                    kinds,
                    missing,
                    set = setResult,
                    typeIdentity,
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }
    }
}
