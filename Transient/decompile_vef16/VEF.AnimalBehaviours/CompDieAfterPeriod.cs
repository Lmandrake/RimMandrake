using System;
using RimWorld;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class CompDieAfterPeriod : ThingComp
{
	public int tickCounter;

	public CompProperties_DieAfterPeriod Props => (CompProperties_DieAfterPeriod)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref tickCounter, "tickCounter", 0, false);
	}

	public override void CompTickInterval(int delta)
	{
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		tickCounter += delta;
		if (tickCounter < Props.timeToDieInTicks)
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val != null && ((Thing)val).Map != null)
		{
			if (Props.effect)
			{
				IntVec3 val2 = default(IntVec3);
				for (int i = 0; i < 20; i++)
				{
					CellFinder.TryFindRandomReachableNearbyCell(((Thing)base.parent).Position, ((Thing)base.parent).Map, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val2, 999999);
					FilthMaker.TryMakeFilth(val2, ((Thing)base.parent).Map, ThingDef.Named(Props.effectFilth), 1, (FilthSourceFlags)0, true);
				}
				SoundStarter.PlayOneShot(VEFDefOf.Hive_Spawn, SoundInfo.op_Implicit(new TargetInfo(((Thing)base.parent).Position, ((Thing)base.parent).Map, false)));
			}
			if (Props.justVanish)
			{
				((Thing)val).Destroy((DestroyMode)0);
			}
			else
			{
				((Thing)val).Kill((DamageInfo?)null, (Hediff)null);
			}
		}
		tickCounter = 0;
	}

	public override string CompInspectStringExtra()
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		string text = ((ThingComp)this).CompInspectStringExtra();
		string text2 = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF_TimeToDie", NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod(Props.timeToDieInTicks - tickCounter, true, false, true, true, false))));
		return text + text2;
	}
}
