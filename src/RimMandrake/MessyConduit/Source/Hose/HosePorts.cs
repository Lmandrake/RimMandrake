using System;
using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;
using Verse;

namespace RimMandrake.MessyConduit.Hose
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
    /// Which neighbour a reel is coupled to. Classifies by def extension first, then by TYPE NAME so MessyConduit never
    /// references FlowWorks or VE PipeSystem at compile time: FlowWorks' Building_LiquidTank (the built single-liquid tank)
    /// = Tank; a VE PipeSystem storage comp = Tank, any other VE PipeSystem resource comp (its pipes) = Pipe; a Dubs Bad
    /// Hygiene pipe comp = Pipe. The choice itself is HosePortRule (Verse-free, selftested).
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
            for (Type ty = t.def.thingClass; ty != null && ty != typeof(object); ty = ty.BaseType)
                if (ty.Name == "Building_LiquidTank") return HosePortKind.Tank;
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

        /// <summary>The reel's coupled neighbour (null when none), the side it is on and its kind.</summary>
        public static Thing Find(CompHoseReel r, out Cell side, out HosePortKind kind)
        {
            side = new Cell(0, 0);
            kind = HosePortKind.None;
            Map map = r.parent.Map;
            if (map == null) return null;
            IntVec3 p = r.parent.Position;
            var things = new List<Thing>();
            var cands = new List<HosePortCandidate>();
            foreach (Cell s in HosePortRule.SideOrder)
            {
                var c = new IntVec3(p.x + s.X, 0, p.z + s.Z);
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
            int pick = HosePortRule.Pick(new Cell(p.x, p.z), cands, out side);
            if (pick < 0) return null;
            kind = cands[pick].Kind;
            return things[pick];
        }
    }
}
