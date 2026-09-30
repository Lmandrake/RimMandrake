// BLUEDESERT_MECHANICS_BUILD_1 §1 — the vhaulk's trigger-gated detonation.
//
// Ruled (the_blue_desert.md 2026-09-28 amendment (2); item §1): the
// cistern detonates ONLY on a heat-family killing blow — lightning comes free
// because WeatherEvent_LightningStrike.DoStrike explodes DamageDefOf.Flame —
// and a kinetic or cold kill leaves it intact. The ion trap: ANY EMP damage
// against a LIVING vhaulk detonates it at once, checked on hit, not on death.
//
// Engine seams (RimSage, decompiled 1.6, 2026-09-29):
//  - HediffComp_ExplodeOnDeath explodes in Notify_PawnKilled(), which has NO
//    DamageInfo (Pawn.DoKillSideEffects calls it before the pawn despawns).
//    The kill's DamageInfo first reaches hediff comps in
//    Notify_PawnDied(DamageInfo?, Hediff culprit), called from Pawn.Kill
//    after the corpse is placed. So this subclass suppresses the vanilla
//    Notify_PawnKilled blast and explodes from Notify_PawnDied instead, at
//    the corpse's PositionHeld/MapHeld.
//  - Pawn_HealthTracker.PostApplyDamage calls Kill() BEFORE the per-hediff
//    Notify_PawnPostApplyDamage loop, so a lethal blow never reaches the EMP
//    hook below; the hook only ever sees a living vhaulk — exactly the ruling.
//  - EMP (DamageDef EMP, harmsHealth false) on a flesh pawn is not stunned
//    (StunHandler skips non-mech EMP) but still passes Thing.TakeDamage ->
//    Pawn.PostApplyDamage -> the hediff loop, so the hook fires.
//
// Configurable in XML so the heat family is data, not code: heatDamageDefs
// (Flame, Burn) and heatCulpritHediffs (Heatstroke, Burn — a hediff death
// has a null DamageInfo and names the hediff as culprit, e.g. a burn wound
// that finishes a vital part).
//
// Mod Settings (RM_BlueDesertSettings): masterEnabled && nativeDetonations-
// Enabled off -> no vhaulk blast at all; vhaulkHeatGateEnabled off -> ANY
// death detonates (the pre-ruling ungated behaviour); vhaulkEmpTrapEnabled
// off -> EMP is ordinary damage.

using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.BlueDesert
{
    public class RM_HediffCompProperties_HeatGatedExplodeOnDeath : HediffCompProperties_ExplodeOnDeath
    {
        public List<DamageDef> heatDamageDefs;
        public List<HediffDef> heatCulpritHediffs;
        public List<DamageDef> empDamageDefs;

        public RM_HediffCompProperties_HeatGatedExplodeOnDeath()
        {
            compClass = typeof(RM_HediffComp_HeatGatedExplodeOnDeath);
        }

        public override IEnumerable<string> ConfigErrors(HediffDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (heatDamageDefs.NullOrEmpty())
            {
                yield return "RM_HediffCompProperties_HeatGatedExplodeOnDeath has no heatDamageDefs: nothing could ever detonate it.";
            }
        }
    }

    public class RM_HediffComp_HeatGatedExplodeOnDeath : HediffComp_ExplodeOnDeath
    {
        // Set by the EMP hook just before it kills the pawn, so the death
        // that follows detonates whatever its DamageInfo says.
        private bool empTriggered;

        private RM_HediffCompProperties_HeatGatedExplodeOnDeath GatedProps =>
            (RM_HediffCompProperties_HeatGatedExplodeOnDeath)props;

        private static bool DetonationsOn =>
            RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.nativeDetonationsEnabled;

        public override void Notify_PawnKilled()
        {
            // Deliberately NOT base: vanilla explodes here with no DamageInfo
            // to gate on. The blast moves to Notify_PawnDied below.
        }

        public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
        {
            bool detonate = DetonationsOn && (empTriggered
                || !RM_BlueDesertSettings.vhaulkHeatGateEnabled
                || IsHeatKill(dinfo, culprit));
            empTriggered = false;
            if (detonate)
            {
                Explode();
            }
            base.Notify_PawnDied(dinfo, culprit); // destroyBody handling only
        }

        public override void Notify_PawnPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.Notify_PawnPostApplyDamage(dinfo, totalDamageDealt);
            if (!DetonationsOn || !RM_BlueDesertSettings.vhaulkEmpTrapEnabled)
            {
                return;
            }
            Pawn pawn = Pawn;
            if (pawn == null || pawn.Dead || pawn.Destroyed || !IsEmp(dinfo.Def))
            {
                return;
            }
            empTriggered = true;
            pawn.Kill(dinfo);
        }

        private bool IsEmp(DamageDef def)
        {
            List<DamageDef> emp = GatedProps.empDamageDefs;
            if (emp.NullOrEmpty())
            {
                return def == DamageDefOf.EMP;
            }
            return emp.Contains(def);
        }

        private bool IsHeatKill(DamageInfo? dinfo, Hediff culprit)
        {
            if (dinfo.HasValue && dinfo.Value.Def != null
                && GatedProps.heatDamageDefs != null && GatedProps.heatDamageDefs.Contains(dinfo.Value.Def))
            {
                return true;
            }
            if (culprit != null && GatedProps.heatCulpritHediffs != null
                && GatedProps.heatCulpritHediffs.Contains(culprit.def))
            {
                return true;
            }
            return false;
        }

        private void Explode()
        {
            Pawn pawn = Pawn;
            if (pawn == null)
            {
                return;
            }
            Map map = pawn.MapHeld;
            if (map == null)
            {
                return; // died off-map (caravan, world pawn): nothing to glass
            }
            GenExplosion.DoExplosion(pawn.PositionHeld, map, Props.explosionRadius,
                Props.damageDef, pawn, Props.damageAmount);
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref empTriggered, "rmEmpTriggered", false);
        }
    }
}
