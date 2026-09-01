using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class Ability_Barrier : Ability
{
	public override void Cast(params GlobalTargetInfo[] targets)
	{
		if (((ThingWithComps)pawn).GetComp<CompAbilities>().ReinitShield(GetPowerForPawn(), ((Def)def).GetModExtension<AbilityExtension_Shield>()?.shieldTexPath, GetDurationForPawn()))
		{
			base.Cast(targets);
		}
	}
}
