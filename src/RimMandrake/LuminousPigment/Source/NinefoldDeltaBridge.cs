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
    // Ninefold.cs, God.cs and RM_NinefoldMod.cs: `public static
    // GameComponent_Ninefold Instance`, `public void ApplyDelta(God god, float
    // amount, string reason = null)`, `public float GetSatiation(God god)`,
    // enum `God { Ishko, Ohm, Oomo, MobUnloo, Rekko, TaBaa, Zizzik, Shkaar,
    // Ozzik }`, `RM_NinefoldSettings.eventMagnitudeMultiplier` (static float).
    //
    // Callers: DeepfireGodDeltas.cs (every §5.2 coat/sold/statue row),
    // IngestionOutcomeDoer_SteeredFamily (dish eaten), HediffComp_DeepfireGlow
    // (the vermilion's Ishko penalty).
    internal static class NinefoldDeltaBridge
    {
        private const string NinefoldTypeName = "RimMandrake.Ninefold.GameComponent_Ninefold";
        private const string GodTypeName = "RimMandrake.Ninefold.God";
        private const string SettingsTypeName = "RimMandrake.Ninefold.RM_NinefoldSettings";

        private static bool resolved;
        private static bool warned;
        private static PropertyInfo instanceProp;
        private static MethodInfo applyDeltaMethod;
        private static MethodInfo getSatiationMethod;
        private static FieldInfo multiplierField;
        private static Type godType;
        private static string[] godNames = new string[0];

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
            getSatiationMethod = AccessTools.Method(ninefoldType, "GetSatiation", new[] { godType });
            Type settingsType = AccessTools.TypeByName(SettingsTypeName);
            multiplierField = settingsType != null ? AccessTools.Field(settingsType, "eventMagnitudeMultiplier") : null;

            if (instanceProp == null || applyDeltaMethod == null || !godType.IsEnum)
            {
                WarnOnce("found Ninefold but GameComponent_Ninefold.Instance/ApplyDelta(God,float,string) changed shape");
                instanceProp = null;
                applyDeltaMethod = null;
                return;
            }
            godNames = Enum.GetNames(godType);
        }

        private static void WarnOnce(string what)
        {
            if (warned) return;
            warned = true;
            Log.Warning("[RimMandrake.LuminousPigment] " + what + " -- Ninefold god reactions are OFF.");
        }

        public static bool Available
        {
            get
            {
                Resolve();
                return applyDeltaMethod != null;
            }
        }

        // Every God enum member name, in enum order; empty with Ninefold absent.
        public static string[] GodNames
        {
            get
            {
                Resolve();
                return godNames;
            }
        }

        public static bool IsGod(string godName)
        {
            if (string.IsNullOrEmpty(godName)) return false;
            return Array.IndexOf(GodNames, godName) >= 0;
        }

        // Ninefold scales every ApplyDelta by this (GameComponent_Ninefold.
        // ApplyDelta); 1 when unreadable. Proof actions report it so a
        // before/after diff is compared against amount x multiplier.
        public static float MagnitudeMultiplier
        {
            get
            {
                Resolve();
                if (multiplierField == null) return 1f;
                return (float)multiplierField.GetValue(null);
            }
        }

        // RM_NinefoldSettings.engineEnabled: with the engine off Ninefold's
        // ApplyDelta returns before moving anything. Reported by the proofs
        // so an all-zero diff is not misread as our wiring being dead.
        public static bool EngineEnabled
        {
            get
            {
                Resolve();
                if (multiplierField == null) return true;
                FieldInfo f = AccessTools.Field(multiplierField.DeclaringType, "engineEnabled");
                return f == null || (bool)f.GetValue(null);
            }
        }

        public static bool TryGetSatiation(string godName, out float value)
        {
            value = 0f;
            Resolve();
            if (instanceProp == null || getSatiationMethod == null || !IsGod(godName)) return false;
            object instance = instanceProp.GetValue(null);
            if (instance == null) return false;
            value = (float)getSatiationMethod.Invoke(instance, new[] { Enum.Parse(godType, godName) });
            return true;
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
