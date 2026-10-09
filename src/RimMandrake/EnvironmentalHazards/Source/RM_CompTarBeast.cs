using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_BEAST_BUILD_1 - the tar beast (design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md s3).
    // Built on RM_CompStationEater (bites, satiation, mound + letter) and the RUT_BeastBulge wake chain
    // (damage / construction / dig-shaft lottery via RM_CompBeastWakeRelay, plus RM_CompBulgePumpWake below).
    // Everything the beast does is a state change a player can read: tar coating behind it, a mound and a
    // letter per swallowed building, a message and a tar ring when it sinks. Nothing vanishes unsigned.

    public class CompProperties_TarBeast : CompProperties
    {
        public ThingDef trailFilthDef;
        public int trailLayers = 2;
        public float trailRadius = 1.5f;
        public ThingDef bulgeDef;
        public int staggerTicks = 90;
        public HediffDef paceHediff;

        public CompProperties_TarBeast()
        {
            compClass = typeof(RM_CompTarBeast);
        }
    }

    public class RM_CompTarBeast : ThingComp
    {
        private IntVec3 lastCell = IntVec3.Invalid;
        private bool paceApplied;
        private bool huntPending;

        public CompProperties_TarBeast Props => (CompProperties_TarBeast)props;
        private Pawn Beast => (Pawn)parent;

        public override void CompTick()
        {
            base.CompTick();
            Pawn pawn = Beast;
            if (!RM_EnvironmentalHazardsSettings.tarBeastEnabled || pawn.Dead || !pawn.Spawned)
            {
                return;
            }
            if (!paceApplied)
            {
                paceApplied = true;
                ApplyPace(pawn);
                // The bulge's PawnSpawnOnWakeup put it in a defend-point Lord whose duty would override the think tree.
                pawn.GetLord()?.Notify_PawnLost(pawn, PawnLostCondition.ForcedToJoinOtherLord);
                // SUMP_SOLVENT_WAKE_BUILD_1: woken by a solvent pour -> hunts every pawn on the map, for good.
                // TAR_BEAST_SETTINGS_CONSISTENCY_1: the wake record is consumed once, so a refused mental state is
                // remembered and retried below instead of being lost.
                if (RM_MapComponent_TarSolventWake.TryConsume(pawn.Map, pawn.Position, out bool hunt) && hunt)
                {
                    huntPending = true;
                    TryStartHunt(pawn);
                }
            }
            else if (huntPending && pawn.IsHashIntervalTick(60))
            {
                TryStartHunt(pawn);
            }
            // TAR_BEAST_SETTINGS_CONSISTENCY_1: a changed pace setting reaches beasts already awake.
            if (pawn.IsHashIntervalTick(250))
            {
                ApplyPace(pawn);
            }

            IntVec3 pos = pawn.Position;
            if (pos != lastCell)
            {
                lastCell = pos;
                if (Props.trailFilthDef != null)
                {
                    RM_TarCoatingUtility.CoatCells(pawn.Map, GenRadial.RadialCellsAround(pos, Props.trailRadius, true), Props.trailFilthDef, Props.trailLayers);
                }
            }

            if (pawn.IsHashIntervalTick(20))
            {
                ShoveNeighbours(pawn);
            }
            if (pawn.IsHashIntervalTick(250) && ShouldSink(pawn))
            {
                Sink(pawn);
            }
        }

        private void TryStartHunt(Pawn pawn)
        {
            if (pawn.MentalStateDef == MentalStateDefOf.ManhunterPermanent)
            {
                huntPending = false;
                return;
            }
            if (pawn.mindState?.mentalStateHandler != null
                && pawn.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.ManhunterPermanent,
                    reason: "tar woken by solvent", forceWake: true, transitionSilently: true))
            {
                huntPending = false;
            }
        }

        // The pace slider is read through three hediff stages (slow / normal / fast presets), refreshed every 250
        // ticks so a changed setting reaches beasts already awake.
        private void ApplyPace(Pawn pawn)
        {
            if (Props.paceHediff == null || pawn.health == null)
            {
                return;
            }
            float pace = RM_EnvironmentalHazardsSettings.tarBeastPace;
            float want = pace < 0.75f ? 0.5f : (pace > 1.5f ? 2.5f : 1.5f);
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(Props.paceHediff) ?? pawn.health.AddHediff(Props.paceHediff);
            if (h.Severity != want)
            {
                h.Severity = want;
            }
        }

        // Pawns in the way are staggered, never bitten.
        private void ShoveNeighbours(Pawn beast)
        {
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(beast))
            {
                if (!c.InBounds(beast.Map))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(beast.Map);
                for (int i = 0; i < things.Count; i++)
                {
                    Pawn p = things[i] as Pawn;
                    if (p != null && p != beast && !p.Dead && p.stances != null && p.stances.stagger != null)
                    {
                        p.stances.stagger.StaggerFor(Props.staggerTicks);
                    }
                }
            }
        }

        private bool ShouldSink(Pawn pawn)
        {
            RM_CompStationEater eater = pawn.TryGetComp<RM_CompStationEater>();
            if (eater == null)
            {
                return false;
            }
            if (eater.Satiated) // Satiated reads tarBeastMaxBuildings for a tar beast: one effective limit
            {
                return true;
            }
            // A solvent-woken beast that has nobody left to hunt sinks back down. It hunts every pawn on the map,
            // so "nobody" means no other living, standing pawn that is not an animal (colonists, raiders, visitors).
            return pawn.MentalStateDef == MentalStateDefOf.ManhunterPermanent && !AnyoneToHunt(pawn);
        }

        private static bool AnyoneToHunt(Pawn beast)
        {
            IReadOnlyList<Pawn> all = beast.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn p = all[i];
                if (p != beast && !p.Dead && !p.Downed && !p.AnimalOrWildMan())
                {
                    return true;
                }
            }
            return false;
        }

        // Back into the deepest tar as a dormant bulge, far from the colony; says so.
        private void Sink(Pawn pawn)
        {
            Map map = pawn.Map;
            IntVec3 here = pawn.Position;
            IntVec3 dest = IntVec3.Invalid;
            if (Props.bulgeDef != null)
            {
                float best = -1f;
                for (int tries = 0; tries < 400; tries++)
                {
                    IntVec3 c = CellFinder.RandomCell(map);
                    TerrainDef t = c.GetTerrain(map);
                    if (t == null || t != RM_MapComponent_SumpLivingMap.TarDeep || !c.Standable(map) && c.GetFirstBuilding(map) != null)
                    {
                        continue;
                    }
                    float d = ClosestPlayerBuildingDist(map, c);
                    if (d > best)
                    {
                        best = d;
                        dest = c;
                    }
                }
            }
            if (dest.IsValid)
            {
                Thing bulge = ThingMaker.MakeThing(Props.bulgeDef);
                GenSpawn.Spawn(bulge, dest, map);
                RM_TarCoatingUtility.CoatCells(map, GenRadial.RadialCellsAround(dest, 2.5f, true), Props.trailFilthDef, 1);
            }
            Messages.Message("The tar beast sinks back into the black" + (dest.IsValid ? ", and a smooth bulge rises elsewhere in the tar." : "."),
                new TargetInfo(here, map), MessageTypeDefOf.NeutralEvent);
            pawn.Destroy();
        }

        private static float ClosestPlayerBuildingDist(Map map, IntVec3 c)
        {
            float best = 9999f;
            List<Building> bs = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < bs.Count; i++)
            {
                float d = (bs[i].Position - c).LengthHorizontal;
                if (d < best)
                {
                    best = d;
                }
            }
            return best;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastCell, "tarBeastLastCell", IntVec3.Invalid);
            Scribe_Values.Look(ref paceApplied, "tarBeastPaceApplied", false);
            Scribe_Values.Look(ref huntPending, "tarBeastHuntPending", false);
        }
    }

    // Crawls to the densest cluster of the colony's buildings, then hands the eating to RM_EatStructure.
    // Null for any pawn without RM_CompTarBeast, so inserting it on the global Animal_PreMain tag is inert for the rest.
    public class RM_JobGiver_TarBeastEat : ThinkNode_JobGiver
    {
        private const float ClusterRadius = 12f;

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!RM_EnvironmentalHazardsSettings.tarBeastEnabled || pawn.TryGetComp<RM_CompTarBeast>() == null)
            {
                return null;
            }
            RM_CompStationEater eater = pawn.TryGetComp<RM_CompStationEater>();
            if (eater == null || eater.Satiated)
            {
                return null;
            }
            List<Building> all = pawn.Map.listerBuildings.allBuildingsColonist;
            float reach = eater.Props.searchRadius;
            var near = new List<Building>();
            for (int i = 0; i < all.Count; i++)
            {
                if ((all[i].Position - pawn.Position).LengthHorizontal <= reach)
                {
                    near.Add(all[i]);
                }
            }
            if (near.Count == 0)
            {
                return null;
            }
            // stride-sample the scoring pass so a huge base cannot stall a tick
            int stride = near.Count > 300 ? near.Count / 300 + 1 : 1;
            Building best = null;
            int bestScore = -1;
            for (int i = 0; i < near.Count; i += stride)
            {
                int score = 0;
                for (int j = 0; j < near.Count; j += stride)
                {
                    if ((near[i].Position - near[j].Position).LengthHorizontalSquared <= ClusterRadius * ClusterRadius)
                    {
                        score++;
                    }
                }
                if (score > bestScore && pawn.CanReach(near[i], PathEndMode.Touch, Danger.Deadly))
                {
                    bestScore = score;
                    best = near[i];
                }
            }
            if (best == null)
            {
                return null;
            }
            return JobMaker.MakeJob(RM_EnvironmentalHazardsJobDefOf.RM_EatStructure, best);
        }
    }

    // On RUT_BeastBulge: pumping or deep drilling within range wakes the dormant beast (the spec's
    // "deep dig ... and pumping" wake cause; the dig-shaft cause is RM_CompBeastWakeRelay).
    public class CompProperties_BulgePumpWake : CompProperties
    {
        public float radius = 30f;
        public List<string> workingDefNames = new List<string>();

        public CompProperties_BulgePumpWake()
        {
            compClass = typeof(RM_CompBulgePumpWake);
        }
    }

    public class RM_CompBulgePumpWake : ThingComp
    {
        public CompProperties_BulgePumpWake Props => (CompProperties_BulgePumpWake)props;

        public override void CompTick()
        {
            base.CompTick();
            if (!RM_EnvironmentalHazardsSettings.tarBeastEnabled || !parent.Spawned || !parent.IsHashIntervalTick(250))
            {
                return; // mod option off: the pump relay must not wake a beast the option disables
            }
            float radius = Props.radius * RM_EnvironmentalHazardsSettings.tarBeastPumpWakeFactor;
            CompCanBeDormant dormant = parent.GetComp<CompCanBeDormant>();
            if (radius <= 0f || dormant == null || dormant.Awake)
            {
                return;
            }
            foreach (Building b in parent.Map.listerBuildings.allBuildingsColonist)
            {
                if ((b.Position - parent.Position).LengthHorizontalSquared > radius * radius)
                {
                    continue;
                }
                if (IsWorking(b))
                {
                    parent.GetComp<CompWakeUpDormant>()?.Activate(null);
                    return;
                }
            }
        }

        private bool IsWorking(Building b)
        {
            CompDeepDrill drill = b.GetComp<CompDeepDrill>();
            if (drill != null)
            {
                return drill.UsedLastTick();
            }
            if (Props.workingDefNames.Contains(b.def.defName))
            {
                CompPowerTrader power = b.GetComp<CompPowerTrader>();
                return power == null || power.PowerOn;
            }
            return false;
        }
    }
}
