// JawaBenchZoneTools.cs - Group H: zones/bills/jobs/anomaly/royalty/stuff, the
// six MEDIUM rows from BRIDGE_TOOLS_MEDIUM_REMAINING.md Group H that were NOT
// already covered by an existing tool.
//
// THREE ROWS SKIPPED - already built, verified against source before writing
// a line here:
//   - "create-stockpile / growing zone"  -> jawa/map_zones action=createZone
//        (Zone_Stockpile/Zone_Growing + ZoneManager.RegisterZone, already does
//        the bulk-AddCell-then-CheckContiguous dance this row asks for).
//   - "add/remove zone cells"            -> jawa/map_zones action=paintZone
//        (Zone.AddCell/RemoveCell per cell, refusals reported, CheckContiguous
//        run after - exactly this row's api and its own listed pitfall).
//   - "force-job"                        -> jawa/ordered_job
//        (JobMaker.MakeJob + Pawn_JobTracker.TryTakeOrderedJob for ANY JobDef;
//        the roster's "order_pawn is Goto-only" caveat predates ordered_job).
//
// THE SIX BUILT HERE:
//   jawa/storage_settings   - StorageSettings.Priority + ThingFilter.SetAllow/
//                             SetDisallowAll on a zone OR a storage building.
//   jawa/bill_add           - new Bill_Production(recipe) + BillStack.AddBill,
//                             the "does not ADD a bill" gap jawa/configure_bill
//                             names explicitly in its own Description.
//   jawa/prioritized_work   - Pawn_JobTracker.TryTakeOrderedJobPrioritizedWork,
//                             DIFFERENT from ordered_job's TryTakeOrderedJob -
//                             it also stamps mindState.priorityWork so the
//                             pawn keeps coming back to that cell.
//   jawa/anomaly_knowledge  - ResearchManager.ApplyKnowledge, Anomaly-gated.
//   jawa/royal_title        - Pawn_RoyaltyTracker.SetTitle/SetFavor/GainFavor,
//                             Royalty-gated.
//   jawa/set_stuff          - Thing.SetStuffDirect + the MaxHitPoints cache
//                             clear + hit-point-ratio fix the game's own
//                             CompAbilityEffect_Transmute performs alongside
//                             it (read from source, not guessed).
//
// ⚠ jawa/storage_settings' "Notify_SettingsChanged() is a required post-step"
// warning in the roster is WRONG for the direct API used here, and this file
// says so rather than silently repeating it: ThingFilter's settingsChanged
// callback (Verse/ThingFilter.cs) already calls owner.Notify_SettingsChanged()
// from inside SetAllow/SetDisallowAll, and StorageSettings.Priority's setter
// does its own haul-recalc inline. Calling it a second time would be
// redundant, not wrong, but this file does not - the automatic call is real
// and was confirmed by reading ThingFilter.cs and StorageSettings.cs, not
// assumed from the roster's phrasing.
//
// THREAD AFFINITY: same rule as every sibling file. Everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ---- local helper (this file only) ----------------------------------
        // A zone-or-building resolver for StorageSettings, distinct from
        // JawaBenchJobTools.ResolveSlotGroup (which returns an ISlotGroup for
        // Bill_Production.SetStoreMode). Both a Zone_Stockpile and a
        // Building_Storage implement IStoreSettingsParent directly.
        private static IStoreSettingsParent ResolveStoreSettingsParent(Map map, string spec, out string err)
        {
            err = null;
            var s = (spec ?? "").Trim();
            if (s.Length == 0)
            {
                err = "Give 'target': a storage building's ThingID, or a stockpile zone's label.";
                return null;
            }
            var thing = map.listerThings.AllThings.FirstOrDefault(
                t => string.Equals(t.ThingID, s, StringComparison.OrdinalIgnoreCase));
            if (thing is IStoreSettingsParent sspThing) return sspThing;

            var zone = map.zoneManager.AllZones.FirstOrDefault(
                z => string.Equals(z.label, s, StringComparison.OrdinalIgnoreCase));
            if (zone is IStoreSettingsParent sspZone) return sspZone;

            if (thing != null)
            {
                err = $"'{s}' is a {thing.GetType().Name}, which is not a storage-settings owner (IStoreSettingsParent).";
                return null;
            }
            err = $"No storage building or stockpile zone matching '{s}' (checked spawned ThingIDs and zone labels).";
            return null;
        }

        // ================================================================
        //  jawa/storage_settings
        // ================================================================
        [Tool(
            "jawa/storage_settings",
            Description =
                "Read or write the STORAGE SETTINGS of a stockpile zone or a storage building " +
                "(shelf, storage basket, ...): StoragePriority, and the ThingFilter that decides " +
                "what may be stored - via StorageSettings.Priority and ThingFilter.SetAllow / " +
                "SetDisallowAll. 'target' takes EITHER a stockpile zone label OR a spawned " +
                "building's ThingID (jawa/map_zones action=listZones / jawa/list_things names both). " +
                "Only the fields you pass are changed; give none to just READ the current settings. " +
                "🔑 The haul-list recalc this needs (Notify_SettingsChanged) is CONFIRMED AUTOMATIC by " +
                "reading Verse/ThingFilter.cs: SetAllow and SetDisallowAll already invoke it through " +
                "the filter's settingsChangedCallback, and the Priority setter does its own haul-recalc " +
                "inline - this tool does not call it a second time. " +
                "⚠ If 'target' is a Building_Storage in a StorageGroup, these settings are SHARED - " +
                "every building in the group changes together, which is reported as sharedGroup/" +
                "groupMemberCount so a one-building change is not mistaken for a whole-group one. " +
                "⚠ An unknown ThingDef in 'allow'/'disallow' is REFUSED by name with suggestions, " +
                "never silently skipped.",
            ResultDescription =
                "success, target, kind (Zone_Stockpile|Building_Storage), sharedGroup, " +
                "groupMemberCount, priorityBefore/priorityAfter, allowedCountBefore/After, " +
                "allowedSample[] (capped), changed[] naming what was applied, and refused[] " +
                "naming any ThingDef in allow/disallow that did not resolve.")]
        public static async Task<object> StorageSettingsTool(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Stockpile zone label, or a storage building's ThingID.")]
            string target = null,
            [ToolParameter(Description = "New StoragePriority: Unstored|Low|Normal|Preferred|Important|Critical. Omit to leave unchanged.")]
            string priority = null,
            [ToolParameter(Description = "Comma-separated ThingDef defNames to ALLOW.")]
            string allow = null,
            [ToolParameter(Description = "Comma-separated ThingDef defNames to DISALLOW.")]
            string disallow = null,
            [ToolParameter(Description = "SetDisallowAll() first - clears every allowance before 'allow' is applied. Off by default.")]
            bool disallowAll = false,
            [ToolParameter(Description = "Cap on allowedSample rows. Default 40.")]
            int limit = 40)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err;
                var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                var parent = ResolveStoreSettingsParent(map, target, out err);
                if (parent == null) return Fail(err);

                var settings = parent.GetStoreSettings();
                if (settings == null || settings.filter == null)
                    return Fail($"'{target}' has no StorageSettings to read (GetStoreSettings() returned null or filterless).");

                var priorityBefore = settings.Priority;
                var allowedBefore = settings.filter.AllowedDefCount;

                var changed = new List<string>();
                var refused = new List<object>();

                // Validated BEFORE any mutation below - previously this was checked
                // last, so a bad priority string returned Fail over a filter that
                // disallowAll/disallow/allow had already rewritten in place.
                StoragePriority? parsedPriority = null;
                if (priority != null)
                {
                    StoragePriority pr;
                    if (!Enum.TryParse(priority.Trim(), true, out pr))
                        return Fail($"Unknown priority '{priority}'.", new { accepted = Enum.GetNames(typeof(StoragePriority)) });
                    parsedPriority = pr;
                }

                if (disallowAll)
                {
                    settings.filter.SetDisallowAll();
                    changed.Add("disallowAll");
                }

                if (!string.IsNullOrWhiteSpace(disallow))
                {
                    foreach (var raw in disallow.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                    {
                        var nm = raw.Trim();
                        if (nm.Length == 0) continue;
                        var pd = DefDatabase<ThingDef>.GetNamedSilentFail(nm);
                        if (pd == null) { refused.Add(new { thingDef = nm, action = "disallow", reason = "NoSuchThingDef", suggestions = DefSuggestions<ThingDef>(nm) }); continue; }
                        settings.filter.SetAllow(pd, false);
                        changed.Add("disallow:" + pd.defName);
                    }
                }

                if (!string.IsNullOrWhiteSpace(allow))
                {
                    foreach (var raw in allow.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                    {
                        var nm = raw.Trim();
                        if (nm.Length == 0) continue;
                        var pd = DefDatabase<ThingDef>.GetNamedSilentFail(nm);
                        if (pd == null) { refused.Add(new { thingDef = nm, action = "allow", reason = "NoSuchThingDef", suggestions = DefSuggestions<ThingDef>(nm) }); continue; }
                        settings.filter.SetAllow(pd, true);
                        changed.Add("allow:" + pd.defName);
                    }
                }

                if (parsedPriority.HasValue)
                {
                    settings.Priority = parsedPriority.Value;
                    changed.Add("priority:" + parsedPriority.Value);
                }

                // No priority/allow/disallow/disallowAll given: this IS the read (the
                // tool's own Description says so) - fall through to the same payload
                // a mutating call gets, rather than reporting Fail on a legitimate read.
                var buildingParent = parent as Building_Storage;
                var sharedGroup = buildingParent != null && buildingParent.storageGroup != null;

                return new
                {
                    success = true,
                    message = changed.Count + " change(s) applied" + (refused.Count > 0 ? ", " + refused.Count + " REFUSED" : "") + ".",
                    target,
                    kind = parent.GetType().Name,
                    sharedGroup,
                    groupMemberCount = sharedGroup ? buildingParent.storageGroup.MemberCount : (int?)null,
                    priorityBefore = priorityBefore.ToString(),
                    priorityAfter = settings.Priority.ToString(),
                    allowedCountBefore = allowedBefore,
                    allowedCountAfter = settings.filter.AllowedDefCount,
                    allowedSample = settings.filter.AllowedThingDefs.Take(limit).Select(d => d.defName).ToList(),
                    changed,
                    refused,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/bill_add
        // ================================================================
        [Tool(
            "jawa/bill_add",
            Description =
                "ADD a new production bill to a workbench's BillStack - new Bill_Production(recipe) " +
                "+ BillStack.AddBill. This is the gap jawa/configure_bill names in its own Description " +
                "('This does not ADD a bill') - together the two cover the whole bill lifecycle. " +
                "'giverId' is a spawned IBillGiver's ThingID; 'recipe' must be in that workbench def's " +
                "AllRecipes or the call is REFUSED naming the valid ones - RimWorld's own AddBill float " +
                "menu is built from exactly that list, so a recipe outside it could never appear there " +
                "either. Optional repeatMode/repeatCount/targetCount/storeMode/storeTargetId/" +
                "qualityMin/qualityMax/suspended set the SAME fields jawa/configure_bill exposes, so a " +
                "bill can be fully configured in one call instead of add-then-configure. " +
                "⚠ BillStack.MaxCount is 15 - a full stack is REFUSED, not silently ignored.",
            ResultDescription =
                "success, giverId, recipe, billIndex (position on the stack after adding), and every " +
                "field read back off the new Bill_Production: suspended/repeatMode/repeatCount/" +
                "targetCount/storeMode/qualityMin/qualityMax.")]
        public static async Task<object> BillAdd(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID of the bill giver (a spawned workbench).")]
            string giverId = null,
            [ToolParameter(Description = "RecipeDef defName to add.")]
            string recipe = null,
            [ToolParameter(Description = "'repeatcount', 'targetcount' or 'forever'. Default is the engine default (repeatcount).")]
            string repeatMode = null,
            [ToolParameter(Description = "repeatCount, when repeatMode is repeatcount.")]
            int? repeatCount = null,
            [ToolParameter(Description = "targetCount, when repeatMode is targetcount.")]
            int? targetCount = null,
            [ToolParameter(Description = "'dropfloor', 'beststockpile' or 'specificstockpile'. specificstockpile needs storeTargetId.")]
            string storeMode = null,
            [ToolParameter(Description = "Storage building ThingID or stockpile zone label, for storeMode 'specificstockpile'.")]
            string storeTargetId = null,
            [ToolParameter(Description = "Lower bound: Awful/Poor/Normal/Good/Excellent/Masterwork/Legendary.")]
            string qualityMin = null,
            [ToolParameter(Description = "Upper bound, same names as qualityMin.")]
            string qualityMax = null,
            [ToolParameter(Description = "Create the bill suspended. Default false.")]
            bool suspended = false)
        {
            if (string.IsNullOrWhiteSpace(giverId)) return Fail("giverId is required: the ThingID of the workbench.");
            if (string.IsNullOrWhiteSpace(recipe)) return Fail("recipe is required: a RecipeDef defName.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                var thing = map.listerThings.AllThings.FirstOrDefault(
                    t => string.Equals(t.ThingID, giverId.Trim(), StringComparison.OrdinalIgnoreCase));
                if (thing == null) return Fail($"No spawned thing with id '{giverId}'.");
                var giver = thing as IBillGiver;
                if (giver == null) return Fail($"'{giverId}' is a {thing.GetType().Name}, which is not an IBillGiver.");

                var rd = DefDatabase<RecipeDef>.GetNamedSilentFail(recipe.Trim());
                if (rd == null) return Fail($"No RecipeDef '{recipe}'.", new { suggestions = DefSuggestions<RecipeDef>(recipe) });

                var validRecipes = thing.def.AllRecipes;
                if (validRecipes == null || !validRecipes.Contains(rd))
                    return Fail(
                        $"'{rd.defName}' is not a recipe '{thing.def.defName}' can run.",
                        new { validRecipes = (validRecipes ?? new List<RecipeDef>()).Select(r => r.defName).ToList() });

                var stack = giver.BillStack;
                if (stack == null) return Fail($"'{giverId}' has a null BillStack.");
                if (stack.Count >= BillStack.MaxCount)
                    return Fail($"'{giverId}' already has {stack.Count}/{BillStack.MaxCount} bills - the stack is full.");

                var bill = new Bill_Production(rd);
                bill.suspended = suspended;

                if (repeatMode != null)
                {
                    BillRepeatModeDef rmDef;
                    if (!TryParseRepeatMode(repeatMode, out rmDef))
                        return Fail($"Unknown repeatMode '{repeatMode}'.", new { accepted = new[] { "repeatcount", "targetcount", "forever" } });
                    bill.repeatMode = rmDef;
                }
                if (repeatCount.HasValue) bill.repeatCount = repeatCount.Value;
                if (targetCount.HasValue) bill.targetCount = targetCount.Value;

                if (storeMode != null)
                {
                    BillStoreModeDef smDef;
                    if (!TryParseStoreMode(storeMode, out smDef))
                        return Fail($"Unknown storeMode '{storeMode}'.", new { accepted = new[] { "dropfloor", "beststockpile", "specificstockpile" } });
                    ISlotGroup grp = null;
                    if (smDef == BillStoreModeDefOf.SpecificStockpile)
                    {
                        string sgErr;
                        grp = ResolveSlotGroup(map, storeTargetId, out sgErr);
                        if (grp == null) return Fail(sgErr);
                    }
                    bill.SetStoreMode(smDef, grp);
                }

                if (qualityMin != null || qualityMax != null)
                {
                    var min = bill.qualityRange.min;
                    var max = bill.qualityRange.max;
                    if (qualityMin != null && !Enum.TryParse(qualityMin.Trim(), true, out min))
                        return Fail($"Unknown qualityMin '{qualityMin}'.", new { accepted = Enum.GetNames(typeof(QualityCategory)) });
                    if (qualityMax != null && !Enum.TryParse(qualityMax.Trim(), true, out max))
                        return Fail($"Unknown qualityMax '{qualityMax}'.", new { accepted = Enum.GetNames(typeof(QualityCategory)) });
                    bill.qualityRange = new QualityRange(min, max);
                }

                stack.AddBill(bill);

                return new
                {
                    success = true,
                    message = $"Bill for '{rd.defName}' added to '{giverId}' at index {stack.IndexOf(bill)}.",
                    giverId,
                    recipe = rd.defName,
                    billIndex = stack.IndexOf(bill),
                    billCount = stack.Count,
                    suspended = bill.suspended,
                    repeatMode = bill.repeatMode != null ? bill.repeatMode.defName : null,
                    repeatCount = bill.repeatCount,
                    targetCount = bill.targetCount,
                    storeMode = bill.GetStoreMode() != null ? bill.GetStoreMode().defName : null,
                    qualityMin = bill.qualityRange.min.ToString(),
                    qualityMax = bill.qualityRange.max.ToString(),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/prioritized_work
        // ================================================================
        [Tool(
            "jawa/prioritized_work",
            Description =
                "Issue the right-click 'Prioritize' order - Pawn_JobTracker." +
                "TryTakeOrderedJobPrioritizedWork(Job, WorkGiver, IntVec3) - which is DIFFERENT from " +
                "jawa/ordered_job's plain TryTakeOrderedJob: it also stamps " +
                "mindState.priorityWork.Set(cell, workGiverDef) when the WorkGiverDef has " +
                "prioritizeSustains, so the pawn keeps returning to that cell for that WorkGiver after " +
                "the job ends, the way a player's right-click prioritize does. " +
                "'workGiverDef' names the WorkGiverDef whose def.tagToGive is used and whose " +
                "def.giverClass is instantiated as the WorkGiver argument (WorkGiverDef.Worker - the " +
                "same cached instance the game itself uses, built via Activator.CreateInstance). " +
                "'cell' defaults to targetA's cell/position, then the pawn's own position, if not given " +
                "explicitly. Internally this ALWAYS calls TryTakeOrderedJob with requestQueueing=false " +
                "- there is no queueing option on the prioritized-work path in 1.6, so it always " +
                "interrupts. A TRUE return only means ENQUEUED; this waits waitTicks game ticks and " +
                "reads curJob back afterward, same discipline as jawa/ordered_job.",
            ResultDescription =
                "accepted (TryTakeOrderedJobPrioritizedWork's own bool), interruptibleBefore, " +
                "beforeJobDef/afterJobDef, nowRunningRequested, cellUsed, workGiverPrioritizeSustains " +
                "(whether priorityWork was actually stamped). success requires accepted AND " +
                "nowRunningRequested.")]
        public static async Task<object> PrioritizedWork(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID, name or thingIDNumber of the pawn to order.")]
            string pawnId = null,
            [ToolParameter(Description = "JobDef defName, e.g. DoBill, HaulToCell.")]
            string jobDef = null,
            [ToolParameter(Description = "WorkGiverDef defName, e.g. DoBillsWorktable, Mine, GrowerSow.")]
            string workGiverDef = null,
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
            [ToolParameter(Description = "The priority-work cell. Defaults to targetA's cell, else the pawn's position.", DefaultValue = -1)]
            int cellX = -1,
            [ToolParameter(Description = "The priority-work cell Z.", DefaultValue = -1)]
            int cellZ = -1,
            [ToolParameter(Description = "Job.count, for jobs that carry a stack count.")]
            int? count = null,
            [ToolParameter(Description = "Game ticks to wait before reading curJob back.", DefaultValue = 60)]
            int waitTicks = 60,
            [ToolParameter(Description = "Wall-clock ceiling on the wait.", DefaultValue = 15)]
            int timeoutSeconds = 15)
        {
            if (string.IsNullOrWhiteSpace(jobDef)) return Fail("jobDef is required, e.g. 'DoBill' or 'HaulToCell'.");
            if (string.IsNullOrWhiteSpace(workGiverDef)) return Fail("workGiverDef is required, e.g. 'DoBillsWorktable'.");
            if (waitTicks < 0) return Fail($"waitTicks must be >= 0, got {waitTicks}.");
            if (timeoutSeconds < 1 || timeoutSeconds > 300) return Fail($"timeoutSeconds must be 1-300, got {timeoutSeconds}.");

            var startTicks = 0;
            var accepted = false;
            var interruptibleBefore = false;
            string beforeJobDef = null;
            string jdefName = null;
            IntVec3 cellUsed = IntVec3.Invalid;
            bool prioritizeSustains = false;

            var setup = await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var map = Find.CurrentMap;
                if (map == null) return Fail("No current map. Load a game first.");

                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null) return Fail(perr);
                if (pawn.jobs == null) return Fail($"'{pawnId}' has no Pawn_JobTracker.");

                var jd = DefDatabase<JobDef>.GetNamedSilentFail(jobDef.Trim());
                if (jd == null) return Fail($"Unknown JobDef '{jobDef}'.", new { suggestions = DefSuggestions<JobDef>(jobDef) });
                jdefName = jd.defName;

                var wgd = DefDatabase<WorkGiverDef>.GetNamedSilentFail(workGiverDef.Trim());
                if (wgd == null) return Fail($"Unknown WorkGiverDef '{workGiverDef}'.", new { suggestions = DefSuggestions<WorkGiverDef>(workGiverDef) });
                if (wgd.giverClass == null) return Fail($"WorkGiverDef '{wgd.defName}' has no giverClass.");

                WorkGiver giver;
                try { giver = wgd.Worker; }
                catch (Exception ex) { return Fail($"Could not build WorkGiver for '{wgd.defName}': {ex.GetType().Name}: {ex.Message}"); }
                prioritizeSustains = wgd.prioritizeSustains;

                string errA, errB;
                var a = ResolveTarget(map, targetAId, targetAX, targetAZ, out errA);
                if (a == null && errA != null) return Fail(errA);
                var b = ResolveTarget(map, targetBId, targetBX, targetBZ, out errB);
                if (b == null && errB != null) return Fail(errB);

                var job = a.HasValue
                    ? (b.HasValue ? JobMaker.MakeJob(jd, a.Value, b.Value) : JobMaker.MakeJob(jd, a.Value))
                    : JobMaker.MakeJob(jd);
                if (count.HasValue) job.count = count.Value;

                if (cellX >= 0 && cellZ >= 0)
                {
                    var c = new IntVec3(cellX, 0, cellZ);
                    if (!c.InBounds(map)) return Fail($"cell ({cellX},{cellZ}) is outside the map.");
                    cellUsed = c;
                }
                else if (a.HasValue) cellUsed = a.Value.Cell;
                else cellUsed = pawn.Position;

                interruptibleBefore = pawn.jobs.IsCurrentJobPlayerInterruptible();
                beforeJobDef = pawn.jobs.curJob != null && pawn.jobs.curJob.def != null ? pawn.jobs.curJob.def.defName : null;

                var tm = Find.TickManager;
                startTicks = tm != null ? tm.TicksGame : -1;

                accepted = pawn.jobs.TryTakeOrderedJobPrioritizedWork(job, giver, cellUsed);
                return null;
            }, cancellationToken).ConfigureAwait(false);
            if (setup != null) return setup;

            var ticksNow = startTicks;
            var elapsedMs = 0;
            while (ticksNow - startTicks < waitTicks && elapsedMs < timeoutSeconds * 1000)
            {
                cancellationToken.ThrowIfCancellationRequested();
                await Task.Delay(100, cancellationToken).ConfigureAwait(false);
                elapsedMs += 100;
                ticksNow = await ctx.MainThread.InvokeAsync(() => TicksGameSafe(), cancellationToken).ConfigureAwait(false);
            }

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                string perr;
                var pawn = FindPawn(pawnId, out perr);
                if (pawn == null) return new { success = false, accepted, message = "Pawn no longer resolvable after the wait." };

                var afterJobDef = pawn.jobs != null && pawn.jobs.curJob != null && pawn.jobs.curJob.def != null ? pawn.jobs.curJob.def.defName : null;
                var nowRunningRequested = string.Equals(afterJobDef, jdefName, StringComparison.OrdinalIgnoreCase);

                string note = null;
                if (!accepted)
                    note = "TryTakeOrderedJobPrioritizedWork REFUSED: the inner TryTakeOrderedJob call " +
                           "returned false (current job non-interruptible, its driver refuses, or the " +
                           "pawn is on fire).";
                else if (!nowRunningRequested)
                    note = $"Job was accepted (enqueued) but curJob after {waitTicks} tick(s) is " +
                           $"'{afterJobDef ?? "(none)"}', not '{jdefName}' - it may have finished, " +
                           "failed immediately, or be queued rather than current.";

                return new
                {
                    success = accepted && nowRunningRequested,
                    accepted,
                    interruptibleBefore,
                    beforeJobDef,
                    requestedJobDef = jdefName,
                    afterJobDef,
                    nowRunningRequested,
                    cellUsed = new { x = cellUsed.x, z = cellUsed.z },
                    workGiverPrioritizeSustains = prioritizeSustains,
                    ticksElapsed = ticksNow - startTicks,
                    note,
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/anomaly_knowledge
        // ================================================================
        [Tool(
            "jawa/anomaly_knowledge",
            Description =
                "Add to the Anomaly research currency - ResearchManager.ApplyKnowledge(category, " +
                "amount), the same call CompStudiable.Study feeds when a pawn studies an entity. " +
                "⚠ ⚠ REQUIRES ModsConfig.AnomalyActive - ApplyKnowledge's OWN body checks " +
                "ModLister.CheckAnomaly and returns having done NOTHING when it is off, so this tool " +
                "refuses by name up front instead of reporting success for a call that changed nothing. " +
                "⚠ It also no-ops for amount<=0 for the same reason, so that is refused here too. " +
                "The category's CURRENT active project (ResearchManager.GetProject - the one the " +
                "player has selected in the research tab for this category, which may be NONE) is " +
                "read back BEFORE and AFTER via GetKnowledge, so a call whose knowledge had nowhere to " +
                "go (no active project, and no overflowCategory beyond it) is visible rather than " +
                "reading as a silent success.",
            ResultDescription =
                "success, category, amount, projectBefore/projectAfter (ResearchProjectDef defName or " +
                "null), knowledgeBefore/knowledgeAfter (on that project), projectFinishedByThisCall, " +
                "overflowCategory (named if this category has one knowledge could spill into).")]
        public static async Task<object> AnomalyKnowledge(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "KnowledgeCategoryDef defName, e.g. Basic, Advanced, Dark.")]
            string category = null,
            [ToolParameter(Description = "Amount of knowledge to add. Must be > 0.")]
            float amount = 0f)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.AnomalyActive)
                    return Fail("ModsConfig.AnomalyActive is false. ResearchManager.ApplyKnowledge would silently do nothing.");
                if (string.IsNullOrWhiteSpace(category)) return Fail("Give a KnowledgeCategoryDef defName in 'category'.");
                if (amount <= 0f) return Fail($"amount must be > 0, got {amount}. ApplyKnowledge no-ops for amount<=0.");

                var kd = DefDatabase<KnowledgeCategoryDef>.GetNamedSilentFail(category.Trim());
                if (kd == null) return Fail($"No KnowledgeCategoryDef '{category}'.", new { suggestions = DefSuggestions<KnowledgeCategoryDef>(category) });

                var rm = Find.ResearchManager;
                if (rm == null) return Fail("Find.ResearchManager is null.");

                var projectBefore = rm.GetProject(kd);
                var knowledgeBefore = projectBefore != null ? rm.GetKnowledge(projectBefore) : 0f;

                rm.ApplyKnowledge(kd, amount);

                var projectAfter = rm.GetProject(kd);
                var knowledgeAfter = projectAfter != null ? rm.GetKnowledge(projectAfter)
                    : (projectBefore != null ? rm.GetKnowledge(projectBefore) : 0f);
                var finished = projectBefore != null && projectBefore.IsFinished;

                return new
                {
                    success = true,
                    message = projectBefore == null && kd.overflowCategory == null
                        ? $"No active project for '{kd.defName}' and it has no overflowCategory - the " +
                          "knowledge had nowhere to go."
                        : $"{amount} knowledge applied to '{kd.defName}'.",
                    category = kd.defName,
                    amount,
                    projectBefore = projectBefore != null ? projectBefore.defName : null,
                    projectAfter = projectAfter != null ? projectAfter.defName : null,
                    knowledgeBefore,
                    knowledgeAfter,
                    projectFinishedByThisCall = finished,
                    overflowCategory = kd.overflowCategory != null ? kd.overflowCategory.defName : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/royal_title
        // ================================================================
        [Tool(
            "jawa/royal_title",
            Description =
                "Grant/revoke a royal title and set/adjust honor (favor) with a faction - " +
                "Pawn_RoyaltyTracker.SetTitle / SetFavor / GainFavor. " +
                "⚠ ⚠ REQUIRES ModsConfig.RoyaltyActive - every one of these calls is internally " +
                "gated by ModLister.CheckRoyalty and does NOTHING when it is off, so this tool refuses " +
                "by name up front. " +
                "action: 'setTitle' (needs 'title', a RoyalTitleDef defName; also resets favor to 0, " +
                "same as the game's own award path) | 'removeTitle' (SetTitle with a null title; " +
                "grantRewards is forced OFF for this action regardless of the parameter, since " +
                "ApplyRewardsForTitle is meant for gaining a title, not losing one) | 'setFavor' (needs " +
                "'favor', an absolute amount) | 'gainFavor' (needs 'favor', a signed DELTA - negative " +
                "favor can trigger TryUpdateTitle, i.e. a demotion). " +
                "'pawn' must have a non-null royalty tracker (humanlike; refused by name otherwise).",
            ResultDescription =
                "success, pawn, faction, action, titleBefore/titleAfter (RoyalTitleDef defName or " +
                "null), favorBefore/favorAfter.")]
        public static async Task<object> RoyalTitle(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name, as returned by jawa/list_pawns.")]
            string pawn = null,
            [ToolParameter(Description = "Faction defName, or 'Player' for the player faction.")]
            string faction = null,
            [ToolParameter(Description = "'setTitle' | 'removeTitle' | 'setFavor' | 'gainFavor'.")]
            string action = null,
            [ToolParameter(Description = "RoyalTitleDef defName, for action=setTitle.")]
            string title = null,
            [ToolParameter(Description = "Apply the title's reward items/thoughts. Default true. Ignored (forced false) for removeTitle.")]
            bool grantRewards = true,
            [ToolParameter(Description = "Send the usual title-change letter. Default true.")]
            bool sendLetter = true,
            [ToolParameter(Description = "Absolute favor (setFavor) or signed delta (gainFavor).")]
            int? favor = null,
            [ToolParameter(Description =
                "For action=setTitle with grantRewards=true: when jumping straight to a mid-tier " +
                "title on a titleless (or lower-titled) pawn, SetTitle's own ApplyRewardsForTitle " +
                "normally grants the reward for EVERY intermediate title between the pawn's current " +
                "one and the new one, not just the new title - that IS Pawn_RoyaltyTracker.SetTitle's " +
                "own default (rewardsOnlyForNewestTitle=false), matched here. Pass true to restrict " +
                "rewards to just the newest title being granted. Ignored for removeTitle, which " +
                "already forces grantRewards off.")]
            bool rewardsOnlyForNewestTitle = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.RoyaltyActive)
                    return Fail("ModsConfig.RoyaltyActive is false. Pawn_RoyaltyTracker's title/favor calls are gated by ModLister.CheckRoyalty and would do nothing.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.royalty == null) return Fail($"'{pawn}' has no Pawn_RoyaltyTracker (not humanlike, or created before Royalty was active).");

                if (string.IsNullOrWhiteSpace(faction)) return Fail("Give 'faction': a defName, or 'Player'.");
                var fac = ResolveFactionArg(faction);
                if (fac == null) return FactionNotFound(faction);

                var act = (action ?? "").Trim().ToLowerInvariant();
                var titleBefore = p.royalty.GetCurrentTitle(fac);
                var favorBefore = p.royalty.GetFavor(fac);

                switch (act)
                {
                    case "settitle":
                    {
                        if (string.IsNullOrWhiteSpace(title)) return Fail("action=setTitle needs 'title' (a RoyalTitleDef defName).");
                        var td = DefDatabase<RoyalTitleDef>.GetNamedSilentFail(title.Trim());
                        if (td == null) return Fail($"No RoyalTitleDef '{title}'.", new { suggestions = DefSuggestions<RoyalTitleDef>(title) });
                        p.royalty.SetTitle(fac, td, grantRewards, rewardsOnlyForNewestTitle, sendLetter);
                        break;
                    }
                    case "removetitle":
                        p.royalty.SetTitle(fac, null, false, false, sendLetter);
                        break;
                    case "setfavor":
                        if (!favor.HasValue) return Fail("action=setFavor needs 'favor' (absolute amount).");
                        p.royalty.SetFavor(fac, favor.Value);
                        break;
                    case "gainfavor":
                        if (!favor.HasValue) return Fail("action=gainFavor needs 'favor' (signed delta).");
                        p.royalty.GainFavor(fac, favor.Value);
                        break;
                    default:
                        return Fail($"Unknown action '{action}'.", new { accepted = new[] { "setTitle", "removeTitle", "setFavor", "gainFavor" } });
                }

                var titleAfter = p.royalty.GetCurrentTitle(fac);
                var favorAfter = p.royalty.GetFavor(fac);

                return new
                {
                    success = true,
                    message = $"{p.LabelShortCap} / {fac.Name}: title {(titleBefore != null ? titleBefore.defName : "(none)")} -> " +
                              $"{(titleAfter != null ? titleAfter.defName : "(none)")}, favor {favorBefore} -> {favorAfter}.",
                    pawn = p.ThingID,
                    faction = fac.def != null ? fac.def.defName : fac.Name,
                    action = act,
                    titleBefore = titleBefore != null ? titleBefore.defName : null,
                    titleAfter = titleAfter != null ? titleAfter.defName : null,
                    favorBefore,
                    favorAfter,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/set_stuff
        // ================================================================
        [Tool(
            "jawa/set_stuff",
            Description =
                "Change what an EXISTING item is made of - Thing.SetStuffDirect(newStuff) - and repeat " +
                "the follow-up the game's own CompAbilityEffect_Transmute performs (read from source, " +
                "Source/RimWorld/CompAbilityEffect_Transmute.cs), because SetStuffDirect alone leaves " +
                "stale state: StatDefOf.MaxHitPoints.Worker.ClearCacheForThing(thing) (its cache would " +
                "otherwise keep the OLD stuff's max), Notify_ColorChanged() and DirtyMapMesh() (so the " +
                "render catches up), and HitPoints rescaled to preserve the same DAMAGE RATIO under the " +
                "new max rather than being left as a raw number that may now exceed it. " +
                "⚠ Only the MaxHitPoints stat cache is cleared, matching the game's own Transmute path " +
                "exactly - if another modded stat with a StatPart reads stale after this, that is a " +
                "DIFFERENT cache and jawa/stat_cache_bust clears it. " +
                "⚠ 'thing' must be MadeFromStuff and 'stuff' must be a valid stuff for it " +
                "(ThingDef.IsStuff and stuffProps.CanMake(thing.def), the same test GenStuff." +
                "AllowedStuffsFor uses) - REFUSED by name otherwise, listing the allowed stuffs, " +
                "rather than silently writing a stuff field the def's stats will never read.",
            ResultDescription =
                "success, thing, stuffBefore/stuffAfter, hitPointsBefore/After, maxHitPointsBefore/" +
                "After, hpRatioPreserved (hitPointsAfter/maxHitPointsAfter vs the ratio before), " +
                "marketValueBefore/After as an independent instrument that the change took.")]
        public static async Task<object> SetStuff(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id, as accepted by jawa/thing_stats.")]
            string thing = null,
            [ToolParameter(Description = "ThingDef defName of the new stuff, e.g. Plasteel, WoodLog.")]
            string stuff = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string terr;
                var t = SystemToolsFindThing(thing, out terr);
                if (t == null) return Fail(terr ?? "No thing.");

                if (!t.def.MadeFromStuff)
                    return Fail($"'{t.def.defName}' is not MadeFromStuff (no stuffCategories) - SetStuffDirect would set a field its stats never read.");

                if (string.IsNullOrWhiteSpace(stuff)) return Fail("Give a ThingDef defName in 'stuff'.");
                var newStuff = DefDatabase<ThingDef>.GetNamedSilentFail(stuff.Trim());
                if (newStuff == null) return Fail($"No ThingDef '{stuff}'.", new { suggestions = DefSuggestions<ThingDef>(stuff) });

                if (!newStuff.IsStuff || newStuff.stuffProps == null || !newStuff.stuffProps.CanMake(t.def))
                    return Fail(
                        $"'{newStuff.defName}' cannot be the stuff of '{t.def.defName}' (stuffProps.CanMake is false).",
                        new { allowedStuffs = GenStuff.AllowedStuffsFor(t.def).Select(d => d.defName).ToList() });

                var stuffBefore = t.Stuff != null ? t.Stuff.defName : null;
                var hpBefore = t.HitPoints;
                var maxHpBefore = t.MaxHitPoints;
                float marketBefore;
                try { marketBefore = t.GetStatValue(StatDefOf.MarketValue); } catch { marketBefore = -1f; }
                var ratio = maxHpBefore > 0 ? (float)hpBefore / maxHpBefore : 1f;

                t.SetStuffDirect(newStuff);
                StatDefOf.MaxHitPoints.Worker.ClearCacheForThing(t);
                try { t.Notify_ColorChanged(); } catch { }
                if (t.Spawned && t.Map != null) { try { t.DirtyMapMesh(t.Map); } catch { } }

                var maxHpAfter = t.MaxHitPoints;
                var newHp = Mathf.CeilToInt(maxHpAfter * ratio);
                if (maxHpAfter > 0) newHp = Mathf.Clamp(newHp, 1, maxHpAfter);
                t.HitPoints = newHp;

                float marketAfter;
                try { marketAfter = t.GetStatValue(StatDefOf.MarketValue); } catch { marketAfter = -1f; }

                return new
                {
                    success = t.Stuff == newStuff,
                    message = $"{t.ThingID}: stuff {(stuffBefore ?? "(none)")} -> {newStuff.defName}.",
                    thing = t.ThingID,
                    stuffBefore,
                    stuffAfter = t.Stuff != null ? t.Stuff.defName : null,
                    hitPointsBefore = hpBefore,
                    hitPointsAfter = t.HitPoints,
                    maxHitPointsBefore = maxHpBefore,
                    maxHitPointsAfter = maxHpAfter,
                    hpRatioBefore = ratio,
                    hpRatioAfter = maxHpAfter > 0 ? (float)t.HitPoints / maxHpAfter : 1f,
                    marketValueBefore = marketBefore,
                    marketValueAfter = marketAfter,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
