using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Patches
{
    // QUICKTEST_POLICY_NRE_FULLLIST_1: vanilla ReadingPolicyDatabase.GenerateStartingPolicies (run by every Game..ctor:
    // new game, quicktest, LoadGame) calls item.thingClass.SameOrSubclassOf<Book>() on EVERY ThingDef with no null check
    // (decomp rw16 RimWorld/ReadingPolicyDatabase.cs:76). One ThingDef with a null thingClass anywhere on the list (an
    // unresolved ParentName, a stale DLL, a def missing the field) therefore NREs every game start, and the only clue is
    // vanilla's "has null thingClass." config error buried in a long log. Seen four times (RSW_*Juv, RUT_Webwork_*, a stale
    // FlowWorks DLL, the 613-mod list).
    //
    // This guard repairs each such def to a safe class (race -> Pawn, comps -> ThingWithComps, else Thing) and logs ONE
    // error per def naming the def, its mod and its file, so the game starts and the log isolates the mod. It runs at
    // StaticConstructorOnStartup and again as a prefix on GenerateStartingPolicies (catches defs added after startup).
    // The def is still broken: the error stays red so it is fixed at its source.
    [StaticConstructorOnStartup]
    public static class NullThingClassGuardStartup
    {
        static NullThingClassGuardStartup()
        {
            NullThingClassGuard.Install();
            NullThingClassGuard.Repair("startup");
        }
    }

    public static class NullThingClassGuard
    {
        public const string TargetType = "RimWorld.ReadingPolicyDatabase";
        public const string TargetMethod = "GenerateStartingPolicies";
        public const string LogTag = "[RimMandrake Patches] null thingClass:";

        private static bool installed;
        private static readonly HashSet<string> reported = new HashSet<string>();
        public static int RepairedCount { get; private set; }

        public static string Status => !RM_PatchesSettings.nullThingClassGuard
            ? "Null-thingClass guard is off."
            : RepairedCount == 0
                ? "Null-thingClass guard is on; no broken ThingDef found."
                : "Null-thingClass guard repaired " + RepairedCount + " ThingDef(s); see the log for which mod.";

        public static void Install()
        {
            if (installed)
                return;
            installed = true;
            try
            {
                var target = AccessTools.Method(typeof(ReadingPolicyDatabase), TargetMethod);
                if (target == null)
                {
                    Log.Warning("[RimMandrake Patches] " + TargetType + "." + TargetMethod + " not found; null-thingClass guard runs at startup only.");
                    return;
                }
                new Harmony("mandrake.rm.patches.nullthingclass").Patch(target,
                    prefix: new HarmonyMethod(typeof(NullThingClassGuard), nameof(Prefix)));
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake Patches] null-thingClass guard could not patch " + TargetMethod + ": " + e.Message);
            }
        }

        public static void Prefix() => Repair("game start");

        // The class a broken def falls back to. Pure, so the choice is the same at both call sites.
        public static Type FallbackClass(bool isRace, bool hasComps)
        {
            if (isRace)
                return typeof(Pawn);
            return hasComps ? typeof(ThingWithComps) : typeof(Thing);
        }

        public static void Repair(string when)
        {
            if (!RM_PatchesSettings.nullThingClassGuard)
                return;
            List<ThingDef> defs = DefDatabase<ThingDef>.AllDefsListForReading;
            for (int i = 0; i < defs.Count; i++)
            {
                ThingDef def = defs[i];
                if (def == null || def.thingClass != null)
                    continue;
                def.thingClass = FallbackClass(def.race != null, def.comps != null && def.comps.Count > 0);
                RepairedCount++;
                if (reported.Add(def.defName ?? "?"))
                {
                    Log.Error(LogTag + " ThingDef " + (def.defName ?? "?") +
                              " from mod '" + (def.modContentPack?.Name ?? "?") + "' (" + (def.modContentPack?.PackageId ?? "?") +
                              "), file " + (def.fileName ?? "?") + ", has no thingClass; set to " + def.thingClass.Name +
                              " at " + when + " so the game can start. Fix the def (often an unresolved ParentName or a stale deploy).");
                }
            }
        }
    }
}
