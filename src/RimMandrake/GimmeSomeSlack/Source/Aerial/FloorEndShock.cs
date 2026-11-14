using System.Collections.Generic;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO (bars floor_end_shock, floor_end_shocks_crossers): a sparking floor-cord
    /// end bites. Owner 2026-11-05: "if they approach intending to fix it, they are safe. If they incidentally go over the sparking
    /// end with a different job, they (or anyone else) gets shocked." and 2026-11-06: "Every sparking end shocks, but settable in
    /// settings to those three options: None, only downed lines, or all."
    ///
    /// Contacts: the end cell of EVERY floor-cord end whose net read live at the last poll (a cut conduit run, or a run the player
    /// stopped laying), however many ends the spark budget lets glow. Only that cell: the live cord behind it is harmless. The
    /// decision is ShockRule.Takes (shockReach, LineKind.FloorEnd); the shock itself (knock-out, weak heart, knockback) is
    /// RM_FallenWireShock.Shock. The colonist whose current job targets a power-conduit blueprint or frame joining THIS end
    /// (delivering steel to it, or building it) is not shocked here; one building some other conduit is.
    /// Called from RM_MapComponent_CordGraph's tick, so it runs with the overhead-lines master switch off.
    /// </summary>
    public static class FloorEndShock
    {
        /// <summary>State reads for the live scene (sc_floor_end_shock): shocks dealt, and contact cells at the last rebuild.</summary>
        public static int shocks, lastContacts;

        /// <summary>Rebuild the contact cells (cell index -> the end's conduit cell) from every live end of the cord graph.</summary>
        public static void RebuildContacts(Map map, RM_MapComponent_CordGraph g, Dictionary<int, IntVec3> contacts)
        {
            contacts.Clear();
            if (!ShockRule.KindBites(AerialSettings.shockReach, LineKind.FloorEnd)) { lastContacts = 0; return; }
            foreach (CordEnd e in g.AllEnds())
            {
                if (g.EndLive(e.NetCell) != true) continue;
                (int x, int z) = ShockRule.EndCell(e.Tip.X, e.Tip.Z);
                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(map)) continue;
                contacts[map.cellIndices.CellToIndex(c)] = new IntVec3(e.NetCell.X, 0, e.NetCell.Z);
            }
            lastContacts = contacts.Count;
        }

        /// <summary>Shock every pawn ShockRule takes on a contact cell.</summary>
        public static void CheckPawns(Map map, RM_MapComponent_CordGraph g, Dictionary<int, IntVec3> contacts)
        {
            if (contacts.Count == 0 || !RM_FallenWireShock.Ready()) return;
            List<(Pawn p, IntVec3 end)> hit = null;
            foreach (KeyValuePair<int, IntVec3> kv in contacts)
            {
                IntVec3 c = map.cellIndices.IndexToCell(kv.Key);
                bool live = g.EndLive(new Cell(kv.Value.x, kv.Value.z)) == true;
                List<Thing> things = map.thingGrid.ThingsListAtFast(c);
                for (int i = 0; i < things.Count; i++)
                    if (things[i] is Pawn p && ShockRule.Takes(AerialSettings.shockReach, LineKind.FloorEnd, live, p.RaceProps.IsFlesh, p.Dead,
                                                               RM_FallenWireShock.AlreadyOut(p), FixingThisEnd(p, kv.Value)))
                        (hit ??= new List<(Pawn, IntVec3)>()).Add((p, kv.Value));
            }
            if (hit == null) return;
            foreach ((Pawn p, IntVec3 end) in hit)
            {
                if (!p.Spawned || p.Dead) continue;
                shocks++;
                // the knockback reads "away from the live end": thrown back along the cord, toward its conduit cell's far side
                RM_FallenWireShock.Shock(p, contacts, "a sparking cord end");
            }
        }

        /// <summary>The fixer's exemption, scoped to THIS end: the pawn's current job targets a power-conduit blueprint or frame
        /// on the end's conduit cell or one of its four neighbours (the destroyed cell, or the next cell of an unfinished run).
        /// Any other job, a construction job elsewhere included, is no shield.</summary>
        public static bool FixingThisEnd(Pawn p, IntVec3 end)
        {
            Job job = p.CurJob;
            if (job == null) return false;
            return Joins(job.targetA.Thing, end) || Joins(job.targetB.Thing, end) || Joins(job.targetC.Thing, end);
        }

        private static bool Joins(Thing t, IntVec3 end)
        {
            if (t == null || !t.Spawned) return false;
            BuildableDef built = t is Blueprint bp ? bp.def.entityDefToBuild : t is Frame fr ? fr.def.entityDefToBuild : null;
            if (!(built is ThingDef td) || !td.EverTransmitsPower) return false;
            return ShockRule.TargetJoinsEnd(end.x, end.z, t.Position.x, t.Position.z);
        }
    }
}
