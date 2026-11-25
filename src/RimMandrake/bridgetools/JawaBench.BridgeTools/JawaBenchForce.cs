// JawaBenchForce.cs - the Verse half of the order through the giver, the motive and the force record of BRIDGE v2.0. Item
// RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER. The rules are JawaBenchForceCore.cs; page:
// design/specs/2026-11-23-bridge-v2/boundary.md §THE ORDER THROUGH THE GIVER, THE MOTIVE, THE FORCE RECORD. No Harmony patch.
//
// This file copies no giver's rules. It asks the game's own code and reports what that code said:
//   a WorkGiverDef  -> FloatMenuOptionProvider_WorkGivers.GetWorkGiverOption, the option the player's float menu would show for
//                      that giver and that target (a disabled option's label is the giver's reason); the job starts by that
//                      option's own action (TryTakeOrderedJobPrioritizedWork, job.workGiverDef set by the float menu code);
//   a JobGiver type -> the node of that type in the pawn's duty node, main tree or constant tree, TryIssueJobPackage; its job
//                      starts as Pawn_JobTracker.DetermineNextJob starts one: StartJob(job, InterruptForced, node, ...).
//
// ENGINE FACTS READ OUT OF DECOMPILED 1.6 VIA RimSage (2026-11-25):
//   FloatMenuOptionProvider_WorkGivers.GetWorkGiverOption(Pawn, WorkGiverDef, LocalTargetInfo, FloatMenuContext) is private. It
//   returns null when the giver offers nothing (drafted, not a scanner, not directOrderable, ShouldSkip, no job and no reason), and
//   for a thing target of a giver in an equivalence group it stores the option in the static equivalenceGroupTempStorage[index]
//   and returns null. It refuses a label already in the static tmpUsedLabels. GetWorkGiversOptionsFor yields nothing for a pawn
//   whose main tree has no JobGiver_Work.
//   Pawn_JobTracker.TryTakeOrderedJobPrioritizedWork sets job.workGiverDef only AFTER TryTakeOrderedJob; the float menu sets it
//   before the action, so the job tap sees it at StartJob.
//   Pawn_JobTracker.cs:148 starts a think-tree job as StartJob(job, InterruptForced, sourceNode, false, false, thinkTree, tag).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;
using FC = JawaBench.BridgeTools.JawaBenchForceCore;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        internal static readonly FC.ForceLog ForceLog = new FC.ForceLog();
        private static readonly ForceHost TheForceHost = new ForceHost();

        /// <summary>The force entries of this session, per actor (jawa/session action=state).</summary>
        internal static Dictionary<string, object> ForceSummary(string session) { return ForceLog.Summary(session); }

        [Tool(
            "jawa/order",
            Description =
                "Give one pawn one order at a level of the Minimum Force ladder (BRIDGE v2.0, design/specs/2026-11-23-bridge-v2/boundary.md " +
                "§THE ORDER THROUGH THE GIVER). level=giver (level 3) asks the game's own giver and starts only the job that the giver makes: " +
                "a WorkGiverDef goes through the player's float menu code for that giver and that target, a ThinkNode_JobGiver type is asked " +
                "through TryIssueJobPackage on the node of the pawn's duty, main or constant tree. level=raw (level 4) builds the job and " +
                "starts it through TryTakeOrderedJob: no giver ran. fallback=raw gives the raw order when the giver refuses. A giver's " +
                "refusal is a fact about the mod: success true, given false, reason = the giver's words, nothing started. Every order writes " +
                "a force record (the level of the path that RAN, never the level asked) to the session trace and to jawa/session state. " +
                "One hop: it waits for no tick.",
            ResultDescription =
                "success, given, reason (the giver's), started, queued, levelAsked, levelUsed (null when nothing was forced), via " +
                "(WorkGiverDef:<defName>, the node type, or raw), job (def#loadID of the pawn's job after), startReason, node (where the " +
                "JobGiver node was found: duty, main, constant or fresh; 'float menu' for a work giver), note ('not shown reachable in play' " +
                "for level 4), record, force. A refusal: success false, refused (BAD_ARGS, NO_ACTOR, NO_SUCH_GIVER), message, repair.")]
        public static async Task<object> ForceOrder(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The pawn: a session alias, alias[n], or a pawn id.")]
            string actor = null,
            [ToolParameter(Description = "giver (level 3) or raw (level 4).")]
            string level = "giver",
            [ToolParameter(Description = "For level=giver: a WorkGiverDef defName (e.g. Rescue, HaulGeneral) or a ThinkNode_JobGiver type (e.g. JobGiver_RM_FetchFallen).")]
            string giver = null,
            [ToolParameter(Description = "For level=raw, or fallback=raw: the JobDef to build.")]
            string jobDef = null,
            [ToolParameter(Description = "The target: an alias, a thing id, or 'x,z'. A work giver needs one; a JobGiver chooses its own (this one is then only reported against).")]
            string target = null,
            [ToolParameter(Description = "raw: when the giver refuses, give the raw order instead (recorded asked 3, used 4). Empty: a refusal starts nothing.")]
            string fallback = null)
        {
            var req = new OrderReq { Actor = actor, Level = level, Giver = giver, JobDef = jobDef, Target = target, Fallback = fallback };
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Current.Game == null || Find.CurrentMap == null) return FC.Refusal("NO_GAME", "no map is loaded", "load a game first");
                return FC.Order(req, TheForceHost, ForceLog, JawaBenchHands.SessionId);
            }, cancellationToken).ConfigureAwait(false);
        }

        [Tool(
            "jawa/motive",
            Description =
                "Level 2 of the Minimum Force ladder: give the pawn's lord a new LordJob (through the body of jawa/lord_set_job: SetJob, then " +
                "the graph's starting toil, so every member's duty is issued again), and read the pawn's duty back. A pawn with no lord is " +
                "refused NO_LORD: a motive gives a group a goal, it does not make a group. Writes a force record (level 2). One hop.",
            ResultDescription =
                "success, lordBefore, lordAfter ('lord <loadID> <LordJob type>'), duty (the pawn's DutyDef after), levelAsked, levelUsed, " +
                "record, force. A refusal: success false, refused (BAD_ARGS, NO_ACTOR, NO_LORD, MOTIVE_NOT_SET), message, repair.")]
        public static async Task<object> ForceMotive(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The pawn: a session alias, alias[n], or a pawn id.")]
            string actor = null,
            [ToolParameter(Description = "LordJob type, e.g. LordJob_AssaultColony.")]
            string lordJob = null,
            [ToolParameter(Description = "Constructor arguments 'name=value;name=value', bound by name as jawa/lord_set_job binds them.")]
            string args = null)
        {
            var req = new MotiveReq { Actor = actor, LordJob = lordJob, Args = args };
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Current.Game == null || Find.CurrentMap == null) return FC.Refusal("NO_GAME", "no map is loaded", "load a game first");
                return FC.SetMotive(req, TheForceHost, ForceLog, JawaBenchHands.SessionId);
            }, cancellationToken).ConfigureAwait(false);
        }

        // ============================================================================================ the game
        private sealed class ForceHost : IForceHost
        {
            private static readonly MethodInfo GetOption = AccessTools.Method(typeof(FloatMenuOptionProvider_WorkGivers), "GetWorkGiverOption");
            private static readonly FieldInfo EqStore = AccessTools.Field(typeof(FloatMenuOptionProvider_WorkGivers), "equivalenceGroupTempStorage");
            private static readonly FieldInfo UsedLabels = AccessTools.Field(typeof(FloatMenuOptionProvider_WorkGivers), "tmpUsedLabels");
            private FloatMenuOptionProvider_WorkGivers _provider;

            private static Pawn P(string actor)
            {
                if (string.IsNullOrWhiteSpace(actor)) return null;
                var t = JawaBenchHands.BoundThing(actor.Trim()) ?? HandsFindThing(actor.Trim());
                return t as Pawn;
            }

            private static string JobText(Job j) { return j == null ? null : (j.def != null ? j.def.defName : "?") + "#" + j.loadID.ToString(CultureInfo.InvariantCulture); }

            /// <summary>True with an invalid target for an empty text; false with the fault for a text that names nothing.</summary>
            private static bool Target(string s, Map map, out LocalTargetInfo t, out string bad)
            {
                t = LocalTargetInfo.Invalid; bad = null;
                if (string.IsNullOrWhiteSpace(s)) return true;
                s = s.Trim();
                var parts = s.Split(',');
                int x, z;
                if (parts.Length == 2 && int.TryParse(parts[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out x)
                    && int.TryParse(parts[1].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out z))
                {
                    var c = new IntVec3(x, 0, z);
                    if (!c.InBounds(map)) { bad = "the target cell " + s + " is off the map"; return false; }
                    t = c; return true;
                }
                var th = JawaBenchHands.BoundThing(s) ?? HandsFindThing(s);
                if (th == null) { bad = "no thing '" + s + "' is bound or found"; return false; }
                if (!th.Spawned || th.Map != map) { bad = "the target '" + s + "' is not spawned on the pawn's map"; return false; }
                t = th; return true;
            }

            public string WhyNoActor(string actor)
            {
                var p = P(actor);
                if (p == null) return "no pawn '" + actor + "' is bound or found";
                if (!p.Spawned || p.Map == null) return "'" + actor + "' is not spawned on a map";
                if (p.jobs == null) return "'" + actor + "' has no job tracker";
                return null;
            }

            public GiverAnswer AskGiver(OrderReq r)
            {
                var p = P(r.Actor);
                string name = r.Giver.Trim();
                var wgd = DefDatabase<WorkGiverDef>.GetNamedSilentFail(name);
                if (wgd != null) return AskWork(p, wgd, r);
                var ty = GenTypes.GetTypeInAnyAssembly(name);
                if (ty != null && typeof(ThinkNode_JobGiver).IsAssignableFrom(ty) && !ty.IsAbstract) return AskJobGiver(p, ty, r);
                return new GiverAnswer { Found = false };
            }

            private static GiverAnswer No(string via, string node, string reason) { return new GiverAnswer { Given = false, Via = via, Node = node, Reason = reason }; }

            private GiverAnswer AskWork(Pawn p, WorkGiverDef wgd, OrderReq r)
            {
                LocalTargetInfo t; string bad;
                if (!Target(r.Target, p.Map, out t, out bad)) return new GiverAnswer { Bad = bad };
                if (!t.IsValid) return new GiverAnswer { Bad = "an order through the work giver " + wgd.defName + " needs its target (the float menu is a click on a thing or a cell)" };
                string via = "WorkGiverDef:" + wgd.defName;
                if (p.thinker == null || p.thinker.TryGetMainTreeThinkNode<JobGiver_Work>() == null)
                    return No(via, "float menu", "the pawn's think tree has no JobGiver_Work: the float menu offers it no work order");
                if (GetOption == null) return new GiverAnswer { Bad = "FloatMenuOptionProvider_WorkGivers.GetWorkGiverOption is not in this game version: the bridge cannot ask the float menu" };
                FloatMenuOption opt;
                JobFailReason.Clear();
                try { opt = WorkOption(p, wgd, t); }
                catch (Exception e)
                {
                    var x = e is TargetInvocationException && e.InnerException != null ? e.InnerException : e;
                    return No(via, "float menu", "the float menu code threw " + x.GetType().Name + ": " + x.Message);
                }
                if (opt == null)
                {
                    var facts = new List<string>();
                    if (p.Drafted && !wgd.canBeDoneWhileDrafted) facts.Add("the pawn is drafted and this giver is not done while drafted");
                    if (!(wgd.Worker is WorkGiver_Scanner)) facts.Add("its worker is not a WorkGiver_Scanner");
                    else if (!wgd.directOrderable) facts.Add("the giver is not directOrderable");
                    if (JobFailReason.HaveReason) facts.Add(JobFailReason.Reason);
                    JobFailReason.Clear();
                    return No(via, "float menu", "the float menu offers no order of " + wgd.defName + " for " + t + (facts.Count > 0 ? ": " + string.Join("; ", facts.ToArray()) : ""));
                }
                JobFailReason.Clear();
                if (opt.Disabled || opt.action == null) return No(via, "float menu", opt.Label);
                return new GiverAnswer { Given = true, Via = via, Node = "float menu", Job = opt, Reason = opt.Label };
            }

            private FloatMenuOption WorkOption(Pawn p, WorkGiverDef wgd, LocalTargetInfo t)
            {
                if (_provider == null) _provider = new FloatMenuOptionProvider_WorkGivers();
                int n = DefDatabase<WorkGiverEquivalenceGroupDef>.DefCount;
                var store = EqStore != null ? EqStore.GetValue(null) as FloatMenuOption[] : null;
                if (EqStore != null && (store == null || store.Length != n)) { store = new FloatMenuOption[n]; EqStore.SetValue(null, store); }
                int slot = wgd.equivalenceGroup != null && store != null && wgd.equivalenceGroup.index < store.Length ? wgd.equivalenceGroup.index : -1;
                if (slot >= 0) store[slot] = null;
                var used = UsedLabels != null ? UsedLabels.GetValue(null) as HashSet<string> : null;
                if (used != null) used.Clear();
                var fctx = new FloatMenuContext(new List<Pawn> { p }, t.Cell.ToVector3Shifted(), p.Map);
                var opt = (FloatMenuOption)GetOption.Invoke(_provider, new object[] { p, wgd, t, fctx });
                if (opt == null && slot >= 0 && t.HasThing) { opt = store[slot]; store[slot] = null; }
                if (used != null) used.Clear();
                return opt;
            }

            private static ThinkNode FindNode(Pawn p, Type ty, out string where)
            {
                var roots = new List<KeyValuePair<string, Func<ThinkNode>>>
                {
                    new KeyValuePair<string, Func<ThinkNode>>("duty", () => p.mindState != null && p.mindState.duty != null && p.mindState.duty.def != null ? p.mindState.duty.def.thinkNode : null),
                    new KeyValuePair<string, Func<ThinkNode>>("main", () => p.thinker != null ? p.thinker.MainThinkNodeRoot : null),
                    new KeyValuePair<string, Func<ThinkNode>>("constant", () => p.thinker != null ? p.thinker.ConstantThinkNodeRoot : null),
                };
                foreach (var kv in roots)
                {
                    ThinkNode root;
                    try { root = kv.Value(); } catch (Exception) { continue; }
                    if (root == null) continue;
                    if (root.GetType() == ty) { where = kv.Key; return root; }
                    foreach (var c in root.ChildrenRecursive) if (c != null && c.GetType() == ty) { where = kv.Key; return c; }
                }
                where = null;
                return null;
            }

            private static GiverAnswer AskJobGiver(Pawn p, Type ty, OrderReq r)
            {
                LocalTargetInfo t; string bad;
                if (!Target(r.Target, p.Map, out t, out bad)) return new GiverAnswer { Bad = bad };
                string where;
                var node = FindNode(p, ty, out where);
                if (node == null)
                {
                    try { node = (ThinkNode)Activator.CreateInstance(ty); where = "fresh"; }
                    catch (Exception e) { return new GiverAnswer { Bad = "the JobGiver " + ty.Name + " is in none of the pawn's trees and cannot be made fresh: " + e.GetType().Name + ": " + e.Message }; }
                }
                JobFailReason.Clear();
                ThinkResult res;
                try { res = node.TryIssueJobPackage(p, default(JobIssueParams)); }
                catch (Exception e) { JobFailReason.Clear(); return No(ty.Name, where, "the giver threw " + e.GetType().Name + ": " + e.Message); }
                if (res.Job == null)
                {
                    string why = "the giver gave no job" + (JobFailReason.HaveReason ? ": " + JobFailReason.Reason : "");
                    JobFailReason.Clear();
                    return No(ty.Name, where, why);
                }
                JobFailReason.Clear();
                string onTarget = t.IsValid ? (res.Job.targetA == t ? "; on the asked target" : "; on " + res.Job.targetA + ", not the asked " + t) : "";
                return new GiverAnswer { Given = true, Via = ty.Name, Node = where, Job = res, Reason = JobText(res.Job) + onTarget };
            }

            public StartAnswer StartGiven(OrderReq r, GiverAnswer a)
            {
                var p = P(r.Actor);
                var before = p.jobs.curJob;
                var opt = a.Job as FloatMenuOption;
                if (opt != null)
                {
                    var wgd = DefDatabase<WorkGiverDef>.GetNamedSilentFail(a.Via.Substring("WorkGiverDef:".Length));
                    opt.action();
                    var cj = p.jobs.curJob;
                    bool started = cj != null && !ReferenceEquals(cj, before) && cj.workGiverDef == wgd;
                    bool queued = !started && p.jobs.jobQueue != null && p.jobs.jobQueue.Any(q => q.job != null && q.job.workGiverDef == wgd);
                    return new StartAnswer
                    {
                        Started = started, Queued = queued, Job = JobText(cj),
                        Reason = started ? null : queued ? "the job was queued behind a job that the pawn may not leave"
                                                         : "the option's action started no job of this giver (TryTakeOrderedJobPrioritizedWork refused: the target could not be reserved)",
                    };
                }
                var res = (ThinkResult)a.Job;
                p.jobs.StartJob(res.Job, JobCondition.InterruptForced, res.SourceNode, false, false, p.thinker.MainThinkTree, res.Tag);
                bool st = ReferenceEquals(p.jobs.curJob, res.Job);
                return new StartAnswer { Started = st, Job = JobText(p.jobs.curJob), Reason = st ? null : "StartJob did not keep the giver's job (its pre-toil reservations failed, or it ended at once)" };
            }

            public StartAnswer StartRaw(OrderReq r)
            {
                var p = P(r.Actor);
                var jd = DefDatabase<JobDef>.GetNamedSilentFail(r.JobDef.Trim());
                if (jd == null) return new StartAnswer { Bad = "no JobDef '" + r.JobDef + "'" };
                LocalTargetInfo t; string bad;
                if (!Target(r.Target, p.Map, out t, out bad)) return new StartAnswer { Bad = bad };
                var job = t.IsValid ? JobMaker.MakeJob(jd, t) : JobMaker.MakeJob(jd);
                job.playerForced = true;            // as jawa/ordered_job: an ordered job is a player order
                bool took = p.jobs.TryTakeOrderedJob(job, JobTag.Misc);
                bool started = ReferenceEquals(p.jobs.curJob, job);
                bool queued = !started && p.jobs.jobQueue != null && p.jobs.jobQueue.Any(q => ReferenceEquals(q.job, job));
                return new StartAnswer
                {
                    Started = started, Queued = queued, Job = JobText(p.jobs.curJob),
                    Reason = started ? null : !took ? "TryTakeOrderedJob refused: the pawn could not reserve the job's target" : queued ? "queued behind a job that the pawn may not leave" : "the job ended at once",
                };
            }

            public string LordOf(string actor)
            {
                var p = P(actor);
                var l = p != null ? p.GetLord() : null;
                return l == null ? null : "lord " + l.loadID.ToString(CultureInfo.InvariantCulture) + " " + (l.LordJob != null ? l.LordJob.GetType().Name : "(no job)");
            }

            public MotiveAnswer SetMotive(MotiveReq m)
            {
var setJob = typeof(JawaBenchTerrainTools).GetMethod("LordSetJob", BindingFlags.Public | BindingFlags.Static);   // in a JAWA_GM_TOOLS build only
                if (setJob == null) return new MotiveAnswer { Reason = "this companion was built without JAWA_GM_TOOLS: jawa/lord_set_job is not in it" };
                var p = P(m.Actor);
                var lord = p.GetLord();
                string before = LordOf(m.Actor);
                int idx = p.Map.lordManager.lords.IndexOf(lord);
                if (idx < 0) return new MotiveAnswer { Reason = "the pawn's lord is not in its map's lord manager" };
                Task<object> task;
                try { task = (Task<object>)setJob.Invoke(null, new object[] { JawaBenchHands.InlineCtx, CancellationToken.None, idx, lord.loadID, m.LordJob, m.Args }); }
                catch (TargetInvocationException e) { return new MotiveAnswer { Reason = "jawa/lord_set_job threw " + (e.InnerException ?? e).Message, Before = before, After = LordOf(m.Actor) }; }
                if (!task.IsCompleted) return new MotiveAnswer { Reason = "jawa/lord_set_job did not end inside the hop" };
                if (task.IsFaulted) return new MotiveAnswer { Reason = "jawa/lord_set_job threw " + task.Exception.GetBaseException().Message, Before = before, After = LordOf(m.Actor) };
                string err;
                if (OneHopTools.SaidNo(task.Result, out err)) return new MotiveAnswer { Reason = err, Before = before, After = LordOf(m.Actor) };
                return new MotiveAnswer
                {
                    Done = true, Before = before, After = LordOf(m.Actor),
                    Duty = p.mindState != null && p.mindState.duty != null && p.mindState.duty.def != null ? p.mindState.duty.def.defName : null,
                };
            }

            public long Tick() { return Current.Game != null && Find.TickManager != null ? Find.TickManager.TicksGame : -1; }
            public long Record(string rec, string fields) { return JawaBenchHands.SessionRecord(rec, fields); }
        }
    }
}
