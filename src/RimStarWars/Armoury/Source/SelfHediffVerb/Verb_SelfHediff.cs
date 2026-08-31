using System.Linq;
using RimWorld;
using Verse;

namespace SelfHediffVerb;

public class Verb_SelfHediff : Verb
{
    protected override bool TryCastShot()
    {
        if (verbProps is not VerbProperties_SelfHediff props)
        {
            Log.Error("Verb_SelfHediff must have VerbProperties_SelfHediff!");
            return false;
        }
        if (!CasterIsPawn)
        {
            return false;
        }
        CompApparelReloadable reloadableCompSource = ReloadableCompSource;
        CompVerbWithCooltime compVerbWithCooltime = EquipmentSource?.GetComp<CompVerbWithCooltime>();
        if (compVerbWithCooltime != null && !compVerbWithCooltime.CanBeUsed)
        {
            Messages.Message("SelfHediffVerb_CooltimeRemain".Translate(compVerbWithCooltime.remainCooltimeTicks.ToStringSecondsFromTicks("F0")), MessageTypeDefOf.RejectInput, false);
            return false;
        }
        if (reloadableCompSource != null && !reloadableCompSource.CanBeUsed(out string failReason))
        {
            return false;
        }
        reloadableCompSource?.UsedOnce();
        compVerbWithCooltime?.UsedOnce();
        BodyPartRecord targetPart = CasterPawn.health.hediffSet
            .GetNotMissingParts()
            .FirstOrFallback((BodyPartRecord p) => p.def == props.part);
        HediffComp_RemoveIfApparelDropped comp = CasterPawn.health.AddHediff(props.hediffDef, targetPart)
            .TryGetComp<HediffComp_RemoveIfApparelDropped>();
        if (comp != null && EquipmentSource is Apparel apparel)
        {
            comp.wornApparel = apparel;
        }
        return true;
    }
}
