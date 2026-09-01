using System.Linq;
using RimWorld;
using Verse;
using Verse.Sound;

namespace VEF.Hediffs;

public class HediffComp_DamageAura : HediffComp_Draw
{
	private Sustainer sustainer;

	public HediffCompProperties_DamageAura Props => ((HediffComp)this).props as HediffCompProperties_DamageAura;

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (sustainer == null)
		{
			sustainer = SoundStarter.TrySpawnSustainer(Props.sustainer, SoundInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn));
		}
		Sustainer obj = sustainer;
		if (obj != null)
		{
			obj.Maintain();
		}
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		if (!Gen.IsHashIntervalTick((Thing)(object)((HediffComp)this).Pawn, Props.ticksBetween, delta))
		{
			return;
		}
		foreach (Thing item in GenCollection.Except<Thing>(GenRadial.RadialDistinctThingsAround(((Thing)((HediffComp)this).Pawn).Position, ((Thing)((HediffComp)this).Pawn).Map, Props.radius, true), (Thing)(object)((HediffComp)this).Pawn).Where(ValidateTarget))
		{
			item.TakeDamage(new DamageInfo(Props.damageDef, Props.damageAmount, Props.armorPenetration, Vector3Utility.AngleToFlat(((Thing)((HediffComp)this).Pawn).DrawPos, item.DrawPos), (Thing)(object)((HediffComp)this).Pawn, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
		}
	}

	public override void CompPostPostRemoved()
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		Sustainer obj = sustainer;
		if (obj != null)
		{
			obj.End();
		}
		SoundDef soundEnded = Props.soundEnded;
		if (soundEnded != null)
		{
			SoundStarter.PlayOneShot(soundEnded, SoundInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn));
		}
		base.CompPostPostRemoved();
	}

	protected virtual bool ValidateTarget(Thing thing)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		if (!Props.hostileOnly || GenHostility.HostileTo(thing, (Thing)(object)((HediffComp)this).Pawn))
		{
			return Props.targetingParameters.CanTarget(TargetInfo.op_Implicit(thing), (ITargetingSource)null);
		}
		return false;
	}
}
