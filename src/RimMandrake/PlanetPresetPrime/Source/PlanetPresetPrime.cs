using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.PlanetPresetPrime
{
    // Ash'karr is 21,872 tiles: planetCoverage 1.0 at subdivisions 7. Nothing in
    // RimWorld remembers either number - Config/Prefs.xml has 63 keys and not one
    // of them mentions planet, coverage, subcount or seed, and My Little Planet
    // writes no mod config at all. Both are re-chosen from a hardcoded default
    // every time the world-creation page opens.
    //
    // Open that page at the defaults and you get a 119,904-tile grid, against
    // which world/ASHKARR_WORLDMAP_tiles.csv (rows 0..21871) addresses entirely
    // different ground - and an import reports success while writing a scrambled
    // planet. This primes both numbers so that cannot happen by forgetting.
    [StaticConstructorOnStartup]
    public static class PlanetPresetPrimeMod
    {
        public const float Coverage    = 1.0f;
        public const int   Subdivisions = 7;   // MLP's slider is 6..10 inclusive; 7 is in range

        static PlanetPresetPrimeMod()
        {
            Harmony h = new Harmony("mandrake.rm.planetpresetprime");
            h.PatchAll(Assembly.GetExecutingAssembly());

            // A mod that writes nothing at load is indistinguishable from a mod that
            // failed to load at all - that is JAWABENCH_HAS_NO_INIT_LINE_1, filed on
            // this project for exactly this mistake. So say so at STARTUP, not only
            // when the page opens: the page may never open in a given session, and
            // its silence would then read as "the assembly is missing".
            Log.Message(string.Format(
                "[RimMandrake.PlanetPresetPrime] loaded: will prime coverage {0}, subdivisions {1}. "
                + "MLP type {2}.",
                Coverage, Subdivisions,
                AccessTools.TypeByName("WorldGenRules.WorldGenRules") != null ? "found" : "ABSENT"));
        }
    }

    // Reset() is the method that actually assigns planetCoverage
    // (Page_CreateWorldParams.cs:56-66), and PreOpen() calls it exactly once behind
    // an `initialized` flag. Patching PreOpen would fight that flag; patching
    // DoWindowContents would rewrite the value every frame and stop the owner from
    // ever dragging a slider deliberately. Reset() is the one that runs once and
    // leaves the fields public and settable afterwards.
    //
    // This PRIMES. It does not LOCK. Coverage is a button cycling a fixed set
    // {0.3, 0.5, 1.0} (PlanetCoverages, :32) rather than a slider, and 1.0 is one of
    // its three legal values - so the owner can still click it to anything the
    // unpatched game offered.
    [HarmonyPatch(typeof(Page_CreateWorldParams), "Reset")]
    public static class Patch_Page_CreateWorldParams_Reset
    {
        private static bool reported;

        // Page_CreateWorldParams.cs:16 declares `private float planetCoverage`. It is
        // NOT public - so it is set reflectively, and cached once rather than looked
        // up on every open.
        private static readonly FieldInfo CoverageField =
            AccessTools.Field(typeof(Page_CreateWorldParams), "planetCoverage");

        [HarmonyPostfix]
        public static void Postfix(Page_CreateWorldParams __instance)
        {
            if (CoverageField != null)
                CoverageField.SetValue(__instance, PlanetPresetPrimeMod.Coverage);
            else
                Log.Warning("[RimMandrake.PlanetPresetPrime] Page_CreateWorldParams.planetCoverage not found; "
                          + "coverage not primed. The field was renamed by a game update.");

            bool mlp = PrimeSubdivisions(PlanetPresetPrimeMod.Subdivisions);

            if (!reported)
            {
                reported = true;
                Log.Message(string.Format(
                    "[RimMandrake.PlanetPresetPrime] ready: coverage {0}, subdivisions {1}, MLP slider {2}",
                    PlanetPresetPrimeMod.Coverage,
                    PlanetPresetPrimeMod.Subdivisions,
                    mlp ? "primed" : "ABSENT (vanilla subdivisions set anyway)"));
            }
        }

        // Two different fields, and setting only one of them does nothing useful.
        //
        //   PlanetLayerSettingsDefOf.Surface.settings.subdivisions  is what the
        //       generator actually consumes.
        //   WorldGenRules.WorldGenRules.subcount                    is My Little
        //       Planet's slider memory. Its transpiler on DoWindowContents draws
        //       the slider FROM that field and assigns both back on every frame,
        //       so leaving it at its default 10 means the first drawn frame stamps
        //       10 over whatever we set on the vanilla side.
        //
        // So set the MLP field first and the vanilla field last: the slider then
        // reads 7 back out and re-assigns the same 7, and the two never disagree.
        //
        // MLP is reached reflectively on purpose. WorldGenRules.WorldGenRules is a
        // PRIVATE type, so a compile-time reference would need the assembly and
        // would fail at type load - taking this whole mod down - if MLP were ever
        // removed or renamed. Reflection degrades to "vanilla only" instead.
        private static bool PrimeSubdivisions(int n)
        {
            bool mlpPrimed = false;
            try
            {
                Type t = AccessTools.TypeByName("WorldGenRules.WorldGenRules");
                if (t != null)
                {
                    FieldInfo f = AccessTools.Field(t, "subcount");
                    if (f != null && f.FieldType == typeof(int))
                    {
                        f.SetValue(null, n);
                        mlpPrimed = true;
                    }
                    else
                    {
                        Log.Warning("[RimMandrake.PlanetPresetPrime] My Little Planet is present but "
                                  + "WorldGenRules.WorldGenRules.subcount is missing or not an int. "
                                  + "Its slider will stamp its own default over the planet size.");
                    }
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.PlanetPresetPrime] could not prime My Little Planet's subcount: " + e.Message);
            }

            PlanetLayerSettingsDef surface = PlanetLayerSettingsDefOf.Surface;
            if (surface != null && surface.settings != null)
                surface.settings.subdivisions = n;
            else
                Log.Warning("[RimMandrake.PlanetPresetPrime] PlanetLayerSettingsDefOf.Surface.settings is null; "
                          + "subdivisions not set.");

            return mlpPrimed;
        }
    }
}
