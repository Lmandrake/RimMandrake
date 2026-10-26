using HarmonyLib;
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

        // Read by SyncFieldShutdown (the authoritative gate) and by
        // HarmonyPatches.Patch_CompProjectileInterceptor_CheckIntercept (a second gate for when the
        // shutDown field cannot be resolved). Defaults to active when no CompShieldModuleSwitch is
        // present, so this comp still works standalone.
        public bool BubbleModeActive
        {
            get
            {
                CompShieldModuleSwitch moduleSwitch = parent.GetComp<CompShieldModuleSwitch>();
                return moduleSwitch == null || moduleSwitch.CurrentMode == ShieldFieldMode.Bubble;
            }
        }

        // SHIELDGEN_FIX_RECHARGE_UNPOWERED: the base class adds HitPointsPerInterval (1) every
        // rechargeHitPointsIntervalTicks with no power check, so once the def ticks (2965619d82)
        // an unpowered or flicked-off generator recharged for free. Mirrors vanilla
        // CompGravshipShieldGenerator's ShouldCharge gate (no unpowered drain: a drain to 0
        // would fire the collapse explosion, which is for a forced collapse, not a power cut).
        private CompPowerTrader powerTrader;
        private CompPowerTrader PowerTrader => powerTrader ?? (powerTrader = parent.GetComp<CompPowerTrader>());

        protected override int HitPointsPerInterval
        {
            get
            {
                CompPowerTrader power = PowerTrader;
                return power == null || power.PowerOn ? base.HitPointsPerInterval : 0;
            }
        }

        // SHIELDGEN_DECIDE_INTERCEPT_UNPOWERED (delegated: design): an unpowered bubble blocks
        // nothing. "Just use power for fuel ... Power does the trick" (owner, ship_shields_deep_design.md
        // thermal-veil row), and the other three fields already stop when PowerOn is false
        // (ShieldHazardUtility.IsPowered, CompShieldCryoEnvelope, CompShieldThermalVeil). Vanilla's
        // Active getter has no power test and is not virtual, so the base's own private shutDown
        // flag is driven instead: it already gates CheckIntercept, damage absorption, bombardment,
        // the drawn bubble and the "Shut down" inspect line. Only a shutdown THIS comp set is ever
        // cleared (unpoweredShutDown), so another cause's shutdown is never undone. Hit points are
        // kept (no drain, no collapse explosion: a power cut is not a forced collapse) and the field
        // returns at the hit points it had once power is back.
        //
        // SHIELDGEN_FIX_NONBUBBLE_MODE_INTERCEPTS: the same shutdown is held while another field mode
        // (Thermal/Particulate/Cryo) is selected. The Harmony prefix only gates CheckIntercept; vanilla's
        // CheckBombardmentIntercept, BombardmentCanStartFireAt, PostDraw and the ambient sustainer all read
        // Active, so a thermal-configured generator still stopped orbital bombardment and drew and hummed a
        // bubble. "only the currently-selected field should ever intercept anything" (shd:loadout-tradeoff).
        private static readonly AccessTools.FieldRef<CompProjectileInterceptor, bool> ShutDownRef = ResolveShutDownRef();
        // True while shutDown is set by THIS comp (unpowered or not in Bubble mode). The save key keeps its
        // original name so saves written before the mode gate still load the flag.
        private bool unpoweredShutDown;

        private static AccessTools.FieldRef<CompProjectileInterceptor, bool> ResolveShutDownRef()
        {
            try
            {
                return AccessTools.FieldRefAccess<CompProjectileInterceptor, bool>("shutDown");
            }
            catch (System.Exception e)
            {
                Log.Error("[RimMandrake.Utinni.ShipShields] CompProjectileInterceptor.shutDown not found; an unpowered bubble will keep intercepting: " + e.Message);
                return null;
            }
        }

        // True when the generator has power (or no power comp at all, so the comp still works standalone).
        public bool FieldPowered
        {
            get
            {
                CompPowerTrader power = PowerTrader;
                return power == null || power.PowerOn;
            }
        }

        private void SyncFieldShutdown()
        {
            if (ShutDownRef == null)
            {
                return;
            }
            ref bool shutDown = ref ShutDownRef(this);
            if (!FieldPowered || !BubbleModeActive)
            {
                if (!shutDown)
                {
                    shutDown = true;
                    unpoweredShutDown = true;
                }
            }
            else if (unpoweredShutDown)
            {
                shutDown = false;
                unpoweredShutDown = false;
            }
        }

        // Vanilla's other shutdown cause (a destroyed lord) sets the same flag. If it lands while this comp
        // holds its own (unpowered / non-Bubble) shutdown, the flag now belongs to the lord: forget ours so
        // power returning or a switch back to Bubble does not undo it.
        public override void Notify_LordDestroyed()
        {
            base.Notify_LordDestroyed();
            unpoweredShutDown = false;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref unpoweredShutDown, "unpoweredShutDown", false);
            // SHIELDGEN_FIX_COLLAPSE_REARM_ON_LOAD: unsaved, a load inside the hp==0 window (until the
            // next recharge interval) re-armed it to true and the generator exploded a second time.
            Scribe_Values.Look(ref collapseExplosionArmed, "collapseExplosionArmed", true);
            Scribe_Values.Look(ref predictiveLastSampleTick, "predictiveLastSampleTick", -1);
            Scribe_Values.Look(ref predictiveLastSampleHitPoints, "predictiveLastSampleHitPoints", -1);
            Scribe_Values.Look(ref predictiveWarningActive, "predictiveWarningActive", false);
        }

        public override void CompTick()
        {
            SyncFieldShutdown();
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

            // -1 is the base class's "never initialised" value (PostPostMake did not run, e.g. a comp added
            // to an existing building by a def change); the base recharges it upward. Only 0, reached by
            // being drained, is a collapse. Disarm here: the first recharge clamps -1+1 to exactly 0, which
            // must not read as a collapse either.
            if (currentHitPoints < 0)
            {
                collapseExplosionArmed = false;
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
