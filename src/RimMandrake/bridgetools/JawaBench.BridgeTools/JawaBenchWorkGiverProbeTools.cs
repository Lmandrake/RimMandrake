// JawaBenchWorkGiverProbeTools.cs - generic WorkGiver_Scanner probe for one pawn and one thing (2026-10-25).
//
// WHY: SUSPENSION_TOWER_DIAGNOSE_UNSUPPLIED_IN_POOL. A blueprint in a deep-water pool got zero deliveries
// with idle builders and steel on the bank, and no bridge tool could ask WHICH gate of the delivery
// WorkGiver refused. jawa/flowworks_job_probe is cell-based and FlowWorks-only; deepfire/debug_workgiver
// is LuminousPigment-only. This one walks the same gates JobGiver_Work walks for a thing-scanner, in
// order, and reports each answer instead of the first false.
//
// READ-ONLY CONTRACT: HasJobOnThing / JobOnThing are called (vanilla's own pure queries); any Job they
// return is described and never started. Construction extras (GenConstruct.CanConstruct,
// FirstBlockingThing, ResourceDeliverJobFor) are resolved by reflection so a signature change is a
// loud "unresolved" field, not a compile break.
//
// THREAD AFFINITY: everything inside ctx.MainThread.InvokeAsync.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
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
            "jawa/workgiver_probe",
            Description =
                "Diagnostic: for ONE pawn, ONE thing and ONE WorkGiverDef (a thing scanner, e.g. " +
                "ConstructDeliverResourcesToBlueprints), walk the gates the work AI walks and report every " +
                "answer: work type active/priority, giver in the pawn's normal list, ShouldSkip, thing among " +
                "PotentialWorkThingsGlobal / request accepts it, forbidden, CanReach with the giver's PathEndMode " +
                "(through every Harmony postfix on CanReach), CanReserve, HasJobOnThing and JobFailReason, " +
                "JobOnThing's job (def, count, targets). For a construction thing it adds GenConstruct.CanConstruct, " +
                "FirstBlockingThing, ResourceDeliverJobFor, the materials still needed with the closest reachable " +
                "stack of each, and the thing's 8 neighbour cells (terrain, standable, reach OnCell). If FlowWorks " +
                "is loaded, the pawn's swim profile. Never starts a job. Read-only.",
            ResultDescription = "success, gates{...}, job{def,count,targetA,targetB,targetC,queueA,queueB} or null, failReason, construction{...}, neighbours[], swim{...}.")]
        public static async Task<object> WorkGiverProbe(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "Thing id (e.g. Blueprint_RM_SuspensionTower17163).")] string thing = null,
            [ToolParameter(Description = "WorkGiverDef defName (default ConstructDeliverResourcesToBlueprints).")] string workGiver = "ConstructDeliverResourcesToBlueprints")
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Pawn p = FindPawn(pawn, out string perr);
                if (p == null) return Fail(perr);
                Thing t = FindLiveThingById(thing, out string terr);
                if (t == null) return Fail(terr);
                if (!t.Spawned || t.Map != p.Map) return Fail("Thing and pawn are not spawned on the same map.");
                WorkGiverDef wgd = DefDatabase<WorkGiverDef>.GetNamedSilentFail(workGiver ?? "");
                if (wgd == null) return Fail("No WorkGiverDef '" + workGiver + "'.");
                var sc = wgd.Worker as WorkGiver_Scanner;
                if (sc == null) return Fail("WorkGiverDef '" + workGiver + "' worker " + wgd.Worker?.GetType().FullName + " is not a WorkGiver_Scanner.");
                Map map = p.Map;
                var errors = new List<string>();
                Func<string, Func<object>, object> safe = (name, f) =>
                {
                    try { return f(); }
                    catch (Exception e) { errors.Add(name + ": " + e.GetType().Name + ": " + e.Message); return "threw"; }
                };

                bool? workActive = p.workSettings != null && wgd.workType != null ? p.workSettings.WorkIsActive(wgd.workType) : (bool?)null;
                int prio = p.workSettings != null && wgd.workType != null ? p.workSettings.GetPriority(wgd.workType) : -1;
                bool inList = p.workSettings != null && p.workSettings.WorkGiversInOrderNormal.Contains(wgd.Worker);
                object shouldSkip = safe("ShouldSkip", () => sc.ShouldSkip(p, false));
                object inPotential = safe("PotentialWorkThingsGlobal", () =>
                {
                    var pot = sc.PotentialWorkThingsGlobal(p);
                    if (pot == null) return (object)"null (uses PotentialWorkThingRequest)";
                    return pot.Contains(t);
                });
                object requestAccepts = safe("PotentialWorkThingRequest", () => sc.PotentialWorkThingRequest.Accepts(t));
                PathEndMode pem = sc.PathEndMode;
                Danger danger = sc.MaxPathDanger(p);
                object canReach = safe("CanReach", () => p.CanReach(t, pem, danger));
                object canReachTouchDeadly = safe("CanReachTouch", () => p.CanReach(t, PathEndMode.Touch, Danger.Deadly));
                object canReserve = safe("CanReserve", () => p.CanReserve(t));
                JobFailReason.Clear();
                object hasJob = safe("HasJobOnThing", () => sc.HasJobOnThing(p, t, false));
                string failReason = JobFailReason.Reason;
                JobFailReason.Clear();
                object job = safe("JobOnThing", () => DescribeJob(sc.JobOnThing(p, t, false)));
                string failReason2 = JobFailReason.Reason;
                JobFailReason.Clear();

                object construction = null;
                if (t is IConstructible ic)
                {
                    var c = new Dictionary<string, object>();
                    c["canConstruct"] = safe("CanConstruct", () => InvokeFilled(typeof(GenConstruct), "CanConstruct", t, p, wgd.workType));
                    c["canConstructFailReason"] = JobFailReason.Reason;
                    JobFailReason.Clear();
                    c["firstBlockingThing"] = safe("FirstBlockingThing", () => (InvokeFilled(typeof(GenConstruct), "FirstBlockingThing", t, p, wgd.workType) as Thing)?.ThingID ?? "none");
                    c["resourceDeliverJobFor"] = safe("ResourceDeliverJobFor", () => DescribeJob(InvokeFilled(typeof(WorkGiver_ConstructDeliverResources), "ResourceDeliverJobFor", t, p, wgd.workType, sc) as Job));
                    c["resourceDeliverFailReason"] = JobFailReason.Reason;
                    JobFailReason.Clear();
                    var needs = new List<object>();
                    foreach (ThingDefCountClass need in ic.TotalMaterialCost())
                    {
                        int needed = ic.ThingCountNeeded(need.thingDef);
                        if (needed <= 0) continue;
                        Thing closest = null;
                        safe("ClosestThingReachable", () => closest = GenClosest.ClosestThingReachable(p.Position, map, ThingRequest.ForDef(need.thingDef),
                            PathEndMode.ClosestTouch, TraverseParms.For(p, Danger.Deadly, TraverseMode.ByPawn), 9999f));
                        var all = map.listerThings.ThingsOfDef(need.thingDef);
                        needs.Add(new
                        {
                            def = need.thingDef.defName,
                            needed,
                            onMap = all.Sum(x => x.stackCount),
                            stacks = all.Take(8).Select(x => new
                            {
                                id = x.ThingID, x = x.Position.x, z = x.Position.z, count = x.stackCount,
                                forbidden = x.IsForbidden(p), reach = p.CanReach(x, PathEndMode.ClosestTouch, Danger.Deadly),
                                reserved = map.reservationManager.IsReservedByAnyoneOf(x, p.Faction)
                            }).ToList(),
                            closestReachable = closest?.ThingID
                        });
                    }
                    c["needs"] = needs;
                    construction = c;
                }

                var neighbours = new List<object>();
                foreach (IntVec3 n in GenAdj.CellsAdjacent8Way(t))
                {
                    if (!n.InBounds(map)) continue;
                    neighbours.Add(new
                    {
                        x = n.x, z = n.z, terrain = n.GetTerrain(map)?.defName, standable = n.Standable(map),
                        walkable = n.Walkable(map), reachOnCell = p.CanReach(n, PathEndMode.OnCell, Danger.Deadly)
                    });
                }

                object swim = safe("swimProfile", () =>
                {
                    Type sw = GenTypes.GetTypeInAnyAssembly("RimMandrake.FlowWorks.Swimming.RM_Swim");
                    MethodInfo pof = sw?.GetMethod("ProfileOf", BindingFlags.Public | BindingFlags.Static);
                    if (pof == null) return (object)"FlowWorks RM_Swim.ProfileOf not found";
                    object pr = pof.Invoke(null, new object[] { p });
                    return pr.GetType().GetFields().ToDictionary(f => f.Name, f => (object)f.GetValue(pr)?.ToString());
                });

                return (object)new
                {
                    success = true,
                    pawn = p.LabelShort, pawnPos = new { x = p.Position.x, z = p.Position.z },
                    pawnJob = p.CurJobDef?.defName, carried = p.carryTracker?.CarriedThing?.ThingID,
                    thing = t.ThingID, thingPos = new { x = t.Position.x, z = t.Position.z, sx = t.def.size.x, sz = t.def.size.z },
                    workGiver = wgd.defName, worker = sc.GetType().FullName,
                    gates = new
                    {
                        workType = wgd.workType?.defName, workActive, priority = prio, giverInNormalList = inList,
                        shouldSkip, inPotential, requestAccepts, forbidden = t.IsForbidden(p),
                        pathEndMode = pem.ToString(), maxDanger = danger.ToString(), canReach, canReachTouchDeadly, canReserve,
                        hasJobOnThing = hasJob
                    },
                    failReason, jobOnThingFailReason = failReason2, job, construction, neighbours, swim, errors,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        private static object DescribeJob(Job j)
        {
            if (j == null) return null;
            Func<LocalTargetInfo, string> d = x => !x.IsValid ? null : x.HasThing ? x.Thing.ThingID : x.Cell.ToString();
            return new
            {
                def = j.def?.defName, count = j.count, targetA = d(j.targetA), targetB = d(j.targetB), targetC = d(j.targetC),
                queueA = j.targetQueueA?.Select(d).ToList(), queueB = j.targetQueueB?.Select(d).ToList()
            };
        }

        /// <summary>Call the static (or instance, on <paramref name="instance"/>) method <paramref name="name"/> of
        /// <paramref name="type"/> with the overload having the most parameters, filling each by type (Thing / IConstructible
        /// / Pawn / WorkTypeDef) or its default; anything else unfillable refuses the overload.</summary>
        private static object InvokeFilled(Type type, string name, Thing t, Pawn p, WorkTypeDef wt, object instance = null)
        {
            var flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
            foreach (MethodInfo m in type.GetMethods(flags).Where(m => m.Name == name).OrderByDescending(m => m.GetParameters().Length))
            {
                if (!m.IsStatic && instance == null) continue;
                var ps = m.GetParameters();
                var args = new object[ps.Length];
                bool ok = true;
                for (int i = 0; i < ps.Length && ok; i++)
                {
                    Type pt = ps[i].ParameterType;
                    if (pt == typeof(Pawn)) args[i] = p;
                    else if (pt.IsInstanceOfType(t)) args[i] = t;
                    else if (pt == typeof(WorkTypeDef)) args[i] = wt;
                    else if (ps[i].HasDefaultValue) args[i] = ps[i].DefaultValue;
                    else if (pt == typeof(bool)) args[i] = false;
                    else if (!pt.IsValueType) args[i] = null;
                    else ok = false;
                }
                if (!ok) continue;
                return m.Invoke(m.IsStatic ? null : instance, args);
            }
            throw new MissingMethodException(type.FullName, name + " (no fillable overload)");
        }
    }
}
