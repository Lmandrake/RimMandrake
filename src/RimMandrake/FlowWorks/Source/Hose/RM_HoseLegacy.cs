using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using HarmonyLib;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// The hose's ESSENTIAL patches (hose port step 2, design FINAL §3.9 / G2.7): the save-skip (RM_MapComponent_Hoses never
    /// written into a save) and the type-name alias (a colonist saved mid-carry under GimmeSomeSlack / MessyConduit names
    /// resolves to the FlowWorks driver). They are applied here, outside PatchApplier's soft per-feature path, from the
    /// FlowWorks Mod constructor, and checked with harmony.GetPatchedMethods() afterwards. A missing one logs one red line;
    /// a missing save-skip also takes the hose map component off every map (RM_MapComponent_Hoses.FinalizeInit).
    /// The third essential (step 4): the universal pipe's def alias (RM_LiquidHose -> RM_UniversalPipe); without it an old
    /// save loses its pipe cells with missing-def errors.
    /// </summary>
    public static class RM_HoseEssentials
    {
        public const string HarmonyId = "mandrake.rm.flowworks.hose.essential";
        /// <summary>State read: the save-skip prefix/finalizer is on Map.ExposeComponents.</summary>
        public static bool SaveSkipPatched;
        /// <summary>State read: the type-name alias prefix is on GenTypes.GetTypeInAnyAssembly.</summary>
        public static bool TypeAliasPatched;
        /// <summary>State read: the universal pipe's def alias postfix is on BackCompatibility.BackCompatibleDefName.</summary>
        public static bool DefAliasPatched;
        /// <summary>State read: names of the essential patches that failed to apply (empty = all present).</summary>
        public static readonly List<string> Missing = new List<string>();
        private static bool applied;

        public static void Apply()
        {
            if (applied) return;
            applied = true;
            var h = new Harmony(HarmonyId);
            var exposeComponents = AccessTools.Method(typeof(Map), "ExposeComponents");
            var getType = AccessTools.Method(typeof(GenTypes), nameof(GenTypes.GetTypeInAnyAssembly));
            try
            {
                h.Patch(exposeComponents,
                    prefix: new HarmonyMethod(typeof(Patch_Map_ExposeComponents_SkipHoses), nameof(Patch_Map_ExposeComponents_SkipHoses.Prefix)),
                    finalizer: new HarmonyMethod(typeof(Patch_Map_ExposeComponents_SkipHoses), nameof(Patch_Map_ExposeComponents_SkipHoses.Finalizer)));
            }
            catch (Exception ex) { Log.Error("[FlowWorks] hose save-skip patch failed: " + ex.Message); }
            try { h.Patch(getType, prefix: new HarmonyMethod(typeof(RM_HoseLegacy), nameof(RM_HoseLegacy.TypeNamePrefix))); }
            catch (Exception ex) { Log.Error("[FlowWorks] hose type-name alias patch failed: " + ex.Message); }
            var defName = AccessTools.Method(typeof(BackCompatibility), nameof(BackCompatibility.BackCompatibleDefName));
            try { h.Patch(defName, postfix: new HarmonyMethod(typeof(RM_HoseLegacy), nameof(RM_HoseLegacy.DefNamePostfix))); }
            catch (Exception ex) { Log.Error("[FlowWorks] universal pipe def alias patch failed: " + ex.Message); }
            var patched = new HashSet<System.Reflection.MethodBase>(h.GetPatchedMethods());
            SaveSkipPatched = exposeComponents != null && patched.Contains(exposeComponents);
            TypeAliasPatched = getType != null && patched.Contains(getType);
            DefAliasPatched = defName != null && patched.Contains(defName);
            if (!SaveSkipPatched) Missing.Add("save-skip (Map.ExposeComponents)");
            if (!TypeAliasPatched) Missing.Add("type alias (GenTypes.GetTypeInAnyAssembly)");
            if (!DefAliasPatched) Missing.Add("def alias (BackCompatibility.BackCompatibleDefName)");
            if (!SaveSkipPatched)
                Log.Error("[FlowWorks] ESSENTIAL hose patch missing: save-skip (Map.ExposeComponents). Hoses are switched off for this session (nothing drawn; reels keep their saved hose ends) so no save names the hose map component.");
            if (!TypeAliasPatched)
                Log.Error("[FlowWorks] ESSENTIAL hose patch missing: type alias (GenTypes.GetTypeInAnyAssembly). A colonist saved mid-carry under the old Gimme Some Slack name loses that job on load (\"Cleaning up invalid job state\"); nothing else is lost.");
            if (!DefAliasPatched)
                Log.Error("[FlowWorks] ESSENTIAL patch missing: def alias (BackCompatibility.BackCompatibleDefName). An old save's RM_LiquidHose pipe cells do not load as universal pipes.");
            Log.Message("[FlowWorks] hose essential patches: " + (Missing.Count == 0 ? "all present (save-skip, type alias, def alias)" : "missing " + string.Join(", ", Missing)));
        }
    }

    /// <summary>Save and settings compatibility for the hose moved from Gimme Some Slack (design v2 §6, FINAL §3.8).</summary>
    public static class RM_HoseLegacy
    {
        /// <summary>GenTypes.GetTypeInAnyAssembly prefix: RimMandrake.GimmeSomeSlack.Hose.X and RimMandrake.MessyConduit.Hose.X
        /// -> RimMandrake.FlowWorks.Hose.X. Handles both prefixes itself, so it works with GSS absent.</summary>
        internal static void TypeNamePrefix(ref string typeName)
        {
            string mapped = RM_HoseLegacyMath.MapTypeName(typeName);
            if (mapped != null) typeName = mapped;
        }

        /// <summary>BackCompatibility.BackCompatibleDefName postfix: a saved RM_LiquidHose (and its blueprint/frame) loads as the
        /// universal pipe, unless that old name is itself a live def.</summary>
        internal static void DefNamePostfix(Type defType, ref string __result)
        {
            if (__result == null) return;
            string to = RM_HoseLegacyMath.MapDefName(defType?.Name, __result);
            if (to != null && DefDatabase<ThingDef>.GetNamedSilentFail(__result) == null) __result = to;
        }

        /// <summary>S3: an OLD Gimme Some Slack (one still carrying the hose) next to this FlowWorks would bring a second reel
        /// comp type, map component and style registration; the def copy FlowWorks loads after it replaces silently. One red line.</summary>
        public static void DetectOldGss()
        {
            try
            {
                // not GenTypes: our own alias would map the old name onto FlowWorks' type
                foreach (System.Reflection.Assembly a in AppDomain.CurrentDomain.GetAssemblies())
                    if (a != typeof(CompHoseReel).Assembly && a.GetType("RimMandrake.GimmeSomeSlack.Hose.CompHoseReel", false) != null)
                    {
                        Log.Error("[FlowWorks] Gimme Some Slack is older than this FlowWorks (it still carries the flexible hose); update both.");
                        break;
                    }
            }
            catch (Exception) { }
        }

        /// <summary>One-time import of the Gimme Some Slack hose settings (and its global look) into FlowWorks' hose section.
        /// Returns true when it changed anything (the caller writes the settings file). Never deletes the old file.</summary>
        public static bool ImportOnce()
        {
            if (RM_HoseSettings.hoseSettingsImported) return false;
            RM_HoseSettings.hoseSettingsImported = true;
            try
            {
                string dir = GenFilePaths.ConfigFolderPath;
                ModContentPack gss = LoadedModManager.RunningModsListForReading.FirstOrDefault(m => m.PackageIdPlayerFacing.ToLowerInvariant() == "mandrake.rm.gimmesomeslack");
                string prefer = gss?.FolderName;
                string hoseFile = Pick(dir, prefer, RM_HoseLegacyMath.HoseFileSuffix);
                int n = 0;
                if (hoseFile != null)
                {
                    Dictionary<string, string> keys = RM_HoseLegacyMath.HoseImport(File.ReadAllText(hoseFile));
                    if (!keys.ContainsKey("maxLengthDefaults")) RM_HoseSettings.maxLengthDefaults = 0;   // written before round 6
                    foreach (var kv in keys)
                        if (Set(kv.Key, kv.Value)) n++;
                    RM_HoseSettings.maxLength = (float)HoseMath.MigrateMaxLength(RM_HoseSettings.maxLength, RM_HoseSettings.maxLengthDefaults);
                    RM_HoseSettings.maxLengthDefaults = HoseMath.MaxLengthDefaultsVersion;
                }
                string cordFile = null;
                foreach (string suf in RM_HoseLegacyMath.CordFileSuffixes)
                    if ((cordFile = Pick(dir, prefer, suf)) != null) break;
                if (cordFile != null) RM_HoseSettings.defaultLook = RM_HoseLegacyMath.LookFromCordSettings(File.ReadAllText(cordFile));
                Log.Message("[FlowWorks] hose settings imported once from Gimme Some Slack: " + (hoseFile == null ? "no hose file (defaults)" : n + " keys from " + Path.GetFileName(hoseFile)) +
                            "; default look " + RM_HoseSettings.defaultLook + (cordFile == null ? " (no cord file)" : " from " + Path.GetFileName(cordFile)));
            }
            catch (Exception ex) { Log.Warning("[FlowWorks] could not import the Gimme Some Slack hose settings (defaults kept): " + ex.Message); }
            return true;
        }

        private static string Pick(string dir, string prefer, string suffix)
        {
            if (!Directory.Exists(dir)) return null;
            var c = new List<(string, DateTime)>();
            foreach (string f in Directory.GetFiles(dir, "Mod_*" + suffix)) c.Add((f, File.GetLastWriteTimeUtc(f)));
            return RM_HoseLegacyMath.PickFile(c, prefer, suffix);
        }

        private static bool Set(string key, string value)
        {
            var f = typeof(RM_HoseSettings).GetField(key, System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
            if (f == null) return false;
            if (f.FieldType == typeof(bool) && RM_HoseLegacyMath.TryBool(value, out bool b)) { f.SetValue(null, b); return true; }
            if (f.FieldType == typeof(int) && RM_HoseLegacyMath.TryInt(value, out int i)) { f.SetValue(null, i); return true; }
            if (f.FieldType == typeof(float) && RM_HoseLegacyMath.TryFloat(value, out float x)) { f.SetValue(null, x); return true; }
            return false;
        }
    }
}
