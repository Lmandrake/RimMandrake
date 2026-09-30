using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_GOD_BRIDGE_DELTAS_1, spec §8 LightsOut row / §10 step 10:
    // "proxies survive an empty room being 'switched off'".
    //
    // The spec expected LightsOut to leave our proxies alone ("no
    // CompFlickable, no power"). It does not. Read from the installed
    // LightsOut.dll (juanlopez2008.lightsout, workshop 2584269293, its 1.6
    // load folder is the root Assemblies/), decompiled:
    //   - Lights.CanBeLight(ThingWithComps) accepts any thing with a
    //     CompGlower, none of CompPowerPlant/HeatPusher/Schedule/TempControl/
    //     ShipLandingBeacon, and a lowercased defName containing "light",
    //     "lamp" or "illuminated". RM_DeepfireLightProxy and
    //     RM_DeepfireWornLightProxy both contain "light".
    //   - Lights.DisableAllLights(room) walks room.ContainedAndAdjacentThings
    //     (Ethereal things are region-listed: ListerThings.EverListable only
    //     drops Motes and Projectiles, RimSage) and sets
    //     Resources.BuildingStatus[thing] = false.
    //   - Its CompGlower postfix then forces the glow off whenever
    //     Resources.CanConsumeResources(parent) == false.
    // So an empty or sleeping room would douse every coated wall, floor
    // cluster and item in it.
    //
    // Fix, both halves by reflection (LightsOut is a soft dependency; no
    // assembly reference): CanBeLight answers false for our two proxy defs
    // (they are never switched), and CanConsumeResources answers null for
    // them (the glow postfix leaves them alone even if some other LightsOut
    // path recorded a status). Patched by position (__0) because the
    // parameter names are the decompiler's, not a contract.
    [StaticConstructorOnStartup]
    public static class DeepfireLightsOutCompat
    {
        public const string HarmonyId = "mandrake.rm.luminouspigment.lightsout";
        public const string LightsTypeName = "LightsOut.Common.Lights";
        public const string ResourcesTypeName = "LightsOut.Common.Resources";

        public static readonly bool LightsOutLoaded;
        public static readonly bool CanBeLightPatched;
        public static readonly bool CanConsumePatched;

        static DeepfireLightsOutCompat()
        {
            Type lights = AccessTools.TypeByName(LightsTypeName);
            Type resources = AccessTools.TypeByName(ResourcesTypeName);
            if (lights == null || resources == null) return; // LightsOut not loaded -- a normal modlist.
            LightsOutLoaded = true;

            var harmony = new Harmony(HarmonyId);

            MethodInfo canBeLight = AccessTools.Method(lights, "CanBeLight", new[] { typeof(ThingWithComps) });
            if (canBeLight != null && canBeLight.ReturnType == typeof(bool))
            {
                harmony.Patch(canBeLight, prefix: new HarmonyMethod(typeof(DeepfireLightsOutCompat), nameof(CanBeLightPrefix)));
                CanBeLightPatched = true;
            }

            MethodInfo canConsume = AccessTools.Method(resources, "CanConsumeResources", new[] { typeof(ThingWithComps) });
            if (canConsume != null && canConsume.ReturnType == typeof(bool?))
            {
                harmony.Patch(canConsume, postfix: new HarmonyMethod(typeof(DeepfireLightsOutCompat), nameof(CanConsumePostfix)));
                CanConsumePatched = true;
            }

            if (!CanBeLightPatched || !CanConsumePatched)
            {
                Log.Warning("[RimMandrake.LuminousPigment] LightsOut is loaded but Lights.CanBeLight/Resources.CanConsumeResources "
                    + "changed shape -- LightsOut may switch Deepfire glows off in empty rooms.");
            }
        }

        public static bool IsDeepfireProxy(Thing thing)
        {
            if (thing == null) return false;
            return thing.def == DeepfireDefOf.RM_DeepfireLightProxy || thing.def == DeepfireDefOf.RM_DeepfireWornLightProxy;
        }

        public static bool CanBeLightPrefix(ThingWithComps __0, ref bool __result)
        {
            if (!IsDeepfireProxy(__0)) return true;
            __result = false;
            return false;
        }

        public static void CanConsumePostfix(ThingWithComps __0, ref bool? __result)
        {
            if (IsDeepfireProxy(__0)) __result = null;
        }
    }
}
