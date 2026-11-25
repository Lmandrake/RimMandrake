// Settings are the first live producer of the process deviation record.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using C = JawaBench.BridgeTools.JawaBenchCondCore;
using D = JawaBench.BridgeTools.JawaBenchDeviationCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchDeviations
    {
        private static readonly Harmony Hooks = new Harmony("mandrake.jawabench.deviations");
        private static readonly HashSet<MethodBase> Guarded = new HashSet<MethodBase>();
        private static readonly HashSet<Type> DefaultSnapshots = new HashSet<Type>();
        private static bool _saveHook;
        internal static readonly D.Record Record = new D.Record(() =>
            Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench", "deviation-journal.jsonl"));

        internal static string CanonicalRefusal()
        {
            string save = JawaBenchCompanionSafety.LoadedSave(out string unknown);
            if (save == null) return "COULD_NOT_LOOK: " + unknown;
            if (JawaBenchSafetyCore.IsCanonical(save, JawaBenchCanonicalSaves.Names, JawaBenchCanonicalSaves.Starts))
                return "CANONICAL_SAVE: overlay refused on " + save;
            return null;
        }

        internal static string Revert(string holder) => Record.Revert(holder);

        internal static D.Entry Setting(Type type, FieldInfo field, object target, string key, object value)
        {
            IDictionary Dict() => field.GetValue(target) as IDictionary ??
                throw new InvalidOperationException(field.Name + " has no dictionary to address");
            if (key != null) _ = Dict();
            string name = type.FullName + "." + field.Name;
            if (key != null) name += "[" + C.Canon(key) + "]";
            return new D.Entry("overlay", "PUT BACK", "process", name, type.Assembly.FullName, value,
                () =>
                {
                    if (key == null) return field.GetValue(target);
                    var dict = Dict();
                    return dict.Contains(key) ? dict[key] : D.Absent;
                },
                v =>
                {
                    if (key == null) field.SetValue(target, v);
                    else if (ReferenceEquals(v, D.Absent)) Dict().Remove(key);
                    else Dict()[key] = v;
                });
        }

        private const BindingFlags StaticDefaults = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static;

        internal static void ObserveDefault(Type type, FieldInfo field, object target)
        {
            var attr = field.GetCustomAttribute<System.ComponentModel.DefaultValueAttribute>();
            var declared = type.GetField("Default" + char.ToUpperInvariant(field.Name[0]) + field.Name.Substring(1), StaticDefaults);
            if (attr != null)
                Record.ObserveDefault(type.FullName + "." + field.Name, attr.Value, () => field.GetValue(target));
            else if (declared != null && declared.IsLiteral && declared.FieldType == field.FieldType)
                Record.ObserveDefault(type.FullName + "." + field.Name, declared.GetRawConstantValue(), () => field.GetValue(target));

            // Settings Kit reset buttons already keep a snapshot of the shipped scalars, taken before ExposeData.
            if (!field.IsStatic || !DefaultSnapshots.Add(type)) return;
            var snapshot = type.GetField("shippedDefaults", StaticDefaults);
            if (snapshot?.GetValue(null) is IDictionary<string, object> values)
                foreach (var entry in values)
                {
                    var member = type.GetField(entry.Key, BindingFlags.Public | BindingFlags.Static);
                    if (member != null)
                        Record.ObserveDefault(type.FullName + "." + member.Name, entry.Value, () => member.GetValue(null));
                }
        }

        internal static string ApplyPlan(string driver, string overlay)
        {
            if (overlay == null) return null;
            if (overlay == "none")
                return Equals(Record.Receipt()["clean"], true) ? null : "OVERLAY_NOT_CLEAN: the game carries deviations";
            var no = CanonicalRefusal();
            if (no != null) return no;
            try
            {
                var plan = C.ParseJson(overlay) as Dictionary<string, object>;
                if (plan == null || plan.Count != 2 || !plan.TryGetValue("name", out object name) || !(name is string text) ||
                    string.IsNullOrWhiteSpace(text) || text.IndexOfAny(new[] { '\r', '\n' }) >= 0 ||
                    !plan.TryGetValue("entries", out object entries) || !(entries is List<object> rows) || rows.Count == 0)
                    return "BAD_OVERLAY: give a name and a nonempty list of settings entries";
                var writes = new List<D.Entry>();
                foreach (var row in rows)
                {
                    var fields = row as Dictionary<string, object>;
                    if (fields == null) return "BAD_OVERLAY: entry is not an object";
                    writes.Add(JawaBenchTerrainTools.PrepareOverlaySetting(fields));
                }
                return ApplySettings(driver, text, writes.ToArray());
            }
            catch (Exception e) { return "BAD_OVERLAY: " + e.Message; }
        }

        internal static string ApplySettings(string driver, string name, params D.Entry[] entries)
        {
            try
            {
                InstallSaveHook();
                InstallSettingsGuard(entries);
            }
            catch (Exception e) { return "COULD_NOT_LOOK: could not install the settings guards: " + e.Message; }
            JawaBenchVitals.EnsureDriver();
            var tm = Current.Game != null ? Find.TickManager : null;
            var speed = tm == null ? TimeSpeed.Paused : tm.CurTimeSpeed;
            if (tm != null) tm.CurTimeSpeed = TimeSpeed.Paused;
            try
            {
                return Record.Apply(JawaBenchHands.SettingsSessionOpen ? driver : null, name, entries);
            }
            finally { if (tm != null && !Record.Spoiled) tm.CurTimeSpeed = speed; }
        }

        internal static void Draw()
        {
            string stamp = Record.OverlayStamp;
            if (stamp != null) Widgets.Label(new Rect(12, 12, 600, 28), "OVERLAY " + stamp);
        }

        // The guard sits on the disk write itself, so a mod's own WriteSettings override (apply, rebuild tables)
        // still runs its body; only the file write is skipped while an open session holds that mod's entry.
        private static void InstallSettingsGuard(D.Entry[] entries)
        {
            var method = AccessTools.Method(typeof(LoadedModManager), nameof(LoadedModManager.WriteModSettings),
                new[] { typeof(string), typeof(string), typeof(ModSettings) });
            if (method == null) throw new MissingMethodException("LoadedModManager.WriteModSettings");
            if (Guarded.Contains(method)) return;
            Hooks.Patch(method, prefix: new HarmonyMethod(typeof(JawaBenchDeviations), nameof(WriteModSettingsPrefix)) { priority = Priority.First });
            Guarded.Add(method);
        }

        private static bool OwnsSettings(Mod mod, Func<string, bool> matches)
            => matches(mod.GetType().Assembly.FullName) ||
               mod.Content?.assemblies?.loadedAssemblies?.Any(a => matches(a.FullName)) == true;

        private static bool WriteModSettingsPrefix(string modHandleName, ModSettings settings)
        {
            try
            {
                if (settings != null && Record.BlocksSettings(settings.GetType().Assembly.FullName)) return false;
                foreach (var mod in LoadedModManager.ModHandles)
                    if (mod.GetType().Name == modHandleName && OwnsSettings(mod, assembly => Record.BlocksSettings(assembly)))
                        return false;
                return true;
            }
            catch (Exception e) { Log.Error("[JawaBench] settings write guard: " + e.Message); return false; }
        }

        internal static void InstallSaveHook()
        {
            if (_saveHook) return;
            var method = AccessTools.Method(typeof(Game), nameof(Game.ExposeData), Type.EmptyTypes);
            if (method == null) throw new MissingMethodException("Game.ExposeData");
            Hooks.Patch(method, postfix: new HarmonyMethod(typeof(JawaBenchDeviations), nameof(SaveMarkPostfix)));
            _saveHook = true;
        }

        private static void SaveMarkPostfix(bool __runOriginal)
        {
            if (!__runOriginal) return;
            try
            {
                bool tuned = Record.Tainted;
                bool dirty = Record.SaveDirty || Record.Spoiled;
                Scribe_Values.Look(ref tuned, "jawaBenchTuned");
                Scribe_Values.Look(ref dirty, "jawaBenchSaveDirty");
                if (Scribe.mode == LoadSaveMode.LoadingVars) Record.Load(tuned, dirty);
            }
            catch (Exception e) { Log.Error("[JawaBench] deviation save mark: " + e.Message); }
        }
    }
}
