using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Patches
{
    // Forces CAI 5000's own fog of war off (CAI_FOG_SILENCE_FORCED_OFF_BY_US; owner card 2026-10-20 "Keep CAI, force its
    // fog off" after Real Fog of War left the list). MEASURED 2026-11-01 from the installed CombatAI.dll (Krkr.rule56,
    // workshop 3673768803): CombatAI.Settings.FogOfWar_Enabled has no initializer and Scribe default false, and no preset
    // assigns it, so a fresh install starts with fog off; only CAI's checkbox (Mod Settings or first-run Quick Setup)
    // turns it on, and a player's old config keeps it on. This keeps it off in both cases.
    //
    // CombatAI.dll is never referenced: every member is bound by name. CAI absent -> nothing happens, silently. CAI present
    // but a member renamed -> one warning naming it, nothing patched. The names are checked against the installed DLL by
    // selftest_mandrakepatches.py (CAI_MEMBERS there must match the strings here).
    //
    // Two hooks: (1) at our Mod constructor (we loadAfter Krkr.rule56, so CAI's settings are already read) and again at
    // StaticConstructorOnStartup, before any map exists; (2) a Harmony prefix on CombatAIMod.WriteSettings, which CAI runs
    // when its settings window closes, so a ticked checkbox never persists. A map that drew CAI fog while the window was
    // open clears itself: MapComponent_FogGrid restores its applied fog when it next sees FogOfWar_Enabled go false.
    [StaticConstructorOnStartup]
    public static class CaiFogOffStartup
    {
        // A separate class on purpose: StaticConstructorOnStartup runs a class constructor that has not run yet, and CaiFogOff
        // is first touched inside our Mod constructor, so the attribute on it would never fire at startup.
        static CaiFogOffStartup()
        {
            CaiFogOff.Install();
            CaiFogOff.Force("startup");
        }
    }

    public static class CaiFogOff
    {
        public const string FinderType = "CombatAI.Finder";
        public const string ModType = "CombatAI.CombatAIMod";
        public const string FinderSettingsField = "Settings";
        public const string FinderModField = "Mod";
        public const string FogField = "FogOfWar_Enabled";
        public const string SightField = "NewSightSystem_Enabled";   // CAI itself clears this whenever fog is off
        public const string PrevFogField = "prevFogEnabled";          // CombatAIMod's record of the last written fog state
        public const string WriteSettingsMethod = "WriteSettings";

        static FieldInfo finderSettings, finderMod, fog, sight, prevFog;
        static bool installed, bound;
        public static string Status = "CAI 5000 is not loaded: nothing to do.";

        public static void Install()
        {
            if (installed) return;
            installed = true;
            Type finderT = AccessTools.TypeByName(FinderType);
            if (finderT == null) return;   // CAI absent: silent no-op
            Type modT = AccessTools.TypeByName(ModType);
            finderSettings = AccessTools.Field(finderT, FinderSettingsField);
            finderMod = AccessTools.Field(finderT, FinderModField);
            Type settingsT = finderSettings?.FieldType;
            fog = settingsT == null ? null : AccessTools.Field(settingsT, FogField);
            sight = settingsT == null ? null : AccessTools.Field(settingsT, SightField);
            prevFog = modT == null ? null : AccessTools.Field(modT, PrevFogField);
            MethodInfo write = modT == null ? null : AccessTools.Method(modT, WriteSettingsMethod, Type.EmptyTypes);
            if (fog == null || fog.FieldType != typeof(bool) || write == null)
            {
                Status = "CAI 5000 is loaded but its fog setting was not found (CAI changed): fog NOT forced off.";
                Log.Warning("[RimMandrake Patches] CAI 5000 found but " + settingsT + "." + FogField + " or " + ModType + "." +
                            WriteSettingsMethod + "() is missing; its fog of war is NOT being forced off.");
                return;
            }
            new Harmony("mandrake.rm.patches.caifogoff").Patch(write,
                prefix: new HarmonyMethod(typeof(CaiFogOff), nameof(Prefix_WriteSettings)));
            bound = true;
            Force("constructor");
        }

        public static void Prefix_WriteSettings() => Force("CAI settings saved");

        // True when this call left CAI's fog off.
        public static bool Force(string why)
        {
            if (!bound) return false;
            if (!RM_PatchesSettings.caiFogForcedOff)
            {
                Status = "CAI 5000 is loaded; its fog is left to CAI's own checkbox.";
                return false;
            }
            object settings = finderSettings.GetValue(null);
            if (settings == null) return false;   // CAI not constructed yet; StaticConstructorOnStartup tries again
            bool was = (bool)fog.GetValue(settings);
            fog.SetValue(settings, false);
            if (sight != null && sight.FieldType == typeof(bool)) sight.SetValue(settings, false);
            // Before any map exists, align CAI's last-written record too, so its next WriteSettings sees no fog change.
            if (why != "CAI settings saved" && prevFog != null && prevFog.FieldType == typeof(bool) && Current.Game == null)
            {
                object mod = finderMod?.GetValue(null);
                if (mod != null) prevFog.SetValue(mod, false);
            }
            Status = "CAI 5000 is loaded; its fog of war is forced off.";
            if (was) Log.Message("[RimMandrake Patches] CAI 5000 fog of war was on; forced off (" + why + ").");
            return true;
        }
    }
}
