using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_StageByVacuum : HediffComp
{
	public HediffCompProperties_StageByVacuum Props => (HediffCompProperties_StageByVacuum)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((Hediff)base.parent).pawn, 500, delta))
		{
			return;
		}
		if (((Thing)((Hediff)base.parent).pawn).Position != IntVec3.Invalid)
		{
			Map map = ((Thing)((Hediff)base.parent).pawn).Map;
			if (map != null && MapGenUtility.BiomeAt(map, ((Thing)((Hediff)base.parent).pawn).Position)?.inVacuum == true)
			{
				if (Props.vacuumResistanceInArmorDisablesHediff && !Props.reverseVacuumResistanceEffects)
				{
					if (!(((HediffComp)this).Pawn.VacuumResistanceFromArmor() > Props.vacuumResistanceValueToDisable))
					{
						Pawn_HealthTracker health = ((HediffComp)this).Pawn.health;
						object obj;
						if (health == null)
						{
							obj = null;
						}
						else
						{
							HediffSet hediffSet = health.hediffSet;
							obj = ((hediffSet != null) ? hediffSet.GetFirstHediffOfDef(InternalDefOf.VacskinGland, false) : null);
						}
						if (obj == null)
						{
							goto IL_0108;
						}
					}
					((Hediff)base.parent).Severity = Props.notVacuumStageIndex;
					return;
				}
				goto IL_0108;
			}
		}
		if (Props.vacuumResistanceInArmorDisablesHediff && Props.reverseVacuumResistanceEffects)
		{
			if (!(((HediffComp)this).Pawn.VacuumResistanceFromArmor() > Props.vacuumResistanceValueToDisable))
			{
				Pawn_HealthTracker health2 = ((HediffComp)this).Pawn.health;
				object obj2;
				if (health2 == null)
				{
					obj2 = null;
				}
				else
				{
					HediffSet hediffSet2 = health2.hediffSet;
					obj2 = ((hediffSet2 != null) ? hediffSet2.GetFirstHediffOfDef(InternalDefOf.VacskinGland, false) : null);
				}
				if (obj2 == null)
				{
					goto IL_0193;
				}
			}
			((Hediff)base.parent).Severity = Props.vacuumStageIndex;
			return;
		}
		goto IL_0193;
		IL_0108:
		((Hediff)base.parent).Severity = Props.vacuumStageIndex;
		return;
		IL_0193:
		((Hediff)base.parent).Severity = Props.notVacuumStageIndex;
	}
}
