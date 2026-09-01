using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompHediffGiver : ThingComp
{
	public CompProperties_HediffGiver Props => (CompProperties_HediffGiver)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickRate, delta) || !((Thing)base.parent).Spawned)
		{
			return;
		}
		IReadOnlyList<Pawn> allPawnsSpawned = ((Thing)base.parent).Map.mapPawns.AllPawnsSpawned;
		for (int num = allPawnsSpawned.Count - 1; num >= 0; num--)
		{
			Pawn val = allPawnsSpawned[num];
			if (!((float)IntVec3Utility.DistanceToSquared(((Thing)val).Position, ((Thing)base.parent).Position) > Props.radius * Props.radius))
			{
				float num2 = Props.severityIncrease;
				if (!GenList.NullOrEmpty<StatDef>((IList<StatDef>)Props.stats))
				{
					for (int i = 0; i < Props.stats.Count; i++)
					{
						num2 *= StatExtension.GetStatValue((Thing)(object)val, Props.stats[i], true, -1);
					}
				}
				Hediff firstHediffOfDef = val.health.hediffSet.GetFirstHediffOfDef(Props.hediffDef, false);
				if (firstHediffOfDef != null)
				{
					Hediff obj = firstHediffOfDef;
					obj.Severity += num2;
				}
				else
				{
					firstHediffOfDef = HediffMaker.MakeHediff(Props.hediffDef, val, (BodyPartRecord)null);
					firstHediffOfDef.Severity = num2;
					val.health.AddHediff(firstHediffOfDef, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
			}
		}
	}
}
