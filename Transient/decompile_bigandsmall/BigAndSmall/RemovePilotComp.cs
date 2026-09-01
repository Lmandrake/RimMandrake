using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class RemovePilotComp : CompAbilityEffect
{
	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		RemovePilotedHediff(((AbilityComp)this).parent.pawn);
		Pawn pawn = ((AbilityComp)this).parent.pawn;
		if (pawn == null || pawn.Dead)
		{
			return;
		}
		Pawn pawn2 = ((AbilityComp)this).parent.pawn;
		if (pawn2 == null)
		{
			return;
		}
		Pawn_StanceTracker stances = pawn2.stances;
		if (stances != null)
		{
			StunHandler stunner = stances.stunner;
			if (stunner != null)
			{
				stunner.StunFor(Rand.Range(80, 240), (Thing)(object)((AbilityComp)this).parent.pawn, true, true, false);
			}
		}
	}

	public void RemovePilotedHediff(Pawn pawn)
	{
		Hediff[] array = pawn.health.hediffSet.hediffs.Where((Hediff x) => x is Piloted).ToArray();
		for (int i = 0; i < array.Length; i++)
		{
			if (array[i] is Piloted piloted)
			{
				piloted.RemovePilots();
				break;
			}
		}
	}

	public override bool CanApplyOn(LocalTargetInfo target, LocalTargetInfo dest)
	{
		return true;
	}
}
