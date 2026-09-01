using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class DamageWorker_Berserk : DamageWorker_AddInjury
{
	public override DamageResult Apply(DamageInfo dinfo, Thing victim)
	{
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((victim is Pawn) ? victim : null);
		if (val != null && ((Thing)val).Faction == Faction.OfPlayer && !val.Dead)
		{
			val.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Berserk, (string)null, true, false, false, (Pawn)null, false, false, false);
		}
		return ((DamageWorker_AddInjury)this).Apply(dinfo, victim);
	}
}
