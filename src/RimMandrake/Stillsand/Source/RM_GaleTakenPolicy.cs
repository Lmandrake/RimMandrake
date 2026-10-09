using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.FlowWorks.TakenByLand;

namespace RimMandrake.Stillsand
{
    /// <summary>
    /// TAKEN_BY_LAND_SERVICE_1: the dune gale's carry-off as a taker of the shared FlowWorks service (kind "gale"). The service
    /// holds the pawn, writes the letters and brings them back; this class supplies only what is the gale's own: leaving by the
    /// downwind edge, coming back in from that edge a few cells upwind (RM_GaleKernel), a survival roll, scour on return, its
    /// words. Everyone is held, the player's or not.
    /// </summary>
    public class RM_GaleTakenPolicy : RM_TakenPolicy
    {
        public override string Kind => "gale";

        public override bool Holds(Pawn p) => true;

        public override float RollDays() => 3f;

        private static Rot4 ToRot4(RM_Edge e)
        {
            switch (e)
            {
                case RM_Edge.East: return Rot4.East;
                case RM_Edge.South: return Rot4.South;
                case RM_Edge.West: return Rot4.West;
                default: return Rot4.North;
            }
        }

        public override void Remove(Pawn p, Map map, RM_TakenRecord r)
        {
            p.ExitMap(false, ToRot4(RM_GaleKernel.ExitEdge(r.dir.x, r.dir.z)));
            if (!Find.WorldPawns.Contains(p))
            {
                Log.Warning("[Stillsand] gale carried " + p + " off the map but it is not a world pawn; it cannot come back.");
            }
            else
            {
                Find.WorldPawns.ForcefullyKeptPawns.Add(p);
            }
        }

        public override IntVec3 PickReturnCell(RM_TakenRecord r, Map map)
        {
            IntVec3 wind = r.dir == IntVec3.Zero ? IntVec3.South : r.dir;
            Rot4 edge = ToRot4(RM_GaleKernel.ReturnEdge(wind.x, wind.z));
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && !c.Fogged(map), map, edge, 0f, out IntVec3 cell)
                && !CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map), map, 0f, out cell))
            {
                cell = map.Center;
            }
            // Comes in a few cells from the edge, "somewhere downwind".
            int inX = cell.x, inZ = cell.z;
            RM_GaleKernel.WalkIn(ref inX, ref inZ, wind.x, wind.z, (x, z) => new IntVec3(x, 0, z).InBounds(map),
                (x, z) => new IntVec3(x, 0, z).Standable(map));
            return new IntVec3(inX, 0, inZ);
        }

        public override void AfterReturn(RM_TakenRecord r, Pawn p)
        {
            RM_GameCondition_DuneGale.Bruise(p, Rand.RangeInclusive(2, 6));
        }

        public override void TakenLetter(RM_TakenRecord r, Pawn p, Map map, float days, out string label, out string text, out LetterDef def)
        {
            string bearing = RM_GameCondition_DuneGale.BearingName(r.dir);
            string name = p.LabelShortCap;
            label = "Carried off: " + name;
            text = "The gale took " + name + " off the crest and carried them " + bearing + ", out past the edge of the map.\n\n"
                 + "The wind gives back what it takes. The next gale, or a few days' drift, will bring "
                 + (r.wasPlayer ? "them" : "it") + " back in from the " + bearing + " \u2014 alive, or not.";
            def = r.wasPlayer ? LetterDefOf.NegativeEvent : LetterDefOf.NeutralEvent;
        }

        public override void ReturnedLetter(RM_TakenRecord r, Pawn p, Pawn target, bool dead, out string label, out string text, out LetterDef def)
        {
            IntVec3 wind = r.dir == IntVec3.Zero ? IntVec3.South : r.dir;
            label = dead ? "Given back: the body of " + p.LabelShortCap : "Given back: " + p.LabelShortCap;
            text = dead
                ? "The wind has brought back what it took. " + p.LabelShortCap + "'s body lies where the drift dropped it, in from the "
                  + RM_GameCondition_DuneGale.BearingName(wind) + "."
                : p.LabelShortCap + " has walked back in from the " + RM_GameCondition_DuneGale.BearingName(wind)
                  + ", scoured raw and half-buried, but alive.";
            def = r.wasPlayer ? (dead ? LetterDefOf.Death : LetterDefOf.PositiveEvent) : LetterDefOf.NeutralEvent;
        }

        public override void LostLetter(RM_TakenRecord r, string name, bool mapGone, out string label, out string text)
        {
            label = "Lost to the sand";
            text = "Something the gale carried off was never given back: " + name
                 + (mapGone ? ". The map it was taken from is gone." : ". Nothing came in on the wind.");
        }

        public override void DiedLetter(RM_TakenRecord r, Pawn p, out string label, out string text)
        {
            label = "Lost to the sand";
            text = p.LabelShortCap + " died out past the edge. The wind kept the body.";
        }
    }

    [StaticConstructorOnStartup]
    internal static class RM_GaleTakenStartup
    {
        static RM_GaleTakenStartup() { RM_TakenByLand.Register(new RM_GaleTakenPolicy()); }
    }

    /// <summary>State read for the first script (jawa/static_call).</summary>
    public static class RM_GaleTakenProof
    {
        public static string Registered(string arg)
        {
            return "GALETAKEN registered=" + (RM_TakenByLand.PolicyFor("gale") is RM_GaleTakenPolicy)
                + " pendingGale=" + (Find.World?.GetComponent<RM_WorldComponent_TakenByLand>()?.PendingOfKind("gale") ?? -1);
        }
    }
}
