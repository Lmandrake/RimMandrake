using System.Collections;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Armoury
{
    // ASTEROID_DESERT_ORES_1 + the aboard re-melt duty of CANON_MATERIALS_BUILD_1 — applies four
    // RSW_ArmourySettings toggles at startup (they take effect after the next game load):
    //   dooniumAsteroidEnabled  RSW_MineableDoonium stays in the Odyssey asteroid GenSteps' mineableCounts and in
    //                           GeneratedLocationDef Asteroids.preciousResources
    //   dooniumSmeltEnabled     RSW_SmeltDoonium stays on the ship smelters
    //   phrikSmeltEnabled       RSW_SmeltPhrik stays on the ship smelters
    //   slagRemeltAboardEnabled RSW_SmeltPlasteelFromSlag / RSW_SmeltDurasteelFromSlag stay on the ship smelters
    // Patches/RSW_OdysseyAsteroid_Doonium.xml and Patches/RSW_Smelter_Alloys.xml add them unconditionally on the
    // setting; this removes what a disabled toggle should not have. PipeSystem (VFE) types are not referenced by this
    // assembly: the process defs and the comps' `processes` lists are reached by reflection on their XML field names.
    // Every lookup is silent-fail: no VFE Factory, no Odyssey, or an unpatched def means nothing to do.
    [StaticConstructorOnStartup]
    public static class RSW_AlloyOres
    {
        static readonly string[] Smelters =
        {
            "VFEFactory_AutomatedSmelter", "RM_WM_AutomatedSmelter_Kludged",
            "RM_WM_AutomatedSmelter_Refurbished", "RM_WM_AutomatedSmelter_Repaired",
        };

        static readonly string[] AsteroidSteps = { "Asteroid", "Asteroid_NoRuins", "AsteroidBasic" };

        static RSW_AlloyOres()
        {
            Apply();
        }

        public static void Apply()
        {
            if (!RSW_ArmourySettings.dooniumSmeltEnabled) RemoveProcess("RSW_SmeltDoonium");
            if (!RSW_ArmourySettings.phrikSmeltEnabled) RemoveProcess("RSW_SmeltPhrik");
            if (!RSW_ArmourySettings.slagRemeltAboardEnabled)
            {
                RemoveProcess("RSW_SmeltPlasteelFromSlag");
                RemoveProcess("RSW_SmeltDurasteelFromSlag");
            }
            if (!RSW_ArmourySettings.dooniumAsteroidEnabled) RemoveAsteroidDoonium();
        }

        static void RemoveProcess(string processDefName)
        {
            var processType = GenTypes.GetTypeInAnyAssembly("PipeSystem.ProcessDef");
            if (processType == null) return;
            var process = GenDefDatabase.GetDefSilentFail(processType, processDefName, false);
            if (process == null) return;
            foreach (string name in Smelters)
            {
                var smelter = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (smelter == null || smelter.comps == null) continue;
                foreach (var props in smelter.comps)
                {
                    var f = props.GetType().GetField("processes",
                        BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                    if (f == null) continue;
                    var list = f.GetValue(props) as IList;
                    if (list != null && list.Contains(process)) list.Remove(process);
                }
            }
        }

        // GenStep_Asteroid.mineableCounts is a List<MineableCountConfig> (1.6 decompile; the XML's element-name keys are read by
        // MineableCountConfig.LoadDataFromXmlCustom), not a dictionary; GenStep_BasicAsteroid derives from it. The ore must also
        // leave GeneratedLocationDef Asteroids.preciousResources: WorldComponent_LocationGenerator picks a site's precious
        // resource from that list and GenStep_Asteroid.SpawnOres places the precious resource first, so leaving it there would
        // keep spawning doonium (and, with its count gone, log "No count found for resource"). An asteroid site generated
        // before the toggle went off keeps its saved precious resource; that one site logs the vanilla error and gets no ore.
        static void RemoveAsteroidDoonium()
        {
            var ore = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_MineableDoonium");
            if (ore == null) return;
            foreach (string step in AsteroidSteps)
            {
                var def = DefDatabase<GenStepDef>.GetNamedSilentFail(step);
                if (def?.genStep is GenStep_Asteroid asteroid && asteroid.mineableCounts != null)
                    asteroid.mineableCounts.RemoveAll(c => c != null && c.mineable == ore);
            }
            DefDatabase<GeneratedLocationDef>.GetNamedSilentFail("Asteroids")?.preciousResources?.Remove(ore);
        }
    }
}
