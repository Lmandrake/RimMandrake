using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_ThoughtOnTarget : AbilityExtension_AbilityMod
{
	public ThoughtDef thoughtDef;

	public override void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets, ability);
		for (int i = 0; i < targets.Length; i++)
		{
			GlobalTargetInfo val = targets[i];
			Thing thing = ((GlobalTargetInfo)(ref val)).Thing;
			Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val2 != null)
			{
				val2.needs.mood.thoughts.memories.TryGainMemory(thoughtDef, ability.pawn, (Precept)null);
			}
		}
	}
}
