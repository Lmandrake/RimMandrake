using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    /// <summary>
    /// FEVERWOOD_RM_CAST_COMPLETION_1: the silloch's bark wait-ambush (fauna
    /// roster row 7: "It does not stalk. It waits, sometimes for days, and
    /// then it is simply attached to something."). Ban 3 binds: no native
    /// chase predators. The race is predator=false so the vanilla think tree
    /// never hunts with it; this comp is its only attack.
    ///
    /// Local to FeverWood on purpose. CreatureBehaviors'
    /// CompProperties_FalseShadeAmbusher lies on OPEN ground (the opposite of
    /// hiding on bark) and CompProperties_AquaticAmbusher only works in water.
    /// Shape copied from the false-shade comp, behaviour changed:
    ///  1. something small enough steps adjacent → one strike, then vanilla
    ///     AttackMelee to finish, with a short expiry;
    ///  2. a victim that gets more than leashCells away is let go (the job is
    ///     ended), so it never becomes a chase;
    ///  3. its own dead victim nearby and it is hungry → eat it where it fell
    ///     (the corpse is the readable sign; nothing vanishes);
    ///  4. idly wandering → go and press against the nearest tree trunk and
    ///     wait there.
    /// A tamed silloch only strikes things hostile to it. All of it is off
    /// when RM_FeverWoodSettings.sillochAmbushEnabled is off (it is then an
    /// ordinary wandering animal that never attacks unprovoked).
    ///
    ///   <li Class="RimMandrake.FeverWood.RM_CompProperties_SillochAmbush" />
    /// </summary>
    public class RM_CompProperties_SillochAmbush : CompProperties
    {
        public int checkIntervalTicks = 60;
        public float strikeRangeCells = 1.9f;
        public float maxPreyBodySize = 1.0f;
        public FloatRange strikeDamageRange = new FloatRange(8f, 14f);
        public DamageDef strikeDamage;
        public float leashCells = 4f;
        public float trunkSearchRadius = 10f;
        public int waitTicks = 2500;

        public RM_CompProperties_SillochAmbush()
        {
            compClass = typeof(RM_CompSillochAmbush);
        }
    }

    public class RM_CompSillochAmbush : ThingComp
    {
        private Pawn lastVictim;

        public RM_CompProperties_SillochAmbush Props => (RM_CompProperties_SillochAmbush)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref lastVictim, "rmSillochLastVictim");
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(System.Math.Max(1, Props.checkIntervalTicks)))
            {
                return;
            }
            if (!RM_FeverWoodSettings.sillochAmbushEnabled)
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

            if (cur == JobDefOf.AttackMelee && LetGoIfClear(pawn))
            {
                return;
            }

            if (IsIdle(cur, tame))
            {
                Pawn victim = FindVictim(pawn, tame);
                if (victim != null)
                {
                    Strike(pawn, victim);
                    return;
                }
            }

            if (!tame && TryEatVictim(pawn, cur))
            {
                return;
            }

            if (!tame && (cur == JobDefOf.GotoWander || cur == JobDefOf.Wait_Wander))
            {
                PressToBark(pawn);
            }
        }

        private static bool IsIdle(JobDef cur, bool tame)
        {
            if (cur == null || cur == JobDefOf.Wait || cur == JobDefOf.Wait_Wander || cur == JobDefOf.GotoWander
                || cur == JobDefOf.Wait_MaintainPosture)
            {
                return true;
            }
            return tame && cur == JobDefOf.FollowClose;
        }

        // Never a chase: once the struck victim is past the leash, end the
        // attack. Only our own ambush attack is ended; a manhunter state
        // (the crown alarm, or being hurt) is a mental state and is skipped
        // by the InMentalState gate above.
        private bool LetGoIfClear(Pawn pawn)
        {
            if (lastVictim == null || pawn.CurJob?.targetA.Thing != lastVictim)
            {
                return false;
            }
            float leash = Props.leashCells;
            if (lastVictim.Dead || !lastVictim.Spawned
                || (lastVictim.Position - pawn.Position).LengthHorizontalSquared <= leash * leash)
            {
                return false;
            }
            pawn.jobs.EndCurrentJob(JobCondition.InterruptForced);
            return true;
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

        private void Strike(Pawn pawn, Pawn victim)
        {
            DamageDef dmg = Props.strikeDamage ?? DamageDefOf.Cut;
            float angle = (victim.Position - pawn.Position).ToVector3().AngleFlat();
            victim.TakeDamage(new DamageInfo(dmg, Props.strikeDamageRange.RandomInRange, 0f, angle, pawn));
            lastVictim = victim;

            if (victim.Faction == Faction.OfPlayer && victim.Spawned)
            {
                Messages.Message("What " + victim.LabelShort + " took for bark was a " + pawn.KindLabel
                    + ". It has struck.", new LookTargets(pawn), MessageTypeDefOf.ThreatSmall);
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

        private void PressToBark(Pawn pawn)
        {
            Map map = pawn.Map;
            if (BesideTrunk(pawn.Position, map))
            {
                Job wait = JobMaker.MakeJob(JobDefOf.Wait);
                wait.expiryInterval = Props.waitTicks;
                wait.checkOverrideOnExpire = true;
                pawn.jobs.StartJob(wait, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
                return;
            }
            if (CellFinder.TryFindRandomReachableNearbyCell(pawn.Position, map, Props.trunkSearchRadius,
                    TraverseParms.For(pawn), c => c.Standable(map) && BesideTrunk(c, map), null, out IntVec3 bark))
            {
                Job go = JobMaker.MakeJob(JobDefOf.Goto, bark);
                go.locomotionUrgency = LocomotionUrgency.Walk;
                pawn.jobs.StartJob(go, JobCondition.InterruptForced, resumeCurJobAfterwards: false);
            }
        }

        // A tree, or one of the Fever Wood's great trunks, in an adjacent cell.
        private static bool BesideTrunk(IntVec3 cell, Map map)
        {
            for (int i = 0; i < 8; i++)
            {
                IntVec3 n = cell + GenAdj.AdjacentCells[i];
                if (!n.InBounds(map))
                {
                    continue;
                }
                List<Thing> things = n.GetThingList(map);
                for (int j = 0; j < things.Count; j++)
                {
                    ThingDef d = things[j].def;
                    if ((d.plant != null && d.plant.IsTree) || d.defName.Contains("FeverTrunk"))
                    {
                        return true;
                    }
                }
            }
            return false;
        }
    }
}
