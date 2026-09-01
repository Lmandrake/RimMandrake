using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF.Maps;

public class TerrainComp_Healer : TerrainComp
{
	public TerrainCompProperties_Healer Props => (TerrainCompProperties_Healer)props;

	public override void CompTick()
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		base.CompTick();
		foreach (Pawn item in GridsUtility.GetThingList(parent.Position, parent.Map).OfType<Pawn>())
		{
			Hediff val = FirstInjuryToThreat(item);
			if (val != null)
			{
				val.Heal(Props.amountToHeal);
				item.health.Notify_HediffChanged(val);
			}
		}
	}

	public Hediff FirstInjuryToThreat(Pawn pawn)
	{
		List<Hediff_Injury> list = new List<Hediff_Injury>();
		pawn.health.hediffSet.GetHediffs<Hediff_Injury>(ref list, (Predicate<Hediff_Injury>)null);
		List<Hediff> list2 = new List<Hediff>();
		List<Hediff> list3 = new List<Hediff>();
		foreach (Hediff_Injury item in list)
		{
			HediffComp_GetsPermanent val = HediffUtility.TryGetComp<HediffComp_GetsPermanent>((Hediff)(object)item);
			if (val == null || !val.IsPermanent)
			{
				list2.Add((Hediff)(object)item);
			}
			else if (val != null && val.IsPermanent)
			{
				list3.Add((Hediff)(object)item);
			}
		}
		if (GenCollection.Any<Hediff>(list2))
		{
			return GenCollection.MinBy<Hediff, float>((IEnumerable<Hediff>)list2, (Func<Hediff, float>)((Hediff x) => x.BleedRate));
		}
		if (Props.curePermanent && GenCollection.Any<Hediff>(list3))
		{
			return GenCollection.MinBy<Hediff, float>((IEnumerable<Hediff>)list3, (Func<Hediff, float>)((Hediff x) => x.Part.def.GetMaxHealth(pawn) - pawn.health.hediffSet.GetPartHealth(x.Part)));
		}
		return null;
	}

	public override void PostExposeData()
	{
		base.PostExposeData();
	}
}
