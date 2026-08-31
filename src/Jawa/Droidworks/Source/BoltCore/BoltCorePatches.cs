using System;
using System.Reflection;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Harmony bootstrap for the restraining-bolt core (DROIDWORKS_BOLT_CORE_1).
    /// Runs unconditionally at startup - unlike JawaIonVehicleTierMod's own
    /// AppDomain probe for an optional dependency (Vehicle Framework),
    /// MentalBreakWorker is a base-game type that always exists, so there is
    /// nothing to probe for here. The one thing that CAN be legitimately
    /// missing is the RSW_DW_RestrainingBolt HediffDef itself (RimMandrake.StarWars.Droidworks not
    /// installed, or a future rename) - BoltCorePatches.Prefix degrades
    /// quietly for that case rather than throwing.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class DroidworksBoltCoreMod
    {
        static DroidworksBoltCoreMod()
        {
            try
            {
                BoltCorePatches.Apply(new Harmony("mandrake.rsw.droidworks.boltcore"));
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.StarWars.RimMandrake.StarWars.Droidworks] Failed to apply restraining-bolt patches: " + ex);
            }
        }
    }

    /// <summary>
    /// DROIDWORKS_BOLT_CORE_1 - suppresses mental breaks while a pawn carries
    /// RSW_DW_RestrainingBolt, copying the EXACT mechanism design/Jawa/
    /// droid_ruling.md section 3 documents for OuterRim's own restraint bolt:
    /// "A Harmony prefix on MentalBreakWorker.BreakCanOccur returns false
    /// while it is fitted." ("Asimov's own" per the item brief - Droid
    /// Depot's Asimov-framework dependency, Neronix17.Asimov, is what ships
    /// the mental-break-suppression convention this copies; the prefix itself
    /// is OuterRimDroids' own code, not literally in the Asimov assembly, but
    /// the pattern - and the field shape on the hediff it gates - both come
    /// from that mod family.)
    ///
    /// Looked up by defName via DefDatabase&lt;HediffDef&gt;.GetNamedSilentFail
    /// rather than a hard reference to the main RimMandrake.StarWars.Droidworks.dll (net472) -
    /// this sub-project is net48 (see csproj header) and stays load-order
    /// independent of it, same reasoning VehicleIonPatches.cs uses for
    /// reading IonDamageDef's empAmountDroid field by reflection instead of
    /// referencing RimMandrake.StarWars.JawaIonWeapons.dll.
    /// </summary>
    public static class BoltCorePatches
    {
        private const string BoltHediffDefName = "RSW_DW_RestrainingBolt";

        private static HediffDef _boltDefCache;
        private static bool _boltDefResolved;

        public static void Apply(Harmony harmony)
        {
            MethodInfo breakCanOccur = AccessTools.Method(typeof(MentalBreakWorker),
                nameof(MentalBreakWorker.BreakCanOccur));
            if (breakCanOccur == null)
            {
                Log.Error("[RimMandrake.StarWars.RimMandrake.StarWars.Droidworks] MentalBreakWorker.BreakCanOccur not found by "
                    + "reflection - vanilla API has moved. Restraining-bolt break suppression not applied.");
                return;
            }

            harmony.Patch(breakCanOccur,
                prefix: new HarmonyMethod(typeof(BoltCorePatches), nameof(Prefix)));
        }

        /// <summary>
        /// Runs BEFORE the vanilla/any-other-mod break-eligibility check.
        /// Returning false from a Harmony prefix skips the original entirely
        /// and whatever this method wrote into __result stands as the
        /// method's return value - so a bolted pawn never even reaches the
        /// break-specific logic of whichever MentalBreakWorker asked.
        /// </summary>
        public static bool Prefix(Pawn pawn, ref bool __result)
        {
            if (pawn?.health?.hediffSet == null) return true;

            HediffDef boltDef = BoltDef;
            if (boltDef == null) return true; // RimMandrake.StarWars.Droidworks not loaded / def missing - degrade quietly

            if (!pawn.health.hediffSet.HasHediff(boltDef)) return true;

            __result = false;
            return false;
        }

        private static HediffDef BoltDef
        {
            get
            {
                if (!_boltDefResolved)
                {
                    _boltDefCache = DefDatabase<HediffDef>.GetNamedSilentFail(BoltHediffDefName);
                    _boltDefResolved = true;
                }
                return _boltDefCache;
            }
        }
    }
}
