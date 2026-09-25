using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // GREENTIDE_WASP_SWARM_1's sting curve ("negligible once, frightening
    // twenty times") needs every sting to accumulate on ONE hediff instance,
    // not spawn a fresh instance per hit. RimSage-verified this pass against
    // the decompiled engine (Verse/Pawn_HealthTracker.cs): AddHediff always
    // calls hediffSet.AddDirect with no merge check, and vanilla's own
    // DamageDef.hediff pipeline (Verse/DamageWorker_AddGlobal.cs) uses that
    // same AddHediff — so a plain <hediff> DamageDef, or Tool.hediff's
    // Verb_MeleeApplyHediff (which additionally applies to EVERY not-missing
    // body part per hit — wrong shape for one whole-body irritation), both
    // give N coexisting instances, not one accumulating severity.
    //
    // This worker is DamageWorker_AddGlobal's own shape (apply a hediff to the
    // whole pawn, no wound, no blood — see that class) with the merge
    // DamageWorker_AddGlobal is missing: find the pawn's existing hediff of
    // this DamageDef's hediff first, and add severity to it instead of
    // creating a second instance.
    public class RM_DamageWorker_StingAccumulate : DamageWorker
    {
        public override DamageResult Apply(DamageInfo dinfo, Thing thing)
        {
            DamageResult result = new DamageResult();

            if (!(thing is Pawn pawn) || pawn.health == null || dinfo.Def.hediff == null)
            {
                return result;
            }

            Hediff existing = pawn.health.hediffSet.GetFirstHediffOfDef(dinfo.Def.hediff);
            if (existing != null)
            {
                existing.Severity = Mathf.Min(existing.Severity + dinfo.Amount, existing.def.maxSeverity);
                result.AddHediff(existing);
            }
            else
            {
                Hediff added = pawn.health.AddHediff(dinfo.Def.hediff, null, dinfo);
                added.Severity = Mathf.Min(dinfo.Amount, added.def.maxSeverity);
                result.AddHediff(added);
            }

            return result;
        }
    }
}
