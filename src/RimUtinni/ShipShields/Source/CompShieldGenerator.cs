using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // Bubble/kinetic field (shd:bubble-not-wall). A real subclass of
    // vanilla's CompProjectileInterceptor -- everything CheckIntercept,
    // hit-point draining, EMP handling, and the forcefield visuals already
    // do is reused as-is; this class only adds the collapse explosion and
    // exposes the mode gate the Harmony patch reads.
    public class CompShieldGenerator : CompProjectileInterceptor
    {
        private bool collapseExplosionArmed = true;

        // shd:shield-collapse-evacuate's alert half: "Shields that are
        // slowly failing due to an environmental stressor can predict and
        // alert to let the crew return and leave." Sampled every
        // PredictiveSampleIntervalTicks; a sustained hit-point decline is
        // linearly projected forward, and a single warning letter fires
        // once the projected time-to-failure crosses the threshold. This
        // reads the same currentHitPoints field the base class already
        // drains from combat/EMP/forced-collapse -- no new stressor tracking
        // invented, it just watches the number that already means "failing".
        private const int PredictiveSampleIntervalTicks = 250;
        private const int PredictiveWarnWithinTicks = 2500; // roughly 1 in-game hour
        private const float PredictiveRecoveryFraction = 0.6f;
        private int predictiveLastSampleTick = -1;
        private int predictiveLastSampleHitPoints = -1;
        private bool predictiveWarningActive;

        // Hides (does not override -- the base property is not virtual) the
        // base Props with our subclass so callers get the extra fields.
        public new CompProperties_ShieldGenerator Props => (CompProperties_ShieldGenerator)props;

        // Read by HarmonyPatches.Patch_CompProjectileInterceptor_CheckIntercept.
        // Defaults to active when no CompShieldModuleSwitch is present, so
        // this comp still works standalone.
        public bool BubbleModeActive
        {
            get
            {
                CompShieldModuleSwitch moduleSwitch = parent.GetComp<CompShieldModuleSwitch>();
                return moduleSwitch == null || moduleSwitch.CurrentMode == ShieldFieldMode.Bubble;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref predictiveLastSampleTick, "predictiveLastSampleTick", -1);
            Scribe_Values.Look(ref predictiveLastSampleHitPoints, "predictiveLastSampleHitPoints", -1);
            Scribe_Values.Look(ref predictiveWarningActive, "predictiveWarningActive", false);
        }

        public override void CompTick()
        {
            base.CompTick();

            if (ShipShieldsSettings.predictiveFailureAlertEnabled)
            {
                EvaluatePredictiveFailure();
            }

            if (currentHitPoints > 0)
            {
                collapseExplosionArmed = true;
                return;
            }

            if (!collapseExplosionArmed)
            {
                return;
            }

            collapseExplosionArmed = false;
            TriggerCollapseExplosion();
        }

        private void EvaluatePredictiveFailure()
        {
            if (!parent.IsHashIntervalTick(PredictiveSampleIntervalTicks))
            {
                return;
            }

            int hp = currentHitPoints;
            int maxHp = HitPointsMax;
            int nowTick = Find.TickManager.TicksGame;

            if (hp <= 0 || maxHp <= 0)
            {
                return;
            }

            if (predictiveLastSampleTick < 0)
            {
                predictiveLastSampleTick = nowTick;
                predictiveLastSampleHitPoints = hp;
                return;
            }

            int elapsed = nowTick - predictiveLastSampleTick;
            int dropped = predictiveLastSampleHitPoints - hp;
            predictiveLastSampleTick = nowTick;
            predictiveLastSampleHitPoints = hp;

            if (elapsed <= 0)
            {
                return;
            }

            if (dropped <= 0)
            {
                // Holding or recharging -- clear a standing warning only once
                // comfortably clear of the failure band, so it doesn't flap.
                if (predictiveWarningActive && hp >= maxHp * PredictiveRecoveryFraction)
                {
                    predictiveWarningActive = false;
                }
                return;
            }

            float declinePerTick = dropped / (float)elapsed;
            float ticksToFailure = hp / declinePerTick;

            if (predictiveWarningActive || ticksToFailure > PredictiveWarnWithinTicks)
            {
                return;
            }

            predictiveWarningActive = true;
            Find.LetterStack.ReceiveLetter(
                "Shield failing",
                parent.LabelCap + "'s field is degrading under sustained stress and is projected to "
                    + "collapse in roughly " + Mathf.RoundToInt(ticksToFailure).ToStringTicksToPeriod()
                    + ". Recommend the crew return to the hull and prepare to leave before it fails.",
                LetterDefOf.ThreatSmall,
                new TargetInfo(parent.Position, parent.Map));
        }

        private void TriggerCollapseExplosion()
        {
            if (!ShipShieldsSettings.collapseExplosionEnabled)
            {
                return;
            }

            if (parent?.Map == null)
            {
                return;
            }

            DamageDef damage = Props.collapseExplosionDamage ?? DamageDefOf.Bomb;
            int damAmount = Mathf.Max(1, Mathf.RoundToInt(Props.collapseExplosionDamageAmount * ShipShieldsSettings.collapseExplosionDamageMultiplier));
            GenExplosion.DoExplosion(
                center: parent.Position,
                map: parent.Map,
                radius: Props.collapseExplosionRadius,
                damType: damage,
                instigator: parent,
                damAmount: damAmount,
                chanceToStartFire: Props.collapseExplosionChanceToStartFire);
        }
    }
}
