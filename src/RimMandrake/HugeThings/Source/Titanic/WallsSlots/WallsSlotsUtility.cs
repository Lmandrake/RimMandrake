using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// BIG_CREATURES_DESIGN_WALLS_AND_SLOTS phase 1 (design/RimMandrake/big_creatures_walls_and_slots_2026-10-18.md §5): the
    /// Verse side of the walls-and-slots rule. Every decision is the Verse-free WallsSlots kernel; this class gathers its inputs
    /// (breadth, footprint, the crossing a route meets, the gap a squeeze would use, the roof over a wall) and says what happened
    /// in a text mote, never a silent vanish.
    ///
    /// Only creatures carrying CompTitanicWake (a body size at or above the T1 floor) are ever judged, so only big creatures pay.
    ///
    /// Route agreement (§6): the path-start hook (Patch_StartPath_TitanClearing) is the one place a decision is made. A squeeze is
    /// a job that walks a straight gap cell by cell (JobDriver_TitanSqueeze); the pathfinder and reachability are never told a
    /// narrow gap is open, so nothing else can route a body into it. A crossing the creature holds at is remembered per creature
    /// (HeldCells) and closed to its own path requests (Patch_PathGridDoorsBlockedJob_RoofExclusion, the per-request provider
    /// cost), so the breach search looks for another crossing instead of offering the same impossible one again; the memory is
    /// dropped the moment any of its walls is despawned (Patch_Building_DeSpawn_WallsSlots), not only when it times out.
    /// </summary>
    public static class WallsSlotsUtility
    {
        // ---- per-creature numbers --------------------------------------------------------------------------------------------
        public static int Breadth(Pawn p)
        {
            if (p == null) return 1;
            int ov = p.def.GetModExtension<RM_TitanicExtension>()?.breadthCells ?? 0;
            return WallsSlots.Breadth(p.BodySize, ov);
        }

        public static int Footprint(Pawn p)
        {
            if (p == null || !p.Spawned) return 1;
            CellRect r = p.OccupiedRect();
            return Math.Max(1, Math.Max(r.Width, r.Height));
        }

        public static int Passage(Pawn p) => WallsSlots.PassageWidth(Breadth(p), Footprint(p));

        public static float Restless(Pawn p) => p?.TryGetComp<CompTitanicWake>()?.restless ?? 0f;

        public static bool Fleeing(Pawn p)
        {
            JobDef j = p?.CurJobDef;
            return j != null && (j == JobDefOf.Flee || j == JobDefOf.FleeAndCower);
        }

        public static bool Hunting(Pawn p) => p?.CurJobDef == JobDefOf.PredatorHunt;

        public static bool FullRule(Pawn p) => WallsSlots.FullRule(RM_HugeThingsSettings.TemperamentActive, Restless(p), Fleeing(p),
            p != null && p.InAggroMentalState, Hunting(p));

        // ---- motes -------------------------------------------------------------------------------------------------------------
        private static readonly Dictionary<long, int> lastSaid = new Dictionary<long, int>();

        /// <summary>A text mote over the creature; the same message from the same creature at most once per `everyTicks`.</summary>
        public static void Say(Pawn p, string text, int everyTicks = 0)
        {
            if (p == null || !p.Spawned || text.NullOrEmpty()) return;
            int now = Find.TickManager.TicksGame;
            if (everyTicks > 0)
            {
                long key = ((long)p.thingIDNumber << 32) ^ (uint)text.GetHashCode();
                if (lastSaid.TryGetValue(key, out int t) && t <= now && now - t < everyTicks) return;
                lastSaid[key] = now;
            }
            MoteMaker.ThrowText(p.DrawPos, p.Map, text, new Color(0.95f, 0.85f, 0.6f), 3.5f);
        }

        // ---- held crossings (read off the main thread by the provider-cost postfix) ---------------------------------------------
        private static readonly object heldGate = new object();
        private static readonly HeldBook held = new HeldBook();
        private static int lastPrune = int.MinValue;
        private const int PruneEveryTicks = 600;
        /// <summary>Fast gate for the despawn postfix: no held crossing anywhere costs one static read.</summary>
        internal static volatile bool AnyHeld;

        public static void NoteHeld(Pawn p, List<IntVec3> cells)
        {
            if (p?.Map == null || cells == null || cells.Count == 0) return;
            CellIndices idx = p.Map.cellIndices;
            int[] arr = new int[cells.Count];
            for (int i = 0; i < cells.Count; i++) arr[i] = idx.CellToIndex(cells[i]);
            lock (heldGate)
            {
                held.Add(p.thingIDNumber, p.Map.uniqueID, Find.TickManager.TicksGame, TitanClearing.GiveUpMemoTicks, arr);
                AnyHeld = held.Any;
            }
        }

        /// <summary>The cells this creature currently holds at, for one path request (any thread). Expired and stale entries
        /// (a time from another game) never apply.</summary>
        public static void HeldCellsFor(Pawn p, Map map, int now, List<int> into)
        {
            into.Clear();
            if (!AnyHeld || p == null || map == null) return;
            lock (heldGate) held.CellsFor(p.thingIDNumber, map.uniqueID, now, TitanClearing.GiveUpMemoTicks, into);
        }

        /// <summary>A wall left the map: every held crossing that contains its cells is forgotten at once (it is now thinner), and so
        /// is the decider's "goal unreachable" cooldown of each creature that held there. BIG_CREATURES_DESIGN_WALLS_AND_SLOTS pass 3
        /// (2026-10-19, read from the code): a creature held on every breach try is noted unreachable for 600 ticks
        /// (UnreachableMemo), so without this it re-judged the thinner wall up to 600 ticks late, against §6's "re-judges as soon
        /// as part of it is gone".</summary>
        public static void NotifyDespawned(Map map, CellRect rect)
        {
            if (!AnyHeld || map == null) return;
            CellIndices idx = map.cellIndices;
            List<int> touched;
            lock (heldGate)
            {
                touched = held.RemoveWhere(map.uniqueID, cells =>
                {
                    foreach (int c in cells)
                        if (rect.Contains(idx.IndexToCell(c))) return true;
                    return false;
                });
                AnyHeld = held.Any;
            }
            if (touched != null) WallsSlotsDecider.ForgetUnreachable(touched);
        }

        /// <summary>Main thread, at most every PruneEveryTicks (and at once when the tick goes backwards, a load): drop held crossings
        /// of creatures that are dead, despawned, destroyed or on a map that is gone, and expired ones; trim the mote memo.</summary>
        public static void PruneMemos(int now)
        {
            bool back = now < lastPrune;
            if (!back && lastPrune != int.MinValue && now - lastPrune < PruneEveryTicks) return;
            lastPrune = now;
            if (back) lastSaid.Clear();
            else
            {
                List<long> old = null;
                foreach (KeyValuePair<long, int> kv in lastSaid)
                    if (now - kv.Value > 20000 || kv.Value > now) (old ?? (old = new List<long>())).Add(kv.Key);
                if (old != null) foreach (long k in old) lastSaid.Remove(k);
            }
            lock (heldGate)
            {
                if (!held.Any) return;
                held.Prune(now, TitanClearing.GiveUpMemoTicks, id => CreatureLive(id), id => MapLive(id));
                AnyHeld = held.Any;
            }
        }

        private static bool MapLive(int mapId)
        {
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++) if (maps[i].uniqueID == mapId) return true;
            return false;
        }

        private static bool CreatureLive(int thingId)
        {
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                IReadOnlyList<Pawn> ps = maps[i].mapPawns.AllPawnsSpawned;
                for (int j = 0; j < ps.Count; j++)
                    if (ps[j].thingIDNumber == thingId) return !ps[j].Dead && !ps[j].Destroyed;
            }
            return false;
        }

        // ---- what a wall is to this creature -----------------------------------------------------------------------------------
        public enum CellKind
        {
            Open = 0,
            /// <summary>A built blocker this creature may break.</summary>
            Wall = 1,
            /// <summary>Natural rock: never damaged, ever.</summary>
            Rock = 2,
            /// <summary>A blocker it may not break (protected by the crush table, its own faction's, a quest object, indestructible).</summary>
            Protected = 3,
            /// <summary>A giant plant's trunk: the giant-plant smash route (tier-gated, unchanged).</summary>
            Trunk = 4,
            /// <summary>Not walkable for another reason (deep water, out of bounds): no crossing here.</summary>
            Impassable = 5,
        }

        public static CellKind KindAt(Pawn p, IntVec3 c, out Building b)
        {
            b = null;
            Map map = p.Map;
            if (!c.InBounds(map)) return CellKind.Impassable;
            Building ed = c.GetEdifice(map);
            if (ed != null && ed.BlocksPawn(p))
            {
                b = ed;
                if (ed is Building_TrunkBlocker) return CellKind.Trunk;
                if (ed.def.building != null && ed.def.building.isNaturalRock) return CellKind.Rock;
                return WallEligible(p, ed) ? CellKind.Wall : CellKind.Protected;
            }
            if (!c.Walkable(map))
            {
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                    if (things[i] is Plant pl && pl.TryGetComp<CompHugeFootprint>() != null) return CellKind.Trunk;
                return ed != null && ed.def.building != null && ed.def.building.isNaturalRock ? CellKind.Rock : CellKind.Impassable;
            }
            return CellKind.Open;
        }

        /// <summary>§5.8: the walls-and-slots rule replaces the tier gate on walls; the crush table still decides what is ever
        /// breakable (a row crushable at any tier), and never its own faction's or a friendly building, a quest object, natural
        /// rock or an indestructible def.</summary>
        public static bool WallEligible(Pawn p, Building b)
        {
            if (b == null || b.Destroyed || !b.Spawned || !b.def.destroyable) return false;
            if (b.def.building != null && b.def.building.isNaturalRock) return false;
            if (b is Building_TrunkBlocker) return false;
            if (b.questTags != null && b.questTags.Count > 0) return false;
            if (b.Faction != null && p.Faction != null && (b.Faction == p.Faction || !b.Faction.HostileTo(p.Faction))) return false;
            return CrushTableUtility.IsCrushableAtTier(b, TitanicTier.T3);
        }

        /// <summary>§1 roofed, X4: on one side of the wall (along the dominant axis of travel), at least half the cells within 2 of it
        /// are roofed. Read when the creature decides, before its own wake can hole the roof.</summary>
        public static bool RoofedWall(Map map, IntVec3 c, bool alongX)
        {
            int ra = 0, ta = 0, rb = 0, tb = 0;
            for (int depth = 1; depth <= 2; depth++)
                for (int lat = -2; lat <= 2; lat++)
                {
                    IntVec3 a = alongX ? new IntVec3(c.x - depth, 0, c.z + lat) : new IntVec3(c.x + lat, 0, c.z - depth);
                    IntVec3 bb = alongX ? new IntVec3(c.x + depth, 0, c.z + lat) : new IntVec3(c.x + lat, 0, c.z + depth);
                    if (a.InBounds(map)) { ta++; if (map.roofGrid.Roofed(a)) ra++; }
                    if (bb.InBounds(map)) { tb++; if (map.roofGrid.Roofed(bb)) rb++; }
                }
            return WallsSlots.RoofedWall(ra, ta, rb, tb);
        }

        // ---- the crossing a route meets ---------------------------------------------------------------------------------------
        public sealed class Crossing
        {
            public readonly List<Building> walls = new List<Building>();
            public readonly List<IntVec3> cells = new List<IntVec3>();
            public readonly List<int> layer = new List<int>();
            public readonly List<bool> roofed = new List<bool>();
            public bool forbidden;
            public bool trunk;
            public int thickness;
            public float hpSum;
            public CrossVerdict verdict;
            public int breadth;
        }

        /// <summary>
        /// The first crossing along a route (cells from the creature outward): the swept area of the body (its current footprint
        /// offset onto each route cell) from first contact with a blocker until it has been clear for B steps, or the route ends,
        /// so gapped layers within its own length are one crossing (X1) and walls touching its flank count (X8). Rock or a
        /// protected building the route itself digs through (the centre line) makes the crossing forbidden; rock beside the
        /// route is never part of it and never damaged (X7: a wooden plug between outcrops is wood). Null: no crossing at all.
        /// </summary>
        public static Crossing Probe(Pawn p, List<IntVec3> route)
        {
            if (p?.Map == null || route == null || route.Count == 0) return null;
            Map map = p.Map;
            int b = Breadth(p);
            IntVec3 pos = p.Position;
            CellRect foot = p.OccupiedRect();
            int ox0 = foot.minX - pos.x, oz0 = foot.minZ - pos.z, ox1 = foot.maxX - pos.x, oz1 = foot.maxZ - pos.z;
            var seen = new HashSet<int>();
            var cr = new Crossing { breadth = b };
            int started = -1, lastContact = -1, clearRun = 0;
            int n = Math.Min(route.Count, WallsSlots.CrossingNodeCap);
            for (int i = 0; i < n; i++)
            {
                IntVec3 node = route[i];
                bool contact = false;
                for (int dz = oz0; dz <= oz1; dz++)
                    for (int dx = ox0; dx <= ox1; dx++)
                    {
                        IntVec3 c = new IntVec3(node.x + dx, 0, node.z + dz);
                        CellKind k = KindAt(p, c, out Building wall);
                        if (k == CellKind.Open) continue;
                        bool centre = c == node;
                        if (k == CellKind.Trunk) { cr.trunk = true; contact = true; continue; }
                        if (k == CellKind.Impassable) { if (centre) { cr.forbidden = true; contact = true; } continue; }
                        if (k == CellKind.Rock) { if (centre) { cr.forbidden = true; contact = true; } continue; }
                        contact = true;
                        if (k == CellKind.Protected) { cr.forbidden = true; continue; }
                        int key = map.cellIndices.CellToIndex(c);
                        if (!seen.Add(key)) continue;
                        cr.walls.Add(wall);
                        cr.cells.Add(c);
                    }
                if (contact)
                {
                    if (started < 0) started = i;
                    lastContact = i;
                    clearRun = 0;
                }
                else if (started >= 0 && ++clearRun >= b) break;
            }
            if (started < 0) return null;
            if (cr.cells.Count == 0 && !cr.forbidden) return cr.trunk ? cr : null;
            IntVec3 from = started > 0 ? route[started - 1] : pos;
            IntVec3 to = route[Math.Max(lastContact, started)];
            int ddx = to.x - from.x, ddz = to.z - from.z;
            bool alongX = Math.Abs(ddx) >= Math.Abs(ddz);
            float roofHp = RM_HugeThingsSettings.roofWallHpFactor;
            int m = cr.cells.Count;
            var xs = new int[m];
            var zs = new int[m];
            var hp = new float[m];
            for (int i = 0; i < m; i++)
            {
                bool roofed = RoofedWall(map, cr.cells[i], alongX);
                cr.roofed.Add(roofed);
                xs[i] = cr.cells[i].x;
                zs[i] = cr.cells[i].z;
                hp[i] = WallsSlots.CountedHp(cr.walls[i].HitPoints, roofed, roofHp);
            }
            CrossingInfo info = WallsSlots.Analyze(b, xs, zs, hp, ddx, ddz, from.x, from.z);
            for (int i = 0; i < m; i++) cr.layer.Add(m == 0 ? 0 : info.LayerOf[i]);
            cr.thickness = m == 0 ? (cr.forbidden ? 1 : 0) : info.Thickness;
            cr.hpSum = info.HpSum;
            cr.verdict = WallsSlots.Decide(b, cr.thickness, cr.hpSum, cr.forbidden, RM_HugeThingsSettings.breadth2BreakingEnabled,
                RM_HugeThingsSettings.holdLineFactor, RM_HugeThingsSettings.trampleBudgetPerBreadth);
            return cr;
        }

        /// <summary>A found path's cells from the creature outward (PawnPath stores them reversed).</summary>
        public static List<IntVec3> RouteOf(PawnPath path)
        {
            var list = new List<IntVec3>();
            if (path == null || !path.Found) return list;
            List<IntVec3> rev = path.NodesReversed;
            for (int i = rev.Count - 1; i >= 0; i--) list.Add(rev[i]);
            return list;
        }

        /// <summary>The straight line to a cell, as a route (the fallback when no breach path exists, e.g. a body the breach
        /// search cannot route at all).</summary>
        public static List<IntVec3> LineRoute(IntVec3 from, IntVec3 to)
        {
            var list = new List<IntVec3> { from };
            foreach (int[] xz in TitanClearing.LineCells(from.x, from.z, to.x, to.z, TitanClearing.ProbeMaxCells))
                list.Add(new IntVec3(xz[0], 0, xz[1]));
            return list;
        }

        // ---- squeezing ----------------------------------------------------------------------------------------------------------
        public sealed class SqueezePlan
        {
            public readonly List<IntVec3> cells = new List<IntVec3>();   // entry first, exit last
            public readonly List<int> slots = new List<int>();
            public float ticks;
        }

        /// <summary>Open for a squeezing body: walkable ground, no blocker this creature cannot pass (a door it cannot open is a
        /// wall, X3), and never under overhead mountain (his card #1).</summary>
        public static bool SqueezeOpen(Pawn p, IntVec3 c)
        {
            Map map = p.Map;
            if (!c.InBounds(map) || !c.Walkable(map)) return false;
            RoofDef r = c.GetRoof(map);
            if (r != null && r.isThickRoof) return false;
            Building ed = c.GetEdifice(map);
            return ed == null || !ed.BlocksPawn(p);
        }

        /// <summary>The clear width S of the gap at c across the step direction (dx, dz), counted up to P.</summary>
        public static int SlotAt(Pawn p, IntVec3 c, int dx, int dz, int pCap)
        {
            if (!SqueezeOpen(p, c)) return 0;
            int px = dz != 0 ? 1 : 0, pz = dx != 0 ? 1 : 0;   // the perpendicular axis of a cardinal step
            if (px == 1 && pz == 1) return Math.Min(SlotAt(p, c, 1, 0, pCap), SlotAt(p, c, 0, 1, pCap));
            int s = 1;
            for (int k = 1; k < pCap && s < pCap; k++) { if (!SqueezeOpen(p, new IntVec3(c.x + px * k, 0, c.z + pz * k))) break; s++; }
            for (int k = 1; k < pCap && s < pCap; k++) { if (!SqueezeOpen(p, new IntVec3(c.x - px * k, 0, c.z - pz * k))) break; s++; }
            return s;
        }

        /// <summary>
        /// §4 geometry: along a body-free route (a pawnless path) the first run of cells whose gap is narrower than P is the gap.
        /// It must be straight and cardinal, every cell at least half P (WallsSlots.SqueezeRunTicks), no longer than
        /// WallsSlots.MaxSqueezeCells. The squeeze line runs along the gap's own axis, out from both ends until the body fits
        /// again (Large Pawns' whole-square walkability: a P x P clear square to enter and to leave), so the approach the route
        /// happened to take never matters; the entry must be reachable by the body. Null: no legal squeeze on this route.
        /// </summary>
        public static SqueezePlan PlanSqueeze(Pawn p, List<IntVec3> route)
        {
            if (p?.Map == null || route == null || route.Count < 2) return null;
            Map map = p.Map;
            int pw = Passage(p);
            if (pw <= 1) return null;
            int start = -1, end = -1;
            IntVec3 dir = IntVec3.Zero;
            for (int i = 1; i < route.Count; i++)
            {
                IntVec3 d = route[i] - route[i - 1];
                int sl = SlotAt(p, route[i], d.x, d.z, pw);
                if (sl < pw)
                {
                    if (start < 0) { start = i; dir = d; }
                    else if (d != dir) return null;    // the gap bends: no squeeze
                    end = i;
                }
                else if (start >= 0) break;
            }
            if (start < 0 || Math.Abs(dir.x) + Math.Abs(dir.z) != 1) return null;
            if (end - start + 1 > WallsSlots.MaxSqueezeCells) return null;
            IntVec3 entry = route[start] - dir;
            for (int k = 0; !entry.WalkableBy(map, p); k++)
            {
                if (k > pw + 2 || !SqueezeOpen(p, entry)) return null;
                entry -= dir;
            }
            IntVec3 exit = route[end] + dir;
            for (int k = 0; !exit.WalkableBy(map, p); k++)
            {
                if (k > pw + 2 || !SqueezeOpen(p, exit)) return null;
                exit += dir;
            }
            var plan = new SqueezePlan();
            for (IntVec3 c = entry; ; c += dir)
            {
                plan.cells.Add(c);
                if (c == exit || plan.cells.Count > WallsSlots.MaxSqueezeCells + 2 * pw + 6) break;
            }
            if (plan.cells[plan.cells.Count - 1] != exit) return null;
            var run = new int[plan.cells.Count - 1];
            plan.slots.Add(pw);
            for (int i = 1; i < plan.cells.Count; i++)
            {
                int sl = i == plan.cells.Count - 1 ? pw : SlotAt(p, plan.cells[i], dir.x, dir.z, pw);
                run[i - 1] = sl;
                plan.slots.Add(sl);
            }
            if (run.Length > WallsSlots.MaxSqueezeCells) return null;
            float tpc = Math.Max(1f, p.TicksPerMoveCardinal);
            float t = WallsSlots.SqueezeRunTicks(run, pw, RM_HugeThingsSettings.squeezeSlowdownAtHalf, tpc);
            if (t < 0f) return null;
            plan.ticks = t;
            if (!map.reachability.CanReach(p.Position, entry, PathEndMode.OnCell, TraverseParms.For(p, Danger.Deadly, TraverseMode.ByPawn)))
                return null;
            return plan;
        }

        // ---- scraping ----------------------------------------------------------------------------------------------------------
        private static readonly Dictionary<long, int> lastScrape = new Dictionary<long, int>();

        /// <summary>§5.6: one squeezing step scrapes each built wall flanking the gap at c (the first blocker either side across
        /// the step, and any built blocker under the body), at most once a second per wall. Rock is never scraped.</summary>
        public static void Scrape(Pawn p, IntVec3 c, int dx, int dz)
        {
            if (!RM_HugeThingsSettings.ScrapeActive || p?.Map == null) return;
            Map map = p.Map;
            int pw = Passage(p);
            var hit = new HashSet<Building>();
            int px = dz != 0 ? 1 : 0, pz = dx != 0 ? 1 : 0;
            for (int sgn = -1; sgn <= 1; sgn += 2)
                for (int k = 1; k <= pw; k++)
                {
                    IntVec3 q = new IntVec3(c.x + sgn * px * k, 0, c.z + sgn * pz * k);
                    if (SqueezeOpen(p, q)) continue;
                    if (KindAt(p, q, out Building w) == CellKind.Wall) hit.Add(w);
                    break;
                }
            foreach (IntVec3 q in p.OccupiedRect())
                if (KindAt(p, q, out Building w) == CellKind.Wall) hit.Add(w);
            int now = Find.TickManager.TicksGame;
            foreach (Building w in hit)
            {
                long key = ((long)map.uniqueID << 32) ^ (uint)map.cellIndices.CellToIndex(w.Position);
                int last = lastScrape.TryGetValue(key, out int l) ? l : -1;
                if (!WallsSlots.ScrapeDue(last, now)) continue;
                lastScrape[key] = now;
                w.TakeDamage(new DamageInfo(DamageDefOf.Crush, WallsSlots.ScrapeDamage, instigator: p));
            }
            if (lastScrape.Count > 4096) lastScrape.Clear();
        }

        // ---- inspect lines ------------------------------------------------------------------------------------------------------
        /// <summary>§5.9, the creature: "Breadth 4 (needs 4-wide gaps) · squeezes gaps of 2+ · breaks walls up to 400 HP · smashes up
        /// to 3 thick · stopped by 4 thick".</summary>
        public static string CreatureLine(Pawn p)
        {
            int b = Breadth(p), pw = Passage(p);
            var parts = new List<string> { "RM_WallsSlots_PartBreadth".Translate(b, pw) };
            if (RM_HugeThingsSettings.SqueezeActive && pw > 1) parts.Add("RM_WallsSlots_PartSqueeze".Translate(WallsSlots.MinSqueeze(pw)));
            int hold = WallsSlots.HoldThickness(b, RM_HugeThingsSettings.holdLineFactor);
            bool breaks = b >= 3 || (b == 2 && RM_HugeThingsSettings.breadth2BreakingEnabled);
            if (breaks)
            {
                parts.Add("RM_WallsSlots_PartBreaks".Translate(WallsSlots.TrampleBudget(b, RM_HugeThingsSettings.trampleBudgetPerBreadth).ToString("0")));
                if (hold > 1) parts.Add("RM_WallsSlots_PartSmashes".Translate(hold - 1));
                parts.Add("RM_WallsSlots_PartStopped".Translate(hold));
            }
            else parts.Add("RM_WallsSlots_PartStoppedAny".Translate());
            return string.Join(" · ", parts);
        }

        /// <summary>§5.9, the wall: the thickness of the run of wall it belongs to here (the thinner of its two straight runs
        /// through this cell, any material, roof not counted) and the widest creature that holds back.</summary>
        public static string WallLine(Building b)
        {
            Map map = b.Map;
            int Run(int dx, int dz)
            {
                int n = 1;
                for (int s = -1; s <= 1; s += 2)
                    for (int k = 1; k <= 12; k++)
                    {
                        IntVec3 c = new IntVec3(b.Position.x + s * dx * k, 0, b.Position.z + s * dz * k);
                        if (!c.InBounds(map)) break;
                        Building e = c.GetEdifice(map);
                        if (e == null || e.def.passability != Traversability.Impassable) break;
                        n++;
                    }
                return n;
            }
            int t = Math.Min(Run(1, 0), Run(0, 1));
            int up = WallsSlots.StopsUpTo(t, RM_HugeThingsSettings.holdLineFactor);
            return up >= 2 ? "RM_WallsSlots_WallStops".Translate(up, t) : "RM_WallsSlots_WallStopsNone".Translate(t);
        }
    }
}
