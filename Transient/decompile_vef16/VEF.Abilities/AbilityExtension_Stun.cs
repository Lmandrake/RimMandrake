using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_Stun : AbilityExtension_AbilityMod
{
	public IntRange? stunTicks;

	public StatDef durationMultiplier;

	public bool durationMultiplierFromCaster;

	public override void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets, ability);
		for (int i = 0; i < targets.Length; i++)
		{
			Thing thing = ((GlobalTargetInfo)(ref targets[i])).Thing;
			Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val != null && ((Thing)val).Spawned)
			{
				int num;
				if (!stunTicks.HasValue)
				{
					num = ability.GetDurationForPawn();
				}
				else
				{
					IntRange value = stunTicks.Value;
					num = ((IntRange)(ref value)).RandomInRange;
				}
				int num2 = num;
				if (durationMultiplier != null)
				{
					num2 = (int)((float)num2 * (durationMultiplierFromCaster ? StatExtension.GetStatValue((Thing)(object)ability.pawn, durationMultiplier, true, -1) : StatExtension.GetStatValue((Thing)(object)val, durationMultiplier, true, -1)));
				}
				val.stances.stunner.StunFor(num2, (Thing)(object)ability.pawn, true, true, false);
			}
		}
	}
}
