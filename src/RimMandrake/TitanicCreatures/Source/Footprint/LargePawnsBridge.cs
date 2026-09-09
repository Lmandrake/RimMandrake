using System;
using System.Collections;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Verse;

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

        private static void TryReconcile()
        {
            try
            {
                Type mainType = GenTypes.GetTypeInAnyAssembly(LargePawnsMainTypeName);
                if (mainType == null)
                {
                    // Not installed/active - the mod already degrades correctly
                    // to 1x1 footprints via vanilla GenAdj.OccupiedRect, nothing
                    // further to do.
                    return;
                }

                FieldInfo settingsField = AccessTools.Field(mainType, "settings");
                object settings = settingsField?.GetValue(null);
                if (settings == null)
                {
                    Log.Warning("[RimMandrake.TitanicCreatures] LargePawns.Main found but its " +
                                "'settings' field is null or missing - skipping reconciliation, " +
                                "footprints will fall back to Large Pawns' own untouched ladder.");
                    return;
                }
                Type settingsType = settings.GetType();

                RM_TitanicTierDef tiers = TitanicTierUtility.Thresholds;
                SetFloatField(settings, settingsType, "size2Min", tiers.t1MinBodySize);
                SetFloatField(settings, settingsType, "size3Min", tiers.t2MinBodySize);
                SetFloatField(settings, settingsType, "size4Min", tiers.t3MinBodySize);

                PushOverrideRows(settings, settingsType);

                MethodInfo notifyEdited = AccessTools.Method(settingsType, "NotifyEdited");
                notifyEdited?.Invoke(settings, null);

                Log.Message("[RimMandrake.TitanicCreatures] reconciled Large Pawns' size ladder " +
                            "to our tier table (T1/T2/T3 = " + tiers.t1MinBodySize + "/" +
                            tiers.t2MinBodySize + "/" + tiers.t3MinBodySize + ").");
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.TitanicCreatures] Large Pawns reconciliation failed " +
                             "(mod likely updated past the decompile this was built against) - " +
                             "continuing with its own untouched ladder. " + e);
            }
        }

        private static void SetFloatField(object instance, Type type, string fieldName, float value)
        {
            FieldInfo field = AccessTools.Field(type, fieldName);
            if (field == null)
            {
                throw new MissingFieldException(type.FullName, fieldName);
            }
            field.SetValue(instance, value);
        }

        /// <summary>
        /// Pushes one SizeOverride row per race carrying an explicit
        /// RM_TitanicExtension.forceEnabled - both directions, per the item's
        /// own read of Large Pawns' resolution order (size 1 = force 1x1
        /// opt-out; 2-4 = force that size opt-in, consulted before bodySize).
        /// Races with no override (the common case: auto by bodySize) are left
        /// alone - Large Pawns' own bodySize thresholds now match ours from
        /// SetFloatField above, so its default resolution already agrees.
        /// </summary>
        private static void PushOverrideRows(object settings, Type settingsType)
        {
            FieldInfo overridesField = AccessTools.Field(settingsType, "sizeOverrides");
            IList overrides = overridesField?.GetValue(settings) as IList;
            Type sizeOverrideType = GenTypes.GetTypeInAnyAssembly(SizeOverrideTypeName);
            if (overrides == null || sizeOverrideType == null)
            {
                Log.Warning("[RimMandrake.TitanicCreatures] Large Pawns' sizeOverrides table or " +
                             "SizeOverride type not found - per-def overrides will not propagate " +
                             "to it (bodySize-based thresholds still were).");
                return;
            }
            FieldInfo defNameField = AccessTools.Field(sizeOverrideType, "defName");
            FieldInfo sizeField = AccessTools.Field(sizeOverrideType, "size");

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

                int desiredSize;
                if (ext.forceEnabled == false)
                {
                    desiredSize = 1;
                }
                else
                {
                    // Forced-in: our own tier ladder decides the actual size
                    // (GetTier floors at T1 when there's no natural bodySize
                    // qualification); Large Pawns' hard ceiling is 4, matching
                    // our own T3 footprint cap (item's own ⚠️: "4x4 is its hard
                    // ceiling").
                    TitanicTier tier = TitanicTierUtility.DefQualifies(raceDef)
                        ? TierForBodySize(raceDef.race.baseBodySize)
                        : TitanicTier.T1;
                    desiredSize = FootprintSizeFor(tier);
                }

                object row = overrides.Cast<object>()
                    .FirstOrDefault(o => (string)defNameField.GetValue(o) == raceDef.defName);
                if (row == null)
                {
                    row = Activator.CreateInstance(sizeOverrideType);
                    defNameField.SetValue(row, raceDef.defName);
                    overrides.Add(row);
                }
                sizeField.SetValue(row, desiredSize);
            }
        }

        private static TitanicTier TierForBodySize(float bodySize)
        {
            RM_TitanicTierDef t = TitanicTierUtility.Thresholds;
            if (bodySize >= t.t3MinBodySize)
            {
                return TitanicTier.T3;
            }
            if (bodySize >= t.t2MinBodySize)
            {
                return TitanicTier.T2;
            }
            return TitanicTier.T1;
        }

        private static int FootprintSizeFor(TitanicTier tier)
        {
            switch (tier)
            {
                case TitanicTier.T3:
                    return 4; // Large Pawns' hard ceiling - see the ⚠️ above.
                case TitanicTier.T2:
                    return 3;
                default:
                    return 2;
            }
        }
    }
}
