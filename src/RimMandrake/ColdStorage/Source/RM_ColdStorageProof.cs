using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace RimMandrake.ColdStorage
{
    /// <summary>
    /// static_call probe for COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE (design/RimStarWars/cold_storage_line_2026-10-26.md
    /// §9.9). <c>Run("A1")</c> .. <c>Run("A6")</c> stage on the current map, measure, destroy what they made and return
    /// one line "COLDPROOF A&lt;n&gt; key=value ..."; coldstorage_live_proof.py judges it. Synchronous: game time does not
    /// move; a day is 240 hand steps of 250 ticks (unit Step, then each item's CompTickInterval) in a roofed steel room
    /// held at 25 C. A unit's power is forced on (no power net forms inside one call; the grid is vanilla, not ours).
    /// A1 chill (RSW_CryoUnit) · A2 stasis (RM_AncientStasisLocker_Original) · A3 sealed (RM_ResinSealedMeat), each against
    /// floor meat in the same room · A4 aging transition · A5 wall unit: room intact, prisoner in the facing room may
    /// eat from it, one outside may not, reach by Touch · A6 the cryo unit and its meat carried by a gravship lifted and
    /// set down on the same map (no flight, no world travel). "REFUSED: ..." = could not stage (unmeasured).
    /// </summary>
    public static class RM_ColdStorageProof
    {
        private const float RoomTemp = 25f;
        private const int Step = 250;
        private const int StepsPerDay = 240;

        public static string Run(string clause)
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "REFUSED: no current map";
            }
            var made = new List<Thing>();
            var roofed = new List<IntVec3>();
            try
            {
                switch (clause)
                {
                    case "A1": return RotClause(map, made, roofed, "A1", "RSW_CryoUnit");
                    case "A2": return RotClause(map, made, roofed, "A2", "RM_AncientStasisLocker_Original");
                    case "A3": return RotClause(map, made, roofed, "A3", null);
                    case "A4": return Aging(map, made, roofed);
                    case "A5": return Wall(map, made, roofed);
                    case "A6": return Gravship(map, made);
                    default: return "REFUSED: unknown clause " + clause + " (A1..A6)";
                }
            }
            catch (Exception ex)
            {
                return "REFUSED: " + clause + " threw " + ex.GetType().Name + ": " + ex.Message;
            }
            finally
            {
                foreach (Thing t in made.AsEnumerable().Reverse())
                {
                    if (!t.Destroyed)
                    {
                        t.Destroy();
                    }
                }
                foreach (IntVec3 c in roofed)
                {
                    map.roofGrid.SetRoof(c, null);
                }
            }
        }

        // ---------------------------------------------------------------- staging

        private static bool Clear(Map map, IntVec3 c) => c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null
            && c.GetFirstPawn(map) == null && c.GetFirstItem(map) == null && !c.Fogged(map) && !c.Roofed(map)
            && !c.GetTerrain(map).IsWater && map.terrainGrid.FoundationAt(c) == null;

        /// <summary>An open w×h patch near the centre holding no item, pawn, building or foundation; its plants and
        /// filth are cleared (nothing a colony owns is destroyed).</summary>
        private static bool FindSite(Map map, int w, int h, out CellRect rect)
        {
            CellRect found = CellRect.Empty;
            bool ok = CellFinder.TryFindRandomCellNear(map.Center, map, 60, c =>
            {
                var r = new CellRect(c.x, c.z, w, h);
                return r.Cells.All(x => Clear(map, x));
            }, out IntVec3 at);
            if (ok)
            {
                found = new CellRect(at.x, at.z, w, h);
                foreach (IntVec3 c in found)
                {
                    foreach (Thing t in c.GetThingList(map).ToList())
                    {
                        if (t.def.destroyable && (t.def.category == ThingCategory.Plant || t.def.category == ThingCategory.Filth))
                        {
                            t.Destroy();
                        }
                    }
                }
            }
            rect = found;
            return ok;
        }

        private static Thing Spawn(Map map, List<Thing> made, Thing t, IntVec3 c, Rot4 rot)
        {
            Thing s = GenSpawn.Spawn(t, c, map, rot, WipeMode.Vanish);
            made.Add(s);
            return s;
        }

        private static Thing SpawnDef(Map map, List<Thing> made, ThingDef def, IntVec3 c, int count = 1, Rot4? rot = null)
        {
            Thing t = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
            t.stackCount = Math.Min(count, def.stackLimit);
            if (def.CanHaveFaction)
            {
                t.SetFactionDirect(Faction.OfPlayer);
            }
            return Spawn(map, made, t, c, rot ?? Rot4.North);
        }

        /// <summary>A 7×7 steel-walled, roofed room at <paramref name="r"/> (interior 5×5), held at 25 C.</summary>
        private static Room BuildRoom(Map map, List<Thing> made, List<IntVec3> roofed, CellRect r)
        {
            foreach (IntVec3 c in r.EdgeCells)
            {
                Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.Steel);
                wall.SetFactionDirect(Faction.OfPlayer);
                Spawn(map, made, wall, c, Rot4.North);
            }
            foreach (IntVec3 c in r)
            {
                map.roofGrid.SetRoof(c, RoofDefOf.RoofConstructed);
                roofed.Add(c);
            }
            return HoldRoom(map, r.ContractedBy(1).CenterCell);
        }

        private static Room HoldRoom(Map map, IntVec3 inside)
        {
            map.regionAndRoomUpdater.TryRebuildDirtyRegionsAndRooms();
            Room room = inside.GetRoom(map);
            if (room != null && !room.UsesOutdoorTemperature)
            {
                room.Temperature = RoomTemp;
            }
            return room;
        }

        private static ThingDef Meat()
        {
            return DefDatabase<ThingDef>.GetNamedSilentFail("Meat_Cow")
                ?? DefDatabase<ThingDef>.AllDefs.FirstOrDefault(d => d.IsMeat && d.HasComp(typeof(CompRottable)));
        }

        private static void ForcePower(Thing unit)
        {
            CompPowerTrader p = unit.TryGetComp<CompPowerTrader>();
            if (p != null)
            {
                p.PowerOn = true;
            }
        }

        private static float RotOf(Thing t) => t.TryGetComp<CompRottable>()?.RotProgress ?? -1f;

        private static string F(float v) => v.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture);

        // ---------------------------------------------------------------- A1-A3 rot per mode

        private static string RotClause(Map map, List<Thing> made, List<IntVec3> roofed, string id, string unitDefName)
        {
            ThingDef meat = Meat();
            ThingDef unitDef = unitDefName == null ? null : DefDatabase<ThingDef>.GetNamedSilentFail(unitDefName);
            ThingDef sealedDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ResinSealedMeat");
            if (meat == null || (unitDefName != null && unitDef == null) || (unitDefName == null && sealedDef == null))
            {
                return "REFUSED: " + id + " missing def (meat " + (meat != null) + ", " + (unitDefName ?? "RM_ResinSealedMeat") + ")";
            }
            if (!FindSite(map, 7, 7, out CellRect r))
            {
                return "REFUSED: " + id + " no clear 7x7 patch";
            }
            Room room = BuildRoom(map, made, roofed, r);
            if (room == null || room.UsesOutdoorTemperature)
            {
                return "REFUSED: " + id + " the staged room did not close";
            }
            IntVec3 o = r.Min;
            Thing floor = SpawnDef(map, made, meat, o + new IntVec3(1, 0, 1), 10);
            Thing held;
            CompStorageClimate unit = null;
            if (unitDef != null)
            {
                Thing u = SpawnDef(map, made, unitDef, o + new IntVec3(3, 0, 1));
                ForcePower(u);
                unit = u.TryGetComp<CompStorageClimate>();
                if (unit == null)
                {
                    return "REFUSED: " + id + " " + unitDefName + " has no CompStorageClimate";
                }
                held = SpawnDef(map, made, meat, u.Position, 10);
            }
            else
            {
                held = SpawnDef(map, made, sealedDef, o + new IntVec3(3, 0, 1), 10);
            }
            room = HoldRoom(map, o + new IntVec3(3, 0, 3));   // spawning a unit may rebuild the room object
            float rot0Floor = RotOf(floor), rot0Held = RotOf(held);
            for (int i = 0; i < StepsPerDay; i++)
            {
                if (unit != null)
                {
                    ForcePower(unit.parent);
                    unit.Step(Step);
                }
                floor.TryGetComp<CompRottable>()?.CompTickInterval(Step);
                held.TryGetComp<CompRottable>()?.CompTickInterval(Step);
                room = HoldRoom(map, o + new IntVec3(3, 0, 3)) ?? room;
            }
            string s = "COLDPROOF " + id + " floorRot=" + F(RotOf(floor) - rot0Floor) + " heldRot=" + F(RotOf(held) - rot0Held)
                + " room=" + F(room.Temperature) + " heldAmbient=" + F(held.AmbientTemperature);
            if (unit != null)
            {
                s += " unit=" + unitDef.defName + " mode=" + unit.Effective + " active=" + unit.Active + " unitTemp=" + F(unit.currentTemp)
                    + " setpoint=" + F(unit.EffectiveSetpoint) + " holding=" + (StorageClimateRegistry.UnitHolding(held) == unit);
            }
            else
            {
                s += " sealed=" + CompSealed.IsSealed(held) + " item=" + held.def.defName;
            }
            return s;
        }

        // ---------------------------------------------------------------- A4 aging

        private static string Aging(Map map, List<Thing> made, List<IntVec3> roofed)
        {
            ThingDef sealedDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_ResinSealedMeat");
            if (sealedDef == null)
            {
                return "REFUSED: A4 no RM_ResinSealedMeat";
            }
            if (!RM_ColdStorageSettings.sealAgingEnabled)
            {
                return "REFUSED: A4 seal aging is switched off in Mod Settings";
            }
            if (!FindSite(map, 3, 3, out CellRect r))
            {
                return "REFUSED: A4 no clear patch";
            }
            float oldFail = RM_ColdStorageSettings.sealFailureMultiplier;
            float oldMult = RM_ColdStorageSettings.agingTimeMultiplier;
            try
            {
                RM_ColdStorageSettings.sealFailureMultiplier = 0f;
                RM_ColdStorageSettings.agingTimeMultiplier = 0.001f;   // 20 days -> 1200 ticks; restored below
                IntVec3 cell = r.CenterCell;
                Thing item = SpawnDef(map, made, sealedDef, cell, 10);
                CompSealed seal = CompSealed.SealOf(item);
                CompIngredients ing = item.TryGetComp<CompIngredients>();
                ThingDef ingredient = Meat();
                if (ing != null && ingredient != null && ing.ingredients.Count == 0)
                {
                    ing.ingredients.Add(ingredient);
                }
                if (seal == null || seal.Props.agesInto == null)
                {
                    return "REFUSED: A4 RM_ResinSealedMeat has no CompSealed/agesInto";
                }
                int now = Find.TickManager.TicksGame;
                int aging = seal.AgingTicks;
                if (aging <= 0 || now - aging - 1 < 0)
                {
                    return "REFUSED: A4 aging ticks " + aging + " vs game tick " + now;
                }
                seal.sealedTick = now - aging + 1;            // one tick short: must not age yet
                seal.CompTickInterval(Step);
                CompSealed.RunPending();
                bool earlyHeld = !item.Destroyed && item.def == sealedDef;
                seal.sealedTick = now - aging - 1;            // past due: ages on its next check
                seal.CompTickInterval(Step);
                CompSealed.RunPending();
                Thing aged = cell.GetThingList(map).FirstOrDefault(t => t.def == seal.Props.agesInto);
                if (aged != null)
                {
                    made.Add(aged);
                }
                CompIngredients agedIng = aged?.TryGetComp<CompIngredients>();
                return "COLDPROOF A4 agingTicks=" + aging + " earlyHeld=" + earlyHeld + " oldGone=" + item.Destroyed
                    + " aged=" + (aged?.def.defName ?? "none") + " want=" + seal.Props.agesInto.defName
                    + " stack=" + (aged?.stackCount ?? 0)
                    + " ingredientsKept=" + (agedIng != null && ingredient != null && agedIng.ingredients.Contains(ingredient));
            }
            finally
            {
                RM_ColdStorageSettings.sealFailureMultiplier = oldFail;
                RM_ColdStorageSettings.agingTimeMultiplier = oldMult;
            }
        }

        // ---------------------------------------------------------------- A5 wall unit propriety

        private static string Wall(Map map, List<Thing> made, List<IntVec3> roofed)
        {
            ThingDef wallUnitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_CoolingUnit_Wall");
            ThingDef food = new[] { Meat(), ThingDefOf.MealSimple }.FirstOrDefault(d => d != null && d.socialPropernessMatters);
            Faction host = Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f => !f.IsPlayer && !f.Hidden
                && !f.defeated && f.def.humanlikeFaction && f.def.basicMemberKind != null);
            if (wallUnitDef == null || food == null || host == null)
            {
                return "REFUSED: A5 missing RSW_CoolingUnit_Wall " + (wallUnitDef != null) + ", food " + (food != null)
                    + ", a humanlike faction " + (host != null);
            }
            if (!FindSite(map, 7, 10, out CellRect site))
            {
                return "REFUSED: A5 no clear 7x10 patch";
            }
            var r = new CellRect(site.minX, site.minZ, 7, 7);
            IntVec3 o = r.Min;
            BuildRoom(map, made, roofed, r);
            IntVec3 wallCell = o + new IntVec3(3, 0, 6);         // north wall, facing south into the room
            Thing unitThing = SpawnDef(map, made, wallUnitDef, wallCell, 1, Rot4.South);
            ForcePower(unitThing);
            CompStorageClimate unit = unitThing.TryGetComp<CompStorageClimate>();
            Room room = HoldRoom(map, o + new IntVec3(3, 0, 3));
            bool roomIntact = room != null && !room.UsesOutdoorTemperature && room.CellCount == 25;
            Thing meal = SpawnDef(map, made, food, wallCell, 1);
            Pawn inside = Prisoner(map, made, host, o + new IntVec3(3, 0, 4));
            Pawn outside = Prisoner(map, made, host, site.Min + new IntVec3(3, 0, 8));
            bool inOk = meal.IsSociallyProper(inside, true);
            bool outOk = meal.IsSociallyProper(outside, true);
            // OnCell on purpose: our Reachability patch must turn it into Touch for an item in a wall unit (a hauling or
            // eating job asks OnCell); vanilla OnCell into an impassable cell is false.
            bool reach = inside.CanReach(meal, PathEndMode.OnCell, Danger.Deadly);
            return "COLDPROOF A5 food=" + food.defName + " unitFacing=" + unitThing.Rotation.ToStringHuman()
                + " roomCells=" + (room?.CellCount ?? -1) + " roomIntact=" + roomIntact
                + " roomSide=" + (unit != null && unit.RoomSideCell.GetRoom(map) == room)
                + " holding=" + (unit != null && StorageClimateRegistry.UnitHolding(meal) == unit)
                + " insideProper=" + inOk + " outsideProper=" + outOk + " insideReach=" + reach;
        }

        private static Pawn Prisoner(Map map, List<Thing> made, Faction host, IntVec3 c)
        {
            Pawn p = PawnGenerator.GeneratePawn(host.def.basicMemberKind, host);
            Spawn(map, made, p, c, Rot4.South);
            p.guest.SetGuestStatus(Faction.OfPlayer, GuestStatus.Prisoner);
            return p;
        }

        // ---------------------------------------------------------------- A6 gravship carry

        private static string Gravship(Map map, List<Thing> made)
        {
            ThingDef cryoDef = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_CryoUnit");
            ThingDef meat = Meat();
            if (!ModsConfig.OdysseyActive || ThingDefOf.GravEngine == null || TerrainDefOf.Substructure == null)
            {
                return "REFUSED: A6 Odyssey gravship defs absent";
            }
            if (cryoDef == null || meat == null)
            {
                return "REFUSED: A6 missing RSW_CryoUnit or meat";
            }
            if (Current.Game.Gravship != null || Find.GravshipController.LandingAreaConfirmationInProgress)
            {
                return "REFUSED: A6 a gravship is already in flight or landing";
            }
            if (!FindSite(map, 21, 9, out CellRect site))
            {
                return "REFUSED: A6 no clear 21x9 patch";
            }
            const int Shift = 12;
            var deck = new CellRect(site.minX + 1, site.minZ + 1, 7, 7);
            var foundations = new List<IntVec3>();
            Building_GravEngine engine;
            try
            {
                foreach (IntVec3 c in deck)
                {
                    map.terrainGrid.SetFoundation(c, TerrainDefOf.Substructure);
                    foundations.Add(c);
                    foundations.Add(c + new IntVec3(Shift, 0, 0));   // where it lands: cleared even if the landing throws
                }
                engine = (Building_GravEngine)SpawnDef(map, made, ThingDefOf.GravEngine, deck.CenterCell);
                Thing cryo = SpawnDef(map, made, cryoDef, deck.Min + new IntVec3(1, 0, 1));
                Thing food = SpawnDef(map, made, meat, cryo.Position, 10);
                CompStorageClimate unit = cryo.TryGetComp<CompStorageClimate>();
                if (unit == null)
                {
                    return "REFUSED: A6 RSW_CryoUnit has no CompStorageClimate";
                }
                unit.SetSetpoint(unit.Props.defaultSetpoint - 3f);     // a custom setpoint must survive the trip
                unit.currentTemp = -28f;
                float setBefore = unit.setpoint;
                engine.substructureDirty = true;
                bool onDeck = engine.OnValidSubstructure(cryo) && engine.OnValidSubstructure(food);
                if (!onDeck)
                {
                    return "REFUSED: A6 the cryo unit is not on the engine's valid substructure ("
                        + engine.ValidSubstructure.Count + " cells)";
                }
                IntVec3 before = cryo.Position;
                Gravship ship = GravshipUtility.GenerateGravship(engine);
                if (ship == null)
                {
                    return "REFUSED: A6 GenerateGravship returned no ship";
                }
                bool despawned = !cryo.Spawned && !food.Spawned;
                bool carried = ship != null && ship.Things.Contains(cryo) && ship.Things.Contains(food);
                IntVec3 root = engine.Position + new IntVec3(Shift, 0, 0);
                GravshipPlacementUtility.PlaceGravshipInMap(ship, root, map, out List<Thing> spawned);
                typeof(GravshipPlacementUtility).GetMethod("PostSwapMap", BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public)
                    ?.Invoke(null, new object[] { ship, spawned });
                bool landed = cryo.Spawned && cryo.Map == map && cryo.Position == before + new IntVec3(Shift, 0, 0);
                bool foodOn = food.Spawned && food.Position == cryo.Position;
                bool sameUnit = StorageClimateRegistry.UnitHolding(food) == unit;
                return "COLDPROOF A6 carried=" + carried + " despawnedInFlight=" + despawned + " landed=" + landed
                    + " foodOnUnit=" + foodOn + " registered=" + sameUnit + " setpointKept=" + (unit.setpoint == setBefore) + " setpoint=" + F(unit.setpoint)
                    + " unitTemp=" + F(unit.currentTemp) + " foodAmbient=" + F(food.Spawned ? food.AmbientTemperature : float.NaN)
                    + " stack=" + food.stackCount;
            }
            finally
            {
                Current.Game.Gravship = null;                 // none was in flight when the probe began (checked above)
                foreach (IntVec3 c in foundations)
                {
                    if (c.InBounds(map) && map.terrainGrid.FoundationAt(c) != null)
                    {
                        map.terrainGrid.RemoveFoundation(c, false);
                    }
                }
            }
        }
    }
}
