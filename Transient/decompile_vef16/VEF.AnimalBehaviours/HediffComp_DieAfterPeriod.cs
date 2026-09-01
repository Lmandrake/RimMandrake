using System;
using RimWorld;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class HediffComp_DieAfterPeriod : HediffComp
{
	public int tickCounter;

	public HediffCompProperties_DieAfterPeriod Props => (HediffCompProperties_DieAfterPeriod)(object)base.props;

	public override string CompLabelInBracketsExtra => GetLabel();

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_Values.Look<int>(ref tickCounter, "tickCounter", 0, false);
	}

	public override void CompPostTickInterval(ref float severityAdjustment, int delta)
	{
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTickInterval(ref severityAdjustment, delta);
		tickCounter += delta;
		if (tickCounter < Props.timeToDieInTicks)
		{
			return;
		}
		Pawn pawn = ((Hediff)base.parent).pawn;
		if (pawn != null && ((Thing)pawn).Map != null)
		{
			if (Props.effect)
			{
				IntVec3 val = default(IntVec3);
				for (int i = 0; i < 20; i++)
				{
					CellFinder.TryFindRandomReachableNearbyCell(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val, 999999);
					FilthMaker.TryMakeFilth(val, ((Thing)((Hediff)base.parent).pawn).Map, ThingDef.Named(Props.effectFilth), 1, (FilthSourceFlags)0, true);
				}
				SoundStarter.PlayOneShot(VEFDefOf.Hive_Spawn, SoundInfo.op_Implicit(new TargetInfo(((Thing)((Hediff)base.parent).pawn).Position, ((Thing)((Hediff)base.parent).pawn).Map, false)));
			}
			if (Props.justVanish)
			{
				((Thing)pawn).Destroy((DestroyMode)0);
			}
			else
			{
				((Thing)pawn).Kill((DamageInfo?)null, (Hediff)null);
			}
		}
		tickCounter = 0;
	}

	public string GetLabel()
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(Props.DescriptionLabel, NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod(Props.timeToDieInTicks - tickCounter, true, false, true, true, false))));
	}
}
