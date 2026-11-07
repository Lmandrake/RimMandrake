using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Patches
{
    // BEER_DIAGNOSE_NON_DRUG_3200_LOG_ERRORS: Cherry Picker (Owlchemist.CherryPicker) cuts a drug by setting
    // ingestible.drugCategory = None and stripping it from every DrugPolicyDef, but it cannot reach the DrugPolicy
    // objects inside a save. Our kill list cuts ThingDef/Beer, so a save made where Beer was still a drug (the
    // RM_TestSite_calm_v2 fixture lists it in its policies) keeps an entry for a def that is no longer a drug.
    // JobGiver_TakeDrugsForDrugPolicy then walks that entry every pawn think, and Pawn_DrugPolicyTracker logs
    // "AllowedToTakeScheduledEver on non-drug Beer" each time (3200 in session ee0fbaa8, until the Verse.Log cap hid
    // the rest). Vanilla's own PostLoadInit prunes only a null drug, so this prunes the non-drug entry beside it.
    [StaticConstructorOnStartup]
    public static class CutDrugPolicyGuardStartup
    {
        static CutDrugPolicyGuardStartup()
        {
            CutDrugPolicyGuard.Install();
        }
    }

    public static class CutDrugPolicyGuard
    {
        public const string TargetMethod = "ExposeData";
        public const string EntriesField = "entriesInt";
        public const string LogTag = "[RimMandrake Patches] cut drug in policy:";

        private static bool installed;
        public static int RemovedCount { get; private set; }

        public static string Status => !RM_PatchesSettings.cutDrugPolicyGuard
            ? "Cut-drug policy repair is off."
            : RemovedCount == 0
                ? "Cut-drug policy repair is on; no saved policy listed a cut drug."
                : "Cut-drug policy repair removed " + RemovedCount + " saved policy entries; see the log for which drugs.";

        public static void Install()
        {
            if (installed)
                return;
            installed = true;
            try
            {
                var target = AccessTools.Method(typeof(DrugPolicy), TargetMethod);
                if (target == null)
                {
                    Log.Warning("[RimMandrake Patches] DrugPolicy." + TargetMethod + " not found; cut-drug policy repair is inactive.");
                    return;
                }
                new Harmony("mandrake.rm.patches.cutdrugpolicy").Patch(target,
                    postfix: new HarmonyMethod(typeof(CutDrugPolicyGuard), nameof(Postfix)));
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake Patches] cut-drug policy repair could not patch " + TargetMethod + ": " + e.Message);
            }
        }

        public static void Postfix(DrugPolicy __instance)
        {
            if (Scribe.mode != LoadSaveMode.PostLoadInit)
                return;
            if (!RM_PatchesSettings.cutDrugPolicyGuard)
                return;
            var entries = Traverse.Create(__instance).Field(EntriesField).GetValue<List<DrugPolicyEntry>>();
            if (entries == null)
                return;
            for (int i = entries.Count - 1; i >= 0; i--)
            {
                ThingDef drug = entries[i]?.drug;
                if (drug == null || drug.IsDrug)
                    continue;
                entries.RemoveAt(i);
                RemovedCount++;
                Log.Message(LogTag + " " + drug.defName + " is no longer a drug on this mod list; removed from saved policy '"
                    + __instance.label + "'.");
            }
        }
    }
}
