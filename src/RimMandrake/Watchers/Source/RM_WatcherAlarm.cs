using System.Collections.Generic;
using Verse;

namespace RimMandrake.Watchers
{
    /// <summary>
    /// WATCHER_CREATURES_MOD_1, the alarm ripple (owner ruling 2026-10-08, by question card: yes, bounded: a short local wave of about 5
    /// creatures, with delays, hop count/age/distance limits, expiring event ids so it cannot loop, its own Mod Settings toggle).
    ///
    /// A watcher that goes under for a body or the geophone (StepFlags.RaiseAlarm), or that dies (RM_DeathActionWorker_Watcher), starts an
    /// event. Each pass reaches the nearest eligible watchers (awake, visible, in the watch job) chosen by RM_WatcherKernel.AlarmPick; each
    /// lands after a rolled delay (AlarmDeliverTick), holds that watcher under for holdTicks (RM_CompWatcher.alarmUntilTick, read by the
    /// watch step as StepIn.alarmed), and passes the event on. A watcher hiding because of an alarm never starts a new event.
    ///
    /// Not saved: an event lives at most maxAgeTicks (10 s), so a save drops at most that much of a ripple in flight. The hold on each
    /// reached watcher IS saved (alarmUntilTick on its comp).
    /// </summary>
    public class RM_WatcherAlarm : MapComponent
    {
        private class AlarmEvent
        {
            public int id;
            public IntVec3 origin;
            public int startTick;
            /// <summary>The source sits in `reached` (so it is never re-alarmed) but is not one of the "about 5" the event reaches.</summary>
            public bool hasSource;
            public readonly HashSet<Pawn> reached = new HashSet<Pawn>();
        }

        private struct Pending
        {
            public AlarmEvent ev;
            public Pawn target;
            public int deliverTick;
            public int hop;
        }

        private readonly List<Pending> pending = new List<Pending>();
        private int nextId;

        // Scratch lists for AlarmPick (one pass at a time on the main thread).
        private readonly List<Pawn> cand = new List<Pawn>();
        private readonly List<float> dPasser = new List<float>(), dOrigin = new List<float>();
        private readonly List<bool> eligible = new List<bool>(), reached = new List<bool>();

        public RM_WatcherAlarm(Map map) : base(map)
        {
        }

        /// <summary>A live watcher went under for a body or the geophone.</summary>
        public static void Raise(Pawn source, Map map)
        {
            if (source != null && map != null)
            {
                RaiseAt(source, source.Position, map);
            }
        }

        /// <summary>Start an event from a cell (a death uses the corpse's cell). The source is counted as reached so it is never re-alarmed.</summary>
        public static void RaiseAt(Pawn source, IntVec3 cell, Map map)
        {
            if (!RM_WatchersSettings.watchersEnabled || !RM_WatchersSettings.alarmRipple || map == null)
            {
                return;
            }
            map.GetComponent<RM_WatcherAlarm>()?.Start(source, cell);
        }

        private void Start(Pawn source, IntVec3 cell)
        {
            var ev = new AlarmEvent { id = ++nextId, origin = cell, startTick = Find.TickManager.TicksGame };
            if (source != null)
            {
                ev.reached.Add(source);
                ev.hasSource = true;
            }
            Pass(ev, cell, 0, ev.startTick);
        }

        private void Pass(AlarmEvent ev, IntVec3 from, int hop, int passerTick)
        {
            RM_WatcherKernel.AlarmLimits L = RM_WatcherKernel.DefaultAlarmLimits();
            cand.Clear(); dPasser.Clear(); dOrigin.Clear(); eligible.Clear(); reached.Clear();
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                RM_WatcherExtension ext = p.def.GetModExtension<RM_WatcherExtension>();
                if (ext == null || p.Dead)
                {
                    continue;
                }
                cand.Add(p);
                dPasser.Add((p.Position - from).LengthHorizontalSquared);
                dOrigin.Add((p.Position - ev.origin).LengthHorizontalSquared);
                eligible.Add(RM_JobDriver_Watch.InWatchJob(p) && !RM_WatcherUtility.IsHidden(p, ext));
                reached.Add(ev.reached.Contains(p));
            }
            List<int> picked = RM_WatcherKernel.AlarmPick(dPasser, dOrigin, eligible, reached, hop, ev.reached.Count - (ev.hasSource ? 1 : 0),
                Find.TickManager.TicksGame, ev.startTick, L);
            for (int k = 0; k < picked.Count; k++)
            {
                Pawn t = cand[picked[k]];
                ev.reached.Add(t);
                pending.Add(new Pending { ev = ev, target = t, hop = hop + 1,
                    deliverTick = RM_WatcherKernel.AlarmDeliverTick(passerTick, Rand.Value, L) });
            }
        }

        public override void MapComponentTick()
        {
            if (pending.Count == 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (now % 5 != 0)
            {
                return;
            }
            RM_WatcherKernel.AlarmLimits L = RM_WatcherKernel.DefaultAlarmLimits();
            for (int i = pending.Count - 1; i >= 0; i--)
            {
                Pending p = pending[i];
                if (!RM_WatcherKernel.AlarmLive(now, p.ev.startTick, L) || !RM_WatchersSettings.alarmRipple)
                {
                    pending.RemoveAt(i);
                    continue;
                }
                if (now < p.deliverTick)
                {
                    continue;
                }
                pending.RemoveAt(i);
                Pawn t = p.target;
                RM_CompWatcher comp = t?.GetComp<RM_CompWatcher>();
                if (t == null || !t.Spawned || t.Dead || t.Map != map || comp == null)
                {
                    continue;
                }
                comp.alarmUntilTick = now + L.holdTicks;
                Pass(p.ev, t.Position, p.hop, p.deliverTick);
            }
        }
    }
}
