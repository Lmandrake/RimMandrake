using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_HighlyFlammable : HediffComp
{
	public HediffCompProperties_HighlyFlammable Props => (HediffCompProperties_HighlyFlammable)(object)base.props;

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Expected O, but got Unknown
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.tickInterval, delta))
		{
			return;
		}
		Pawn pawn = ((Hediff)base.parent).pawn;
		bool flag = (FireUtility.IsBurning((Thing)(object)pawn) && !Props.sunlightBurns) || (Props.sunlightBurns && ((Thing)((Hediff)base.parent).pawn).Map != null && SanguophageUtility.InSunlight(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map));
		if (((Thing)pawn).Map != null && flag)
		{
			BattleLogEntry_DamageTaken val = null;
			if (pawn != null)
			{
				val = new BattleLogEntry_DamageTaken(pawn, RulePackDefOf.DamageEvent_Fire, pawn);
				Find.BattleLog.Add((LogEntry)(object)val);
			}
			DamageDef damageToInflict = Props.damageToInflict;
			float damageAmount = Props.damageAmount;
			Thing pawn2 = (Thing)(object)((Hediff)base.parent).pawn;
			((Thing)((Hediff)base.parent).pawn).TakeDamage(new DamageInfo(damageToInflict, damageAmount, 0f, -1f, pawn2, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false)).AssociateWithLog((LogEntry_DamageResult)(object)val);
		}
	}
}
