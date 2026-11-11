using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_CAMPS_SCAVENGERS_EVENTS_1, card #4 (owner 2026-09-09): a T3 corpse site is "harvested over days - camps, spoilage,
    /// scavenger draw". Once a day the site may draw scavengers (wild predators of the map's own biomes, never a titan) and,
    /// rarely, a camp of people from a non-hostile faction who sit by the remains for a while and cut their share. Both eat into
    /// the site's meat pool while they are near it, so the player races them for the yield. Engine-only: no creature or faction
    /// is named - the map's biomes and the world's factions decide who comes.
    /// </summary>
    public static class CorpseSiteVisitors
    {
        public const float NearRadius = 10f;

        /// <summary>Wild predators the map's biomes home, adult tier None (a titan is never a scavenger), the season survivable.</summary>
        public static List<PawnKindDef> ScavengerKinds(Map map)
        {
            return map.Biomes.SelectMany(b => b.AllWildAnimals).Distinct()
                .Where(k => k?.race?.race != null && k.RaceProps.Animal && k.RaceProps.predator && !k.RaceProps.Dryad
                            && TitanicTierUtility.AdultTier(k.race) == TitanicTier.None
                            && map.mapTemperature.SeasonAndOutdoorTemperatureAcceptableFor(k.race))
                .ToList();
        }

        /// <summary>Spawns `count` scavengers of one kind at a map edge and sends them to the site. Returns those spawned.</summary>
        public static List<Pawn> DrawScavengers(Building_TitanicCorpseSite site, int count)
        {
            var spawned = new List<Pawn>();
            Map map = site.Map;
            if (map == null || count <= 0) return spawned;
            if (!ScavengerKinds(map).TryRandomElement(out PawnKindDef kind)) return spawned;
            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Animal)) return spawned;
            for (int i = 0; i < count; i++)
            {
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, map.Tile));
                GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(entry, map, 6), map);
                SendTo(p, site);
                spawned.Add(p);
            }
            if (spawned.Count > 0)
                Messages.Message("RM_TitanicCorpseSite_Scavengers".Translate(kind.GetLabelPlural(), site.LabelCap), new LookTargets(spawned),
                    MessageTypeDefOf.ThreatSmall);
            return spawned;
        }

        /// <summary>A camp: 2-4 people of one non-hostile humanlike faction walk in and stay by the remains for the setting's hours
        /// (vanilla LordJob_VisitColony with the chill spot beside the site), then leave. Returns those spawned.</summary>
        public static List<Pawn> MakeCamp(Building_TitanicCorpseSite site)
        {
            var spawned = new List<Pawn>();
            Map map = site.Map;
            if (map == null) return spawned;
            Faction faction = Find.FactionManager.AllFactionsVisible
                .Where(f => !f.IsPlayer && !f.defeated && !f.temporary && f.def.humanlikeFaction && !f.HostileTo(Faction.OfPlayer))
                .RandomElementWithFallback();
            if (faction == null) return spawned;
            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Neutral)) return spawned;
            if (!CellFinder.TryFindRandomCellNear(site.Position, map, 6, c => c.Standable(map) && !c.Fogged(map) && c.GetEdifice(map) == null,
                    out IntVec3 chill)) return spawned;
            int n = Rand.RangeInclusive(2, 4);
            for (int i = 0; i < n; i++)
            {
                PawnKindDef kind = faction.RandomPawnKind();
                if (kind == null) break;
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, faction, PawnGenerationContext.NonPlayer, map.Tile));
                GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(entry, map, 5), map);
                spawned.Add(p);
            }
            if (spawned.Count == 0) return spawned;
            int ticks = (int)(RM_HugeThingsSettings.corpseSiteCampHours * GenDate.TicksPerHour);
            LordMaker.MakeNewLord(faction, new LordJob_VisitColony(faction, chill, ticks), map, spawned);
            Find.LetterStack.ReceiveLetter("RM_TitanicCorpseSite_CampLabel".Translate(),
                "RM_TitanicCorpseSite_CampText".Translate(faction.Name, site.LabelCap), LetterDefOf.NeutralEvent, new LookTargets(spawned));
            return spawned;
        }

        /// <summary>A visitor is "at the site" while spawned on its map, able to move, and within NearRadius of its centre.</summary>
        public static bool AtSite(Pawn p, Building_TitanicCorpseSite site)
        {
            return p != null && p.Spawned && !p.Dead && !p.Downed && p.Map == site.Map
                   && p.Position.InHorDistOf(site.OccupiedRect().CenterCell, NearRadius);
        }

        private static void SendTo(Pawn p, Building_TitanicCorpseSite site)
        {
            Map map = site.Map;
            if (!CellFinder.TryFindRandomCellNear(site.Position, map, 5, c => c.Standable(map), out IntVec3 dest)) return;
            Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
            job.locomotionUrgency = LocomotionUrgency.Walk;
            p.jobs?.StartJob(job, JobCondition.InterruptForced);
        }
    }
}
