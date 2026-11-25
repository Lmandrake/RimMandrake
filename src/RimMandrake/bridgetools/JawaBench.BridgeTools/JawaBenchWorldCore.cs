// JawaBenchWorldCore.cs - the world tracks of a scene run and the six world-event taps: the PURE half (no Verse, no Unity, no
// Harmony). Item RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY. Page: design/specs/2026-11-23-bridge-v2/boundary.md
// §WORLD EVENT TAPS AND WORLD TRACKS. The Verse half is JawaBenchWorld.cs; its hooks are on bridgetools/HOOKS.md.
//
// Compiled into bridgetools/WorldTapsSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
//
// What it does:
//   Tracks - six tracks of the run's map, read at each sample of the run and written as a `track` row named `world.<field>` on
//            change only: weather, game conditions, outdoor temperature, hour, camera (view rectangle and zoom), window stack.
//            Its cost per tick and the six taps' coverage are in the close record's `world` field.
//   Taps   - the recorder of six Harmony taps. Each hook pair goes through a JawaBenchHookGuard: the six rules of HOOKS.md.
//            Each admitted call takes an entry ordinal `ord` at its prefix (shared with no other recorder), so a letter sent
//            inside a mental state's start keeps its call order beside the trace's own `n`.
//              mental     every attempt (`mental_attempt`, started or not), and a second record `mental_start` for a start
//              quest      a quest offered to QuestManager.Add: `quest`, added or refused (already there, or null)
//              letter     `letter`: shown in the stack, queued with a delay, or not shown
//              message    `message`, written whether or not the repeat rule hides it (`shown` false: a live message with the
//                         same text and targets). Only the outermost of the nested Messages.Message calls writes the record.
//              fire       `fire`: a fire spawned (not one restored by a load), with its instigator and what it is attached to
//              explosion  `explosion`: its centre, radius, damage, instigator, weapon and projectile
//            A record outside any running run is dropped and counted. A pawn or thing of the cast carries its alias.
using System;
using System.Diagnostics;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    /// <summary>What the world tracks need of the game.</summary>
    internal interface IWorldSource
    {
        /// <summary>Fill the six fields of JawaBenchWorldCore.Fields. Null when read, else why not ("gone": the map is gone).</summary>
        string Read(object[] into);
    }

    internal static class JawaBenchWorldCore
    {
        static string S(object o) { return JawaBenchCondCore.Canon(o); }

        // ============================================================================================ the world tracks
        /// <summary>The world tracks of 06_build_order.md: their order is the order of the rows of one sample.</summary>
        internal static readonly string[] Fields = { "weather", "conditions", "temp", "hour", "camera", "windows" };

        internal sealed class Tracks : ISceneCast
        {
            readonly IWorldSource _src;
            readonly Func<double> _now;
            readonly Taps _taps;
            object[] _last = new object[Fields.Length], _cur = new object[Fields.Length];
            string _lastSt;
            bool _has;
            public long Samples, Reads, Rows;
            public double Ms, MsMax;
            static readonly string[] Names = MakeNames();

            static string[] MakeNames() { var a = new string[Fields.Length]; for (int i = 0; i < a.Length; i++) a[i] = "world." + Fields[i]; return a; }

            /// <summary>taps: the recorder whose coverage the close record carries (null: none).</summary>
            public Tracks(IWorldSource src, Func<double> nowMs, Taps taps) { _src = src; _now = nowMs; _taps = taps; }

            public void Sample(SceneRow row, long tick, string phase, bool all)
            {
                double t0 = _now();
                Samples++;
                for (int f = 0; f < Fields.Length; f++) _cur[f] = null;
                string st = _src.Read(_cur) ?? "ok";
                Reads++;
                for (int f = 0; f < Fields.Length; f++)
                {
                    bool force = all || !_has || st != _lastSt;
                    if (!force && JawaBenchCondCore.SameValue(_cur[f], _last[f])) continue;
                    var v = st == "ok" ? _cur[f] : null;
                    row(tick, phase, "track", "\"name\":" + S(Names[f]) + ",\"st\":" + S(st) + ",\"v\":" + S(v) + (st == "ok" ? "" : ",\"detail\":" + S(st)));
                    Rows++;
                }
                var swap = _last; _last = _cur; _cur = swap;
                _lastSt = st; _has = true;
                double ms = _now() - t0;
                Ms += ms;
                if (ms > MsMax) MsMax = ms;
            }

            /// <summary>The world tracks have nothing to reconcile: the taps' coverage is in the summary.</summary>
            public void Reconcile(SceneRow row, long tick) { }

            static string R(double v) { return Math.Round(v, 4).ToString(CultureInfo.InvariantCulture); }

            public string Summary()
            {
                double per = Samples > 0 ? Ms / Samples : 0;
                return "{\"tracks\":" + Fields.Length + ",\"samples\":" + Samples + ",\"reads\":" + Reads + ",\"rows\":" + Rows + ",\"ms\":" + R(Ms) +
                       ",\"msMax\":" + R(MsMax) + ",\"msPerTick\":" + R(per) + ",\"taps\":" + (_taps == null ? "null" : _taps.Summary()) + "}";
            }
        }

        // ============================================================================================ the taps
        /// <summary>Who or what caused a fire or an explosion, as a tap sees it.</summary>
        internal struct Who
        {
            public bool Has;
            public int Id;
            public string Text;     // ThingID
            public bool Pawn;
            public string Kind() { return !Has ? "none" : Pawn ? "pawn" : "thing"; }
        }

        /// <summary>The per-call state a prefix hands its own postfix and finalizer (Harmony __state): never a static.</summary>
        internal struct TapState
        {
            public JawaBenchHookGuard.Scope S;
            public long Ord;
            public bool Before;     // what the prefix saw: the quest was already there / a message
            public string Prev;     // the mental state before the call
            public object Ref;      // the last live message before the call
        }

        internal sealed class Taps
        {
            public readonly JawaBenchHookGuard GMental = new JawaBenchHookGuard("world.mental", allowNesting: true);
            public readonly JawaBenchHookGuard GQuest = new JawaBenchHookGuard("world.quest", allowNesting: true);
            public readonly JawaBenchHookGuard GLetter = new JawaBenchHookGuard("world.letter", allowNesting: true);
            /// <summary>Kept depth (TryEnter/Exit): a string overload of Messages.Message calls Message(Message) inside itself.</summary>
            public readonly JawaBenchHookGuard GMessage = new JawaBenchHookGuard("world.message", allowNesting: true);
            public readonly JawaBenchHookGuard GFire = new JawaBenchHookGuard("world.fire", allowNesting: true);
            public readonly JawaBenchHookGuard GExplosion = new JawaBenchHookGuard("world.explosion", allowNesting: true);
            /// <summary>The live run, or nothing. Read at each record.</summary>
            public Func<ICastSink> Sink;
            /// <summary>The alias of a thing of the cast of the live run, or null.</summary>
            public Func<int, string> Alias;
            long _ord;
            public long Records, Outside, Dropped, Inner, Loaded;

            public JawaBenchHookGuard[] Guards { get { return new[] { GMental, GQuest, GLetter, GMessage, GFire, GExplosion }; } }

            /// <summary>The prefix half: thread and admission first (Admit), and only then the entry ordinal. Nothing is touched
            /// before the thread check.</summary>
            public bool Enter(JawaBenchHookGuard g, bool onMain, out TapState st)
            {
                st = default(TapState);
                if (!g.Admit(onMain, out st.S)) return false;
                Opened(ref st);
                return true;
            }

            /// <summary>The message prefix: the same, with the guard's depth kept (TryEnter), so the finalizer closes it (Exit).</summary>
            public bool EnterMessage(bool onMain, out TapState st)
            {
                st = default(TapState);
                if (!GMessage.TryEnter(onMain, out st.S)) return false;
                Opened(ref st);
                return true;
            }

            /// <summary>After admission: the entry ordinal (the call order, also when calls nest).</summary>
            public void Opened(ref TapState st) { st.Ord = ++_ord; }

            public void Threw(JawaBenchHookGuard g, Exception e) { try { if (e != null) g.NoteThrew(); } catch { } }

            /// <summary>The message finalizer: close the scope its own prefix opened, and count the throw.</summary>
            public void MessageExit(TapState st, Exception e)
            {
                try { if (e != null) GMessage.NoteThrew(); if (st.S.Valid) GMessage.Exit(st.S); } catch { }   // an orphan is counted once, by the postfix's Commit
            }

            // The postfix halves. The Verse postfix calls Commit itself (so the hook audit sees __runOriginal handed to it) and then
            // Record*; Mental, Quest, Letter, Message, Fire and Explosion are the same two steps for the harness.
            public void Mental(TapState st, bool ran, int pawn, string state, string reason, bool forced, bool started, string now)
            {
                if (!GMental.Commit(st.S, ran)) return;
                try { RecordMental(st, pawn, state, reason, forced, started, now); } catch (Exception e) { GMental.Note("mental", e); }
            }

            public void Quest(TapState st, bool ran, int id, string root, string name, bool added, bool accepted)
            {
                if (!GQuest.Commit(st.S, ran)) return;
                try { RecordQuest(st, id, root, name, added, accepted); } catch (Exception e) { GQuest.Note("quest", e); }
            }

            public void Letter(TapState st, bool ran, string def, string label, int delay, bool shown, int quest, string targets)
            {
                if (!GLetter.Commit(st.S, ran)) return;
                try { RecordLetter(st, def, label, delay, shown, quest, targets); } catch (Exception e) { GLetter.Note("letter", e); }
            }

            public void Message(TapState st, bool ran, string text, string def, bool shown, string targets)
            {
                if (!GMessage.Commit(st.S, ran)) return;
                try { RecordMessage(st, text, def, shown, targets); } catch (Exception e) { GMessage.Note("message", e); }
            }

            public void Fire(TapState st, bool ran, int fire, string cell, Who attached, Who instigator, double size, bool loaded)
            {
                if (!GFire.Commit(st.S, ran)) return;
                try { RecordFire(st, fire, cell, attached, instigator, size, loaded); } catch (Exception e) { GFire.Note("fire", e); }
            }

            public void Explosion(TapState st, bool ran, string cell, double radius, string damage, Who instigator, string weapon, string projectile)
            {
                if (!GExplosion.Commit(st.S, ran)) return;
                try { RecordExplosion(st, cell, radius, damage, instigator, weapon, projectile); } catch (Exception e) { GExplosion.Note("explosion", e); }
            }

            /// <summary>A mental state asked for: the attempt is one record, and a start is a second record of its own, so a judge
            /// tells "a break was tried and refused" from "a break began".</summary>
            public void RecordMental(TapState st, int pawn, string state, string reason, bool forced, bool started, string now)
            {
                string who = "\"thing\":" + pawn + ",\"alias\":" + S(AliasOf(pawn));
                Record(st, "mental_attempt", who + ",\"state\":" + S(state) + ",\"reason\":" + S(reason) + ",\"forced\":" + B(forced) +
                                             ",\"started\":" + B(started) + ",\"prev\":" + S(st.Prev));
                if (started) Record(st, "mental_start", who + ",\"state\":" + S(state) + ",\"now\":" + S(now));
            }

            /// <summary>A quest offered to the quest manager: added, or refused (it was there already, or null).</summary>
            public void RecordQuest(TapState st, int id, string root, string name, bool added, bool accepted)
            {
                Record(st, "quest", "\"quest\":" + id + ",\"root\":" + S(root) + ",\"name\":" + S(name) + ",\"added\":" + B(added) +
                                    ",\"refused\":" + S(added ? null : (st.Before ? "already there" : "not added")) + ",\"accepted\":" + B(accepted));
            }

            /// <summary>A letter received: shown in the stack now, queued (delay > 0), or neither (it cannot show).</summary>
            public void RecordLetter(TapState st, string def, string label, int delay, bool shown, int quest, string targets)
            {
                Record(st, "letter", "\"def\":" + S(def) + ",\"label\":" + S(label) + ",\"delay\":" + delay + ",\"queued\":" + B(delay > 0) +
                                     ",\"shown\":" + B(shown) + ",\"quest\":" + (quest >= 0 ? quest.ToString(CultureInfo.InvariantCulture) : "null") +
                                     ",\"targets\":" + S(targets));
            }

            /// <summary>A message sent: written before and whatever the repeat rule decides. Only the outermost call writes it.</summary>
            public void RecordMessage(TapState st, string text, string def, bool shown, string targets)
            {
                if (st.S.Depth > 1) { Inner++; return; }      // Message(Message) inside a string overload: the outer call writes it
                Record(st, "message", "\"text\":" + S(text) + ",\"def\":" + S(def) + ",\"shown\":" + B(shown) +
                                      ",\"hidden\":" + S(shown ? null : "a live message with the same text and targets") + ",\"targets\":" + S(targets));
            }

            /// <summary>A fire spawned, with its instigator and what it burns on. A fire a load restores is not a start: counted.</summary>
            public void RecordFire(TapState st, int fire, string cell, Who attached, Who instigator, double size, bool loaded)
            {
                if (loaded) { Loaded++; return; }
                Record(st, "fire", "\"fire\":" + fire + ",\"cell\":" + S(cell) + ",\"size\":" + S(size) + ",\"attached\":" + S(attached.Has ? attached.Text : null) +
                                   ",\"attachedAlias\":" + S(attached.Has ? AliasOf(attached.Id) : null) + "," + Instigator(instigator));
            }

            /// <summary>An explosion begun, with its instigator.</summary>
            public void RecordExplosion(TapState st, string cell, double radius, string damage, Who instigator, string weapon, string projectile)
            {
                Record(st, "explosion", "\"cell\":" + S(cell) + ",\"radius\":" + S(radius) + ",\"damage\":" + S(damage) + "," + Instigator(instigator) +
                                        ",\"weapon\":" + S(weapon) + ",\"projectile\":" + S(projectile));
            }

            string Instigator(Who w)
            {
                return "\"instigator\":" + S(w.Has ? w.Text : null) + ",\"instigatorKind\":" + S(w.Kind()) + ",\"instigatorAlias\":" + S(w.Has ? AliasOf(w.Id) : null);
            }

            string AliasOf(int thing) { return Alias == null ? null : Alias(thing); }

            static string B(bool b) { return b ? "true" : "false"; }

            void Record(TapState st, string rec, string fields)
            {
                var sink = Sink == null ? null : Sink();
                long seq = sink == null ? -2 : sink.EmitTap(rec, "\"ord\":" + st.Ord + "," + fields);
                if (seq == -2) Outside++;
                else if (seq < 0) Dropped++;
                else Records++;
            }

            public string Summary()
            {
                var sb = new StringBuilder("{\"records\":").Append(Records).Append(",\"outside\":").Append(Outside).Append(",\"dropped\":").Append(Dropped)
                    .Append(",\"innerMessages\":").Append(Inner).Append(",\"loadedFires\":").Append(Loaded).Append(",\"hooks\":[");
                var gs = Guards;
                for (int i = 0; i < gs.Length; i++) { if (i > 0) sb.Append(','); sb.Append('{').Append(gs[i].CoverageFields()).Append('}'); }
                return sb.Append("]}").ToString();
            }
        }

        /// <summary>A monotonic clock for the cost of the tracks.</summary>
        internal static double ClockMs() { return Stopwatch.GetTimestamp() * 1000.0 / Stopwatch.Frequency; }
    }
}
