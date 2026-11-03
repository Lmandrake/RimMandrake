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

        // STILLSAND_DUNE_GALE_LIVE_1: reads and pokes for prove_dune_gale.py / validation.py gale_chain. Each takes
        // a pawn thingIDNumber, or "-" for the first free colonist on the current map.
        private static Pawn PickPawn(Map map, string arg)
        {
            if (map == null) return null;
            string a = (arg ?? "").Trim();
            if (a != "" && a != "-")
            {
                int.TryParse(a, out int id);
                foreach (Pawn q in map.mapPawns.AllPawnsSpawned)
                    if (q.ThingID == a || (id > 0 && q.thingIDNumber == id)) return q;
                return null;
            }
            foreach (Pawn q in map.mapPawns.FreeColonistsSpawned)
                if (!q.Dead && !q.Downed) return q;
            return null;
        }

        private static RM_GameCondition_DuneGale ActiveGale(Map map)
        {
            return map?.gameConditionManager?.GetActiveCondition<RM_GameCondition_DuneGale>();
        }

        private static int DragMarks(Map map)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_DragMark");
            return d == null || map == null ? -1 : map.listerThings.ThingsOfDef(d).Count;
        }

        /// <summary>The pawn's sun exposure as every consumer reads it (ShadeGrid.ExposureFor: cover, glare floor and
        /// the weather's sun factor), beside the bare cell read, which carries no weather factor.</summary>
        public static string PawnExposure(string arg)
        {
            // arg "<pawn>@x,z" first stands the pawn on that cell, so a clear-sky read and a gale read are of one cell.
            Map map = Find.CurrentMap;
            string who = arg ?? "-";
            IntVec3 at = IntVec3.Invalid;
            int sep = who.IndexOf('@');
            if (sep >= 0)
            {
                string[] xz = who.Substring(sep + 1).Split(',');
                who = who.Substring(0, sep);
                if (xz.Length != 2 || !int.TryParse(xz[0], out int ax) || !int.TryParse(xz[1], out int az))
                    return "GALEEXPO error=bad cell " + arg;
                at = new IntVec3(ax, 0, az);
            }
            Pawn p = PickPawn(map, who);
            if (p != null && at.IsValid)
            {
                if (!at.InBounds(map) || !at.Standable(map)) return "GALEEXPO error=cell not standable " + at;
                p.pather?.StopDead();
                p.Position = at;
                p.Notify_Teleported();
            }
            var grid = map == null ? null : RimMandrake.CreatureBehaviors.RM_MapComponent_ShadeGrid.For(map);
            if (p == null || grid == null)
                return "GALEEXPO error=" + (p == null ? "no pawn" : "no shade grid");
            return "GALEEXPO pawn=" + p.thingIDNumber + " at=" + p.Position.x + "," + p.Position.z
                + " exposure=" + grid.ExposureFor(p).ToString("F3") + " cell=" + grid.ExposureAt(p.Position).ToString("F3")
                + " roofed=" + p.Position.Roofed(map) + " weather=" + map.weatherManager.curWeather?.defName
                + " gale=" + (ActiveGale(map) != null);
        }

        /// <summary>One carry by the active gale, dice and crest gate skipped; reports the drag marks it laid.</summary>
        public static string ForceDrag(string arg)
        {
            Map map = Find.CurrentMap;
            RM_GameCondition_DuneGale gale = ActiveGale(map);
            Pawn p = PickPawn(map, arg);
            if (gale == null || p == null)
                return "GALEDRAG error=" + (gale == null ? "no active gale" : "no pawn");
            IntVec3 from = p.Position;
            int before = DragMarks(map);
            string outcome = gale.CarryNowForProof(p);
            return "GALEDRAG pawn=" + p.thingIDNumber + " outcome=" + outcome.Replace(' ', ':') + " from=" + from.x + "," + from.z
                + " to=" + (p.Spawned ? p.Position.x + "," + p.Position.z : "gone") + " dragBefore=" + before
                + " dragAfter=" + DragMarks(map) + " spawned=" + p.Spawned;
        }

        /// <summary>A carry off the edge by the active gale: the shared service takes the pawn (letter "Carried off: ..."),
        /// as RM_GameComponent_GaleCarried.CarryOff does but at alive chance 1, so the proof's return is not a dice roll.</summary>
        public static string ForceCarryOff(string arg)
        {
            Map map = Find.CurrentMap;
            RM_GameCondition_DuneGale gale = ActiveGale(map);
            Pawn p = PickPawn(map, arg);
            if (gale == null || p == null || gale.Ext == null)
                return "GALEOFF error=" + (gale == null ? "no active gale" : "no pawn");
            int id = p.thingIDNumber;
            RM_TakenByLand.Take(p, "gale", gale.Downwind(map), gale.Ext.returnDays.RandomInRange, 1f);
            return "GALEOFF pawn=" + id + " spawned=" + p.Spawned + " held=" + RM_TakenByLand.IsHeld(p)
                + " pendingGale=" + (Find.World?.GetComponent<RM_WorldComponent_TakenByLand>()?.PendingOfKind("gale") ?? -1);
        }

        /// <summary>The last emergence: its row key, how many things it placed, and how many are still spawned on the map.</summary>
        public static string LastEmergence(string arg)
        {
            var placed = RM_GameCondition_DuneGale.LastEmergencePlaced ?? new System.Collections.Generic.List<Thing>();
            Map map = Find.CurrentMap;
            int onMap = 0;
            var defs = new System.Collections.Generic.List<string>();
            foreach (Thing t in placed)
            {
                bool here = t != null && t.Spawned && t.Map == map;
                if (here) onMap++;
                defs.Add((t?.def?.defName ?? "null") + (here ? "" : "(gone)"));
            }
            return "GALEEMERGE key=" + (RM_GameCondition_DuneGale.LastEmergenceKey ?? "none") + " placed=" + placed.Count
                + " onMap=" + onMap + " things=" + string.Join(";", defs);
        }

        /// <summary>What the next gale's end does: give back every gale take on this map from before now.</summary>
        public static string ReturnGale(string arg)
        {
            Map map = Find.CurrentMap;
            var comp = Find.World?.GetComponent<RM_WorldComponent_TakenByLand>();
            if (map == null || comp == null) return "GALERETURN error=no map or service";
            int n = comp.ReturnEarlierOnMap("gale", map, Find.TickManager.TicksGame + 1);
            Pawn p = PickPawn(map, arg);
            return "GALERETURN returned=" + n + " pawnBack=" + (p != null && p.Spawned)
                + " pendingGale=" + comp.PendingOfKind("gale");
        }
    }
}
