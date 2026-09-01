using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class HediffComp_PlaySound : HediffComp
{
	private Sustainer sustainer;

	public HediffCompProperties_PlaySound Props => (HediffCompProperties_PlaySound)(object)base.props;

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (Props.sustainer != null)
		{
			if (sustainer == null || sustainer.Ended)
			{
				sustainer = SoundStarter.TrySpawnSustainer(Props.sustainer, SoundInfo.InMap(TargetInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn), (MaintenanceType)1));
			}
			Sustainer obj = sustainer;
			if (obj != null)
			{
				obj.Maintain();
			}
		}
	}

	public override void CompPostPostRemoved()
	{
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostPostRemoved();
		if (Props.sustainer != null && !sustainer.Ended)
		{
			Sustainer obj = sustainer;
			if (obj != null)
			{
				obj.End();
			}
		}
		if (Props.endSound != null)
		{
			SoundStarter.PlayOneShot(Props.endSound, SoundInfo.op_Implicit((Thing)(object)((HediffComp)this).Pawn));
		}
	}
}
