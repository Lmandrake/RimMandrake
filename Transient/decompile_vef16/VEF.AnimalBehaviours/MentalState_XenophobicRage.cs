using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class MentalState_XenophobicRage : MentalState
{
	public Pawn target;

	private const int NoLongerValidTargetCheckInterval = 120;

	public override void ExposeData()
	{
		((MentalState)this).ExposeData();
		Scribe_References.Look<Pawn>(ref target, "target", false);
	}

	public override RandomSocialMode SocialModeMax()
	{
		return (RandomSocialMode)0;
	}

	public override void PreStart()
	{
		((MentalState)this).PreStart();
		TryFindNewTarget();
	}

	public override void MentalStateTick(int delta)
	{
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		((MentalState)this).MentalStateTick(delta);
		if (target != null && target.Dead)
		{
			((MentalState)this).RecoverFromState();
		}
		if (Gen.IsHashIntervalTick((Thing)(object)base.pawn, 120, delta) && !IsTargetStillValidAndReachable())
		{
			if (!TryFindNewTarget())
			{
				((MentalState)this).RecoverFromState();
				return;
			}
			TaggedString val = TranslatorFormattedStringExtensions.Translate("MessageMurderousRageChangedTarget", NamedArgument.op_Implicit(base.pawn.NameShortColored), NamedArgument.op_Implicit(((Entity)target).Label), NamedArgumentUtility.Named((object)base.pawn, "PAWN"), NamedArgumentUtility.Named((object)target, "TARGET"));
			Messages.Message(GenText.AdjustedFor(((TaggedString)(ref val)).Resolve(), base.pawn, "PAWN", true), LookTargets.op_Implicit((Thing)(object)base.pawn), MessageTypeDefOf.NegativeEvent, true);
			((MentalState)this).MentalStateTick(delta);
		}
	}

	public override TaggedString GetBeginLetterText()
	{
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		if (target == null)
		{
			Log.Error("No target. This should have been checked in this mental state's worker.");
			return TaggedString.op_Implicit("");
		}
		TaggedString val = GrammarResolverSimpleStringExtensions.Formatted(base.def.beginLetter, NamedArgument.op_Implicit(base.pawn.NameShortColored), NamedArgument.op_Implicit(target.NameShortColored), NamedArgumentUtility.Named((object)base.pawn, "PAWN"), NamedArgumentUtility.Named((object)target, "TARGET"));
		val = ((TaggedString)(ref val)).AdjustedFor(base.pawn, "PAWN", true);
		return TaggedString.op_Implicit(GenText.CapitalizeFirst(((TaggedString)(ref val)).Resolve()));
	}

	private bool TryFindNewTarget()
	{
		target = XenophobicRageMentalStateUtility.FindPawnToKill(base.pawn);
		return target != null;
	}

	public bool IsTargetStillValidAndReachable()
	{
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		if (target != null && ((Thing)target).SpawnedParentOrMe != null && (!(((Thing)target).SpawnedParentOrMe is Pawn) || ((Thing)target).SpawnedParentOrMe == target))
		{
			return ReachabilityUtility.CanReach(base.pawn, LocalTargetInfo.op_Implicit(((Thing)target).SpawnedParentOrMe), (PathEndMode)2, (Danger)3, true, true, (TraverseMode)0);
		}
		return false;
	}
}
