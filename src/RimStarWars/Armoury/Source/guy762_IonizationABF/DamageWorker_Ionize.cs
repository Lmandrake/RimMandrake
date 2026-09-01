using ArtificialBeings;
using guy762_Ionization;
using RimWorld;
using Verse;

namespace guy762_IonizationABF;

/// <summary>
/// Ported from guy762.mm.kotorcore's own AdditionalMods/MHC/Assemblies/
/// guy762_IonizationABF.dll (gated IfModActive="Killathon.ArtificialBeings",
/// which is active on this mod list -- found and ported as part of
/// WEAPONS_DONOR_RETIREMENT_1's AdditionalMods absorption pass).
/// Namespace and class names kept identical to the source so
/// Absorbed_AdditionalMods/kotorcore/MHC's Patch_IonDamageWorker.xml (which
/// points workerClass at "guy762_IonizationABF.DamageWorker_Ionize") needs
/// zero rewriting.
///
/// The difference from the base (non-ABF) guy762_Ionization workers this mod
/// already ports: those check RaceProps.IsMechanoid; this checks
/// RaceProps.IsMechanoid OR ABF_Utils.IsArtificial(pawn), so ABF's Synstruct
/// pawns are recognised as artificial for ion-damage hediff purposes too.
/// </summary>
public class DamageWorker_Ionize : DamageWorker_AddInjury
{
    public override DamageResult Apply(DamageInfo dinfo, Thing thing)
    {
        HediffDef hediffToAdd = null;
        ModExtension_HediffGiver modExtension = dinfo.Def.GetModExtension<ModExtension_HediffGiver>();
        if (modExtension != null)
        {
            hediffToAdd = modExtension.hediffToAdd;
        }

        DamageResult result = base.Apply(dinfo, thing);

        if (thing is Pawn pawn && hediffToAdd != null &&
            (pawn.RaceProps.IsMechanoid || ABF_Utils.IsArtificial(pawn)))
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
                    Hediff hediff = HediffMaker.MakeHediff(hediffToAdd, pawn, null);
                    hediff.Severity = severity;
                    pawn.health.AddHediff(hediff, null, dinfo, null);
                }
                else
                {
                    foreach (BodyPartRecord part in result.parts)
                    {
                        Hediff hediff = HediffMaker.MakeHediff(hediffToAdd, pawn, part);
                        hediff.Severity = severity;
                        pawn.health.AddHediff(hediff, part, dinfo, null);
                    }
                }
            }

            result.stunned = true;
        }

        return result;
    }
}

/// <summary>
/// Same source file's other class -- used by DamageDefs this pass did not
/// find any active DamageDef pointing at (guy762_RangedDamage_ion etc. all
/// resolve to DamageWorker_Ionize above, per Patch_IonDamageWorker.xml).
/// Ported anyway since it shipped in the same DLL and costs nothing extra;
/// unlike DamageWorker_Ionize it never sets `stunned`.
/// </summary>
public class DamageWorker_AllDroids : DamageWorker_AddInjury
{
    public override DamageResult Apply(DamageInfo dinfo, Thing thing)
    {
        HediffDef hediffToAdd = null;
        ModExtension_HediffGiver modExtension = dinfo.Def.GetModExtension<ModExtension_HediffGiver>();
        if (modExtension != null)
        {
            hediffToAdd = modExtension.hediffToAdd;
        }

        DamageResult result = base.Apply(dinfo, thing);

        if (thing is Pawn pawn && hediffToAdd != null &&
            (pawn.RaceProps.IsMechanoid || ABF_Utils.IsArtificial(pawn)))
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
                    Hediff hediff = HediffMaker.MakeHediff(hediffToAdd, pawn, null);
                    hediff.Severity = severity;
                    pawn.health.AddHediff(hediff, null, dinfo, null);
                }
                else
                {
                    foreach (BodyPartRecord part in result.parts)
                    {
                        Hediff hediff = HediffMaker.MakeHediff(hediffToAdd, pawn, part);
                        hediff.Severity = severity;
                        pawn.health.AddHediff(hediff, part, dinfo, null);
                    }
                }
            }
        }

        return result;
    }
}
