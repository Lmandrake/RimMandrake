using System.Collections.Generic;
using System.Linq;
using System.Text;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// THE ARCHITECTURE GATE, as a harness.
    ///
    /// Caravan is designed to be TRANSIENT and this design uses its shape for
    /// something PERMANENT. Pawns held in a ThingOwner off-map are not ticked --
    /// which is exactly what "frozen until visited" wants -- but vanilla never
    /// stress-tests that across years, and everything else in RimMandrake.Inhabited rests on
    /// it holding.
    ///
    /// This file only MEASURES. It fixes nothing and it must not start to: if a
    /// roster does not survive intact, the container choice is wrong and the
    /// design gets re-specified before anything more is built on it.
    ///
    /// THE SOAK, which is not something this file can run:
    ///   1. Stuff a roster       (RimMandrake.Inhabited: stuff roster)
    ///   2. Report                (RimMandrake.Inhabited: report roster)  -- keep the output
    ///   3. Save, QUIT TO DESKTOP, reload
    ///   4. Let 100+ in-game days pass WITHOUT visiting the tile
    ///   5. Report again and diff
    ///
    /// PASS  = identical ThingIDs, names, relation counts and hediff counts.
    /// AGE   = either frozen (0 days advanced) or ticked (exactly the elapsed
    ///         time). BOTH ARE ACCEPTABLE, but WHICH ONE MUST BE REPORTED --
    ///         the design promises frozen, and a ticking roster changes it.
    /// FAIL  = any pawn missing, any relation dropped, or any
    ///         "Could not load reference to" in Player.log naming a pawn.
    /// </summary>
    public static class DebugActions_Inhabited
    {
        private const string Cat = "RimMandrake.Inhabited";

        [DebugAction(Cat, "Create place at current tile", allowedGameStates = AllowedGameStates.Playing)]
        private static void CreatePlaceHere()
        {
            PlanetTile tile = CurrentTile();
            if (!tile.Valid)
            {
                Log.Warning("[RimMandrake.Inhabited] no current tile: open a map or select a world tile.");
                return;
            }
            if (Find.WorldObjects.AnyWorldObjectAt<WorldObject_Inhabited>(tile))
            {
                Log.Message("[RimMandrake.Inhabited] a place already exists at tile " + tile + ".");
                return;
            }
            WorldObjectDef def = DefDatabase<WorldObjectDef>.GetNamedSilentFail("Inhabited_Place");
            if (def == null)
            {
                Log.Error("[RimMandrake.Inhabited] WorldObjectDef Inhabited_Place did not load.");
                return;
            }
            WorldObject_Inhabited place = (WorldObject_Inhabited)WorldObjectMaker.MakeWorldObject(def);
            place.Tile = tile;
            place.SetFaction(Find.FactionManager.RandomNonHostileFaction(allowNonHumanlike: false));
            place.Name = "Test place";

            // INHABITED_STOCK_ONTO_MAP_AND_FATE_1: a place with no archetype has
            // no larder and no fate, so every stock and fate action below would
            // silently do nothing on it. The first authored archetype is the
            // sensible default; the picker action can change it.
            place.placeDef = DefDatabase<InhabitedPlaceDef>.AllDefsListForReading.FirstOrDefault();

            Find.WorldObjects.Add(place);
            Log.Message("[RimMandrake.Inhabited] created " + place.LabelCap + " at tile " + tile
                        + " for " + (place.Faction?.Name ?? "no faction")
                        + ", archetype " + (place.placeDef?.defName ?? "NONE (no InhabitedPlaceDef loaded)") + ".");
        }

        [DebugAction(Cat, "Set place archetype", allowedGameStates = AllowedGameStates.Playing)]
        private static void SetPlaceDef()
        {
            WorldObject_Inhabited place = FindPlace();
            if (place == null)
            {
                return;
            }
            List<InhabitedPlaceDef> all = DefDatabase<InhabitedPlaceDef>.AllDefsListForReading.ToList();
            if (all.Count == 0)
            {
                Log.Error("[RimMandrake.Inhabited] no InhabitedPlaceDefs loaded.");
                return;
            }
            Dialog_DebugOptionListLister.ShowSimpleDebugMenu(all, d => d.defName,
                delegate (InhabitedPlaceDef d)
                {
                    // Evacuate BEFORE flipping castInstantiated: InstantiateCast() only
                    // ever adds to the roster and is guarded solely by that flag, so
                    // resetting it without first clearing the old cast doubled the
                    // roster on the next instantiate instead of replacing it.
                    place.EvacuateRoster();
                    place.placeDef = d;
                    place.castInstantiated = false;
                    place.stock?.GetDirectlyHeldThings().ClearAndDestroyContents();
                    Log.Message("[RimMandrake.Inhabited] " + place.LabelCap + " is now a " + d.defName
                                + " (fate " + d.fate + "); its cast and stock will re-roll.");
                });
        }

        [DebugAction(Cat, "Stuff roster (3 pawns)", allowedGameStates = AllowedGameStates.Playing)]
        private static void StuffRoster()
        {
            WorldObject_Inhabited place = FindPlace();
            if (place == null)
            {
                return;
            }

            Faction faction = place.Faction ?? Find.FactionManager.RandomNonHostileFaction(allowNonHumanlike: false);
            PawnKindDef kind = faction?.def?.basicMemberKind ?? PawnKindDefOf.Villager;

            for (int i = 0; i < 3; i++)
            {
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                    kind, faction, PawnGenerationContext.NonPlayer, place.Tile,
                    forceGenerateNewPawn: true, allowDead: false, allowDowned: false,
                    canGeneratePawnRelations: true, mustBeCapableOfViolence: false));
                if (p == null)
                {
                    continue;
                }

                // Pawn 0 gets a named social relation to a colonist. A relation is
                // the single most load-bearing element of attachment, and it is the
                // thing a records-based roster could never have carried.
                if (i == 0)
                {
                    Pawn colonist = PawnsFinder.AllMaps_FreeColonists.FirstOrDefault();
                    if (colonist != null && p.relations != null)
                    {
                        p.relations.AddDirectRelation(PawnRelationDefOf.Sibling, colonist);
                    }
                    else
                    {
                        Log.Warning("[RimMandrake.Inhabited] no free colonist to relate to; relation half of the test is not armed.");
                    }
                }

                // Pawn 1 gets a permanent injury and a trouble-trait.
                if (i == 1)
                {
                    BodyPartRecord part = p.RaceProps?.body?.AllParts?
                        .FirstOrDefault(bp => bp.def == BodyPartDefOf.Eye);
                    if (part != null)
                    {
                        p.health.AddHediff(HediffDefOf.MissingBodyPart, part);
                    }
                    if (p.story?.traits != null && !p.story.traits.HasTrait(TraitDefOf.Abrasive))
                    {
                        p.story.traits.GainTrait(new Trait(TraitDefOf.Abrasive));
                    }
                }

                if (!place.roster.TryAdd(p, canMergeWithExistingStacks: false))
                {
                    Log.Error("[RimMandrake.Inhabited] roster refused " + p.LabelShort);
                    p.Destroy();
                }
            }
            place.castInstantiated = true;
            Log.Message("[RimMandrake.Inhabited] roster of " + place.LabelCap + " now holds " + place.roster.Count + ".");
            ReportRoster();
        }

        [DebugAction(Cat, "Report roster", allowedGameStates = AllowedGameStates.Playing)]
        private static void ReportRoster()
        {
            WorldObject_Inhabited place = FindPlace();
            if (place == null)
            {
                return;
            }
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("[RimMandrake.Inhabited] ROSTER REPORT  tick=" + Find.TickManager.TicksGame
                          + "  day=" + GenDate.DaysPassed
                          + "  place=" + place.LabelCap + " tile=" + place.Tile
                          + "  held=" + place.roster.Count + "  alive=" + place.SoulCount
                          + "  state=" + place.state);
            List<Pawn> held = place.roster.InnerListForReading.ToList();
            for (int i = 0; i < held.Count; i++)
            {
                sb.AppendLine("  " + Describe(held[i]));
            }
            InhabitedReport.Write("ROSTER REPORT  " + place.LabelCap, sb.ToString().TrimEndNewlines());
        }

        [DebugAction(Cat, "Report displaced pool", allowedGameStates = AllowedGameStates.Playing)]
        private static void ReportPool()
        {
            DisplacedPool pool = DisplacedPool.Current;
            if (pool == null)
            {
                Log.Error("[RimMandrake.Inhabited] no DisplacedPool game component. It should be created automatically.");
                return;
            }
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("[RimMandrake.Inhabited] DISPLACED POOL  held=" + pool.Count);
            foreach (Pawn p in pool.AllPlaceless.ToList())
            {
                sb.AppendLine("  " + Describe(p)
                              + "  reason=" + pool.ReasonFor(p)
                              + "  from=" + (pool.OriginFor(p) ?? "-"));
            }
            InhabitedReport.Write("DISPLACED POOL", sb.ToString().TrimEndNewlines());
        }

        [DebugAction(Cat, "Absorb roster into pool", allowedGameStates = AllowedGameStates.Playing)]
        private static void AbsorbRoster()
        {
            WorldObject_Inhabited place = FindPlace();
            DisplacedPool pool = DisplacedPool.Current;
            if (place == null || pool == null)
            {
                return;
            }
            List<Pawn> held = place.roster.InnerListForReading.ToList();
            int moved = 0;
            for (int i = 0; i < held.Count; i++)
            {
                Pawn p = held[i];
                if (p == null || p.Dead || !place.roster.Remove(p))
                {
                    continue;
                }
                if (pool.Absorb(p, place.Faction, DisplacedReason.Fled, place.LabelCap))
                {
                    moved++;
                }
            }
            Log.Message("[RimMandrake.Inhabited] moved " + moved + " into the pool; roster now " + place.roster.Count + ".");
        }

        [DebugAction(Cat, "Draw 3 from pool", allowedGameStates = AllowedGameStates.Playing)]
        private static void DrawFromPool()
        {
            WorldObject_Inhabited place = FindPlace();
            DisplacedPool pool = DisplacedPool.Current;
            if (place == null || pool == null)
            {
                return;
            }
            // Fixed 2026-09-02 (opus code review): this used to draw first and add
            // second, and print "ROSTER REFUSED" for anyone the roster would not
            // take -- at which point that person was out of the pool, in no roster
            // and unsaveable. A refusal now simply leaves them in the pool and
            // shows up as a smaller count.
            List<Pawn> arrived = new List<Pawn>();
            int moved = pool.DrawInto(place.Faction, 3, place.roster, arrived);
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("[RimMandrake.Inhabited] drew " + moved + "; pool now " + pool.Count + ".");
            for (int i = 0; i < arrived.Count; i++)
            {
                sb.AppendLine("  " + Describe(arrived[i]));
            }
            Log.Message(sb.ToString().TrimEndNewlines());
        }

        // ------------------------------------------------------------------
        // INHABITED_STOCK_ONTO_MAP_AND_FATE_1. These drive the stock/fate cycle
        // by hand on whatever map is open.
        //
        // 🔑 WHY THEY EXIST RATHER THAN "GENERATE A MAP AND LOOK". Neither route
        // that would run GenStep_InhabitedStock is reachable in play today.
        // WorldObject_Inhabited is a MapParent now (INHABITED_SETTLEMENT_
        // MAPPARENT_GAP_1, rebased 2026-09-04) so its map generator no longer
        // throws on cast -- but nothing in the game ever constructs an
        // Inhabited_Settlement (no producer exists yet, a second and separate
        // gap the rebase does not touch), and no TileMutatorDef anywhere in the
        // build set names Inhabited_Cast, so the wilderness route still has no
        // way in either. These actions exercise the same InhabitedStock and
        // InhabitedFateWorker calls the GenStep and the teardown patch make, on a
        // quicktest map, without waiting on either gap.
        // ------------------------------------------------------------------

        [DebugAction(Cat, "Stock: dump onto this map", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DumpStock()
        {
            WorldObject_Inhabited place = FindPlace();
            Map map = Find.CurrentMap;
            if (place == null || map == null)
            {
                return;
            }
            if (!place.castInstantiated)
            {
                place.InstantiateCast();
            }
            if (place.stock == null || place.stock.Count == 0)
            {
                Log.Warning("[RimMandrake.Inhabited] " + place.LabelCap + " holds no goods. Its archetype is "
                            + (place.placeDef?.defName ?? "NONE") + "; check its larder table.");
                return;
            }

            place.stockOnTheGround.Clear();
            place.stockSpot = map.Center.Standable(map) ? map.Center : CellFinder.RandomNotEdgeCell(12, map);
            place.stockSpawnedCount = place.stock.DumpOnto(map, place.stockSpot, place.stockOnTheGround);
            Log.Message("[RimMandrake.Inhabited] dumped " + place.stockSpawnedCount + " goods in "
                        + place.stockOnTheGround.Count + " stacks at " + place.stockSpot
                        + "; the holder now has " + place.stock.Count + " left.");
        }

        [DebugAction(Cat, "Stock: collect from this map", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CollectStock()
        {
            WorldObject_Inhabited place = FindPlace();
            Map map = Find.CurrentMap;
            if (place == null || map == null || place.stock == null)
            {
                return;
            }
            int before = place.stockSpawnedCount;
            int back = place.stock.CollectFrom(map, place.StockArea, place.stockOnTheGround);
            place.stockSpawnedCount = 0;
            place.stockSpot = IntVec3.Invalid;
            Log.Message("[RimMandrake.Inhabited] took back " + back + " of " + before
                        + "; the holder now has " + place.stock.TotalStackCount + " in "
                        + place.stock.Count + " stacks.");
        }

        [DebugAction(Cat, "Fate: test the cause now", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void TestFate()
        {
            WorldObject_Inhabited place = FindPlace();
            Map map = Find.CurrentMap;
            if (place == null || map == null)
            {
                return;
            }
            string cause = InhabitedFateWorker.DetectCause(place, map);
            Log.Message("[RimMandrake.Inhabited] fate=" + (place.placeDef?.fate.ToString() ?? "NO ARCHETYPE")
                        + "  cause=" + (cause ?? "none")
                        + "  threatened=" + place.threatened
                        + "  stockArea=" + place.StockArea
                        + "  spawned=" + place.stockSpawnedCount
                        + "  onMap=" + InhabitedStock.CountOnMap(map, place.StockArea, place.stockOnTheGround));
        }

        [DebugAction(Cat, "Fate: fire the consequence now", allowedGameStates = AllowedGameStates.Playing)]
        private static void ApplyFate()
        {
            WorldObject_Inhabited place = FindPlace();
            if (place == null)
            {
                return;
            }
            place.threatened = true;
            InhabitedFateWorker.Apply(place);
        }

        [DebugAction(Cat, "Spawn authored character", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SpawnCharacter()
        {
            List<CharacterDef> all = CharacterApplier.All.ToList();
            if (all.Count == 0)
            {
                Log.Error("[RimMandrake.Inhabited] no CharacterDefs loaded. Run cast_to_xml.py --write and redeploy.");
                return;
            }
            Dialog_DebugOptionListLister.ShowSimpleDebugMenu(
                all.OrderBy(c => c.faction).ThenBy(c => c.label),
                c => c.faction + " / " + (c.place ?? "-") + " / " + c.label,
                delegate (CharacterDef c)
                {
                    Map map = Find.CurrentMap;
                    if (map == null)
                    {
                        return;
                    }
                    Pawn p = CharacterApplier.Spawn(c, Faction.OfPlayer, null, map.Tile);
                    if (p == null)
                    {
                        Log.Error("[RimMandrake.Inhabited] could not build " + c.defName);
                        return;
                    }
                    GenSpawn.Spawn(p, CellFinder.RandomSpawnCellForPawnNear(map.Center, map), map);
                    Log.Message("[RimMandrake.Inhabited] " + c.defName + " -> " + Describe(p)
                                + "\n    ageText: " + (c.ageText ?? "-")
                                + "\n    hook:    " + (c.hook ?? "-"));
                });
        }

        private static string Describe(Pawn p)
        {
            if (p == null)
            {
                return "NULL ENTRY  <- this is a failure";
            }
            int relations = p.relations?.DirectRelations?.Count ?? -1;
            int hediffs = p.health?.hediffSet?.hediffs?.Count ?? -1;
            return p.ThingID
                   + "  " + (p.Name?.ToStringFull ?? p.LabelShort)
                   + "  age=" + p.ageTracker.AgeBiologicalYears + "y"
                   + " (" + p.ageTracker.AgeBiologicalTicks + " ticks)"
                   + "  relations=" + relations
                   + "  hediffs=" + hediffs
                   + "  traits=" + (p.story?.traits?.allTraits?.Count ?? -1)
                   + "  dead=" + p.Dead
                   + "  faction=" + (p.Faction?.Name ?? "-");
        }

        private static PlanetTile CurrentTile()
        {
            if (Find.CurrentMap != null)
            {
                return Find.CurrentMap.Tile;
            }
            List<WorldObject> sel = Find.WorldSelector?.SelectedObjects?.OfType<WorldObject>().ToList();
            if (sel != null && sel.Count > 0)
            {
                return sel[0].Tile;
            }
            return PlanetTile.Invalid;
        }

        private static WorldObject_Inhabited FindPlace()
        {
            WorldObject_Inhabited place = Find.WorldObjects.AllWorldObjects
                .OfType<WorldObject_Inhabited>()
                .FirstOrDefault();
            if (place == null)
            {
                Log.Warning("[RimMandrake.Inhabited] no WorldObject_Inhabited exists. Run 'Create place at current tile' first.");
            }
            return place;
        }
    }
}
