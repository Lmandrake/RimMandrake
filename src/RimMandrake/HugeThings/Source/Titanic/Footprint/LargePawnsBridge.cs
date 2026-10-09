using System;
using System.Collections;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Soft integration with neku.largepawns (workshop 3777700657) per the
    /// item's decompile verdict ("ride-with-config"): reconciles ITS size
    /// thresholds and per-def override table to match OURS, so our tier table
    /// stays the single authority ("no second size ladder live" - item verify
    /// checklist) instead of the two mods disagreeing about who is titanic.
    ///
    /// Deliberately reflection-only, never a hard dependency: no compile-time
    /// reference to LargePawns.dll exists anywhere in this project, so the mod
    /// loads and works (at 1x1 footprint) with Large Pawns absent, disabled, or
    /// updated to a build whose internals have moved - this method simply logs
    /// a warning and no-ops rather than throwing.
    ///
    /// ⚠️ UNVERIFIED AGAINST A RUNNING GAME (explicitly CANNOT DO for this
    /// build - no bridge/game access). Every member name below
    /// (LargePawns.Main.settings, Settings.size2Min/size3Min/size4Min,
    /// sizeOverrides, SizeOverride.defName/.size, NotifyEdited()) is read
    /// directly off the IL decompile in
    /// design/Jawa/worldbuilding/research/large_pawns_decompile_2026-09-09.md
    /// (mod version 0.24.16) - not guessed - but a decompile of the DLL on
    /// disk is not proof of runtime behaviour, and a future Large Pawns update
    /// could rename any of it. The live quicktest that closes this out is
    /// listed in that item's own verify section.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class LargePawnsBridge
    {
        private const string LargePawnsMainTypeName = "LargePawns.Main";
        private const string SizeOverrideTypeName = "LargePawns.SizeOverride";

        static LargePawnsBridge()
        {
            // Deferred to after the long "Initializing" event (defs loaded,
            // EVERY [StaticConstructorOnStartup] type - including Large
            // Pawns' own Main, which populates its per-def table in its cctor
            // - has already run) so ordering against Large Pawns' own startup
            // work never depends on assembly/type scan order between mods.
            LongEventHandler.ExecuteWhenFinished(TryReconcile);
        }

        private static readonly string[] ClearingFields = { "pathClearingManhunter", "pathClearingBerserk", "pathClearingAIFight" };

        /// <summary>
        /// LARGEPAWNS_BRIDGE_HARDENING_1 (B3.16): every member is resolved BEFORE anything is written; the ladder, the clearing bools and
        /// the override rows are snapshotted, applied, and rolled back whole on any throw, and success is logged only after
        /// NotifyEdited ran. (B3.15): Large Pawns' own PathClearingUtility wall-break (three bools) is forced off, so the curated crush
        /// table is the only destruction authority (TITANIC_CREATURES_MOD_1 card #3); its own toggle.
        /// B3.17, Large Pawns' size precedence (decompile 0.24.16): an override row of 1..4 beats body size outright, so a force-in
        /// row pins the footprint at the adult-projected size while our runtime tier follows the pawn's current BodySize.
        /// </summary>
        private static void TryReconcile()
        {
            // Mod Settings (restart): giant animals off, or the Large Pawns footprint off, leaves Large Pawns' own ladder untouched.
            if (!RM_HugeThingsSettings.LargePawnsFootprintActive) return;
            Type mainType = GenTypes.GetTypeInAnyAssembly(LargePawnsMainTypeName);
            if (mainType == null)
            {
                // Not installed/active - footprints degrade to 1x1 via vanilla GenAdj.OccupiedRect.
                return;
            }

            // ---- resolve (no writes) ----
            object settings = AccessTools.Field(mainType, "settings")?.GetValue(null);
            if (settings == null)
            {
                Log.Warning("[RimMandrake.TitanicCreatures] LargePawns.Main found but its 'settings' field is null or missing - " +
                            "nothing changed; footprints follow Large Pawns' own untouched ladder.");
                return;
            }
            Type settingsType = settings.GetType();
            FieldInfo s2 = AccessTools.Field(settingsType, "size2Min");
            FieldInfo s3 = AccessTools.Field(settingsType, "size3Min");
            FieldInfo s4 = AccessTools.Field(settingsType, "size4Min");
            FieldInfo overridesField = AccessTools.Field(settingsType, "sizeOverrides");
            IList overrides = overridesField?.GetValue(settings) as IList;
            Type sizeOverrideType = GenTypes.GetTypeInAnyAssembly(SizeOverrideTypeName);
            FieldInfo defNameField = sizeOverrideType == null ? null : AccessTools.Field(sizeOverrideType, "defName");
            FieldInfo sizeField = sizeOverrideType == null ? null : AccessTools.Field(sizeOverrideType, "size");
            MethodInfo notifyEdited = AccessTools.Method(settingsType, "NotifyEdited");
            FieldInfo[] clearing = ClearingFields.Select(n => AccessTools.Field(settingsType, n)).ToArray();
            bool clearingWanted = RM_HugeThingsSettings.largePawnsClearingOff;
            var missing = new System.Collections.Generic.List<string>();
            if (s2 == null || s2.FieldType != typeof(float)) missing.Add("size2Min");
            if (s3 == null || s3.FieldType != typeof(float)) missing.Add("size3Min");
            if (s4 == null || s4.FieldType != typeof(float)) missing.Add("size4Min");
            if (overrides == null) missing.Add("sizeOverrides");
            if (defNameField == null || sizeField == null) missing.Add("SizeOverride.defName/size");
            if (notifyEdited == null) missing.Add("NotifyEdited()");
            if (clearingWanted)
                for (int i = 0; i < clearing.Length; i++)
                    if (clearing[i] == null || clearing[i].FieldType != typeof(bool)) missing.Add(ClearingFields[i]);
            if (missing.Count > 0)
            {
                Log.Warning("[RimMandrake.TitanicCreatures] Large Pawns reconciliation skipped, nothing changed (mod likely updated past " +
                            "the decompile this was built against); missing: " + string.Join(", ", missing.ToArray()));
                return;
            }

            // ---- snapshot ----
            float old2 = (float)s2.GetValue(settings), old3 = (float)s3.GetValue(settings), old4 = (float)s4.GetValue(settings);
            bool[] oldClearing = clearingWanted ? clearing.Select(f => (bool)f.GetValue(settings)).ToArray() : null;
            int oldCount = overrides.Count;
            var oldSizes = new System.Collections.Generic.List<object>(oldCount);
            foreach (object row in overrides) oldSizes.Add(row == null ? null : sizeField.GetValue(row));

            // ---- apply ----
            RM_TitanicTierDef tiers = TitanicTierUtility.Thresholds;
            try
            {
                s2.SetValue(settings, tiers.t1MinBodySize);
                s3.SetValue(settings, tiers.t2MinBodySize);
                s4.SetValue(settings, tiers.t3MinBodySize);
                if (clearingWanted)
                    foreach (FieldInfo f in clearing) f.SetValue(settings, false);
                PushOverrideRows(overrides, sizeOverrideType, defNameField, sizeField);
                notifyEdited.Invoke(settings, null);
            }
            catch (Exception e)
            {
                try
                {
                    s2.SetValue(settings, old2);
                    s3.SetValue(settings, old3);
                    s4.SetValue(settings, old4);
                    if (clearingWanted)
                        for (int i = 0; i < clearing.Length; i++) clearing[i].SetValue(settings, oldClearing[i]);
                    while (overrides.Count > oldCount) overrides.RemoveAt(overrides.Count - 1);
                    for (int i = 0; i < oldCount; i++)
                        if (overrides[i] != null && oldSizes[i] != null) sizeField.SetValue(overrides[i], oldSizes[i]);
                    notifyEdited.Invoke(settings, null);
                    Log.Warning("[RimMandrake.TitanicCreatures] Large Pawns reconciliation failed and was rolled back; its own ladder " +
                                "stands. " + e);
                }
                catch (Exception e2)
                {
                    Log.Error("[RimMandrake.TitanicCreatures] Large Pawns reconciliation failed AND its rollback failed; its settings " +
                              "may be partly edited for this session (nothing was written to disk by us). First: " + e + " Rollback: " + e2);
                }
                return;
            }

            Log.Message("[RimMandrake.TitanicCreatures] reconciled Large Pawns' size ladder to our tier table (T1/T2/T3 = " +
                        tiers.t1MinBodySize + "/" + tiers.t2MinBodySize + "/" + tiers.t3MinBodySize + "); its path-clearing wall-break " +
                        (clearingWanted
                            ? "forced OFF (" + string.Join(", ", ClearingFields.Select((n, i) => n + "=" + clearing[i].GetValue(settings)).ToArray()) + ")."
                            : "left as Large Pawns has it (setting off)."));
        }

        /// <summary>
        /// Pushes one SizeOverride row per race carrying an explicit
        /// RM_TitanicExtension.forceEnabled - both directions, per the item's
        /// own read of Large Pawns' resolution order (size 1 = force 1x1
        /// opt-out; 2-4 = force that size opt-in, consulted before bodySize).
        /// Races with no override (the common case: auto by bodySize) are left
        /// alone - Large Pawns' own bodySize thresholds now match ours, so its
        /// default resolution already agrees.
        /// </summary>
        private static void PushOverrideRows(IList overrides, Type sizeOverrideType, FieldInfo defNameField, FieldInfo sizeField)
        {
            foreach (ThingDef raceDef in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (raceDef.race == null)
                {
                    continue;
                }
                RM_TitanicExtension ext = raceDef.GetModExtension<RM_TitanicExtension>();
                if (ext == null || ext.forceEnabled == null)
                {
                    continue;
                }

                int desiredSize = RM_TitanicKernel.OverrideFootprint(raceDef.race.baseBodySize,
                    TitanicTierUtility.Thresholds.t1MinBodySize, TitanicTierUtility.Thresholds.t2MinBodySize,
                    TitanicTierUtility.Thresholds.t3MinBodySize, TitanicTierUtility.ForceOf(ext));

                object row = overrides.Cast<object>()
                    .FirstOrDefault(o => o != null && (string)defNameField.GetValue(o) == raceDef.defName);
                if (row == null)
                {
                    row = Activator.CreateInstance(sizeOverrideType);
                    defNameField.SetValue(row, raceDef.defName);
                    overrides.Add(row);
                }
                sizeField.SetValue(row, desiredSize);
            }
        }
    }
}
