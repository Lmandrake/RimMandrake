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

        public override void CompTick()
        {
            base.CompTick();

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
