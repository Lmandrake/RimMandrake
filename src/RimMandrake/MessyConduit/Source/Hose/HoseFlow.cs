using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>
    /// The narrow flow signal a hose's state machine reads (design 3.3): "did liquid move through this hose this
    /// pulse". Null = this provider has nothing to say about that hose (the next one is asked).
    /// </summary>
    public interface IHoseFlowState
    {
        string Name { get; }
        bool? Flowing(CompHoseReel hose, int now);
    }

    /// <summary>
    /// (a) FlowWorks adapter. The design's signal is a pump's last-pulse record: RM_PumpPortable.lastMovedUnits and
    /// lastMovedTick (design 3.3, owed by FlowWorks). No pump exists in FlowWorks yet (2026-10-02), so this reads,
    /// by reflection and without any compile-time reference, any thing on or beside the reel (or a comp of it)
    /// carrying those two fields, and applies HoseMath.PumpFlowing with FlowWorks' own pulse interval. Today it
    /// finds nothing and answers null, and the debug provider decides. MessyConduit never references FlowWorks.
    /// </summary>
    public sealed class FlowWorksPumpFlow : IHoseFlowState
    {
        public string Name => "flowworks-pump";
        private static readonly Dictionary<Type, FieldInfo[]> fields = new Dictionary<Type, FieldInfo[]>();
        private static bool pulseResolved;
        private static PropertyInfo pulseProp;

        private static FieldInfo[] Fields(Type t)
        {
            if (fields.TryGetValue(t, out FieldInfo[] f)) return f;
            FieldInfo u = AccessTools.Field(t, "lastMovedUnits"), k = AccessTools.Field(t, "lastMovedTick");
            f = u != null && k != null ? new[] { u, k } : null;
            fields[t] = f;
            return f;
        }

        public static int PulseTicks()
        {
            if (!pulseResolved)
            {
                pulseResolved = true;
                Type s = AccessTools.TypeByName("RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings");
                pulseProp = s != null ? AccessTools.Property(s, "PulseIntervalTicks") : null;
            }
            try { return pulseProp != null ? Convert.ToInt32(pulseProp.GetValue(null)) : 250; }
            catch { return 250; }
        }

        public bool? Flowing(CompHoseReel hose, int now)
        {
            if (!HoseSettings.useFlowWorksPumps) return null;
            Map map = hose.parent.Map;
            if (map == null) return null;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(hose.parent))
            {
                if (!c.InBounds(map)) continue;
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    bool? r = Read(things[i], now);
                    if (r.HasValue) return r;
                    if (things[i] is ThingWithComps tw)
                        foreach (ThingComp tc in tw.AllComps)
                        {
                            bool? rc = Read(tc, now);
                            if (rc.HasValue) return rc;
                        }
                }
            }
            return null;
        }

        private static bool? Read(object o, int now)
        {
            FieldInfo[] f = Fields(o.GetType());
            if (f == null) return null;
            try
            {
                double units = Convert.ToDouble(f[0].GetValue(o));
                int tick = Convert.ToInt32(f[1].GetValue(o));
                return HoseMath.PumpFlowing(units, tick, now, PulseTicks());
            }
            catch { return null; }
        }
    }

    /// <summary>(b) The debug/test provider: the reel's own debugFlowing flag, set by a dev-mode gizmo or by
    /// HoseProbe "flow:x,z=on|off" from the bridge. Always answers, so it is asked last.</summary>
    public sealed class DebugHoseFlow : IHoseFlowState
    {
        public string Name => "debug";
        public bool? Flowing(CompHoseReel hose, int now) => hose.debugFlowing;
    }

    public static class HoseFlow
    {
        public static readonly List<IHoseFlowState> Providers = new List<IHoseFlowState> { new FlowWorksPumpFlow(), new DebugHoseFlow() };

        public static bool Signal(CompHoseReel hose, int now, out string provider)
        {
            foreach (IHoseFlowState p in Providers)
            {
                bool? r = p.Flowing(hose, now);
                if (r.HasValue) { provider = p.Name; return r.Value; }
            }
            provider = "none";
            return false;
        }
    }
}
