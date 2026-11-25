// JawaBenchGates.cs - the Verse half of the scene gates (incident, quest, mental state) and of the incident queue held aside.
// Item RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE. The rules are JawaBenchGatesCore.cs; page:
// design/specs/2026-11-23-bridge-v2/boundary.md §SCENE GATES; hooks: bridgetools/HOOKS.md.
//
// Three gates, each a mechanism with an allow list and an attempt count, for the calm profile to use
// (RIMMANDRAKE_BUILD_CALM_PROFILE_BREACH_LOG_AND_LEASE joins them into a profile with its lease; the tap certificate shows a held
// route and a refused route for each):
//   incident  on the PRESENT awareness hook (JawaBenchAwareness.IncPre on IncidentWorker.TryExecute calls IncidentGate): no new
//             patch site. Arm refuses it when that hook is not on the method.
//   quest     a prefix on QuestManager.Add (QuestGatePre)
//   mental    a prefix on MentalStateHandler.TryStartMentalState (MentalGatePre)
// The two prefixes go on lazily, at the first Arm of their gate, and stay on; an off gate returns at once.
//
// ENGINE FACTS READ OUT OF DECOMPILED 1.6 VIA RimSage (2026-11-24):
//   QuestManager.Add(Quest) returns void. QuestUtility.GenerateQuestAndMakeAvailable calls it and returns the quest whatever Add did,
//   so a caller can still send its offer letter (QuestUtility.SendLetterQuestAvailable) for a quest the gate held: the letter tap
//   records that letter.
//   MentalStateHandler.TryStartMentalState(...) returns bool, false for every refusal: a held attempt returns false, the same as
//   the game's own refusals. The `pawn` field is private.
//   IncidentQueue holds a private List<QueuedIncident> queuedIncidents; IncidentQueue.Add(QueuedIncident) sorts by FireTick.
//   QueuedIncident has private int fireTick, retryDurationTicks and bool triedToFire. IncidentQueueTick fires an untried entry when
//   FireTick <= TicksGame, and drops a tried entry when FireTick + RetryDurationTicks <= TicksGame: so a held entry must have its
//   fire tick moved, and its retry window keeps its length (both absolute ends move).
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;
using K = JawaBench.BridgeTools.JawaBenchGatesCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchGates
    {
        internal const string HarmonyId = "jawabench.gates";
        internal static readonly K.Gates G = new K.Gates();
        internal static string PatchStatus = "not patched";
        private static AccessTools.FieldRef<IncidentQueue, List<QueuedIncident>> _queued;
        private static AccessTools.FieldRef<QueuedIncident, int> _fireTick, _retry;

        static JawaBenchGates()
        {
            foreach (var g in G.All) g.Sink = () => JawaBenchWorld.LiveSink;
        }

        private static bool OnMain() { try { return UnityData.IsInMainThread; } catch { return false; } }
        private static long Tick() { try { return Find.TickManager != null ? Find.TickManager.TicksGame : -1; } catch { return -1; } }

        /// <summary>A canonical world save is loaded: the cached policy (a hook reads it; Arm reads the live one).</summary>
        private static bool Campaign() { try { return JawaBenchCompanionSafety.CurrentPolicy.DenyCampaignFamilies; } catch { return true; } }

        // ------------------------------------------------------------------ arm, release, the queue (main thread)
        /// <summary>Arm one gate (incident, quest or mental) for the game now loaded. allow: comma names (incident def, quest root
        /// def, mental state def); a name listed N times goes through N times. null when armed, else the refusal.</summary>
        internal static string Arm(string kind, string allow)
        {
            try
            {
                if (!UnityData.IsInMainThread) return "REFUSED: not on the main thread";
                var g = G.Of(kind);
                if (g == null) return "REFUSED: no gate '" + kind + "' (incident, quest, mental)";
                bool campaign = JawaBenchCompanionSafety.PolicyNow().DenyCampaignFamilies;
                if (campaign) return g.Arm(Current.Game, true, allow);
                string off = g == G.GIncident ? IncidentHookOff() : EnsurePatched();
                if (off != null) return "REFUSED: the " + g.Kind + " gate has no hook: " + off;
                return g.Arm(Current.Game, false, allow);
            }
            catch (Exception e) { return "REFUSED: " + e.GetType().Name + ": " + e.Message; }
        }

        internal static void Release(string kind, string why)
        {
            foreach (var g in G.All) if (kind == null || string.Equals(g.Kind, kind, StringComparison.OrdinalIgnoreCase)) g.Release(why);
        }

        /// <summary>null while the awareness prefix is on IncidentWorker.TryExecute, read from Harmony, else why not.</summary>
        internal static string IncidentHookOff()
        {
            JawaBenchAwareness.EnsureInstalled();
            var m = AccessTools.Method(typeof(IncidentWorker), "TryExecute", new[] { typeof(IncidentParms) });
            if (m == null) return "IncidentWorker.TryExecute not found";
            var i = Harmony.GetPatchInfo(m);
            bool on = i != null && i.Prefixes.Any(p => p.PatchMethod != null && p.PatchMethod.Name == "IncPre" && p.PatchMethod.DeclaringType == typeof(JawaBenchAwareness));
            return on ? null : "the awareness prefix is not on IncidentWorker.TryExecute (awareness: " + JawaBenchAwareness.InstallStatus + ")";
        }

        /// <summary>Take the incident queue aside. null when held, else the refusal (the queue is untouched). report: the entries
        /// past their retry window, which are not given back.</summary>
        internal static string HoldQueue(List<string> report)
        {
            try
            {
                if (!UnityData.IsInMainThread) return "REFUSED: not on the main thread";
                var q = Find.Storyteller != null ? Find.Storyteller.incidentQueue : null;
                if (q == null) return "REFUSED: no storyteller or incident queue";
                if (!QueueFields()) return "REFUSED: the fields of IncidentQueue or QueuedIncident were not found";
                var list = _queued(q);
                var entries = new List<K.QEntry>();
                foreach (var qi in list)
                    entries.Add(new K.QEntry
                    {
                        Def = qi.FiringIncident != null && qi.FiringIncident.def != null ? qi.FiringIncident.def.defName : null,
                        FireTick = qi.FireTick, RetryEnd = (long)qi.FireTick + qi.RetryDurationTicks, Tried = qi.TriedToFire, Ref = qi,
                    });
                var why = G.Queue.Hold(Current.Game, JawaBenchCompanionSafety.PolicyNow().DenyCampaignFamilies, Tick(), entries, report);
                if (why == null) list.Clear();
                return why;
            }
            catch (Exception e) { return "REFUSED: " + e.GetType().Name + ": " + e.Message; }
        }

        /// <summary>Give the held entries back with both absolute ticks moved by the ticks held. Returns how many went back;
        /// report names each entry that did not.</summary>
        internal static int GiveBackQueue(List<string> report)
        {
            if (!UnityData.IsInMainThread) { report?.Add("not on the main thread: nothing given back, the entries stay aside"); return 0; }
            var q = Find.Storyteller != null ? Find.Storyteller.incidentQueue : null;
            var back = G.Queue.GiveBack(q != null ? Current.Game : null, Tick(), report);
            int n = 0;
            foreach (var e in back)
            {
                try
                {
                    var qi = (QueuedIncident)e.Ref;
                    _fireTick(qi) = (int)e.FireTick;
                    _retry(qi) = (int)e.RetryDuration;
                    q.Add(qi);
                    n++;
                }
                catch (Exception ex) { report?.Add("not given back (" + ex.GetType().Name + "): " + e.Text()); }
            }
            return n;
        }

        private static bool QueueFields()
        {
            if (_queued != null && _fireTick != null && _retry != null) return true;
            try
            {
                _queued = AccessTools.FieldRefAccess<IncidentQueue, List<QueuedIncident>>("queuedIncidents");
                _fireTick = AccessTools.FieldRefAccess<QueuedIncident, int>("fireTick");
                _retry = AccessTools.FieldRefAccess<QueuedIncident, int>("retryDurationTicks");
                return true;
            }
            catch { _queued = null; return false; }
        }

        internal static string Summary() { return G.Summary(); }

        // ------------------------------------------------------------------ hooks
        /// <summary>Main thread. null when the quest and mental prefixes are on, else why not.</summary>
        internal static string EnsurePatched()
        {
            try
            {
                if (!UnityData.IsInMainThread) return PatchStatus = "not on the main thread";
                var h = new Harmony(HarmonyId);
                HarmonyMethod Hm(string n) => new HarmonyMethod(typeof(JawaBenchGates).GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic)) { priority = Priority.First };
                var quest = AccessTools.Method(typeof(QuestManager), "Add", new[] { typeof(Quest) });
                var mental = AccessTools.Method(typeof(MentalStateHandler), "TryStartMentalState");
                if (quest == null || mental == null)
                    return PatchStatus = "not found:" + (quest == null ? " QuestManager.Add" : "") + (mental == null ? " MentalStateHandler.TryStartMentalState" : "");
                if (!Mine(quest)) h.Patch(quest, prefix: Hm(nameof(QuestGatePre)));
                if (!Mine(mental)) h.Patch(mental, prefix: Hm(nameof(MentalGatePre)));
                PatchStatus = "patched";
                return null;
            }
            catch (Exception e) { return PatchStatus = "patch failed: " + e.GetType().Name + ": " + e.Message; }
        }

        private static bool Mine(MethodBase m)
        {
            var i = Harmony.GetPatchInfo(m);
            return i != null && i.Prefixes.Any(p => p.owner == HarmonyId);
        }

        /// <summary>Who called the gated method: the first frame that is not ours, not Harmony's replacement and not the method.</summary>
        private static string CallerOf(Type target, string method)
        {
            var st = new StackTrace(1, false);
            for (int i = 0; i < st.FrameCount; i++)
            {
                var m = st.GetFrame(i)?.GetMethod();
                if (m == null) continue;
                var t = m.DeclaringType;
                if (t == null) continue;                                       // a dynamic method: Harmony's replacement
                var n = t.FullName ?? t.Name;
                if (n.StartsWith("JawaBench.BridgeTools.JawaBenchGates", StringComparison.Ordinal) ||
                    n.StartsWith("JawaBench.BridgeTools.JawaBenchAwareness", StringComparison.Ordinal) || n.StartsWith("HarmonyLib", StringComparison.Ordinal)) continue;
                if (t == target && m.Name == method) continue;
                return n + "." + m.Name;
            }
            return "unknown";
        }

        /// <summary>The incident gate, called by JawaBenchAwareness.IncPre. true: the incident runs.</summary>
        internal static bool IncidentGate(IncidentWorker worker, IncidentParms parms, bool runOriginal)
        {
            try
            {
                var g = G.GIncident;
                if (!g.On) return true;
                return g.Decide(OnMain(), runOriginal, Current.Game, Campaign(), worker != null && worker.def != null ? worker.def.defName : null,
                                () => CallerOf(typeof(IncidentWorker), "TryExecute"),
                                () => parms == null ? null : (parms.target is Map m ? "map " + m.uniqueID : parms.target != null ? parms.target.GetType().Name : "no target") +
                                                              (parms.quest != null ? ", quest " + parms.quest.id : "") + (parms.forced ? ", forced" : ""),
                                Tick());
            }
            catch { return true; }
        }

        private static bool QuestGatePre(Quest quest, bool __runOriginal)
        {
            try
            {
                var g = G.GQuest;
                if (!g.On) return true;
                return g.Decide(OnMain(), __runOriginal, Current.Game, Campaign(), quest != null && quest.root != null ? quest.root.defName : null,
                                () => CallerOf(typeof(QuestManager), "Add"), () => quest == null ? "null quest" : "quest " + quest.id + " " + quest.name, Tick());
            }
            catch { return true; }
        }

        private static bool MentalGatePre(MentalStateDef stateDef, bool forced, Pawn ___pawn, bool __runOriginal, ref bool __result)
        {
            try
            {
                var g = G.GMental;
                if (!g.On) return true;
                bool run = g.Decide(OnMain(), __runOriginal, Current.Game, Campaign(), stateDef != null ? stateDef.defName : null,
                                    () => CallerOf(typeof(MentalStateHandler), "TryStartMentalState"),
                                    () => ___pawn == null ? null : "pawn " + ___pawn.thingIDNumber + (JawaBenchCast.AliasNow(___pawn.thingIDNumber) is string a ? " (" + a + ")" : "") +
                                                                   (forced ? ", forced" : ""),
                                    Tick());
                if (!run) __result = false;
                return run;
            }
            catch { return true; }
        }
    }
}
