using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WASTELAND_BRINE_BATTERY_DISCHARGE_1. wasteland.md §4: "Hypersaline
    // pools over mineral beds are half a voltaic cell; what lives in them
    // runs on ion gradients and discharges them as defense. The pool you
    // want to mine has an owner, and the owner is a capacitor."
    //
    // Checked this repo's own XML first (RUT_BrineBattery.xml's own header)
    // for an absorbed EMP/zap/shock CompProperties class — none exists in
    // the active mod set (the only named candidate, SW_Electrictick,
    // belongs to a dormant mod not in ModsConfig.xml). RimSage's own
    // search_defs/search_source (this pass) confirms the same for the
    // engine's own C#: no CompProperties_*Emp*/*Shock*/*Zap*/*Discharge*
    // class exists anywhere in the decompiled tree either — every hit was
    // temperature/power-transmission machinery (CompProperties_
    // TemperatureDamaged/TempControl/TemperatureRuinable), nothing that
    // reads as "zap whoever just hit me." So this is genuinely new C#,
    // built to this assembly's own established house style rather than a
    // new architecture: PostPostApplyDamage(DamageInfo, float), the exact
    // hook RM_CompWoundLink already relies on and already documents as
    // "confirmed real, fires synchronously from Thing.TakeDamage after
    // damage (and armor) has already been resolved."
    //
    // Trigger is "took damage", not "the pool got mined" — there is no
    // engine mining mechanic on a water-terrain pool (mining targets
    // Building_MineableRock, not terrain a pawn merely sits in), so
    // "handled roughly" is read as its buildable, general case: anyone who
    // hurts this pawn at close range gets shocked, whether that's a melee
    // swing, a point-blank shot, or a tamer's rough handling gone wrong —
    // covers the sheet's "reached into a promising pool for the wrong
    // reason" without inventing a fictional mining-terrain hook.
    //
    //   <comps>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_DefensiveDischarge" />
    //   </comps>
    public class RM_CompDefensiveDischarge : ThingComp
    {
        private int lastDischargeTick = -999999;

        public RM_CompProperties_DefensiveDischarge Props => (RM_CompProperties_DefensiveDischarge)props;

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);

            if (!RM_CreatureBehaviorsSettings.brineBatteryDischargeEnabled)
            {
                return; // mod option: defensive discharge disabled
            }

            if (!(parent is Pawn self) || !self.Spawned || self.Dead || self.health == null || self.Map == null)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            if (now - lastDischargeTick < Props.dischargeCooldownTicks)
            {
                return; // still recharging from the last shock
            }

            Thing attacker = dinfo.Instigator;
            if (attacker == null || attacker == self || attacker.Destroyed || !attacker.Spawned || attacker.Map != self.Map)
            {
                return; // no instigator (e.g. environmental damage) or nothing left to shock
            }

            float distSq = (attacker.Position - self.Position).LengthHorizontalSquared;
            if (distSq > Props.dischargeRange * Props.dischargeRange)
            {
                return; // a shooter standing off at range never touches the water
            }

            float mult = UnityEngine.Mathf.Max(0f, RM_CreatureBehaviorsSettings.brineBatteryDischargeMultiplier);
            float amount = Props.dischargeAmount * mult;
            if (amount <= 0f)
            {
                return; // mod option: discharge strength scaled to zero
            }

            DamageDef damageDef = Props.dischargeDamageDef ?? DamageDefOf.EMP;
            DamageInfo shock = new DamageInfo(damageDef, amount, 0f, -1f, self);
            attacker.TakeDamage(shock);

            lastDischargeTick = now;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastDischargeTick, "lastDischargeTick", -999999);
        }
    }
}
