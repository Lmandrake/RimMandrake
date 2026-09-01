using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class Gibblets
{
	public static void SpawnGibblets(Pawn pawn, IntVec3 centerPos, Map map, int bloodMin = 10, int bloodMax = 20, int gibbletMin = 1, int gibbletMax = 3, float bloodChance = 1f, float gibbletChance = 1f, float randomOrganChance = 0f, float skullChance = 0f)
	{
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		bool flag = Rand.Chance(bloodChance);
		bool num = Rand.Chance(gibbletChance) && flag;
		bool flag2 = Rand.Chance(randomOrganChance);
		bool flag3 = Rand.Chance(skullChance);
		if (flag)
		{
			int num2 = (int)((float)Rand.RangeInclusive(bloodMin, bloodMax) * pawn.BodySize);
			object obj;
			if (pawn == null)
			{
				obj = null;
			}
			else
			{
				RaceProperties raceProps = pawn.RaceProps;
				obj = ((raceProps != null) ? raceProps.BloodDef : null);
			}
			ThingDef val = (ThingDef)obj;
			if (val != null)
			{
				FilthMaker.TryMakeFilth(centerPos, map, val, num2, (FilthSourceFlags)0, true);
			}
		}
		if (num)
		{
			int num3 = Rand.RangeInclusive(gibbletMin, gibbletMax);
			if (pawn.RaceProps?.meatDef != null)
			{
				for (int i = 0; i < num3; i++)
				{
					Thing val2 = ((!pawn.RaceProps.IsMechanoid) ? ThingMaker.MakeThing(pawn.RaceProps.meatDef, (ThingDef)null) : ((!Rand.Chance(0.2f)) ? ThingMaker.MakeThing(ThingDefOf.Steel, (ThingDef)null) : ThingMaker.MakeThing(ThingDefOf.ComponentIndustrial, (ThingDef)null)));
					val2.stackCount = (int)Mathf.Max(1f, (float)Rand.RangeInclusive(-1, 2) * pawn.BodySize);
					IntVec3 val3 = centerPos + new IntVec3(Rand.Range(-1, 1), 0, Rand.Range(-1, 1));
					GenSpawn.Spawn(val2, val3, map, (WipeMode)0);
				}
			}
		}
		int num4;
		if (pawn == null)
		{
			num4 = 0;
		}
		else
		{
			RaceProperties raceProps2 = pawn.RaceProps;
			num4 = ((((raceProps2 != null) ? new bool?(raceProps2.Humanlike) : ((bool?)null)) == true) ? 1 : 0);
		}
		if (((uint)num4 & (flag2 ? 1u : 0u)) != 0)
		{
			List<ThingDef> source = new List<ThingDef>(4)
			{
				BSDefs.Heart,
				BSDefs.Liver,
				BSDefs.Lung,
				BSDefs.Kidney
			};
			IEnumerable<BodyPartRecord> bodyOrgans = pawn.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null);
			IEnumerable<ThingDef> enumerable = source.Where((ThingDef x) => bodyOrgans.Any((BodyPartRecord y) => ((Def)y.def).defName == ((Def)x).defName));
			if (enumerable.Any())
			{
				GenSpawn.Spawn(ThingMaker.MakeThing(GenCollection.RandomElement<ThingDef>(enumerable), (ThingDef)null), centerPos, map, (WipeMode)0);
			}
		}
		if (flag3 && ModsConfig.IdeologyActive)
		{
			GenSpawn.Spawn(ThingMaker.MakeThing(ThingDefOf.Skull, (ThingDef)null), centerPos, map, (WipeMode)0);
		}
	}
}
