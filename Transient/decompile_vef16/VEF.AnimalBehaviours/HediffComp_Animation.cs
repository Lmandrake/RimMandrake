using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Animation : HediffComp
{
	public HediffCompProperties_Animation Props => (HediffCompProperties_Animation)(object)base.props;

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		((Hediff)base.parent).pawn.Drawer.renderer.SetAnimation(Props.animation);
	}

	public override void CompPostTick(ref float severityAdjustment)
	{
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (!((Hediff)base.parent).pawn.Drawer.renderer.HasAnimation)
		{
			((Hediff)base.parent).pawn.Drawer.renderer.SetAnimation(Props.animation);
		}
		if (Props.shamblerParticles && Rand.MTBEventOccurs(1f, 60f, 1f))
		{
			FleckMaker.ThrowShamblerParticles((Thing)(object)((Hediff)base.parent).pawn);
		}
	}

	public override void CompPostPostRemoved()
	{
		((Hediff)base.parent).pawn.Drawer.renderer.SetAnimation((AnimationDef)null);
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
		((Hediff)base.parent).pawn.Drawer.renderer.SetAnimation((AnimationDef)null);
	}

	public override void Notify_PawnKilled()
	{
		((Hediff)base.parent).pawn.Drawer.renderer.SetAnimation((AnimationDef)null);
	}
}
