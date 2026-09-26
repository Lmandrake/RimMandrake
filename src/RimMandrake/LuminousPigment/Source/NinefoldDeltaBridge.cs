using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §5.1: "Deepfire binds to it by reflection, no assembly reference
    // -- copy src/RimMandrake/Aftermath/Source/NinefoldBandBridge.cs ... and
    // add ApplyDelta." Same idiom as that file (and as HediffComp_
    // DeepfireGlow.DeepfireLightsBridge in this mod): resolve by name once,
    // cache, warn only on a real shape mismatch, and treat Ninefold absent
    // as a normal, silent no-op -- Ninefold is a soft dependency this mod is
    // fully functional without (About.xml).
    //
    // Verified against src/RimMandrake/Ninefold/Source/GameComponent_
    // Ninefold.cs and God.cs: `public static GameComponent_Ninefold
    // Instance`, `public void ApplyDelta(God god, float amount, string
    // reason = null)`, enum `God { Ishko, Ohm, Oomo, MobUnloo, Rekko, TaBaa,
    // Zizzik, Shkaar, Ozzik }`.
    //
    // Only two of §5.2's event rows are wired by this build:
    //   - "a Deepfire dish eaten" (Zizzik +Small, Ozzik +Small) --
    //     IngestionOutcomeDoer_SteeredFamily, fires on every deepfire dish.
    //   - the vermilion's "cannot be hidden -- Ishko -Medium on reaching
    //     III" -- HediffComp_DeepfireGlow.
    // Every other row (first coat, worn coat, sold, statue) needs
    // CompDeepfire (piece 1, painting), which this item defers to
    // DEEPFIRE_PAINT_LIVE_VERIFY_1 -- wiring them is that follow-on's work,
    // not a new engine question, once CompDeepfire exists to raise the event.
    internal static class NinefoldDeltaBridge
    {
        private const string NinefoldTypeName = "RimMandrake.Ninefold.GameComponent_Ninefold";
        private const string GodTypeName = "RimMandrake.Ninefold.God";

        private static bool resolved;
        private static bool warned;
        private static PropertyInfo instanceProp;
        private static MethodInfo applyDeltaMethod;
        private static Type godType;

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;

            Type ninefoldType = AccessTools.TypeByName(NinefoldTypeName);
            godType = AccessTools.TypeByName(GodTypeName);
            if (ninefoldType == null || godType == null) return; // Ninefold not loaded -- a normal modlist.

            instanceProp = AccessTools.Property(ninefoldType, "Instance");
            applyDeltaMethod = AccessTools.Method(ninefoldType, "ApplyDelta",
                new[] { godType, typeof(float), typeof(string) });

            if (instanceProp == null || applyDeltaMethod == null || !godType.IsEnum)
            {
                WarnOnce("found Ninefold but GameComponent_Ninefold.Instance/ApplyDelta(God,float,string) changed shape");
                instanceProp = null;
                applyDeltaMethod = null;
            }
        }

        private static void WarnOnce(string what)
        {
            if (warned) return;
            warned = true;
            Log.Warning("[RimMandrake.LuminousPigment] " + what + " -- Ninefold god reactions are OFF.");
        }

        // godName must be one of the God enum member names (e.g. "Ishko",
        // "Zizzik", "Ozzik"). Never throws; Ninefold absent, unloaded,
        // renamed, or godName not a real member all read as a silent no-op.
        public static void ApplyDelta(string godName, float amount, string reason)
        {
            if (!LuminousPigmentSettings.godsReact) return;
            Resolve();
            if (instanceProp == null || applyDeltaMethod == null) return;

            object instance = instanceProp.GetValue(null);
            if (instance == null) return; // no live Game.

            object godBoxed;
            try
            {
                godBoxed = Enum.Parse(godType, godName);
            }
            catch (ArgumentException)
            {
                WarnOnce("God." + godName + " no longer exists");
                return;
            }

            applyDeltaMethod.Invoke(instance, new object[] { godBoxed, amount, reason });
        }
    }
}
