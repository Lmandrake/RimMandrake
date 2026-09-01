using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class Ability_OrbitalStrike : Ability
{
	public override void Cast(params GlobalTargetInfo[] targets)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets);
		for (int i = 0; i < targets.Length; i++)
		{
			GlobalTargetInfo val = targets[i];
			OrbitalStrike val2 = (OrbitalStrike)GenSpawn.Spawn(((Def)def).GetModExtension<AbilityExtension_Projectile>().projectile, ((GlobalTargetInfo)(ref val)).Cell, ((Thing)pawn).Map, (WipeMode)0);
			val2.duration = GetDurationForPawn();
			val2.instigator = (Thing)(object)pawn;
			val2.StartStrike();
		}
	}
}
