using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Regeneration : HediffComp
{
	public HediffCompProperties_Regeneration Props => (HediffCompProperties_Regeneration)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.rateInTicks, delta))
		{
			return;
		}
		Pawn pawn = ((Hediff)base.parent).pawn;
		if (pawn.health == null)
		{
			return;
		}
		List<Hediff_Injury> injuries = GetInjuries(pawn, Props.bodypart);
		if (injuries.Count <= 0 || (Props.needsSun && (((Thing)pawn).Map == null || !SanguophageUtility.InSunlight(((Thing)pawn).Position, ((Thing)pawn).Map))) || (Props.needsWater && (((Thing)pawn).Map == null || !GridsUtility.GetTerrain(((Thing)pawn).Position, ((Thing)pawn).Map).IsWater)))
		{
			return;
		}
		if (Props.healAll)
		{
			if (Props.onlyTendButNotHeal)
			{
				foreach (Hediff_Injury item in injuries)
				{
					if (((Hediff)item).TendableNow(false))
					{
						((Hediff)item).Tended(Props.tendMin, Props.tendMax, 0);
					}
				}
				return;
			}
			{
				foreach (Hediff_Injury item2 in injuries)
				{
					((Hediff)item2).Heal(Props.healAmount);
				}
				return;
			}
		}
		if (Props.onlyTendButNotHeal)
		{
			Hediff_Injury obj = GenCollection.RandomElement<Hediff_Injury>(injuries.Where((Hediff_Injury x) => ((Hediff)x).TendableNow(false)));
			if (obj != null)
			{
				((Hediff)obj).Tended(Props.tendMin, Props.tendMax, 0);
			}
		}
		else
		{
			((Hediff)GenCollection.RandomElement<Hediff_Injury>((IEnumerable<Hediff_Injury>)injuries)).Heal(Props.healAmount);
		}
	}

	public List<Hediff_Injury> GetInjuries(Pawn pawn, BodyPartDef bodypart)
	{
		List<Hediff_Injury> list = new List<Hediff_Injury>();
		for (int i = 0; i < pawn.health.hediffSet.hediffs.Count; i++)
		{
			Hediff obj = pawn.health.hediffSet.hediffs[i];
			Hediff_Injury val = (Hediff_Injury)(object)((obj is Hediff_Injury) ? obj : null);
			if (val != null && (bodypart == null || ((Hediff)val).Part.def == bodypart) && (!Props.onlyBleeding || ((Hediff)val).Bleeding))
			{
				list.Add(val);
			}
		}
		return list;
	}
}
