using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // Two scrub dens, both decided by the owner by question card 2026-10-26.
    //
    // THORNHOLD_DECIDE_DEN_AND_STAND -> "Stand its ground":
    //   RM_CompVineDen picks the nearest venomvine cell (a list of plant defs in
    //   XML) and makes it the thornhold's HomeTether home. Struck by a living
    //   attacker while within standRadius of that den, the wild thornhold starts
    //   RM_ThornholdStand (ScopedAggression): hostile to that attacker only,
    //   ending when the attacker is downed, gone, or farther than the disengage
    //   radius from the den. The comp runs in Pawn.PostApplyDamage BEFORE
    //   mindState.Notify_DamageTaken (decomp Pawn.cs 1938 vs 1952), and an animal
    //   in a mental state neither flees (FleeUtility.ShouldAnimalFleeDanger) nor
    //   rolls vanilla manhunter, so the stand replaces the flight. Nobody is
    //   attacked for walking past: only damage starts it.
    //
    // ROLLBUG_DECIDE_CARRION_BALL -> "Any corpse in reach":
    //   A wild rollbug now and then walks to the nearest flesh corpse in reach,
    //   ANY corpse, the player's kills and dead colonists included (Mod Setting
    //   rollbugTakesColonyCorpses, default on, can exclude the player's own),
    //   picks it up and rolls it to its larder (the HomeTether home). There it
    //   strips the corpse (gear lies at the larder, never destroyed) and over the
    //   following days RM_CompCarrionLarder takes vanilla-shaped bites: one
    //   outside body part becomes a fresh Bite MissingBodyPart and its nutrition
    //   feeds the bug; when only the core part is left the corpse is gone (a
    //   ball that dries out first is no longer Rollable: it lies there like
    //   vanilla dessicated remains). No item is ever made, so nothing is
    //   duplicated; Corpse.Destroy would destroy gear (lesson 20261026T091325Z),
    //   so every Destroy is preceded by Strip.
    // ════════════════════════════════════════════════════════════════════

    [DefOf]
    public static class RM_ScrubDensDefOf
    {
        public static JobDef RM_RollCarrion;

        static RM_ScrubDensDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ScrubDensDefOf));
        }
    }

    // ── Thornhold: the vine den and the stand ────────────────────────────

    public class RM_CompProperties_VineDen : CompProperties
    {
        public List<ThingDef> denPlants = new List<ThingDef>();

        public float searchRadius = 30f;

        public float standRadius = 6f;

        public float disengageRadius = 12f;

        public float maxChaseRadius = 30f;

        public MentalStateDef standState;

        public int retryIntervalTicks = 2500;

        public RM_CompProperties_VineDen()
        {
            compClass = typeof(RM_CompVineDen);
        }
    }

    public class RM_CompVineDen : ThingComp
    {
        private IntVec3 den = IntVec3.Invalid;

        // The tether home before the first den replaced it (its spawn cell). The setting is SettingScope.Now and its
        // tooltip promises "Off: it picks no den (it still keeps near where it first appeared)", so switching dens off
        // mid-game hands the tether this cell back instead of leaving the thornhold bound to its old vine.
        private IntVec3 preDenHome = IntVec3.Invalid;

        public RM_CompProperties_VineDen Props => (RM_CompProperties_VineDen)props;

        public IntVec3 Den => den;

        public static bool DenOn => RM_WindCalendar.On(RM_LeaningScrubSettings.thornholdDenEnabled);

        public static bool StandOn => DenOn && RM_LeaningScrubSettings.thornholdStandEnabled;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad || !den.IsValid)
            {
                TryPickDen();
            }
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            if (!parent.Spawned || !parent.IsHashIntervalTick(Mathf.Max(60, Props.retryIntervalTicks), delta))
            {
                return;
            }
            if (!DenOn)
            {
                if (den.IsValid)
                {
                    ReleaseDen();
                }
                return;
            }
            // Re-pick only when there is no den or its vine is gone (cut, burnt, trimmed).
            if (!den.IsValid || !HasDenPlant(parent.Map, den))
            {
                TryPickDen();
            }
        }

        public bool HasDenPlant(Map map, IntVec3 cell)
        {
            if (map == null || !cell.InBounds(map))
            {
                return false;
            }
            Plant plant = cell.GetPlant(map);
            return plant != null && Props.denPlants.Contains(plant.def);
        }

        /// <summary>Nearest reachable den-plant cell within searchRadius, made the HomeTether home. Null on success, else why not.</summary>
        public string TryPickDen()
        {
            Pawn pawn = parent as Pawn;
            if (!DenOn)
            {
                return "thornhold dens are off";
            }
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Faction != null)
            {
                return "not a spawned wild pawn";
            }
            Map map = pawn.Map;
            float limit = Props.searchRadius * Props.searchRadius;
            // Candidates in range, nearest first, so reachability is asked only until one answers.
            List<IntVec3> near = new List<IntVec3>();
            for (int d = 0; d < Props.denPlants.Count; d++)
            {
                ThingDef plantDef = Props.denPlants[d];
                if (plantDef == null)
                {
                    continue;
                }
                List<Thing> plants = map.listerThings.ThingsOfDef(plantDef);
                for (int i = 0; i < plants.Count; i++)
                {
                    if ((plants[i].Position - pawn.Position).LengthHorizontalSquared <= limit)
                    {
                        near.Add(plants[i].Position);
                    }
                }
            }
            IntVec3 here = pawn.Position;
            near.Sort((a, b) => (a - here).LengthHorizontalSquared.CompareTo((b - here).LengthHorizontalSquared));
            IntVec3 found = IntVec3.Invalid;
            for (int i = 0; i < near.Count && i < 40; i++)
            {
                if (pawn.CanReach(near[i], PathEndMode.OnCell, Danger.Deadly))
                {
                    found = near[i];
                    break;
                }
            }
            if (!found.IsValid)
            {
                return "no reachable den plant within " + Props.searchRadius.ToString("F0") + " cells";
            }
            RM_CompHomeTether tether = pawn.TryGetComp<RM_CompHomeTether>();
            if (!preDenHome.IsValid && tether != null && tether.Home.IsValid && tether.Home != den)
            {
                preDenHome = tether.Home;   // a save from before this field has den == tether home: nothing to keep
            }
            den = found;
            tether?.SetHome(den);
            return null;
        }

        /// <summary>Dens switched off: forget the den and give the tether back the home it had before (or, for a save
        /// made before preDenHome existed, where the thornhold stands now).</summary>
        public void ReleaseDen()
        {
            RM_CompHomeTether tether = parent.TryGetComp<RM_CompHomeTether>();
            if (tether != null && tether.Home == den)
            {
                tether.SetHome(preDenHome.IsValid ? preDenHome : parent.Position);
            }
            den = IntVec3.Invalid;
        }

        /// <summary>Why a hit from `instigator` would not start the stand, or null when it would.</summary>
        public string WhyNotStand(Thing instigator, DamageDef damage)
        {
            Pawn pawn = parent as Pawn;
            if (!StandOn)
            {
                return "thornhold stand is off";
            }
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.Faction != null)
            {
                return "not a spawned, standing, wild pawn";
            }
            if (pawn.InMentalState)
            {
                return "already in a mental state";
            }
            if (Props.standState == null)
            {
                return "no standState in the comp";
            }
            if (!den.IsValid)
            {
                return "has no den";
            }
            if ((pawn.Position - den).LengthHorizontalSquared > Props.standRadius * Props.standRadius)
            {
                return "outside its den radius";
            }
            if (!(instigator is Pawn attacker) || attacker.Dead || !attacker.Spawned || attacker.Map != pawn.Map || attacker == pawn)
            {
                return "no living attacker on the map";
            }
            if (damage == null || !damage.ExternalViolenceFor(pawn))
            {
                return "not external violence";
            }
            return null;
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            if (WhyNotStand(dinfo.Instigator, dinfo.Def) != null)
            {
                return;
            }
            StartStand((Pawn)dinfo.Instigator);
        }

        public bool StartStand(Pawn attacker)
        {
            Pawn pawn = (Pawn)parent;
            if (!pawn.mindState.mentalStateHandler.TryStartMentalState(Props.standState, null, forced: true, forceWake: true,
                    causedByMood: false, otherPawn: attacker, transitionSilently: false, causedByDamage: true))
            {
                return false;
            }
            if (pawn.MentalState is RM_MentalState_ScopedAggression stand)
            {
                float reach = Mathf.Sqrt((attacker.Position - den).LengthHorizontalSquared) + 4f;
                stand.anchorCell = den;
                stand.disengageRadius = Mathf.Max(Props.disengageRadius, Mathf.Min(reach, Props.maxChaseRadius));
            }
            return true;
        }

        public override string CompInspectStringExtra()
        {
            return den.IsValid && DenOn ? "Dens in the venomvine." : null;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref den, "rmVineDen", IntVec3.Invalid);
            Scribe_Values.Look(ref preDenHome, "rmVineDenPrevHome", IntVec3.Invalid);
        }

        /// <summary>Bridge proof: the thornhold at `cell` — its den, or why it has none.</summary>
        public static string ProofDen(Map map, IntVec3 cell)
        {
            RM_CompVineDen comp = FindAt<RM_CompVineDen>(map, cell, out Pawn p);
            if (comp == null)
            {
                return "REFUSED: no vine-den pawn at " + cell;
            }
            string why = comp.TryPickDen();
            IntVec3 home = p.TryGetComp<RM_CompHomeTether>()?.Home ?? IntVec3.Invalid;
            return why == null ? "DEN " + p.ThingID + " den=" + comp.den + " home=" + home : "REFUSED: " + why;
        }

        /// <summary>Bridge proof: hit the thornhold at `cell` as if `attackerCell`'s pawn struck it; report the resulting state.</summary>
        public static string ProofStand(Map map, IntVec3 cell, IntVec3 attackerCell)
        {
            RM_CompVineDen comp = FindAt<RM_CompVineDen>(map, cell, out Pawn p);
            Pawn attacker = map == null ? null : attackerCell.GetFirstPawn(map);
            if (comp == null || attacker == null)
            {
                return "REFUSED: need a vine-den pawn at " + cell + " and a pawn at " + attackerCell;
            }
            string why = comp.WhyNotStand(attacker, DamageDefOf.Scratch);
            if (why != null)
            {
                return "REFUSED: " + why;
            }
            if (!comp.StartStand(attacker))
            {
                return "REFUSED: TryStartMentalState refused";
            }
            return "STAND " + p.ThingID + " state=" + p.MentalStateDef?.defName + " target=" + attacker.ThingID;
        }

        internal static T FindAt<T>(Map map, IntVec3 cell, out Pawn pawn) where T : ThingComp
        {
            pawn = null;
            if (map == null || !cell.InBounds(map))
            {
                return null;
            }
            foreach (Thing t in cell.GetThingList(map))
            {
                if (t is Pawn p && p.TryGetComp<T>() is T comp)
                {
                    pawn = p;
                    return comp;
                }
            }
            return null;
        }
    }

    // ── Rollbug: the carrion ball and the larder ─────────────────────────

    public class RM_CompProperties_CarrionLarder : CompProperties
    {
        public float reachRadius = 14f;

        public float larderRadius = 2f;

        // PROVISIONAL (builder): about 12 bites a day while the bug is home and hungry.
        public int biteIntervalTicks = 5000;

        public RM_CompProperties_CarrionLarder()
        {
            compClass = typeof(RM_CompCarrionLarder);
        }
    }

    public class RM_CompCarrionLarder : ThingComp
    {
        private IntVec3 fallbackLarder = IntVec3.Invalid;

        // The corpse this bug last rolled home. The drop is ThingPlaceMode.Near and a cell holds one item (GenPlace
        // PlaceSpotQualityAt), so once stripped gear fills the larder's cells the ball lands beyond larderRadius; the
        // radial scan alone then missed it, the bug rolled the same corpse home again and again and never ate it.
        // Remembered, it counts as the larder's ball while it lies within larderRadius + BallKeepMargin of the larder.
        private Corpse ball;

        private const float BallKeepMargin = 6f;

        public RM_CompProperties_CarrionLarder Props => (RM_CompProperties_CarrionLarder)props;

        public static bool On => RM_WindCalendar.On(RM_LeaningScrubSettings.rollbugCarrionEnabled);

        public IntVec3 Larder
        {
            get
            {
                IntVec3 home = parent.TryGetComp<RM_CompHomeTether>()?.Home ?? IntVec3.Invalid;
                return home.IsValid ? home : fallbackLarder;
            }
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!fallbackLarder.IsValid)
            {
                fallbackLarder = parent.Position;
            }
        }

        public bool InLarder(Thing t, Map map)
        {
            IntVec3 larder = Larder;
            return larder.IsValid && t.Map == map
                && (t.Position - larder).LengthHorizontalSquared <= Props.larderRadius * Props.larderRadius;
        }

        /// <summary>A corpse already lying in this bug's larder, or null.</summary>
        public Corpse BallAtLarder()
        {
            Map map = parent.Map;
            IntVec3 larder = Larder;
            if (map == null || !larder.IsValid)
            {
                return null;
            }
            if (ball != null)
            {
                float keep = Props.larderRadius + BallKeepMargin;
                if (ball.Spawned && ball.Map == map && Rollable(ball) && (ball.Position - larder).LengthHorizontalSquared <= keep * keep)
                {
                    return ball;
                }
                ball = null;   // eaten, hauled off, burnt, dried out or carried away: forget it
            }
            foreach (IntVec3 c in GenRadial.RadialCellsAround(larder, Props.larderRadius, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i] is Corpse corpse && Rollable(corpse))
                    {
                        return corpse;
                    }
                }
            }
            return null;
        }

        /// <summary>Flesh, not dried out, not an Anomaly unnatural corpse, not burning, not bugged.</summary>
        public static bool Rollable(Corpse corpse)
        {
            return corpse != null && !corpse.Destroyed && !corpse.Bugged && !(corpse is UnnaturalCorpse)
                && corpse.InnerPawn?.RaceProps != null && corpse.InnerPawn.RaceProps.IsFlesh
                && corpse.GetRotStage() != RotStage.Dessicated && !corpse.IsBurning();
        }

        /// <summary>Why this bug would not go for carrion now, or null (corpse in `found`).</summary>
        public string WhyNotRoll(out Corpse found)
        {
            found = null;
            Pawn pawn = parent as Pawn;
            if (!On)
            {
                return "rollbug carrion is off";
            }
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.Faction != null)
            {
                return "not a spawned, standing, wild pawn";
            }
            if (pawn.InMentalState)
            {
                return "in a mental state";
            }
            if (pawn.carryTracker == null || pawn.carryTracker.CarriedThing != null)
            {
                return "already carrying";
            }
            IntVec3 larder = Larder;
            if (!larder.IsValid)
            {
                return "has no larder";
            }
            if (BallAtLarder() != null)
            {
                return "a ball already lies in its larder";
            }
            Map map = pawn.Map;
            float best = Props.reachRadius * Props.reachRadius;
            List<Thing> corpses = map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse);
            for (int i = 0; i < corpses.Count; i++)
            {
                if (!(corpses[i] is Corpse corpse) || !corpse.Spawned || !Rollable(corpse))
                {
                    continue;
                }
                float d = (corpse.Position - pawn.Position).LengthHorizontalSquared;
                if (d > best || InLarder(corpse, map))
                {
                    continue;
                }
                if (!RM_LeaningScrubSettings.rollbugTakesColonyCorpses && corpse.InnerPawn.Faction == Faction.OfPlayer)
                {
                    continue;
                }
                if (pawn.carryTracker.MaxStackSpaceEver(corpse.def) < 1
                    || !pawn.CanReserve(corpse)
                    || !pawn.CanReach(corpse, PathEndMode.ClosestTouch, Danger.Some))
                {
                    continue;
                }
                best = d;
                found = corpse;
            }
            if (found == null)
            {
                return "no rollable corpse within " + Props.reachRadius.ToString("F0") + " cells";
            }
            if (!map.reachability.CanReach(found.Position, larder, PathEndMode.OnCell, TraverseParms.For(pawn, Danger.Some)))
            {
                found = null;
                return "larder unreachable from the corpse";
            }
            return null;
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            if (!parent.Spawned || !parent.IsHashIntervalTick(Mathf.Max(60, Props.biteIntervalTicks), delta))
            {
                return;
            }
            TryBite(out _);
        }

        /// <summary>One bite of the ball in the larder. Null when it bit, else why not.</summary>
        public string TryBite(out string what)
        {
            what = null;
            Pawn pawn = parent as Pawn;
            if (!On)
            {
                return "rollbug carrion is off";
            }
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.Faction != null
                || pawn.carryTracker?.CarriedThing != null)
            {
                return "not a free, standing, wild bug";
            }
            Need_Food food = pawn.needs?.food;
            if (food == null)
            {
                return "has no food need";
            }
            float room = food.MaxLevel - food.CurLevel;
            if (food.CurLevelPercentage > 0.75f || room <= 0f)
            {
                return "not hungry";
            }
            if (!InLarder(pawn, pawn.Map))
            {
                return "not at its larder";
            }
            Corpse ball = BallAtLarder();
            if (ball == null)
            {
                return "no ball in its larder";
            }
            what = Bite(ball, pawn, room);
            return null;
        }

        /// <summary>
        /// Vanilla corpse-bite shape (Corpse.IngestedCalculateAmounts): one outside part
        /// becomes a fresh Bite MissingBodyPart; the core part, no part left, or a dried
        /// corpse ends it. Gear is stripped to the ground first, every time.
        /// </summary>
        public static string Bite(Corpse ball, Pawn eater, float room)
        {
            if (ball.AnythingToStrip())
            {
                ball.Strip(false);
            }
            Pawn inner = ball.InnerPawn;
            BodyPartRecord core = inner.RaceProps.body.corePart;
            BodyPartRecord part = ball.GetRotStage() == RotStage.Dessicated ? null : ball.GetBestBodyPartToEat(room);
            float nutrition = part == null ? 0f : FoodUtility.GetBodyPartNutrition(ball, part);
            if (part == null || part == core)
            {
                if (inner.RaceProps.Humanlike && PawnUtility.ShouldSendNotificationAbout(inner))
                {
                    Messages.Message("MessageEatenByPredator".Translate(inner.LabelShort, eater.Named("PREDATOR"), inner.Named("EATEN")).CapitalizeFirst(),
                        eater, MessageTypeDefOf.NegativeEvent);
                }
                string label = ball.LabelShort;
                ball.Destroy();
                Feed(eater, nutrition, room);
                return "FINISHED " + label;
            }
            Hediff_MissingPart missing = (Hediff_MissingPart)HediffMaker.MakeHediff(HediffDefOf.MissingBodyPart, inner, part);
            missing.lastInjury = HediffDefOf.Bite;
            missing.IsFresh = true;
            inner.health.AddHediff(missing);
            Feed(eater, nutrition, room);
            return "BIT " + part.Label + " (" + nutrition.ToString("F2") + " nutrition)";
        }

        private static void Feed(Pawn eater, float nutrition, float room)
        {
            if (eater.needs?.food != null && nutrition > 0f)
            {
                eater.needs.food.CurLevel += Mathf.Min(nutrition, room);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref fallbackLarder, "rmLarderFallback", IntVec3.Invalid);
            if (Scribe.mode == LoadSaveMode.Saving && ball != null && !ball.Spawned)
            {
                ball = null;   // only a ball lying on the map is worth a reference (a carried-off one may never come back)
            }
            Scribe_References.Look(ref ball, "rmLarderBall");
        }

        /// <summary>The driver's drop: this corpse is now the larder's ball, wherever Near put it.</summary>
        public void Notify_RolledHome(Corpse corpse)
        {
            ball = corpse;
        }

        /// <summary>Bridge proof: ask the real job giver for the rollbug at `cell`. "ORDERED ..." or "REFUSED: why".</summary>
        public static string ProofOrderRoll(Map map, IntVec3 cell)
        {
            RM_CompCarrionLarder comp = RM_CompVineDen.FindAt<RM_CompCarrionLarder>(map, cell, out Pawn bug);
            if (comp == null)
            {
                return "REFUSED: no larder pawn at " + cell;
            }
            Job job = new RM_JobGiver_RollCarrion().TryIssueJobPackage(bug, default(JobIssueParams)).Job;
            if (job == null)
            {
                return "REFUSED: " + (comp.WhyNotRoll(out _) ?? "giver returned no job");
            }
            bug.jobs.StartJob(job, JobCondition.InterruptForced);
            return "ORDERED " + bug.ThingID + " -> " + job.targetA.Thing?.ThingID + " larder=" + job.targetB.Cell;
        }

        /// <summary>Bridge proof: one bite by the rollbug at `cell` (hunger forced to empty first).</summary>
        public static string ProofBite(Map map, IntVec3 cell)
        {
            RM_CompCarrionLarder comp = RM_CompVineDen.FindAt<RM_CompCarrionLarder>(map, cell, out Pawn bug);
            if (comp == null)
            {
                return "REFUSED: no larder pawn at " + cell;
            }
            if (bug.needs?.food != null)
            {
                bug.needs.food.CurLevel = 0f;
            }
            string why = comp.TryBite(out string what);
            return why == null ? "ATE " + what : "REFUSED: " + why;
        }
    }

    public class RM_JobGiver_RollCarrion : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            RM_CompCarrionLarder comp = pawn.TryGetComp<RM_CompCarrionLarder>();
            if (comp == null || comp.WhyNotRoll(out Corpse corpse) != null)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(RM_ScrubDensDefOf.RM_RollCarrion, corpse, comp.Larder);
            job.count = 1;
            job.haulMode = HaulMode.ToCellNonStorage;
            return job;
        }
    }

    public class RM_JobDriver_RollCarrion : JobDriver
    {
        private const TargetIndex CorpseInd = TargetIndex.A;
        private const TargetIndex LarderInd = TargetIndex.B;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(CorpseInd), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDestroyedOrNull(CorpseInd);
            this.FailOn(() => !RM_CompCarrionLarder.On);
            // Never leave a carried corpse inside the bug: ExitMap destroys a carried thing
            // (decomp Pawn.cs ~2550) and an interrupted job must not keep it in hand.
            AddFinishAction(delegate
            {
                if (pawn.Spawned && pawn.Map != null && pawn.carryTracker?.CarriedThing is Corpse)
                {
                    pawn.carryTracker.TryDropCarriedThing(pawn.Position, ThingPlaceMode.Near, out _);
                }
            });
            yield return Toils_Goto.GotoThing(CorpseInd, PathEndMode.ClosestTouch).FailOnDespawnedOrNull(CorpseInd);
            yield return Toils_Haul.StartCarryThing(CorpseInd);
            yield return Toils_Goto.GotoCell(LarderInd, PathEndMode.OnCell);
            Toil drop = ToilMaker.MakeToil("RM_RollCarrion_Drop");
            drop.initAction = delegate
            {
                if (pawn.carryTracker.TryDropCarriedThing(job.GetTarget(LarderInd).Cell, ThingPlaceMode.Near, out Thing dropped)
                    && dropped is Corpse ball)
                {
                    pawn.TryGetComp<RM_CompCarrionLarder>()?.Notify_RolledHome(ball);
                    if (ball.AnythingToStrip())
                    {
                        ball.Strip(false);
                    }
                }
            };
            drop.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return drop;
        }
    }
}
