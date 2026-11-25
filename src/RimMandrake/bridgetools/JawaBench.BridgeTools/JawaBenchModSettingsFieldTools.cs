// JawaBenchModSettingsFieldTools.cs - BRIDGE_STATIC_SETTINGS_FIELDS_1.
//
// rimworld/update_mod_settings (RimBridgeServer's own base tool, not ours -
// its source is not vendored with an editable Core project in this repo,
// only Tests/Tools/docs) resolves INSTANCE fields on a ModSettings object
// and refuses `public static` ones ("Could not resolve field ...") -
// MEASURED live 2026-09-12 on Pits (MOD_VALIDATION_PIT_PILOT_1). The
// 2026-09-13 modcheck retrofit wave found the static pattern is OUR HOUSE
// STYLE, not a one-off: RimMandrakeFlowWorksSettings, RM_NinefoldSettings,
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
using D = JawaBench.BridgeTools.JawaBenchDeviationCore;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // Measured 2026-10-04: the full scan of every type in every loaded assembly cost ~0.7 s per call on the 638-mod
        // list, and the MessyConduit matrix made 3,169 of them (88% of a 2,640 s run). A loaded type never unloads, so a
        // hit is cached; a miss is NOT cached (the mod may load later).
        //
        // 🔴 RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD A3 (2026-10-20): the type MUST be the copy the game's own code runs. On a list
        // with Prepatcher (zetrith.prepatcher; VEF, BigAndSmall, yayoAni, CombatAI carry [PrepatcherField]s) every modified
        // assembly AND every assembly that references one is loaded a SECOND time ("Prepatcher: Setting refonly / Loading
        // patched assemblies", Reloader.PropagateNeedsReload). The pre-patch originals stay in the AppDomain, earlier in
        // GetAssemblies() order, so the old "first FullName match in the AppDomain" bound a DEAD copy of
        // RimMandrake.Cauldron.RM_CauldronSettings: `set rhossakBindEnabled=False` read back False while the live comp kept
        // reading its own True and the pane kept saying "Bound to twisting thornwood" (two runs, same verdict).
        // GenTypes.GetTypeInAnyAssembly walks LoadedModManager.RunningMods' loadedAssemblies — the resolver the def loader
        // used for every comp class — so a static written through it is the static the comp reads. The AppDomain scan is
        // only a fallback (a type outside every running mod) and skips ReflectionOnly assemblies.
        private static readonly Dictionary<string, Type> SettingsTypeCache = new Dictionary<string, Type>();

        internal static Type ResolveLiveType(string typeName, out string resolvedVia, out int copiesInAppDomain)
        {
            copiesInAppDomain = 0;
            foreach (Assembly a in AppDomain.CurrentDomain.GetAssemblies())
            {
                try { if (a.GetType(typeName, false) != null) copiesInAppDomain++; }
                catch { /* an assembly that cannot answer is not a copy we could bind anyway */ }
            }
            lock (SettingsTypeCache)
            {
                if (SettingsTypeCache.TryGetValue(typeName, out Type cached)) { resolvedVia = "GenTypes(cached)"; return cached; }
            }
            Type live = null;
            try { live = GenTypes.GetTypeInAnyAssembly(typeName); } catch { live = null; }
            if (live != null)
            {
                lock (SettingsTypeCache) SettingsTypeCache[typeName] = live;
                resolvedVia = "GenTypes";
                return live;
            }
            resolvedVia = "AppDomain";
            return AppDomain.CurrentDomain.GetAssemblies()
                .Where(a => { try { return !a.ReflectionOnly; } catch { return false; } })
                .Select(a => { try { return a.GetType(typeName, false); } catch { return null; } })
                .LastOrDefault(t => t != null);   // last: a reloaded copy is loaded after the original it replaces
        }

        private static Type ResolveSettingsType(string typeName)
        {
            return ResolveLiveType(typeName, out _, out _);
        }

        private static object FindModSettingsInstance(Type settingsType)
        {
            MethodInfo getSettingsOpen = typeof(Mod).GetMethod("GetSettings", BindingFlags.Public | BindingFlags.Instance);
            if (getSettingsOpen == null)
            {
                return null;
            }
            // GetSettings<T> is constrained to ModSettings, new(): any other type made MakeGenericMethod throw, so list
            // and get on a non-settings type (which they promise to read) failed with "Invalid generic arguments".
            if (!typeof(ModSettings).IsAssignableFrom(settingsType) || settingsType.IsAbstract
                || settingsType.GetConstructor(Type.EmptyTypes) == null)
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

        private static string SettingsWriteRefusal(Type settingsType, string typeName, FieldInfo fi, string key, out object details)
        {
            details = null;
            string immutable = key == null ? JawaBenchDeviationCore.FieldRefusal(fi) : null;
            if (immutable != null) return immutable;
            Assembly asm = settingsType.Assembly;
            bool modAsm = LoadedModManager.RunningMods.Any(m => m.assemblies?.loadedAssemblies?.Contains(asm) == true)
                && asm.GetTypes().Any(t => typeof(ModSettings).IsAssignableFrom(t));
            if (!JawaBenchSafetyCore.SettingsTypeWritable(typeof(ModSettings).IsAssignableFrom(settingsType),
                    settingsType.IsAbstract && settingsType.IsSealed, modAsm, settingsType.FullName))
                return "REFUSED: '" + typeName + "' is neither a Verse.ModSettings class nor a static *Settings class of a running mod's assembly; set writes only a mod's settings (list and get still read any type).";
            string why, declared;
            if (JawaBenchCompanionSafety.Effective(out why, out declared) == JawaBenchSafetyCore.Test)
            {
                // The profile is cached. Check the loaded save again before journaling a write.
                why = JawaBenchDeviations.CanonicalRefusal();
                if (why == null) return null;
            }
            details = new { profile = JawaBenchSafetyCore.Campaign, profileWhy = why };
            return "REFUSED: set is off under the CAMPAIGN profile (" + why + "); change a campaign game's settings in the Mod Settings dialog. list and get stay available.";
        }

        private static object SettingsSetFailure(Type settingsType, string typeName, FieldInfo fi, string key, string value)
        {
            string no = SettingsWriteRefusal(settingsType, typeName, fi, key, out object details);
            if (no != null) return Fail(no, details);
            return value == null ? Fail("Give 'value' for action='set'.") : null;
        }

        private static Type SettingsDictionaryValueType(Type ft)
        {
            Type dictIface = ft.GetInterfaces().FirstOrDefault(i => i.IsGenericType && i.GetGenericTypeDefinition() == typeof(IDictionary<,>));
            Type[] kv = dictIface?.GetGenericArguments();
            return kv != null && kv[0] == typeof(string) ? kv[1] : null;
        }

        internal static D.Entry PrepareOverlaySetting(Dictionary<string, object> fields)
        {
            string Text(string key) => fields.TryGetValue(key, out object v) ? v as string : null;
            string typeName = Text("typeName"), field = Text("field"), value = Text("value"), key = Text("key");
            if (string.IsNullOrEmpty(typeName) || string.IsNullOrEmpty(field) || value == null ||
                fields.Keys.Any(k => k != "typeName" && k != "field" && k != "value" && k != "key") ||
                (fields.ContainsKey("key") && key == null))
                throw new ArgumentException("each entry takes string typeName, field, value and optional key");
            Type type = ResolveSettingsType(typeName);
            if (type == null) throw new ArgumentException("No loaded type '" + typeName + "' found");
            object instance = null;
            bool looked = false;
            string error = ResolveSettingsField(type, field, ref instance, ref looked, out FieldInfo fi, out object target, out _);
            if (error == null) error = SettingsWriteRefusal(type, typeName, fi, key, out _);
            if (error != null) throw new ArgumentException(error);
            Type valueType = key == null ? fi.FieldType : SettingsDictionaryValueType(fi.FieldType);
            if (valueType == null) throw new ArgumentException(field + " is not a dictionary with string keys");
            JawaBenchDeviations.ObserveDefault(type, fi, target);
            return JawaBenchDeviations.Setting(type, fi, target, key, CoerceSettingsValue(value, valueType));
        }

        private static object SettingsDeviations(string action, string driver)
        {
            if (action == "revert")
            {
                string error = JawaBenchDeviations.Revert(JawaBenchHands.SettingsSessionOpen ? driver : null);
                if (error != null) return Fail(error);
            }
            return new { success = true, deviation = JawaBenchDeviations.Record.Receipt() };
        }

        [Tool(
            "jawa/mod_settings_field",
            Description = "Read or write ANY public field (static OR instance) on a mod's " +
                "ModSettings-derived class by TYPE NAME and field name (set REFUSES a type that is neither ModSettings-derived " +
                "nor a static *Settings class of a running mod's assembly, and refuses under the CAMPAIGN profile; list/get read any type). BRIDGE_STATIC_SETTINGS_" +
                "FIELDS_1: rimworld/update_mod_settings only resolves INSTANCE fields and " +
                "refuses public static ones - most of our own mods' settings classes declare " +
                "static fields, which that tool cannot touch at all. This tool tries the field " +
                "as STATIC first; if not found there, falls back to INSTANCE by locating a " +
                "loaded Mod (assembly-matched to the settings type) whose Mod.GetSettings<T>() " +
                "resolves it. Values are read/written as their string form and coerced to the " +
                "field's real type (bool/int/float/double/string/enum only - refuses other " +
                "types by name rather than guessing a conversion). action='list' (default, " +
                "typeName only) reports every public field's name/type/kind/current value so a " +
                "caller can discover names without reading source first. key= addresses ONE entry of a field that is a " +
                "Dictionary with string keys (e.g. RM_BiomesSettings.enabled, key 'Pyrelands'): get reads that entry " +
                "(present=false when absent), set writes it, coerced to the dictionary's value type.",
            ResultDescription = "list: success, fields[] (name, type, kind, value). " +
                "get: success, field, fieldKind, value (with key: key, present). " +
                "set: success, field, fieldKind, valueBefore, valueAfter (with key: key, presentBefore). " +
                "deviations/revert: success, deviation (the process record).")]
        public static async Task<object> ModSettingsField(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Type.FullName of the settings class, e.g. 'RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings' - exact, not guessed; use action='list' on a near-miss to see what's actually loaded, or jawa/get_defs-adjacent source reading to confirm the real namespace.")]
            string typeName,
            [ToolParameter(Description = "'list' (default), 'get', 'set', 'deviations' or 'revert'.")]
            string action = "list",
            [ToolParameter(Description = "get/set: the field name.")]
            string field = null,
            [ToolParameter(Description = "set: the value as a string, coerced to the field's real type ('true'/'false' for bool, parsed for numeric, verbatim for string, name for enum).")]
            string value = null,
            [ToolParameter(Description = "get/set on a Dictionary<string,T> field: the entry's key (RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN: the Baroque Biomes roster toggle is RM_BiomesSettings.enabled[key]).", DefaultValue = null)]
            string key = null,
            [ToolParameter(Description = "Session driver for set or revert while a session is open.")] string driver = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                string a = (action ?? "list").Trim().ToLowerInvariant();
                string driverRefusal = a == "set" || a == "revert" ? JawaBenchHands.SettingsDriver(driver) : null;
                if (driverRefusal != null) return Fail(driverRefusal);
                if (a == "deviations" || a == "revert") return SettingsDeviations(a, driver);
                Type settingsType = ResolveLiveType(typeName, out string resolvedVia, out int copies);
                // Said out loud in every reply: copies > 1 means a stale twin exists, and resolvedVia must then be GenTypes.
                var typeIdentity = new { resolvedVia, copiesInAppDomain = copies, assembly = settingsType?.Assembly.GetName().Name };
                if (settingsType == null)
                {
                    return Fail("No loaded type '" + typeName + "' found - mod not active, or the name is wrong (pass Type.FullName exactly).");
                }

                if (a == "list")
                {
                    object instance = FindModSettingsInstance(settingsType);
                    var rows = new List<object>();
                    foreach (FieldInfo staticField in settingsType.GetFields(BindingFlags.Public | BindingFlags.Static))
                    {
                        JawaBenchDeviations.ObserveDefault(settingsType, staticField, null);
                        rows.Add(new { name = staticField.Name, type = staticField.FieldType.Name, kind = "static", value = SafeFieldToString(staticField.GetValue(null)) });
                    }
                    foreach (FieldInfo instanceField in settingsType.GetFields(BindingFlags.Public | BindingFlags.Instance))
                    {
                        if (instance != null) JawaBenchDeviations.ObserveDefault(settingsType, instanceField, instance);
                        rows.Add(new
                        {
                            name = instanceField.Name,
                            type = instanceField.FieldType.Name,
                            kind = "instance",
                            value = instance != null ? SafeFieldToString(instanceField.GetValue(instance)) : null,
                            instanceFound = instance != null,
                        });
                    }
                    return (object)new { success = true, action = "list", typeName, typeIdentity, count = rows.Count, fields = rows, ticksGame = TicksGameSafe() };
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

                JawaBenchDeviations.ObserveDefault(settingsType, fi, target);
                if (key != null && (a == "get" || a == "set"))
                {
                    Type valueType = SettingsDictionaryValueType(fi.FieldType);
                    if (valueType == null)
                        return Fail("'" + field + "' is a " + fi.FieldType.Name + ", not a dictionary with string keys: key= applies only to one.");
                    var dict = fi.GetValue(target) as System.Collections.IDictionary;
                    if (dict == null)
                    {
                        return Fail("'" + field + "' is null on " + typeName + ": no dictionary to address.");
                    }
                    bool presentBefore = dict.Contains(key);
                    string entryBefore = presentBefore ? SafeFieldToString(dict[key]) : null;
                    if (a == "get")
                    {
                        return (object)new { success = true, action = "get", field = fi.Name, fieldKind = kind, key, present = presentBefore, value = entryBefore, typeIdentity, ticksGame = TicksGameSafe() };
                    }
                    object no = SettingsSetFailure(settingsType, typeName, fi, key, value);
                    if (no != null) return no;
                    object coercedK;
                    try
                    {
                        coercedK = CoerceSettingsValue(value, valueType);
                    }
                    catch (Exception e)
                    {
                        return Fail("Could not coerce '" + value + "' to " + valueType.Name + ": " + e.Message);
                    }
                    string error = JawaBenchDeviations.ApplySettings(driver, null, JawaBenchDeviations.Setting(settingsType, fi, target, key, coercedK));
                    if (error != null) return Fail(error);
                    return (object)new
                    {
                        success = true, action = "set", field = fi.Name, fieldKind = kind, key, presentBefore,
                        valueBefore = entryBefore, valueAfter = dict.Contains(key) ? SafeFieldToString(dict[key]) : null,
                        typeIdentity, ticksGame = TicksGameSafe(),
                    };
                }

                if (a == "get")
                {
                    return (object)new { success = true, action = "get", field = fi.Name, fieldKind = kind, value = SafeFieldToString(fi.GetValue(target)), typeIdentity, ticksGame = TicksGameSafe() };
                }

                if (a == "set")
                {
                    object no = SettingsSetFailure(settingsType, typeName, fi, null, value);
                    if (no != null) return no;
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
                    string error = JawaBenchDeviations.ApplySettings(driver, null, JawaBenchDeviations.Setting(settingsType, fi, target, null, coerced));
                    if (error != null) return Fail(error);
                    return (object)new
                    {
                        success = true,
                        action = "set",
                        field = fi.Name,
                        fieldKind = kind,
                        valueBefore = before,
                        valueAfter = SafeFieldToString(fi.GetValue(target)),
                        typeIdentity,
                        ticksGame = TicksGameSafe(),
                    };
                }

                return Fail("action must be 'list', 'get' or 'set'.");
            }).ConfigureAwait(false);
        }
    }
}
