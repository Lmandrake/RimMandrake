using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Warcasket
{
    // WARCASKET_SUIT_CLASS_1 — the compound-failure mechanic. Owner ruling,
    // verbatim: "very resistant to extreme temps + vacuum + toxins... very
    // slow, bulky, prone to failure under compound threats — a primitive
    // tank around a person." This is the "prone to failure under compound
    // threats" half, built as a real mechanism rather than flavor text:
    //
    //   1. Every checkIntervalTicks (CompTickRare cadence), count how many
    //      of the suit's three hazard classes are ACTUALLY active against
    //      the wearer right now:
    //        vacuum       — Room.Vacuum above vacuumThreshold (0.5f matches
    //                       vanilla's own Region.cs ConcernedByVacuum gate)
    //        extreme temp — ambient temperature outside a wide safe band
    //        toxin        — standing on polluted ground, or a ToxicFallout
    //                       game condition active on the map
    //   2. One hazard alone NEVER fails the suit — a primitive tank holds
    //      against one threat fine. Two or more stacked is what "compound"
    //      means, and only then does a failure chance get rolled at all.
    //   3. A damaged suit fails more often (its own HitPoints fraction
    //      scales the roll up to 1.6x when nearly wrecked) — degradation
    //      compounds on itself, same as the ruling's own framing implies.
    //   4. A failure damages the suit's own HP (never destroys it outright
    //      mid-hazard — a broken suit stranding someone IN a compound
    //      hazard is worse than a merely damaged one) and gives the wearer
    //      a real, tendable RM_WarcasketBreach hediff scaled by how many
    //      hazards were stacked.
    //
    // Mod Settings: masterEnabled / compoundFailureEnabled. Off degrades to
    // "the suit never fails" (MOD_OPTIONS_RETROFIT_1: off never strands or
    // harms anyone) — the suit keeps its stat coverage either way, only the
    // risk mechanic is removed.
    public class RM_CompProperties_WarcasketIntegrity : CompProperties
    {
        public int checkIntervalTicks = 250;
        public float vacuumThreshold = 0.5f;
        public float extremeColdThresholdC = -60f;
        public float extremeHeatThresholdC = 70f;

        // Failure chance PER CHECK once exactly 2 hazards are active.
        public float baseFailureChancePerCheck = 0.015f;

        // Added per hazard beyond the second (so 3 active hazards = base +
        // 1x this, not base again).
        public float failureChancePerExtraHazard = 0.02f;

        public int integrityDamagePerFailure = 12;
        public float wearerHediffSeverityPerFailure = 0.08f;

        public RM_CompProperties_WarcasketIntegrity()
        {
            compClass = typeof(RM_CompWarcasketIntegrity);
        }
    }

    public class RM_CompWarcasketIntegrity : ThingComp
    {
        public RM_CompProperties_WarcasketIntegrity Props => (RM_CompProperties_WarcasketIntegrity)props;

        public override void CompTickRare()
        {
            base.CompTickRare();

            if (!RM_WarcasketSettings.masterEnabled || !RM_WarcasketSettings.compoundFailureEnabled)
            {
                return; // MOD_OPTIONS_RETROFIT_1: off means the suit simply never fails
            }

            if (!(parent is Apparel apparel) || apparel.Wearer == null || !apparel.Wearer.Spawned)
            {
                return;
            }

            Pawn wearer = apparel.Wearer;
            Map map = wearer.MapHeld;
            if (map == null)
            {
                return;
            }

            int hazards = CountActiveHazards(wearer, map);
            if (hazards < 2)
            {
                return; // a single hazard is exactly what this suit is built to shrug off
            }

            float chance = Props.baseFailureChancePerCheck
                + Props.failureChancePerExtraHazard * (hazards - 2);

            int maxHp = parent.MaxHitPoints > 0 ? parent.MaxHitPoints : 1;
            float hpFrac = Mathf.Clamp01((float)parent.HitPoints / maxHp);
            // A badly damaged suit fails up to 1.6x more often than a pristine one.
            chance *= Mathf.Lerp(1.6f, 1f, hpFrac);
            chance = Mathf.Clamp01(chance);

            if (!Rand.Chance(chance))
            {
                return;
            }

            TriggerFailure(wearer, hazards);
        }

        private int CountActiveHazards(Pawn wearer, Map map)
        {
            int n = 0;

            Room room = wearer.Position.GetRoom(map);
            if (room != null && room.Vacuum > Props.vacuumThreshold)
            {
                n++;
            }

            float temp = wearer.AmbientTemperature;
            if (temp <= Props.extremeColdThresholdC || temp >= Props.extremeHeatThresholdC)
            {
                n++;
            }

            bool toxicGround = wearer.Position.IsPolluted(map);
            bool toxicFallout = map.gameConditionManager != null
                && map.gameConditionManager.ConditionIsActive(GameConditionDefOf.ToxicFallout);
            if (toxicGround || toxicFallout)
            {
                n++;
            }

            return n;
        }

        private void TriggerFailure(Pawn wearer, int hazardCount)
        {
            int dmg = Props.integrityDamagePerFailure + Rand.RangeInclusive(0, hazardCount * 4);
            // Never destroy the suit outright from a failure roll — a wearer
            // stranded suitless mid-compound-hazard is a worse outcome than a
            // damaged suit that still (mostly) works.
            parent.HitPoints = Mathf.Max(1, parent.HitPoints - dmg);

            HealthUtility.AdjustSeverity(wearer, RM_WarcasketDefOf.RM_WarcasketBreach,
                Props.wearerHediffSeverityPerFailure * hazardCount);

            Messages.Message(
                wearer.LabelShortCap + "'s warcasket fails under compound strain (" + hazardCount + " hazards at once)!",
                wearer, MessageTypeDefOf.NegativeHealthEvent);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WarcasketSettings.masterEnabled || !RM_WarcasketSettings.compoundFailureEnabled)
            {
                return null;
            }

            if (!(parent is Apparel apparel) || apparel.Wearer == null || !apparel.Wearer.Spawned)
            {
                return null;
            }

            Map map = apparel.Wearer.MapHeld;
            if (map == null)
            {
                return null;
            }

            int hazards = CountActiveHazards(apparel.Wearer, map);
            return hazards >= 2
                ? "Compound strain: " + hazards + " hazards active at once — integrity at risk."
                : null;
        }
    }
}
