using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_GiveMentalState : AbilityExtension_AbilityMod
{
	public MentalStateDef stateDef;

	public MentalStateDef stateDefForMechs;

	public StatDef durationMultiplier;

	public bool durationScalesWithCaster;

	public bool applyToSelf;

	public bool clearOthers;

	public bool causedByPsycast;

	public override void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets, ability);
		for (int i = 0; i < targets.Length; i++)
		{
			GlobalTargetInfo val = targets[i];
			Pawn val2 = (Pawn)(applyToSelf ? ((object)ability.pawn) : ((object)/*isinst with value type is only supported in some contexts*/));
			if (val2 == null)
			{
				continue;
			}
			if (val2.InMentalState)
			{
				if (!clearOthers)
				{
					continue;
				}
				val2.mindState.mentalStateHandler.CurState.RecoverFromState();
			}
			TryGiveMentalStateWithDuration(val2.RaceProps.IsMechanoid ? (stateDefForMechs ?? stateDef) : stateDef, val2, ability, durationMultiplier, durationScalesWithCaster, causedByPsycast);
			RestUtility.WakeUp(val2, true);
		}
	}

	public override bool Valid(GlobalTargetInfo[] targets, Ability ability, bool throwMessages = false)
	{
		Pawn val = targets.Select((GlobalTargetInfo t) => ((GlobalTargetInfo)(ref t)).Thing).OfType<Pawn>().FirstOrDefault();
		if (val != null && !AbilityUtility.ValidateNoMentalState(val, throwMessages, (Ability)null))
		{
			return false;
		}
		return true;
	}

	public static void TryGiveMentalStateWithDuration(MentalStateDef def, Pawn p, Ability ability, StatDef multiplierStat, bool durationScalesWithCaster, bool causedByPsycast)
	{
		if (p.mindState.mentalStateHandler.TryStartMentalState(def, (string)null, true, false, false, (Pawn)null, false, false, causedByPsycast))
		{
			float num = ability.GetDurationForPawn();
			if (multiplierStat != null)
			{
				num = ((!durationScalesWithCaster) ? (num * StatExtension.GetStatValue((Thing)(object)ability.pawn, multiplierStat, true, -1)) : (num * StatExtension.GetStatValue((Thing)(object)p, multiplierStat, true, -1)));
			}
			p.mindState.mentalStateHandler.CurState.forceRecoverAfterTicks = (int)num;
		}
	}
}
