using System;
using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;
using RimWorld;
using Verse;

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>
    /// Where a lying hose's free end is and what it lies on (hose_carry_design_2026-10-04 section 7): DERIVED from the end's
    /// cell, never saved. Read-only for FlowWorks (no compile-time reference either way): cell, kind, the port it couples to
    /// (any faction's pipe or tank beside the end) and the terrain under it.
    /// </summary>
    public struct HoseFreeEnd
    {
        public IntVec3 Cell;
        public HoseEndKind Kind;
        /// <summary>Kind Port: the pipe/tank beside the end, its kind, and the side it is on (unit cell offset from the end).</summary>
        public Thing Port;
        public HosePortKind PortKind;
        public Cell PortSide;
        /// <summary>Kind Relay: the reel whose intake the end lies on.</summary>
        public CompHoseReel Relay;
        /// <summary>The terrain under the end, and the water terrain it lies in or touches (null when none).</summary>
        public TerrainDef Terrain, Water;

        public string Describe() =>
            Kind == HoseEndKind.Relay ? "coupled to the relay reel at " + Relay?.parent.Position
            : Kind == HoseEndKind.Port ? "coupled to " + Port?.LabelShort + (Port?.Faction != null && Port.Faction != Faction.OfPlayer ? " (" + Port.Faction.Name + ")" : "")
            : Kind == HoseEndKind.Water ? "intake in " + Water?.label
            : Kind == HoseEndKind.Free ? "lying free" : "none";
    }

    public static class HoseEnds
    {
        /// <summary>The free end of r, read now (the map component caches it for 60 ticks: <see cref="FreeEnd"/>).</summary>
        public static HoseFreeEnd Read(CompHoseReel r)
        {
            var e = new HoseFreeEnd { Cell = IntVec3.Invalid, Kind = HoseEndKind.None };
            Map map = r?.parent?.Map;
            if (map == null || !r.laid || !r.far.IsValid) return e;
            e.Cell = r.far;
            RM_MapComponent_Hoses comp = map.GetComponent<RM_MapComponent_Hoses>();
            e.Relay = comp?.RelayOf(r);
            if (e.Relay == null) e.Port = HosePorts.FindAt(map, r.far, r.parent, out e.PortSide, out e.PortKind);
            if (r.far.InBounds(map)) e.Terrain = r.far.GetTerrain(map);
            e.Water = WaterAt(map, r.far);
            e.Kind = HoseLive.EndKind(true, e.Relay != null, e.Port != null, e.Water != null);
            return e;
        }

        /// <summary>The water terrain the end lies in, else one it touches (edge-adjacent), else null. A carried end is set in
        /// water from the shore (PathEndMode.Touch), so the end cell itself is usually the water cell.</summary>
        public static TerrainDef WaterAt(Map map, IntVec3 c)
        {
            if (!c.InBounds(map)) return null;
            TerrainDef t = c.GetTerrain(map);
            if (t != null && t.IsWater) return t;
            foreach (IntVec3 d in GenAdj.CardinalDirections)
            {
                IntVec3 n = c + d;
                if (!n.InBounds(map)) continue;
                TerrainDef tn = n.GetTerrain(map);
                if (tn != null && tn.IsWater) return tn;
            }
            return null;
        }

        /// <summary>Section 7's public read-only accessor (cached, re-read every 60 ticks by the map component).</summary>
        public static HoseFreeEnd FreeEnd(this CompHoseReel r)
        {
            RM_MapComponent_Hoses comp = r?.parent?.Map?.GetComponent<RM_MapComponent_Hoses>();
            return comp != null ? comp.FreeEndOf(r) : Read(r);
        }
    }

    /// <summary>
    /// Section 10's hooks, static C# events with no FlowWorks reference: EndPlaced when a hose end comes to lie somewhere (set
    /// down, dropped, or its derived kind changes while lying: a tank built beside it), EndLifted when a colonist picks a
    /// lying end up. Raised by RM_MapComponent_Hoses from the reels' state each tick; a subscriber that throws is logged once
    /// and never breaks the tick.
    /// </summary>
    public static class HoseEvents
    {
        public static event Action<CompHoseReel, HoseEndKind, Thing, Faction> EndPlaced;
        public static event Action<CompHoseReel> EndLifted;
        /// <summary>State read for the probe: how many of each were raised this session.</summary>
        public static int Placed, Lifted;
        private static bool errorLogged;

        internal static void RaisePlaced(CompHoseReel r, HoseFreeEnd e)
        {
            Placed++;
            try { EndPlaced?.Invoke(r, e.Kind, e.Port, e.Port?.Faction); }
            catch (Exception ex) { if (!errorLogged) { errorLogged = true; Log.Error("[MessyConduit] a HoseEvents.EndPlaced subscriber failed: " + ex); } }
        }

        internal static void RaiseLifted(CompHoseReel r)
        {
            Lifted++;
            try { EndLifted?.Invoke(r); }
            catch (Exception ex) { if (!errorLogged) { errorLogged = true; Log.Error("[MessyConduit] a HoseEvents.EndLifted subscriber failed: " + ex); } }
        }
    }
}
