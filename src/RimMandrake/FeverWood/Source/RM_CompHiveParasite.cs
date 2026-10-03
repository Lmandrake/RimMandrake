using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_HIVE_PARASITE_CHAMBER_1. Chamber 2 of 3 (owner ruling
    // 2026-09-22): "a parasite the ants tolerate or cannot see — something
    // feeding on the hive itself. The horror chamber, and the one that can be
    // an ally: whatever eats ants is not your enemy."
    //
    // The glomvar is NOT a predator in vanilla's sense (race predator=false),
    // so vanilla never sends it after a colonist; this comp is its only hunt,
    // and its only prey is the host hive's own residents (pawns whose race
    // answers `hostTag` via RM_AlarmResponderExtension). It eats what it kills
    // through ordinary corpse-eating (CarnivoreAnimal food type). The hive
    // cannot perceive it: its race carries RM_ReactionUnseenExtension, so a
    // bite never rings the alarm and it is never "noticed".
    //
    //   - Hungry (food below `hungerThreshold`) and off its own cooldown: it
    //     takes the nearest calm host resident within `huntRadius`.
    //   - The ally half: when the host hive raises an alarm nearby (someone
    //     else is fighting the ants), it goes into a feeding frenzy for
    //     `frenzyTicks`, ignoring hunger and cooldown, and falls on rallied
    //     residents — the player's fight becomes its meal.
    // Faction pawns (tamed glomvar, raiding-column kurreth) are never part of
    // this. Gated by RM_FeverWoodSettings.antHiveParasiteChamberEnabled.
    public class RM_CompProperties_HiveParasite : CompProperties
    {
        public string hostTag = "KurrethHive";

        public float huntRadius = 12f;

        public float hungerThreshold = 0.4f;

        /// <summary>Minimum ticks between two ordinary (non-frenzy) hunts. INVENTED: a day — one ant a day keeps a 20-ant hive alive for weeks.</summary>
        public int huntCooldownTicks = 60000;

        public float frenzyRadius = 20f;

        public int frenzyTicks = 2500;

        public int checkIntervalTicks = 250;

        public RM_CompProperties_HiveParasite()
        {
            compClass = typeof(RM_CompHiveParasite);
        }
    }

    public class RM_CompHiveParasite : ThingComp
    {
        private int lastHuntTick = -999999;

        private int frenzyUntilTick = -1;

        public RM_CompProperties_HiveParasite Props => (RM_CompProperties_HiveParasite)props;

        public bool InFrenzy => Find.TickManager.TicksGame < frenzyUntilTick;

        public void StartFrenzy()
        {
            frenzyUntilTick = Find.TickManager.TicksGame + Props.frenzyTicks;
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            if (!RM_FeverWoodSettings.antHiveParasiteChamberEnabled || !parent.Spawned
                || !parent.IsHashIntervalTick(Props.checkIntervalTicks, delta))
            {
                return;
            }

            Pawn self = parent as Pawn;
            if (self == null || self.Dead || self.Downed || self.Faction != null || self.InMentalState
                || self.jobs == null || !self.Awake())
            {
                return;
            }

            if (self.CurJobDef == JobDefOf.AttackMelee || self.CurJobDef == JobDefOf.Ingest)
            {
                return; // already killing or eating
            }

            bool frenzy = InFrenzy;
            if (!frenzy)
            {
                if (self.needs?.food == null || self.needs.food.CurLevelPercentage > Props.hungerThreshold)
                {
                    return;
                }
                if (Find.TickManager.TicksGame - lastHuntTick < Props.huntCooldownTicks)
                {
                    return;
                }
            }

            Pawn prey = FindPrey(self, frenzy);
            if (prey == null)
            {
                return;
            }

            lastHuntTick = Find.TickManager.TicksGame;
            Job job = JobMaker.MakeJob(JobDefOf.AttackMelee, prey);
            job.killIncappedTarget = true;
            job.expiryInterval = 2000;
            self.jobs.StartJob(job, JobCondition.InterruptForced);
        }

        private Pawn FindPrey(Pawn self, bool frenzy)
        {
            float radius = frenzy ? Props.frenzyRadius : Props.huntRadius;
            float best = radius * radius;
            Pawn found = null;
            IReadOnlyList<Pawn> pawns = self.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p == self || p.Dead || p.Faction != null)
                {
                    continue;
                }

                if (!RM_ReactionResponders.Answers(p, Props.hostTag))
                {
                    continue;
                }

                if (!frenzy && p.InMentalState)
                {
                    continue; // outside a frenzy it takes only the calm ones
                }

                int d = (p.Position - self.Position).LengthHorizontalSquared;
                if (d < best && self.CanReach(p, PathEndMode.Touch, Danger.Deadly))
                {
                    best = d;
                    found = p;
                }
            }
            return found;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastHuntTick, "rmParasiteLastHunt", -999999);
            Scribe_Values.Look(ref frenzyUntilTick, "rmParasiteFrenzyUntil", -1);
        }

        public override string CompInspectStringExtra()
        {
            return InFrenzy ? "Feeding frenzy: the hive is distracted." : null;
        }

        // Subscribed in RM_FeverWoodMod beside RM_HiveSealing.OnAlarm.
        public static void OnAlarm(RM_ReactionEvent evt)
        {
            if (!RM_FeverWoodSettings.antHiveParasiteChamberEnabled || evt?.Map == null)
            {
                return;
            }

            IReadOnlyList<Pawn> pawns = evt.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                RM_CompHiveParasite comp = pawns[i]?.TryGetComp<RM_CompHiveParasite>();
                if (comp == null || pawns[i].Faction != null || comp.Props.hostTag != evt.Tag)
                {
                    continue;
                }

                float r = comp.Props.frenzyRadius;
                if ((pawns[i].Position - evt.OriginCell).LengthHorizontalSquared <= r * r)
                {
                    comp.StartFrenzy();
                }
            }
        }
    }
}
