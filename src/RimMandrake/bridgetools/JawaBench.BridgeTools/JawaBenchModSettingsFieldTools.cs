// JawaBenchModSettingsFieldTools.cs - BRIDGE_STATIC_SETTINGS_FIELDS_1.
//
// rimworld/update_mod_settings (RimBridgeServer's own base tool, not ours -
// its source is not vendored with an editable Core project in this repo,
// only Tests/Tools/docs) resolves INSTANCE fields on a ModSettings object
// and refuses `public static` ones ("Could not resolve field ...") -
// MEASURED live 2026-09-12 on Pits (MOD_VALIDATION_PIT_PILOT_1). The
// 2026-09-13 modcheck retrofit wave found the static pattern is OUR HOUSE
// STYLE, not a one-off: PitsSettings, RM_NinefoldSettings,
// RM_InhabitedSettings, PropertySettings, AntiquitiesSettings,
// RM_AftermathSettings, RM_PyrelandsSettings, ShipMemorySettings,
// RM_GraffitiMod, StructureInjections' settings all declare static fields.
// No toggle-flip validation.py component can write any of them through the
// third-party tool.
//
// This is a NEW tool, not a patch to update_mod_settings (that source isn't
// ours to edit) - generalises jawa/debug_settings (DebugSettings-only,
// static-bool-only, JawaBenchDebugGems1.cs) to ANY type, ANY of
// bool/int/float/double/string/enum, and BOTH static and instance fields
// (static tried first since that's every currently-known real target;
// instance falls back to Mod.GetSettings<T>() on the first loaded Mod
// handle whose own assembly matches the settings type's assembly, since
// GetSettings<T>() logs an error and returns null if called against a mod
// that already cached a DIFFERENT settings type - an assembly match avoids
// that log spam rather than trying every mod handle blind).
//
// THREAD AFFINITY: reflection over live static/instance state - main
// thread only, same rule as every other file here.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private static Type ResolveSettingsType(string typeName) =>
            AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(a => { try { return a.GetTypes(); } catch { return Array.Empty<Type>(); } })
                .FirstOrDefault(t => t.FullName == typeName);

        private static object FindModSettingsInstance(Type settingsType)
        {
            MethodInfo getSettingsOpen = typeof(Mod).GetMethod("GetSettings", BindingFlags.Public | BindingFlags.Instance);
            if (getSettingsOpen == null)
            {
                return null;
            }
            MethodInfo getSettings = getSettingsOpen.MakeGenericMethod(settingsType);
            foreach (Mod mod in LoadedModManager.ModHandles)
            {
                if (mod.GetType().Assembly != settingsType.Assembly)
                {
                    continue;
                }
                try
                {
                    object result = getSettings.Invoke(mod, null);
                    if (result != null)
                    {
                        return result;
                    }
                }
                catch
                {
                    // This mod handle already cached a different settings type
                    // (Mod.GetSettings<T>() logs and returns null in that case) -
                    // try the next assembly-matched handle rather than surface
                    // a misleading error for a mod we were only guessing at.
                }
            }
            return null;
        }

        private static object CoerceSettingsValue(string raw, Type fieldType)
        {
            if (fieldType == typeof(bool)) return bool.Parse(raw);
            if (fieldType == typeof(int)) return int.Parse(raw, CultureInfo.InvariantCulture);
            if (fieldType == typeof(float)) return float.Parse(raw, CultureInfo.InvariantCulture);
            if (fieldType == typeof(double)) return double.Parse(raw, CultureInfo.InvariantCulture);
            if (fieldType == typeof(string)) return raw;
            if (fieldType.IsEnum) return Enum.Parse(fieldType, raw, ignoreCase: true);
            throw new NotSupportedException("field type " + fieldType.FullName + " not supported (bool/int/float/double/string/enum only)");
        }

        private static string SafeFieldToString(object v) => v?.ToString();

        [Tool(
            "jawa/mod_settings_field",
            Description = "Read or write ANY public field (static OR instance) on a mod's " +
                "ModSettings-derived class by TYPE NAME and field name. BRIDGE_STATIC_SETTINGS_" +
                "FIELDS_1: rimworld/update_mod_settings only resolves INSTANCE fields and " +
                "refuses public static ones - most of our own mods' settings classes declare " +
                "static fields, which that tool cannot touch at all. This tool tries the field " +
                "as STATIC first; if not found there, falls back to INSTANCE by locating a " +
                "loaded Mod (assembly-matched to the settings type) whose Mod.GetSettings<T>() " +
                "resolves it. Values are read/written as their string form and coerced to the " +
                "field's real type (bool/int/float/double/string/enum only - refuses other " +
                "types by name rather than guessing a conversion). action='list' (default, " +
                "typeName only) reports every public field's name/type/kind/current value so a " +
                "caller can discover names without reading source first.",
            ResultDescription = "list: success, fields[] (name, type, kind, value). " +
                "get: success, field, fieldKind, value. " +
                "set: success, field, fieldKind, valueBefore, valueAfter.")]
        public static async Task<object> ModSettingsField(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Type.FullName of the settings class, e.g. 'Pits.PitsSettings' - exact, not guessed; use action='list' on a near-miss to see what's actually loaded, or jawa/get_defs-adjacent source reading to confirm the real namespace.")]
            string typeName,
            [ToolParameter(Description = "'list' (default), 'get', or 'set'.")]
            string action = "list",
            [ToolParameter(Description = "get/set: the field name.")]
            string field = null,
            [ToolParameter(Description = "set: the value as a string, coerced to the field's real type ('true'/'false' for bool, parsed for numeric, verbatim for string, name for enum).")]
            string value = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                Type settingsType = ResolveSettingsType(typeName);
                if (settingsType == null)
                {
                    return Fail("No loaded type '" + typeName + "' found - mod not active, or the name is wrong (pass Type.FullName exactly).");
                }

                string a = (action ?? "list").Trim().ToLowerInvariant();

                if (a == "list")
                {
                    object instance = FindModSettingsInstance(settingsType);
                    var rows = new List<object>();
                    foreach (FieldInfo staticField in settingsType.GetFields(BindingFlags.Public | BindingFlags.Static))
                    {
                        rows.Add(new { name = staticField.Name, type = staticField.FieldType.Name, kind = "static", value = SafeFieldToString(staticField.GetValue(null)) });
                    }
                    foreach (FieldInfo instanceField in settingsType.GetFields(BindingFlags.Public | BindingFlags.Instance))
                    {
                        rows.Add(new
                        {
                            name = instanceField.Name,
                            type = instanceField.FieldType.Name,
                            kind = "instance",
                            value = instance != null ? SafeFieldToString(instanceField.GetValue(instance)) : null,
                            instanceFound = instance != null,
                        });
                    }
                    return (object)new { success = true, action = "list", typeName, count = rows.Count, fields = rows, ticksGame = TicksGameSafe() };
                }

                if (string.IsNullOrWhiteSpace(field))
                {
                    return Fail("Give 'field' for action='" + a + "'.");
                }

                FieldInfo fiStatic = settingsType.GetField(field, BindingFlags.Public | BindingFlags.Static);
                FieldInfo fiInstance = fiStatic == null ? settingsType.GetField(field, BindingFlags.Public | BindingFlags.Instance) : null;
                if (fiStatic == null && fiInstance == null)
                {
                    return Fail("No public field '" + field + "' (static or instance) on " + typeName + ".",
                        new
                        {
                            staticFields = settingsType.GetFields(BindingFlags.Public | BindingFlags.Static).Select(f => f.Name).OrderBy(n => n).ToList(),
                            instanceFields = settingsType.GetFields(BindingFlags.Public | BindingFlags.Instance).Select(f => f.Name).OrderBy(n => n).ToList(),
                        });
                }

                FieldInfo fi = fiStatic ?? fiInstance;
                string kind = fiStatic != null ? "static" : "instance";
                object target = null;
                if (kind == "instance")
                {
                    target = FindModSettingsInstance(settingsType);
                    if (target == null)
                    {
                        return Fail("'" + field + "' is an INSTANCE field but no loaded Mod's GetSettings<" + typeName + ">() could be located (assembly-matched mod search found none).");
                    }
                }

                if (a == "get")
                {
                    return (object)new { success = true, action = "get", field = fi.Name, fieldKind = kind, value = SafeFieldToString(fi.GetValue(target)), ticksGame = TicksGameSafe() };
                }

                if (a == "set")
                {
                    if (value == null)
                    {
                        return Fail("Give 'value' for action='set'.");
                    }
                    object coerced;
                    try
                    {
                        coerced = CoerceSettingsValue(value, fi.FieldType);
                    }
                    catch (Exception e)
                    {
                        return Fail("Could not coerce '" + value + "' to " + fi.FieldType.Name + ": " + e.Message);
                    }
                    string before = SafeFieldToString(fi.GetValue(target));
                    try
                    {
                        fi.SetValue(target, coerced);
                    }
                    catch (Exception e)
                    {
                        return Fail("SetValue threw " + e.GetType().Name + ": " + e.Message);
                    }
                    return (object)new
                    {
                        success = true,
                        action = "set",
                        field = fi.Name,
                        fieldKind = kind,
                        valueBefore = before,
                        valueAfter = SafeFieldToString(fi.GetValue(target)),
                        ticksGame = TicksGameSafe(),
                    };
                }

                return Fail("action must be 'list', 'get' or 'set'.");
            }).ConfigureAwait(false);
        }
    }
}
