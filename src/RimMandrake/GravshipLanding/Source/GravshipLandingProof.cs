// GRAVSHIPLANDING_COVERAGE_GAPS_1 -- live proof hook (jawa/static_call). Stages a 5x5 walled, roofed room in an
// open 21x21 rect of the current map, fogs the rect, and runs the SHIPPED RevealIfArrival three ways (arrival on,
// setting off, not an arrival). Walls, roof, fog and the setting are restored in finally.
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.GravshipLanding
{
    public static class GravshipLandingProof
    {
        /// <summary>"outdoor=A/B interiorFogged=C/9 off_unfogged=D nonarrival_unfogged=E" or "REFUSED: ..." / "ERROR ...".</summary>
        public static string ProofReveal(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED: no current map";
            CellRect rect = CellRect.Empty;
            bool found = false;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(map.Center, 60f, true))
            {
                CellRect r = CellRect.CenteredOn(c, 10);
                if (!r.FullyContainedWithin(map.BoundsRect().ContractedBy(2))) continue;
                if (r.Cells.All(x => x.Standable(map) && !x.Roofed(map) && x.GetEdifice(map) == null && x.GetFirstPawn(map) == null))
                { rect = r; found = true; break; }
            }
            if (!found) return "REFUSED: no open unroofed 21x21 rect within 60 cells of the map centre";

            ThingDef stuff = DefDatabase<ThingDef>.GetNamedSilentFail("BlocksGranite") ?? ThingDefOf.Steel;
            CellRect room = CellRect.CenteredOn(rect.CenterCell, 2);           // 5x5 ring, 3x3 interior
            CellRect interior = room.ContractedBy(1);
            var snapshot = new Dictionary<IntVec3, bool>();
            foreach (IntVec3 c in rect) snapshot[c] = map.fogGrid.IsFogged(c);
            var walls = new List<Thing>();
            bool was = GravshipLandingSettings.revealOutdoorsBeforeLanding;
            try
            {
                foreach (IntVec3 c in room.EdgeCells)
                    walls.Add(GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.Wall, stuff), c, map));
                foreach (IntVec3 c in interior) map.roofGrid.SetRoof(c, RoofDefOf.RoofConstructed);
                var outdoor = rect.Cells.Where(c => !room.Contains(c)).ToList();

                GravshipLandingSettings.revealOutdoorsBeforeLanding = true;
                map.fogGrid.Refog(rect);
                Patch_GenStep_GravshipMarker_Generate.RevealIfArrival(map, true, rect);
                int outOpen = outdoor.Count(c => !map.fogGrid.IsFogged(c));
                int inFog = interior.Cells.Count(c => map.fogGrid.IsFogged(c));

                GravshipLandingSettings.revealOutdoorsBeforeLanding = false;
                map.fogGrid.Refog(rect);
                Patch_GenStep_GravshipMarker_Generate.RevealIfArrival(map, true, rect);
                int offOpen = rect.Cells.Count(c => !map.fogGrid.IsFogged(c));

                GravshipLandingSettings.revealOutdoorsBeforeLanding = true;
                map.fogGrid.Refog(rect);
                Patch_GenStep_GravshipMarker_Generate.RevealIfArrival(map, false, rect);
                int nonOpen = rect.Cells.Count(c => !map.fogGrid.IsFogged(c));

                return "outdoor=" + outOpen + "/" + outdoor.Count + " interiorFogged=" + inFog + "/" + interior.Area
                    + " off_unfogged=" + offOpen + " nonarrival_unfogged=" + nonOpen;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                GravshipLandingSettings.revealOutdoorsBeforeLanding = was;
                foreach (Thing w in walls) if (!w.Destroyed) w.Destroy(DestroyMode.Vanish);
                foreach (IntVec3 c in interior) map.roofGrid.SetRoof(c, null);
                foreach (var kv in snapshot)
                {
                    bool now = map.fogGrid.IsFogged(kv.Key);
                    if (kv.Value && !now) map.fogGrid.Refog(CellRect.SingleCell(kv.Key));
                    else if (!kv.Value && now) map.fogGrid.Unfog(kv.Key);
                }
            }
        }
    }
}
