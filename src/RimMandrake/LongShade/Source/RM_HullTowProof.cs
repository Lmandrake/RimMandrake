using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.LongShade
{
    /// <summary>static_call probe for LONGSHADE_JAWATOW_RECHECK_1 (driven by LongShade/prove_jawatow.py).
    /// Every method works on Find.CurrentMap and returns one line the driver parses:
    ///   Hull("")      "HULL biome=X hasHull=B center=x,z rect=x,z,w,h entered=B clanComing=B towed=B buildings=N items=N hostiles=N"
    ///   Stage("")     a drafted colonist is spawned inside the hull, hostile pawns in it are killed and loose items
    ///                 (corpses included) destroyed: "STAGED colonist=x,z killed=N items=N"
    ///   CanFire(arg)  asks a FRESH IncidentWorker_RM_HullTow (IncidentWorker.CanFireNow caches its answer per worker per
    ///                 tick, so the def's own worker replays a stale answer in a paused game). arg "disabled" sets
    ///                 jawaReturnEnabled=false for the question and restores it. "CANFIRE forced=B unforced=B setting=B"
    ///   Fire("")      TryExecute on a fresh worker, then reports the pawns that arrived:
    ///                 "FIRED ok=B pawns=N faction=X peacefulMaker=B hostile=B lords=LordJob_X clanComing=B"
    /// Nothing here changes the mechanism; it only reads it and stages the scene.</summary>
    public static class RM_HullTowProof
    {
        private const string DefName = "RUT_JawaReturnTow";

        private static RM_MapComponent_CrawlerHull HullOf(Map map) => map?.GetComponent<RM_MapComponent_CrawlerHull>();

        private static IEnumerable<IntVec3> Cells(Map map, RM_MapComponent_CrawlerHull h)
        {
            foreach (IntVec3 c in h.HullRect) if (c.InBounds(map)) yield return c;
        }

        public static string Hull(string _)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_CrawlerHull h = HullOf(map);
            if (map == null || h == null) return "REFUSED: no current map or no RM_MapComponent_CrawlerHull";
            int buildings = 0, items = 0, hostiles = 0;
            if (h.hullCenter.IsValid)
            {
                foreach (IntVec3 c in Cells(map, h))
                {
                    foreach (Thing t in c.GetThingList(map))
                    {
                        if (t.def.category == ThingCategory.Building && t.Faction == null
                            && !(t.def.building != null && t.def.building.isNaturalRock)) buildings++;
                        else if (t is Pawn p && !p.Dead && p.HostileTo(Faction.OfPlayer)) hostiles++;
                        else if (t.def.category == ThingCategory.Item && t.def.EverHaulable) items++;
                    }
                }
            }
            CellRect r = h.HullRect;
            return "HULL biome=" + map.Biome.defName + " hasHull=" + h.HasHull + " center=" + h.hullCenter.x + "," + h.hullCenter.z
                + " rect=" + r.minX + "," + r.minZ + "," + r.Width + "," + r.Height + " entered=" + h.Entered
                + " clanComing=" + h.ClanComing + " towed=" + h.Towed + " towTicks=" + h.TowTicks
                + " buildings=" + buildings + " items=" + items + " hostiles=" + hostiles;
        }

        public static string Stage(string _)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_CrawlerHull h = HullOf(map);
            if (map == null || h == null || !h.HasHull) return "REFUSED: no hull on the current map";
            int killed = 0, destroyed = 0;
            foreach (IntVec3 c in Cells(map, h).ToList())
            {
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (t is Pawn p && !p.Dead && p.HostileTo(Faction.OfPlayer)) { p.Kill(null); killed++; }
                }
            }
            foreach (IntVec3 c in Cells(map, h).ToList())
            {
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (t.def.category == ThingCategory.Item && t.def.EverHaulable && !t.Destroyed) { t.Destroy(DestroyMode.Vanish); destroyed++; }
                }
            }
            List<IntVec3> spots = Cells(map, h).Where(c => c.Standable(map) && c.GetFirstPawn(map) == null)
                .OrderBy(c => c.DistanceToSquared(h.hullCenter)).ToList();
            if (spots.Count == 0) return "REFUSED: no standable cell inside the hull";
            IntVec3 spot = spots[0];
            Pawn col = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            GenSpawn.Spawn(col, spot, map);
            if (col.drafter != null) col.drafter.Drafted = true;   // stays put through the 250-tick entry scan
            return "STAGED colonist=" + spot.x + "," + spot.z + " killed=" + killed + " items=" + destroyed;
        }

        private static IncidentWorker Fresh(IncidentDef def)
        {
            IncidentWorker w = (IncidentWorker)Activator.CreateInstance(def.workerClass);
            w.def = def;
            return w;
        }

        private static IncidentParms Parms(IncidentDef def, Map map, bool forced)
        {
            IncidentParms p = StorytellerUtility.DefaultParmsNow(def.category, map);
            p.forced = forced;
            return p;
        }

        public static string CanFire(string arg)
        {
            Map map = Find.CurrentMap;
            IncidentDef def = DefDatabase<IncidentDef>.GetNamedSilentFail(DefName);
            if (map == null || def == null) return "REFUSED: no map or no IncidentDef " + DefName;
            bool old = RM_LongShadeSettings.jawaReturnEnabled;
            try
            {
                if (arg == "disabled") RM_LongShadeSettings.jawaReturnEnabled = false;
                bool forced = Fresh(def).CanFireNow(Parms(def, map, true));
                bool unforced = Fresh(def).CanFireNow(Parms(def, map, false));
                return "CANFIRE forced=" + forced + " unforced=" + unforced + " setting=" + RM_LongShadeSettings.jawaReturnEnabled;
            }
            finally { RM_LongShadeSettings.jawaReturnEnabled = old; }
        }

        public static string Fire(string _)
        {
            Map map = Find.CurrentMap;
            IncidentDef def = DefDatabase<IncidentDef>.GetNamedSilentFail(DefName);
            RM_MapComponent_CrawlerHull h = HullOf(map);
            if (map == null || def == null || h == null) return "REFUSED: no map, def or hull component";
            var before = new HashSet<Pawn>(map.mapPawns.AllPawnsSpawned);
            bool ok = Fresh(def).TryExecute(Parms(def, map, true));
            List<Pawn> arrived = map.mapPawns.AllPawnsSpawned.Where(p => !before.Contains(p) && p.Faction != null && !p.Faction.IsPlayer).ToList();
            Faction f = arrived.FirstOrDefault()?.Faction;
            bool peaceful = f?.def.pawnGroupMakers != null && f.def.pawnGroupMakers.Any(m => m.kindDef == PawnGroupKindDefOf.Peaceful);
            string lords = string.Join("+", arrived.Select(p => p.GetLord()?.LordJob?.GetType().Name ?? "none").Distinct());
            return "FIRED ok=" + ok + " pawns=" + arrived.Count + " faction=" + (f?.def.defName ?? "none")
                + " factions=" + arrived.Select(p => p.Faction).Distinct().Count() + " peacefulMaker=" + peaceful
                + " hostile=" + (f != null && f.HostileTo(Faction.OfPlayer)) + " lords=" + lords + " clanComing=" + h.ClanComing;
        }
    }
}
