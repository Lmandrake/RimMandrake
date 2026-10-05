using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// Per-build style, stage 2: the run rule (design 2.2-2.3, owner decisions 2026-10-04). A run is worked out from the map
    /// whenever it is needed (a flood fill over touching members and anchor spans), never stored. New members are queued on
    /// spawn and resolved once, in spawn order, on the next tick or frame (after the stage-1 Frame guard has put the picked
    /// style on a building whose worker had no ideoligion):
    ///   * no neighbouring run: the member keeps the style it was built with;
    ///   * one run: it adopts that run's style;
    ///   * several (a bridge): the run with the most conduit cells wins, a tie goes to the older run, the others are
    ///     repainted, and the player is told which style won over which;
    ///   * a split (deconstruction, fire, explosion) needs nothing: every member already carries its style.
    /// A legacy member (an older save's piece, or one built outside the menu: no stored style) is written only when its
    /// drawing would change (its run takes a non-default look, or a stored Modern colour / the mix) or the run is restyled
    /// (ConduitStyles.NeedsWrite); otherwise it keeps storing nothing and drawing the default. Loading never runs the rule.
    /// Nothing here is saved: the queue only lives between a spawn and the next tick.
    /// </summary>
    public class RM_MapComponent_ConduitRuns : MapComponent
    {
        private readonly List<Thing> pending = new List<Thing>();
        private readonly HashSet<Thing> pendingSet = new HashSet<Thing>();
        private readonly List<(Thing, Thing)> pendingLinks = new List<(Thing, Thing)>();
        /// <summary>State read (probe "cstyles").</summary>
        /// <summary>materialised = writes onto a member that stored no style; legacyKept = unstyled members left unwritten
        /// because they already draw the run's look.</summary>
        public int processed, adopted, bridges, repainted, materialised, legacyKept, restyles, linkBridges;
        /// <summary>Round 6: lamps repainted because their run was restyled / lamps that kept a look of their own / lamp
        /// Restyle gizmo uses.</summary>
        public int lampsFollowed, lampsKeptOwn, lampRestyles;
        public string lastMessage;

        public RM_MapComponent_ConduitRuns(Map map) : base(map) { }

        public void Queue(Thing t) { if (pendingSet.Add(t)) pending.Add(t); }
        public void QueueLink(Thing a, Thing b) => pendingLinks.Add((a, b));
        public int PendingCount => pending.Count + pendingLinks.Count;

        public override void MapComponentTick() { if (PendingCount > 0) ProcessPending(); }
        public override void MapComponentUpdate() { if (PendingCount > 0) ProcessPending(); }

        public void ProcessPending()
        {
            // in spawn order; a member still waiting is not part of any run yet (pendingSet), so a god-mode line of cells
            // resolves cell by cell exactly as if built one at a time
            for (int i = 0; i < pending.Count; i++)
            {
                Thing t = pending[i];
                try { if (t.Spawned && t.Map == map) Place(t); }
                catch (Exception ex) { Log.ErrorOnce("[GimmeSomeSlack] run rule: " + ex, 0x5E1E03); }
                pendingSet.Remove(t);
            }
            pending.Clear();
            pendingSet.Clear();
            while (pendingLinks.Count > 0)
            {
                (Thing a, Thing b) = pendingLinks[0];
                pendingLinks.RemoveAt(0);
                try { if (a.Spawned && b.Spawned) Link(a, b); }
                catch (Exception ex) { Log.ErrorOnce("[GimmeSomeSlack] run link rule: " + ex, 0x5E1E04); }
            }
        }

        // ------------------------------------------------------------------ the graph
        /// <summary>Members touching t: in its cells or a cardinal neighbour of them, plus its anchor's span partners.</summary>
        public IEnumerable<Thing> Neighbours(Thing t)
        {
            CellRect r = t.OccupiedRect();
            var cells = new HashSet<IntVec3>(r.Cells);
            foreach (IntVec3 c in r.Cells)
                foreach (IntVec3 d in GenAdj.CardinalDirections) cells.Add(c + d);
            foreach (IntVec3 c in cells)
            {
                if (!c.InBounds(map)) continue;
                List<Thing> l = map.thingGrid.ThingsListAtFast(c);
                for (int i = 0; i < l.Count; i++)
                    if (l[i] != t && ConduitStylePicker.IsMember(l[i].def)) yield return l[i];
            }
            CompAerialAnchor a = CompAerialAnchor.Of(t);
            if (a != null)
                foreach (SpanLink s in a.links)
                    if (s.other?.parent != null && s.other.Spawned) yield return s.other.parent;
        }

        /// <summary>The run containing seed (flood fill), never stepping onto an excluded member or across the cut link.</summary>
        public List<Thing> RunOf(Thing seed, HashSet<Thing> exclude = null, Thing cutA = null, Thing cutB = null)
        {
            var seen = new HashSet<Thing> { seed };
            var stack = new Stack<Thing>();
            stack.Push(seed);
            var res = new List<Thing>();
            while (stack.Count > 0)
            {
                Thing x = stack.Pop();
                res.Add(x);
                foreach (Thing n in Neighbours(x))
                {
                    if (exclude != null && exclude.Contains(n)) continue;
                    if (cutA != null && ((x == cutA && n == cutB) || (x == cutB && n == cutA)) && !Touching(x, n)) continue;
                    if (seen.Add(n)) stack.Push(n);
                }
            }
            res.Sort((p, q) => p.thingIDNumber.CompareTo(q.thingIDNumber));
            return res;
        }

        private static bool Touching(Thing a, Thing b)
        {
            CellRect ra = a.OccupiedRect().ExpandedBy(1), rb = b.OccupiedRect();
            foreach (IntVec3 c in rb.Cells)
                if (ra.Contains(c) && (a.OccupiedRect().Contains(c) || IsCardinalTo(a.OccupiedRect(), c))) return true;
            return false;
        }

        private static bool IsCardinalTo(CellRect r, IntVec3 c)
        {
            foreach (IntVec3 d in GenAdj.CardinalDirections) if (r.Contains(c + d)) return true;
            return false;
        }

        public static ConduitStyles.Run Info(List<Thing> run)
        {
            var info = new ConduitStyles.Run { Oldest = int.MaxValue, Tag = run };
            var colours = new List<string>();
            foreach (Thing t in run)
            {
                bool conduit = ConduitStylePicker.IsConduit(t.def);
                if (conduit) info.Area++;
                info.Oldest = Math.Min(info.Oldest, t.thingIDNumber);
                string look = ConduitStylePicker.LookOf(StylePicker.RawStyle(t), out string colour);
                if (look != null && info.Look == null) info.Look = look;       // run sorted by id: the oldest styled member
                if (conduit && look == "Modern") colours.Add(colour);
            }
            info.Colour = info.Look == "Modern" ? ConduitStyles.RunColour(colours) : null;
            return info;
        }

        // ------------------------------------------------------------------ floor lamps (round 6)
        /// <summary>The floor lamps hooked to a run: its power connection (CompPower.connectParent, which is also where the
        /// lamp's plug cord runs) is a run member, or the lamp stands on / beside a member cell. Thing-id order.</summary>
        public List<Thing> LampsOf(List<Thing> run)
        {
            var set = new HashSet<Thing>(run);
            var cells = new HashSet<IntVec3>();
            foreach (Thing m in run) foreach (IntVec3 c in m.OccupiedRect().Cells) cells.Add(c);
            var o = new List<Thing>();
            foreach (string dn in ConduitStyles.LampDefs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                if (d == null) continue;
                foreach (Thing l in map.listerThings.ThingsOfDef(d))
                {
                    Thing parent = l.TryGetComp<CompPower>()?.connectParent?.parent;
                    bool hooked = parent != null && set.Contains(parent);
                    if (!hooked)
                        foreach (IntVec3 c in l.OccupiedRect().Cells)
                        {
                            if (cells.Contains(c)) { hooked = true; break; }
                            foreach (IntVec3 dd in GenAdj.CardinalDirections) if (cells.Contains(c + dd)) { hooked = true; break; }
                            if (hooked) break;
                        }
                    if (hooked) o.Add(l);
                }
            }
            o.Sort((p, q) => p.thingIDNumber.CompareTo(q.thingIDNumber));
            return o;
        }

        /// <summary>The run a lamp is hooked to (via its power connection), or null.</summary>
        public List<Thing> RunOfLamp(Thing lamp)
        {
            Thing parent = lamp.TryGetComp<CompPower>()?.connectParent?.parent;
            if (parent != null && ConduitStylePicker.IsMember(parent.def)) return RunOf(parent);
            foreach (IntVec3 c in GenAdj.CellsAdjacentCardinal(lamp).Concat(lamp.OccupiedRect().Cells))
            {
                if (!c.InBounds(map)) continue;
                foreach (Thing t in c.GetThingList(map)) if (ConduitStylePicker.IsMember(t.def)) return RunOf(t);
            }
            return null;
        }

        /// <summary>The lamp's own "Restyle this lamp" (one piece: a lamp is a machine, not a run member). key = a look, or
        /// <see cref="LampMatchRun"/> = take the look of the run it is hooked to (back to following it).</summary>
        public const string LampMatchRun = "MatchRun";

        public bool RestyleLamp(Thing lamp, string key, bool message)
        {
            if (lamp == null || !lamp.Spawned || !ConduitStyles.IsLampDef(lamp.def.defName)) return false;
            ProcessPending();
            string look = key;
            if (key == LampMatchRun)
            {
                List<Thing> run = RunOfLamp(lamp);
                look = run == null ? null : Info(run).Look ?? StylePicker.DefaultLook;
                if (look == null) { lastMessage = "This lamp is not hooked to a cable run."; return false; }
            }
            if (!AerialStyles.IsLook(look)) return false;
            bool changed = SetStyle(lamp, look);
            lampRestyles++;
            Finish();
            lastMessage = "Restyled this lamp to " + look + (key == LampMatchRun ? " (its run's look)" : "") + ".";
            if (message && Current.ProgramState == ProgramState.Playing) Messages.Message(lastMessage, new LookTargets(lamp), MessageTypeDefOf.SilentInput, historical: false);
            return changed;
        }

        // ------------------------------------------------------------------ the rules
        private void Place(Thing x)
        {
            processed++;
            HashSet<Thing> exclude = pendingSet;                         // still holds x itself and every later spawn
            string ownLook = ConduitStylePicker.LookOf(StylePicker.RawStyle(x), out string ownColour);
            List<Thing> nbrs = Neighbours(x).Where(n => !exclude.Contains(n)).ToList();
            // fast path (big legacy maps, map generation, gravship landings): an unstyled piece among unstyled neighbours
            // joins only legacy runs (a run is uniform) and writes nothing -- no flood fill
            if (ownLook == null && nbrs.All(n => StylePicker.RawStyle(n) == null)) return;
            var runs = new List<List<Thing>>();
            var seen = new HashSet<Thing>();
            foreach (Thing n in nbrs)
            {
                if (seen.Contains(n)) continue;
                List<Thing> r = RunOf(n, exclude);
                seen.UnionWith(r);
                runs.Add(r);
            }
            if (runs.Count == 0) return;
            List<ConduitStyles.Run> infos = runs.Select(Info).ToList();
            ConduitStyles.Plan plan = ConduitStyles.PlanPlacement(ownLook, ownColour, infos, StylePicker.DefaultLook);
            if (plan.Look == null) return;
            string colour = Apply(plan, runs, infos);
            Paint(x, plan.Look, colour);
            if (runs.Count == 1) adopted++;
            Finish();
            if (plan.Repaint.Count > 0) Announce(plan, infos, x);
        }

        /// <summary>A new span between a and b: if it joined two runs, the bridge rule.</summary>
        private void Link(Thing a, Thing b)
        {
            HashSet<Thing> exclude = pendingSet;
            List<Thing> ra = RunOf(a, exclude, a, b);
            if (ra.Contains(b)) return;                                   // already one run
            List<Thing> rb = RunOf(b, exclude, a, b);
            var runs = new List<List<Thing>> { ra, rb };
            List<ConduitStyles.Run> infos = runs.Select(Info).ToList();
            ConduitStyles.Plan plan = ConduitStyles.PlanPlacement(null, null, infos, StylePicker.DefaultLook);
            if (plan.Look == null) return;
            Apply(plan, runs, infos);
            linkBridges++;
            Finish();
            if (plan.Repaint.Count > 0) Announce(plan, infos, a);
        }

        /// <summary>Repaint the losers to the winner's (look, colour mode); returns the colour mode the run ends with. A legacy
        /// winner is the default look with no stored colour, and its own members are left unwritten (NeedsWrite): a Modern
        /// loser repainted to it stores plain "Modern" and draws the same per-net colour as the winner's cords.</summary>
        private string Apply(ConduitStyles.Plan plan, List<List<Thing>> runs, List<ConduitStyles.Run> infos)
        {
            string colour = plan.Colour;
            foreach (int i in plan.Repaint)
            {
                List<Thing> lamps = LampsOf(runs[i]);            // round 6: the loser's lamps, read before it is repainted
                foreach (Thing t in runs[i]) Paint(t, plan.Look, colour);
                foreach (Thing l in lamps)
                {
                    if (!ConduitStyles.LampFollowsRun(ConduitStylePicker.RawLook(l), infos[i].Look, StylePicker.DefaultLook, restyle: false)) { lampsKeptOwn++; continue; }
                    if (SetStyle(l, plan.Look)) lampsFollowed++;
                }
                bridges++;
            }
            return colour;
        }

        private void Announce(ConduitStyles.Plan plan, List<ConduitStyles.Run> infos, Thing at)
        {
            if (!plan.StylesDiffered) return;
            ConduitStyles.Run w = infos[plan.Winner];
            lastMessage = "Joined a " + plan.LoserLook + " run to a larger " + plan.Look + " run (" + w.Area + " conduit cells): the " +
                          plan.LoserLook + " run is now " + plan.Look + ".";
            if (Current.ProgramState == ProgramState.Playing)
                Messages.Message(lastMessage, new LookTargets(at), MessageTypeDefOf.NeutralEvent, historical: false);
        }

        /// <summary>Paint one member with the run's (look, colour mode). A Mix run's new cells carry the Mix marker. A member
        /// with no stored style is written only when its drawing would change, or on a Restyle (force) -- so loading, adopting
        /// or bridging never stamps an older save's pieces that already draw right (live S7/S8 2026-10-04).</summary>
        private void Paint(Thing t, string look, string colourMode, bool force = false)
        {
            bool conduit = ConduitStylePicker.IsConduit(t.def);
            bool had = StylePicker.RawStyle(t) != null;
            if (!ConduitStyles.NeedsWrite(had, conduit, look, colourMode, StylePicker.DefaultLook, force)) { legacyKept++; return; }
            if (!SetStyle(t, ConduitStyles.KeyForMember(conduit, look, colourMode))) return;
            repainted++;
            if (!had) materialised++;
        }

        private bool dirtyCords;

        private bool SetStyle(Thing t, string key)
        {
            ThingStyleDef s = ConduitStylePicker.StyleFor(t.def, key);
            if (s == null || StylePicker.RawStyle(t) == s) return false;
            t.StyleDef = s;
            t.Notify_ColorChanged();
            if (ConduitStylePicker.IsOurs(t.def))
            {
                map.mapDrawer.MapMeshDirty(t.Position, GimmeSomeSlackDefOf.RM_MessyCords);
                dirtyCords = true;
            }
            CompAerialAnchor a = CompAerialAnchor.Of(t);
            if (a != null)
            {
                RM_MapComponent_Aerial ac = map.GetComponent<RM_MapComponent_Aerial>();
                ac?.DirtyGround(a);
                ac?.Notify_SpansChanged();
                dirtyCords = true;
            }
            return true;
        }

        private void Finish()
        {
            if (!dirtyCords) return;
            dirtyCords = false;
            map.GetComponent<RM_MapComponent_CordGraph>()?.Notify_SettingsChanged();
        }

        /// <summary>The free "Restyle this run" (owner 2026-10-04): repaint the whole run t belongs to. "One colour per run"
        /// picks one random colour for the whole run. Returns the number of members changed.</summary>
        public int RestyleRun(Thing t, string key, bool message)
        {
            if (t == null || !t.Spawned) return 0;
            ProcessPending();
            string look, colour;
            if (key == ConduitStyles.Key("Modern", ConduitStyles.Multi)) { look = "Modern"; colour = ConduitStyles.Colours[Rand.Range(0, ConduitStyles.Colours.Length)]; }
            else if (!ConduitStyles.TryParseKey(key, out look, out colour)) return 0;
            List<Thing> run = RunOf(t);
            string lookBefore = Info(run).Look;
            List<Thing> lamps = LampsOf(run);
            int before = repainted;
            foreach (Thing m in run) Paint(m, look, colour, true);
            // round 6: the floor lamps hooked to the run follow it, unless the player styled a lamp on purpose
            int lampsChanged = 0, lampsKept = 0;
            foreach (Thing l in lamps)
            {
                if (!ConduitStyles.LampFollowsRun(ConduitStylePicker.RawLook(l), lookBefore, StylePicker.DefaultLook)) { lampsKept++; continue; }
                if (SetStyle(l, look)) { lampsChanged++; lampsFollowed++; }
            }
            lampsKeptOwn += lampsKept;
            restyles++;
            Finish();
            int n = repainted - before;
            lastMessage = "Restyled this run (" + run.Count + " pieces, " + n + " changed) to " + ConduitStylePicker.Label(ConduitStyles.Key(look, colour)) +
                          (lamps.Count > 0 ? "; lamps on it: " + lampsChanged + " changed" + (lampsKept > 0 ? ", " + lampsKept + " kept their own look" : "") : "") + ".";
            if (message && Current.ProgramState == ProgramState.Playing) Messages.Message(lastMessage, new LookTargets(t), MessageTypeDefOf.SilentInput, historical: false);
            return n;
        }

    }
}
