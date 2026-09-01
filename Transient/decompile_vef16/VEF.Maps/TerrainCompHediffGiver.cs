using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF.Maps;

public class TerrainCompHediffGiver : TerrainComp
{
	public TerrainCompProperties_HediffGiver Props => (TerrainCompProperties_HediffGiver)props;

	public override void CompTick()
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		base.CompTick();
		foreach (Pawn item in GridsUtility.GetThingList(parent.Position, parent.Map).OfType<Pawn>())
		{
			HediffData hediffData = null;
			if (item.RaceProps.Humanlike)
			{
				IEnumerable<HediffData> enumerable = Props.hediffsForHumanlike.Where((HediffData x) => x.hediff != null);
				hediffData = ((enumerable != null) ? GenCollection.RandomElement<HediffData>(enumerable) : null);
			}
			else if (item.IsAnimal)
			{
				IEnumerable<HediffData> enumerable2 = Props.hediffsForAnimals.Where((HediffData x) => x.hediff != null);
				hediffData = ((enumerable2 != null) ? GenCollection.RandomElement<HediffData>(enumerable2) : null);
			}
			if (hediffData == null || item.health.hediffSet.GetHediffCount(hediffData.hediff) >= hediffData.hediffLimit)
			{
				continue;
			}
			if (hediffData.randomBodyParts)
			{
				List<BodyPartRecord> list = item.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null).ToList();
				if (list != null && list.Count > 0)
				{
					BodyPartRecord val = GenCollection.RandomElement<BodyPartRecord>((IEnumerable<BodyPartRecord>)list);
					Hediff val2 = HediffMaker.MakeHediff(hediffData.hediff, item, val);
					item.health.AddHediff(val2, val, (DamageInfo?)null, (DamageResult)null);
				}
			}
			else
			{
				item.health.AddHediff(hediffData.hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}

	public override void PostExposeData()
	{
		base.PostExposeData();
	}
}
