// JawaBenchCast.cs - the Verse half of the standard cast tracks and of the job and reservation taps. Item
// RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY. The rules are JawaBenchCastCore.cs; page:
// design/specs/2026-11-23-bridge-v2/boundary.md §CAST TRACKS AND JOB TAPS; hooks: bridgetools/HOOKS.md.
//
// The cast of a jawa/run_until run is every pawn of the session's bindings (an alias, or a member of a group, `g[0]`).
// The taps go on lazily, at the first run that has a cast, and stay on; with no running run they record nothing (counted).
//
// ENGINE FACTS READ OUT OF DECOMPILED 1.6 VIA RimSage (2026-11-24):
//   Pawn_JobTracker.StartJob(Job newJob, JobCondition lastJobEndCondition, ThinkNode jobGiver, bool resumeCurJobAfterwards, ...,
//   bool fromQueue, ...) ends the current job through CleanupCurrentJob (or SuspendCurrentJob when resumeCurJobAfterwards and the
//   def is suspendable), and may start another job inside itself (an opportunistic job, the queued job's end): StartJob nests.
//   Every job end goes through the private CleanupCurrentJob(JobCondition condition, bool releaseReservations, ...): EndCurrentJob
//   calls it before it starts the next job, so the end record comes before the next start. The `pawn` field is protected.
//   ReservationManager.Reserve(Pawn claimant, Job job, LocalTargetInfo target, int maxPawns, int stackCount, ReservationLayerDef
//   layer, ...) returns false for a refusal; FirstRespectedReserver(target, claimant, layer) names who holds it.
//   Job.loadID is new at every JobMaker.MakeJob, so a pooled Job object read again is a new job.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;
using K = JawaBench.BridgeTools.JawaBenchCastCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchCast
    {
        internal const string HarmonyId = "jawabench.cast";
        internal static readonly K.Taps Tp = new K.Taps();
        internal static string PatchStatus = "not patched";
        private static volatile K.Cast _cast;
        private static T.SceneRun _run;
        private static readonly Sink TheSink = new Sink();

        private sealed class Sink : ICastSink
        {
            public long EmitTap(string rec, string fields)
            {
                var r = _run;
                if (r == null || !ReferenceEquals(JawaBenchSceneTick.Cur, r)) return -2;
                return r.EmitTap(rec, fields);
            }
        }

        static JawaBenchCast()
        {
            Tp.Sink = () => TheSink;
            Tp.CastNow = () => { var r = _run; return r != null && r.Running ? _cast : null; };
        }

        private static bool OnMain() { try { return UnityData.IsInMainThread; } catch { return false; } }

        /// <summary>The alias of a thing of the cast of the live run, or null (the world taps name a cast pawn or thing by it).</summary>
        internal static string AliasNow(int thing) { var c = Tp.CastNow(); return c != null ? c.AliasOf(thing) : null; }

        /// <summary>Give this run the standard cast tracks of these pawns, and put the taps on. Main thread, before Arm.</summary>
        internal static void Join(T.SceneRun run, IList<KeyValuePair<string, Thing>> pawns)
        {
            if (run == null || pawns == null || pawns.Count == 0) return;
            var src = new Source();
            var members = new List<KeyValuePair<string, int>>();
            foreach (var kv in pawns)
            {
                if (kv.Value == null) continue;
                src.Things[kv.Value.thingIDNumber] = kv.Value;
                members.Add(new KeyValuePair<string, int>(kv.Key, kv.Value.thingIDNumber));
            }
            if (members.Count == 0) return;
            EnsurePatched();
            Tp.NewRun();
            var c = new K.Cast(members, src, K.ClockMs, Tp);
            _cast = c;
            _run = run;
            run.Cast = c;
        }

        // ------------------------------------------------------------------ hooks
        /// <summary>Main thread. null when the three taps are on, else why not (the run goes on with its cast tracks, untapped; the
        /// close record's cast.taps says so).</summary>
        internal static string EnsurePatched()
        {
            try
            {
                if (!UnityData.IsInMainThread) return PatchStatus = "not on the main thread";
                var h = new Harmony(HarmonyId);
                HarmonyMethod Hm(string n) => new HarmonyMethod(typeof(JawaBenchCast).GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic)) { priority = Priority.Last };
                var start = AccessTools.Method(typeof(Pawn_JobTracker), "StartJob");
                var end = AccessTools.Method(typeof(Pawn_JobTracker), "CleanupCurrentJob");
                var reserve = AccessTools.Method(typeof(ReservationManager), "Reserve");
                if (start == null || end == null || reserve == null)
                    return PatchStatus = "not found:" + (start == null ? " Pawn_JobTracker.StartJob" : "") + (end == null ? " Pawn_JobTracker.CleanupCurrentJob" : "") + (reserve == null ? " ReservationManager.Reserve" : "");
                if (!Mine(start)) h.Patch(start, prefix: Hm(nameof(StartPre)), postfix: Hm(nameof(StartPost)), finalizer: Hm(nameof(StartFin)));
                if (!Mine(end)) h.Patch(end, prefix: Hm(nameof(EndPre)), postfix: Hm(nameof(EndPost)), finalizer: Hm(nameof(EndFin)));
                if (!Mine(reserve)) h.Patch(reserve, prefix: Hm(nameof(ReservePre)), postfix: Hm(nameof(ReservePost)), finalizer: Hm(nameof(ReserveFin)));
                PatchStatus = "patched";
                return null;
            }
            catch (Exception e) { return PatchStatus = "patch failed: " + e.GetType().Name + ": " + e.Message; }
        }

        private static bool Mine(MethodBase m)
        {
            var i = Harmony.GetPatchInfo(m);
            return i != null && i.Postfixes.Any(p => p.owner == HarmonyId);
        }

        private static K.JobSnap Snap(Job j, JobDriver d)
        {
            var s = default(K.JobSnap);
            if (j == null) return s;
            s.Has = true; s.Id = j.loadID; s.Def = j.def != null ? j.def.defName : null; s.Toil = d != null ? d.CurToilIndex : -1;
            return s;
        }

        private static string Giver(Job j, ThinkNode giver, bool fromQueue)
        {
            if (giver != null) return giver.GetType().Name;
            if (j != null && j.jobGiver != null) return j.jobGiver.GetType().Name;
            if (j != null && j.workGiverDef != null) return "WorkGiverDef:" + j.workGiverDef.defName;   // a work giver's job given outside the tree (the float menu)
            if (fromQueue) return "queue";
            return j != null && j.playerForced ? "player" : "direct";
        }

        private static void StartPre(Pawn_JobTracker __instance, Job newJob, ThinkNode jobGiver, bool fromQueue, bool resumeCurJobAfterwards, out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GStart.Admit(OnMain(), out __state.S)) return;
            try
            {
                var cj = __instance != null ? __instance.curJob : null;
                Tp.Opened(ref __state, Snap(cj, cj != null ? __instance.curDriver : null), resumeCurJobAfterwards && cj != null && cj.def != null && cj.def.suspendable);
                __state.New = Snap(newJob, null);
                __state.NewGiver = newJob != null ? Giver(newJob, jobGiver, fromQueue) : null;
            }
            catch (Exception e) { Tp.GStart.Note("job_start-pre", e); }
        }

        private static void StartPost(Pawn_JobTracker __instance, Job newJob, JobCondition lastJobEndCondition, ThinkNode jobGiver, bool fromQueue, Pawn ___pawn,
                                      bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GStart.Commit(__state.S, __runOriginal)) return;
            try
            {
                if (newJob == null || ___pawn == null) return;
                var cond = lastJobEndCondition == JobCondition.None ? JobCondition.InterruptForced : lastJobEndCondition;   // as StartJob does
                Tp.RecordStart(__state, ___pawn.thingIDNumber, __state.New.Has ? __state.New : Snap(newJob, null),
                               __state.NewGiver ?? Giver(newJob, jobGiver, fromQueue), cond.ToString(),
                               ReferenceEquals(__instance.curJob, newJob));
            }
            catch (Exception e) { Tp.GStart.Note("job_start", e); }
        }

        private static void StartFin(Exception __exception) => Tp.Threw(Tp.GStart, __exception);

        private static void EndPre(Pawn_JobTracker __instance, out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GEnd.Admit(OnMain(), out __state.S)) return;
            try
            {
                var cj = __instance != null ? __instance.curJob : null;
                Tp.Opened(ref __state, Snap(cj, cj != null ? __instance.curDriver : null), false);
            }
            catch (Exception e) { Tp.GEnd.Note("job_end-pre", e); }
        }

        private static void EndPost(JobCondition condition, Pawn ___pawn, bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GEnd.Commit(__state.S, __runOriginal)) return;
            try { if (___pawn != null) Tp.RecordEnd(__state, ___pawn.thingIDNumber, condition.ToString()); }
            catch (Exception e) { Tp.GEnd.Note("job_end", e); }
        }

        private static void EndFin(Exception __exception) => Tp.Threw(Tp.GEnd, __exception);

        private static void ReservePre(out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GReserve.Admit(OnMain(), out __state.S)) return;
            try { Tp.Opened(ref __state, default(K.JobSnap), false); }
            catch (Exception e) { Tp.GReserve.Note("reserve-pre", e); }
        }

        private static void ReservePost(ReservationManager __instance, Pawn claimant, Job job, LocalTargetInfo target, ReservationLayerDef layer, bool __result,
                                        bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GReserve.Commit(__state.S, __runOriginal)) return;
            try
            {
                if (claimant == null) return;
                string holder = null;
                if (!__result && Tp.Wanted(claimant.thingIDNumber))
                {
                    var who = __instance.FirstRespectedReserver(target, claimant, layer);
                    holder = who != null ? who.ThingID : null;
                }
                Tp.RecordReserve(__state, claimant.thingIDNumber, Snap(job, null), Target(target), __result, holder);
            }
            catch (Exception e) { Tp.GReserve.Note("reserve", e); }
        }

        private static void ReserveFin(Exception __exception) => Tp.Threw(Tp.GReserve, __exception);

        private static string Target(LocalTargetInfo t)
        {
            if (t.HasThing) return t.Thing.ThingID;
            return t.IsValid ? t.Cell.x + "," + t.Cell.z : null;
        }

        /// <summary>From JawaBenchSituationalTools.KillPostfix (admitted and contained there): the kill record of a cast pawn.</summary>
        internal static void OnKill(Pawn p, DamageInfo? dinfo, Hediff culprit)
        {
            if (p == null || _cast == null) return;
            string why = culprit != null && culprit.def != null ? "hediff " + culprit.def.defName
                       : dinfo.HasValue && dinfo.Value.Def != null ? "damage " + dinfo.Value.Def.defName : null;
            Tp.Kill(p.thingIDNumber, why);
        }

        // ------------------------------------------------------------------ the twelve fields
        private sealed class Source : ICastSource
        {
            internal readonly Dictionary<int, Thing> Things = new Dictionary<int, Thing>();
            private readonly Dictionary<int, Cache> _cache = new Dictionary<int, Cache>();
            private static readonly object True = true, False = false;
            private static readonly object[] Boxed = MakeBoxes(256);
            private static readonly string[] Rot = { "north", "east", "south", "west" };

            private sealed class Cache
            {
                public int Px = int.MinValue, Pz, Job = int.MinValue, Carried = int.MinValue;
                public string Pos, JobText, CarriedText, HolderText, FactionText;
                public object Holder, Faction;
            }

            private static object[] MakeBoxes(int n) { var a = new object[n]; for (int i = 0; i < n; i++) a[i] = (double)i; return a; }
            private static object Box(int v) { return v >= 0 && v < Boxed.Length ? Boxed[v] : (object)(double)v; }
            private static object B(bool v) { return v ? True : False; }

            public int Successor(int thing, out string why)
            {
                why = null;
                Thing t;
                if (!Things.TryGetValue(thing, out t)) return -1;
                var p = t as Pawn;
                if (p == null || !p.Dead) return -1;
                var c = p.Corpse;
                if (c == null || c.Destroyed) return -1;
                Things[c.thingIDNumber] = c;
                why = "dead: its corpse";
                return c.thingIDNumber;
            }

            public string Read(int thing, object[] v)
            {
                Thing t;
                if (!Things.TryGetValue(thing, out t) || t == null) return "gone";
                var p = t as Pawn ?? (t as Corpse)?.InnerPawn;
                if (p == null || (t.Destroyed && !(t is Pawn && p.Dead))) return "gone";
                Cache k;
                if (!_cache.TryGetValue(thing, out k)) _cache[thing] = k = new Cache();
                var at = t.PositionHeld;
                if (at.x != k.Px || at.z != k.Pz || k.Pos == null) { k.Px = at.x; k.Pz = at.z; k.Pos = at.x + "," + at.z; }
                v[0] = k.Pos;
                v[1] = Rot[p.Rotation.AsInt & 3];
                var job = p.CurJob;
                int jid = job != null ? job.loadID : -1;
                if (jid != k.Job) { k.Job = jid; k.JobText = job != null ? (job.def != null ? job.def.defName : "?") + "#" + jid : null; }
                v[2] = k.JobText;
                v[3] = job != null && p.jobs != null && p.jobs.curDriver != null ? Box(p.jobs.curDriver.CurToilIndex) : null;
                v[4] = p.health != null && p.health.summaryHealth != null ? Box((int)Math.Round(p.health.summaryHealth.SummaryHealthPercent * 100f)) : null;
                v[5] = B(p.Downed);
                v[6] = B(p.Dead);
                v[7] = p.MentalStateDef != null ? p.MentalStateDef.defName : null;
                var carried = p.carryTracker != null ? p.carryTracker.CarriedThing : null;
                int cid = carried != null ? carried.thingIDNumber : -1;
                if (cid != k.Carried) { k.Carried = cid; k.CarriedText = carried != null ? carried.ThingID : null; }
                v[8] = k.CarriedText;
                var holder = t.ParentHolder;
                if (!ReferenceEquals(holder, k.Holder) || k.HolderText == null) { k.Holder = holder; k.HolderText = HolderName(holder); }
                v[9] = k.HolderText;
                var f = p.Faction;
                if (!ReferenceEquals(f, k.Faction)) { k.Faction = f; k.FactionText = f != null ? (f.def != null ? f.def.defName : "?") + "#" + f.loadID : null; }
                v[10] = k.FactionText;
                v[11] = B(p.Drafted);
                return null;
            }

            private static string HolderName(IThingHolder h)
            {
                if (h == null) return "none";
                if (h is Map) return "map";
                var th = h as Thing;
                if (th != null) return th.ThingID;
                var carry = h as Pawn_CarryTracker;
                if (carry != null && carry.pawn != null) return carry.pawn.ThingID;
                var owner = h.ParentHolder as Thing;
                return h.GetType().Name + (owner != null ? " of " + owner.ThingID : "");
            }
        }
    }
}
