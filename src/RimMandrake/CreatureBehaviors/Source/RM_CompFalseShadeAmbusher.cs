using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// LONGSHADE_BEDAZZLE_MECHANICS_1 part 2 — the mirrak's ambush. See
    /// RM_FalseShade.cs for the design citation.
    ///
    ///   <li Class="RimMandrake.CreatureBehaviors.CompProperties_FalseShadeAmbusher">
    ///     <maxPreyBodySize>1.2</maxPreyBodySize>
    ///   </li>
    /// </summary>
    public class CompProperties_FalseShadeAmbusher : CompProperties
    {
        /// <summary>How often the comp looks for something to seize.</summary>
        public int checkIntervalTicks = 60;

        /// <summary>A victim must be this close — adjacent, i.e. standing in
        /// the "shadow" (RM_FalseShadeExtension.radius).</summary>
        public float strikeRangeCells = 1.9f;

        /// <summary>Largest body the mirrak will close over.</summary>
        public float maxPreyBodySize = 1.2f;

        /// <summary>The seizing strike, dealt once, before ordinary melee
        /// finishes the job.</summary>
        public FloatRange strikeDamageRange = new FloatRange(14f, 22f);

        public DamageDef strikeDamage;

        /// <summary>Ground at or below this real shade counts as OPEN — where
        /// a mirrak lies. It lies in the light on purpose: a shadow where no
        /// shadow should be is the whole trick.</summary>
        public float openGroundMaxShade = 0.2f;

        /// <summary>How long one bout of lying in wait lasts before the
        /// think tree gets a turn (food, rest).</summary>
        public int lieStillTicks = 2500;

        /// <summary>How far it will creep to find open ground to lie on.</summary>
        public float relocateRadius = 12f;

        /// <summary>The kill sign (owner's condition on this item: nothing
        /// "disappears spontaneously"): filth laid where the prey was seized.
        /// Defaults to vanilla Filth_Sand — the disturbed patch.</summary>
        public ThingDef seizeFilth;
        public int seizeFilthCount = 3;

        public CompProperties_FalseShadeAmbusher()
        {
            compClass = typeof(RM_CompFalseShadeAmbusher);
        }
    }

    /// <summary>
    /// Wild behaviour, in order each check:
    ///  1. something small enough stands in its "shadow" → one seizing strike
    ///     (manual TakeDamage, the RM_JobDriver_LungeAttack idiom), a disturbed
    ///     patch of filth under the victim, then vanilla AttackMelee with
    ///     killIncappedTarget to finish — no pursuit beyond that (ban 3: the
    ///     race is slow and not a predator, so the think tree never hunts).
    ///  2. its last victim lies dead nearby and it is not full → Ingest the
    ///     corpse where it fell. The corpse IS the readable remains; it is
    ///     eaten in place, never carried off.
    ///  3. it is idly wandering → lie still on open ground (Wait), creeping to
    ///     the nearest open cell first if it is standing in real shade.
    /// A tamed mirrak strikes only things hostile to it and never overrides
    /// its orders. Everything is off when falseShadeAmbushEnabled is off.
    /// </summary>
    public class RM_CompFalseShadeAmbusher : ThingComp
    {
        private Pawn lastVictim;

        public CompProperties_FalseShadeAmbusher Props => (CompProperties_FalseShadeAmbusher)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref lastVictim, "rmFalseShadeLastVictim");
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(System.Math.Max(1, Props.checkIntervalTicks)))
            {
                return;
            }
            if (!RM_CreatureBehaviorsSettings.falseShadeAmbushEnabled)
            {
                return;
            }
            if (!(parent is Pawn pawn) || !pawn.Spawned || pawn.Dead || pawn.Downed || pawn.InMentalState
                || pawn.Drafted || pawn.jobs == null)
            {
                return;
            }
            bool tame = pawn.Faction != null;
            JobDef cur = pawn.CurJobDef;

            if (IsIdle(cur, tame))
            {
                Pawn victim = FindVictim(pawn, tame);
                if (victim != null)
                {
                    Seize(pawn, victim);
                    return;
                }
            }

            if (!tame && TryEatVictim(pawn, cur))
            {
                return;
            }

            if (!tame && (cur == JobDefOf.GotoWander || cur == JobDefOf.Wait_Wander))
            {
                LieInWait(pawn);
            }
        }

        private static bool IsIdle(JobDef cur, bool tame)
        {
            if (cur == null || cur == JobDefOf.Wait || cur == JobDefOf.Wait_Wander || cur == JobDefOf.GotoWander
                || cur == JobDefOf.Wait_MaintainPosture)
            {
                return true;
            }
            // A tame one also answers hostiles while following/idling in a pen.
            return tame && cur == JobDefOf.FollowClose;
        }

        private Pawn FindVictim(Pawn pawn, bool tame)
        {
            float rangeSq = Props.strikeRangeCells * Props.strikeRangeCells;
            IReadOnlyList<Pawn> pawns = pawn.Map.mapPawns.AllPawnsSpawned;
            Pawn best = null;
            float bestSq = float.MaxValue;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn c = pawns[i];
                if (c == pawn || c.Dead || c.def == pawn.def || c.Flying || !c.RaceProps.IsFlesh)
                {
                    continue;
                }
                if (c.BodySize > Props.maxPreyBodySize)
                {
                    continue;
                }
                float d = (c.Position - pawn.Position).LengthHorizontalSquared;
                if (d > rangeSq || d >= bestSq)
                {
                    continue;
                }
                if (tame ? !pawn.HostileTo(c) : (c.Faction != null && c.Faction == pawn.Faction))
                {
                    continue;
                }
                best = c;
                bestSq = d;
            }
            return best;
        }

        private void Seize(Pawn pawn, Pawn victim)
        {
            ThingDef filth = Props.seizeFilth ?? DefDatabase<ThingDef>.GetNamedSilentFail("Filth_Sand");
            if (filth != null && Props.seizeFilthCount > 0)
            {
                FilthMaker.TryMakeFilth(victim.Position, pawn.Map, filth, Props.seizeFilthCount);
            }
            DamageDef dmg = Props.strikeDamage ?? DamageDefOf.Bite;
            float angle = (victim.Position - pawn.Position).ToVector3().AngleFlat();
            victim.TakeDamage(new DamageInfo(dmg, Props.strikeDamageRange.RandomInRange, 0f, angle, pawn));
            lastVictim = victim;

            if (victim.Faction == Faction.OfPlayer && victim.Spawned)
            {
                Messages.Message("The shadow " + victim.LabelShort + " stepped into was a "
                    + pawn.KindLabel + " — it has seized " + victim.Possessive() + ".",
                    new LookTargets(pawn), MessageTypeDefOf.ThreatSmall);
            }

            if (!victim.Dead && victim.Spawned)
            {
                Job attack = JobMaker.MakeJob(JobDefOf.AttackMelee, victim);
                attack.killIncappedTarget = true;
                attack.expiryInterval = 600;
                attack.checkOverrideOnExpire = true;
                pawn.jobs.StartJob(attack, JobCondition.InterruptForced, resumeCurJobAfterwards: false, cancelBusyStances: true);
            }
        }

        private bool TryEatVictim(Pawn pawn, JobDef cur)
        {
            if (lastVictim == null || !lastVictim.Dead)
            {
                return false;
            }
            Corpse corpse = lastVictim.Corpse;
            if (corpse == null || !corpse.Spawned || corpse.Map != pawn.Map
                || (corpse.Position - pawn.Position).LengthHorizontalSquared > 16f)
            {
                lastVictim = null;
                return false;
            }
            if (cur == JobDefOf.Ingest || pawn.needs?.food == null || pawn.needs.food.CurLevelPercentage > 0.9f)
            {
                return false;
            }
            if (!pawn.CanReserveAndReach(corpse, PathEndMode.Touch, Danger.Some))
            {
                return false;
            }
            Job eat = JobMaker.MakeJob(JobDefOf.Ingest, corpse);
            eat.count = 1;
            pawn.jobs.StartJob(eat, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
            return true;
        }

        private void LieInWait(Pawn pawn)
        {
            Map map = pawn.Map;
            RM_MapComponent_ShadeGrid grid = map.GetComponent<RM_MapComponent_ShadeGrid>();
            float here = grid?.ShadeAt(pawn.Position) ?? 0f;
            if (here <= Props.openGroundMaxShade)
            {
                Job wait = JobMaker.MakeJob(JobDefOf.Wait);
                wait.expiryInterval = Props.lieStillTicks;
                wait.checkOverrideOnExpire = true;
                pawn.jobs.StartJob(wait, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
                return;
            }
            float maxShade = Props.openGroundMaxShade;
            if (CellFinder.TryFindRandomReachableNearbyCell(pawn.Position, map, Props.relocateRadius,
                    TraverseParms.For(pawn), c => c.Standable(map) && (grid?.ShadeAt(c) ?? 0f) <= maxShade,
                    null, out IntVec3 open))
            {
                Job go = JobMaker.MakeJob(JobDefOf.Goto, open);
                go.locomotionUrgency = LocomotionUrgency.Walk;
                pawn.jobs.StartJob(go, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
            }
        }
    }
}
