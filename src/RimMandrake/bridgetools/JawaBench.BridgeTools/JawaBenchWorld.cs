// JawaBenchWorld.cs - the Verse half of the world tracks and of the six world-event taps (mental state attempt, quest, letter,
// message, fire, explosion). Item RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY. The rules are JawaBenchWorldCore.cs; page:
// design/specs/2026-11-23-bridge-v2/boundary.md §WORLD EVENT TAPS AND WORLD TRACKS; hooks: bridgetools/HOOKS.md.
//
// Every jawa/run_until run gets the world tracks of its map. The taps go on lazily, at the first run, and stay on; with no
// running run they record nothing (counted).
//
// ENGINE FACTS READ OUT OF DECOMPILED 1.6 VIA RimSage (2026-11-24):
//   MentalStateHandler.TryStartMentalState(MentalStateDef stateDef, string reason, bool forced, ...) returns false for every
//   refusal (blocked, same state, asleep, StateCanOccur false) and true for a start; it can send a letter inside itself. The
//   `pawn` field is private.
//   QuestManager.Add(Quest quest) returns void: a null quest or one already there is refused with a Log.Error.
//   LetterStack.ReceiveLetter has three overloads; the two that take a label make a letter and call ReceiveLetter(Letter, string
//   debugInfo, int delayTicks, bool playSound), so one site sees them all. delayTicks > 0 queues the letter; LetterStackTick
//   receives it again on arrival with no delay. A letter that cannot show is not added to the stack.
//   Messages.Message has four overloads. The three that take a string test the repeat rule (private AcceptsMessage: a live
//   message with the same text and targets) BEFORE they build a Message, and then call Message(Message, bool), which tests it
//   again. So all four are tapped; the outermost call writes the record, and a message the rule hides is still recorded.
//   Both fire routes (FireUtility.TryStartFireIn on a cell, FireUtility.TryAttachFire on a thing) make a Fire and spawn it, so
//   Fire.SpawnSetup is the one choke point; `instigator` and AttachableThing.parent are public fields. A load respawns fires
//   with respawningAfterLoad true: that is not a start.
//   GenExplosion.DoExplosion(IntVec3 center, Map map, float radius, DamageDef damType, Thing instigator, ..., ThingDef weapon,
//   ThingDef projectile, ...) has one overload.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;
using K = JawaBench.BridgeTools.JawaBenchWorldCore;
using T = JawaBench.BridgeTools.JawaBenchSceneTickCore;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchWorld
    {
        internal const string HarmonyId = "jawabench.world";
        internal static readonly K.Taps Tp = new K.Taps();
        internal static string PatchStatus = "not patched";
        private static T.SceneRun _run;
        private static readonly Sink TheSink = new Sink();
        /// <summary>The live run's tap sink (outside any run: -2). The scene gates write their `gate` rows here.</summary>
        internal static ICastSink LiveSink { get { return TheSink; } }
        private static FieldInfo _live;      // Messages.liveMessages, private static

        private sealed class Sink : ICastSink
        {
            public long EmitTap(string rec, string fields)
            {
                var r = _run;
                if (r == null || !ReferenceEquals(JawaBenchSceneTick.Cur, r)) return -2;
                return r.EmitTap(rec, fields);
            }
        }

        static JawaBenchWorld()
        {
            Tp.Sink = () => TheSink;
            Tp.Alias = JawaBenchCast.AliasNow;
        }

        private static bool OnMain() { try { return UnityData.IsInMainThread; } catch { return false; } }

        /// <summary>Give this run the world tracks of its map, and put the taps on. Main thread, before Arm.</summary>
        internal static void Join(T.SceneRun run, int mapId)
        {
            if (run == null) return;
            EnsurePatched();
            run.World = new K.Tracks(new Source(mapId), K.ClockMs, Tp);
            _run = run;
        }

        // ------------------------------------------------------------------ hooks
        /// <summary>Main thread. null when the six taps are on, else why not (the run goes on with its world tracks, untapped;
        /// the close record's world.taps says so).</summary>
        internal static string EnsurePatched()
        {
            try
            {
                if (!UnityData.IsInMainThread) return PatchStatus = "not on the main thread";
                var h = new Harmony(HarmonyId);
                HarmonyMethod Hm(string n) => new HarmonyMethod(typeof(JawaBenchWorld).GetMethod(n, BindingFlags.Static | BindingFlags.NonPublic)) { priority = Priority.Last };
                var mental = AccessTools.Method(typeof(MentalStateHandler), "TryStartMentalState");
                var quest = AccessTools.Method(typeof(QuestManager), "Add", new[] { typeof(Quest) });
                var letter = AccessTools.Method(typeof(LetterStack), "ReceiveLetter", new[] { typeof(Letter), typeof(string), typeof(int), typeof(bool) });
                var fire = AccessTools.DeclaredMethod(typeof(Fire), "SpawnSetup");
                var boom = AccessTools.Method(typeof(GenExplosion), "DoExplosion");
                var msgQuest = AccessTools.Method(typeof(Messages), "Message", new[] { typeof(string), typeof(LookTargets), typeof(MessageTypeDef), typeof(Quest), typeof(bool) });
                var msgTargets = AccessTools.Method(typeof(Messages), "Message", new[] { typeof(string), typeof(LookTargets), typeof(MessageTypeDef), typeof(bool) });
                var msgText = AccessTools.Method(typeof(Messages), "Message", new[] { typeof(string), typeof(MessageTypeDef), typeof(bool) });
                var msgObj = AccessTools.Method(typeof(Messages), "Message", new[] { typeof(Message), typeof(bool) });
                _live = AccessTools.Field(typeof(Messages), "liveMessages");
                var missing = new List<string>();
                if (mental == null) missing.Add("MentalStateHandler.TryStartMentalState");
                if (quest == null) missing.Add("QuestManager.Add");
                if (letter == null) missing.Add("LetterStack.ReceiveLetter(Letter)");
                if (fire == null) missing.Add("Fire.SpawnSetup");
                if (boom == null) missing.Add("GenExplosion.DoExplosion");
                if (msgQuest == null || msgTargets == null || msgText == null || msgObj == null) missing.Add("Messages.Message (an overload)");
                if (_live == null) missing.Add("Messages.liveMessages");
                if (missing.Count > 0) return PatchStatus = "not found: " + string.Join(", ", missing);
                if (!Mine(mental)) h.Patch(mental, prefix: Hm(nameof(MentalPre)), postfix: Hm(nameof(MentalPost)), finalizer: Hm(nameof(MentalFin)));
                if (!Mine(quest)) h.Patch(quest, prefix: Hm(nameof(QuestPre)), postfix: Hm(nameof(QuestPost)), finalizer: Hm(nameof(QuestFin)));
                if (!Mine(letter)) h.Patch(letter, prefix: Hm(nameof(LetterPre)), postfix: Hm(nameof(LetterPost)), finalizer: Hm(nameof(LetterFin)));
                if (!Mine(fire)) h.Patch(fire, prefix: Hm(nameof(FirePre)), postfix: Hm(nameof(FirePost)), finalizer: Hm(nameof(FireFin)));
                if (!Mine(boom)) h.Patch(boom, prefix: Hm(nameof(BoomPre)), postfix: Hm(nameof(BoomPost)), finalizer: Hm(nameof(BoomFin)));
                if (!Mine(msgQuest)) h.Patch(msgQuest, prefix: Hm(nameof(MsgPre)), postfix: Hm(nameof(MsgTargetPost)), finalizer: Hm(nameof(MsgFin)));
                if (!Mine(msgTargets)) h.Patch(msgTargets, prefix: Hm(nameof(MsgPre)), postfix: Hm(nameof(MsgTargetPost)), finalizer: Hm(nameof(MsgFin)));
                if (!Mine(msgText)) h.Patch(msgText, prefix: Hm(nameof(MsgPre)), postfix: Hm(nameof(MsgTextPost)), finalizer: Hm(nameof(MsgFin)));
                if (!Mine(msgObj)) h.Patch(msgObj, prefix: Hm(nameof(MsgPre)), postfix: Hm(nameof(MsgObjPost)), finalizer: Hm(nameof(MsgFin)));
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

        private static K.Who Who(Thing t)
        {
            var w = default(K.Who);
            if (t == null) return w;
            w.Has = true; w.Id = t.thingIDNumber; w.Text = t.ThingID; w.Pawn = t is Pawn;
            return w;
        }

        private static string Cell(IntVec3 c) { return c.IsValid ? c.x.ToString(CultureInfo.InvariantCulture) + "," + c.z.ToString(CultureInfo.InvariantCulture) : null; }

        private static string Targets(LookTargets lt)
        {
            if (lt == null) return null;
            var g = lt.PrimaryTarget;
            if (!g.IsValid) return null;
            if (g.HasThing) return g.Thing.ThingID;
            return g.Cell.IsValid ? Cell(g.Cell) : g.ToString();
        }

        // ---- mental state
        private static void MentalPre(MentalStateHandler __instance, out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GMental.Admit(OnMain(), out __state.S)) return;
            try
            {
                Tp.Opened(ref __state);
                var cur = __instance != null ? __instance.CurStateDef : null;
                __state.Prev = cur != null ? cur.defName : null;
            }
            catch (Exception e) { Tp.GMental.Note("mental-pre", e); }
        }

        private static void MentalPost(MentalStateHandler __instance, MentalStateDef stateDef, string reason, bool forced, Pawn ___pawn, bool __result,
                                       bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GMental.Commit(__state.S, __runOriginal)) return;
            try
            {
                if (___pawn == null) return;
                var now = __instance != null ? __instance.CurStateDef : null;
                Tp.RecordMental(__state, ___pawn.thingIDNumber, stateDef != null ? stateDef.defName : null, reason, forced, __result, now != null ? now.defName : null);
            }
            catch (Exception e) { Tp.GMental.Note("mental", e); }
        }

        private static void MentalFin(Exception __exception) => Tp.Threw(Tp.GMental, __exception);

        // ---- quest
        private static void QuestPre(QuestManager __instance, Quest quest, out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GQuest.Admit(OnMain(), out __state.S)) return;
            try
            {
                Tp.Opened(ref __state);
                __state.Before = quest != null && __instance != null && __instance.Contains(quest);
            }
            catch (Exception e) { Tp.GQuest.Note("quest-pre", e); }
        }

        private static void QuestPost(QuestManager __instance, Quest quest, bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GQuest.Commit(__state.S, __runOriginal)) return;
            try
            {
                bool added = quest != null && !__state.Before && __instance != null && __instance.Contains(quest);
                Tp.RecordQuest(__state, quest != null ? quest.id : -1, quest != null && quest.root != null ? quest.root.defName : null,
                               quest != null ? quest.name : null, added, quest != null && quest.initiallyAccepted);
            }
            catch (Exception e) { Tp.GQuest.Note("quest", e); }
        }

        private static void QuestFin(Exception __exception) => Tp.Threw(Tp.GQuest, __exception);

        // ---- letter
        private static void LetterPre(out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GLetter.Admit(OnMain(), out __state.S)) return;
            try { Tp.Opened(ref __state); }
            catch (Exception e) { Tp.GLetter.Note("letter-pre", e); }
        }

        private static void LetterPost(LetterStack __instance, Letter let, int delayTicks, bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GLetter.Commit(__state.S, __runOriginal)) return;
            try
            {
                if (let == null) return;
                bool shown = delayTicks <= 0 && __instance != null && __instance.LettersListForReading.Contains(let);
                var cl = let as ChoiceLetter;
                Tp.RecordLetter(__state, let.def != null ? let.def.defName : null, let.Label.RawText, delayTicks, shown,
                                cl != null && cl.quest != null ? cl.quest.id : -1, Targets(let.lookTargets));
            }
            catch (Exception e) { Tp.GLetter.Note("letter", e); }
        }

        private static void LetterFin(Exception __exception) => Tp.Threw(Tp.GLetter, __exception);

        // ---- message: four overloads, one guard with its depth kept; the outermost call writes the record
        private static object LastLive()
        {
            var l = _live != null ? _live.GetValue(null) as List<Message> : null;
            return l != null && l.Count > 0 ? l[l.Count - 1] : null;
        }

        private static void MsgPre(out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GMessage.TryEnter(OnMain(), out __state.S)) return;
            try { Tp.Opened(ref __state); __state.Ref = LastLive(); }
            catch (Exception e) { Tp.GMessage.Note("message-pre", e); }
        }

        /// <summary>A message is shown when the call added a live message: the last live one is a new object.</summary>
        private static bool Shown(K.TapState st) { var now = LastLive(); return now != null && !ReferenceEquals(now, st.Ref); }

        private static void MsgTargetPost(string text, LookTargets lookTargets, MessageTypeDef def, bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GMessage.Commit(__state.S, __runOriginal)) return;
            try { Tp.RecordMessage(__state, text, def != null ? def.defName : null, Shown(__state), Targets(lookTargets)); }
            catch (Exception e) { Tp.GMessage.Note("message", e); }
        }

        private static void MsgTextPost(string text, MessageTypeDef def, bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GMessage.Commit(__state.S, __runOriginal)) return;
            try { Tp.RecordMessage(__state, text, def != null ? def.defName : null, Shown(__state), null); }
            catch (Exception e) { Tp.GMessage.Note("message", e); }
        }

        private static void MsgObjPost(Message msg, bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GMessage.Commit(__state.S, __runOriginal)) return;
            try
            {
                if (msg == null) return;
                Tp.RecordMessage(__state, msg.text, msg.def != null ? msg.def.defName : null, Shown(__state), Targets(msg.lookTargets));
            }
            catch (Exception e) { Tp.GMessage.Note("message", e); }
        }

        private static void MsgFin(Exception __exception, K.TapState __state) => Tp.MessageExit(__state, __exception);

        // ---- fire
        private static void FirePre(out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GFire.Admit(OnMain(), out __state.S)) return;
            try { Tp.Opened(ref __state); }
            catch (Exception e) { Tp.GFire.Note("fire-pre", e); }
        }

        private static void FirePost(Fire __instance, bool respawningAfterLoad, bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GFire.Commit(__state.S, __runOriginal)) return;
            try
            {
                if (__instance == null) return;
                Tp.RecordFire(__state, __instance.thingIDNumber, Cell(__instance.Position), Who(__instance.parent), Who(__instance.instigator),
                              Math.Round(__instance.fireSize, 3), respawningAfterLoad);
            }
            catch (Exception e) { Tp.GFire.Note("fire", e); }
        }

        private static void FireFin(Exception __exception) => Tp.Threw(Tp.GFire, __exception);

        // ---- explosion
        private static void BoomPre(out K.TapState __state)
        {
            __state = default(K.TapState);
            if (!Tp.GExplosion.Admit(OnMain(), out __state.S)) return;
            try { Tp.Opened(ref __state); }
            catch (Exception e) { Tp.GExplosion.Note("explosion-pre", e); }
        }

        private static void BoomPost(IntVec3 center, float radius, DamageDef damType, Thing instigator, ThingDef weapon, ThingDef projectile,
                                     bool __runOriginal, K.TapState __state)
        {
            if (!Tp.GExplosion.Commit(__state.S, __runOriginal)) return;
            try
            {
                Tp.RecordExplosion(__state, Cell(center), Math.Round(radius, 3), damType != null ? damType.defName : null, Who(instigator),
                                   weapon != null ? weapon.defName : null, projectile != null ? projectile.defName : null);
            }
            catch (Exception e) { Tp.GExplosion.Note("explosion", e); }
        }

        private static void BoomFin(Exception __exception) => Tp.Threw(Tp.GExplosion, __exception);

        // ------------------------------------------------------------------ the six world tracks
        private sealed class Source : IWorldSource
        {
            private readonly int _mapId;
            private Map _map;
            private static readonly object[] Hours = MakeBoxes(24);
            private readonly List<GameCondition> _conds = new List<GameCondition>();
            private string _condText;
            private readonly List<Window> _wins = new List<Window>();
            private string _winText;
            private int _cx = int.MinValue, _cz, _cX, _cZ, _zoom;
            private string _camText;
            private double _temp = double.NaN;
            private object _tempBox;

            internal Source(int mapId) { _mapId = mapId; }

            private static object[] MakeBoxes(int n) { var a = new object[n]; for (int i = 0; i < n; i++) a[i] = (double)i; return a; }

            private Map TheMap()
            {
                var maps = Find.Maps;
                if (_map != null && maps != null && maps.Contains(_map)) return _map;
                _map = null;
                if (maps == null) return null;
                for (int i = 0; i < maps.Count; i++) if (maps[i].uniqueID == _mapId) return _map = maps[i];
                return null;
            }

            public string Read(object[] v)
            {
                var map = TheMap();
                if (map == null) return "gone";
                v[0] = map.weatherManager != null && map.weatherManager.curWeather != null ? map.weatherManager.curWeather.defName : null;
                v[1] = Conditions(map);
                double t = Math.Round(map.mapTemperature.OutdoorTemp, 1);
                if (!(t == _temp)) { _temp = t; _tempBox = t; }
                v[2] = _tempBox;
                int h = GenLocalDate.HourOfDay(map);
                v[3] = h >= 0 && h < Hours.Length ? Hours[h] : (object)(double)h;
                v[4] = Camera(map);
                v[5] = Windows();
                return null;
            }

            /// <summary>The active game conditions of the map and of the world, by def, sorted; rebuilt only when the set changes.</summary>
            private string Conditions(Map map)
            {
                var a = map.gameConditionManager != null ? map.gameConditionManager.ActiveConditions : null;
                var b = Find.World != null && Find.World.gameConditionManager != null ? Find.World.gameConditionManager.ActiveConditions : null;
                int n = (a != null ? a.Count : 0) + (b != null ? b.Count : 0);
                bool same = n == _conds.Count && _condText != null;
                for (int i = 0; same && a != null && i < a.Count; i++) same = ReferenceEquals(a[i], _conds[i]);
                for (int i = 0, o = a != null ? a.Count : 0; same && b != null && i < b.Count; i++) same = ReferenceEquals(b[i], _conds[o + i]);
                if (same) return _condText;
                _conds.Clear();
                if (a != null) _conds.AddRange(a);
                if (b != null) _conds.AddRange(b);
                var names = new List<string>(_conds.Count);
                foreach (var c in _conds) names.Add(c != null && c.def != null ? c.def.defName : "?");
                names.Sort(string.CompareOrdinal);
                return _condText = string.Join(",", names);
            }

            /// <summary>The view rectangle and the zoom, when the camera is on this map; "elsewhere" when it is not.</summary>
            private string Camera(Map map)
            {
                if (!ReferenceEquals(Find.CurrentMap, map)) return "elsewhere";
                var cd = Find.CameraDriver;
                if (cd == null) return null;
                var r = cd.CurrentViewRect;
                int z = (int)cd.CurrentZoom;
                if (r.minX == _cx && r.minZ == _cz && r.maxX == _cX && r.maxZ == _cZ && z == _zoom && _camText != null) return _camText;
                _cx = r.minX; _cz = r.minZ; _cX = r.maxX; _cZ = r.maxZ; _zoom = z;
                return _camText = r.minX + "," + r.minZ + ".." + r.maxX + "," + r.maxZ + " zoom " + cd.CurrentZoom;
            }

            /// <summary>The open windows, bottom to top, by type; rebuilt only when the stack changes.</summary>
            private string Windows()
            {
                var ws = Find.WindowStack;
                if (ws == null) return null;
                int n = ws.Count;
                bool same = n == _wins.Count && _winText != null;
                for (int i = 0; same && i < n; i++) same = ReferenceEquals(ws[i], _wins[i]);
                if (same) return _winText;
                _wins.Clear();
                var names = new List<string>(n);
                for (int i = 0; i < n; i++) { _wins.Add(ws[i]); names.Add(ws[i] != null ? ws[i].GetType().Name : "?"); }
                return _winText = string.Join(",", names);
            }
        }
    }
}
