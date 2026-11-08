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
            // Door cells take the room's floor: bare soil under a door bleeds dirt tufts onto both rooms.
            foreach (int[] d in new[] { new[] { 10, 12 }, new[] { 21, 12 }, new[] { 33, 12 }, new[] { 14, 16 }, new[] { 31, 16 }, new[] { 25, 20 } })
            {
                map.terrainGrid.SetTerrain(C(d[0], d[1]), TerrainDefOf.Concrete);
            }
            foreach (int[] d in new[] { new[] { 4, 14 }, new[] { 39, 14 } }) map.terrainGrid.SetTerrain(C(d[0], d[1]), TerrainDefOf.Concrete);
            // Power first, so everything spawned after it connects. Conduit runs inside the walls, as a colony builds it, with three fuelled generators out back.
            foreach (int[] run in new[] { new[] { 5, 12, 41, 12 }, new[] { 25, 12, 25, 25 }, new[] { 26, 25, 38, 25 }, new[] { 5, 16, 25, 16 } })
            {
                for (int x = run[0]; x <= run[2]; x++)
                {
                    for (int z = run[1]; z <= run[3]; z++)
                    {
                        Thing pipe = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("PowerConduit"));
                        pipe.SetFaction(Faction.OfPlayer);
                        GenSpawn.Spawn(pipe, C(x, z), map, Rot4.North, WipeMode.VanishOrMoveAside, respawningAfterLoad: false, forbidLeavings: false);
                    }
                }
            }
            Put(map, "WoodFiredGenerator", null, 41, 13, Rot4.North);
            Put(map, "WoodFiredGenerator", null, 41, 10, Rot4.North);
            Put(map, "WoodFiredGenerator", null, 41, 7, Rot4.North);
            Put(map, "Battery", null, 41, 16, Rot4.North);
            // bedrooms
            // a bed for each of the cast and one spare, three to a room
            foreach (int x in new[] { 6, 8, 10, 17, 19, 21, 29, 31, 33 })
            {
                Put(map, "Bed", wood, x, 6, Rot4.North);
            }
            Put(map, "EndTable", wood, 7, 5); Put(map, "Dresser", wood, 12, 6, Rot4.South);
            foreach (int[] lamp in new[] { new[] { 13, 10 }, new[] { 6, 10 }, new[] { 25, 10 }, new[] { 17, 10 }, new[] { 37, 10 }, new[] { 29, 10 }, new[] { 10, 15 }, new[] { 24, 15 }, new[] { 36, 15 }, new[] { 13, 20 } })
            {
                Put(map, "StandingLamp", null, lamp[0], lamp[1]);
            }
            Put(map, "PlantPot", steel, 22, 5);
            // hall: tables and chairs, a stove against the back wall
            Put(map, "Table2x4c", wood, 9, 20, Rot4.North); Put(map, "Table2x4c", wood, 18, 20, Rot4.North);
            foreach (int x in new[] { 8, 11, 17, 20 })
            {
                Put(map, "DiningChair", wood, x, 21, x % 2 == 0 ? Rot4.East : Rot4.West);
            }
            Put(map, "FueledStove", steel, 6, 23, Rot4.South); Put(map, "StandingLamp", null, 21, 18); Put(map, "StandingLamp", null, 22, 23); Put(map, "HorseshoesPin", wood, 19, 23);
            // workshop
            Put(map, "TableMachining", null, 30, 23, Rot4.South); Put(map, "ElectricSmelter", null, 35, 23, Rot4.South); Put(map, "Shelf", wood, 28, 18, Rot4.North);
            Put(map, "StandingLamp", null, 37, 18); Put(map, "StandingLamp", null, 27, 22); Put(map, "StandingLamp", null, 33, 22);
            // food, so a run of days watches recreation and not starvation; stores and clutter, so it looks like people live here
            // Live 2026-11-07: 60 meals ran out on day 7 and three of eight starved or sickened: a week's run watched a famine, not a colony.
            for (int i = 0; i < 14; i++)
            {
                Thing meals = ThingMaker.MakeThing(ThingDefOf.MealSurvivalPack);
                meals.stackCount = 10;
                GenSpawn.Spawn(meals, C(6 + i % 7, 18 - i / 7), map);
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

        /// <summary>Give the colony a day's work, so a run of days measures an ordinary colony and not eight people with nothing to do: a potato
        /// field to sow, a granite storeroom to build from blueprints with its blocks dumped in the yard, steel and wood scattered to haul into
        /// a stockpile, every bill set to forever, and the trees near the base marked to cut. Call after Colony. -> BUSY counts</summary>
        public static string Busy(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            origin = new IntVec3(map.Size.x / 2 - W / 2, 0, map.Size.z / 2 - H / 2);
            CellRect field = new CellRect(origin.x + 24, origin.z - 15, 16, 10);
            Clear(map, field.ExpandedBy(1), TerrainDefOf.Soil);
            Zone_Growing zone = new Zone_Growing(map.zoneManager);
            map.zoneManager.RegisterZone(zone);
            foreach (IntVec3 c in field) zone.AddCell(c);
            ThingDef potato = DefDatabase<ThingDef>.GetNamedSilentFail("Plant_Potato");
            if (potato != null) zone.SetPlantDefToGrow(potato);
            CellRect store = new CellRect(origin.x + 47, origin.z + 3, 9, 8);
            Clear(map, store.ExpandedBy(2), TerrainDefOf.Soil);
            int blueprints = 0;
            foreach (IntVec3 c in store.EdgeCells)
            {
                if (c.z == store.minZ && c.x == store.minX + 4) continue;     // the doorway
                GenConstruct.PlaceBlueprintForBuild(ThingDefOf.Wall, c, map, Rot4.North, Faction.OfPlayer, ThingDefOf.BlocksGranite);
                blueprints++;
            }
            GenConstruct.PlaceBlueprintForBuild(ThingDefOf.Door, new IntVec3(store.minX + 4, 0, store.minZ), map, Rot4.North, Faction.OfPlayer, ThingDefOf.WoodLog);
            for (int i = 0; i < 4; i++)
            {
                Thing blocks = ThingMaker.MakeThing(ThingDefOf.BlocksGranite);
                blocks.stackCount = 75;
                GenSpawn.Spawn(blocks, new IntVec3(store.minX + 2 * i, 0, store.minZ - 2), map);
            }
            Zone_Stockpile pile = new Zone_Stockpile(StorageSettingsPreset.DefaultStockpile, map.zoneManager);
            map.zoneManager.RegisterZone(pile);
            foreach (IntVec3 c in new CellRect(origin.x + 27, origin.z + 17, 11, 2))
            {
                if (c.GetEdifice(map) == null) pile.AddCell(c);
            }
            int hauls = 0;
            for (int i = 0; i < 14; i++)
            {
                Thing heap = ThingMaker.MakeThing(i % 2 == 0 ? ThingDefOf.Steel : ThingDefOf.WoodLog);
                heap.stackCount = 30;
                IntVec3 at = new IntVec3(origin.x - 6 + (i * 5) % 50, 0, origin.z + H + 3 + (i * 3) % 6);
                if (at.InBounds(map) && at.Standable(map) && GenPlace.TryPlaceThing(heap, at, map, ThingPlaceMode.Near)) hauls++;
            }
            int bills = 0;
            foreach (Building b in map.listerBuildings.allBuildingsColonist)
            {
                if (!(b is IBillGiver giver)) continue;
                foreach (Bill bill in giver.BillStack.Bills)
                {
                    if (bill is Bill_Production prod)
                    {
                        prod.repeatMode = BillRepeatModeDefOf.Forever;
                        bills++;
                    }
                }
            }
            int trees = 0;
            foreach (Plant plant in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant).OfType<Plant>().ToList())
            {
                if (plant.def.plant.IsTree && plant.Position.InHorDistOf(C(W / 2, H / 2), 40f) && map.designationManager.DesignationOn(plant) == null)
                {
                    map.designationManager.AddDesignation(new Designation(plant, DesignationDefOf.CutPlant));
                    trees++;
                }
            }
            return "BUSY field " + field.Area + " | blueprints " + blueprints + " | hauls " + hauls + " | bills forever " + bills + " | trees to cut " + trees;
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

        /// <summary>Proof only: draw a clumsy hand the pass-13 way (its smeared double over the mark, muddier paint) so the old and new looks can be
        /// shot on one wall a few seconds apart. Never saved.</summary>
        internal static bool smearOver;

        /// <summary>SMEAR old|new: switch how clumsy hands draw, and redraw the map. -> SMEAR state.</summary>
        public static string Smear(string args)
        {
            smearOver = args == "old";
            Find.CurrentMap?.mapDrawer.RegenerateEverythingNow();
            return "SMEAR " + (smearOver ? "old" : "new");
        }

        /// <summary>never_reads_as_dirt and mark_ugliness_is_visible on one lit wall, as a player meets them: the ugliest hands (an awful scrawl, an
        /// awful and a poor glyph, a poor tag), a tally, a tag half weathered away, a good piece, with vanilla filth on the floor in front and at the
        /// wall's foot. args: the wall's stuff (BlocksGranite by default). -> DIRT rect | x:def:craft:Beauty per mark.</summary>
        public static string Dirt(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            Pawn hand = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (hand == null) return "REFUSED no colonist";
            string[] a = (args ?? "").Split(',');
            ThingDef stuff = DefDatabase<ThingDef>.GetNamedSilentFail(a[0].NullOrEmpty() || a[0] == "x" ? "BlocksGranite" : a[0]) ?? ThingDefOf.BlocksGranite;
            bool doors = a.Contains("door");
            origin = new IntVec3(10, 0, 40);
            const int Len = 30;
            Clear(map, new CellRect(origin.x, origin.z, Len, 8), TerrainDefOf.Soil);
            WallRun(map, stuff, 0, 5, Len - 1, 5);
            foreach (IntVec3 c in new CellRect(origin.x, origin.z, Len, 8)) map.areaManager.Home[c] = false;
            var marks = new (string def, int craft, int weather)[]
            {
                ("RM_Graffiti_Vandal", RM_GraffitiKernel.Awful, 0), ("RM_Graffiti_Glyph_HighLife", RM_GraffitiKernel.Awful, 0), ("RM_Graffiti_Tag_A", RM_GraffitiKernel.Poor, 0),
                ("RM_Graffiti_TallyMarks", RM_GraffitiKernel.Normal, 0), ("RM_Graffiti_Glyph_AnimalPersonhood", RM_GraffitiKernel.Poor, 0),
                ("RM_Graffiti_Tag_B", RM_GraffitiKernel.Normal, 2), ("RM_Graffiti_Scratches", RM_GraffitiKernel.Normal, 0), ("RM_Graffiti_Piece", RM_GraffitiKernel.Good, 0),
            };
            int cursor = 1, now = Find.TickManager.TicksGame;
            var parts = new List<string>();
            foreach (var spec in marks)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(spec.def);
                if (def == null) continue;
                int w = (int)System.Math.Ceiling(GraffitiPool.WidthOf(def));
                Filth_Mark m = Filth_Mark.MakeMark(C(cursor + w / 2, 4), map, def, hand);
                if (m != null)
                {
                    m.hasCraft = true;
                    m.craft = spec.craft;
                    if (spec.weather > 0)
                    {
                        // Dated back so its age, not a flag, puts it at that step: WeatherFade starts at 0.6 of a life and is gone at 1.0.
                        ModExtension_Graffiti ext = def.GetModExtension<ModExtension_Graffiti>();
                        float life = RM_GraffitiKernel.WeatherDays(ext?.form ?? GraffitiForm.Scrawl, m.craft, !map.roofGrid.Roofed(m.Position), m.thingIDNumber);
                        m.placedTick = now - (int)((0.6f + 0.4f * (spec.weather - 0.5f) / 4f) * life * GenDate.TicksPerDay);
                        m.weatherStep = m.WeatherStepNow(out _);
                    }
                    parts.Add((cursor + w / 2) + ":" + def.defName.Replace("RM_Graffiti_", "") + ":" + m.CraftLabel + ":" + m.NetBeauty.ToString("+0;-0;0") + (m.weatherStep > 0 ? ":W" + m.weatherStep : ""));
                }
                cursor += w + 1;
            }
            string[] filth = { "Filth_Dirt", "Filth_Blood", "Filth_Vomit", "Filth_Ash", "Filth_Trash", "Filth_Slime", "Filth_RubbleRock", "Filth_Fuel", "Filth_AnimalFilth" };
            for (int i = 0; i < filth.Length; i++)
            {
                ThingDef f = DefDatabase<ThingDef>.GetNamedSilentFail(filth[i]);
                if (f == null) continue;
                FilthMaker.TryMakeFilth(C(2 + 3 * i, 2), map, f, 4);
                FilthMaker.TryMakeFilth(C(3 + 3 * i, 4), map, f, 2);     // at the wall's foot, right under the paint
            }
            if (doors)
            {
                // A door put into a painted wall, as a player would: one under the scrawl's own wall cell (the paint goes with its wall), one beside
                // the piece's (its paint stops at the door, not across it).
                Put(map, "Door", ThingDefOf.Steel, 2, 5);
                Put(map, "Door", ThingDefOf.Steel, 22, 5);
                parts.Add("doors@2,22");
            }
            map.mapDrawer.RegenerateEverythingNow();
            return "DIRT " + origin.x + "," + origin.z + "," + Len + ",7 | " + string.Join(" ", parts);
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

        /// <summary>The owner's art-skill line at a glance: one mark (args: its def, a Piece by default) at every craft from awful to legendary, left to
        /// right on one granite wall, as the hands of seven skills would leave it. -> CRAFTS rect | x:craft:Beauty per column.</summary>
        public static string Crafts(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            Pawn hand = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (hand == null) return "REFUSED no colonist";
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(args.NullOrEmpty() || args == "x" ? "RM_Graffiti_Piece" : args);
            if (def == null) return "REFUSED no such mark";
            origin = new IntVec3(6, 0, map.Size.z - 26);
            int w = (int)System.Math.Ceiling(GraffitiPool.WidthOf(def));
            int len = 7 * (w + 1) + 1;
            Clear(map, new CellRect(origin.x, origin.z, len, 5), TerrainDefOf.Concrete);
            WallRun(map, ThingDefOf.BlocksGranite, 0, 3, len - 1, 3);
            foreach (IntVec3 c in new CellRect(origin.x, origin.z, len, 5)) map.areaManager.Home[c] = false;
            var parts = new List<string>();
            for (int q = 0; q < 7; q++)
            {
                int x = 1 + q * (w + 1) + w / 2;
                Filth_Mark m = Filth_Mark.MakeMark(C(x, 2), map, def, hand);
                if (m == null) continue;
                m.craft = q;
                parts.Add(x + ":" + m.CraftLabel + ":" + m.NetBeauty.ToString("+0;-0;0"));
            }
            map.mapDrawer.RegenerateEverythingNow();
            return "CRAFTS " + origin.x + "," + origin.z + "," + len + ",5 | " + string.Join(" ", parts);
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

        /// <summary>Put every pawn's drawing where the pawn is. The tweener only moves while frames run unpaused, so after a fast advance
        /// a paused camera draws colonists where they stood a day ago, which reads as a staged shot and is false.</summary>
        /// <summary>NAME faction/settlement: name the player's faction and its home as the player would, so the game stops putting its naming
        /// dialog over every shot after day 4.3 (Faction.FactionTick), and so captions can say which colony a shot is from. -> NAMED.</summary>
        public static string Name(string args)
        {
            if (Faction.OfPlayer == null) return "REFUSED no game";
            string[] parts = (args ?? "").Split('/');
            if (parts.Length < 2 || parts[0].NullOrEmpty() || parts[1].NullOrEmpty()) return "REFUSED usage faction/settlement";
            Faction.OfPlayer.Name = parts[0];
            int n = 0;
            foreach (RimWorld.Planet.Settlement s in Find.WorldObjects.Settlements)
            {
                if (s.Faction != Faction.OfPlayer) continue;
                s.Name = n == 0 ? parts[1] : parts[1] + " " + (n + 1);
                s.namedByPlayer = true;
                n++;
            }
            foreach (Window w in Find.WindowStack.Windows.ToList())
            {
                if (w is Dialog_NamePlayerFaction || w is Dialog_NamePlayerFactionAndSettlement || w is Dialog_NamePlayerSettlement) w.Close(false);
            }
            return "NAMED " + Faction.OfPlayer.Name + " / " + parts[1] + " (" + n + " settlements)";
        }

        /// <summary>BEAUTY on|off: the game's own Beauty overlay (the play-settings toggle), so a shot shows each cell's Beauty where the
        /// player would read it, around the hovered cell. -> BEAUTY state.</summary>
        public static string Beauty(string args)
        {
            if (Find.PlaySettings == null) return "REFUSED no game";
            Find.PlaySettings.showBeauty = args != "off";
            return "BEAUTY " + (Find.PlaySettings.showBeauty ? "on" : "off");
        }

        public static string Settle(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            int n = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                p.Drawer?.tweener?.ResetTweenedPosToRoot();
                n++;
            }
            return "SETTLED " + n;
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

        /// <summary>SCRUB x,z,w,h: the player drags the Scrub graffiti order over this rect, through the designator's own drag path.
        /// -> SCRUB marks designated, and the cells the drag refused.</summary>
        public static string Scrub(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            int[] r = (args ?? "").Split(',').Select(s => int.TryParse(s.Trim(), out int v) ? v : -1).ToArray();
            if (r.Length != 4 || r.Any(v => v < 0)) return "REFUSED want x,z,w,h";
            Designator_ScrubGraffiti d = new Designator_ScrubGraffiti();
            List<IntVec3> cells = new CellRect(r[0], r[1], r[2], r[3]).Cells.Where(c => d.CanDesignateCell(c).Accepted).ToList();
            int before = map.designationManager.SpawnedDesignationsOfDef(RMGraffitiDefOf.RM_ScrubGraffiti).Count();
            d.DesignateMultiCell(cells);
            int after = map.designationManager.SpawnedDesignationsOfDef(RMGraffitiDefOf.RM_ScrubGraffiti).Count();
            return "SCRUB designated " + (after - before) + " marks over " + cells.Count + " cells, " + after + " waiting";
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
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned.ToList())
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
