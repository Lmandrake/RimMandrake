using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Patches
{
    // jawa/static_call surface for prove_light_order_live.py (one string param each). WRITES: it spawns the row's target near
    // a colonist, builds the game's own right-click menu for that square (FloatMenuMakerMap.GetOptions: every provider,
    // FlowWorks' too) and, for a lightable row, runs the chosen line's action exactly as a click does. Read then reports
    // whether a Fire this colonist started stands on the target; Clean puts the fires out and removes the target (harness
    // housekeeping, not the mod).
    public static class LightOrderProof
    {
        private static Pawn pawn;
        private static Thing target;
        private static IntVec3 cell = IntVec3.Invalid;

        // "wall" | "hay" | "puddle" | "steel" | "hay@x,z" (a haystack on that square, e.g. a FlowWorks spill).
        public static string Stage(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            if (!RM_PatchesSettings.lightOrderEnabled) return "UNMEASURED: lightOrderEnabled is off";
            pawn = map.mapPawns.FreeColonistsSpawned.FirstOrDefault(p => !p.Downed && !p.InMentalState
                && p.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation));
            if (pawn == null) return "UNMEASURED: no standing colonist with hands";
            if (pawn.drafter != null) pawn.drafter.Drafted = true;   // stays put between rows
            string row = (arg ?? "").Trim();
            string kind = row.Split('@')[0];
            cell = row.Contains("@") ? ParseCell(row.Split('@')[1], map) : FreeCellNear(pawn, map);
            if (!cell.IsValid) return "UNMEASURED: no usable square for row " + row;
            foreach (Thing t in cell.GetThingList(map).ToList())
                if (t is Plant || t is Filth) t.Destroy();
            target = Spawn(kind, cell, map);
            if (target == null) return "UNMEASURED: could not spawn the row's target (" + kind + ")";
            List<FloatMenuOption> opts = FloatMenuMakerMap.GetOptions(new List<Pawn> { pawn }, cell.ToVector3Shifted(), out _);
            List<FloatMenuOption> ours = opts.Where(o => o.Label != null && (o.Label.StartsWith("Set fire to ") || o.Label.StartsWith("Cannot set fire to "))
                && o.Label.Contains(target.LabelShort)).ToList();
            List<FloatMenuOption> flow = opts.Where(o => o.Label != null && o.Label.StartsWith("Toss a flame here")).ToList();
            string head = "row=" + kind + " cell=" + cell.x + "," + cell.z + " target=" + target.def.defName + (target.Stuff != null ? "/" + target.Stuff.defName : "")
                + " flammableNow=" + target.FlammableNow + " ours=[" + string.Join("|", ours.Select(o => o.Label + (o.Disabled ? " (disabled)" : "")))
                + "] flow=[" + string.Join("|", flow.Select(o => o.Label)) + "] options=" + opts.Count;
            FloatMenuOption click = ours.FirstOrDefault(o => !o.Disabled && o.action != null);
            if (click == null) return "MENU " + head;
            click.action();
            return "STAGED " + head + " job=" + (pawn.CurJobDef?.defName ?? "none");
        }

        // A free square near the first standing colonist, for a row that must lay something there first (the FlowWorks spill).
        public static string Pick(string arg)
        {
            Map map = Find.CurrentMap;
            Pawn p = map?.mapPawns.FreeColonistsSpawned.FirstOrDefault(c => !c.Downed && !c.InMentalState);
            if (p == null) return "UNMEASURED: no standing colonist";
            IntVec3 c = FreeCellNear(p, map);
            return c.IsValid ? "CELL " + c.x + "," + c.z : "UNMEASURED: no usable square";
        }

        public static string Read(string arg)
        {
            if (pawn == null || !cell.IsValid) return "UNMEASURED: nothing staged";
            Map map = pawn.MapHeld;
            if (map == null) return "UNMEASURED: the colonist left the map";
            IEnumerable<IntVec3> cells = target != null && target.Spawned ? target.OccupiedRect().Cells : new[] { cell };
            List<Fire> fires = cells.SelectMany(c => c.GetThingList(map).OfType<Fire>()).ToList();
            bool ours = fires.Any(f => f.instigator == pawn);
            return "READ lit=" + ours + " fires=" + fires.Count + " targetSpawned=" + (target != null && target.Spawned)
                + " job=" + (pawn.CurJobDef?.defName ?? "none");
        }

        public static string Clean(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null || !cell.IsValid) return "CLEAN nothing";
            int fires = 0;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(cell, 6f, true))
            {
                if (!c.InBounds(map)) continue;
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (t is Fire) { t.Destroy(); fires++; }
                }
            }
            if (target != null && !target.Destroyed) target.Destroy();
            if (arg == "end" && pawn?.drafter != null) pawn.drafter.Drafted = false;
            string r = "CLEAN fires=" + fires;
            target = null;
            cell = IntVec3.Invalid;
            return r;
        }

        private static Thing Spawn(string kind, IntVec3 c, Map map)
        {
            switch (kind)
            {
                case "wall": return GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.WoodLog), c, map);
                case "steel": return GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.Steel), c, map);
                case "hay":
                    ThingDef hay = DefDatabase<ThingDef>.GetNamedSilentFail("Hay");
                    if (hay == null) return null;
                    Thing h = ThingMaker.MakeThing(hay);
                    h.stackCount = 75;
                    return GenSpawn.Spawn(h, c, map);
                case "puddle":
                    if (!FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_Fuel)) return null;
                    return c.GetThingList(map).FirstOrDefault(t => t.def == ThingDefOf.Filth_Fuel);
                default: return null;
            }
        }

        // A clear square 3 to 6 from the colonist that it can reach, with no fire near, out of the colonist's own square.
        private static IntVec3 FreeCellNear(Pawn p, Map map)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(p.Position, 6f, false))
            {
                if (!c.InBounds(map) || c.DistanceTo(p.Position) < 3f || !c.Standable(map) || c.GetEdifice(map) != null
                    || c.GetThingList(map).Any(t => !(t is Plant) && !(t is Filth)) || c.Roofed(map) && c.GetRoof(map).isThickRoof)
                    continue;
                if (!p.CanReach(c, Verse.AI.PathEndMode.Touch, Danger.Deadly)) continue;
                if (GenRadial.RadialCellsAround(c, 2f, true).Any(n => n.InBounds(map) && n.GetThingList(map).Any(t => t is Fire)))
                    continue;
                return c;
            }
            return IntVec3.Invalid;
        }

        private static IntVec3 ParseCell(string s, Map map)
        {
            string[] p = (s ?? "").Split(',');
            if (p.Length != 2 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z)) return IntVec3.Invalid;
            IntVec3 c = new IntVec3(x, 0, z);
            return c.InBounds(map) ? c : IntVec3.Invalid;
        }
    }
}
