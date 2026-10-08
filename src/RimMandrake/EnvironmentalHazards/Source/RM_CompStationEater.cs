using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S3 (sump_kit_spec.md, "station-eating"). Generic by
    // construction — not Sump-specific — matching this mod's own posture for
    // every other reusable comp (RM_CompFloodIgniter, RM_CompWorkedLottery):
    // any future "eats player structures, ignores pawns" creature reuses
    // this unchanged, same rationale RM_SetPieceElement_SpawnMarker /
    // RM_SetPieceElement_AnchoredPawn already document for their own genus.
    //
    // ❓ resolved (this item's own named breach-seam question): NOT
    // JobGiver_AIBreaching / BreachingUtility (RimWorld/JobGiver_AIBreaching.cs,
    // RimWorld/BreachingUtility.cs — both read in full this pass). That
    // machinery is raid-specific end to end: a Lord running
    // LordJob_AssaultColonyBreaching, a per-Lord BreachingGrid computed by
    // LordToil_AssaultColonyBreaching.UpdateCurrentBreachTarget, and target
    // selection gated on the pawn's own EQUIPPED VERB
    // (BreachingUtility.FindVerbToUseForBreaching reads pawn.equipment,
    // requires verb.verbProps.ai_IsBuildingDestroyer). A lone, factionless,
    // weaponless dormant-beast-turned-pawn has none of that: no Lord, no
    // raid, no equipped weapon. Reusing it would mean building a fake
    // one-pawn Lord/BreachingGrid purely to satisfy an API shaped for
    // squads — more machinery than the job needs, not less. The small
    // custom JobGiver + JobDriver below (GenClosest.ClosestThingReachable +
    // direct DamageInfo application, no verb, no Lord — the same
    // ClosestThingReachable call CompWakeUpDormant.TickRareWorker's own
    // wakeUpOnThingConstructedRadius check already uses) is the smaller,
    // correct answer.
    //
    // "Never hunts pawns" is structural here, not tuned low:
    // RM_JobGiver_EatNearestStructure only ever searches
    // ThingRequestGroup.BuildingArtificial (verified,
    // Verse/ThingRequestGroup.cs — a Pawn is never a member of that group),
    // so there is no code path by which this JobGiver can hand the pawn a
    // Pawn as a target.
    //
    // Wired onto RM_TarBeast (TheSump, SUMP_TAR_BEAST_BUILD_1); RM_CompTarBeast adds the tar trail, shoving and sinking.
    public class CompProperties_StationEater : CompProperties
    {
        /// <summary>How far to search for a player structure. INVENTED —
        /// the spec names no number, only "the nearest player-built
        /// structure cluster."</summary>
        public float searchRadius = 60f;

        /// <summary>Damage per bite. INVENTED.</summary>
        public float eatDamagePerHit = 60f;

        /// <summary>Ticks between bites — the EATING cadence, distinct from
        /// the spec's own 0.9 c/s MOVE speed (a PawnKindDef-level stat, the
        /// roster pass owns it). INVENTED.</summary>
        public int ticksPerBite = 180;

        /// <summary>Falls back to DamageDefOf.Crush if unset — same
        /// fallback-default idiom RM_CompWorkedLottery.trapDamageDef already
        /// uses in this mod.</summary>
        public DamageDef eatDamageDef;

        /// <summary>Satiation — the spec's own INVENTED numbers ("8
        /// structures / 3 days"). Crossing either ends the eating job; see
        /// RM_CompStationEater.Satiated's own comment for what v1 does and
        /// does not do about it.</summary>
        public int maxStructuresEaten = 8;

        public int maxTicksAwake = 3 * 60000; // 3 in-game days (GenDate.TicksPerDay = 60000)

        /// <summary>SUMP_TAR_BEAST_BUILD_1: filth left where a structure was swallowed (a mound of it). Null = none.</summary>
        public ThingDef moundFilthDef;
        public int moundLayers = 4;

        /// <summary>Letter on each swallow; {0} = the building's label. Blank = no letter.</summary>
        public string letterLabel;
        public string letterText;

        public CompProperties_StationEater()
        {
            compClass = typeof(RM_CompStationEater);
        }
    }

    public class RM_CompStationEater : ThingComp
    {
        private int structuresEaten;
        private int wakeTick = -1;

        public CompProperties_StationEater Props => (CompProperties_StationEater)props;

        /// <summary>v1 satiation per the spec's own "may land one build
        /// later — flag, not silent": once true, RM_JobGiver_EatNearestStructure
        /// stops handing out eat jobs. The full "re-submerge into a fresh
        /// bulge at a new deep-tar cell" behavior is the deferred polish —
        /// this pass ships the check, not the re-submergence; see the item
        /// file's own "not done, honestly" section.</summary>
        public bool Satiated
        {
            get
            {
                CompProperties_StationEater props = Props;
                if (props == null)
                {
                    return false;
                }
                if (structuresEaten >= props.maxStructuresEaten)
                {
                    return true;
                }
                return wakeTick >= 0 && Find.TickManager.TicksGame - wakeTick >= props.maxTicksAwake;
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (wakeTick < 0)
            {
                wakeTick = Find.TickManager.TicksGame;
            }
        }

        public int StructuresEaten => structuresEaten;

        public void NotifyStructureDestroyed()
        {
            structuresEaten++;
        }

        /// <summary>Leaves the mound and sends the letter. Called by the driver with the target's facts
        /// captured BEFORE the killing blow (a destroyed Thing has no Map).</summary>
        public void OnStructureSwallowed(string label, IntVec3 cell, Map map)
        {
            CompProperties_StationEater props = Props;
            if (props == null || map == null)
            {
                return;
            }
            if (props.moundFilthDef != null)
            {
                RM_TarCoatingUtility.CoatCells(map, new List<IntVec3> { cell }, props.moundFilthDef, props.moundLayers);
            }
            if (!string.IsNullOrEmpty(props.letterLabel))
            {
                Find.LetterStack.ReceiveLetter(
                    props.letterLabel,
                    string.Format(props.letterText ?? "{0}", label),
                    LetterDefOf.NegativeEvent,
                    new TargetInfo(cell, map));
            }
        }

        /// <summary>Same GenClosest.ClosestThingReachable call
        /// CompWakeUpDormant.TickRareWorker already uses for
        /// wakeUpOnThingConstructedRadius (RimWorld/CompWakeUpDormant.cs:67,
        /// verified) — ThingRequestGroup.BuildingArtificial structurally
        /// excludes pawns from the result, see this file's own header.</summary>
        public Thing FindNearestStructure(Pawn pawn)
        {
            CompProperties_StationEater props = Props;
            if (props == null || pawn.Map == null)
            {
                return null;
            }
            return GenClosest.ClosestThingReachable(
                pawn.Position,
                pawn.Map,
                ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial),
                PathEndMode.Touch,
                TraverseParms.For(pawn),
                props.searchRadius,
                (Thing t) => t.Faction == Faction.OfPlayer && !t.Destroyed);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref structuresEaten, "structuresEaten", 0);
            Scribe_Values.Look(ref wakeTick, "wakeTick", -1);
        }
    }

    public class RM_JobGiver_EatNearestStructure : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_CompStationEater eater = pawn.TryGetComp<RM_CompStationEater>();
            if (eater == null || eater.Satiated)
            {
                return null;
            }

            Thing target = eater.FindNearestStructure(pawn);
            if (target == null)
            {
                return null;
            }

            return JobMaker.MakeJob(RM_EnvironmentalHazardsJobDefOf.RM_EatStructure, target);
        }
    }

    public class RM_JobDriver_EatStructure : JobDriver
    {
        private const TargetIndex StructInd = TargetIndex.A;

        private int ticksUntilNextBite;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // No reservation: eating is destructive, not claim-based — it
            // never competes with a colonist's own claim on the same
            // building, matching the spec's "evacuate, not fight" register.
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksUntilNextBite, "ticksUntilNextBite", 0);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(StructInd);
            this.FailOnDestroyedOrNull(StructInd);

            yield return Toils_Goto.GotoThing(StructInd, PathEndMode.Touch);

            Toil eat = ToilMaker.MakeToil("MakeNewToils");
            eat.tickIntervalAction = delegate (int delta)
            {
                Thing target = job.GetTarget(StructInd).Thing;
                if (target == null || target.Destroyed)
                {
                    ReadyForNextToil();
                    return;
                }

                // Satiation and the tar-beast option are checked by the job
                // giver only; re-check here so a running job stops too.
                RM_CompStationEater eater = pawn.TryGetComp<RM_CompStationEater>();
                if (eater != null && (eater.Satiated
                    || (!RM_EnvironmentalHazardsSettings.tarBeastEnabled && pawn.TryGetComp<RM_CompTarBeast>() != null)))
                {
                    EndJobWith(JobCondition.Succeeded);
                    return;
                }

                ticksUntilNextBite -= delta;
                if (ticksUntilNextBite > 0)
                {
                    return;
                }

                CompProperties_StationEater props = eater?.Props;
                float damage = props?.eatDamagePerHit ?? 60f;
                DamageDef damageDef = props?.eatDamageDef ?? DamageDefOf.Crush;
                ticksUntilNextBite += props?.ticksPerBite ?? 180;
                if (ticksUntilNextBite < 1)
                {
                    ticksUntilNextBite = 1;
                }

                string targetLabel = target.LabelCap;
                IntVec3 targetCell = target.Position;
                Map targetMap = target.Map;
                target.TakeDamage(new DamageInfo(damageDef, damage, instigator: pawn));

                if (target.Destroyed)
                {
                    eater?.NotifyStructureDestroyed();
                    eater?.OnStructureSwallowed(targetLabel, targetCell, targetMap);
                    ReadyForNextToil();
                }
            };
            eat.defaultCompleteMode = ToilCompleteMode.Never;
            yield return eat;
        }
    }

    [DefOf]
    public static class RM_EnvironmentalHazardsJobDefOf
    {
        public static JobDef RM_EatStructure;

        // SUMP_SOLVENT_WAKE_BUILD_1 - see RM_TarSolventPour.cs.
        public static JobDef RM_PourSolvent;

        // GREENTIDE_MECHANICS_2 M6, feller 3 — see RM_JobGiver_GnawTreeBase.cs.
        public static JobDef RM_GnawTreeBase;

        // SUMP_MECHANICS_1 S2 build pass — see RM_WorkGiver_WorkLottery.cs.
        public static JobDef RM_WorkLottery;

        // SUMP_MECHANICS_1 owner card 2 — see RM_WorkGiver_DisarmLotteryTrap.cs.
        public static JobDef RM_DisarmLotteryTrap;

        static RM_EnvironmentalHazardsJobDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_EnvironmentalHazardsJobDefOf));
        }
    }
}
