using System.Linq;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI.Group;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_CAMPS_SCAVENGERS_EVENTS_1 live criteria A2-A5: PUBLIC STATIC wrappers so `jawa/static_call` (which refuses instance
    /// methods) can drive the corpse site's daily step and the passage's arrival, and read back one text line each. Current map
    /// only. Validation surface: nothing in play calls these.
    /// </summary>
    public static class TitanValidationHooks
    {
        /// <summary>Generates an adult of `kindDefName` at `cell` and kills it there, so the real Corpse.SpawnSetup -> corpse-site
        /// conversion path runs. Returns the corpse's tier and id.</summary>
        public static string KillTitanAt(string kindDefName, IntVec3 cell)
        {
            Map map = Find.CurrentMap;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindDefName);
            if (map == null || kind == null) return "FAIL no map or kind " + kindDefName;
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, map.Tile,
                allowDowned: true, fixedBiologicalAge: kind.RaceProps.lifeStageAges.Last().minAge + 1f));
            GenSpawn.Spawn(p, cell, map);
            string tier = TitanicTierUtility.GetTier(p).ToString();
            p.Kill(null);
            return "killed " + p.ThingID + " tier=" + tier + " bodySize=" + p.BodySize.ToString("0.0") + " corpse=" + (p.Corpse?.ThingID ?? "none");
        }

        public static string SiteReport()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "FAIL no map";
            var sites = map.listerThings.AllThings.OfType<Building_TitanicCorpseSite>().ToList();
            var sb = new StringBuilder("sites=" + sites.Count);
            foreach (var s in sites)
            {
                sb.Append(" | ").Append(s.ThingID).Append(" at ").Append(s.Position.x).Append(',').Append(s.Position.z)
                  .Append(" meat=").Append(s.MeatRemaining).Append(" eaten=").Append(s.VisitorsEatenTotal)
                  .Append(" scav=").Append(s.ScavengerCount).Append(" camp=").Append(s.CamperCount);
                foreach (Pawn p in s.Scavengers.Where(x => x != null))
                    sb.Append(" S[").Append(p.kindDef.defName).Append(" tier=").Append(TitanicTierUtility.AdultTier(p.def))
                      .Append(" homedHere=").Append(map.Biomes.Any(b => b.CommonalityOfAnimal(p.kindDef) > 0f))
                      .Append(" pred=").Append(p.RaceProps.predator).Append(" spawned=").Append(p.Spawned)
                      .Append(" atSite=").Append(CorpseSiteVisitors.AtSite(p, s)).Append(']');
                foreach (Pawn p in s.Campers.Where(x => x != null))
                {
                    Lord lord = p.GetLord();
                    sb.Append(" C[").Append(p.kindDef.defName).Append(" fac=").Append(p.Faction?.Name ?? "none")
                      .Append(" hostile=").Append(p.Faction != null && p.Faction.HostileTo(Faction.OfPlayer))
                      .Append(" lord=").Append(lord?.LordJob?.GetType().Name ?? "none")
                      .Append(" toil=").Append(lord?.CurLordToil?.GetType().Name ?? "none")
                      .Append(" spawned=").Append(p.Spawned).Append(']');
                }
            }
            return sb.ToString();
        }

        /// <summary>One forced daily step on every site of the current map (visitor meal, then the draw and camp rolls, then
        /// spoilage), then SiteReport.</summary>
        public static string SiteDailyStep()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "FAIL no map";
            foreach (var s in map.listerThings.AllThings.OfType<Building_TitanicCorpseSite>().ToList()) s.DebugDailyStep();
            return SiteReport();
        }

        public static string PassageCanFire()
        {
            Map map = Find.CurrentMap;
            IncidentDef def = DefDatabase<IncidentDef>.GetNamedSilentFail("RM_TitanPassage");
            if (map == null || def == null) return "FAIL no map or RM_TitanPassage";
            bool can = def.Worker.CanFireNow(new IncidentParms { target = map });
            bool t3 = TitanPassageUtility.T3OnMap(map);
            var kinds = DefDatabase<PawnKindDef>.AllDefsListForReading.Where(k => TitanPassageUtility.Eligible(k, map, t3)).ToList();
            return "canFire=" + can + " active=" + RM_HugeThingsSettings.TitanEventsActive + " t3OnMap=" + t3 + " eligible=" + kinds.Count
                   + " [" + string.Join(",", kinds.Select(k => k.defName + ":" + TitanicTierUtility.AdultTier(k.race))) + "]";
        }

        public static string PassageReport()
        {
            Map map = Find.CurrentMap;
            var comp = map?.GetComponent<MapComponent_TitanPassages>();
            if (comp == null) return "FAIL no MapComponent_TitanPassages";
            var sb = new StringBuilder("pending=" + comp.HasPending + " kind=" + (comp.PendingKind?.defName ?? "none")
                                       + " arrivalIn=" + (comp.HasPending ? comp.ArrivalTick - Find.TickManager.TicksGame : -1));
            Pawn a = comp.LastArrived;
            if (a != null)
            {
                Lord lord = a.GetLord();
                sb.Append(" arrived=").Append(a.ThingID).Append(" kind=").Append(a.kindDef.defName)
                  .Append(" tier=").Append(TitanicTierUtility.AdultTier(a.def)).Append(" spawned=").Append(a.Spawned)
                  .Append(" homedHere=").Append(map.Biomes.Any(b => b.CommonalityOfAnimal(a.kindDef) > 0f))
                  .Append(" lord=").Append(lord?.LordJob?.GetType().Name ?? "none")
                  .Append(" pos=").Append(a.Position.x).Append(',').Append(a.Position.z);
            }
            return sb.ToString();
        }

        public static string PassageArriveNow()
        {
            var comp = Find.CurrentMap?.GetComponent<MapComponent_TitanPassages>();
            if (comp == null) return "FAIL no MapComponent_TitanPassages";
            comp.DebugArriveNow();
            return PassageReport();
        }
    }
}
