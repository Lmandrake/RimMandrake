using System;
using System.Collections.Generic;
using Verse;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// Opt-in for any building a hose reel may couple to (owner review round 2, 2026-10-04: "the Hose Reel can also connect
    /// to standard static piping and other pipe-friendly buildings (like tanks) ... universal pipes that can carry any liquid
    /// of any kind"). FlowWorks' universal pipe / universal tank (design-only today) add this to their defs; nothing else
    /// is needed on their side. kind: Pipe | Tank | Other.
    /// </summary>
    public class HosePortExtension : DefModExtension
    {
        public HosePortKind kind = HosePortKind.Pipe;
    }

    /// <summary>
    /// Which neighbour a reel is coupled to (what the DRAWN hose screws onto). Classifies by def extension first, then
    /// FlowWorks' own types (tank, universal pipe, liquid machines), then by TYPE NAME for the mods FlowWorks never
    /// references: a VE PipeSystem storage comp = Tank, any other VE PipeSystem resource comp (its pipes) = Pipe; a Dubs Bad
    /// Hygiene pipe comp = Pipe -- those stay VISUAL couplings only (RM_LiquidNet.RoleOfThing: None). The choice itself is
    /// HosePortRule (Verse-free, selftested).
    /// </summary>
    public static class HosePorts
    {
        private static readonly Dictionary<ThingDef, HosePortKind> cache = new Dictionary<ThingDef, HosePortKind>();

        public static HosePortKind Classify(Thing t)
        {
            if (t?.def == null || t.def.category != ThingCategory.Building) return HosePortKind.None;
            if (cache.TryGetValue(t.def, out HosePortKind k)) return k;
            k = ClassifyDef(t);
            cache[t.def] = k;
            return k;
        }

        private static HosePortKind ClassifyDef(Thing t)
        {
            HosePortExtension ext = t.def.GetModExtension<HosePortExtension>();
            if (ext != null) return ext.kind;
            if (t is ThingWithComps tw && tw.GetComp<CompHoseReel>() != null) return HosePortKind.None;
            // FlowWorks' own buildings by TYPE since the hose moved into FlowWorks (hose port): the tank, the universal pipe, and
            // the liquid machines (Machine kind, step 6). The hydraulic role (RM_LiquidNet.RoleOfThing) decides what CARRIES.
            if (t is RimMandrake.FlowWorks.LiquidTypes.Building_LiquidTank) return HosePortKind.Tank;
            if (RimMandrake.FlowWorks.Machinery.RM_LiquidNet.IsPipe(t)) return HosePortKind.Pipe;
            if (RimMandrake.FlowWorks.Machinery.RM_LiquidNet.RoleOfKind(t) == RimMandrake.FlowWorks.Machinery.RM_NetRole.Machine) return HosePortKind.Machine;
            HosePortKind best = HosePortKind.None;
            if (t.def.comps != null)
                foreach (CompProperties cp in t.def.comps)
                {
                    HosePortKind ck = ClassifyComp(cp.compClass);
                    if (ck < best) best = ck;
                }
            return best;
        }

        private static HosePortKind ClassifyComp(Type ty)
        {
            for (; ty != null && ty != typeof(object); ty = ty.BaseType)
            {
                string ns = ty.Namespace ?? "", n = ty.Name;
                if (ns == "PipeSystem" && n.StartsWith("CompResourceStorage", StringComparison.Ordinal)) return HosePortKind.Tank;
                if (ns == "PipeSystem" && n == "CompResource") return HosePortKind.Pipe;
                if (ns.StartsWith("DubsBadHygiene", StringComparison.Ordinal) && n == "CompPipe") return HosePortKind.Pipe;
            }
            return HosePortKind.None;
        }

        /// <summary>GPT source read 2026-10-06 B14: Pick keeps the first of equal ranks, so candidates go in thing-id order, never
        /// the order things happen to sit in a cell's list.</summary>
        private static void ById(List<Thing> things, List<HosePortCandidate> cands)
        {
            var idx = new List<int>();
            for (int i = 0; i < things.Count; i++) idx.Add(i);
            idx.Sort((a, b) => things[a].thingIDNumber.CompareTo(things[b].thingIDNumber));
            var t2 = new List<Thing>(); var c2 = new List<HosePortCandidate>();
            foreach (int i in idx) { t2.Add(things[i]); c2.Add(cands[i]); }
            things.Clear(); things.AddRange(t2);
            cands.Clear(); cands.AddRange(c2);
        }

        /// <summary>The reel's coupled neighbour (null when none), the side it is on and its kind.</summary>
        internal static Thing Find(CompHoseReel r, out Cell side, out Cell contact, out HosePortKind kind)
        {
            Thing t = RawFind(r, out side, out contact, out kind);
            if (t is RimMandrake.FlowWorks.LiquidTypes.Building_LiquidPump pump && !PumpSideTakes(pump, ReelSideOn(pump, r), r))
            {
                kind = HosePortKind.None;
                return null;
            }
            return t;
        }

        /// <summary>The geometric coupling of a reel's body, before the pump's one-port-per-side gate.</summary>
        private static Thing RawFind(CompHoseReel r, out Cell side, out Cell contact, out HosePortKind kind)
        {
            side = contact = new Cell(0, 0);
            kind = HosePortKind.None;
            Map map = r.parent.Map;
            if (map == null) return null;
            HoseReelRect rect = r.Rect;
            var things = new List<Thing>();
            var cands = new List<HosePortCandidate>();
            foreach (Cell pc in rect.Perimeter())
            {
                var c = new IntVec3(pc.X, 0, pc.Z);
                if (!c.InBounds(map)) continue;
                List<Thing> l = c.GetThingList(map);
                for (int i = 0; i < l.Count; i++)
                {
                    Thing t = l[i];
                    if (t == r.parent || things.Contains(t)) continue;
                    HosePortKind k = Classify(t);
                    if (k == HosePortKind.None) continue;
                    CellRect rc = t.OccupiedRect();
                    things.Add(t);
                    cands.Add(new HosePortCandidate(rc.minX, rc.minZ, rc.Width, rc.Height, k));
                }
            }
            ById(things, cands);
            int pick = HosePortRule.Pick(rect, cands, out side, out contact);
            if (pick < 0) return null;
            kind = cands[pick].Kind;
            return things[pick];
        }

        /// <summary>Carry stage S4 (design section 7): the pipe/tank, of ANY faction, beside a hose's free end at
        /// <paramref name="end"/> (the same rule as the reel side, the end cell treated as a 1x1 reel). A thing standing ON the
        /// end cell counts too (a hose pushed into a tank's footprint couples to it). Null = none.</summary>
        internal static Thing FindAt(Map map, IntVec3 end, Thing exclude, out Cell side, out HosePortKind kind)
        {
            Thing t = RawFindAt(map, end, exclude, out side, out kind);
            if (t is RimMandrake.FlowWorks.LiquidTypes.Building_LiquidPump pump
                && !PumpSideTakes(pump, EndSideOn(pump, end), (exclude as ThingWithComps)?.GetComp<CompHoseReel>()))
            {
                kind = HosePortKind.None;
                return null;
            }
            return t;
        }

        // ---------------------------------------------------------------- FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE
        /// <summary>The pump side a reel's body touches (RM_PumpPortMath.SideOf), or -1 when it touches only a corner.</summary>
        private static int ReelSideOn(Thing pump, CompHoseReel r)
        {
            CellRect rc = r.parent.OccupiedRect();
            for (int s = 0; s < 4; s++)
            {
                IntVec3 n = pump.Position + new Rot4(s).FacingCell;
                if (rc.Contains(n)) return s;
            }
            return -1;
        }

        /// <summary>The pump side a free end at <paramref name="end"/> lies on, or -1 (a corner, or pushed onto the pump itself).</summary>
        private static int EndSideOn(Thing pump, IntVec3 end)
        {
            return RimMandrake.FlowWorks.Machinery.RM_PumpPortMath.SideOf(end.x - pump.Position.x, end.z - pump.Position.z);
        }

        /// <summary>He typed 2026-10-20, "a HOSE must connect at one of the four sides": may <paramref name="self"/> (a reel, by
        /// its body or its free end) couple at the port on <paramref name="side"/> of <paramref name="pump"/>? Not on a corner,
        /// and not where another hose with a lower id already couples (read geometrically, so no recursion). Pipes are not
        /// ports (they join wherever adjacent) and never block a hose.</summary>
        private static bool PumpSideTakes(Thing pump, int side, CompHoseReel self)
        {
            Map map = pump.Map;
            if (map == null || side < 0) return false;
            var others = new List<int>();
            RM_MapComponent_Hoses comp = map.GetComponent<RM_MapComponent_Hoses>();
            if (comp != null)
            {
                foreach (CompHoseReel o in comp.OrderedReels())
                {
                    if (o == null || o == self || o.parent == null || !o.parent.Spawned) continue;
                    if (RawFind(o, out _, out _, out _) == pump && ReelSideOn(pump, o) == side) others.Add(o.parent.thingIDNumber);
                    else if (o.laid && o.far.IsValid && comp.RelayOf(o) == null && RawFindAt(map, o.far, o.parent, out _, out _) == pump && EndSideOn(pump, o.far) == side)
                        others.Add(o.parent.thingIDNumber);
                }
            }
            int id = self?.parent != null ? self.parent.thingIDNumber : int.MaxValue;
            return RimMandrake.FlowWorks.Machinery.RM_PumpPortMath.HoseMayTake(side, id, others.ToArray());
        }

        /// <summary>The geometric coupling of a free end, before the pump's one-port-per-side gate.</summary>
        private static Thing RawFindAt(Map map, IntVec3 end, Thing exclude, out Cell side, out HosePortKind kind)
        {
            side = new Cell(0, 0);
            kind = HosePortKind.None;
            if (map == null || !end.InBounds(map)) return null;
            var rect = new HoseReelRect(end.x, end.z, 1, 1);
            var things = new List<Thing>();
            var cands = new List<HosePortCandidate>();
            Thing on = null;
            foreach (Thing t in end.GetThingList(map))
                if (t != exclude && Classify(t) != HosePortKind.None && (on == null || t.thingIDNumber < on.thingIDNumber)) on = t;
            if (on != null) { kind = Classify(on); return on; }
            foreach (Cell pc in rect.Perimeter())
            {
                var c = new IntVec3(pc.X, 0, pc.Z);
                if (!c.InBounds(map)) continue;
                List<Thing> l = c.GetThingList(map);
                for (int i = 0; i < l.Count; i++)
                {
                    Thing t = l[i];
                    if (t == exclude || things.Contains(t)) continue;
                    HosePortKind k = Classify(t);
                    if (k == HosePortKind.None) continue;
                    CellRect rc = t.OccupiedRect();
                    things.Add(t);
                    cands.Add(new HosePortCandidate(rc.minX, rc.minZ, rc.Width, rc.Height, k));
                }
            }
            ById(things, cands);
            int pick = HosePortRule.Pick(rect, cands, out side, out _);
            if (pick < 0) return null;
            kind = cands[pick].Kind;
            return things[pick];
        }
    }
}
