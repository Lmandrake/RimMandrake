using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Aftermath
{
    // PLOT_MECHANISM_MODS_WAVE_1, rule 6 ("Zizzik's aftermath") needs to read
    // Ninefold's LIVE Zizzik satiation band. CHRONICLE_NINEFOLD_DECOUPLE_1 /
    // design/CHRONICLE_EVENT_SPINE.md's soft-hook laws forbid a <Reference>
    // in EITHER direction between this engine and Ninefold (see this mod's
    // own .csproj header) -- this is the mirror image of Ninefold's own
    // ChronicleSubscriber.cs (which subscribes to OUR spine by reflection);
    // here WE query THEM by reflection instead. Same idiom: AccessTools.
    // TypeByName, cached MethodInfo/PropertyInfo, warn once on a shape
    // change, and Ninefold absent/renamed/reshaped reads as "never eligible"
    // -- law 2 (this engine is whole with Ninefold absent): rule 6 simply
    // never fires, exactly like every OTHER Ninefold-tied consumer's null
    // guard already does.
    //
    // Verified against source, not guessed (src/RimMandrake/Ninefold/Source/
    // GameComponent_Ninefold.cs, God.cs, SatiationBand.cs): `public static
    // GameComponent_Ninefold Instance`, `public SatiationBand GetBand(God
    // god)`, enum `God` has member `Zizzik`, enum `SatiationBand` is ordered
    // Wrathful < Slighted < Neutral < Content < Exalted so a plain ordinal
    // `>=` comparison against Content is correct.
    internal static class NinefoldBandBridge
    {
        private const string NinefoldTypeName = "RimMandrake.Ninefold.GameComponent_Ninefold";
        private const string GodTypeName = "RimMandrake.Ninefold.God";
        private const string BandTypeName = "RimMandrake.Ninefold.SatiationBand";

        private static bool resolved;
        private static bool warned;
        private static PropertyInfo instanceProp;
        private static MethodInfo getBandMethod;
        private static object zizzikBoxed;
        private static int contentOrdinal = -1;

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;

            Type ninefoldType = AccessTools.TypeByName(NinefoldTypeName);
            Type godType = AccessTools.TypeByName(GodTypeName);
            Type bandType = AccessTools.TypeByName(BandTypeName);
            if (ninefoldType == null || godType == null || bandType == null)
                return; // Ninefold not loaded -- nothing to warn about, this is a normal modlist.

            instanceProp = AccessTools.Property(ninefoldType, "Instance");
            getBandMethod = AccessTools.Method(ninefoldType, "GetBand", new[] { godType });

            if (instanceProp == null || getBandMethod == null || !godType.IsEnum || !bandType.IsEnum)
            {
                WarnOnce("found Ninefold but GameComponent_Ninefold.Instance/GetBand(God) changed shape");
                instanceProp = null;
                getBandMethod = null;
                return;
            }

            try
            {
                zizzikBoxed = Enum.Parse(godType, "Zizzik");
                contentOrdinal = (int)Enum.Parse(bandType, "Content");
            }
            catch (ArgumentException)
            {
                WarnOnce("found Ninefold but God.Zizzik or SatiationBand.Content no longer exists");
                instanceProp = null;
                getBandMethod = null;
            }
        }

        private static void WarnOnce(string what)
        {
            if (warned) return;
            warned = true;
            Log.Warning("[RimMandrake.Aftermath] " + what + " -- rule 6 (Zizzik's aftermath) is OFF.");
        }

        // True only when Ninefold is loaded, a Game is running, and Zizzik's
        // satiation is at Content or higher. Never throws; absent/renamed/
        // no-live-Game all read as false.
        public static bool ZizzikAtLeastContent()
        {
            Resolve();
            if (instanceProp == null || getBandMethod == null || zizzikBoxed == null) return false;

            object instance = instanceProp.GetValue(null);
            if (instance == null) return false;

            object bandBoxed = getBandMethod.Invoke(instance, new[] { zizzikBoxed });
            if (bandBoxed == null) return false;

            return (int)bandBoxed >= contentOrdinal;
        }
    }
}
