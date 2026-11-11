using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// The thing Patch_Thing_Position_Wake finds with TryGetComp, so the wake fires exactly once per cell a tiered pawn actually
    /// enters, driven by the same Thing.Position assignment vanilla's own PathFollower already makes (Verse/AI/Pawn_PathFollower.cs
    /// TryEnterNextPathCell: "this.pawn.Position = nextCell;") - event-driven, not a scan.
    ///
    /// BIG_CREATURES_DESIGN_WALLS_AND_SLOTS §5.7: it also carries the creature's restlessness meter (saved, on the inspect panel)
    /// and the walls-and-slots inspect line (§5.9). The meter is the comp's only periodic work: every RestlessIntervalTicks, and
    /// nothing at all while the rule or its temperament switch is off. Only big creatures carry this comp, so only they pay.
    /// </summary>
    public class CompTitanicWake : ThingComp
    {
        public const int RestlessIntervalTicks = 250;
        private const int BreakoutCooldownTicks = 2500;

        /// <summary>0..1; 1 = the full walls-and-slots rule applies even to a calm creature.</summary>
        public float restless;
        private int lastBreakout = -999999;

        public void Notify_EnteredCell()
        {
            Pawn pawn = parent as Pawn;
            // TITAN_WAKE_FIXES_1 (B3.8): no ground wake while airborne (1.6 Pawn.Flying).
            if (pawn == null || !pawn.Spawned || pawn.Map == null || pawn.Flying)
            {
                return;
            }
            TitanicTier tier = TitanicTierUtility.GetTier(pawn);
            if (tier == TitanicTier.None)
            {
                return;
            }
            TitanicWakeProcessor.ProcessFootprint(pawn, tier);
        }

        public override void CompTick()
        {
            if (!RM_HugeThingsSettings.TemperamentActive) return;
            if (!parent.IsHashIntervalTick(RestlessIntervalTicks)) return;
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed || TitanicTierUtility.GetTier(pawn) == TitanicTier.None) return;
            int p = WallsSlotsUtility.Passage(pawn);
            District d = pawn.Position.GetDistrict(pawn.Map);
            bool confined = d != null && WallsSlots.Confined(d.CellCount, d.TouchesMapEdge, p);
            bool hungry = pawn.needs?.food != null && pawn.needs.food.CurCategory >= HungerCategory.Hungry;
            float before = restless;
            restless = WallsSlots.RestlessStep(restless, confined, hungry, RestlessIntervalTicks);
            if (restless >= 1f && before < 1f) WallsSlotsUtility.Say(pawn, "RM_WallsSlots_Restless".Translate());
            if (restless >= 1f && confined) TryBreakOut(pawn, d);
        }

        /// <summary>At 100% restless and still shut in, the creature goes for somewhere outside its district; the path start then
        /// meets the wall and the walls-and-slots rule decides (break, smash, or held and pacing).</summary>
        private void TryBreakOut(Pawn pawn, District here)
        {
            int now = Find.TickManager.TicksGame;
            if (now - lastBreakout < BreakoutCooldownTicks && now >= lastBreakout) return;
            JobDef cur = pawn.CurJobDef;
            if (pawn.Drafted || pawn.InMentalState || (cur != null && cur != JobDefOf.Wait_Wander && cur != JobDefOf.GotoWander && cur != JobDefOf.Wait)) return;
            lastBreakout = now;
            Map map = pawn.Map;
            for (int i = 0; i < 20; i++)
            {
                // not a reachable-cell finder: the point is a cell it cannot reach
                IntVec3 c = pawn.Position + new IntVec3(Rand.RangeInclusive(-30, 30), 0, Rand.RangeInclusive(-30, 30));
                if (!c.InBounds(map) || !c.Standable(map)) continue;
                District there = c.GetDistrict(map);
                if (there == null || there == here) continue;
                Job job = JobMaker.MakeJob(JobDefOf.Goto, c);
                job.locomotionUrgency = LocomotionUrgency.Walk;
                pawn.jobs.StartJob(job, JobCondition.InterruptForced);
                return;
            }
        }

        public override string CompInspectStringExtra()
        {
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || !RM_HugeThingsSettings.WallsSlotsActive || WallsSlotsUtility.Breadth(pawn) <= 1) return null;
            string s = WallsSlotsUtility.CreatureLine(pawn);
            if (RM_HugeThingsSettings.TemperamentActive)
                s += "\n" + "RM_WallsSlots_Restlessness".Translate((restless * 100f).ToString("0"));
            return s;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref restless, "rmRestless", 0f);
            Scribe_Values.Look(ref lastBreakout, "rmLastBreakout", -999999);
            if (!WallsSlots.Finite(restless) || restless < 0f || restless > 1f) restless = 0f;
        }
    }
}
