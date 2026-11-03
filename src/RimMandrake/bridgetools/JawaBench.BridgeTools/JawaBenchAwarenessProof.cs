// MAP_AWARENESS_PROVE_ON_A_QUIET_MAP: the one step of the live awareness proof no bridge tool does - bring a pawn that
// jawa/caravan_create took off the map BACK onto the current map, so the origin recorder's mapTransfer/observedRespawn
// classification and the set-diff detector's old-id arrival can be observed (A6, A12 of
// src/RimMandrake/Utils/modcheck/live_queue/map_awareness_proof.py). Called through jawa/static_call; returns one
// "AWAREPROOF back key=value ..." line and never throws.
using System;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    public static class JawaBenchAwarenessProof
    {
        /// <summary>Find the caravan holding pawn `pawnId` (ThingID, bare or Thing_ prefixed) and enter it into the
        /// current map at the edge (CaravanEnterMapUtility.Enter). The caravan object is removed by Enter itself.</summary>
        public static string CaravanBack(string pawnId)
        {
            try
            {
                string tid = (pawnId ?? "").Trim();
                if (tid.StartsWith("Thing_")) tid = tid.Substring(6);
                var map = Find.CurrentMap;
                if (map == null) return "AWAREPROOF back ok=False why=noCurrentMap";
                Caravan car = null; Pawn pawn = null;
                foreach (var c in Find.WorldObjects.Caravans)
                {
                    var p = c.PawnsListForReading.FirstOrDefault(x => x.ThingID == tid);
                    if (p != null) { car = c; pawn = p; break; }
                }
                if (car == null) return "AWAREPROOF back ok=False why=noCaravanHolds_" + tid;
                CaravanEnterMapUtility.Enter(car, map, CaravanEnterMode.Edge);
                return "AWAREPROOF back ok=" + pawn.Spawned + " pawn=" + pawn.ThingID + " spawned=" + pawn.Spawned
                       + " sameMap=" + (pawn.MapHeld == map) + " mapId=" + map.uniqueID + " tick=" + Find.TickManager.TicksGame;
            }
            catch (Exception e)
            {
                return "AWAREPROOF back ok=False why=threw_" + e.GetType().Name;
            }
        }
    }
}
