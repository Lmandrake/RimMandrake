using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.SWBestiary
{
    // SWBESTIARY_COVERAGE_GAPS_1 follow-up (r28 left metal eating and hoarding proven only by a settings round-trip).
    // Live proof hook for jawa/static_call, args "current": spawns the real creature on the current map, puts the scrap
    // and nest beside it, and asks the SHIPPED job giver what it would do, then asks again with the setting off.
    // Everything it spawns is destroyed before it returns. Read-only on settings: the toggle is restored in a finally.
    // (The metal-eat proof moved to CreatureBehaviors' RM_MetalEaterProof with the mechanic, KHORRAK_STEEL_DIET_TIER_1.)
    public static class RSW_BeastMechanicsProof
    {
        private sealed class HoardProbe : JobGiver_HoardScrap
        {
            public Job Give(Pawn p) => TryGiveJob(p);
        }

        private static ThingDef RaceWith<T>() where T : CompProperties =>
            DefDatabase<ThingDef>.AllDefsListForReading.FirstOrDefault(d => d.race != null && d.GetCompProperties<T>() != null);

        private static Pawn SpawnWild(ThingDef race, Map map, out IntVec3 cell, out string error)
        {
            cell = IntVec3.Invalid;
            error = null;
            PawnKindDef kind = DefDatabase<PawnKindDef>.AllDefsListForReading.FirstOrDefault(k => k.race == race);
            if (kind == null)
            {
                error = "no PawnKindDef for " + race.defName;
                return null;
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 40, c => c.Standable(map) && !c.Roofed(map)
                    && !map.areaManager.Home[c] && c.GetFirstItem(map) == null && c.GetEdifice(map) == null
                    && GenAdj.CellsAdjacent8Way(new TargetInfo(c, map)).Count(a => a.InBounds(map) && a.Standable(map)
                        && !map.areaManager.Home[a] && a.GetFirstItem(map) == null && a.GetEdifice(map) == null) >= 6,
                    out cell))
            {
                error = "no open non-home cell";
                return null;
            }
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, fixedBiologicalAge: 5f,
                fixedChronologicalAge: 5f));
            GenSpawn.Spawn(p, cell, map);
            return p;
        }

        private static string JobText(Job j) =>
            j == null ? "none" : j.def.defName + " target=" + (j.targetA.Thing?.def.defName ?? "-")
                                 + " targetB=" + (j.targetB.Thing?.def.defName ?? "-");

        /// <summary>A rested, fed scrap-hoarder with its nest nearby and a hoardable item a few cells off: the giver
        /// must hand it RSW_HoardScrap (scrap, nest), and nothing with scrapHoardingEnabled off.</summary>
        public static string ProofHoard(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef race = RaceWith<CompProperties_ScrapHoarder>();
            if (map == null || race == null)
            {
                return "ERROR no map or no race with CompProperties_ScrapHoarder";
            }
            var props = race.GetCompProperties<CompProperties_ScrapHoarder>();
            ThingDef nestDef = DefDatabase<ThingDef>.GetNamedSilentFail(props.nestDef);
            ThingDef scrapDef = props.hoardableDefs?.Select(n => DefDatabase<ThingDef>.GetNamedSilentFail(n)).FirstOrDefault(d => d != null);
            if (nestDef == null || scrapDef == null)
            {
                return "ERROR nest " + props.nestDef + " or hoardable not loaded";
            }
            Pawn p = SpawnWild(race, map, out IntVec3 cell, out string err);
            if (p == null)
            {
                return "ERROR " + err;
            }
            Thing nest = null, scrap = null;
            bool was = RSW_BeastMechanicsSettings.scrapHoardingEnabled;
            try
            {
                if (!CellFinder.TryFindRandomCellNear(cell, map, 6, c => c.Standable(map) && c.GetFirstItem(map) == null
                        && c.GetEdifice(map) == null && !map.areaManager.Home[c] && c.DistanceTo(cell) >= 3f
                        && GenSpawn.CanSpawnAt(nestDef, c, map), out IntVec3 nestCell))
                {
                    return "ERROR no nest cell";
                }
                nest = GenSpawn.Spawn(nestDef, nestCell, map, WipeMode.Vanish);
                if (!CellFinder.TryFindRandomCellNear(cell, map, 6, c => c.Standable(map) && c.GetFirstItem(map) == null
                        && c.GetEdifice(map) == null && !map.areaManager.Home[c] && c.DistanceTo(nestCell) > 3f, out IntVec3 scrapCell))
                {
                    return "ERROR no scrap cell";
                }
                scrap = GenSpawn.Spawn(ThingMaker.MakeThing(scrapDef), scrapCell, map);
                if (p.needs?.food != null) p.needs.food.CurLevelPercentage = 1f;
                if (p.needs?.rest != null) p.needs.rest.CurLevel = 1f;
                var probe = new HoardProbe();
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = true;
                string on = JobText(probe.Give(p));
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = false;
                string off = JobText(probe.Give(p));
                return "hoarder=" + race.defName + " nest=" + nestDef.defName + " scrap=" + scrapDef.defName
                       + " on=" + on.Replace(' ', '|') + " off=" + off.Replace(' ', '|');
            }
            finally
            {
                RSW_BeastMechanicsSettings.scrapHoardingEnabled = was;
                if (scrap != null && !scrap.Destroyed) scrap.Destroy();
                if (nest != null && !nest.Destroyed) nest.Destroy();
                if (!p.Destroyed) p.Destroy();
            }
        }
    }
}
