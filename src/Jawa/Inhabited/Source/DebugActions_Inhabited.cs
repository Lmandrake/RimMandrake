using System.Collections.Generic;
using System.Linq;
using System.Text;
using LudeonTK;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace Inhabited
{
    /// <summary>
    /// THE ARCHITECTURE GATE, as a harness.
    ///
    /// Caravan is designed to be TRANSIENT and this design uses its shape for
    /// something PERMANENT. Pawns held in a ThingOwner off-map are not ticked --
    /// which is exactly what "frozen until visited" wants -- but vanilla never
    /// stress-tests that across years, and everything else in Inhabited rests on
    /// it holding.
    ///
    /// This file only MEASURES. It fixes nothing and it must not start to: if a
    /// roster does not survive intact, the container choice is wrong and the
    /// design gets re-specified before anything more is built on it.
    ///
    /// THE SOAK, which is not something this file can run:
    ///   1. Stuff a roster       (Inhabited: stuff roster)
    ///   2. Report                (Inhabited: report roster)  -- keep the output
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
        private const string Cat = "Inhabited";

        [DebugAction(Cat, "Create place at current tile", allowedGameStates = AllowedGameStates.Playing)]
        private static void CreatePlaceHere()
        {
            PlanetTile tile = CurrentTile();
            if (!tile.Valid)
            {
                Log.Warning("[Inhabited] no current tile: open a map or select a world tile.");
                return;
            }
            if (Find.WorldObjects.AnyWorldObjectAt<WorldObject_Inhabited>(tile))
            {
                Log.Message("[Inhabited] a place already exists at tile " + tile + ".");
                return;
            }
            WorldObjectDef def = DefDatabase<WorldObjectDef>.GetNamedSilentFail("Inhabited_Place");
            if (def == null)
            {
                Log.Error("[Inhabited] WorldObjectDef Inhabited_Place did not load.");
                return;
            }
            WorldObject_Inhabited place = (WorldObject_Inhabited)WorldObjectMaker.MakeWorldObject(def);
            place.Tile = tile;
            place.SetFaction(Find.FactionManager.RandomNonHostileFaction(allowNonHumanlike: false));
            place.Name = "Test place";
            Find.WorldObjects.Add(place);
            Log.Message("[Inhabited] created " + place.LabelCap + " at tile " + tile
                        + " for " + (place.Faction?.Name ?? "no faction") + ".");
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
                        Log.Warning("[Inhabited] no free colonist to relate to; relation half of the test is not armed.");
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
                    Log.Error("[Inhabited] roster refused " + p.LabelShort);
                    p.Destroy();
                }
            }
            place.castInstantiated = true;
            Log.Message("[Inhabited] roster of " + place.LabelCap + " now holds " + place.roster.Count + ".");
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
            sb.AppendLine("[Inhabited] ROSTER REPORT  tick=" + Find.TickManager.TicksGame
                          + "  day=" + GenDate.DaysPassed
                          + "  place=" + place.LabelCap + " tile=" + place.Tile
                          + "  held=" + place.roster.Count + "  alive=" + place.SoulCount
                          + "  state=" + place.state);
            List<Pawn> held = place.roster.InnerListForReading.ToList();
            for (int i = 0; i < held.Count; i++)
            {
                sb.AppendLine("  " + Describe(held[i]));
            }
            Log.Message(sb.ToString().TrimEndNewlines());
        }

        [DebugAction(Cat, "Report displaced pool", allowedGameStates = AllowedGameStates.Playing)]
        private static void ReportPool()
        {
            DisplacedPool pool = DisplacedPool.Current;
            if (pool == null)
            {
                Log.Error("[Inhabited] no DisplacedPool game component. It should be created automatically.");
                return;
            }
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("[Inhabited] DISPLACED POOL  held=" + pool.Count);
            foreach (Pawn p in pool.AllPlaceless.ToList())
            {
                sb.AppendLine("  " + Describe(p)
                              + "  reason=" + pool.ReasonFor(p)
                              + "  from=" + (pool.OriginFor(p) ?? "-"));
            }
            Log.Message(sb.ToString().TrimEndNewlines());
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
            Log.Message("[Inhabited] moved " + moved + " into the pool; roster now " + place.roster.Count + ".");
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
            List<Pawn> drawn = pool.Draw(place.Faction, 3);
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("[Inhabited] drew " + drawn.Count + "; pool now " + pool.Count + ".");
            for (int i = 0; i < drawn.Count; i++)
            {
                sb.AppendLine("  " + Describe(drawn[i]));
                if (!place.roster.TryAdd(drawn[i], canMergeWithExistingStacks: false))
                {
                    sb.AppendLine("    ROSTER REFUSED");
                }
            }
            Log.Message(sb.ToString().TrimEndNewlines());
        }

        [DebugAction(Cat, "Spawn authored character", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SpawnCharacter()
        {
            List<CharacterDef> all = CharacterApplier.All.ToList();
            if (all.Count == 0)
            {
                Log.Error("[Inhabited] no CharacterDefs loaded. Run cast_to_xml.py --write and redeploy.");
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
                        Log.Error("[Inhabited] could not build " + c.defName);
                        return;
                    }
                    GenSpawn.Spawn(p, CellFinder.RandomSpawnCellForPawnNear(map.Center, map), map);
                    Log.Message("[Inhabited] " + c.defName + " -> " + Describe(p)
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
                Log.Warning("[Inhabited] no WorldObject_Inhabited exists. Run 'Create place at current tile' first.");
            }
            return place;
        }
    }
}
