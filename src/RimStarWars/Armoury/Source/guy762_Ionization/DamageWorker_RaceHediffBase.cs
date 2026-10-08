using RimMandrake.StarWars.Armoury;
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

    // Mechanoids get an extra "stunned = true" after the hediff pass (DamageWorker_Ionization).
    protected virtual bool StunsVictim => false;

    public override DamageResult Apply(DamageInfo dinfo, Thing thing)
    {
        ModExtension_HediffGiver modExtension = dinfo.Def.GetModExtension<ModExtension_HediffGiver>();
        DamageResult result = base.Apply(dinfo, thing);
        // MOD_OPTIONS_RETROFIT_1: the kernel's gate is off when the mechanic is off, which skips the whole block
        // below, the mechanoid stun included, so the hit still deals its ordinary injury and nothing more.
        Pawn pawn = thing as Pawn;
        StatDef resist = modExtension?.hediffResistanceStat;
        RSW_IonKernel.Plan plan = RSW_IonKernel.Decide(RSW_ArmourySettings.ionDamageEnabled, modExtension != null, modExtension?.hediffToAdd != null,
            pawn != null && AppliesTo(pawn), StunsVictim,
            modExtension != null ? modExtension.severityFixed : 0f, RSW_ArmourySettings.ionSeverity, resist != null, resist != null ? resist.defaultBaseValue : 0f,
            () => pawn.GetStatValue(resist), modExtension != null && modExtension.severityVariesBySize, pawn != null ? pawn.BodySize : 1f,
            modExtension == null || modExtension.hediffAppliedToWholeBody, result.parts != null ? result.parts.Count : 0);
        if (plan.Applies)
        {
            HediffDef hediffToAdd = modExtension.hediffToAdd;
            if (plan.Hediffs > 0)
            {
                if (modExtension.hediffAppliedToWholeBody)
                {
                    Hediff hediff = HediffMaker.MakeHediff(hediffToAdd, pawn);
                    hediff.Severity = plan.Severity;
                    pawn.health.AddHediff(hediff, null, dinfo);
                }
                else
                {
                    foreach (BodyPartRecord part in result.parts)
                    {
                        Hediff hediff = HediffMaker.MakeHediff(hediffToAdd, pawn, part);
                        hediff.Severity = plan.Severity;
                        pawn.health.AddHediff(hediff, part, dinfo);
                    }
                }
            }
            if (plan.Stun)
            {
                result.stunned = true;
            }
        }
        return result;
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
    protected override bool StunsVictim => true;
}
