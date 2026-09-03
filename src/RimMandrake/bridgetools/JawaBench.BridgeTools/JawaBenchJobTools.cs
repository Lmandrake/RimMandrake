// JawaBenchJobTools.cs - Jobs/work/schedules and Zones/stockpiles/bills/areas.
//
// WHY THIS FILE EXISTS
// =====================
// `BRIDGE_TOOLS_EASY_BLOCK_1`, ten of the 74 EASY capabilities the owner's cull
// left open (`design/Jawa/bridge/dll_capability_roster.html`). Two domains, ten
// rows:
//   Zones/bills   set-crop, configure-bill, new-allowed-area, paint areas
//   Jobs/work     ordered-job, stop/clear queue, set-work-priority,
//                 draft/fire-at-will, timetable, player settings
//
// Every signature below was read out of 1.6 source with mcp__rimsage, not
// guessed:
//   RimWorld.IPlantToGrowSettable.SetPlantDefToGrow/GetPlantDefToGrow
//       - implemented by BOTH Zone_Growing and Building_PlantGrower, so one
//         tool covers the roster's "also Building_PlantGrower" warn for free.
//   RimWorld.Bill_Production.repeatMode/.repeatCount/.targetCount/.qualityRange
//   RimWorld.Bill.GetStoreMode()/SetStoreMode(BillStoreModeDef, ISlotGroup)
//   Verse.AreaManager.TryMakeNewAllowed(out Area_Allowed)  - Verse/AreaManager.cs:147.
//       ⚠️ `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` calls this absent.
//       It is not. Read the source, not the older doc.
//   Verse.AreaManager.Home/.BuildRoof/.NoRoof/.SnowOrSandClear/.PollutionClear,
//       Verse.Area indexer (this[IntVec3]) and Area.Clear()
//   Verse.AI.Pawn_JobTracker.TryTakeOrderedJob(Job, JobTag?, bool)/
//       .StopAll(bool,bool)/.EndCurrentJob(JobCondition,bool,bool)/
//       .ClearQueuedJobs(bool)/.IsCurrentJobPlayerInterruptible()
//   RimWorld.Pawn_WorkSettings.SetPriority(WorkTypeDef,int)/GetPriority(WorkTypeDef)
//   RimWorld.Pawn_DraftController.Drafted/.FireAtWill
//   Verse.AI.Group.LordUtility.GetLord(this Pawn) + Verse.AI.Group.Lord.AllowsDrafting(Pawn)
//   RimWorld.Pawn_TimetableTracker.SetAssignment(int, TimeAssignmentDef)
//   RimWorld.Pawn_PlayerSettings.AreaRestrictionInPawnCurrentMap/.Master/
//       .medCare/.hostilityResponse
//
// 🔴 WHY THE READ-BACK IS THE WHOLE TOOL, IN THIS FILE MORE THAN MOST.
// Several of the writes above are SILENT no-ops by design, not by bug:
//   - Pawn_WorkSettings.GetPriority returns 3 for every ACTIVE work type when
//     Find.PlaySettings.useWorkPriorities is false, no matter what was
//     actually written. jawa/set_work_priority reports that flag alongside
//     the read-back so a caller cannot mistake "reads 3" for "priority 3".
//   - Pawn_WorkSettings.SetPriority itself refuses (Log.Error, priorities[w]
//     left untouched) when priority != 0 and the work type is disabled for
//     that pawn. Checked BEFORE writing, reported either way.
//   - Pawn_JobTracker.TryTakeOrderedJob (Verse/AI/Pawn_JobTracker.cs:891) returns
//     false for exactly ONE reason: job.TryMakePreToilReservations failed. When
//     IsCurrentJobPlayerInterruptible() is false it does NOT refuse - it falls
//     through to ClearQueuedJobs + EnqueueLast and returns TRUE, so the order
//     runs after the current job instead of replacing it. jawa/ordered_job reports
//     both, because a caller told "refused" would go hunting for a fire.
//   - Pawn_DraftController.Drafted has no refusal path of its own; the game's
//     OWN drafting gizmo is disabled by Lord.AllowsDrafting(pawn) before the
//     setter is ever called, so jawa/set_draft checks that AcceptanceReport
//     itself and refuses the same way the UI does, with the same reason
//     string, instead of setting Drafted and leaving a Lord to fight it.
//   - Pawn_TimetableTracker.SetAssignment writes the 24-slot array
//     unconditionally, but CurrentAssignment - what the pawn actually obeys -
//     is hard-coded to Anything for non-colonists and prisoners
//     (Pawn_TimetableTracker.cs:16). The write "succeeds" and does nothing;
//     jawa/timetable says so.
//   - Pawn_PlayerSettings.Master's setter is a Log.ErrorOnce-and-return when
//     the candidate pawn has not learned the Obedience trainable - read back
//     and compared, never assumed.
//   - Pawn_PlayerSettings.AreaRestrictionInPawnCurrentMap's setter keys off
//     pawn.MapHeld; when that is null (pawn not spawned or carried on no
//     spawned map) the dictionary write never happens. Checked first.
//
// THREAD AFFINITY: same rule as every other file here. Everything that
// touches game state is inside ctx.MainThread.InvokeAsync; nothing else is.
// jawa/ordered_job additionally waits real game TICKS between issuing the
// order and reading back curJob, the same reason jawa/order_pawn does -
// TryTakeOrderedJob returning true means "enqueued", not "running".

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimBridgeServer.Sdk;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // =====================================================================
        // Shared lookups
        // =====================================================================

        /// <summary>A growing zone OR a plant-growing building at a target
        /// (ThingID / zone label) or a cell. Both implement
        /// IPlantToGrowSettable, so one lookup covers both roster rows.</summary>
        private static IPlantToGrowSettable ResolvePlantSettable(
            Map map, string target, int x, int z, out string err)
        {
            err = null;
            if (!string.IsNullOrWhiteSpace(target))
            {
                var id = target.Trim();
                var thing = map.listerThings.AllThings.FirstOrDefault(
                    t => string.Equals(t.ThingID, id, StringComparison.OrdinalIgnoreCase));
                if (thing is IPlantToGrowSettable fromThing) return fromThing;

                var zone = map.zoneManager.AllZones.FirstOrDefault(
                    z2 => string.Equals(z2.label, id, StringComparison.OrdinalIgnoreCase));
                if (zone is IPlantToGrowSettable fromZone) return fromZone;

                err = thing != null
                    ? $"'{id}' is a {thing.GetType().Name}, which does not implement " +
                      "IPlantToGrowSettable (not a growing zone or a plant-growing building)."
                    : zone != null
                        ? $"Zone '{id}' is a {zone.GetType().Name}, not a growing zone."
                        : $"No spawned thing or zone named '{id}' on this map.";
                return null;
            }

            if (x >= 0 && z >= 0)
            {
                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(map)) { err = $"({x},{z}) is outside the map."; return null; }
                var zoneAt = map.zoneManager.ZoneAt(c);
                if (zoneAt is IPlantToGrowSettable zoneSettable) return zoneSettable;
                var thingAt = map.thingGrid.ThingsListAt(c)
                    .FirstOrDefault(t => t is IPlantToGrowSettable);
                if (thingAt is IPlantToGrowSettable thingSettable) return thingSettable;
                err = $"No growing zone or plant-growing building at ({x},{z}).";
                return null;
            }

            err = "Give either 'target' (a growing zone label or plant-growing " +
                  "building ThingID) or 'x'/'z' (a cell).";
            return null;
        }

        /// <summary>A standard keyword ("home"/"roof"/"noroof"/"snow"/"pollution")
        /// or the exact label of any area on the map, allowed areas included.</summary>
        private static Area ResolveAreaByKindOrLabel(Map map, string spec, out string err)
        {
            err = null;
            var s = (spec ?? "").Trim();
            if (s.Length == 0) { err = "No area given."; return null; }
            switch (s.ToLowerInvariant())
            {
                case "home": return map.areaManager.Home;
                case "roof": case "buildroof": return map.areaManager.BuildRoof;
                case "noroof": return map.areaManager.NoRoof;
                case "snow": case "snoworsandclear": return map.areaManager.SnowOrSandClear;
                case "pollution": case "pollutionclear":
                    var pc = map.areaManager.PollutionClear;
                    if (pc == null) err = "PollutionClear area is null - Biotech is not active.";
                    return pc;
            }
            var byLabel = map.areaManager.AllAreas.FirstOrDefault(
                a => string.Equals(a.Label, s, StringComparison.OrdinalIgnoreCase));
            if (byLabel != null) return byLabel;
            err = $"No area named '{s}'. Standard kinds: home, roof, noroof, snow, " +
                  "pollution. Or the exact label of an existing Allowed area - " +
                  "jawa/new_allowed_area makes one.";
            return null;
        }

        /// <summary>A storage building or stockpile zone's ISlotGroup, by ThingID
        /// or zone label, for Bill_Production.SetStoreMode(SpecificStockpile,...).</summary>
        private static ISlotGroup ResolveSlotGroup(Map map, string spec, out string err)
        {
            err = null;
            var s = (spec ?? "").Trim();
            if (s.Length == 0)
            {
                err = "storeTargetId is required when storeMode is 'specificstockpile' " +
                      "(a storage building ThingID or a stockpile zone label).";
                return null;
            }
            var thing = map.listerThings.AllThings.FirstOrDefault(
                t => string.Equals(t.ThingID, s, StringComparison.OrdinalIgnoreCase));
            if (thing is ISlotGroupParent sgpThing) return sgpThing.GetSlotGroup();

            var zone = map.zoneManager.AllZones.FirstOrDefault(
                z => string.Equals(z.label, s, StringComparison.OrdinalIgnoreCase));
            if (zone is ISlotGroupParent sgpZone) return sgpZone.GetSlotGroup();

            err = $"No storage building or stockpile zone matching '{s}' " +
                  "(checked spawned ThingIDs and zone labels).";
            return null;
        }

        private static bool TryParseRepeatMode(string s, out BillRepeatModeDef def)
        {
            switch ((s ?? "").Trim().ToLowerInvariant())
            {
                case "repeatcount": def = BillRepeatModeDefOf.RepeatCount; return true;
                case "targetcount": def = BillRepeatModeDefOf.TargetCount; return true;
                case "forever": def = BillRepeatModeDefOf.Forever; return true;
                default: def = null; return false;
            }
        }

        private static bool TryParseStoreMode(string s, out BillStoreModeDef def)
        {
            switch ((s ?? "").Trim().ToLowerInvariant())
            {
                case "dropfloor": case "dropanywhere": def = BillStoreModeDefOf.DropOnFloor; return true;
                case "beststockpile": def = BillStoreModeDefOf.BestStockpile; return true;
                case "specificstockpile": def = BillStoreModeDefOf.SpecificStockpile; return true;
                default: def = null; return false;
            }
        }

        /// <summary>A ThingID or cell (x/z), as a LocalTargetInfo. Returns null
        /// with err==null when NEITHER was given (a valid "no target"), and null
        /// with err set when one was given but could not be resolved.</summary>
        private static LocalTargetInfo? ResolveTarget(
            Map map, string thingId, int x, int z, out string err)
        {
            err = null;
            if (!string.IsNullOrWhiteSpace(thingId))
            {
                var id = thingId.Trim();
                var t = map.listerThings.AllThings.FirstOrDefault(
                    th => string.Equals(th.ThingID, id, StringComparison.OrdinalIgnoreCase));
                if (t == null) { err = $"No spawned thing on this map with id '{id}'."; return null; }
                return new LocalTargetInfo(t);
            }
            if (x >= 0 && z >= 0)
            {
                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(map)) { err = $"({x},{z}) is outside the map."; return null; }
                return new LocalTargetInfo(c);
            }
            return null;
        }

        // =====================================================================
        // jawa/set_crop - Zone_Growing / Building_PlantGrower . SetPlantDefToGrow
        // =====================================================================

        [Tool(
            "jawa/set_crop",
            Description =
                "Set what a growing zone or a plant-growing building (hydroponics basin " +
                "etc.) will plant next - IPlantToGrowSettable.SetPlantDefToGrow, the call " +
                "behind the in-game 'Select crop' gizmo. This is NOT jawa/set_plants: that " +
                "tool spawns actual Plant things on the map right now; this one only " +
                "changes what an existing zone or building sows going forward. Address the " +
                "target by growing-zone label or building ThingID ('target'), or by a cell " +
                "inside it ('x'/'z') when you don't know the label.",
            ResultDescription =
                "success is GetPlantDefToGrow() reading back the def you asked for, never " +
                "the fact that SetPlantDefToGrow was called. Also kind (Zone_Growing or " +
                "Building_PlantGrower), identity (zone label or ThingID), and " +
                "canAcceptSowNow (false on an unpowered hydroponics basin).")]
        public static async Task<object> SetCrop(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "A growing zone's label, or a plant-growing building's ThingID. " +
                "Omit and give x/z instead to address by cell.")]
            string target = null,
            [ToolParameter(Description = "Cell X, if not addressing by 'target'.", DefaultValue = -1)]
            int x = -1,
            [ToolParameter(Description = "Cell Z, if not addressing by 'target'.", DefaultValue = -1)]
            int z = -1,
            [ToolParameter(Description = "ThingDef of the plant to grow, e.g. Plant_Potato.")]
            string plantDef = null)
        {
            if (string.IsNullOrWhiteSpace(plantDef))
                return Fail("plantDef is required, e.g. 'Plant_Potato'.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string err;
                var settable = ResolvePlantSettable(map, target, x, z, out err);
                if (settable == null) return Fail(err);

                var def = DefDatabase<ThingDef>.GetNamedSilentFail(plantDef.Trim());
                if (def == null)
                    return Fail($"Unknown ThingDef '{plantDef}'.");
                if (def.plant == null)
                    return Fail($"ThingDef '{def.defName}' is not a plant (no plant properties) - a grower set to it will never sow.");

                settable.SetPlantDefToGrow(def);
                var readBack = settable.GetPlantDefToGrow();

                // 🔴 SET_CROP_NO_SOWTAG_CHECK_1 (2026-09-03 sonnet fallback review).
                // PlantUtility.CanSowOnGrower (RimWorld/PlantUtility.cs:284) is a UI-only
                // filter - it gates Command_SetPlantToGrow's float-menu options, nothing
                // else. Zone_Growing.SetPlantDefToGrow / Building_PlantGrower.SetPlantDefToGrow
                // both just store the field with NO validation; CanAcceptSowNow() never checks
                // it either (Zone_Growing's is a bare `return true`); and neither
                // WorkGiver_GrowerSow nor JobDriver_PlantSow re-check it downstream - both only
                // call ThingDef.CanNowPlantAt (fertility/temperature/terrain/blocking), which
                // also skips it. So an incompatible assignment is NOT refused anywhere in the
                // engine and WILL actually grow: a plant with an empty sowTags list
                // (PlantProperties.Sowable => !sowTags.NullOrEmpty(), true of most wild-only
                // flora) or one missing this grower's tag (a soil-only crop set on a hydroponics
                // basin, or the reverse) quietly sows something the game's own UI would never
                // offer. Reported here, not blocked - this tool already exposes more than the
                // UI does elsewhere (see jawa/new_allowed_area's header note).
                var sowTagCompatible = PlantUtility.CanSowOnGrower(def, settable);

                return new
                {
                    success = readBack == def,
                    requested = def.defName,
                    readBack = readBack?.defName,
                    kind = settable.GetType().Name,
                    identity = settable is Zone zn ? zn.label
                        : settable is Thing th ? th.ThingID : null,
                    canAcceptSowNow = settable.CanAcceptSowNow(),
                    sowTagCompatible,
                    note = !sowTagCompatible
                        ? $"CanSowOnGrower is false for '{def.defName}' on this " +
                          $"{settable.GetType().Name} - the game's own crop-select menu would " +
                          "never offer this combination (wrong sowTag for this grower type, or " +
                          "the plant is not player-sowable at all). Nothing in the engine " +
                          "actually refuses it though: it will grow anyway. This is a real gap " +
                          "in what the UI would let you choose, not a failed write."
                        : null,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/configure_bill - Bill_Production repeatMode/targetCount/
        //                       SetStoreMode/qualityRange
        // =====================================================================

        [Tool(
            "jawa/configure_bill",
            Description =
                "Configure a production bill already on a workbench's bill stack: repeat " +
                "mode, repeat/target count, store mode (including a specific stockpile), " +
                "and the quality band. Address the workbench by ThingID and the bill either " +
                "by index (0-based, as shown in-game) or by the RecipeDef it runs (first " +
                "match). Only the fields you pass are changed. This does not ADD a bill.",
            ResultDescription =
                "Every field read back off the Bill_Production after writing, never assumed " +
                "from the call succeeding. suspended/repeatCount/targetCount/repeatMode/ " +
                "storeMode/qualityRange as they now stand.")]
        public static async Task<object> ConfigureBill(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID of the bill giver (a workbench).")]
            string giverId = null,
            [ToolParameter(Description = "0-based index into the bill stack.", DefaultValue = 0)]
            int billIndex = 0,
            [ToolParameter(Description =
                "Instead of billIndex, the RecipeDef the bill runs (first matching bill).")]
            string recipeDef = null,
            [ToolParameter(Description = "'repeatcount', 'targetcount' or 'forever'.")]
            string repeatMode = null,
            [ToolParameter(Description = "New repeatCount, when repeatMode is repeatcount.")]
            int? repeatCount = null,
            [ToolParameter(Description = "New targetCount, when repeatMode is targetcount.")]
            int? targetCount = null,
            [ToolParameter(Description =
                "'dropfloor', 'beststockpile' or 'specificstockpile'. specificstockpile " +
                "needs storeTargetId.")]
            string storeMode = null,
            [ToolParameter(Description =
                "Storage building ThingID or stockpile zone label, for storeMode " +
                "'specificstockpile'.")]
            string storeTargetId = null,
            [ToolParameter(Description = "Lower bound: Awful/Poor/Normal/Good/Excellent/" +
                "Masterwork/Legendary.")]
            string qualityMin = null,
            [ToolParameter(Description = "Upper bound, same names as qualityMin.")]
            string qualityMax = null,
            [ToolParameter(Description = "Suspend or unsuspend the bill.")]
            bool? suspended = null)
        {
            if (string.IsNullOrWhiteSpace(giverId))
                return Fail("giverId is required: the ThingID of the workbench.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var thing = map.listerThings.AllThings.FirstOrDefault(
                    t => string.Equals(t.ThingID, giverId.Trim(), StringComparison.OrdinalIgnoreCase));
                if (thing == null) return Fail($"No spawned thing with id '{giverId}'.");
                if (!(thing is IBillGiver giver))
                    return Fail($"'{giverId}' is a {thing.GetType().Name}, which is not an IBillGiver.");

                var stack = giver.BillStack;
                if (stack == null || stack.Count == 0)
                    return Fail($"'{giverId}' has no bills on its bill stack.");

                Bill bill;
                if (!string.IsNullOrWhiteSpace(recipeDef))
                {
                    bill = stack.Bills.FirstOrDefault(
                        b => b.recipe != null &&
                             string.Equals(b.recipe.defName, recipeDef.Trim(), StringComparison.OrdinalIgnoreCase));
                    if (bill == null)
                        return Fail($"No bill running recipe '{recipeDef}' on '{giverId}'.", new
                        {
                            billsOnGiver = stack.Bills.Select(b => b.recipe?.defName).ToList()
                        });
                }
                else
                {
                    if (billIndex < 0 || billIndex >= stack.Count)
                        return Fail($"billIndex {billIndex} out of range; '{giverId}' has {stack.Count} bill(s).");
                    bill = stack[billIndex];
                }

                var bpOrNull = bill as Bill_Production;

                // 🔴 VALIDATE EVERYTHING BEFORE WRITING ANYTHING. This block used to write
                // suspended, then repeatMode, then repeatCount/targetCount, and only THEN
                // parse storeMode and the quality names - so a call that came back
                // success:false had already half-reconfigured the bill and persisted it to
                // the savegame. Nothing below this comment touches the bill.
                if (bpOrNull == null &&
                    (repeatMode != null || repeatCount.HasValue || targetCount.HasValue
                     || qualityMin != null || qualityMax != null))
                    return Fail(
                        $"Bill on '{giverId}' is a {bill.GetType().Name}, not a " +
                        "Bill_Production - repeatMode/repeatCount/targetCount/quality " +
                        "do not exist on it. NOTHING was changed.",
                        new { suspendedNow = bill.suspended });

                BillRepeatModeDef rmDef = null;
                if (repeatMode != null && !TryParseRepeatMode(repeatMode, out rmDef))
                    return Fail($"Unknown repeatMode '{repeatMode}'.", new
                    { accepted = new[] { "repeatcount", "targetcount", "forever" } });

                // The game's own +/- buttons clamp both at zero (Bill_Production.cs
                // DoConfigInterface, Mathf.Max(0, ...)). A negative one here would be
                // scribed straight into the save and leave the bill permanently unable to
                // satisfy itself, with nothing in the UI to show why.
                if (repeatCount.HasValue && repeatCount.Value < 0)
                    return Fail($"repeatCount must be >= 0, got {repeatCount.Value}.");
                if (targetCount.HasValue && targetCount.Value < 0)
                    return Fail($"targetCount must be >= 0, got {targetCount.Value}.");

                BillStoreModeDef smDef = null;
                ISlotGroup grp = null;
                if (storeMode != null)
                {
                    if (!TryParseStoreMode(storeMode, out smDef))
                        return Fail($"Unknown storeMode '{storeMode}'.", new
                        { accepted = new[] { "dropfloor", "beststockpile", "specificstockpile" } });
                    if (smDef == BillStoreModeDefOf.SpecificStockpile)
                    {
                        string sgErr;
                        grp = ResolveSlotGroup(map, storeTargetId, out sgErr);
                        if (grp == null) return Fail(sgErr);
                    }
                }

                QualityRange? newQuality = null;
                if (qualityMin != null || qualityMax != null)
                {
                    // bpOrNull is non-null here: the guard above already refused quality
                    // arguments on a non-Bill_Production.
                    var min = bpOrNull.qualityRange.min;
                    var max = bpOrNull.qualityRange.max;
                    if (qualityMin != null && !Enum.TryParse(qualityMin.Trim(), true, out min))
                        return Fail($"Unknown qualityMin '{qualityMin}'.", new
                        { accepted = Enum.GetNames(typeof(QualityCategory)) });
                    if (qualityMax != null && !Enum.TryParse(qualityMax.Trim(), true, out max))
                        return Fail($"Unknown qualityMax '{qualityMax}'.", new
                        { accepted = Enum.GetNames(typeof(QualityCategory)) });
                    // QualityRange.Includes is `q >= min && q <= max` with no guard of its own
                    // (RimWorld/QualityRange.cs), so an inverted band matches NOTHING: the bill
                    // silently stops accepting every ingredient and just never runs again. The
                    // in-game two-handle slider cannot produce one; this tool could.
                    if (min > max)
                        return Fail(
                            $"qualityMin ({min}) is above qualityMax ({max}). QualityRange.Includes " +
                            "is min<=q<=max, so an inverted band matches no ingredient at all and " +
                            "the bill would silently never run. Nothing was changed.");
                    newQuality = new QualityRange(min, max);
                }

                // ---- validation done; writes start here ----
                if (suspended.HasValue) bill.suspended = suspended.Value;

                if (bpOrNull == null)
                {
                    // Store mode is on the base Bill class; the rest is not.
                    if (smDef != null) bill.SetStoreMode(smDef, grp);

                    return new
                    {
                        success = true,
                        billType = bill.GetType().Name,
                        suspended = bill.suspended,
                        storeMode = bill.GetStoreMode()?.defName,
                    };
                }

                var bp = bpOrNull;
                if (rmDef != null) bp.repeatMode = rmDef;
                if (repeatCount.HasValue) bp.repeatCount = repeatCount.Value;
                if (targetCount.HasValue) bp.targetCount = targetCount.Value;
                if (smDef != null) bp.SetStoreMode(smDef, grp);
                if (newQuality.HasValue) bp.qualityRange = newQuality.Value;

                var group = bp.GetSlotGroup();
                return new
                {
                    success = true,
                    billType = "Bill_Production",
                    recipe = bp.recipe?.defName,
                    suspended = bp.suspended,
                    repeatMode = bp.repeatMode?.defName,
                    repeatCount = bp.repeatCount,
                    targetCount = bp.targetCount,
                    storeMode = bp.GetStoreMode()?.defName,
                    storeGroupCells = group?.CellsList?.Count,
                    qualityMin = bp.qualityRange.min.ToString(),
                    qualityMax = bp.qualityRange.max.ToString(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/new_allowed_area - AreaManager.TryMakeNewAllowed
        // =====================================================================

        [Tool(
            "jawa/new_allowed_area",
            Description =
                "Create a new named Allowed Area on the current map - " +
                "AreaManager.TryMakeNewAllowed(out Area_Allowed). ⚠️ An older doc " +
                "(design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md) calls this method " +
                "absent; it exists at Verse/AreaManager.cs:147 and this tool calls it. " +
                "Refuses when 10 allowed areas already exist " +
                "(AreaManager.CanMakeNewAllowed / MaxAllowedAreas). Paint it with " +
                "jawa/paint_area afterward - this only creates an empty area.",
            ResultDescription =
                "success is TryMakeNewAllowed's own bool. On success: the area's id and " +
                "label, read back from AreaManager.AllAreas, plus the allowed-area count " +
                "now/max (10).")]
        public static async Task<object> NewAllowedArea(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Label for the new area. Omit for the game's default 'Area N'.")]
            string label = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var before = map.areaManager.AllAreas.OfType<Area_Allowed>().Count();
                Area_Allowed area;
                var ok = map.areaManager.TryMakeNewAllowed(out area);
                if (!ok)
                    return Fail(
                        "TryMakeNewAllowed returned false: AreaManager.CanMakeNewAllowed() " +
                        "is false, meaning 10 Allowed areas already exist on this map.",
                        new { existingAllowedAreas = before, max = 10 });

                if (!string.IsNullOrWhiteSpace(label)) area.SetLabel(label.Trim());

                var stillThere = map.areaManager.AllAreas.Contains(area);
                return new
                {
                    success = stillThere,
                    id = area.ID,
                    label = area.Label,
                    allowedAreaCountNow = map.areaManager.AllAreas.OfType<Area_Allowed>().Count(),
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/paint_area - Home/BuildRoof/NoRoof/SnowOrSandClear/PollutionClear
        //                   /Allowed areas, Area indexer + Area.Clear()
        // =====================================================================

        [Tool(
            "jawa/paint_area",
            Description =
                "Paint or clear cells in one of the four standard map areas (home, roof, " +
                "noroof, snow/pollution) or a named Allowed area, via the Area cell " +
                "indexer (Area.this[IntVec3]). ops format 'x,z,w,h' separated by ';' " +
                "(same shape as jawa/set_terrain_batch's ops, minus the def prefix). " +
                "value=false clears the listed cells instead of setting them; " +
                "clearAreaFirst empties the WHOLE area (Area.Clear()) before painting.",
            ResultDescription =
                "Every written cell read back off the area afterward (area[cell] == " +
                "value), never assumed from the call returning. requested/setCount/" +
                "failedVerify/outOfBounds, plus the area's total TrueCount afterward.")]
        public static async Task<object> PaintArea(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "'home', 'roof', 'noroof', 'snow', 'pollution', or the exact label of an " +
                "existing Allowed area.")]
            string area = null,
            [ToolParameter(Description = "Rect ops: 'x,z,w,h' separated by ';' or newlines. w/h default 1.")]
            string ops = null,
            [ToolParameter(Description = "true paints the cells into the area, false removes them.",
                DefaultValue = true)]
            bool value = true,
            [ToolParameter(Description =
                "Empty the WHOLE area (Area.Clear()) before painting the listed cells.",
                DefaultValue = false)]
            bool clearAreaFirst = false,
            [ToolParameter(Description =
                "If 'area' names no existing Allowed area, create one with that label " +
                "(AreaManager.TryMakeNewAllowed) instead of refusing. Never applies to the " +
                "four standard kinds, which always exist.", DefaultValue = false)]
            bool createIfMissing = false)
        {
            if (string.IsNullOrWhiteSpace(ops))
                return Fail("ops is required, e.g. '10,20,5,5;30,30,2,2'.");
            // Blank 'area' with createIfMissing used to fall through ResolveAreaByKindOrLabel's
            // "No area given." into TryMakeNewAllowed and then area.Trim() on a null string:
            // an NRE AFTER an Area_Allowed had already been created, burning one of the map's
            // ten allowed-area slots into the savegame with a null label.
            if (string.IsNullOrWhiteSpace(area))
                return Fail("area is required: 'home', 'roof', 'noroof', 'snow', 'pollution', " +
                            "or the label of an Allowed area (createIfMissing needs a label to give it).");

            List<ParsedOp> parsed;
            var parseErrors = new List<string>();
            if (!TryParseOps(ops, "cells", out parsed, parseErrors))
                return Fail("Could not parse ops.", new { errors = parseErrors });

            long totalCells = 0;
            foreach (var op in parsed) totalCells += (long)op.W * op.H;
            if (parsed.Count > MaxOps)
                return Fail($"Too many ops: {parsed.Count} > {MaxOps}. Split the call.");
            if (totalCells > MaxCells)
                return Fail($"Too many cells: {totalCells} > {MaxCells}. Split the call.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string err;
                var target = ResolveAreaByKindOrLabel(map, area, out err);
                if (target == null)
                {
                    if (!createIfMissing) return Fail(err);
                    Area_Allowed created;
                    if (!map.areaManager.TryMakeNewAllowed(out created))
                        return Fail(
                            $"No area named '{area}', and could not create one: 10 Allowed " +
                            "areas already exist on this map.");
                    created.SetLabel(area.Trim());
                    target = created;
                }

                if (clearAreaFirst) target.Clear();

                var size = map.Size;
                var requested = 0;
                var setCount = 0;
                var failedVerify = 0;
                var outOfBounds = 0;

                foreach (var op in parsed)
                {
                    for (var dx = 0; dx < op.W; dx++)
                    {
                        for (var dz = 0; dz < op.H; dz++)
                        {
                            var c = new IntVec3(op.X + dx, 0, op.Z + dz);
                            requested++;
                            if (c.x < 0 || c.z < 0 || c.x >= size.x || c.z >= size.z)
                            {
                                outOfBounds++;
                                continue;
                            }
                            target[c] = value;
                            if (target[c] == value) setCount++;
                            else failedVerify++;
                        }
                    }
                }
                target.MarkForDraw();

                return new
                {
                    success = failedVerify == 0 && outOfBounds == 0,
                    areaLabel = target.Label,
                    areaId = target.ID,
                    value,
                    requested,
                    setCount,
                    failedVerify,
                    outOfBounds,
                    trueCountNow = target.TrueCount,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/ordered_job - JobMaker.MakeJob + Pawn_JobTracker.TryTakeOrderedJob
        // =====================================================================

        [Tool(
            "jawa/ordered_job",
            Description =
                "Issue ANY JobDef through Pawn_JobTracker.TryTakeOrderedJob - the same " +
                "player-order path jawa/order_pawn uses for Goto specifically, opened up " +
                "to arbitrary jobs (hauling, cleaning, sowing, using a bill giver, ...). " +
                "targetA/targetB each come from a ThingID OR an x/z cell; omit both of a " +
                "pair for a job that needs no target. ⚠️ TryTakeOrderedJob returns false for " +
                "exactly ONE reason - job.TryMakePreToilReservations failed, i.e. the pawn " +
                "could not reserve the target - and that refusal is reported, not swallowed. " +
                "It does NOT refuse a non-interruptible pawn: it enqueues the job LAST and " +
                "returns true, so the order runs after the current job rather than replacing " +
                "it (interruptibleBefore says which happened). A TRUE return only means the " +
                "job was ENQUEUED; this waits waitTicks game ticks and reads curJob back " +
                "afterward, same discipline as jawa/order_pawn. " +
                "🔑 Sow / Replant / PlantSeed REQUIRE plantDef - their driver dereferences " +
                "Job.plantDefToSow in its first toil, and this tool refuses rather than " +
                "letting the engine fail there silently.",
            ResultDescription =
                "accepted (TryTakeOrderedJob's own bool) and interruptibleBefore, plus " +
                "beforeJobDef/afterJobDef read back after the wait and " +
                "nowRunningRequested (afterJobDef == the JobDef you asked for). success " +
                "requires both accepted and nowRunningRequested - so a job legitimately " +
                "QUEUED behind a non-interruptible current job, or queued on purpose with " +
                "queue:true, reads success:false; queueLength and note say so. Also plantDefToSow (what " +
                "was actually set on the Job) and pausedDuringWait - 🔑 when that is true " +
                "NO ticks passed, ticksElapsed is 0 by definition, and the read-back proves " +
                "NOTHING about whether the job would run.")]
        public static async Task<object> OrderedJob(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID, name or thingIDNumber of the pawn to order.")]
            string pawnId = null,
            [ToolParameter(Description = "JobDef defName, e.g. Goto, HaulToCell, CleanFilth.")]
            string jobDef = null,
            [ToolParameter(Description = "targetA: a ThingID. Overrides targetAX/targetAZ.")]
            string targetAId = null,
            [ToolParameter(Description = "targetA: cell X, if not targetAId.", DefaultValue = -1)]
            int targetAX = -1,
            [ToolParameter(Description = "targetA: cell Z, if not targetAId.", DefaultValue = -1)]
            int targetAZ = -1,
            [ToolParameter(Description = "targetB: a ThingID. Overrides targetBX/targetBZ.")]
            string targetBId = null,
            [ToolParameter(Description = "targetB: cell X, if not targetBId.", DefaultValue = -1)]
            int targetBX = -1,
            [ToolParameter(Description = "targetB: cell Z, if not targetBId.", DefaultValue = -1)]
            int targetBZ = -1,
            [ToolParameter(Description = "Job.count, for jobs that carry a stack count.")]
            int? count = null,
            [ToolParameter(Description =
                "ThingDef of the plant, for Sow / Replant / PlantSeed. Sets Job.plantDefToSow. "
                + "REQUIRED for those three - their driver dereferences the field in its FIRST toil, "
                + "so without it the job is accepted and dies before doing anything.")]
            string plantDef = null,
            [ToolParameter(Description =
                "JobTag: Misc, Idle, Homework, MechDefend, ... Defaults to Misc.")]
            string jobTag = "Misc",
            [ToolParameter(Description = "requestQueueing - queue after the current job instead of interrupting.",
                DefaultValue = false)]
            bool queue = false,
            [ToolParameter(Description = "Game ticks to wait before reading curJob back.", DefaultValue = 60)]
            int waitTicks = 60,
            [ToolParameter(Description = "Wall-clock ceiling on the wait.", DefaultValue = 15)]
            int timeoutSeconds = 15)
        {
            if (string.IsNullOrWhiteSpace(jobDef))
                return Fail("jobDef is required, e.g. 'Goto' or 'HaulToCell'.");
            if (waitTicks < 0) return Fail($"waitTicks must be >= 0, got {waitTicks}.");
            if (timeoutSeconds < 1 || timeoutSeconds > 300)
                return Fail($"timeoutSeconds must be 1-300, got {timeoutSeconds}.");

            var startTicks = 0;
            var accepted = false;
            var interruptibleBefore = false;
            string beforeJobDef = null;
            string jdefName = null;
            string plantDefName = null;

            var setup = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null) return Fail(perr);
                if (pawn.jobs == null) return Fail($"'{pawnId}' has no Pawn_JobTracker.");

                // 🔴 OFF-MAP / CONTAINED PAWN GUARD (2026-09-03 sonnet fallback review).
                // FindPawn (JawaBenchPawnTools.cs) was widened tonight to also match held
                // pawns (caskets, growth vats, pods, carried) and world pawns (caravans,
                // transit) - neither is Spawned, so Thing.Map returns null for both
                // (Verse/Thing.cs: the Map getter is gated on mapIndexOrState >= 0, i.e.
                // Spawned). Most JobDrivers dereference pawn.Map UNGUARDED in
                // TryMakePreToilReservations - e.g. JobDriver_Goto.cs:13 is
                // `pawn.Map.pawnDestinationReservationManager.Reserve(...)` - so ordering a
                // job on either population throws a raw NRE out of TryTakeOrderedJob instead
                // of the clean Fail() this tool promises everywhere else. Caught before
                // MakeJob is even called. A pawn spawned on a DIFFERENT loaded map is also
                // refused: targetA/targetB and x/z are resolved against Find.CurrentMap
                // (ResolveTarget below), so a cross-map order would reserve/path against the
                // wrong map's grids.
                if (!pawn.Spawned)
                    return Fail(
                        $"'{pawnId}' is not Spawned (it is contained - casket/vat/pod/carried " +
                        "- or a world pawn - caravan/transit) and has no Map. Job drivers " +
                        "dereference pawn.Map unguarded (e.g. JobDriver_Goto) and would NRE " +
                        "instead of failing cleanly. jawa/ordered_job only works on a pawn " +
                        "spawned on a loaded map.",
                        new { spawned = pawn.Spawned, mapHeld = pawn.MapHeld?.ToString() });
                if (pawn.Map != map)
                    return Fail(
                        $"'{pawnId}' is spawned on map '{pawn.Map}', not the current map " +
                        $"'{map}'. targetA/targetB (and x/z) are resolved against " +
                        "Find.CurrentMap, so this order would reserve/path against the wrong " +
                        "map's grids. Switch to that map first.");

                var jd = DefDatabase<JobDef>.GetNamedSilentFail(jobDef.Trim());
                if (jd == null) return Fail($"Unknown JobDef '{jobDef}'.");
                jdefName = jd.defName;

                JobTag tag;
                if (!Enum.TryParse(string.IsNullOrWhiteSpace(jobTag) ? "Misc" : jobTag.Trim(), true, out tag))
                    return Fail($"Unknown JobTag '{jobTag}'.",
                        new { accepted = Enum.GetNames(typeof(JobTag)) });

                string errA, errB;
                var a = ResolveTarget(map, targetAId, targetAX, targetAZ, out errA);
                if (a == null && errA != null) return Fail(errA);
                var b = ResolveTarget(map, targetBId, targetBX, targetBZ, out errB);
                if (b == null && errB != null) return Fail(errB);

                // ORDERED_JOB_CANNOT_SOW_1, measured live 2026-08-26 and read from 1.6
                // source, not inferred. JobDriver_PlantSow's FIRST toil is
                //     .FailOn(() => PlantUtility.AdjacentSowBlocker(job.plantDefToSow, ...) != null)
                //     .FailOn(() => !job.plantDefToSow.CanNowPlantAt(...))
                // and nothing in this tool's parameter set ever set the field. So every
                // Sow it issued came back accepted:true / nowRunningRequested:false and
                // died in its first toil. Replant (WorkGiver_Replant.cs:69) and PlantSeed
                // (WorkGiver_PlantSeed.cs:59) read the same field.
                //
                // Refuse AT THE TOOL and name the field, rather than letting the engine
                // fail silently in a toil - that is the whole failure class this bridge
                // exists to expose.
                var needsPlant = jd.defName == "Sow" || jd.defName == "Replant" || jd.defName == "PlantSeed";
                ThingDef plantThing = null;
                if (!string.IsNullOrWhiteSpace(plantDef))
                {
                    plantThing = DefDatabase<ThingDef>.GetNamedSilentFail(plantDef.Trim());
                    if (plantThing == null)
                        return Fail($"No ThingDef '{plantDef}' for plantDef.", DefSuggestions<ThingDef>(plantDef));
                    if (plantThing.plant == null)
                        return Fail($"ThingDef '{plantThing.defName}' is not a plant - it has no plant properties, "
                                  + "so Job.plantDefToSow would be meaningless.");
                }
                if (needsPlant && plantThing == null)
                    return Fail($"JobDef '{jd.defName}' requires plantDef: its driver reads "
                              + "Job.plantDefToSow in its FIRST toil and would fail there silently. "
                              + "Pass a plant ThingDef, e.g. Plant_Potato.");

                var job = a.HasValue
                    ? (b.HasValue ? JobMaker.MakeJob(jd, a.Value, b.Value) : JobMaker.MakeJob(jd, a.Value))
                    : JobMaker.MakeJob(jd);
                if (count.HasValue) job.count = count.Value;
                if (plantThing != null) { job.plantDefToSow = plantThing; plantDefName = plantThing.defName; }

                interruptibleBefore = pawn.jobs.IsCurrentJobPlayerInterruptible();
                beforeJobDef = pawn.jobs.curJob?.def?.defName;

                var tm = Find.TickManager;
                startTicks = tm?.TicksGame ?? -1;

                accepted = pawn.jobs.TryTakeOrderedJob(job, tag, queue);
                return null;
            }, cancellationToken).ConfigureAwait(false);
            if (setup != null) return setup;

            // ORDERED_JOB_CANNOT_SOW_1, related half: waitTicks does NOTHING while the game
            // is PAUSED - ticksElapsed comes back 0 however long you ask for, because no
            // ticks pass. Reported below as pausedDuringWait rather than left to look like
            // a job that failed to start.
            var pausedDuringWait = await ctx.MainThread.InvokeAsync(
                () => Find.TickManager != null && Find.TickManager.Paused, cancellationToken)
                .ConfigureAwait(false);

            var ticksNow = startTicks;
            var elapsedMs = 0;
            while (ticksNow - startTicks < waitTicks && elapsedMs < timeoutSeconds * 1000)
            {
                cancellationToken.ThrowIfCancellationRequested();
                await Task.Delay(100, cancellationToken).ConfigureAwait(false);
                elapsedMs += 100;
                ticksNow = await ctx.MainThread.InvokeAsync(() => TicksGameSafe(), cancellationToken)
                    .ConfigureAwait(false);
            }

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null)
                    return new { success = false, accepted, message = "Pawn no longer resolvable after the wait." };

                var afterJobDef = pawn.jobs?.curJob?.def?.defName;
                var nowRunningRequested = string.Equals(afterJobDef, jdefName, StringComparison.OrdinalIgnoreCase);

                string note = null;
                if (!accepted)
                    // Read out of Verse/AI/Pawn_JobTracker.cs:891-961: every one of the three
                    // branches returns true unless job.TryMakePreToilReservations(pawn,
                    // errorOnFailed: true) returns false, which is the ONLY false return in the
                    // method. Non-interruptibility does NOT cause one - see the note below.
                    note = "TryTakeOrderedJob returned false, which in 1.6 has exactly one cause: " +
                           "job.TryMakePreToilReservations failed, i.e. the pawn could not reserve " +
                           "this job's target(s) - another pawn already holds the reservation, or the " +
                           "target/cell is not reservable for this job. RimWorld also logged a warning " +
                           "naming the pawn and job. Nothing about interruptibility, drafting or fire " +
                           "makes this call return false.";
                else if (!nowRunningRequested)
                    note = $"Job was accepted (enqueued) but curJob after {waitTicks} tick(s) is " +
                           $"'{afterJobDef ?? "(none)"}', not '{jdefName}' - it may have finished, " +
                           "failed immediately, or be queued rather than current." +
                           (!interruptibleBefore
                               ? " 🔑 THE PAWN WAS NOT PLAYER-INTERRUPTIBLE when the order was issued "
                                 + $"(it was running '{beforeJobDef ?? "(none)"}'), so TryTakeOrderedJob "
                                 + "enqueued this job LAST instead of replacing the current one. It is "
                                 + "waiting its turn, not lost - queueLength shows it. Stop the current "
                                 + "job (jawa/stop_job) first if you meant to pre-empt."
                               : "") +
                           (queue
                               ? " 🔑 You passed queue:true, so a non-current curJob is the REQUESTED "
                                 + "outcome; check queueLength rather than this field."
                               : "") +
                           (pausedDuringWait
                               ? " ⚠️ THE GAME WAS PAUSED for this wait, so NO ticks passed and this "
                                 + "reading proves nothing about whether the job would run. Unpause, or "
                                 + "step ticks, and ask again."
                               : "");

                return new
                {
                    success = accepted && nowRunningRequested,
                    accepted,
                    interruptibleBefore,
                    beforeJobDef,
                    requestedJobDef = jdefName,
                    afterJobDef,
                    nowRunningRequested,
                    ticksElapsed = ticksNow - startTicks,
                    pausedDuringWait,
                    plantDefToSow = plantDefName,
                    queueLength = pawn.jobs?.jobQueue?.Count ?? 0,
                    note,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/stop_job - StopAll / EndCurrentJob / ClearQueuedJobs
        // =====================================================================

        [Tool(
            "jawa/stop_job",
            Description =
                "Cancel what a pawn is doing: StopAll (current job + queue), EndCurrentJob " +
                "(just the current job, queue survives) or ClearQueuedJobs (queue only, " +
                "current job survives).",
            ResultDescription =
                "curJob and queue length read back BEFORE and AFTER, so a call that changed " +
                "nothing (pawn was already idle) is visible rather than reading as a no-op success.")]
        public static async Task<object> StopJob(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID, name or thingIDNumber of the pawn.")]
            string pawnId = null,
            [ToolParameter(Description = "'stopall', 'endcurrent' or 'clearqueue'.", DefaultValue = "endcurrent")]
            string mode = "endcurrent",
            [ToolParameter(Description =
                "JobCondition for 'endcurrent': InterruptForced, Succeeded, Incompletable, " +
                "...", DefaultValue = "InterruptForced")]
            string jobCondition = "InterruptForced",
            [ToolParameter(Description = "StopAll only: keep a laying pawn laying.", DefaultValue = false)]
            bool ifLayingKeepLaying = false,
            [ToolParameter(Description = "Return the ended job to the pool for reuse.", DefaultValue = true)]
            bool canReturnToPool = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null) return Fail(perr);
                if (pawn.jobs == null) return Fail($"'{pawnId}' has no Pawn_JobTracker.");

                var beforeJob = pawn.jobs.curJob?.def?.defName;
                var beforeQueue = pawn.jobs.jobQueue?.Count ?? 0;

                var m = (mode ?? "").Trim().ToLowerInvariant();
                switch (m)
                {
                    case "stopall":
                        pawn.jobs.StopAll(ifLayingKeepLaying, canReturnToPool);
                        break;
                    case "endcurrent":
                        JobCondition cond;
                        if (!Enum.TryParse(string.IsNullOrWhiteSpace(jobCondition) ? "InterruptForced" : jobCondition.Trim(),
                                true, out cond))
                            return Fail($"Unknown JobCondition '{jobCondition}'.",
                                new { accepted = Enum.GetNames(typeof(JobCondition)) });
                        pawn.jobs.EndCurrentJob(cond, true, canReturnToPool);
                        break;
                    case "clearqueue":
                        pawn.jobs.ClearQueuedJobs(canReturnToPool);
                        break;
                    default:
                        return Fail($"mode must be 'stopall', 'endcurrent' or 'clearqueue', got '{mode}'.");
                }

                var afterJob = pawn.jobs.curJob?.def?.defName;
                var afterQueue = pawn.jobs.jobQueue?.Count ?? 0;

                return new
                {
                    success = true,
                    mode = m,
                    beforeJob,
                    afterJob,
                    beforeQueueLength = beforeQueue,
                    afterQueueLength = afterQueue,
                    changed = beforeJob != afterJob || beforeQueue != afterQueue,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/set_work_priority - Pawn_WorkSettings.SetPriority
        // =====================================================================

        [Tool(
            "jawa/set_work_priority",
            Description =
                "Set one pawn's work-tab priority for one WorkTypeDef - " +
                "Pawn_WorkSettings.SetPriority(WorkTypeDef, int), 0=off, 1 (highest) to 4 " +
                "(lowest). ⚠️ Pawn_WorkSettings.GetPriority - what this tool reads back - " +
                "returns 3 for ANY active (>0) work type when " +
                "Find.PlaySettings.useWorkPriorities is OFF, regardless of what was written. " +
                "That flag is reported alongside the read-back so '3' cannot be mistaken " +
                "for proof. SetPriority itself silently refuses (logs an error, writes " +
                "nothing) when priority != 0 and the work type is disabled for this pawn - " +
                "checked and reported before writing.",
            ResultDescription =
                "manualPrioritiesOn (Find.PlaySettings.useWorkPriorities) and readBack " +
                "(GetPriority after the write) together - never readBack alone.")]
        public static async Task<object> SetWorkPriority(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID, name or thingIDNumber of the pawn.")]
            string pawnId = null,
            [ToolParameter(Description = "WorkTypeDef defName, e.g. Cooking, Hauling, Firefighter.")]
            string workType = null,
            [ToolParameter(Description = "0 (off) to 4 (lowest active).")]
            int priority = 3)
        {
            if (string.IsNullOrWhiteSpace(workType))
                return Fail("workType is required, e.g. 'Cooking'.");
            if (priority < 0 || priority > 4)
                return Fail($"priority must be 0-4, got {priority}.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null) return Fail(perr);

                var wd = DefDatabase<WorkTypeDef>.GetNamedSilentFail(workType.Trim());
                if (wd == null)
                    return Fail($"Unknown WorkTypeDef '{workType}'.", new
                    {
                        knownWorkTypes = DefDatabase<WorkTypeDef>.AllDefsListForReading
                            .Select(d => d.defName).ToList()
                    });

                if (pawn.workSettings == null)
                    return Fail($"'{pawnId}' has no Pawn_WorkSettings (not a work-eligible pawn).");
                pawn.workSettings.EnableAndInitializeIfNotAlreadyInitialized();

                var disabled = pawn.WorkTypeIsDisabled(wd);
                if (priority != 0 && disabled)
                    return Fail(
                        $"SetPriority silently refuses: '{wd.defName}' is DISABLED for this " +
                        "pawn (Log.Error, no change). Nothing was written.",
                        new
                        {
                            disabledWorkTypes = pawn.GetDisabledWorkTypes().Select(d => d.defName).ToList()
                        });

                pawn.workSettings.SetPriority(wd, priority);
                var readBack = pawn.workSettings.GetPriority(wd);
                var manualPrioritiesOn = Find.PlaySettings?.useWorkPriorities ?? false;

                return new
                {
                    success = true,
                    requested = priority,
                    readBack,
                    manualPrioritiesOn,
                    // GetPriority's override is gated on pawn.RaceProps.Humanlike
                    // (RimWorld/Pawn_WorkSettings.cs:164) - a Biotech mech's readBack is the
                    // real stored number even with useWorkPriorities off, so this warning
                    // must not fire for one.
                    note = !manualPrioritiesOn && priority > 0 && pawn.RaceProps.Humanlike
                        ? "useWorkPriorities is OFF: GetPriority returns 3 for any active " +
                          "work type regardless of the value written. readBack does not " +
                          "prove the requested number stuck; it proves only active vs off."
                        : null,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/set_draft - Pawn_DraftController.Drafted / FireAtWill
        // =====================================================================

        [Tool(
            "jawa/set_draft",
            Description =
                "Draft or undraft a pawn (Pawn_DraftController.Drafted) and/or set its fire " +
                "policy (FireAtWill). Before setting Drafted=true this checks " +
                "Lord.AllowsDrafting(pawn) - the same AcceptanceReport that disables the " +
                "game's own draft gizmo (e.g. during a ritual or ceremony) - and refuses " +
                "with the game's own reason string instead of drafting a pawn a Lord will " +
                "immediately fight.",
            ResultDescription =
                "drafted and fireAtWill read back off the controller after writing. On a " +
                "drafting refusal, success is false and message carries " +
                "Lord.AllowsDrafting's Reason verbatim.")]
        public static async Task<object> SetDraft(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID, name or thingIDNumber of the pawn.")]
            string pawnId = null,
            [ToolParameter(Description = "Draft (true) or undraft (false). Omit to leave unchanged.")]
            bool? drafted = null,
            [ToolParameter(Description = "Fire-at-will (true) or wait-for-target (false). Omit to leave unchanged.")]
            bool? fireAtWill = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null) return Fail(perr);
                if (pawn.drafter == null)
                    return Fail($"'{pawnId}' has no Pawn_DraftController (not draftable).");

                if (drafted.HasValue)
                {
                    if (drafted.Value)
                    {
                        var lord = pawn.GetLord();
                        AcceptanceReport allow = lord != null ? lord.AllowsDrafting(pawn) : AcceptanceReport.WasAccepted;
                        if (!allow.Accepted)
                            return Fail(
                                "Lord.AllowsDrafting refused: " +
                                (string.IsNullOrEmpty(allow.Reason) ? "(no reason given)" : allow.Reason),
                                new { lordJob = lord?.LordJob?.GetType().Name });
                    }
                    pawn.drafter.Drafted = drafted.Value;
                }
                if (fireAtWill.HasValue) pawn.drafter.FireAtWill = fireAtWill.Value;

                return new
                {
                    success = true,
                    drafted = pawn.drafter.Drafted,
                    fireAtWill = pawn.drafter.FireAtWill,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/timetable - Pawn_TimetableTracker.SetAssignment
        // =====================================================================

        [Tool(
            "jawa/timetable",
            Description =
                "Set one or all 24 hourly slots of a pawn's timetable - " +
                "Pawn_TimetableTracker.SetAssignment(hour, TimeAssignmentDef). ⛔ The write " +
                "always happens, but Pawn_TimetableTracker.CurrentAssignment - what the " +
                "pawn actually obeys - is HARD-CODED to 'Anything' for non-colonists and " +
                "prisoners (Pawn_TimetableTracker.cs). This tool checks IsColonist and " +
                "IsPrisonerOfColony and says so when the write will have no behavioural " +
                "effect, instead of reporting a bare success.",
            ResultDescription =
                "readBack: GetAssignment for the hour(s) written. ignoredInPractice is true " +
                "when the pawn is not a colonist or is a prisoner, meaning the write took " +
                "but CurrentAssignment will not use it.")]
        public static async Task<object> Timetable(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID, name or thingIDNumber of the pawn.")]
            string pawnId = null,
            [ToolParameter(Description = "Hour 0-23, or -1 for every hour.", DefaultValue = -1)]
            int hour = -1,
            [ToolParameter(Description = "TimeAssignmentDef defName: Anything, Work, Sleep, Joy, Meditate, ...")]
            string assignment = null)
        {
            if (string.IsNullOrWhiteSpace(assignment))
                return Fail("assignment is required, e.g. 'Anything', 'Work', 'Sleep'.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null) return Fail(perr);
                if (pawn.timetable == null)
                    return Fail($"'{pawnId}' has no Pawn_TimetableTracker.");

                var ta = DefDatabase<TimeAssignmentDef>.GetNamedSilentFail(assignment.Trim());
                if (ta == null)
                    return Fail($"Unknown TimeAssignmentDef '{assignment}'.", new
                    {
                        knownAssignments = DefDatabase<TimeAssignmentDef>.AllDefsListForReading
                            .Select(d => d.defName).ToList()
                    });

                if (hour != -1 && (hour < 0 || hour > 23))
                    return Fail($"hour must be 0-23 or -1 (all), got {hour}.");

                if (hour == -1)
                    for (var h = 0; h < 24; h++) pawn.timetable.SetAssignment(h, ta);
                else
                    pawn.timetable.SetAssignment(hour, ta);

                var readBack = Enumerable.Range(0, 24)
                    .Select(h => pawn.timetable.GetAssignment(h).defName).ToList();

                var ignoredInPractice = !pawn.IsColonist || pawn.IsPrisonerOfColony;

                return new
                {
                    success = true,
                    hour,
                    assignment = ta.defName,
                    isColonist = pawn.IsColonist,
                    isPrisoner = pawn.IsPrisonerOfColony,
                    ignoredInPractice,
                    note = ignoredInPractice
                        ? "Write took, but CurrentAssignment is hard-coded to Anything for " +
                          "non-colonists and prisoners, so this has no behavioural effect."
                        : null,
                    readBackAllHours = readBack,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // =====================================================================
        // jawa/set_player_settings - Pawn_PlayerSettings area/master/medCare/
        //                            hostilityResponse
        // =====================================================================

        [Tool(
            "jawa/set_player_settings",
            Description =
                "Set a pawn's Pawn_PlayerSettings: allowed-area restriction, master, " +
                "medical care category, and hostility response. Each parameter is applied " +
                "only if given. ⚠️ Two silent no-ops here, both checked: " +
                "AreaRestrictionInPawnCurrentMap's setter is a no-op when pawn.MapHeld is " +
                "null (not spawned / carried on no spawned map); Master's setter is a " +
                "Log.ErrorOnce-and-return when the candidate has not learned the Obedience " +
                "trainable. Both are read back and reported rather than assumed.",
            ResultDescription =
                "area/master/medCare/hostilityResponse read back off the pawn after " +
                "writing. notes[] carries any silent-refusal explanation.")]
        public static async Task<object> SetPlayerSettings(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID, name or thingIDNumber of the pawn.")]
            string pawnId = null,
            [ToolParameter(Description =
                "Allowed area: 'home'/'roof'/'noroof'/'snow'/'pollution', an Allowed area's " +
                "label, or 'none'/'clear' to remove the restriction.")]
            string area = null,
            [ToolParameter(Description = "Master pawn's ThingID, or 'none' to clear.")]
            string masterId = null,
            [ToolParameter(Description = "MedicalCareCategory: NoCare, NoMeds, HerbalOrWorse, " +
                "NormalOrWorse, Best.")]
            string medCare = null,
            [ToolParameter(Description = "HostilityResponseMode: Ignore, Flee, Attack.")]
            string hostilityResponse = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null) return Fail(perr);
                if (pawn.playerSettings == null)
                    return Fail($"'{pawnId}' has no Pawn_PlayerSettings.");

                var notes = new List<string>();

                if (area != null)
                {
                    if (pawn.MapHeld == null)
                    {
                        notes.Add(
                            "AreaRestrictionInPawnCurrentMap's setter is a no-op when " +
                            "pawn.MapHeld is null. Nothing was changed.");
                    }
                    else
                    {
                        var a = area.Trim();
                        if (string.Equals(a, "none", StringComparison.OrdinalIgnoreCase)
                            || string.Equals(a, "clear", StringComparison.OrdinalIgnoreCase))
                        {
                            pawn.playerSettings.AreaRestrictionInPawnCurrentMap = null;
                        }
                        else
                        {
                            string aerr;
                            var resolved = ResolveAreaByKindOrLabel(pawn.MapHeld, a, out aerr);
                            if (resolved == null) return Fail(aerr);
                            pawn.playerSettings.AreaRestrictionInPawnCurrentMap = resolved;
                        }
                    }
                }

                if (masterId != null)
                {
                    if (string.Equals(masterId.Trim(), "none", StringComparison.OrdinalIgnoreCase))
                    {
                        pawn.playerSettings.Master = null;
                    }
                    else
                    {
                        string merr;
                        var m = FindPawn(masterId, out merr);
                        if (m == null) return Fail(merr);
                        // 🔴 Pawn_PlayerSettings.Master's setter dereferences pawn.training
                        // UNGUARDED (RimWorld/Pawn_PlayerSettings.cs:55). A Pawn_TrainingTracker
                        // only exists for intelligence <= 1, factioned, non-mechanoid pawns
                        // (RimWorld/PawnComponentsUtility.cs:357) - so every humanlike colonist
                        // has training == null and this threw a raw NullReferenceException out
                        // of the tool instead of the documented Obedience report.
                        if (pawn.training == null)
                            return Fail(
                                $"{pawn.LabelShortCap} has no Pawn_TrainingTracker, so it cannot " +
                                "have a master - Pawn_PlayerSettings.Master's setter would throw. " +
                                "Masters are for trainable animals, not humanlikes or mechanoids.");
                        pawn.playerSettings.Master = m;
                        if (pawn.playerSettings.Master != m)
                            notes.Add(
                                $"Master setter silently refused: {pawn.LabelShortCap} has not " +
                                "learned the Obedience trainable. No change made.");
                    }
                }

                if (medCare != null)
                {
                    MedicalCareCategory mc;
                    if (!Enum.TryParse(medCare.Trim(), true, out mc))
                        return Fail($"Unknown MedicalCareCategory '{medCare}'.",
                            new { accepted = Enum.GetNames(typeof(MedicalCareCategory)) });
                    pawn.playerSettings.medCare = mc;
                }

                if (hostilityResponse != null)
                {
                    HostilityResponseMode hr;
                    if (!Enum.TryParse(hostilityResponse.Trim(), true, out hr))
                        return Fail($"Unknown HostilityResponseMode '{hostilityResponse}'.",
                            new { accepted = Enum.GetNames(typeof(HostilityResponseMode)) });
                    pawn.playerSettings.hostilityResponse = hr;
                }

                return new
                {
                    success = true,
                    area = pawn.playerSettings.AreaRestrictionInPawnCurrentMap?.Label,
                    master = pawn.playerSettings.Master?.ThingID,
                    medCare = pawn.playerSettings.medCare.ToString(),
                    hostilityResponse = pawn.playerSettings.hostilityResponse.ToString(),
                    notes,
                };
            }, cancellationToken).ConfigureAwait(false);
        }
    }
}
