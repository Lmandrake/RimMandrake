using System;
using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks.Hose
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
    /// (a) Real flow (hose port step 6, FINAL §3.3): the hose's own lease, stamped by every successful transfer whose route
    /// crosses it (RM_LiquidNet.Credit at the 11 mutation sites, and a tank feeding a hose screwed onto it). Flowing while the
    /// lease runs; NULL (not false) once it has expired, so the debug provider still answers in dev tests.
    /// </summary>
    public sealed class NetFlow : IHoseFlowState
    {
        public string Name => "net";
        public bool? Flowing(CompHoseReel hose, int now) =>
            RimMandrake.FlowWorks.Machinery.RM_LiquidNetKernel.Flowing(hose.flowUntil, now) ? true : (bool?)null;
    }

    /// <summary>(b) The debug/test provider: the reel's own debugFlowing flag (dev-mode gizmo, HoseProbe "flow:"), or that of
    /// any reel feeding it down a relay chain (bridge tests of chains; loops are excluded from FeedersOf). Null when no flag
    /// is set, so a hose with neither provider reads "not flowing" by Signal's default.</summary>
    public sealed class DebugHoseFlow : IHoseFlowState
    {
        public string Name => "debug";
        public bool? Flowing(CompHoseReel hose, int now)
        {
            if (hose.debugFlowing) return true;
            RM_MapComponent_Hoses comp = hose.parent.Map?.GetComponent<RM_MapComponent_Hoses>();
            if (comp == null) return null;
            var seen = new HashSet<CompHoseReel> { hose };
            var stack = new Stack<CompHoseReel>();
            stack.Push(hose);
            while (stack.Count > 0)
                foreach (CompHoseReel f in comp.FeedersOf(stack.Pop()))
                {
                    if (!seen.Add(f) || !f.laid || f.lay == null) continue;
                    if (f.debugFlowing) return true;
                    stack.Push(f);
                }
            return null;
        }
    }

    public static class HoseFlow
    {
        public static readonly List<IHoseFlowState> Providers = new List<IHoseFlowState> { new NetFlow(), new DebugHoseFlow() };

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
