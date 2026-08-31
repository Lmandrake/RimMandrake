using RimWorld;
using Verse;

namespace guy762_Ionization;

// The 5 kotorcore DamageWorker_<Race> classes (Humanlikes/Animals/Insectoids/
// Mechanoids/Organics) were each a byte-identical copy of this method except
// for the one RaceProps predicate -- factored into a shared base rather than
// re-duplicated 5 times, same observable behavior per race, exact def names
// preserved for the 5 leaf classes the absorbed XML's Class= attributes need.
public abstract class DamageWorker_RaceHediffBase : DamageWorker_AddInjury
{
    protected abstract bool AppliesTo(Pawn pawn);

    public override DamageResult Apply(DamageInfo dinfo, Thing thing)
    {
        HediffDef hediffToAdd = null;
        ModExtension_HediffGiver modExtension = dinfo.Def.GetModExtension<ModExtension_HediffGiver>();
        if (modExtension != null)
        {
            hediffToAdd = modExtension.hediffToAdd;
        }
        DamageResult result = base.Apply(dinfo, thing);
        if (thing is Pawn pawn && hediffToAdd != null && AppliesTo(pawn))
        {
            float severity = modExtension.severityFixed;
            if (modExtension.hediffResistanceStat != null)
            {
                float statValue = pawn.GetStatValue(modExtension.hediffResistanceStat);
                severity = modExtension.hediffResistanceStat.defaultBaseValue > 0f
                    ? severity * statValue
                    : severity * (1f - statValue);
            }
            if (severity > 0f)
            {
                if (modExtension.severityVariesBySize)
                {
                    severity /= pawn.BodySize;
                }
                if (modExtension.hediffAppliedToWholeBody)
                {
                    Hediff hediff = HediffMaker.MakeHediff(hediffToAdd, pawn);
                    hediff.Severity = severity;
                    pawn.health.AddHediff(hediff, null, dinfo);
                }
                else
                {
                    foreach (BodyPartRecord part in result.parts)
                    {
                        Hediff hediff = HediffMaker.MakeHediff(hediffToAdd, pawn, part);
                        hediff.Severity = severity;
                        pawn.health.AddHediff(hediff, part, dinfo);
                    }
                }
            }
            OnAppliedTo(result, pawn);
        }
        return result;
    }

    protected virtual void OnAppliedTo(DamageResult result, Pawn pawn)
    {
    }
}

public class DamageWorker_Humanlikes : DamageWorker_RaceHediffBase
{
    protected override bool AppliesTo(Pawn pawn) => pawn.RaceProps.Humanlike;
}

public class DamageWorker_Animals : DamageWorker_RaceHediffBase
{
    protected override bool AppliesTo(Pawn pawn) => pawn.RaceProps.Animal;
}

public class DamageWorker_Insectoids : DamageWorker_RaceHediffBase
{
    protected override bool AppliesTo(Pawn pawn) => pawn.RaceProps.Insect;
}

public class DamageWorker_Mechanoids : DamageWorker_RaceHediffBase
{
    protected override bool AppliesTo(Pawn pawn) => pawn.RaceProps.IsMechanoid;
}

public class DamageWorker_Organics : DamageWorker_RaceHediffBase
{
    protected override bool AppliesTo(Pawn pawn) => pawn.RaceProps.IsFlesh;
}

// Mechanoids get an extra "stunned = true" after the hediff pass -- the one
// behavioral difference among the 5 race workers in the decompiled source.
public class DamageWorker_Ionization : DamageWorker_Mechanoids
{
    protected override void OnAppliedTo(DamageResult result, Pawn pawn)
    {
        result.stunned = true;
    }
}
