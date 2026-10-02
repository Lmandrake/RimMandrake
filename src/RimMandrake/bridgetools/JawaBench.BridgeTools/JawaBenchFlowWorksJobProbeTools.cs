// JawaBenchFlowWorksJobProbeTools.cs - FlowWorks dig / fill-in job probe (2026-10-02).
//
// WHY: FlowWorks/northstar/validation_v2.py had two UNCOVERED rows. S6 (the dig-to-depth gate):
// jawa/designate_batch adds Designations directly and so never runs
// Designator_DigCanal.CanDesignateCell. J_workgiver_selection: the script ORDERS the dig and
// fill-in jobs, so WorkGiver_DigCanal / WorkGiver_FillInCanal choosing the designation was never
// exercised (pawn AI timing is noise; run 3 never chose it). This tool asks the mod's own code
// both questions for one cell, without ordering anything.
//
// READ-ONLY CONTRACT: the designator is a fresh instance whose CanDesignateCell is called and
// nothing else (DesignateSingleCell is never called). The WorkGiver is the def's own Worker.
// ⚠ HasJobOnCell has ONE side effect in shipped code: a STALE designation (water, edifice,
// superdeep, toggle off ...) is deleted. The probe snapshots the designation first and, if the
// call deleted it, puts it back and says so (designationDeletedByWorkGiver / restored). JobOnCell
// is called only when HasJobOnCell said yes, and its Job is returned to the pool, never started.
//
// COUPLING: strictly by reflection on FlowWorks types (the companion must register on a mod list
// without FlowWorks); vanilla Designator / WorkGiver_Scanner are compile-time. Every resolve
// failure is a loud Fail naming what was missing.
//
// THREAD AFFINITY: everything inside ctx.MainThread.InvokeAsync.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/flowworks_job_probe",
            Description =
                "FlowWorks: for ONE cell, ask the mod's own code (1) would the player's designator accept " +
                "this cell (Designator_DigCanal or Designator_FillInCanal .CanDesignateCell, with its " +
                "refusal reason) and (2) would the WorkGiver hand THIS pawn a job here (WorkGiver_DigCanal " +
                "or WorkGiver_FillInCanal: ShouldSkip, cell among PotentialWorkCellsGlobal, HasJobOnCell, " +
                "and JobOnCell's JobDef) - WITHOUT designating or ordering anything. Also reports the " +
                "pawn-side gates the WorkGiver relies on (work type disabled/active/priority, the giver " +
                "in the pawn's normal giver list, missing capacity, reachability). The pawn is optional: " +
                "without one only the designator half runs. A fogged or out-of-bounds cell is reported, " +
                "not hidden. ⚠ HasJobOnCell DELETES a stale designation in shipped code; this probe " +
                "restores it and reports designationDeletedByWorkGiver=true - treat that as the WorkGiver " +
                "saying the designation is stale. Read-only otherwise.",
            ResultDescription =
                "success, kind, cell, fogged, terrain, designationPresent, designator{accepted, reason}, " +
                "workGiver{def, shouldSkip, cellInPotentialWorkCells, hasJobOnCell, jobDef, " +
                "designationDeletedByWorkGiver, designationRestored} or null, pawn{id, workType, " +
                "workTypeDisabled, workActive, priority, giverInNormalList, missingCapacity, canReach} or " +
                "null, ticksGame.")]
        public static async Task<object> FlowWorksJobProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map cell X.")] int x,
            [ToolParameter(Description = "Map cell Z.")] int z,
            [ToolParameter(Description = "dig (Designator_DigCanal + WorkGiver_DigCanal, the default) or fillin " +
                                         "(Designator_FillInCanal + WorkGiver_FillInCanal).",
                DefaultValue = "dig")]
            string kind = "dig",
            [ToolParameter(Description = "Pawn id/ThingID/name for the WorkGiver half. Empty = designator only.")]
            string pawnId = null,
            [ToolParameter(Description = "Pass forced=true to the WorkGiver (a player right-click order). " +
                                         "Default false = the pawn's own unprompted scan.", DefaultValue = false)]
            bool forced = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                string k = (kind ?? "dig").Trim().ToLowerInvariant();
                string desName, workerName, designatorName;
                if (k == "dig") { desName = "RM_DigCanal"; designatorName = "Designator_DigCanal"; workerName = "WorkGiver_DigCanal"; }
                else if (k == "fillin") { desName = "RM_FillInCanal"; designatorName = "Designator_FillInCanal"; workerName = "WorkGiver_FillInCanal"; }
                else return Fail("kind must be dig or fillin, got '" + kind + "'.");

                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(map)) return Fail("Cell out of bounds: " + c);
                Type desType = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks." + designatorName);
                Type wgType = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks." + workerName);
                DesignationDef desDef = DefDatabase<DesignationDef>.GetNamedSilentFail(desName);
                var missing = new List<string>();
                if (desType == null) missing.Add(designatorName);
                if (wgType == null) missing.Add(workerName);
                if (desDef == null) missing.Add("DesignationDef " + desName);
                WorkGiverDef wgDef = wgType == null ? null
                    : DefDatabase<WorkGiverDef>.AllDefsListForReading.FirstOrDefault(d => d.giverClass == wgType);
                if (wgType != null && wgDef == null) missing.Add("WorkGiverDef with giverClass " + workerName);
                if (missing.Count > 0) return Fail("FlowWorks types/defs not found (is the mod loaded?)", new { missing });

                try
                {
                    // (1) the designator, exactly as the player's drag would ask it
                    var designator = Activator.CreateInstance(desType) as Designator;
                    if (designator == null) return Fail(designatorName + " is not a Designator.");
                    AcceptanceReport ar = designator.CanDesignateCell(c);
                    bool desBefore = map.designationManager.DesignationAt(c, desDef) != null;

                    // (2) the WorkGiver for one pawn
                    object wgOut = null, pawnOut = null;
                    if (!string.IsNullOrWhiteSpace(pawnId))
                    {
                        Pawn pawn = FindPawn(pawnId, out string perr);
                        if (pawn == null) return Fail("Pawn not found: " + perr);
                        if (pawn.Map != map) return Fail("Pawn " + pawn.ThingID + " is not on the current map.");
                        var worker = wgDef.Worker as WorkGiver_Scanner;
                        if (worker == null) return Fail(workerName + "'s Worker is not a WorkGiver_Scanner.");

                        WorkTypeDef wt = wgDef.workType;
                        bool wtDisabled = wt != null && pawn.WorkTypeIsDisabled(wt);
                        bool wtActive = wt != null && pawn.workSettings != null && pawn.workSettings.EverWork && pawn.workSettings.WorkIsActive(wt);
                        int prio = (wt != null && pawn.workSettings != null && pawn.workSettings.EverWork) ? pawn.workSettings.GetPriority(wt) : -1;
                        bool inList = pawn.workSettings != null && pawn.workSettings.EverWork
                            && pawn.workSettings.WorkGiversInOrderNormal.Any(w => w.def == wgDef);
                        PawnCapacityDef missingCap = worker.MissingRequiredCapacity(pawn);
                        bool canReach = pawn.CanReach(c, worker.PathEndMode, Danger.Deadly);

                        bool skip = worker.ShouldSkip(pawn, forced);
                        bool inCells = worker.PotentialWorkCellsGlobal(pawn).Contains(c);
                        bool has = worker.HasJobOnCell(pawn, c, forced);
                        bool deleted = desBefore && map.designationManager.DesignationAt(c, desDef) == null;
                        bool restored = false;
                        if (deleted)
                        {
                            map.designationManager.AddDesignation(new Designation(c, desDef));
                            restored = map.designationManager.DesignationAt(c, desDef) != null;
                        }
                        string jobDef = null;
                        if (has)
                        {
                            Job job = worker.JobOnCell(pawn, c, forced);
                            jobDef = job?.def?.defName;
                            if (job != null) JobMaker.ReturnToPool(job);
                        }
                        wgOut = new
                        {
                            def = wgDef.defName,
                            shouldSkip = skip,
                            cellInPotentialWorkCells = inCells,
                            hasJobOnCell = has,
                            jobDef,
                            designationDeletedByWorkGiver = deleted,
                            designationRestored = restored
                        };
                        pawnOut = new
                        {
                            id = pawn.ThingID,
                            workType = wt?.defName,
                            workTypeDisabled = wtDisabled,
                            workActive = wtActive,
                            priority = prio,
                            giverInNormalList = inList,
                            missingCapacity = missingCap?.defName,
                            canReach
                        };
                    }

                    return (object)new
                    {
                        success = true,
                        kind = k,
                        cell = new { x, z },
                        fogged = c.Fogged(map),
                        terrain = c.GetTerrain(map)?.defName,
                        designationPresent = desBefore,
                        designator = new { accepted = ar.Accepted, reason = ar.Reason },
                        workGiver = wgOut,
                        pawn = pawnOut,
                        ticksGame = TicksGameSafe()
                    };
                }
                catch (Exception e)
                {
                    return Fail("probe threw " + e.GetType().Name + ": " + e.Message, new { stack = e.StackTrace });
                }
            });
        }
    }
}
