using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Graffiti
{
    /// <summary>
    /// A lived-in test base for looking at the mod the way a player does, through jawa/static_call on a throwaway quicktest map
    /// (driver: src/RimMandrake/Graffiti/stage_colony.py). Colony builds rooms off a corridor with furniture, doors and three wall
    /// materials; Gallery paints every mark on a wall row with vanilla filth beside it; Faces paints each of a room's four
    /// walls from inside and out; Spree sends colonists on the real spree. Nothing here runs in play.
    /// </summary>
    public static class RM_GraffitiStage
    {
        private const int W = 44, H = 30;
        private static IntVec3 origin;

        private static IntVec3 C(int dx, int dz) => new IntVec3(origin.x + dx, 0, origin.z + dz);

        private static void Clear(Map map, CellRect rect, TerrainDef terrain)
        {
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map)) continue;
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (t is Pawn p && p.Faction == Faction.OfPlayer) continue;
                    if (!t.Destroyed) t.Destroy(DestroyMode.Vanish);
                }
                map.terrainGrid.SetTerrain(c, terrain);
                map.roofGrid.SetRoof(c, null);
                map.fogGrid.Unfog(c);
                map.areaManager.Home[c] = true;
            }
        }

        private static void Put(Map map, string def, ThingDef stuff, int dx, int dz, Rot4 rot = default)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamed(def);
            Thing t = ThingMaker.MakeThing(d, d.MadeFromStuff ? stuff : null);
            t.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(t, C(dx, dz), map, rot, WipeMode.Vanish);
        }

        private static void WallRun(Map map, ThingDef stuff, int x0, int z0, int x1, int z1)
        {
            for (int x = x0; x <= x1; x++)
            {
                for (int z = z0; z <= z1; z++)
                {
                    Put(map, "Wall", stuff, x, z);
                }
            }
        }

        private static void Floor(Map map, TerrainDef terrain, int x0, int z0, int x1, int z1)
        {
            for (int x = x0; x <= x1; x++)
            {
                for (int z = z0; z <= z1; z++)
                {
                    map.terrainGrid.SetTerrain(C(x, z), terrain);
                    map.roofGrid.SetRoof(C(x, z), RoofDefOf.RoofConstructed);
                }
            }
        }

        /// <summary>COLONY dims | hall x,z,w,h | corridor | exterior: the rects the driver frames.</summary>
        public static string Colony(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            origin = new IntVec3(map.Size.x / 2 - W / 2, 0, map.Size.z / 2 - H / 2);
            Clear(map, new CellRect(origin.x, origin.z, W, H), TerrainDefOf.Soil);
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
            {
                if (p.Faction != Faction.OfPlayer && p.Position.DistanceTo(C(W / 2, H / 2)) < 40f) p.Destroy(DestroyMode.Vanish);
            }
            ThingDef granite = ThingDefOf.BlocksGranite, steel = ThingDefOf.Steel, wood = ThingDefOf.WoodLog;
            TerrainDef plank = DefDatabase<TerrainDef>.GetNamed("WoodPlankFloor"), tile = DefDatabase<TerrainDef>.GetNamed("PavedTile");
            Floor(map, TerrainDefOf.Concrete, 4, 13, 39, 15);     // corridor
            Floor(map, plank, 5, 5, 38, 11);                      // bedrooms
            Floor(map, tile, 5, 17, 24, 24);                      // hall
            Floor(map, TerrainDefOf.Concrete, 26, 17, 38, 24);    // workshop
            WallRun(map, granite, 4, 4, 39, 4); WallRun(map, granite, 4, 25, 39, 25);
            WallRun(map, granite, 4, 5, 4, 24); WallRun(map, granite, 39, 5, 39, 24);
            WallRun(map, steel, 5, 12, 38, 12); WallRun(map, steel, 5, 16, 38, 16);
            WallRun(map, wood, 15, 5, 15, 11); WallRun(map, wood, 27, 5, 27, 11);
            WallRun(map, steel, 25, 17, 25, 24);
            foreach (int[] d in new[] { new[] { 10, 12 }, new[] { 21, 12 }, new[] { 33, 12 }, new[] { 14, 16 }, new[] { 31, 16 }, new[] { 4, 14 }, new[] { 39, 14 }, new[] { 25, 20 } })
            {
                Put(map, "Door", steel, d[0], d[1]);
            }
            // bedrooms
            foreach (int x in new[] { 6, 8, 17, 19, 29, 31 })
            {
                Put(map, "Bed", wood, x, 6, Rot4.North);
            }
            Put(map, "EndTable", wood, 7, 5); Put(map, "Dresser", wood, 12, 6, Rot4.South);
            Put(map, "StandingLamp", null, 13, 10); Put(map, "StandingLamp", null, 25, 10); Put(map, "StandingLamp", null, 37, 10);
            Put(map, "PlantPot", steel, 22, 5);
            // hall: tables and chairs, a stove against the back wall
            Put(map, "Table2x4c", wood, 9, 20, Rot4.North); Put(map, "Table2x4c", wood, 18, 20, Rot4.North);
            foreach (int x in new[] { 8, 11, 17, 20 })
            {
                Put(map, "DiningChair", wood, x, 21, x % 2 == 0 ? Rot4.East : Rot4.West);
            }
            Put(map, "FueledStove", steel, 6, 23, Rot4.South); Put(map, "StandingLamp", null, 22, 18); Put(map, "HorseshoesPin", wood, 22, 22);
            // workshop
            Put(map, "TableMachining", null, 30, 23, Rot4.South); Put(map, "ElectricSmelter", null, 35, 23, Rot4.South); Put(map, "Shelf", wood, 28, 18, Rot4.North);
            Put(map, "StandingLamp", null, 37, 18);
            // food, so a run of days watches recreation and not starvation
            for (int i = 0; i < 6; i++)
            {
                Thing meals = ThingMaker.MakeThing(ThingDefOf.MealSurvivalPack);
                meals.stackCount = 10;
                GenSpawn.Spawn(meals, C(6 + i, 18), map);
            }
            map.mapDrawer.RegenerateEverythingNow();
            List<Pawn> pawns = map.mapPawns.FreeColonistsSpawned.ToList();
            for (int i = 0; i < pawns.Count; i++)
            {
                pawns[i].jobs?.StopAll();
                pawns[i].DeSpawn();
                GenSpawn.Spawn(pawns[i], C(12 + 2 * i, 18), map);
            }
            return "COLONY origin " + origin.x + "," + origin.z + " | pawns " + pawns.Count;
        }

        /// <summary>Every mark def on rows of wall (steel then granite then wood), with vanilla filth on the floor below for comparison.
        /// args "page": 0.. -> GALLERY rects. Row spacing leaves the floor in front visible.</summary>
        public static string Gallery(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            Pawn hand = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (hand == null) return "REFUSED no colonist";
            origin = new IntVec3(map.Size.x / 2 - 14, 0, 12);
            List<ThingDef> marks = DefDatabase<ThingDef>.AllDefsListForReading.Where(d => d.GetModExtension<ModExtension_Graffiti>() != null).OrderBy(d => d.defName).ToList();
            const int RowLen = 28, RowStep = 4;
            ThingDef[] stuffs = { ThingDefOf.Steel, ThingDefOf.BlocksGranite, ThingDefOf.WoodLog };
            int rows = 0, cursor = 0;
            Clear(map, new CellRect(origin.x, origin.z, RowLen, 60), TerrainDefOf.Concrete);
            foreach (ThingDef mark in marks)
            {
                float w = GraffitiPool.WidthOf(mark);
                int need = (int)w + 1;
                if (cursor == 0 || cursor + need > RowLen - 1)
                {
                    int wallZ = (++rows) * RowStep;
                    WallRun(map, stuffs[(rows - 1) % stuffs.Length], 0, wallZ, RowLen - 1, wallZ);
                    cursor = 1;
                }
                IntVec3 cell = C(cursor + (int)(w / 2f), rows * RowStep - 1);
                Filth_Mark.MakeMark(cell, map, mark, hand);
                cursor += need;
            }
            string[] filth = { "Filth_Dirt", "Filth_Trash", "Filth_Blood", "Filth_RubbleRock", "Filth_Vomit", "Filth_Slime" };
            for (int i = 0; i < filth.Length; i++)
            {
                ThingDef f = DefDatabase<ThingDef>.GetNamedSilentFail(filth[i]);
                if (f != null) FilthMaker.TryMakeFilth(C(2 + 3 * i, 1), map, f, 3);
            }
            return "GALLERY origin " + origin.x + "," + origin.z + " | rows " + rows + " | step " + RowStep + " | len " + RowLen + " | marks " + marks.Count;
        }

        /// <summary>One room: the same tag on each of its four walls inside, and each wall's outer face. -> FACES x,z,w,h</summary>
        public static string Faces(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            Pawn hand = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (hand == null) return "REFUSED no colonist";
            origin = new IntVec3(10, 0, 12);
            Clear(map, new CellRect(origin.x, origin.z, 20, 16), TerrainDefOf.Concrete);
            WallRun(map, ThingDefOf.Steel, 4, 3, 14, 3); WallRun(map, ThingDefOf.Steel, 4, 11, 14, 11);
            WallRun(map, ThingDefOf.Steel, 4, 4, 4, 10); WallRun(map, ThingDefOf.Steel, 14, 4, 14, 10);
            ThingDef[] m = { DefDatabase<ThingDef>.GetNamed("RM_Graffiti_Tag_A"), DefDatabase<ThingDef>.GetNamed("RM_Graffiti_ThrowUp_A"), DefDatabase<ThingDef>.GetNamed("RM_Graffiti_Tag_B"), DefDatabase<ThingDef>.GetNamed("RM_Graffiti_Stencil_Fist") };
            int[][] cells =
            {
                new[] { 7, 10 }, new[] { 11, 10 },   // inside, north wall
                new[] { 7, 4 }, new[] { 11, 4 },     // inside, south wall
                new[] { 13, 6 }, new[] { 13, 9 },    // inside, east wall
                new[] { 5, 6 }, new[] { 5, 9 },      // inside, west wall
                new[] { 6, 2 }, new[] { 12, 2 },     // outside, on the south wall's outer (front) face
                new[] { 6, 12 }, new[] { 12, 12 },   // outside, on the north wall's outer (back) face
                new[] { 15, 7 }, new[] { 3, 7 },     // outside, east and west
            };
            for (int i = 0; i < cells.Length; i++)
            {
                Filth_Mark.MakeMark(C(cells[i][0], cells[i][1]), map, m[i % m.Length], hand);
            }
            return "FACES " + origin.x + "," + origin.z + ",20,16";
        }

        /// <summary>Beauty at a glance and dirt beside paint: on one wall, a run of Vandal (-15) then tallies (-3), and vanilla filth on the
        /// floor below both. -> COMPARE x,z,w,h</summary>
        public static string Compare(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            Pawn hand = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (hand == null) return "REFUSED no colonist";
            origin = new IntVec3(10, 0, 40);
            Clear(map, new CellRect(origin.x, origin.z, 26, 8), TerrainDefOf.Concrete);
            WallRun(map, ThingDefOf.Steel, 0, 5, 25, 5);
            foreach (IntVec3 c in new CellRect(origin.x, origin.z, 26, 8)) map.areaManager.Home[c] = false;   // or the colonists clean the comparison away
            ThingDef vandal = RMGraffitiDefOf.RM_Graffiti_Vandal, tally = DefDatabase<ThingDef>.GetNamed("RM_Graffiti_TallyMarks");
            for (int x = 1; x <= 11; x += 2) Filth_Mark.MakeMark(C(x, 4), map, vandal, hand);
            for (int x = 14; x <= 24; x += 2) Filth_Mark.MakeMark(C(x, 4), map, tally, hand);
            string[] filth = { "Filth_Dirt", "Filth_Trash", "Filth_Blood", "Filth_RubbleRock", "Filth_Vomit", "Filth_Slime", "Filth_Ash", "Filth_Fuel" };
            for (int i = 0; i < filth.Length; i++)
            {
                ThingDef f = DefDatabase<ThingDef>.GetNamedSilentFail(filth[i]);
                if (f != null) FilthMaker.TryMakeFilth(C(2 + 3 * i, 2), map, f, 4);
            }
            return "COMPARE " + origin.x + "," + origin.z + ",26,7";
        }

        /// <summary>WALLGONE: paint a mark on a fresh wall, destroy the wall; the mark must not outlive it. -> before/after counts.</summary>
        public static string WallGone(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            Pawn hand = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (hand == null) return "REFUSED no colonist";
            origin = new IntVec3(40, 0, 40);
            Clear(map, new CellRect(origin.x, origin.z, 6, 4), TerrainDefOf.Concrete);
            WallRun(map, ThingDefOf.Steel, 0, 2, 5, 2);
            Filth_Mark m = Filth_Mark.MakeMark(C(2, 1), map, DefDatabase<ThingDef>.GetNamed("RM_Graffiti_Tag_A"), hand);
            bool made = m != null && m.Spawned;
            C(2, 2).GetEdifice(map).Destroy(DestroyMode.Deconstruct);
            return "WALLGONE made " + made + " | destroyed " + (m == null || m.Destroyed);
        }

        /// <summary>The real thing: args "n" free colonists start the forced spree. -> SPREE started k of n</summary>
        public static string Spree(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            int want = int.TryParse(args, out int n) ? n : 1;
            int k = 0;
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned.Where(p => !p.Downed && !p.InMentalState).Take(want).ToList())
            {
                if (p.mindState.mentalStateHandler.TryStartMentalState(RMGraffitiDefOf.RM_GraffitiPaintingSpreeState, "stage", forced: true, forceWake: true)) k++;
            }
            return "SPREE started " + k + " of " + want;
        }

        /// <summary>WHO: each colonist's joy, tolerance for this mark's kind, current job, and what the paint joy giver answers now.</summary>
        public static string Who(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            JoyGiverDef giver = DefDatabase<JoyGiverDef>.GetNamed("RM_PaintGraffitiJoy");
            var rows = new List<string>();
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
            {
                bool found = GraffitiJobUtility.TryFindWallMarkCell(p, out IntVec3 cell);
                rows.Add(p.LabelShort + " joy=" + (p.needs?.joy?.CurLevelPercentage.ToString("F2") ?? "none")
                    + " chance=" + giver.Worker.GetChance(p).ToString("F2")
                    + " can=" + giver.Worker.CanBeGivenTo(p)
                    + " job=" + (p.CurJobDef?.defName ?? "none")
                    + " wall=" + found + (found ? "@" + cell : "")
                    + " give=" + (giver.Worker.TryGiveJob(p)?.def.defName ?? "null")
                    + " sched=" + (p.timetable?.CurrentAssignment?.defName ?? "?")
                    + " medTol=" + (p.needs?.joy?.tolerances?[giver.joyKind].ToString("F2") ?? "?")
                    + " bored=" + (p.needs?.joy?.tolerances?.BoredOf(giver.joyKind).ToString() ?? "?")
                    + " pos=" + p.Position + " room=" + (p.GetRoom()?.CellCount ?? -1)
                    );
            }
            return "WHO " + string.Join(" || ", rows);
        }

        /// <summary>COUNT: marks on the map by def, and how many stand with no wall behind them.</summary>
        public static string Count(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            List<Filth_Mark> all = map.listerThings.ThingsInGroup(ThingRequestGroup.Filth).OfType<Filth_Mark>().ToList();
            return "COUNT " + all.Count + " noWall " + all.Count(m => m.wallSide == RM_GraffitiKernel.NoWall) + " | "
                + string.Join(" ", all.GroupBy(m => m.def.defName.Replace("RM_Graffiti_", "")).OrderByDescending(g => g.Count()).Select(g => g.Key + ":" + g.Count()));
        }
    }
}
