using System;
using System.Reflection;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING. A save made on PAINT (no Worldbuilder) loaded on the full list (with
    // Worldbuilder) ran UNLOCKED: Alien Worlds' PlanetTypeManager.Current reads Worldbuilder's preset there, the save
    // had no <worldPresetName>, so Current = "Default", the 7f.alienworlds.tidallylocked patches were never applied
    // (the sun rose and set) and the next save wrote alienWorldsFrameworkPlanetType = Default. Measured live
    // 2026-10-20: design/RimMandrake/world_physics_audit_2026-10-20.md §1.
    //
    // Two postfixes, all by reflection (neither Alien Worlds nor Worldbuilder is a hard dependency):
    //  1. World.ExposeData, LoadingVars: remember the planet type the SAVE carries. Alien Worlds' own prefix has just
    //     read it into PlanetTypeManager.current; its load hook overwrites that field with "Default" a moment later.
    //  2. SavedGameLoaderNow.LoadGameFromSaveFileNow, Priority.Last (after Alien Worlds' PostSaveLoadHook): when
    //     RM_TidalLockPresetKernel says so, set Worldbuilder's World_ExposeData_Patch.WorldPresetName = TidallyLocked
    //     and call PlanetTypeManager.UpdateActive(). Then ALWAYS log one readback line, which harvest_log.py's
    //     `tidallock` check reads, so a moving sun is caught at load (a warning when the save is locked and the
    //     planet is not):
    //       [RM CreatureBehaviors] planet lock at load: saved=<type> preset=<name> backend=<b> current=<type>
    //       lockPatches=<True|False> action=<restored|none|off>
    // Setting: tidalLockPresetGuard (default on). Off: the load is left to the two mods (the readback still logs).
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_TidalLockPresetGuard
    {
        public const string LinePrefix = "[RM CreatureBehaviors] planet lock at load: ";

        static readonly FieldInfo awfCurrent = AccessTools.Field(AccessTools.TypeByName("AlienWorlds.PlanetTypeManager"), "current");
        static readonly PropertyInfo awfCurrentProp = AccessTools.Property(AccessTools.TypeByName("AlienWorlds.PlanetTypeManager"), "Current");
        static readonly MethodInfo awfUpdateActive = AccessTools.Method(AccessTools.TypeByName("AlienWorlds.PlanetTypeManager"), "UpdateActive", new Type[0]);
        static readonly FieldInfo awfBackend = AccessTools.Field(AccessTools.TypeByName("AlienWorlds.AlienWorldsFramework"), "backend");
        static readonly PropertyInfo wbPresetName = AccessTools.Property(AccessTools.TypeByName("Worldbuilder.World_ExposeData_Patch"), "WorldPresetName");

        static string savedPlanetType;
        static bool sawWorldLoad;

        static RM_TidalLockPresetGuard()
        {
            if (awfCurrent == null || awfUpdateActive == null || awfBackend == null || awfCurrentProp == null) return; // no Alien Worlds: nothing to guard
            try
            {
                var harmony = new Harmony("mandrake.rm.creaturebehaviors.tidallockpreset");
                harmony.Patch(AccessTools.Method(typeof(World), nameof(World.ExposeData)),
                    postfix: new HarmonyMethod(typeof(RM_TidalLockPresetGuard), nameof(Postfix_WorldExposeData)));
                harmony.Patch(AccessTools.Method(typeof(SavedGameLoaderNow), nameof(SavedGameLoaderNow.LoadGameFromSaveFileNow)),
                    postfix: new HarmonyMethod(typeof(RM_TidalLockPresetGuard), nameof(Postfix_LoadGame)) { priority = Priority.Last });
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] tidal lock preset guard: patch failed; a save without a preset name may load unlocked: " + e);
            }
        }

        public static void Postfix_WorldExposeData()
        {
            if (Scribe.mode != LoadSaveMode.LoadingVars) return;
            try
            {
                savedPlanetType = awfCurrent.GetValue(null) as string;
                sawWorldLoad = true;
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] tidal lock preset guard: cannot read the saved planet type: " + e, 0x7A1D7);
            }
        }

        public static void Postfix_LoadGame()
        {
            if (!sawWorldLoad) return;
            string saved = savedPlanetType;
            savedPlanetType = null;
            sawWorldLoad = false;
            try
            {
                bool wb = awfBackend.GetValue(null)?.ToString() == "Worldbuilder" && wbPresetName != null;
                string preset = wb ? wbPresetName.GetValue(null) as string : null;
                bool on = RM_CreatureBehaviorsSettings.tidalLockPresetGuard;
                string restore = RM_TidalLockPresetKernel.PresetToRestore(on, wb, preset, saved);
                string action = !on ? "off" : "none";
                if (restore != null)
                {
                    wbPresetName.SetValue(null, restore);
                    awfUpdateActive.Invoke(null, null);
                    action = "restored";
                }
                string current = awfCurrentProp.GetValue(null) as string;
                bool patched = Harmony.HasAnyPatches(RM_TidalSunGlowPatch.TidalLockHarmonyId);
                string line = LinePrefix + "saved=" + (saved ?? "(none)") + " preset=" + (preset ?? "(none)")
                    + " backend=" + awfBackend.GetValue(null) + " current=" + (current ?? "(none)")
                    + " lockPatches=" + patched + " action=" + action;
                if (saved == RM_TidalLockPresetKernel.LockedType && (current != RM_TidalLockPresetKernel.LockedType || !patched))
                    Log.Warning(line + " -- MOVING SUN: the save is tidally locked, the loaded planet is not");
                else
                    Log.Message(line);
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] tidal lock preset guard: load hook failed; the planet may be unlocked: " + e);
            }
        }
    }
}
