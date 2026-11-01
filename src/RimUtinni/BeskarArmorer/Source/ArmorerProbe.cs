// BESKAR_ARMORER_QUEST_1: the live proof's hands, driven by ../prove_beskar_armorer.py through rimworld/execute_debug_action. Each
// action does the real game call and appends one JSON line per row to <save data>/BeskarArmorerProbe.jsonl. They need dev mode and
// never run on their own.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Utinni.BeskarArmorer
{
    public static class ArmorerProbe
    {
        private const string Cat = "Beskar Armorer";
        public static string FilePath { get { return Path.Combine(GenFilePaths.SaveDataFolderPath, "BeskarArmorerProbe.jsonl"); } }

        private static void Row(string row, bool pass, string detail)
        {
            string esc = (detail ?? "").Replace("\\", "/").Replace("\"", "'").Replace("\n", " ").Replace("\r", " ");
            File.AppendAllText(FilePath, "{\"row\":\"" + row + "\",\"pass\":" + (pass ? "true" : "false") + ",\"detail\":\"" + esc + "\"}\n");
        }

        private static void Guarded(string row, Action a)
        {
            try { a(); }
            catch (Exception e) { Row(row, false, "EXCEPTION " + e.GetType().Name + ": " + e.Message + " @ " + (e.StackTrace ?? "").Split('\n').FirstOrDefault()); }
        }

        private static Map Home { get { return Find.Maps.FirstOrDefault(m => m.IsPlayerHome) ?? Find.AnyPlayerHomeMap ?? Find.CurrentMap; } }
        private static Pawn Colonist(Map m) { return m.mapPawns.FreeColonistsSpawned.First(); }
        private static List<Quest> RouteQuests(QuestScriptDef d) { return Find.QuestManager.QuestsListForReading.Where(q => q.root == d).ToList(); }
        private static int Lords(Map m, Faction f) { return m.lordManager.lords.Count(l => l.faction == f); }
        private static int RaidersOn(Map m, Faction f) { return m.mapPawns.SpawnedPawnsInFaction(f).Count; }

        [DebugAction(Cat, "Probe reset", allowedGameStates = AllowedGameStates.Playing)]
        public static void Reset()
        {
            Guarded("reset", () =>
            {
                File.WriteAllText(FilePath, "");
                firstCast = null;      // statics outlive a run: a second proof in one game session must not compare against the last run's cast
                visits = 0;
                foreach (Quest q in Find.QuestManager.QuestsListForReading.Where(q => q.root == ArmorerDefOf.RM_Quest_ArmorerDebt || q.root == ArmorerDefOf.RM_Quest_ImperialPrisonBreak).ToList())
                    Find.QuestManager.Remove(q);
                SoftReset();
                BeskarArmorerSettings.ResetFields(new[] { "modEnabled", "routeOneEnabled", "routeTwoEnabled", "harmRaidEnabled", "tributeOneIn", "smeltSteelRatio", "prisonBreakEarliestDay", "prisonBreakRefireDays", "revealDelayMinDays", "revealDelayMaxDays" });
                Row("reset", true, "generated reforge recipes=" + ArmorerStartup.GeneratedRecipes);
            });
        }

        private static void SoftReset()
        {
            RM_ArmorerState s = RM_ArmorerState.Get;
            RM_ArmorerCovert c = RM_ArmorerState.Covert;
            if (c != null)
            {
                if (c.HasMap)
                {
                    foreach (Pawn col in c.Map.mapPawns.FreeColonistsSpawned.ToList())
                    {
                        col.DeSpawn();
                        GenSpawn.Spawn(col, CellFinder.StandableCellNear(Home.Center, Home, 15f), Home);
                    }
                    Current.Game.DeinitAndRemoveMap(c.Map, false);
                }
                c.Destroy();
            }
            foreach (Pawn raider in Home.mapPawns.SpawnedPawnsInFaction(Find.FactionManager.OfPirates).ToList()) raider.Destroy();
            s.revealed = false;
            s.lost = false;
            Current.Game.GetComponent<RM_HeatEvents>().events.Clear();
            Faction t = Find.FactionManager.FirstFactionOfDef(ArmorerDefOf.RM_TribeOfTheArmorer);
            if (t != null) t.SetRelationDirect(Faction.OfPlayer, FactionRelationKind.Neutral, false);
        }

        private static Pawn SpawnPrisoner(string kind)
        {
            Map m = Home;
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(DefDatabase<PawnKindDef>.GetNamed(kind), Find.FactionManager.OfPirates, forceGenerateNewPawn: true));
            GenSpawn.Spawn(p, CellFinder.StandableCellNear(Colonist(m).Position, m, 10f), m);
            p.guest.CapturedBy(Faction.OfPlayer, Colonist(m));
            return p;
        }

        // L4 ---------------------------------------------------------------------------------------------------------------
        [DebugAction(Cat, "Probe L4 route one", allowedGameStates = AllowedGameStates.Playing)]
        public static void L4()
        {
            Guarded("L4", () =>
            {
                int before = RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).Count;
                Pawn other = SpawnPrisoner("Mercenary_Gunner");
                GenGuest.PrisonerRelease(other);
                Row("L4.other_pawn_no_quest", RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).Count == before, "released " + other.kindDef.defName + " wasPrisoner=true");

                Pawn hunter = SpawnPrisoner("RUT_Jawa_Blackstar_Heavy");
                Row("L4.hunter_is_prisoner", hunter.IsPrisonerOfColony, hunter.kindDef.defName + " faction=" + hunter.Faction?.def.defName);
                GenGuest.PrisonerRelease(hunter);
                Quest q = RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).Skip(before).FirstOrDefault();
                Row("L4.quest_offered", q != null, q == null ? "no quest" : q.name + " state=" + q.State + " : " + q.description);
                Row("L4.no_covert_yet", RM_ArmorerState.Covert == null, "before the delay");
                if (q == null) return;
                QuestPart_Delay d = q.PartsListForReading.OfType<QuestPart_Delay>().First();
                Row("L4.delay_2_to_5_days", d.delayTicks >= 2 * 60000 && d.delayTicks <= 5 * 60000, "delayTicks=" + d.delayTicks);
                d.DebugForceEnd();
            });
        }

        [DebugAction(Cat, "Probe L4 read", allowedGameStates = AllowedGameStates.Playing)]
        public static void L4Read()
        {
            Guarded("L4.read", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Row("L4.covert_on_orbit", c != null && c.Tile.LayerDef == PlanetLayerDefOf.Orbit, c == null ? "no covert" : "tile " + c.Tile + " layer " + c.Tile.LayerDef?.defName);
                Quest q = RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).LastOrDefault();
                Row("L4.quest_success", q?.State == QuestState.EndedSuccess, "state=" + q?.State);
                Row("L4.three_pawns", c?.cast.Count == 3 && c.cast.All(Find.WorldPawns.Contains), "cast=" + string.Join(",", c?.cast.Select(p => p.LabelShort) ?? new string[0]));
                Row("L4.gravship_gate", c != null && c.GravShipCanLandOn && TileFinder.IsValidTileForNewSettlement(c.Tile, null, forGravship: true), "GravShipCanLandOn=" + c?.GravShipCanLandOn);
            });
        }

        // L5 / L7 --------------------------------------------------------------------------------------------------------
        private static List<int> firstCast;
        private static int visits;

        /// <summary>The gravship's own map path: GravshipUtility generates the destination with GetOrGenerateMap(tile, size, mapParent.def, ...).</summary>
        private static Map Visit(RM_ArmorerCovert c)
        {
            Map m = GetOrGenerateMapUtility.GetOrGenerateMap(c.Tile, c.def.overrideMapSize.Value, c.def);
            visits++;
            return m;
        }

        [DebugAction(Cat, "Probe visit by map path", allowedGameStates = AllowedGameStates.Playing)]
        public static void VisitStep()
        {
            Guarded("visit", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Map m = c.HasMap ? c.Map : Visit(c);
                if (m.mapPawns.FreeColonistsSpawnedCount == 0) MoveColonist(Home, m);
                Row("visit.map", m != null && m.listerThings.ThingsOfDef(ArmorerDefOf.RM_ArmorerForge).Count == 1, "forge count=" + m?.listerThings.ThingsOfDef(ArmorerDefOf.RM_ArmorerForge).Count);
                ReadCast(c, m);
            });
        }

        private static void MoveColonist(Map from, Map to)
        {
            Pawn col = Colonist(from);
            col.DeSpawn();
            GenSpawn.Spawn(col, CellFinder.StandableCellNear(to.Center, to, 15f), to);
        }

        private static void ReadCast(RM_ArmorerCovert c, Map m)
        {
            List<int> ids = c.cast.Select(p => p.thingIDNumber).OrderBy(i => i).ToList();
            if (firstCast == null) firstCast = ids;
            Row("cast.same_three", ids.SequenceEqual(firstCast) && c.cast.Count(p => p.Spawned && p.Map == m) == 3, "ids " + string.Join(",", ids) + " spawned=" + c.cast.Count(p => p.Spawned) + " visit=" + visits);
        }

        [DebugAction(Cat, "Probe cast read", allowedGameStates = AllowedGameStates.Playing)]
        public static void CastRead() { Guarded("cast", () => { RM_ArmorerCovert c = RM_ArmorerState.Covert; ReadCast(c, c.Map); }); }

        [DebugAction(Cat, "Probe leave", allowedGameStates = AllowedGameStates.Playing)]
        public static void Leave()
        {
            Guarded("leave", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                MoveColonist(c.Map, Home);
                bool stay = c.ShouldRemoveMapNow(out bool also);
                Row("leave.map_removable_object_stays", stay && !also, "remove=" + stay + " alsoObject=" + also);
                c.Abandon(wasGravshipLaunch: true);
                Row("leave.object_survives", RM_ArmorerState.Covert == c && !c.HasMap, "hasMap=" + c.HasMap);
            });
        }

        private static readonly float[] savedWork = new float[2];
        private static Bill_Production meltBill, reforgeBill;
        private static int meltMass;

        [DebugAction(Cat, "Probe L5 forge setup", allowedGameStates = AllowedGameStates.Playing)]
        public static void L5Setup()
        {
            Guarded("L5.setup", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Map m = c.Map;
                Building_WorkTable forge = (Building_WorkTable)m.listerThings.ThingsOfDef(ArmorerDefOf.RM_ArmorerForge).First();
                ThingDef helmet = DefDatabase<ThingDef>.GetNamed("guy762_MandoHelmet_supercom");
                RecipeDef reforge = DefDatabase<RecipeDef>.GetNamed("RM_Reforge_guy762_MandoHelmet_supercom");
                Row("L5.recipes_listed", forge.def.AllRecipes.Contains(reforge) && forge.def.AllRecipes.Contains(ArmorerDefOf.RM_Recipe_ArmorerMeltBeskar), "forge recipes=" + forge.def.AllRecipes.Count);
                // two pieces to melt, 1 in 5 kept
                Thing a = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("guy762_MandoArmor_supercom"));
                Thing b = ThingMaker.MakeThing(helmet);
                a.HitPoints = a.MaxHitPoints / 2;                    // full mass regardless of hit points
                meltMass = BeskarUtil.Mass(a) + BeskarUtil.Mass(b);
                IntVec3 at = forge.InteractionCell;
                GenPlace.TryPlaceThing(a, at, m, ThingPlaceMode.Near);
                GenPlace.TryPlaceThing(b, at, m, ThingPlaceMode.Near);
                savedWork[0] = ArmorerDefOf.RM_Recipe_ArmorerMeltBeskar.workAmount;
                savedWork[1] = reforge.workAmount;
                ArmorerDefOf.RM_Recipe_ArmorerMeltBeskar.workAmount = 60f;
                reforge.workAmount = 60f;
                meltBill = (Bill_Production)ArmorerDefOf.RM_Recipe_ArmorerMeltBeskar.MakeNewBill();
                meltBill.repeatMode = BillRepeatModeDefOf.RepeatCount;
                meltBill.repeatCount = 2;
                reforgeBill = (Bill_Production)reforge.MakeNewBill();
                forge.BillStack.AddBill(meltBill);
                forge.BillStack.AddBill(reforgeBill);
                Row("L5.melt_mass_read", meltMass > 0, "mass=" + meltMass + " expect ingots from melt=" + (meltMass * 4 / 5));
                Pawn colonist = Home.mapPawns.FreeColonists.First();
                Row("L5.colonist_refused_melt", !meltBill.PawnAllowedToStartAnew(colonist), colonist.LabelShort);
                Row("L5.colonist_refused_reforge", !reforgeBill.PawnAllowedToStartAnew(colonist), colonist.LabelShort);
                Row("L5.armorer_allowed", meltBill.PawnAllowedToStartAnew(c.Armorer) && reforgeBill.PawnAllowedToStartAnew(c.Armorer), c.Armorer.LabelShort);
            });
        }

        [DebugAction(Cat, "Probe L5 status", allowedGameStates = AllowedGameStates.Playing)]
        public static void L5Status()
        {
            Guarded("L5.status", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Pawn her = c.Armorer;
                Row("L5.status", true, "tick=" + Find.TickManager.TicksGame + " job=" + her.CurJobDef?.defName + " recipe=" + her.CurJob?.bill?.recipe?.defName + " toil=" + her.jobs.curDriver?.CurToilString
                    + " carried=" + her.carryTracker.CarriedThing + " at=" + her.Position + " meltLeft=" + meltBill.repeatCount + " reforgeLeft=" + reforgeBill.repeatCount
                    + " ingots=" + string.Join(",", c.Map.listerThings.ThingsOfDef(ArmorerDefOf.KOTOR_IngotBeskar).Select(t => t.stackCount + "@" + t.Position)));
            });
        }

        [DebugAction(Cat, "Probe L5 read", allowedGameStates = AllowedGameStates.Playing)]
        public static void L5Read()
        {
            Guarded("L5.read", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Map m = c.Map;
                int ingots = m.listerThings.ThingsOfDef(ArmorerDefOf.KOTOR_IngotBeskar).Sum(t => t.stackCount);
                Thing product = m.listerThings.ThingsOfDef(DefDatabase<ThingDef>.GetNamed("guy762_MandoHelmet_supercom")).FirstOrDefault();
                int helmetCost = DefDatabase<RecipeDef>.GetNamed("RM_Reforge_guy762_MandoHelmet_supercom").ingredients[0].CountRequiredOfFor(ArmorerDefOf.KOTOR_IngotBeskar, DefDatabase<RecipeDef>.GetNamed("RM_Reforge_guy762_MandoHelmet_supercom"));
                bool melted = meltBill.repeatCount == 0 || m.listerThings.ThingsOfDef(DefDatabase<ThingDef>.GetNamed("guy762_MandoArmor_supercom")).Count == 0;
                bool made = reforgeBill.DeletedOrDereferenced || reforgeBill.repeatCount == 0 || (product != null && product.HitPoints == product.MaxHitPoints);
                Row("L5.melted_4_in_5", melted && (ingots == meltMass * 4 / 5 || ingots == meltMass * 4 / 5 - helmetCost), "mass=" + meltMass + " ingots now=" + ingots + " helmetCost=" + helmetCost + " remainder=" + c.meltRemainder);
                Thing forgeT = m.listerThings.ThingsOfDef(ArmorerDefOf.RM_ArmorerForge).First();
                Pawn her = c.Armorer;
                JobFailReason.Clear();
                Job try_ = (ArmorerDefOf.RM_DoBillsArmorerForge.Worker as WorkGiver_DoBill)?.JobOnThing(her, forgeT, forced: true);
                Row("L5.reforged", made && product != null, "product=" + product?.LabelCap + " billLeft=" + reforgeBill.repeatCount + " herJob=" + her.CurJobDef?.defName + " meltLeft=" + meltBill.repeatCount
                    + " stackBills=" + ((Building_WorkTable)forgeT).BillStack.Count + " wouldStart=" + try_?.bill?.recipe?.defName + " why=" + JobFailReason.Reason + " shouldDo=" + reforgeBill.ShouldDoNow() + " spawned=" + her.Spawned + " downed=" + her.Downed + " lord=" + her.GetLord()?.CurLordToil);
                ArmorerDefOf.RM_Recipe_ArmorerMeltBeskar.workAmount = savedWork[0];
                DefDatabase<RecipeDef>.GetNamed("RM_Reforge_guy762_MandoHelmet_supercom").workAmount = savedWork[1];
            });
        }

        // L6 ---------------------------------------------------------------------------------------------------------------
        [DebugAction(Cat, "Probe L6 colony benches", allowedGameStates = AllowedGameStates.Playing)]
        public static void L6()
        {
            Guarded("L6", () =>
            {
                List<string> beskarGear = DefDatabase<ThingDef>.AllDefsListForReading.Where(d => d.category == ThingCategory.Item && !BeskarUtil.IsMaterial(d) && BeskarUtil.DefCarries(d)).Select(d => d.defName).ToList();
                List<string> colonyRecipes = DefDatabase<RecipeDef>.AllDefsListForReading
                    .Where(r => r.products != null && r.products.Any(p => beskarGear.Contains(p.thingDef.defName)) && !r.defName.StartsWith("RM_Reforge_")).Select(r => r.defName).ToList();
                Row("L6.mando_recipes_gone", beskarGear.Count > 0 && colonyRecipes.Count == 0, "beskar gear " + string.Join(",", beskarGear) + "; colony recipes left: " + string.Join(",", colonyRecipes));
                Map m = Home;
                Thing ingot = ThingMaker.MakeThing(ArmorerDefOf.KOTOR_IngotBeskar);
                Thing steel = ThingMaker.MakeThing(ThingDefOf.Steel);
                Thing mando = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("guy762_MandoArmor_supercom"));
                Building_WorkTable smithy = (Building_WorkTable)GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("FueledSmithy")), CellFinder.StandableCellNear(m.Center, m, 30f), m);
                Bill_Production make = (Bill_Production)DefDatabase<RecipeDef>.GetNamed("Make_MeleeWeapon_Gladius").MakeNewBill();
                smithy.BillStack.AddBill(make);
                Row("L6.stuff_bill_refuses_beskar", !make.IsFixedOrAllowedIngredient(ingot) && !make.IsFixedOrAllowedIngredient(ingot.def), "gladius bill, thing=" + make.IsFixedOrAllowedIngredient(ingot) + " def=" + make.IsFixedOrAllowedIngredient(ingot.def));
                Row("L6.stuff_bill_takes_steel", make.IsFixedOrAllowedIngredient(steel), "sanity: the gate is not a blanket no");
                ThingDef smelterDef = DefDatabase<ThingDef>.GetNamed("ElectricSmelter");
                Building_WorkTable smelter = (Building_WorkTable)GenSpawn.Spawn(ThingMaker.MakeThing(smelterDef), CellFinder.StandableCellNear(m.Center, m, 30f), m);
                Bill_Production smelt = (Bill_Production)DefDatabase<RecipeDef>.GetNamed("SmeltApparel").MakeNewBill();
                smelter.BillStack.AddBill(smelt);
                Row("L6.smelter_bill_takes_beskar_gear", smelt.IsFixedOrAllowedIngredient(mando), "SmeltApparel");
                Row("L6.gear_smeltable", mando.Smeltable, "Thing.Smeltable=" + mando.Smeltable);
                List<Thing> got = mando.SmeltProducts(1f).ToList();
                int mass = BeskarUtil.Mass(mando);
                int st = got.Where(t => t.def == ThingDefOf.Steel).Sum(t => t.stackCount);
                int slag = got.Count(t => t.def == ThingDefOf.ChunkSlagSteel);
                Row("L6.smelt_steel_slag", mass > 0 && st >= (mass + 2) / 3 && slag == 1 && !got.Any(t => BeskarUtil.IsMaterial(t.def)),
                    "mass=" + mass + " products=" + string.Join(",", got.Select(t => t.def.defName + "x" + t.stackCount)));
                smithy.Destroy();
                smelter.Destroy();
            });
        }

        // The real ship: the vanilla confirmed-launch closure, as jawa/gravship_launch runs it, which only takes a surface tile. A
        // GravAnchor stays behind so the colony map outlives the launch. Landing is confirmed by jawa/gravship_land.
        [DebugAction(Cat, "Probe gravship build", allowedGameStates = AllowedGameStates.Playing)]
        public static void ShipBuild()
        {
            Guarded("gravship.build", () =>
            {
                SoftReset();
                RM_ArmorerState.Get.Reveal(out string _);
                firstCast = null;
                Map m = Home;
                CellRect rect = CellRect.CenteredOn(m.Center, 5);
                foreach (IntVec3 c in rect)
                {
                    foreach (Thing t in c.GetThingList(m).ToList()) if (!(t is Pawn)) t.Destroy();
                    m.roofGrid.SetRoof(c, null);
                    m.terrainGrid.SetTerrain(c, TerrainDefOf.Soil);
                    m.terrainGrid.SetFoundation(c, TerrainDefOf.Substructure);
                }
                Thing engine = GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("GravEngine")), m.Center, m, Rot4.North);
                engine.SetFaction(Faction.OfPlayer);
                Thing console = GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("PilotConsole")), m.Center + new IntVec3(3, 0, 3), m, Rot4.North);
                console.SetFaction(Faction.OfPlayer);
                Thing anchor = GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.GravAnchor), m.Center + new IntVec3(9, 0, 9), m, Rot4.North);
                anchor.SetFaction(Faction.OfPlayer);
                Pawn col = Colonist(m);
                col.Position = m.Center + new IntVec3(-3, 0, -3);
                col.Notify_Teleported();
                Row("gravship.built", engine is Building_GravEngine g && g.ValidSubstructure.Count > 0, "substructure cells=" + (engine as Building_GravEngine)?.ValidSubstructure.Count);
            });
        }

        private static void Launch(PlanetTile target)
        {
            Building_GravEngine engine = Find.Maps.SelectMany(m => m.listerThings.AllThings.OfType<Building_GravEngine>()).First();
            engine.launchInfo = new LaunchInfo { quality = 1f, doNegativeOutcome = false };
            Find.World.renderer.wantedMode = WorldRenderMode.None;
            Find.GravshipController.InitiateTakeoff(engine, target);
        }

        [DebugAction(Cat, "Probe gravship launch out", allowedGameStates = AllowedGameStates.Playing)]
        public static void ShipOut()
        {
            Guarded("gravship.out", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Row("gravship.gate_open", c.GravShipCanLandOn && TileFinder.IsValidTileForNewSettlement(c.Tile, null, forGravship: true), "tile " + c.Tile);
                Launch(c.Tile);
            });
        }

        [DebugAction(Cat, "Probe gravship launch home", allowedGameStates = AllowedGameStates.Playing)]
        public static void ShipHome()
        {
            Guarded("gravship.home", () => Launch(Home.Tile));
        }

        // Vanilla arrival on a map that already exists leaves the marker unspawned until the player picks a spot with the designator.
        [DebugAction(Cat, "Probe gravship pick spot", allowedGameStates = AllowedGameStates.Playing)]
        public static void ShipPickSpot()
        {
            Guarded("gravship.pick", () =>
            {
                WorldComponent_GravshipController ctrl = Find.GravshipController;
                if (Find.Maps.Any(m => m.listerThings.AllThings.OfType<GravshipLandingMarker>().Any())) return;
                Designator_MoveGravship d = ctrl.MoveDesignator();
                IntVec3 spot = GenRadial.RadialCellsAround(ctrl.landingMap.Center, 45f, true).FirstOrDefault(x => d.CanDesignateCell(x).Accepted);
                Row("gravship.spot", spot.IsValid && spot != IntVec3.Zero, "spot=" + spot);
                d.DesignateSingleCell(spot);
            });
        }

        [DebugAction(Cat, "Probe gravship read covert", allowedGameStates = AllowedGameStates.Playing)]
        public static void ShipReadCovert()
        {
            Guarded("gravship.read", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Map m = c.HasMap ? c.Map : null;
                bool ship = m != null && m.listerThings.AllThings.OfType<Building_GravEngine>().Any();
                Row("gravship.landed", ship && m.mapPawns.FreeColonistsSpawnedCount > 0 && m.listerThings.ThingsOfDef(ArmorerDefOf.RM_ArmorerForge).Count == 1,
                    "hasMap=" + (m != null) + " engineThere=" + ship + " colonists=" + m?.mapPawns.FreeColonistsSpawnedCount);
                if (m != null) ReadCast(c, m);
            });
        }

        [DebugAction(Cat, "Probe gravship read home", allowedGameStates = AllowedGameStates.Playing)]
        public static void ShipReadHome()
        {
            Guarded("gravship.readhome", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Row("gravship.back_home", Home.listerThings.AllThings.OfType<Building_GravEngine>().Any(), "engine on home map");
                Row("gravship.map_discarded_object_stays", c != null && !c.HasMap, "hasMap=" + c?.HasMap);
            });
        }

        // L8 ---------------------------------------------------------------------------------------------------------------
        [DebugAction(Cat, "Probe L8 fresh covert", allowedGameStates = AllowedGameStates.Playing)]
        public static void L8Fresh()
        {
            Guarded("L8.fresh", () =>
            {
                firstCast = null;
                SoftReset();
                RM_ArmorerCovert c = RM_ArmorerState.Get.Reveal(out string refused);
                Row("L8.fresh", c != null, refused ?? "ok");
                Map m = Visit(c);
                Pawn col = Colonist(Home);
                col.DeSpawn();
                GenSpawn.Spawn(col, CellFinder.StandableCellNear(m.Center, m, 15f), m);
            });
        }

        private static void HarmChecks(string how, RM_ArmorerCovert c, int raidersBefore, bool expectRaid)
        {
            Faction pirate = Find.FactionManager.OfPirates;
            Row("L8." + how + ".lost", c.lost && RM_ArmorerState.Get.lost, "covert.lost=" + c.lost);
            HeatEvent h = Current.Game.GetComponent<RM_HeatEvents>().events.LastOrDefault();
            Row("L8." + how + ".heat_max", h != null && h.faction == pirate.def.defName && h.amount == RM_HeatEvents.Max, h == null ? "no heat" : h.faction + " " + h.amount + " " + h.source);
            int raiders = RaidersOn(Home, pirate);
            Row("L8." + how + ".raid", (raiders > raidersBefore) == expectRaid, "raiders " + raidersBefore + " -> " + raiders);
        }

        [DebugAction(Cat, "Probe L8 harm guard", allowedGameStates = AllowedGameStates.Playing)]
        public static void L8Guard()
        {
            Guarded("L8.guard", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Pawn guard = c.cast.First(p => p != c.Armorer);
                int before = RaidersOn(Home, Find.FactionManager.OfPirates);
                Row("L8.neutral_until_harm", !c.Faction.HostileTo(Faction.OfPlayer), "before");
                guard.TakeDamage(new DamageInfo(DamageDefOf.Blunt, 3f, instigator: Colonist(c.Map)));
                HarmChecks("guard", c, before, true);
                Row("L8.hostile_after", c.Faction.HostileTo(Faction.OfPlayer), "tribe hostile");
                Row("L8.object_stays_during_visit", RM_ArmorerState.Covert == c, "not yanked mid-fight");
                Pawn col = Colonist(c.Map);
                col.DeSpawn();
                GenSpawn.Spawn(col, CellFinder.StandableCellNear(Home.Center, Home, 15f), Home);
                bool remove = c.ShouldRemoveMapNow(out bool also);
                Row("L8.gone_on_departure", remove && also, "remove=" + remove + " alsoObject=" + also);
                c.Notify_MyMapAboutToBeRemoved();
                Current.Game.DeinitAndRemoveMap(c.Map, false);
                c.Destroy();
                Row("L8.reveal_refused_after_loss", RM_ArmorerState.Get.Reveal(out string why) == null && why == "covert lost", why);
                int debt = RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).Count;
                Pawn hunter = SpawnPrisoner("RUT_Jawa_Blackstar_Heavy");
                GenGuest.PrisonerRelease(hunter);
                Row("L8.route1_refused_after_loss", RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).Count == debt, "no quest");
                BeskarArmorerSettings.prisonBreakEarliestDay = 0;
                IncidentParms parms = new IncidentParms { target = Find.World };
                Row("L8.route2_refused_after_loss", !ArmorerDefOf.RM_BlackstarPrisonBreakOffer.Worker.CanFireNow(parms), "CanFireNow false");
                BeskarArmorerSettings.prisonBreakEarliestDay = 30;
            });
        }

        [DebugAction(Cat, "Probe L8 harm building", allowedGameStates = AllowedGameStates.Playing)]
        public static void L8Building()
        {
            Guarded("L8.building", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                Building wall = c.Map.listerBuildings.allBuildingsNonColonist.First(b => b.def.defName == "Wall");
                int before = RaidersOn(Home, Find.FactionManager.OfPirates);
                wall.TakeDamage(new DamageInfo(DamageDefOf.Blunt, 3f, instigator: Colonist(c.Map)));
                HarmChecks("building", c, before, true);
            });
        }

        [DebugAction(Cat, "Probe L8 harm capture", allowedGameStates = AllowedGameStates.Playing)]
        public static void L8Capture()
        {
            Guarded("L8.capture", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                int before = RaidersOn(Home, Find.FactionManager.OfPirates);
                c.cast.First(p => p != c.Armorer).guest.CapturedBy(Faction.OfPlayer, Colonist(c.Map));
                HarmChecks("capture", c, before, true);
            });
        }

        [DebugAction(Cat, "Probe L8 harm killed", allowedGameStates = AllowedGameStates.Playing)]
        public static void L8Kill()
        {
            Guarded("L8.kill", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                int before = RaidersOn(Home, Find.FactionManager.OfPirates);
                c.Armorer.Kill(null);
                HarmChecks("kill", c, before, true);
            });
        }

        [DebugAction(Cat, "Probe L8 harm forge", allowedGameStates = AllowedGameStates.Playing)]
        public static void L8Forge()
        {
            Guarded("L8.forge", () =>
            {
                RM_ArmorerCovert c = RM_ArmorerState.Covert;
                int before = RaidersOn(Home, Find.FactionManager.OfPirates);
                c.Map.listerThings.ThingsOfDef(ArmorerDefOf.RM_ArmorerForge).First().TakeDamage(new DamageInfo(DamageDefOf.Blunt, 3f, instigator: Colonist(c.Map)));
                HarmChecks("forge", c, before, true);
            });
        }

        // L9 ---------------------------------------------------------------------------------------------------------------
        private static Quest breakQuest;
        private static Site BreakSite(Quest q) { return q.PartsListForReading.OfType<RM_QuestPart_Breakout>().First().site; }
        private static Pawn Detainee(Quest q) { return q.PartsListForReading.OfType<RM_QuestPart_Breakout>().First().detainee; }

        [DebugAction(Cat, "Probe L9 offer", allowedGameStates = AllowedGameStates.Playing)]
        public static void L9Offer()
        {
            Guarded("L9.offer", () =>
            {
                SoftReset();
                foreach (Quest old in RouteQuests(ArmorerDefOf.RM_Quest_ImperialPrisonBreak).Concat(RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt)).ToList()) Find.QuestManager.Remove(old);
                IncidentWorker w = ArmorerDefOf.RM_BlackstarPrisonBreakOffer.Worker;
                IncidentParms parms = new IncidentParms { target = Find.World, points = 500f };
                Row("L9.not_before_day_30", !ArmorerKernel.RouteTwoOffers(true, 29.9f, BeskarArmorerSettings.prisonBreakEarliestDay, false, false, false) && !(GenDate.DaysPassedSinceSettleFloat < 30f && w.CanFireNow(parms)), "day " + GenDate.DaysPassedSinceSettleFloat + " earliest " + BeskarArmorerSettings.prisonBreakEarliestDay);
                BeskarArmorerSettings.prisonBreakEarliestDay = 0;
                RM_ArmorerState s = RM_ArmorerState.Get;
                s.revealed = true;
                Row("L9.not_while_revealed", !w.CanFireNow(parms), "revealed");
                s.revealed = false; s.lost = true;
                Row("L9.not_while_lost", !w.CanFireNow(parms), "lost");
                s.lost = false;
                bool fired = w.TryExecute(parms);
                breakQuest = RouteQuests(ArmorerDefOf.RM_Quest_ImperialPrisonBreak).LastOrDefault();
                Row("L9.offered", fired && breakQuest != null, breakQuest == null ? "no quest" : breakQuest.name + " : " + breakQuest.description);
                BeskarArmorerSettings.prisonBreakEarliestDay = 30;
                if (breakQuest == null) return;
                breakQuest.Accept(null);
                Site site = BreakSite(breakQuest);
                Row("L9.site_is_empire", site != null && site.Faction == Faction.OfEmpire && site.parts.Any(p => p.def == ArmorerDefOf.RM_ImperialDetentionPost), "site " + site?.Label + " faction " + site?.Faction?.def.defName);
                Map m = GetOrGenerateMapUtility.GetOrGenerateMap(site.Tile, Find.World.info.initialMapSize, site.def);
                Row("L9.map_made", m != null, "map " + m?.uniqueID);
            });
        }

        [DebugAction(Cat, "Probe L9 breakout", allowedGameStates = AllowedGameStates.Playing)]
        public static void L9Breakout()
        {
            Guarded("L9.breakout", () =>
            {
                Pawn d = Detainee(breakQuest);
                Row("L9.detainee_with_you", d != null && d.Spawned && d.Faction == Faction.OfPlayer && !d.IsPrisoner, d?.LabelShort + " faction=" + d?.Faction?.def.defName);
                Row("L9.no_heat_yet", Current.Game.GetComponent<RM_HeatEvents>().events.Count == 0, "before he is out");
                Map site = d.Map;
                Row("L9.plate_in_locker", site.listerThings.AllThings.Any(t => BeskarUtil.Carries(t) && t.def.IsApparel), "evidence locker");
                d.ExitMap(false, Rot4.North);
            });
        }

        [DebugAction(Cat, "Probe L9 out read", allowedGameStates = AllowedGameStates.Playing)]
        public static void L9OutRead()
        {
            Guarded("L9.out", () =>
            {
                HeatEvent h = Current.Game.GetComponent<RM_HeatEvents>().events.LastOrDefault();
                Row("L9.large_heat", h != null && h.faction == Faction.OfEmpire.def.defName && h.amount == RM_HeatEvents.Large, h == null ? "no heat" : h.faction + " " + h.amount);
                QuestPart_Delay delay = breakQuest.PartsListForReading.OfType<QuestPart_Delay>().FirstOrDefault(p => p.GetType() == typeof(QuestPart_Delay));
                Row("L9.pursuit_delay_running", delay != null && delay.State == QuestPartState.Enabled, "state=" + delay?.State + " ticks=" + delay?.delayTicks);
                lastEmpire = RaidersOn(Home, Faction.OfEmpire);
                delay?.DebugForceEnd();
            });
        }

        private static int lastEmpire;

        [DebugAction(Cat, "Probe L9 done read", allowedGameStates = AllowedGameStates.Playing)]
        public static void L9DoneRead()
        {
            Guarded("L9.done", () =>
            {
                int now = RaidersOn(Home, Faction.OfEmpire);
                Row("L9.pursuit_raid", now > lastEmpire, "empire pawns " + lastEmpire + " -> " + now);
                Row("L9.covert_revealed", RM_ArmorerState.Covert != null, "covert " + RM_ArmorerState.Covert?.Tile);
                Row("L9.quest_success", breakQuest.State == QuestState.EndedSuccess, "state=" + breakQuest.State);
                Pawn d = Detainee(breakQuest);
                Row("L9.he_went_home", d.Faction == Find.FactionManager.OfPirates && !d.Spawned, "faction " + d.Faction?.def.defName);
                foreach (Pawn raider in Home.mapPawns.SpawnedPawnsInFaction(Faction.OfEmpire).ToList()) raider.Destroy();
                Site site = BreakSite(breakQuest);
                if (site != null && site.HasMap) Current.Game.DeinitAndRemoveMap(site.Map, false);
            });
        }

        [DebugAction(Cat, "Probe L9 failure paths", allowedGameStates = AllowedGameStates.Playing)]
        public static void L9Fail()
        {
            Guarded("L9.fail", () =>
            {
                SoftReset();
                foreach (Quest old in RouteQuests(ArmorerDefOf.RM_Quest_ImperialPrisonBreak).ToList()) Find.QuestManager.Remove(old);
                BeskarArmorerSettings.prisonBreakEarliestDay = 0;
                IncidentParms parms = new IncidentParms { target = Find.World, points = 500f };
                ArmorerDefOf.RM_BlackstarPrisonBreakOffer.Worker.TryExecute(parms);
                breakQuest = RouteQuests(ArmorerDefOf.RM_Quest_ImperialPrisonBreak).Last();
                breakQuest.Accept(null);
                Site s = BreakSite(breakQuest);
                GetOrGenerateMapUtility.GetOrGenerateMap(s.Tile, Find.World.info.initialMapSize, s.def);
                Detainee(breakQuest).Kill(null);
            });
        }

        [DebugAction(Cat, "Probe L9 death read", allowedGameStates = AllowedGameStates.Playing)]
        public static void L9DeathRead()
        {
            Guarded("L9.death", () =>
            {
                Row("L9.death_fails", breakQuest.State == QuestState.EndedFailed, "state=" + breakQuest.State);
                Row("L9.death_no_covert", RM_ArmorerState.Covert == null, "no reveal");
                Site site = BreakSite(breakQuest);
                if (site != null && site.HasMap) Current.Game.DeinitAndRemoveMap(site.Map, false);
                foreach (Quest old in RouteQuests(ArmorerDefOf.RM_Quest_ImperialPrisonBreak).ToList()) Find.QuestManager.Remove(old);
                ArmorerDefOf.RM_BlackstarPrisonBreakOffer.Worker.TryExecute(new IncidentParms { target = Find.World, points = 500f });
                breakQuest = RouteQuests(ArmorerDefOf.RM_Quest_ImperialPrisonBreak).Last();
                breakQuest.Accept(null);
                QuestPart_WorldObjectTimeout t = breakQuest.PartsListForReading.OfType<QuestPart_WorldObjectTimeout>().FirstOrDefault();
                Row("L9.timeout_armed", t != null && t.State == QuestPartState.Enabled && t.delayTicks >= 10 * 60000, "delayTicks=" + t?.delayTicks + " state=" + t?.State);
                t.DebugForceEnd();
            });
        }

        [DebugAction(Cat, "Probe L9 timeout read", allowedGameStates = AllowedGameStates.Playing)]
        public static void L9TimeoutRead()
        {
            Guarded("L9.timeout", () =>
            {
                Row("L9.timeout_fails", breakQuest.State == QuestState.EndedFailed, "state=" + breakQuest.State);
                BeskarArmorerSettings.prisonBreakEarliestDay = 30;
            });
        }

        // L10 --------------------------------------------------------------------------------------------------------------
        [DebugAction(Cat, "Probe L10 toggles", allowedGameStates = AllowedGameStates.Playing)]
        public static void L10()
        {
            Guarded("L10", () =>
            {
                SoftReset();
                foreach (Quest old in RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).Concat(RouteQuests(ArmorerDefOf.RM_Quest_ImperialPrisonBreak)).ToList()) Find.QuestManager.Remove(old);
                BeskarArmorerSettings.routeOneEnabled = false;
                Pawn h1 = SpawnPrisoner("RUT_Jawa_Blackstar_Heavy");
                GenGuest.PrisonerRelease(h1);
                Row("L10.route1_off", RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).Count == 0, "no quest");
                BeskarArmorerSettings.routeOneEnabled = true;

                BeskarArmorerSettings.prisonBreakEarliestDay = 0;
                BeskarArmorerSettings.routeTwoEnabled = false;
                IncidentParms parms = new IncidentParms { target = Find.World, points = 500f };
                Row("L10.route2_off", !ArmorerDefOf.RM_BlackstarPrisonBreakOffer.Worker.CanFireNow(parms), "CanFireNow false");
                BeskarArmorerSettings.routeTwoEnabled = true;
                BeskarArmorerSettings.prisonBreakEarliestDay = 30;

                BeskarArmorerSettings.harmRaidEnabled = false;
                RM_ArmorerCovert c = RM_ArmorerState.Get.Reveal(out string _);
                Faction pirate = Find.FactionManager.OfPirates;
                int before = RaidersOn(Home, pirate);
                c.cast[1].TakeDamage(new DamageInfo(DamageDefOf.Blunt, 3f, instigator: Colonist(Home)));
                Row("L10.harm_raid_off", RaidersOn(Home, pirate) == before && RM_ArmorerState.Get.lost, "lost, raiders " + before + " -> " + RaidersOn(Home, pirate));
                BeskarArmorerSettings.harmRaidEnabled = true;
                SoftReset();

                Thing mando = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("guy762_MandoArmor_supercom"));
                Thing stuffed = ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("MeleeWeapon_Gladius"), ArmorerDefOf.KOTOR_IngotBeskar);
                string on = string.Join(",", stuffed.SmeltProducts(1f).Select(t => t.def.defName + "x" + t.stackCount));
                BeskarArmorerSettings.modEnabled = false;
                Bill_Production make = (Bill_Production)DefDatabase<RecipeDef>.GetNamed("Make_MeleeWeapon_Gladius").MakeNewBill();
                Row("L10.mod_off_no_gate", make.IsFixedOrAllowedIngredient(ArmorerDefOf.KOTOR_IngotBeskar), "gladius bill takes beskar again");
                string off = string.Join(",", stuffed.SmeltProducts(1f).Select(t => t.def.defName + "x" + t.stackCount));
                Pawn h2 = SpawnPrisoner("RUT_Jawa_Blackstar_Heavy");
                GenGuest.PrisonerRelease(h2);
                Row("L10.mod_off_no_quest", RouteQuests(ArmorerDefOf.RM_Quest_ArmorerDebt).Count == 0, "no quest");
                Row("L10.mod_off_smelt_is_not_ours", on != off, "on=" + on + " off=" + off);
                BeskarArmorerSettings.modEnabled = true;
            });
        }
    }
}
