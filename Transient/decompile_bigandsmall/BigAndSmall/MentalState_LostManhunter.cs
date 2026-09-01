using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class MentalState_LostManhunter : MentalState_Manhunter
{
	public override bool ForceHostileTo(Faction f)
	{
		if (((Thing)((MentalState)this).pawn).Faction == f)
		{
			return ((Def)((Thing)((MentalState)this).pawn).Faction.def).defName == "Zombies";
		}
		return true;
	}

	public override bool ForceHostileTo(Thing t)
	{
		return false;
	}

	public override RandomSocialMode SocialModeMax()
	{
		return (RandomSocialMode)0;
	}
}
