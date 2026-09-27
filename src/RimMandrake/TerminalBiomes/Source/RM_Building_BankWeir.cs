using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_CHANNEL_CURRENT_1 §4. The weir. Two vanilla mechanics carry
    // almost the whole spec with no new job/WorkGiver needed, by design:
    //   - "tend the weir (empty the hopper)": arrested things just sit on
    //     the weir's own cell as ordinary spawned Things once
    //     CompChannelArrester stops the carry there — vanilla hauling
    //     already lets a colonist pick them up. There is no separate
    //     hopper inventory; "the hopper's stock" IS whatever is physically
    //     sitting there.
    //   - "re-drive stakes" / weir maintenance: ordinary HitPoints decay
    //     (Wear, below) plus vanilla WorkGiver_Repair. A weir/stake with
    //     <building><repairable>true</repairable></building> already gets
    //     repaired by any colonist assigned to it — no new job needed.
    // What this class DOES own: the slow HP gnaw, and — Q3, "breach at
    // default" — the breach cascade itself (spill, stake snap, silt
    // revert) when an undersurge catches a weir already run down.
    public class RM_Building_BankWeir : Building
    {
        private const int WearIntervalTicks = 2000;
        private const int WearAmount = 1;
        private const float BreachHpFraction = 0.5f;
        private const int BreachDurationTicks = 2500; // "over ~an hour" — §4
        private const float StakeCascadeRadius = 15f;
        private const int StakeCascadeStepTicks = 150;

        // The Compact's own pre-placed instance (§4 tier note: "their weir
        // never breaches — it is tended, which is the lesson"). Set by
        // RM_GenStep_TwilightChannels right after spawning that one weir;
        // every player-built weir leaves this false.
        public bool neverBreaches;

        private bool breaching;
        private int breachEndTick;
        private List<Thing> cascadeStakes;
        private List<int> cascadeFireTicks;

        private CompChannelArrester arrester;
        private CompChannelArrester Arrester => arrester ?? (arrester = GetComp<CompChannelArrester>());

        protected override void Tick()
        {
            base.Tick();
            if (!RM_TerminalBiomesSettings.ChannelCurrentActive)
            {
                return;
            }

            if (breaching)
            {
                TickBreach();
                return;
            }

            if (this.IsHashIntervalTick(WearIntervalTicks) && HitPoints > 1)
            {
                HitPoints = System.Math.Max(1, HitPoints - WearAmount); // "the current's ordinary gnaw"
            }

            if (!neverBreaches && this.IsHashIntervalTick(600))
            {
                Map map = Map;
                RM_MapComponent_ChannelCurrent current = map?.GetComponent<RM_MapComponent_ChannelCurrent>();
                bool untended = HitPoints < MaxHitPoints * BreachHpFraction;
                if (current != null && current.SurgeActive && untended)
                {
                    Breach();
                }
            }
        }

        // Q3: "breach at default" — the untended-weir-meets-flood cascade.
        // (a) the hopper's stock spills: disabling the arrester lets the
        //     next occupant scan (<=250 ticks) pick up anything sitting on
        //     this cell as an ordinary drift occupant again.
        // (b)+(c)+(d) below.
        private void Breach()
        {
            breaching = true;
            breachEndTick = Find.TickManager.TicksGame + BreachDurationTicks;
            if (Arrester != null)
            {
                Arrester.Active = false;
            }

            Messages.Message("RM_ChannelWeirBreach".Translate(LabelShortCap), this, MessageTypeDefOf.ThreatBig);

            ScheduleStakeCascade();
            RevertNearbySiltTraps();
        }

        private void TickBreach()
        {
            if (cascadeFireTicks != null)
            {
                int now = Find.TickManager.TicksGame;
                for (int i = cascadeFireTicks.Count - 1; i >= 0; i--)
                {
                    if (now < cascadeFireTicks[i])
                    {
                        continue;
                    }
                    Thing stake = cascadeStakes[i];
                    // (c) "an HP cascade on a timer... stoppable at any
                    // stake a colonist reaches in time" — a stake already
                    // destroyed or already repaired back to full between
                    // scheduling and firing is simply skipped, which is the
                    // "stoppable" half: a colonist who re-drove it in time
                    // saves it.
                    if (stake != null && !stake.Destroyed && stake.HitPoints < stake.MaxHitPoints)
                    {
                        stake.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, stake.MaxHitPoints));
                    }
                    cascadeStakes.RemoveAt(i);
                    cascadeFireTicks.RemoveAt(i);
                }
            }

            if (Find.TickManager.TicksGame >= breachEndTick)
            {
                breaching = false;
                if (Arrester != null)
                {
                    Arrester.Active = true; // the breach ends; the weir catches again once repaired past the threshold on its own next check
                }
                cascadeStakes = null;
                cascadeFireTicks = null;
            }
        }

        // (c) the stake-line downstream snaps stake by stake. Simplified to
        // "every RM_BankStake within radius", staggered by distance rather
        // than a true flow-order walk — a build-time simplification, not a
        // ruling; the spec only specifies the shape ("an HP cascade on a
        // timer"), not the exact ordering algorithm.
        private void ScheduleStakeCascade()
        {
            cascadeStakes = new List<Thing>();
            cascadeFireTicks = new List<int>();
            if (Map == null)
            {
                return;
            }
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(Position, Map, StakeCascadeRadius, true))
            {
                if (t.def == RM_ThingDefOf.RM_BankStake)
                {
                    float dist = t.Position.DistanceTo(Position);
                    int fireTick = Find.TickManager.TicksGame + Mathf_RoundToInt(dist) * StakeCascadeStepTicks;
                    cascadeStakes.Add(t);
                    cascadeFireTicks.Add(fireTick);
                }
            }
        }

        // (d) the silt-trap's terrain bonus reverts.
        private void RevertNearbySiltTraps()
        {
            if (Map == null)
            {
                return;
            }
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(Position, Map, StakeCascadeRadius, true))
            {
                if (t is RM_Building_SiltTrap trap)
                {
                    trap.Clog();
                }
            }
        }

        private static int Mathf_RoundToInt(float f)
        {
            return UnityEngine.Mathf.RoundToInt(f);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref neverBreaches, "neverBreaches", false);
            Scribe_Values.Look(ref breaching, "breaching", false);
            Scribe_Values.Look(ref breachEndTick, "breachEndTick", 0);
            Scribe_Collections.Look(ref cascadeStakes, "cascadeStakes", LookMode.Reference);
            Scribe_Collections.Look(ref cascadeFireTicks, "cascadeFireTicks", LookMode.Value);
        }
    }
}
