// LoadTracer - diagnostic instrument for COLD_LOAD_STALL_INTERMITTENT_1.
//
// Replaces StaticConstructorOnStartupUtility.CallAll with a byte-equivalent loop that
// logs every [StaticConstructorOnStartup] type BEFORE invoking it, and brackets the
// stages that run after it inside DoPlayLoad's final ExecuteWhenFinished delegate
// (FloatMenuMakerMap.Init, GlobalTextureAtlasManager.BakeStaticAtlases). When the
// cold load stalls, the last [LoadTracer] line in Player.log names the stuck site.
//
// Per-type lines go through UnityEngine.Debug.Log DIRECTLY: Verse.Log stops logging
// after its message cap (1000), and a 592-mod trace would blow through it mid-list.
// The Mod-subclass ctor runs during LoadedModManager.LoadAllActiveMods, long before
// CallAll, so the patch is always in place in time.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.LoadTracer
{
    public class LoadTracerMod : Mod
    {
        public LoadTracerMod(ModContentPack content) : base(content)
        {
            try
            {
                var h = new Harmony("mandrake.rm.loadtracer");

                h.Patch(
                    AccessTools.Method(typeof(StaticConstructorOnStartupUtility),
                                       nameof(StaticConstructorOnStartupUtility.CallAll)),
                    prefix: new HarmonyMethod(typeof(LoadTracerPatches),
                                              nameof(LoadTracerPatches.CallAllPrefix)));

                h.Patch(
                    AccessTools.Method(typeof(FloatMenuMakerMap), "Init"),
                    prefix: new HarmonyMethod(typeof(LoadTracerPatches), nameof(LoadTracerPatches.FloatMenuInitPrefix)),
                    postfix: new HarmonyMethod(typeof(LoadTracerPatches), nameof(LoadTracerPatches.FloatMenuInitPostfix)));

                h.Patch(
                    AccessTools.Method(typeof(GlobalTextureAtlasManager),
                                       nameof(GlobalTextureAtlasManager.BakeStaticAtlases)),
                    prefix: new HarmonyMethod(typeof(LoadTracerPatches), nameof(LoadTracerPatches.BakePrefix)),
                    postfix: new HarmonyMethod(typeof(LoadTracerPatches), nameof(LoadTracerPatches.BakePostfix)));

                Log.Message("[LoadTracer] armed: CallAll per-type trace + FloatMenuMakerMap.Init/BakeStaticAtlases brackets");
            }
            catch (Exception ex)
            {
                Log.Error("[LoadTracer] failed to arm - tracing is ABSENT this load: " + ex);
            }
        }
    }

    public static class LoadTracerPatches
    {
        // Replicates the original CallAll exactly (same loop, same per-type try/catch,
        // same completion flag) with one Debug.Log line per type added.
        public static bool CallAllPrefix()
        {
            UnityEngine.Debug.Log("[LoadTracer] CallAll begin");
            List<Type> types;
            try
            {
                types = GenTypes.AllTypesWithAttribute<StaticConstructorOnStartup>().ToList();
            }
            catch (Exception ex)
            {
                UnityEngine.Debug.Log("[LoadTracer] type enumeration FAILED, falling back to original CallAll: " + ex);
                return true; // run the original untraced rather than break loading
            }
            UnityEngine.Debug.Log("[LoadTracer] CallAll: " + types.Count + " static ctors to run");
            int i = 0;
            foreach (Type item in types)
            {
                i++;
                UnityEngine.Debug.Log("[LoadTracer] ctor " + i + "/" + types.Count + ": " +
                                      item.FullName + " [" + item.Assembly.GetName().Name + "]");
                try
                {
                    RuntimeHelpers.RunClassConstructor(item.TypeHandle);
                }
                catch (Exception ex)
                {
                    Log.Error("Error in static constructor of " + item?.ToString() + ": " + ex);
                }
            }
            StaticConstructorOnStartupUtility.coreStaticAssetsLoaded = true;
            UnityEngine.Debug.Log("[LoadTracer] CallAll complete");
            return false;
        }

        public static void FloatMenuInitPrefix() => UnityEngine.Debug.Log("[LoadTracer] FloatMenuMakerMap.Init begin");
        public static void FloatMenuInitPostfix() => UnityEngine.Debug.Log("[LoadTracer] FloatMenuMakerMap.Init done");
        public static void BakePrefix() => UnityEngine.Debug.Log("[LoadTracer] BakeStaticAtlases begin");
        public static void BakePostfix() => UnityEngine.Debug.Log("[LoadTracer] BakeStaticAtlases done");
    }
}
