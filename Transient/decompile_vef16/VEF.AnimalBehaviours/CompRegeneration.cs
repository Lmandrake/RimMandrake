using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompRegeneration : ThingComp
{
	public CompProperties_Regeneration Props => (CompProperties_Regeneration)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		if (!AnimalBehaviours_Settings.flagRegeneration || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.rateInTicks, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val.health == null)
		{
			return;
		}
		List<Hediff_Injury> injuries = GetInjuries(val, Props.bodypart);
		if (injuries.Count <= 0 || (Props.needsSun && (((Thing)val).Map == null || !SanguophageUtility.InSunlight(((Thing)val).Position, ((Thing)val).Map))) || (Props.needsWater && (((Thing)val).Map == null || !GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map).IsWater)))
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
		else if (Props.healOneTendOne)
		{
			Hediff_Injury obj2 = GenCollection.RandomElement<Hediff_Injury>(injuries.Where((Hediff_Injury x) => ((Hediff)x).TendableNow(false)));
			if (obj2 != null)
			{
				((Hediff)obj2).Tended(Props.tendMin, Props.tendMax, 0);
			}
			Hediff_Injury obj3 = GenCollection.RandomElement<Hediff_Injury>((IEnumerable<Hediff_Injury>)injuries);
			if (obj3 != null)
			{
				((Hediff)obj3).Heal(Props.healAmount);
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
