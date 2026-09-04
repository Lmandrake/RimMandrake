using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace KoltoTank;

public class CompKoltoTank : ThingComp
{
    public float fillPct;

    private Building_KoltoTank.KoltoTankState state = Building_KoltoTank.KoltoTankState.Empty;

    public CompProperties_KoltoTank Props => (CompProperties_KoltoTank)props;

    public float waterfillspeed => Props.waterfillspeed;

    public Building_KoltoTank.KoltoTankState State => state;

    public float FillPct => fillPct;

    public void StartFilling()
    {
        state = Building_KoltoTank.KoltoTankState.StartFilling;
        fillPct = 0f;
    }

    public void SetFull()
    {
        state = Building_KoltoTank.KoltoTankState.Full;
        fillPct = 1f;
    }

    public void SetEmpty()
    {
        state = Building_KoltoTank.KoltoTankState.Empty;
        fillPct = 0f;
    }

    public bool WillHeal(Hediff hediff)
    {
        if (hediff?.def == null)
        {
            return false;
        }
        if (!hediff.def.everCurableByItem || hediff.def.countsAsAddedPartOrImplant)
        {
            return false;
        }
        if (hediff.def.chronic || hediff.def == HediffDefOf.BloodLoss)
        {
            return true;
        }
        return hediff is Hediff_Injury injury && !injury.IsPermanent();
    }

    public void HealPawnInjuries(Pawn pawn)
    {
        if (pawn?.health == null)
        {
            return;
        }
        bool healed = false;
        foreach (Hediff hediff in pawn.health.hediffSet.hediffs.ToList())
        {
            if (WillHeal(hediff))
            {
                HealthUtility.Cure(hediff);
                healed = true;
                break;
            }
            if (hediff is Hediff_MissingPart missingPart && missingPart.IsFresh)
            {
                missingPart.IsFresh = false;
                pawn.health.Notify_HediffChanged(missingPart);
                healed = true;
                break;
            }
        }
        if (healed)
        {
            Messages.Message("Kolto_InjuryHealed".Translate(pawn.Named("PAWN")), pawn, MessageTypeDefOf.PositiveEvent);
        }
    }

    public void UpdatePowerState(CompPowerTrader powerTraderComp, CompPower powerComp)
    {
        if (powerTraderComp == null || powerComp == null || powerComp.Props == null)
        {
            Log.Error("KoltoTank: Power components are not properly initialized!");
        }
        else if (state == Building_KoltoTank.KoltoTankState.Full)
        {
            powerTraderComp.PowerOutput = -powerComp.Props.PowerConsumption;
        }
        else if (state == Building_KoltoTank.KoltoTankState.Empty)
        {
            powerTraderComp.PowerOutput = -powerComp.Props.idlePowerDraw;
        }
    }

    public void DrawLiquid(Vector3 drawPos, float fillPercent)
    {
        if (Props == null || Props.waterDrawSize == Vector2.zero)
        {
            return;
        }
        Rot4 rotation = parent.Rotation;
        Vector3 center = drawPos + Props.waterDrawCenter.RotatedBy(rotation.AsAngle);
        Rot4 barRotation = parent.Rotation;
        barRotation.Rotate(RotationDirection.Clockwise);
        GenDraw.FillableBarRequest request = default;
        request.center = center;
        request.size = Props.waterDrawSize;
        request.fillPercent = fillPercent;
        request.filledMat = SolidColorMaterials.SimpleSolidColorMaterial(Props.liquidColor);
        request.unfilledMat = SolidColorMaterials.SimpleSolidColorMaterial(Color.clear);
        request.margin = 0.1f;
        request.rotation = barRotation;
        GenDraw.DrawFillableBar(request);
    }
}
