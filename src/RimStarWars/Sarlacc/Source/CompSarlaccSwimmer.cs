using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Sarlacc
{
    public class CompProperties_SarlaccSwimmer : CompProperties
    {
        /// <summary>Abstracted "birth-water" budget, in in-game days of activity before it runs dry.</summary>
        public FloatRange startingReserveRange = new FloatRange(300f, 900f);

        /// <summary>Reserve spent per in-game day of existing; moving costs more (see CompTick).</summary>
        public float reserveDrainPerDay = 1f;

        /// <summary>Reserve refilled on a successful kill (draft §2.1: "kills top it up; misses do not").</summary>
        public float reserveGainOnKill = 150f;

        /// <summary>How far (cells) the swimmer can notice a buried seep.</summary>
        public float seepDetectRadius = 4f;

        /// <summary>Chance, per periodic check, that a nearby seep is actually noticed.</summary>
        public float seepDetectChancePerCheck = 0.15f;

        /// <summary>What it becomes on rooting (Stage II).</summary>
        public ThingDef anchoredDef;

        /// <summary>The marker def a "finds a seep" check scans for.</summary>
        public ThingDef seepMarkerDef;

        public CompProperties_SarlaccSwimmer()
        {
            compClass = typeof(CompSarlaccSwimmer);
        }
    }

    /// <summary>
    /// SARLACC_HABITAT_BUILD_1, Fork 1 — rooting in play. Two triggers, either
    /// sufficient (draft §2.1): the swimmer finds a buried seep, or its birth-water
    /// reserve runs out and it roots where it stands. Also grants one of the seven
    /// changed-return hediffs (§4.5, Fork 8) to a pawn that survives being
    /// swallowed by this swimmer's vanilla CompDevourer and is spat free.
    /// </summary>
    public class CompSarlaccSwimmer : ThingComp
    {
        private float reserve = -1f;
        private bool wasDigesting;
        private Pawn lastDigestingPawn;
        private int nextRareCheckTick;

        public CompProperties_SarlaccSwimmer Props => (CompProperties_SarlaccSwimmer)props;
        private Pawn Pawn => (Pawn)parent;

        private static readonly HediffDef[] ChangedReturnHediffs =
        {
            HediffDef.Named("RSW_TheWrung"),
            HediffDef.Named("RSW_SaltEyed"),
            HediffDef.Named("RSW_TheStillness"),
            HediffDef.Named("RSW_TheTithe"),
            HediffDef.Named("RSW_TheBloom"),
            HediffDef.Named("RSW_Pressed"),
            HediffDef.Named("RSW_TakenAndReturned"),
        };

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref reserve, "rswReserve", -1f);
            Scribe_Values.Look(ref wasDigesting, "rswWasDigesting", defaultValue: false);
            Scribe_References.Look(ref lastDigestingPawn, "rswLastDigestingPawn");
            Scribe_Values.Look(ref nextRareCheckTick, "rswNextRareCheckTick", 0);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (reserve < 0f)
            {
                reserve = Props.startingReserveRange.RandomInRange;
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.Spawned || Pawn.Dead)
            {
                return;
            }

            // Watch our own swallow mechanic for the "survived and was spat free" edge,
            // independent of the rooting toggle — this is the changed-return hook.
            CompDevourer devourer = parent.TryGetComp<CompDevourer>();
            if (devourer != null)
            {
                bool digestingNow = devourer.Digesting;
                if (digestingNow)
                {
                    lastDigestingPawn = devourer.DigestingPawn;
                }
                else if (wasDigesting && lastDigestingPawn != null)
                {
                    // Any completed digestion is "a kill" for reserve purposes,
                    // whether the prey died or (rarely) survived it — only a
                    // miss (never entering Digesting) should not top up.
                    reserve += Props.reserveGainOnKill;
                    if (RSW_SarlaccSettings.changedReturnHediffsEnabled && !lastDigestingPawn.Dead)
                    {
                        GrantChangedReturn(lastDigestingPawn);
                    }
                    lastDigestingPawn = null;
                }
                wasDigesting = digestingNow;
            }

            if (!RSW_SarlaccSettings.rootingInPlayEnabled)
            {
                return;
            }

            float dayFraction = 1f / GenDate.TicksPerDay;
            float movingFactor = (Pawn.pather != null && Pawn.pather.Moving) ? 1.5f : 1f;
            reserve -= Props.reserveDrainPerDay * dayFraction * movingFactor * RSW_SarlaccSettings.reserveDrainMultiplier;

            if (Find.TickManager.TicksGame < nextRareCheckTick)
            {
                return;
            }
            nextRareCheckTick = Find.TickManager.TicksGame + 2500;

            if (reserve <= 0f)
            {
                RootHere(foundSeep: false);
                return;
            }

            if (Props.seepMarkerDef != null && Rand.Chance(Props.seepDetectChancePerCheck))
            {
                Thing seep = GenClosest.ClosestThingReachable(
                    parent.Position,
                    parent.Map,
                    ThingRequest.ForDef(Props.seepMarkerDef),
                    PathEndMode.Touch,
                    TraverseParms.For(Pawn),
                    Props.seepDetectRadius);
                if (seep != null)
                {
                    RootHere(foundSeep: true);
                }
            }
        }

        private void GrantChangedReturn(Pawn survivor)
        {
            if (survivor.Dead || survivor.health == null)
            {
                return;
            }
            HediffDef first = ChangedReturnHediffs[Rand.RangeInclusive(0, ChangedReturnHediffs.Length - 1)];
            survivor.health.AddHediff(first);
            if (Rand.Chance(RSW_SarlaccSettings.secondHediffChance))
            {
                HediffDef second = ChangedReturnHediffs[Rand.RangeInclusive(0, ChangedReturnHediffs.Length - 1)];
                if (second != first)
                {
                    survivor.health.AddHediff(second);
                }
            }
        }

        private void RootHere(bool foundSeep)
        {
            if (Props.anchoredDef == null || !parent.Spawned)
            {
                return;
            }
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            Thing anchored = ThingMaker.MakeThing(Props.anchoredDef);
            GenSpawn.Spawn(anchored, pos, map);
            if (RSW_SarlaccSettings.rootingMessagesEnabled)
            {
                string reason = foundSeep
                    ? "found a buried seep and anchored"
                    : "ran out of its birth-water reserve and rooted where it stood";
                Messages.Message(
                    Pawn.LabelShort.CapitalizeFirst() + " the sarlacc " + reason + ".",
                    anchored,
                    MessageTypeDefOf.NeutralEvent);
            }
            parent.Destroy(DestroyMode.Vanish);
        }
    }
}
