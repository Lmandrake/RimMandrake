using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.GelatinousSlime
{
    // SLIME_SEEKER_LOAD_TOOL_1: the seeker loaded, extracted, injected and raced, without the archive dialog. Built as
    // jawa/static_call proofs in this assembly (the pattern later suites use) instead of a JawaBench jawa/slime_seeker_load
    // tool: the proof calls the mod's own SetLoad / job / target effects. Args "current" = the current map. Each stages
    // its own pawns and items near the map centre; ProofInject removes the patients it made. Output is key=value.
    public static class RM_SlimeSeekerProof
    {
        private static GeneDef Target()
        {
            GeneArchiveDef archive = GeneArchiveDef.Active;
            return archive?.targetGenes?.FirstOrDefault(g => g != SlimeDefs.PheromoneCharm && g != SlimeDefs.TheReek)
                   ?? DefDatabase<GeneDef>.AllDefsListForReading.FirstOrDefault(g => g.defName.StartsWith("RM_Gene_")
                       && g != SlimeDefs.PheromoneCharm && g != SlimeDefs.TheReek);
        }

        private static IntVec3 Near(Map map, int r)
        {
            CellFinder.TryFindRandomCellNear(map.Center, map, r, c => c.Standable(map) && !c.Fogged(map), out IntVec3 cell);
            return cell;
        }

        private static Pawn Colonist(Map map)
        {
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDefOf.Colonist, Faction.OfPlayer,
                forceGenerateNewPawn: true, allowDowned: false));
            GenSpawn.Spawn(p, Near(map, 8), map);
            return p;
        }

        private static Thing Seeker(ThingDef def, GeneDef target, GeneDef rider, Map map)
        {
            Thing s = ThingMaker.MakeThing(def);
            s.TryGetComp<CompGeneSeeker>()?.SetLoad(target, rider);
            GenPlace.TryPlaceThing(s, Near(map, 6), map, ThingPlaceMode.Near);
            return s;
        }

        /// <summary>A primed seeker on the ground, read back: what jawa/slime_seeker_load would have done.</summary>
        public static string ProofLoad(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_GeneSeeker");
            GeneDef target = Target();
            if (map == null || def == null || target == null)
            {
                return "ERROR no map, RM_GeneSeeker or archive gene";
            }
            Thing s = Seeker(def, target, SlimeDefs.TheReek, map);
            CompGeneSeeker comp = s.TryGetComp<CompGeneSeeker>();
            return string.Format("seekerId={0} primed={1} target={2} rider={3}", s.thingIDNumber, comp?.Primed,
                comp?.TargetGene?.defName, comp?.RiderGene?.defName);
        }

        /// <summary>A colonist ordered to carry a primed seeker to a cell and drink there (the extract job). Step
        /// extractWorkTicks plus the walk, then ProofExtractState.</summary>
        public static string ProofExtractStart(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_GeneSeeker");
            JobDef job = DefDatabase<JobDef>.GetNamedSilentFail("RM_ExtractSlimeSample");
            GeneDef target = Target();
            if (map == null || def == null || job == null || target == null)
            {
                return "ERROR no map, seeker, job or archive gene";
            }
            Thing s = Seeker(def, target, SlimeDefs.TheReek, map);
            Pawn p = Colonist(map);
            IntVec3 site = Near(map, 5);
            Job j = JobMaker.MakeJob(job, s, site);
            j.count = 1;
            bool took = p.jobs.TryTakeOrderedJob(j, JobTag.Misc);
            return string.Format("STARTED took={0} pawnId={1} seekerId={2} target={3} workTicks={4}", took, p.thingIDNumber,
                s.thingIDNumber, target.defName, s.TryGetComp<CompGeneSeeker>()?.Props?.extractWorkTicks ?? -1);
        }

        /// <summary>Loaded seekers on the map carrying a load (the def swap happened).</summary>
        public static string ProofExtractState(Map map)
        {
            map = map ?? Find.CurrentMap;
            List<Thing> loaded = SlimeDefs.GeneSeekerLoaded == null ? new List<Thing>()
                : map.listerThings.ThingsOfDef(SlimeDefs.GeneSeekerLoaded);
            int withLoad = loaded.Count(t => t.TryGetComp<CompGeneSeeker>()?.Primed ?? false);
            return string.Format("loaded={0} loadedWithLoad={1}", loaded.Count, withLoad);
        }

        private static string Inject(Map map, Pawn user, Pawn patient, GeneDef target, GeneDef rider)
        {
            Thing s = ThingMaker.MakeThing(SlimeDefs.GeneSeekerLoaded);
            s.TryGetComp<CompGeneSeeker>()?.SetLoad(target, rider);
            GenPlace.TryPlaceThing(s, patient.Position, map, ThingPlaceMode.Near);
            CompTargetEffect_InjectSlimeGenes eff = (s as ThingWithComps)?.GetComp<CompTargetEffect_InjectSlimeGenes>();
            if (eff == null)
            {
                return "noEffect";
            }
            eff.DoEffectOn(user, patient);
            Hediff slim = patient.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification);
            HediffComp_Slimification sc = SlimeUtility.GetSlimification(patient);
            Hediff mark = SlimeDefs.SlimeMarked == null ? null : patient.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.SlimeMarked);
            return string.Format("target={0} rider={1} coma={2} slim={3:0.00} fastClock={4} ratePerDay={5:0.000} mark={6:0.0} seekerUsed={7}",
                patient.genes?.HasEndogene(target) ?? false,
                rider == null || (patient.genes?.HasEndogene(rider) ?? false),
                SlimeDefs.XenogerminationComa != null && patient.health.hediffSet.HasHediff(SlimeDefs.XenogerminationComa),
                slim?.Severity ?? 0f, sc?.FastClock ?? false, sc?.RatePerDay(patient) ?? 0f, mark?.Severity ?? 0f, s.Destroyed);
        }

        /// <summary>Two injections and the race: A takes target + The Reek (mark 2, fast clock ~1/3 a day), B already
        /// carries the pheromone charm and takes target with no rider (mark 0); then a slime antidote on A ends it.</summary>
        public static string ProofInject(Map map)
        {
            map = map ?? Find.CurrentMap;
            GeneDef target = Target();
            ThingDef antidote = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SlimeAntidote");
            if (map == null || target == null || SlimeDefs.GeneSeekerLoaded == null || antidote == null || !ModsConfig.BiotechActive)
            {
                return "ERROR no map, archive gene, loaded seeker, antidote or Biotech";
            }
            Pawn doctor = Colonist(map);
            Pawn a = Colonist(map);
            Pawn b = Colonist(map);
            string ra = Inject(map, doctor, a, target, SlimeDefs.TheReek);
            if (SlimeDefs.PheromoneCharm != null)
            {
                b.genes.AddGene(SlimeDefs.PheromoneCharm, false);
            }
            string rb = Inject(map, doctor, b, target, null);
            Thing amp = ThingMaker.MakeThing(antidote);
            GenPlace.TryPlaceThing(amp, a.Position, map, ThingPlaceMode.Near);
            CompTargetEffect_SlimeAntidote cure = (amp as ThingWithComps)?.GetComp<CompTargetEffect_SlimeAntidote>();
            cure?.DoEffectOn(doctor, a);
            bool curedA = !a.health.hediffSet.HasHediff(SlimeDefs.Slimification);
            foreach (Pawn p in new[] { doctor, a, b })
            {
                if (!p.Destroyed)
                {
                    p.Destroy();
                }
            }
            if (!amp.Destroyed)
            {
                amp.Destroy();
            }
            return "A[" + ra + "] B[" + rb + "] antidoteCuredA=" + curedA;
        }
    }
}
