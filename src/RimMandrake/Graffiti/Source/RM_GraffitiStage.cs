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
            // Power first, so everything spawned after it connects: a fuelled generator on a conduit down the corridor, spurs into the rooms.
            for (int x = 5; x <= 41; x++) Put(map, "PowerConduit", null, x, 14);
            foreach (int[] spur in new[] { new[] { 13, 5, 13, 13 }, new[] { 25, 5, 25, 13 }, new[] { 37, 5, 37, 13 }, new[] { 22, 15, 22, 23 }, new[] { 31, 15, 31, 22 } })
            {
                for (int x = spur[0]; x <= spur[2]; x++)
                {
                    for (int z = spur[1]; z <= spur[3]; z++) Put(map, "PowerConduit", null, x, z);
                }
            }
            Put(map, "WoodFiredGenerator", null, 41, 13, Rot4.North);
            Put(map, "Battery", null, 41, 16, Rot4.North);
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
            Put(map, "FueledStove", steel, 6, 23, Rot4.South); Put(map, "StandingLamp", null, 21, 18); Put(map, "HorseshoesPin", wood, 21, 22);
            // workshop
            Put(map, "TableMachining", null, 30, 23, Rot4.South); Put(map, "ElectricSmelter", null, 35, 23, Rot4.South); Put(map, "Shelf", wood, 28, 18, Rot4.North);
            Put(map, "StandingLamp", null, 37, 18);
            // food, so a run of days watches recreation and not starvation; stores and clutter, so it looks like people live here
            for (int i = 0; i < 6; i++)
            {
                Thing meals = ThingMaker.MakeThing(ThingDefOf.MealSurvivalPack);
                meals.stackCount = 10;
                GenSpawn.Spawn(meals, C(6 + i, 18), map);
            }
            foreach (string[] store in new[] { new[] { "RawPotatoes", "75", "12", "23" }, new[] { "RawRice", "60", "13", "23" }, new[] { "Steel", "75", "28", "19" }, new[] { "WoodLog", "75", "29", "18" }, new[] { "WoodLog", "75", "30", "18" }, new[] { "Cloth", "40", "34", "18" }, new[] { "Medicine", "8", "35", "18" }, new[] { "ComponentIndustrial", "12", "36", "18" } })
            {
                ThingDef what = DefDatabase<ThingDef>.GetNamedSilentFail(store[0]);
                if (what == null) continue;
                Thing heap = ThingMaker.MakeThing(what);
                heap.stackCount = System.Math.Min(int.Parse(store[1]), what.stackLimit);
                GenSpawn.Spawn(heap, C(int.Parse(store[2]), int.Parse(store[3])), map);
            }
            // a working kitchen and workshop, not a set: fuel in the fires, bills on the benches
            foreach (Building b in map.listerBuildings.allBuildingsColonist.ToList())
            {
                CompRefuelable fuel = b.TryGetComp<CompRefuelable>();
                if (fuel != null) fuel.Refuel(fuel.Props.fuelCapacity);
                CompPowerBattery cell = b.TryGetComp<CompPowerBattery>();
                if (cell != null) cell.AddEnergy(cell.Props.storedEnergyMax);
                if (b is IBillGiver giver && b.def.AllRecipes != null)
                {
                    RecipeDef recipe = b.def.AllRecipes.FirstOrDefault(r => r.defName == "CookMealSimple" || r.defName == "Make_ComponentIndustrial" || r.defName == "SmeltWeapon") ?? b.def.AllRecipes.FirstOrDefault();
                    if (recipe != null) giver.BillStack.AddBill(BillUtility.MakeNewBill(recipe));
                }
            }
            // a crop out front, a path worn into the yard, the rubbish of living
            for (int x = 8; x <= 22; x++)
            {
                for (int z = 0; z <= 2; z++)
                {
                    Plant crop = (Plant)ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("Plant_Rice"));
                    crop.Growth = 0.35f + 0.5f * ((x * 7 + z * 13) % 10) / 10f;
                    GenSpawn.Spawn(crop, C(x, z), map);
                }
            }
            for (int i = 0; i < 26; i++)
            {
                ThingDef mess = DefDatabase<ThingDef>.GetNamedSilentFail(i % 3 == 0 ? "Filth_Dirt" : (i % 3 == 1 ? "Filth_Trash" : "Filth_Ash"));
                if (mess != null) FilthMaker.TryMakeFilth(C(6 + (i * 13) % 32, 5 + (i * 7) % 19), map, mess, 1);
            }
            map.mapDrawer.RegenerateEverythingNow();
            List<Pawn> pawns = map.mapPawns.FreeColonistsSpawned.ToList();
            for (int i = 0; i < pawns.Count; i++)
            {
                pawns[i].jobs?.StopAll();
                pawns[i].DeSpawn();
                GenSpawn.Spawn(pawns[i], C(12 + 2 * i, 18), map);
            }
            int powered = 0, dark = 0;
            foreach (Building b in map.listerBuildings.allBuildingsColonist)
            {
                CompPowerTrader power = b.TryGetComp<CompPowerTrader>();
                if (power == null) continue;
                if (power.PowerOn) powered++;
                else dark++;
            }
            return "COLONY origin " + origin.x + "," + origin.z + " | pawns " + pawns.Count + " | powered " + powered + " dark " + dark;
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

        /// <summary>Every mark on one wall, worst Beauty on the left, best on the right, in steps of four cells at most. -> LADDER rect | beauty per column,
        /// so the driver can write what each is above it. The stat and the picture, side by side.</summary>
        public static string Ladder(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            Pawn hand = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (hand == null) return "REFUSED no colonist";
            origin = new IntVec3(6, 0, map.Size.z - 16);
            ThingDef stuff = args == "wood" ? ThingDefOf.WoodLog : ThingDefOf.BlocksGranite;
            string[] names = { "RM_Graffiti_Vandal", "RM_Graffiti_Scratches", "RM_Graffiti_CrossOut", "RM_Graffiti_Tag_A", "RM_Graffiti_WarningGlyph", "RM_Graffiti_Stencil_Crown", "RM_Graffiti_ThrowUp_Wide", "RM_Graffiti_TallyMarks", "RM_Graffiti_Paste_Flyer", "RM_Graffiti_IdeoSigil", "RM_Graffiti_Piece" };
            const int Len = 34;
            Clear(map, new CellRect(origin.x, origin.z, Len, 5), TerrainDefOf.Concrete);
            WallRun(map, stuff, 0, 3, Len - 1, 3);
            foreach (IntVec3 c in new CellRect(origin.x, origin.z, Len, 5)) map.areaManager.Home[c] = false;
            int cursor = 1;
            var parts = new List<string>();
            foreach (string name in names)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (def == null) continue;
                int w = (int)System.Math.Ceiling(GraffitiPool.WidthOf(def));
                Filth_Mark.MakeMark(C(cursor + w / 2, 2), map, def, hand);
                parts.Add((cursor + w / 2) + ":" + def.GetStatValueAbstract(StatDefOf.Beauty).ToString("+0;-0;0"));
                cursor += w + 1;
            }
            map.mapDrawer.RegenerateEverythingNow();
            return "LADDER " + origin.x + "," + origin.z + "," + Len + ",5 | " + string.Join(" ", parts);
        }

        /// <summary>One small room in every wall material, each wall carrying marks: the front, both side faces, the hidden south wall from inside and the
        /// front from outside, a wide mark run into a corner, a door in the run, and a free wall end. -> SWEEP rect | rows.</summary>
        public static string Sweep(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            Pawn hand = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (hand == null) return "REFUSED no colonist";
            origin = new IntVec3(4, 0, 6);
            ThingDef[] stuffs = { ThingDefOf.BlocksGranite, ThingDefOf.WoodLog, ThingDefOf.Steel, DefDatabase<ThingDef>.GetNamedSilentFail("BlocksMarble"), DefDatabase<ThingDef>.GetNamedSilentFail("Plasteel"), DefDatabase<ThingDef>.GetNamedSilentFail("BlocksSlate") };
            const int RoomW = 13, RoomH = 7;
            Clear(map, new CellRect(origin.x, origin.z, 3 * (RoomW + 2) + 2, 2 * (RoomH + 3) + 2), TerrainDefOf.Concrete);
            foreach (IntVec3 c in new CellRect(origin.x, origin.z, 3 * (RoomW + 2) + 2, 2 * (RoomH + 3) + 2)) map.areaManager.Home[c] = false;
            ThingDef wide = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Graffiti_ThrowUp_Wide"), piece = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Graffiti_Piece"),
                tag = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Graffiti_Tag_A"), one = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Graffiti_Stencil_Fist");
            for (int i = 0; i < stuffs.Length; i++)
            {
                if (stuffs[i] == null) continue;
                int x0 = 1 + (i % 3) * (RoomW + 2), z0 = 2 + (i / 3) * (RoomH + 3);
                int x1 = x0 + RoomW, z1 = z0 + RoomH;
                WallRun(map, stuffs[i], x0, z0, x1, z0); WallRun(map, stuffs[i], x0, z1, x1, z1);
                WallRun(map, stuffs[i], x0, z0, x0, z1); WallRun(map, stuffs[i], x1, z0, x1, z1);
                Put(map, "Door", ThingDefOf.Steel, x0 + 9, z1);
                // a free wall end in the room
                WallRun(map, stuffs[i], x0 + 4, z0 + 3, x0 + 6, z0 + 3);
                // front: a piece, run hard into the door on its right; a one-cell mark; a wide mark driven into the corner on the left
                Filth_Mark.MakeMark(C(x0 + 7, z1 - 1), map, piece, hand);
                Filth_Mark.MakeMark(C(x0 + 2, z1 - 1), map, wide, hand);
                Filth_Mark.MakeMark(C(x0 + 11, z1 - 1), map, one, hand);
                // side faces, with a wide mark on one
                Filth_Mark.MakeMark(C(x0 + 1, z0 + 4), map, one, hand);
                Filth_Mark.MakeMark(C(x1 - 1, z0 + 3), map, wide, hand);
                // the hidden side: a south wall seen from inside
                Filth_Mark.MakeMark(C(x0 + 8, z0 + 1), map, tag, hand);
                // the free wall's front, then its two ends' side faces
                Filth_Mark.MakeMark(C(x0 + 5, z0 + 2), map, tag, hand);
                Filth_Mark.MakeMark(C(x0 + 3, z0 + 3), map, tag, hand);
                Filth_Mark.MakeMark(C(x0 + 7, z0 + 3), map, tag, hand);
                // the room's south wall seen from outside: a whole front
                Filth_Mark.MakeMark(C(x0 + 5, z0 - 1), map, wide, hand);
            }
            map.mapDrawer.RegenerateEverythingNow();
            return "SWEEP " + origin.x + "," + origin.z + "," + (3 * (RoomW + 2) + 2) + "," + (2 * (RoomH + 3) + 2);
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
