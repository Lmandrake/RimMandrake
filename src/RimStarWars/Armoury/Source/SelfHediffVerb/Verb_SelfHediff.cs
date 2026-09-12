using System.Linq;
using RimMandrake.StarWars.Armoury;
using RimWorld;
using Verse;

namespace SelfHediffVerb;

public class Verb_SelfHediff : Verb
{
    protected override bool TryCastShot()
    {
        // MOD_OPTIONS_RETROFIT_1: a false here is the verb's ordinary
        // "the shot did not happen" answer — no ammo spent, no cooldown
        // started, no hediff applied.
        if (!RSW_ArmourySettings.selfHediffVerbEnabled)
        {
            return false;
        }
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
