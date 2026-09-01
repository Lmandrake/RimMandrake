using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompHighlyFlammable : ThingComp
{
	public CompProperties_HighlyFlammable Props => (CompProperties_HighlyFlammable)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Expected O, but got Unknown
		((ThingComp)this).CompTickInterval(delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (((Thing)val).Map != null && FireUtility.IsBurning((Thing)(object)val))
		{
			BattleLogEntry_DamageTaken val2 = null;
			if (val != null)
			{
				val2 = new BattleLogEntry_DamageTaken(val, RulePackDefOf.DamageEvent_Fire, val);
				Find.BattleLog.Add((LogEntry)(object)val2);
			}
			DamageDef val3 = Named(Props.hediffToInflict);
			float num = 15f;
			Thing parent2 = (Thing)(object)base.parent;
			((Thing)base.parent).TakeDamage(new DamageInfo(val3, num, 0f, -1f, parent2, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false)).AssociateWithLog((LogEntry_DamageResult)(object)val2);
		}
	}

	public static DamageDef Named(string defName)
	{
		return DefDatabase<DamageDef>.GetNamed(defName, true);
	}
}
