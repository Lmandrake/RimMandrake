using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Shared.Slack;

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
    /// GSS D1 (live S12a 2026-10-15): a run whose winner is legacy STAYS legacy -- a styled piece joining it, or a styled
    /// run losing a bridge to it, has its stored style cleared rather than the default written, so every member follows
    /// the default together and a later default change can never leave one run in two looks.
    /// Nothing here is saved: the queue only lives between a spawn and the next tick.
    /// </summary>
    public class RM_MapComponent_ConduitRuns : MapComponent
    {
        private readonly List<Thing> pending = new List<Thing>();
        private readonly HashSet<Thing> pendingSet = new HashSet<Thing>();
        private readonly List<(Thing, Thing)> pendingLinks = new List<(Thing, Thing)>();
        /// <summary>State read (probe "cstyles"). materialised = writes onto a member that stored no style; legacyKept = unstyled members left unwritten
        /// because they already draw the run's look.</summary>
        public int processed, adopted, bridges, repainted, materialised, legacyKept, restyles, linkBridges;
        /// <summary>State read (GSS D1): members whose stored look was cleared because their run's winner is legacy.</summary>
        public int unpainted;
        /// <summary>State read: members visited by RunOf since load (GPT pre-release D7: a bulk styled spawn's cost, N vs 2N).</summary>
        public long runOfVisits;
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
            var batch = new ConduitStyles.PlacementBatch<Thing>(StylePicker.DefaultLook);
            // in spawn order; a member still waiting is not part of any run yet (pendingSet), so a god-mode line of cells
            // resolves cell by cell exactly as if built one at a time
            for (int i = 0; i < pending.Count; i++)
            {
                Thing t = pending[i];
                try { if (t.Spawned && t.Map == map) Place(t, batch); }
                catch (Exception ex) { batch.Clear(); Log.ErrorOnce("[GimmeSomeSlack] run rule: " + ex, 0x5E1E03); }
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
        /// <summary>Members touching t: in its cells or a cardinal neighbour of them, plus its anchor's span partners. The rule
        /// is ConduitStyles.RunNeighbours (Verse-free, run by T_LINE_RESTYLE_OFFLINE); this feeds it the map.</summary>
        public IEnumerable<Thing> Neighbours(Thing t)
        {
            CompAerialAnchor a = CompAerialAnchor.Of(t);
            return ConduitStyles.RunNeighbours<Thing>(
                t,
                t.OccupiedRect().Cells.Select(c => (c.x, c.z)),
                c => new IntVec3(c.x, 0, c.z).InBounds(map),
                c => map.thingGrid.ThingsListAtFast(new IntVec3(c.x, 0, c.z)),
                x => ConduitStylePicker.IsMember(x.def) || IsBridgeConduit(x.def),
                a?.links.Select(s => ((Thing)s.other?.parent, s.state == SpanState.Up && s.other?.parent != null && s.other.Spawned)));   // GPT read A15: never across a cut span
        }

        /// <summary>GPT pre-release D8: a conduit GSS draws as cords that cannot carry a style (another mod's conduit, not
        /// patched with the style field) still JOINS a run: the flood fill walks through it, but it is never a member (it is
        /// not in the result, so it is never painted or counted). Without this, two halves joined only through it could keep
        /// two looks on one visible cord run.</summary>
        public static bool IsBridgeConduit(ThingDef d) => d != null && ConduitStyles.IsBridge(ConduitStylePicker.IsOurs(d), ConduitVisuals.IsTarget(d));

        /// <summary>The run containing seed (flood fill), never stepping onto an excluded member or across the cut link.</summary>
        public List<Thing> RunOf(Thing seed, HashSet<Thing> exclude = null, Thing cutA = null, Thing cutB = null)
        {
            return ConduitStyles.RunMembers(
                seed, Neighbours, exclude, cutA, cutB, Touching, pendingLinks,
                t => IsBridgeConduit(t.def),
                (p, q) => p.thingIDNumber.CompareTo(q.thingIDNumber),
                () => runOfVisits++);
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

        public static ConduitStyles.Run Info(List<Thing> run) => Info(run, out _);

        /// <summary>The run as the rules see it, and (0.1.1, design 2.5) the looks its members draw: Mixed when more than one.</summary>
        public static ConduitStyles.Run Info(List<Thing> run, out ConduitStyles.LookSet drawn)
        {
            var info = new ConduitStyles.Run { Oldest = int.MaxValue, Tag = run };
            var colours = new List<string>();
            drawn = new ConduitStyles.LookSet(StylePicker.DefaultLook);
            foreach (Thing t in run)
            {
                bool conduit = ConduitStylePicker.IsConduit(t.def);
                if (conduit) info.Area++;
                info.Oldest = Math.Min(info.Oldest, t.thingIDNumber);
                string look = ConduitStylePicker.LookOf(StylePicker.RawStyle(t), out string colour);
                drawn.Add(look, conduit, conduit && look == "Modern" ? colour : null);
                if (look != null && info.Look == null) info.Look = look;       // run sorted by id: the oldest styled member
                if (conduit && look == "Modern") colours.Add(colour);
            }
            info.Colour = info.Look == "Modern" ? ConduitStyles.RunColour(colours) : null;
            info.Mixed = drawn.Mixed;
            return info;
        }

        /// <summary>0.1.1 (design 2.5, rule 2): for each MIXED run, the member a new piece x takes its look from: among x's
        /// neighbours in that run, a conduit cell first when x is conduit, then the oldest (ConduitStyles.LocalPick).</summary>
        private static void SetTouches(Thing x, List<Thing> nbrs, List<ConduitStyles.Run> infos, Func<Thing, int> runIndex)
        {
            if (!infos.Any(i => i.Mixed)) return;
            bool xConduit = ConduitStylePicker.IsConduit(x.def);
            for (int r = 0; r < infos.Count; r++)
            {
                if (!infos[r].Mixed) continue;
                List<ConduitStyles.Run> touched = nbrs.Where(n => runIndex(n) == r && !IsBridgeConduit(n.def)).Select(MemberInfo).ToList();
                int k = ConduitStyles.LocalPick(touched, xConduit);
                infos[r].Touch = k >= 0 ? touched[k] : null;
            }
        }

        // ------------------------------------------------------------------ floor lamps (round 6)
        /// <summary>The floor lamps hooked to a run: its power connection (CompPower.connectParent, which is also where the
        /// lamp's plug cord runs) is a run member, or, for a lamp with no connection, it stands on / beside a member cell
        /// (ConduitStyles.LampHooked; GPT pre-release D2: a lamp wired to ANOTHER run is not this run's). Thing-id order.</summary>
        public List<Thing> LampsOf(List<Thing> run)
        {
            var lamps = new List<Thing>();
            foreach (string dn in ConduitStyles.LampDefs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                if (d != null) lamps.AddRange(map.listerThings.ThingsOfDef(d));
            }
            return ConduitStyles.LampsHookedTo(run, lamps,
                x => x.OccupiedRect().Cells.Select(c => (c.x, c.z)),
                l => l.TryGetComp<CompPower>()?.connectParent?.parent,
                (p, q) => p.thingIDNumber.CompareTo(q.thingIDNumber),
                x => Neighbours(x).Where(n => IsBridgeConduit(n.def)));   // a lamp wired to another mod's conduit in the line is hooked
        }

        /// <summary>D9: the lamp wears a style that is not one of ours (Ideology, another mod).</summary>
        private static bool ForeignStyled(Thing l)
        {
            ThingStyleDef s = StylePicker.RawStyle(l);
            return s != null && !ConduitStylePicker.IsOurStyle(s);
        }

        /// <summary>The run a lamp is hooked to (via its power connection), or null.</summary>
        public List<Thing> RunOfLamp(Thing lamp)
        {
            Thing parent = lamp.TryGetComp<CompPower>()?.connectParent?.parent;
            if (parent != null) return ConduitStylePicker.IsMember(parent.def) ? RunOf(parent) : null;   // D2: same rule as LampsOf
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
                if (look == null)
                {
                    lastMessage = "This lamp is not hooked to a cable run.";
                    // GPT source read 2026-10-06 A20: this used to return before any message was shown
                    if (message && Current.ProgramState == ProgramState.Playing) Messages.Message(lastMessage, new LookTargets(lamp), MessageTypeDefOf.RejectInput, historical: false);
                    return false;
                }
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
        private static ConduitStyles.Run MemberInfo(Thing t)
        {
            bool conduit = ConduitStylePicker.IsConduit(t.def);
            string look = ConduitStylePicker.LookOf(StylePicker.RawStyle(t), out string colour);
            return new ConduitStyles.Run { Area = conduit ? 1 : 0, Oldest = t.thingIDNumber,
                Look = look, Colour = conduit && look == "Modern" ? colour : null };
        }

        private void Place(Thing x, ConduitStyles.PlacementBatch<Thing> batch)
        {
            processed++;
            HashSet<Thing> exclude = pendingSet;                         // still holds x itself and every later spawn
            string ownLook = ConduitStylePicker.LookOf(StylePicker.RawStyle(x), out string ownColour);
            List<Thing> nbrs = Neighbours(x).Where(n => !exclude.Contains(n)).ToList();
            // Fast path for placements that need no run resolution.
            if (ConduitPlacementGate.CanSkip(ownLook, nbrs.Select(n =>
                new ConduitPlacementGate.Neighbour(
                    StylePicker.RawStyle(n) != null, IsBridgeConduit(n.def))))) { batch.Clear(); return; }
            // A bridge seed is included in RunOf's result, but other bridge cells are not.
            // Preserve that existing rule by resolving bridge neighbours through the original flood.
            bool bridgeNeighbour = nbrs.Any(n => IsBridgeConduit(n.def));
            var groups = bridgeNeighbour ? null : batch.Resolve(nbrs, Neighbours,
                exclude.Contains, t => IsBridgeConduit(t.def), MemberInfo, () => runOfVisits++);
            if (groups != null && groups.Count > 0)
            {
                var cachedInfos = groups.Select(gr => gr.Info).ToList();
                SetTouches(x, nbrs, cachedInfos, n => groups.IndexOf(batch.GroupOf(n)));
                ConduitStyles.Plan cachedPlan = ConduitStyles.PlanPlacement(ownLook, ownColour, cachedInfos, StylePicker.DefaultLook);
                if (cachedPlan.Look != null)
                {
                    // Only losers are painted by Apply. Do not enumerate or sort
                    // the growing winner for every placement that joins it.
                    var cachedRuns = groups.Select((gr, i) => i == cachedPlan.Winner ? null
                        : gr.Members.OrderBy(t => t.thingIDNumber).ToList()).ToList();
                    string cachedColour = Apply(cachedPlan, cachedRuns, cachedInfos);
                    if (cachedPlan.MaterialiseWinner) Unpaint(x); else Paint(x, cachedPlan.Look, cachedColour, true);
                    if (groups.Count == 1) adopted++;
                    Finish();
                    if (cachedPlan.Repaint.Count > 0) Announce(cachedPlan, cachedInfos, x);
                    foreach (int i in cachedPlan.Repaint) batch.Refresh(groups[i], MemberInfo);
                }
                foreach (ConduitStyles.Run ci in cachedInfos) ci.Touch = null;   // a cached group's Info outlives this placement
                batch.Merge(x, MemberInfo(x), groups);
                return;
            }
            var runs = new List<List<Thing>>();
            var seen = new HashSet<Thing>();
            foreach (Thing n in nbrs)
            {
                if (seen.Contains(n)) continue;
                List<Thing> r = RunOf(n, exclude);
                seen.UnionWith(r);
                runs.Add(r);
            }
            if (runs.Count == 0) { batch.Remember(new[] { x }, MemberInfo); return; }
            List<ConduitStyles.Run> infos = runs.Select(Info).ToList();
            var runSets = runs.Select(r => new HashSet<Thing>(r)).ToList();
            SetTouches(x, nbrs, infos, n => runSets.FindIndex(rs => rs.Contains(n)));
            ConduitStyles.Plan plan = ConduitStyles.PlanPlacement(ownLook, ownColour, infos, StylePicker.DefaultLook);
            if (plan.Look != null)
            {
                string colour = Apply(plan, runs, infos);
                if (plan.MaterialiseWinner) Unpaint(x); else Paint(x, plan.Look, colour, true);
                if (runs.Count == 1) adopted++;
                Finish();
                if (plan.Repaint.Count > 0) Announce(plan, infos, x);
            }
            List<Thing> joined = runs.SelectMany(r => r).Concat(new[] { x }).Distinct().ToList();
            if (bridgeNeighbour || joined.Any(t => IsBridgeConduit(t.def))) batch.Clear();
            else batch.Remember(joined, MemberInfo);
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
        /// winner's own members are left unwritten, and its losers are cleared to legacy too (GSS D1, Unpaint): the whole run
        /// then draws the default look and the default colour setting, and follows any later default change as one.</summary>
        private string Apply(ConduitStyles.Plan plan, List<List<Thing>> runs, List<ConduitStyles.Run> infos)
        {
            string colour = plan.Colour;
            // GSS_STYLED_WINNER_FIX_KEEPS_LEGACY_LOOK: joined to a run that stores its look, a member storing nothing stores it too, though it
            // draws the same today: left bare it would follow a later change of the default, and the one run would draw two looks
            bool stored = !plan.MaterialiseWinner && plan.Look != null;
            foreach (int i in plan.Repaint)
            {
                List<Thing> lamps = LampsOf(runs[i]);            // round 6: the loser's lamps, read before it is repainted
                foreach (Thing t in runs[i]) { if (plan.MaterialiseWinner) Unpaint(t); else Paint(t, plan.Look, colour, stored); }
                foreach (Thing l in lamps)
                {
                    if (!ConduitStyles.LampFollowsRun(ConduitStylePicker.RawLook(l), infos[i].Look, StylePicker.DefaultLook, restyle: false, ForeignStyled(l))) { lampsKeptOwn++; continue; }
                    // GSS D1: a lamp is NOT cleared under a legacy winner, because a lamp storing no style draws VANILLA art, not
                    // the default look (ConduitStylePicker). It has no "follow the default" state, so it takes the look the run
                    // draws now as its own; a later default change leaves it as a lamp with its own look (LampFollowsRun).
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

        /// <summary>GSS D1: make a member legacy (no stored style) because its run's winner is legacy. Only one of our looks
        /// is cleared; a member storing nothing, or a style that is not ours (it already reads as no look), is left alone.</summary>
        private void Unpaint(Thing t)
        {
            if (ConduitStylePicker.LookOf(StylePicker.RawStyle(t), out _) == null) { legacyKept++; return; }
            if (WriteStyle(t, null)) { repainted++; unpainted++; }
        }

        private bool dirtyCords;

        private bool SetStyle(Thing t, string key)
        {
            ThingStyleDef s = ConduitStylePicker.StyleFor(t.def, key);
            return s != null && WriteStyle(t, s);
        }

        /// <summary>Store s on t and dirty what draws it. null = no style: a run member then draws the default look, a lamp
        /// vanilla art.</summary>
        private bool WriteStyle(Thing t, ThingStyleDef s)
        {
            if (StylePicker.RawStyle(t) == s) return false;
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

        /// <summary>The "All on map" reach (0.1.1, design 2.5; it began as the god-mode "DEV: switch ALL to", owner
        /// 2026-11-22): repaint every run member and floor lamp on this map that the player owns in one look;
        /// <paramref name="everyFaction"/> (god mode) takes other factions' pieces too (ConduitStyles.ReachTakes). A lamp in
        /// another mod's style is left alone; "one colour per run" picks a colour for each run. Returns pieces changed.</summary>
        public int RestyleAll(string key, bool message, bool everyFaction)
        {
            ProcessPending();
            bool multi = key == ConduitStyles.Key("Modern", ConduitStyles.Multi);
            string look, colour = null;
            if (multi) look = "Modern";
            else if (!ConduitStyles.TryParseKey(key, out look, out colour)) return 0;
            int before = repainted, runCount = 0, lampsChanged = 0;
            var seen = new HashSet<Thing>();
            var lampList = new List<Thing>();
            foreach (Thing t in map.listerThings.AllThings.ToList())
            {
                if (t == null || !t.Spawned) continue;
                if (ConduitStylePicker.IsLamp(t.def)) { if (MapTakes(t, everyFaction)) lampList.Add(t); continue; }
                if (!ConduitStylePicker.IsMember(t.def) || seen.Contains(t)) continue;
                List<Thing> run = RunOf(t);
                bool any = false;
                string c = multi ? ConduitStyles.Colours[Rand.Range(0, ConduitStyles.Colours.Length)] : colour;
                foreach (Thing m in run)
                    if (seen.Add(m) && ConduitStylePicker.IsMember(m.def) && MapTakes(m, everyFaction)) { Paint(m, look, c, true); any = true; }
                seen.Add(t);
                if (any) runCount++;
            }
            foreach (Thing l in lampList) if (!ForeignStyled(l) && SetStyle(l, look)) lampsChanged++;
            restyles++;
            Finish();
            int n = repainted - before;
            lastMessage = "Restyled everything on the map" + (everyFaction ? " (god mode: every faction)" : " that you own") + " to " + ConduitStylePicker.Label(key) + ": " +
                          runCount + " runs, " + n + " pieces changed, " + lampsChanged + " of " + lampList.Count + " lamps changed.";
            if (message && Current.ProgramState == ProgramState.Playing) Messages.Message(lastMessage, MessageTypeDefOf.SilentInput, historical: false);
            return n + lampsChanged;
        }

        /// <summary>Does the map reach take this piece (ConduitStyles.ReachTakes: the player's own, or every faction's in god mode).</summary>
        public static bool MapTakes(Thing t, bool everyFaction) =>
            ConduitStyles.ReachTakes(ConduitStyles.Reach.Map, false, false, t.Faction == Faction.OfPlayer, everyFaction);

        /// <summary>What the map reach would repaint now: run members and floor lamps (the reach menu's counts).</summary>
        public void CountMap(bool everyFaction, out int pieces, out int lamps)
        {
            pieces = lamps = 0;
            foreach (ThingDef d in ConduitStylePicker.MemberDefs)
                foreach (Thing t in map.listerThings.ThingsOfDef(d)) if (t.Spawned && MapTakes(t, everyFaction)) pieces++;
            foreach (string dn in ConduitStyles.LampDefs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                if (d != null && ConduitStylePicker.IsLamp(d))
                    foreach (Thing t in map.listerThings.ThingsOfDef(d)) if (t.Spawned && MapTakes(t, everyFaction)) lamps++;
            }
        }

        /// <summary>The "This item" reach on a run member (0.1.1, design 2.5): repaint that one piece and nothing else, so its
        /// run may become mixed. "One colour per run" picks one colour for the piece. No lamp moves. Returns 1 if it changed.</summary>
        public int RestyleOne(Thing t, string key, bool message)
        {
            if (t == null || !t.Spawned || !ConduitStylePicker.IsMember(t.def)) return 0;
            ProcessPending();
            string look, colour;
            if (key == ConduitStyles.Key("Modern", ConduitStyles.Multi)) { look = "Modern"; colour = ConduitStyles.Colours[Rand.Range(0, ConduitStyles.Colours.Length)]; }
            else if (!ConduitStyles.TryParseKey(key, out look, out colour)) return 0;
            int before = repainted;
            Paint(t, look, colour, true);
            restyles++;
            Finish();
            int n = repainted - before;
            lastMessage = "Restyled this " + t.def.label + " only to " + ConduitStylePicker.Label(ConduitStyles.Key(look, ConduitStylePicker.IsConduit(t.def) ? colour : null)) +
                          (n == 0 ? " (it already had that look)" : "") + ".";
            if (message && Current.ProgramState == ProgramState.Playing) Messages.Message(lastMessage, new LookTargets(t), MessageTypeDefOf.SilentInput, historical: false);
            return n;
        }

        /// <summary>"All connected" from a floor lamp: restyle the run it is hooked to (and that run's following lamps), and
        /// the lamp itself. False when the lamp is hooked to no run.</summary>
        public bool RestyleLampRun(Thing lamp, string key, bool message)
        {
            if (lamp == null || !lamp.Spawned) return false;
            ProcessPending();
            List<Thing> run = RunOfLamp(lamp);
            if (run == null || run.Count == 0) return false;
            RestyleRun(run[0], key, false);
            string look = ConduitStyles.TryParseKey(key, out string l, out _) ? l : "Modern";
            bool changed = SetStyle(lamp, look);
            Finish();
            lastMessage += " This lamp: " + look + ".";
            if (message && Current.ProgramState == ProgramState.Playing) Messages.Message(lastMessage, new LookTargets(lamp), MessageTypeDefOf.SilentInput, historical: false);
            return true;
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
            Info(run, out ConduitStyles.LookSet drewBefore);      // 0.1.1 rule 4: every look the (maybe mixed) run drew
            List<Thing> lamps = LampsOf(run);
            int before = repainted;
            foreach (Thing m in run) Paint(m, look, colour, true);
            // round 6: the floor lamps hooked to the run follow it, unless the player styled a lamp on purpose
            int lampsChanged = 0, lampsKept = 0;
            foreach (Thing l in lamps)
            {
                if (!ConduitStyles.LampFollowsRun(ConduitStylePicker.RawLook(l), drewBefore.Looks, true, ForeignStyled(l))) { lampsKept++; continue; }
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
    /// <summary>Keeps RM_MapComponent_ConduitRuns out of the save, as the cord, aerial and hose components are kept out
    /// (walk E1: a save names no class of ours). Map.ExposeComponents writes EVERY MapComponent as
    /// &lt;li Class="..."/&gt; whether or not it has ExposeData, so a mod-less load logs "Could not find class". Found
    /// live 2026-10-05 by proof_all.py SL2 (the class was in the save); nothing here is saved state.</summary>
    [HarmonyLib.HarmonyPatch(typeof(Map), "ExposeComponents")]
    internal static class Patch_Map_ExposeComponents_SkipConduitRuns
    {
        internal sealed class Held { public int Index; public MapComponent Comp; }

        private static void Prefix(Map __instance, out Held __state)
        {
            __state = null;
            if (Scribe.mode != LoadSaveMode.Saving) return;
            List<MapComponent> list = __instance.components;
            int i = list.FindIndex(c => c is RM_MapComponent_ConduitRuns);
            if (i < 0) return;
            __state = new Held { Index = i, Comp = list[i] };
            list.RemoveAt(i);
        }

        private static Exception Finalizer(Map __instance, Exception __exception, Held __state)
        {
            if (__state != null)
            {
                List<MapComponent> list = __instance.components;
                list.RemoveAll(c => c is RM_MapComponent_ConduitRuns);
                list.Insert(Math.Min(__state.Index, list.Count), __state.Comp);
            }
            return __exception;
        }
    }
    /// <summary>GSS D4 (live 2026-10-15, validation_style S12d FAIL: a member saved while still in the pending queue came
    /// back as a second look on its run, because the queue is not saved and loading never runs the rule). Every save
    /// (manual, autosave, the probe's csavenow) goes through GameDataSaveLoader.SaveGame, so the queue is drained first.</summary>
    [HarmonyLib.HarmonyPatch(typeof(GameDataSaveLoader), nameof(GameDataSaveLoader.SaveGame), new[] { typeof(string) })]
    internal static class Patch_GameDataSaveLoader_SaveGame_DrainConduitRuns
    {
        private static void Prefix()
        {
            if (Current.Game?.Maps == null) return;
            foreach (Map m in Current.Game.Maps)
            {
                try { m.GetComponent<RM_MapComponent_ConduitRuns>()?.ProcessPending(); }
                catch (Exception ex) { Log.ErrorOnce("[GimmeSomeSlack] draining the conduit-run queue before a save failed: " + ex, 0x6D2D4A31); }
            }
        }
    }
}
