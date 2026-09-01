using Verse;

namespace BigAndSmall;

public class DummyGeneClass : Gene
{
	public override string Label
	{
		get
		{
			//IL_0005: Unknown result type (might be due to invalid IL or missing references)
			//IL_000a: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			TaggedString val = Translator.Translate("BS_RequirementNotMet");
			return TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst());
		}
	}

	public override bool Active => true;

	public override void PostAdd()
	{
	}

	public override void PostRemove()
	{
	}

	public override void TickInterval(int delta)
	{
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
	}

	public override void ExposeData()
	{
	}
}
